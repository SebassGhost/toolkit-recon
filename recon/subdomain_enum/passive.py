import requests
import re


def from_crtsh(domain):
    """
    Obtiene subdominios desde crt.sh (certificados SSL públicos)
    """
    subdomains = set()

    url = f"https://crt.sh/?q=%25.{domain}&output=json"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return subdomains

        data = r.json()

        for entry in data:
            names = entry.get("name_value", "")
            for name in names.split("\n"):
                if "*" not in name:
                    subdomains.add(name.strip())

    except Exception:
        pass

    return subdomains


def run(domain):
    """
    Ejecuta todas las técnicas pasivas
    """
    results = set()

    results.update(from_crtsh(domain))

    return results
