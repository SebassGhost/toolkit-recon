import os
import requests
from urllib.parse import urljoin

from toolkit_recon.config.profiles import PROFILES

# -------------------------
# Configuración general
# -------------------------
INTERESTING_KEYWORDS = [
    "admin", "api", "login", "dashboard", "upload", "graphql"
]

BASE_DIR = os.path.dirname(__file__)
WORDLIST_FILE = os.path.join(BASE_DIR, "common_paths.txt")


# -------------------------
# Load wordlist
# -------------------------
def load_wordlist():
    if not os.path.exists(WORDLIST_FILE):
        return []

    with open(WORDLIST_FILE, "r", encoding="utf-8") as f:
        return [
            "/" + line.strip().lstrip("/")
            for line in f
            if line.strip() and not line.startswith("#")
        ]


# -------------------------
# Filtro de paths inútiles
# -------------------------
def should_scan(path):
    skip_ext = [
        ".css", ".js", ".png", ".jpg", ".jpeg",
        ".svg", ".ico", ".woff", ".ttf", ".map"
    ]
    return not any(path.lower().endswith(ext) for ext in skip_ext)


# -------------------------
# Detección de interés
# -------------------------
def is_interesting(path, status, length):
    if status not in [200, 301, 302, 401, 403]:
        return False
    if length == 0:
        return False

    return any(k in path.lower() for k in INTERESTING_KEYWORDS)


# =========================
# Runner principal
# =========================
def run(target: str, profile="balanced"):
    # =========================
    # LOAD PROFILE 
    # =========================
    cfg = PROFILES.get(profile)
    if not cfg:
        raise ValueError(f"Invalid profile: {profile}")

    endpoint_cfg = cfg["endpoint"]
    http_cfg = cfg["http"]

    max_paths = endpoint_cfg["max_paths"]
    methods_enabled = endpoint_cfg["methods"]

    timeout = http_cfg["timeout"]

    # =========================
    # NORMALIZAR TARGET
    # =========================
    if target.startswith("http"):
        base_url = target.rstrip("/")
    else:
        base_url = f"https://{target}".rstrip("/")

    paths = load_wordlist()[:max_paths]
    results = []

    # =========================
    # BASELINE SOFT-404
    # =========================
    baseline_status = None
    baseline_length = None

    try:
        fake = requests.get(
            f"{base_url}/this_should_not_exist_987654",
            timeout=timeout,
            allow_redirects=False
        )
        baseline_status = fake.status_code
        baseline_length = len(fake.content)
    except Exception:
        pass

    empty_hits = 0
    max_empty = endpoint_cfg.get("max_empty", 25)

    # =========================
    # ENDPOINT DISCOVERY
    # =========================
    for path in paths:

        if not should_scan(path):
            continue

        url = urljoin(base_url, path)

        try:
            r = requests.get(
                url,
                timeout=timeout,
                allow_redirects=False
            )
        except Exception:
            continue

        # Soft-404 filter
        if (
            baseline_status is not None
            and r.status_code == baseline_status
            and len(r.content) == baseline_length
        ):
            empty_hits += 1
        else:
            empty_hits = 0

        if empty_hits >= max_empty:
            break

        if r.status_code == 404:
            continue

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

        # HEAD
        if "HEAD" in methods_enabled:
            try:
                h = requests.head(
                    url,
                    timeout=timeout,
                    allow_redirects=False
                )
                if h.status_code < 500:
                    entry["methods"].append("HEAD")
            except Exception:
                pass

        # OPTIONS
        if "OPTIONS" in methods_enabled and r.status_code in [200, 401, 403]:
            try:
                o = requests.options(url, timeout=timeout)
                allow = o.headers.get("Allow")
                if allow:
                    entry["methods"] = sorted(set(
                        entry["methods"] + [
                            m.strip() for m in allow.split(",")
                        ]
                    ))
            except Exception:
                pass

        entry["interesting"] = is_interesting(
            path,
            entry["status"],
            entry["length"]
        )

        results.append(entry)

    # =========================
    # RETURN FRAMEWORK DATA
    # =========================
    return {
        "module": "endpoint_discovery",
        "target": target,
        "profile": profile,
        "count": len(results),
        "results": results
    }
