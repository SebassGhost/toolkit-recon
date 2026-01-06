import json
import os

SIGNATURES_PATH = os.path.join(
    os.path.dirname(__file__),
    "signatures.json"
)

with open(SIGNATURES_PATH, "r", encoding="utf-8") as f:
    SIGNATURES = json.load(f)


def detect_server(response):
    return response.headers.get("Server", "Unknown")


def detect_headers(response):
    interesting = [
        "X-Powered-By",
        "X-Frame-Options",
        "Content-Security-Policy",
        "Strict-Transport-Security"
    ]

    found = {}
    for h in interesting:
        if h in response.headers:
            found[h] = response.headers[h]

    return found


def detect_frameworks(response):
    detected = []

    headers = response.headers
    body = response.text.lower()

    for tech, patterns in SIGNATURES.items():
        for p in patterns:
            if p.lower() in body or p in headers.values():
                detected.append(tech)
                break

    return detected
