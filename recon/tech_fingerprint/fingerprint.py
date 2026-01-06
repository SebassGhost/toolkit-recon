import requests
import json
import os

def load_signatures():
    path = os.path.join(os.path.dirname(__file__), "signatures.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_headers(headers):
    return {k.lower(): v for k, v in headers.items()}

def run(target):
    url = f"https://{target}"
    signatures = load_signatures()

    result = {
        "module": "tech_fingerprint",
        "target": target,
        "results": {
            "server": None,
            "cdn": None,
            "frameworks": [],
            "technologies": [],
            "headers": {}
        }
    }

    try:
        response = requests.get(url, timeout=8)
    except Exception as e:
        result["error"] = str(e)
        return result

    headers = normalize_headers(response.headers)
    result["results"]["headers"] = dict(headers)

    # Server
    server = headers.get("server")
    if server:
        result["results"]["server"] = server

    # Signature matching
    for tech, rules in signatures.items():
        for rule in rules:
            header = rule.get("header")
            value = rule.get("value")

            if header in headers and value.lower() in headers[header].lower():
                if rule.get("type") == "cdn":
                    result["results"]["cdn"] = tech
                elif rule.get("type") == "framework":
                    result["results"]["frameworks"].append(tech)
                else:
                    result["results"]["technologies"].append(tech)

    # Deduplicate
    result["results"]["frameworks"] = list(set(result["results"]["frameworks"]))
    result["results"]["technologies"] = list(set(result["results"]["technologies"]))

    return result
