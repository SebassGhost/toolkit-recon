import requests

def run(target):
    results = {
        "module": "endpoint_discovery",
        "target": target,
        "endpoints": []
    }

    paths = [
        "/admin",
        "/login",
        "/dashboard",
        "/api",
        "/robots.txt"
    ]

    for path in paths:
        url = f"http://{target}{path}"
        try:
            r = requests.get(url, timeout=3)
            results["endpoints"].append({
                "endpoint": path,
                "status": r.status_code
            })
        except requests.RequestException:
            continue

    return results
