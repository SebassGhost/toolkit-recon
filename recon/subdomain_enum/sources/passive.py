import requests


def from_crtsh(target):
    """
    Fetch subdomains from crt.sh
    """
    url = f"https://crt.sh/?q=%25.{target}&output=json"
    subdomains = set()

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return subdomains

        data = r.json()
        for entry in data:
            name = entry.get("name_value", "")
            for sub in name.split("\n"):
                if sub.endswith(target):
                    subdomains.add(sub.strip())
    except Exception:
        pass

    return subdomains


def from_threatcrowd(target):
    """
    Fetch subdomains from ThreatCrowd
    """
    url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={target}"
    subdomains = set()

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        for sub in data.get("subdomains", []):
            subdomains.add(sub.strip())
    except Exception:
        pass

    return subdomains


def run(target):
    results = set()

    results.update(from_crtsh(target))
    results.update(from_threatcrowd(target))

    return list(results)
