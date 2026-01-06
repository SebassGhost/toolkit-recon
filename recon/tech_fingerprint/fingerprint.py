import requests
import json
from .detectors import (
    detect_headers,
    detect_server,
    detect_frameworks
)

def run(target: str) -> dict:
    if not target.startswith("http"):
        url = f"https://{target}"
    else:
        url = target

    results = {
        "module": "tech_fingerprint",
        "target": target,
        "results": {}
    }

    try:
        response = requests.get(url, timeout=8, allow_redirects=True)
    except requests.RequestException as e:
        results["error"] = str(e)
        return results

    results["results"]["server"] = detect_server(response)
    results["results"]["headers"] = detect_headers(response)
    results["results"]["frameworks"] = detect_frameworks(response)

    return results
