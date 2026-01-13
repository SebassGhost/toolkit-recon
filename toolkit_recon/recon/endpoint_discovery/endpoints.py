import os
import requests
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

from toolkit_recon.config.profiles import PROFILES


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


# -------------------------
# Utils
# -------------------------
def load_wordlist(name: str):
    filename = WORDLISTS.get(name)
    if not filename:
        return []

    path = os.path.join(BASE_DIR, filename)
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
# HTTP probe
# -------------------------
def probe(url: str, session: requests.Session, cfg: dict):
    try:
        r = session.get(
            url,
            timeout=cfg["timeout"],
            allow_redirects=cfg["follow_redirects"]
        )
    except Exception:
        return None

    entry = {
        "path": url,
        "status": r.status_code,
        "length": len(r.content),
        "content_type": r.headers.get("Content-Type", ""),
        "redirect": r.headers.get("Location"),
        "methods": ["GET"],
        "interesting": False
    }

    if "HEAD" in cfg["methods"]:
        try:
            h = session.head(url, timeout=cfg["timeout"], allow_redirects=False)
            if h.status_code < 500:
                entry["methods"].append("HEAD")
        except Exception:
            pass

    if "OPTIONS" in cfg["methods"] and r.status_code in (200, 401, 403):
        try:
            o = session.options(url, timeout=cfg["timeout"])
            allow = o.headers.get("Allow")
            if allow:
                entry["methods"] = sorted(set(
                    entry["methods"] + [m.strip() for m in allow.split(",")]
                ))
        except Exception:
            pass

    entry["interesting"] = is_interesting(
        url,
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

    cfg = PROFILES.get(profile, PROFILES["balanced"])
    http_cfg = cfg.get("http", {})
    endpoint_cfg = cfg.get("endpoint", {})

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

    session = requests.Session()
    session.headers.update({
        "User-Agent": "toolkit-recon/1.0"
    })

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []

        for path in paths:
            url = urljoin(base_url, path)
            futures.append(
                executor.submit(
                    probe,
                    url,
                    session,
                    {
                        "timeout": timeout,
                        "follow_redirects": follow_redirects,
                        "methods": methods,
                    }
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
