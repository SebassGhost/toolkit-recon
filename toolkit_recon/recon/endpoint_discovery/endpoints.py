import asyncio
import os
import random
import time
from urllib.parse import urljoin

import httpx

from toolkit_recon import SCHEMA_VERSION
from toolkit_recon.config.profiles import get_http_config, get_profile


INTERESTING_KEYWORDS = [
    "admin",
    "api",
    "login",
    "dashboard",
    "upload",
    "graphql",
]

BASE_DIR = os.path.dirname(__file__)

WORDLISTS = {
    "small": "small_paths.txt",
    "medium": "common_paths.txt",
    "large": "large_paths.txt",
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15",
]

RETRY_STATUS = {429, 500, 502, 503, 504}


def load_wordlist(name: str):
    filename = WORDLISTS.get(name)
    if not filename:
        return []

    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        path = os.path.join(BASE_DIR, WORDLISTS["medium"])
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return [
            "/" + line.strip().lstrip("/")
            for line in f
            if line.strip() and not line.startswith("#")
        ]


def should_scan(path: str) -> bool:
    skip_ext = (
        ".css",
        ".js",
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".ico",
        ".woff",
        ".ttf",
        ".map",
    )
    return not path.lower().endswith(skip_ext)


def is_interesting(path: str, status: int, length: int) -> bool:
    if status not in (200, 301, 302, 401, 403):
        return False
    if length == 0:
        return False
    return any(k in path.lower() for k in INTERESTING_KEYWORDS)


def build_headers(stealth_cfg: dict) -> dict:
    if stealth_cfg.get("random_user_agent", False):
        return {"User-Agent": random.choice(USER_AGENTS)}
    return {"User-Agent": "toolkit-recon/1.0"}


class AsyncRateLimiter:
    def __init__(self, max_rps: int):
        self._interval = 1.0 / max_rps if max_rps and max_rps > 0 else 0.0
        self._next_time = 0.0
        self._lock = asyncio.Lock()

    async def wait(self):
        if self._interval <= 0:
            return
        async with self._lock:
            now = time.monotonic()
            if now < self._next_time:
                await asyncio.sleep(self._next_time - now)
            self._next_time = time.monotonic() + self._interval


async def request_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    timeout: float,
    follow_redirects: bool,
    retries: int,
    backoff_factor: float,
    headers: dict,
):
    attempts = 0
    while True:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
                follow_redirects=follow_redirects,
            )
            if response.status_code in RETRY_STATUS and attempts < retries:
                await asyncio.sleep(backoff_factor * (2 ** attempts))
                attempts += 1
                continue
            return response, attempts
        except (httpx.TimeoutException, httpx.NetworkError, httpx.ProtocolError):
            if attempts >= retries:
                return None, attempts
            await asyncio.sleep(backoff_factor * (2 ** attempts))
            attempts += 1


async def _scan_path(
    client: httpx.AsyncClient,
    base_url: str,
    path: str,
    cfg: dict,
    stealth_cfg: dict,
    limiter: AsyncRateLimiter,
):
    await limiter.wait()
    if stealth_cfg.get("delay", 0) > 0:
        await asyncio.sleep(stealth_cfg["delay"])

    headers = build_headers(stealth_cfg)
    url = urljoin(base_url, path)

    response, retries_used = await request_with_retry(
        client=client,
        method="GET",
        url=url,
        timeout=cfg["timeout"],
        follow_redirects=cfg["follow_redirects"],
        retries=cfg["retries"],
        backoff_factor=cfg["backoff_factor"],
        headers=headers,
    )

    if response is None:
        return None, {
            "attempted": 1,
            "completed": 0,
            "errors": 1,
            "retried_requests": retries_used,
        }

    entry = {
        "path": path,
        "url": str(response.url),
        "status": response.status_code,
        "length": len(response.content),
        "content_type": response.headers.get("Content-Type", ""),
        "redirect": response.headers.get("Location"),
        "methods": ["GET"],
        "interesting": False,
    }

    if "HEAD" in cfg["methods"]:
        head_response, head_retries = await request_with_retry(
            client=client,
            method="HEAD",
            url=url,
            timeout=cfg["timeout"],
            follow_redirects=False,
            retries=cfg["retries"],
            backoff_factor=cfg["backoff_factor"],
            headers=headers,
        )
        retries_used += head_retries
        if head_response is not None and head_response.status_code < 500:
            entry["methods"].append("HEAD")

    if "OPTIONS" in cfg["methods"] and response.status_code in (200, 401, 403):
        options_response, options_retries = await request_with_retry(
            client=client,
            method="OPTIONS",
            url=url,
            timeout=cfg["timeout"],
            follow_redirects=False,
            retries=cfg["retries"],
            backoff_factor=cfg["backoff_factor"],
            headers=headers,
        )
        retries_used += options_retries
        if options_response is not None:
            allow = options_response.headers.get("Allow", "")
            if allow:
                entry["methods"] = sorted(
                    set(entry["methods"] + [m.strip() for m in allow.split(",")])
                )

    entry["interesting"] = is_interesting(path, entry["status"], entry["length"])

    return entry, {
        "attempted": 1,
        "completed": 1,
        "errors": 0,
        "retried_requests": retries_used,
    }


