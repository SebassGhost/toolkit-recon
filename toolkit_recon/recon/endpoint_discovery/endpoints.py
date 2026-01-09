import os
import requests
from urllib.parse import urljoin

INTERESTING_KEYWORDS = [
    "admin", "api", "login", "dashboard", "upload", "graphql"
]

BASE_DIR = os.path.dirname(__file__)
WORDLIST = os.path.join(BASE_DIR, "common_paths.txt")


# -------------------------
# Load wordlist
# -------------------------
def load_wordlist():
    with open(WORDLIST, "r", encoding="utf-8") as f:
        return [
            "/" + line.strip().lstrip("/")
            for line in f
            if line.strip() and not line.startswith("#")
        ]


# -------------------------
# Interesting logic
# -------------------------
def is_interesting(path, status, length):
    if status not in [200, 301, 302, 401, 403]:
        return False
    if length == 0:
        return False

    return any(k in path.lower() for k in INTERESTING_KEYWORDS)


# -------------------------
# Main runner
# -------------------------
def run(target: str):
    if target.startswith("http"):
        base_url = target.rstrip("/")
    else:
        base_url = f"https://{target}".rstrip("/")

    paths = load_wordlist()
    results = []

    # -------------------------
    # Baseline (soft-404 detect)
    # -------------------------
    try:
        fake = requests.get(
            f"{base_url}/this_should_not_exist_98765",
            timeout=6,
            allow_redirects=False
        )
        baseline_status = fake.status_code
        baseline_length = len(fake.content)
    except Exception:
        baseline_status = None
        baseline_length = None

    # -------------------------
    # Endpoint discovery
    # -------------------------
    for path in paths:
        url = urljoin(base_url, path)

        try:
            r = requests.get(url, timeout=6, allow_redirects=False)
        except Exception:
            continue

        # Soft-404 filter
        if (
            baseline_status is not None
            and r.status_code == baseline_status
            and len(r.content) == baseline_length
        ):
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

        # -------------------------
        # HEAD support
        # -------------------------
        try:
            h = requests.head(url, timeout=4, allow_redirects=False)
            if h.status_code < 500:
                entry["methods"].append("HEAD")
        except Exception:
            pass

        # -------------------------
        # OPTIONS → allowed methods
        # -------------------------
        try:
            o = requests.options(url, timeout=4)
            allow = o.headers.get("Allow")
            if allow:
                entry["methods"] = sorted(set(
                    entry["methods"] + [m.strip() for m in allow.split(",")]
                ))
        except Exception:
            pass

        # -------------------------
        # Interesting detection
        # -------------------------
        entry["interesting"] = is_interesting(
            path, entry["status"], entry["length"]
        )

        if entry["status"] != 404:
            results.append(entry)

    return {
        "module": "endpoint_discovery",
        "target": target,
        "total_checked": len(paths),
        "results": results
    }
