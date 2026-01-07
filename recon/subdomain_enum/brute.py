import os


def load_wordlist():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "wordlists", "subdomains.txt")

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def run(domain):
    """
    Genera subdominios por fuerza bruta (sin validarlos)
    """
    words = load_wordlist()
    results = set()

    for word in words:
        results.add(f"{word}.{domain}")

    return results
