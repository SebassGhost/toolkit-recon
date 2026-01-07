import socket
import random
import string
import os

WORDLIST_FILE = os.path.join(os.path.dirname(__file__), "wordlist.txt")


def load_wordlist():
    if not os.path.exists(WORDLIST_FILE):
        return []
    with open(WORDLIST_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def resolve(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None


def detect_wildcard(target):
    """
    Generates a random subdomain and checks if it resolves.
    If it does, the domain uses wildcard DNS.
    """
    random_label = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=12)
    )
    test_domain = f"{random_label}.{target}"

    ip = resolve(test_domain)
    return ip  # None = no wildcard, IP = wildcard baseline


def run(target):
    wordlist = load_wordlist()

    results = []
    wildcard_ip = detect_wildcard(target)

    if wildcard_ip:
        print(f"[!] Wildcard DNS detected ({wildcard_ip})")
    else:
        print("[+] No wildcard DNS detected")

    for word in wordlist:
        subdomain = f"{word}.{target}"
        ip = resolve(subdomain)

        if not ip:
            continue

        # Filter wildcard false positives
        if wildcard_ip and ip == wildcard_ip:
            continue

        results.append({
            "subdomain": subdomain,
            "ip": ip
        })

    return {
        "module": "subdomain_enum",
        "target": target,
        "count": len(results),
        "wildcard": bool(wildcard_ip),
        "results": results
    }