async def _run_async(target: str, profile: str = "balanced"):
    cfg = get_profile(profile)
    http_cfg = get_http_config(profile)
    endpoint_cfg = cfg.get("endpoint", {})
    stealth_cfg = cfg.get("stealth", {})

    threads = http_cfg.get("threads", 10)
    timeout = http_cfg.get("timeout", 6)
    follow_redirects = http_cfg.get("follow_redirects", False)
    retries = http_cfg.get("retries", 2)
    backoff_factor = http_cfg.get("backoff_factor", 0.2)

    methods = endpoint_cfg.get("methods", ["GET"])
    wordlist_name = endpoint_cfg.get("wordlist", "medium")
    max_paths = endpoint_cfg.get("max_paths", 500)

    base_url = target.rstrip("/") if target.startswith("http") else f"https://{target}"

    paths = load_wordlist(wordlist_name)
    paths = [p for p in paths if should_scan(p)]
    paths = paths[:max_paths]

    limiter = AsyncRateLimiter(http_cfg.get("max_rps", 0))
    semaphore = asyncio.Semaphore(max(1, int(threads)))

    limits = httpx.Limits(max_connections=max(20, threads * 2), max_keepalive_connections=max(10, threads))
    transport = httpx.AsyncHTTPTransport(retries=0)
    start = time.perf_counter()

    async with httpx.AsyncClient(limits=limits, transport=transport) as client:
        async def _worker(path: str):
            async with semaphore:
                return await _scan_path(
                    client=client,
                    base_url=base_url,
                    path=path,
                    cfg={
                        "timeout": timeout,
                        "follow_redirects": follow_redirects,
                        "methods": methods,
                        "retries": retries,
                        "backoff_factor": backoff_factor,
                    },
                    stealth_cfg=stealth_cfg,
                    limiter=limiter,
                )

        tasks = [asyncio.create_task(_worker(path)) for path in paths]
        scanned = await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    metrics = {
        "total_paths": len(paths),
        "attempted": 0,
        "completed": 0,
        "errors": 0,
        "retried_requests": 0,
        "duration_seconds": 0.0,
        "throughput_rps": 0.0,
    }

    for item in scanned:
        if isinstance(item, Exception):
            metrics["attempted"] += 1
            metrics["errors"] += 1
            continue

        entry, partial = item
        metrics["attempted"] += partial["attempted"]
        metrics["completed"] += partial["completed"]
        metrics["errors"] += partial["errors"]
        metrics["retried_requests"] += partial["retried_requests"]

        if not entry:
            continue
        if entry["status"] == 404:
            continue
        results.append(entry)

    duration = time.perf_counter() - start
    metrics["duration_seconds"] = round(duration, 4)
    metrics["throughput_rps"] = round(metrics["completed"] / duration, 2) if duration > 0 else 0.0

    return {
        "schema_version": SCHEMA_VERSION,
        "module": "endpoint_discovery",
        "target": target,
        "profile": profile,
        "count": len(results),
        "results": results,
        "metrics": metrics,
    }


def run(target: str, profile: str = "balanced"):
    return asyncio.run(_run_async(target, profile=profile))
