import os
import requests
from urllib.parse import urljoin

# -------------------------
# Configuración
# -------------------------
INTERESTING_KEYWORDS = [
    "admin", "api", "login", "dashboard", "upload", "graphql"
]

BASE_DIR = os.path.dirname(__file__)
WORDLIST = os.path.join(BASE_DIR, "common_paths.txt")

MAX_PATHS = 150          # Límite duro
MAX_EMPTY = 25           # Cortar si no hay resultados seguidos
TIMEOUT = 6

BIG_TARGETS = [
    "github.com",
    "google.com",
    "microsoft.com",
    "cloudflare.com"
]


# -------------------------
# Load wordlist
# -------------------------
def load_wordlist():
    if not os.path.exists(WORDLIST):
        return []

    with open(WORDLIST, "r", encoding="utf-8") as f:
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


# -------------------------
# Runner principal
# -------------------------
def run(target: str):

    # Normalizar URL base
    if target.startswith("http"):
        base_url = target.rstrip("/")
    else:
        base_url = f"https://{target}".rstrip("/")

    paths = load_wordlist()

    # Targets grandes → modo conservador
    if any(t in target for t in BIG_TARGETS):
        paths = paths[:50]
    else:
        paths = paths[:MAX_PATHS]

    results = []

    # -------------------------
    # Baseline Soft-404
    # -------------------------
    try:
        fake = requests.get(
            f"{base_url}/this_should_not_exist_987654",
            timeout=TIMEOUT,
            allow_redirects=False
        )
        baseline_status = fake.status_code
        baseline_length = len(fake.content)
    except Exception:
        baseline_status = None
        baseline_length = None

    empty_hits = 0

    # -------------------------
    # Endpoint Discovery
    # -------------------------
    for path in paths:

        if not should_scan(path):
            continue

        url = urljoin(base_url, path)

        try:
            r = requests.get(
                url,
                timeout=TIMEOUT,
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

        if empty_hits >= MAX_EMPTY:
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
        try:
            h = requests.head(url, timeout=4, allow_redirects=False)
            if h.status_code < 500:
                entry["methods"].append("HEAD")
        except Exception:
            pass

        # OPTIONS solo si vale la pena
        if r.status_code in [200, 401, 403]:
            try:
                o = requests.options(url, timeout=4)
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

    return {
        "module": "endpoint_discovery",
        "target": target,
        "count": len(results),
        "results": results
    }
