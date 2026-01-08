import os

from .resolver import resolve, detect_wildcard
from .passive import run as passive_enum


WORDLIST_FILE = os.path.join(os.path.dirname(__file__), "wordlist.txt")


def load_wordlist():
    if not os.path.exists(WORDLIST_FILE):
        return []

    with open(WORDLIST_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def run(target, use_passive=True):
    results = []
    seen = set()

    wildcard_ip = detect_wildcard(target)

    if wildcard_ip:
        print(f"[!] Wildcard DNS detected ({wildcard_ip})")
    else:
        print("[+] No wildcard DNS detected")

    # Active brute-force
    wordlist = load_wordlist()

    for word in wordlist:
        subdomain = f"{word}.{target}"
        ip = resolve(subdomain)

        if not ip:
            continue

        if wildcard_ip and ip == wildcard_ip:
            continue

        seen.add(subdomain)
        results.append({
            "subdomain": subdomain,
            "ip": ip,
            "source": "brute"
        })

    # Passive enumeration
    if use_passive:
        passive_subs = passive_enum(target)

        for subdomain in passive_subs:
            if subdomain in seen:
                continue

            ip = resolve(subdomain)
            if not ip:
                continue

            if wildcard_ip and ip == wildcard_ip:
                continue

            results.append({
                "subdomain": subdomain,
                "ip": ip,
                "source": "passive"
            })

    return {
        "module": "subdomain_enum",
        "target": target,
        "count": len(results),
        "wildcard": bool(wildcard_ip),
        "results": results
    }
