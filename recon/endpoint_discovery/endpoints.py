import requests
from urllib.parse import urljoin

INTERESTING_KEYWORDS = [
    "admin", "api", "login", "dashboard", "upload", "graphql"
]


def load_wordlist():
    with open(__file__.replace("endpoints.py", "common_paths.txt"), "r") as f:
        return [line.strip() for line in f if line.strip()]


def is_interesting(path, status, length):
    if status not in [200, 301, 302, 401, 403]:
        return False
    if length == 0:
        return False
    for k in INTERESTING_KEYWORDS:
        if k in path.lower():
            return True
    return False


def run(target):
    base_url = f"https://{target}"
    paths = load_wordlist()

    results = []

    for path in paths:
        url = urljoin(base_url, path)

        try:
            r = requests.get(url, timeout=6, allow_redirects=False)
        except Exception:
            continue

        entry = {
            "path": path,
            "status": r.status_code,
            "length": len(r.content),
            "type": r.headers.get("Content-Type", ""),
            "redirect": r.headers.get("Location"),
            "methods": ["GET"],
            "interesting": False
        }

        # HEAD support check
        try:
            h = requests.head(url, timeout=4)
            if h.status_code < 500:
                entry["methods"].append("HEAD")
        except Exception:
            pass

        entry["interesting"] = is_interesting(
            path, entry["status"], entry["length"]
        )

        if entry["status"] != 404:
            results.append(entry)

    return {
        "module": "endpoint_discovery",
        "target": target,
        "results": results
    }
