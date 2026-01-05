import requests
import os

def load_wordlist():
    wordlist_path = os.path.join(
        os.path.dirname(__file__),
        "common_paths.txt"
    )
    with open(wordlist_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def run(target):
    results = []
    paths = load_wordlist()

    headers = {
        "User-Agent": "Mozilla/5.0 (Recon Toolkit)",
        "Accept": "*/*"
    }

    schemes = ["https", "http"]

    for scheme in schemes:
        base_url = f"{scheme}://{target}"

        for path in paths:
            url = f"{base_url}/{path}"
            try:
                r = requests.get(
                    url,
                    headers=headers,
                    timeout=4,
                    allow_redirects=True
                )

                if r.status_code < 400:
                    results.append({
                        "url": url,
                        "status": r.status_code,
                        "length": len(r.text)
                    })

            except requests.RequestException:
                continue

        # Si HTTPS funciona, no probamos HTTP
        if results and scheme == "https":
            break

    return {
        "module": "endpoint_discovery",
        "target": target,
        "results": results
    }
