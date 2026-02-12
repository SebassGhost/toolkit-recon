import os
import random
import time
import threading
import requests
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from toolkit_recon.config.profiles import get_profile, get_http_config


# -------------------------
# Constants
# -------------------------
INTERESTING_KEYWORDS = [
    "admin", "api", "login", "dashboard", "upload", "graphql"
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

RETRY_STATUS = (429, 500, 502, 503, 504)


# -------------------------
# Utils
# -------------------------
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
        ".css", ".js", ".png", ".jpg", ".jpeg",
        ".svg", ".ico", ".woff", ".ttf", ".map"
    )
    return not path.lower().endswith(skip_ext)


def is_interesting(path: str, status: int, length: int) -> bool:
    if status not in (200, 301, 302, 401, 403):
        return False
    if length == 0:
        return False

    return any(k in path.lower() for k in INTERESTING_KEYWORDS)


# -------------------------
def build_headers(stealth_cfg: dict) -> dict:
    headers = {}
    if stealth_cfg.get("random_user_agent", False):
        headers["User-Agent"] = random.choice(USER_AGENTS)
    else:
        headers["User-Agent"] = "toolkit-recon/1.0"
    return headers


class RateLimiter:
    def __init__(self, max_rps: int):
        self._interval = 1.0 / max_rps if max_rps and max_rps > 0 else 0.0
        self._next_time = 0.0
        self._lock = threading.Lock()

    def wait(self):
        if self._interval <= 0:
            return

        with self._lock:
            now = time.monotonic()
            if now < self._next_time:
                time.sleep(self._next_time - now)
            self._next_time = time.monotonic() + self._interval


def build_session(http_cfg: dict) -> requests.Session:
    retries = Retry(
        total=http_cfg.get("retries", 2),
        connect=http_cfg.get("retries", 2),
        read=http_cfg.get("retries", 2),
        status=http_cfg.get("retries", 2),
        backoff_factor=http_cfg.get("backoff_factor", 0.2),
        status_forcelist=RETRY_STATUS,
        allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=100, pool_maxsize=100)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


# -------------------------
# HTTP probe
# -------------------------
def probe(
    url: str,
    path: str,
    cfg: dict,
    stealth_cfg: dict,
    thread_ctx: threading.local,
    limiter: RateLimiter,
):
    if not hasattr(thread_ctx, "session"):
        thread_ctx.session = build_session(cfg)
    session = thread_ctx.session

    limiter.wait()
    if stealth_cfg.get("delay", 0) > 0:
        time.sleep(stealth_cfg["delay"])

    headers = build_headers(stealth_cfg)

    try:
        r = session.get(
            url,
            headers=headers,
            timeout=cfg["timeout"],
            allow_redirects=cfg["follow_redirects"]
        )
    except Exception:
        return None

    entry = {
        "path": path,
        "url": url,
        "status": r.status_code,
        "length": len(r.content),
        "content_type": r.headers.get("Content-Type", ""),
        "redirect": r.headers.get("Location"),
        "methods": ["GET"],
        "interesting": False
    }

    if "HEAD" in cfg["methods"]:
        try:
            h = session.head(
                url,
                headers=headers,
                timeout=cfg["timeout"],
                allow_redirects=False
            )
            if h.status_code < 500:
                entry["methods"].append("HEAD")
        except Exception:
            pass

    if "OPTIONS" in cfg["methods"] and r.status_code in (200, 401, 403):
        try:
            o = session.options(url, headers=headers, timeout=cfg["timeout"])
            allow = o.headers.get("Allow")
            if allow:
                entry["methods"] = sorted(set(
                    entry["methods"] + [m.strip() for m in allow.split(",")]
                ))
        except Exception:
            pass

    entry["interesting"] = is_interesting(
        path,
        entry["status"],
        entry["length"]
    )

    return entry


# -------------------------
# Runner
# -------------------------
def run(target: str, profile: str = "balanced"):
    """
    Endpoint discovery module.
    """

    cfg = get_profile(profile)
    http_cfg = get_http_config(profile)
    endpoint_cfg = cfg.get("endpoint", {})
    stealth_cfg = cfg.get("stealth", {})

    threads = http_cfg.get("threads", 10)
    timeout = http_cfg.get("timeout", 6)
    follow_redirects = http_cfg.get("follow_redirects", False)

    methods = endpoint_cfg.get("methods", ["GET"])
    wordlist_name = endpoint_cfg.get("wordlist", "medium")
    max_paths = endpoint_cfg.get("max_paths", 500)

    if target.startswith("http"):
        base_url = target.rstrip("/")
    else:
        base_url = f"https://{target}".rstrip("/")

    paths = load_wordlist(wordlist_name)
    paths = [p for p in paths if should_scan(p)]
    paths = paths[:max_paths]

    results = []
    thread_ctx = threading.local()
    limiter = RateLimiter(http_cfg.get("max_rps", 0))

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []

        for path in paths:
            url = urljoin(base_url, path)
            futures.append(
                executor.submit(
                    probe,
                    url,
                    path,
                    {
                        "timeout": timeout,
                        "follow_redirects": follow_redirects,
                        "methods": methods,
                        "retries": http_cfg.get("retries", 2),
                        "backoff_factor": http_cfg.get("backoff_factor", 0.2),
                    },
                    stealth_cfg,
                    thread_ctx,
                    limiter,
                )
            )

        for future in as_completed(futures):
            entry = future.result()
            if not entry:
                continue
            if entry["status"] == 404:
                continue

            results.append(entry)

    return results
