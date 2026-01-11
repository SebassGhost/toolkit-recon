import os
from .resolver import resolve, detect_wildcard
from .sources.passive import run as passive_enum

WORDLIST_FILE = os.path.join(
    os.path.dirname(__file__),
    "wordlists",
    "subdomains.txt"
)


def load_wordlist():
    if not os.path.exists(WORDLIST_FILE):
        return []

    with open(WORDLIST_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def run(target, use_passive=True):
    results = []
    seen = set()

    # -------------------------
    # Wildcard detection
    # -------------------------
    wildcard_info = detect_wildcard(target)
    wildcard_ips = wildcard_info.get("ips", [])

    if wildcard_info.get("wildcard"):
        print(f"[!] Wildcard DNS detected ({', '.join(wildcard_ips)})")
    else:
        print("[+] No wildcard DNS detected")

    # -------------------------
    # Active / Bruteforce
    # -------------------------
    wordlist = load_wordlist()

    for word in wordlist:
        subdomain = f"{word}.{target}"
        ips = resolve(subdomain)

        if not ips:
            continue

        # Skip pure wildcard matches
        if wildcard_ips and all(ip in wildcard_ips for ip in ips):
            continue

        if subdomain in seen:
            continue

        seen.add(subdomain)
        results.append({
            "subdomain": subdomain,
            "ip": ips[0],
            "source": "brute"
        })

    # -------------------------
    # Passive enumeration
    # -------------------------
    if use_passive:
        passive_subs = passive_enum(target)

        for subdomain in passive_subs:
            if subdomain in seen:
                continue

            ips = resolve(subdomain)
            if not ips:
                continue

            if wildcard_ips and all(ip in wildcard_ips for ip in ips):
                continue

            seen.add(subdomain)
            results.append({
                "subdomain": subdomain,
                "ip": ips[0],
                "source": "passive"
            })

    return {
        "module": "subdomain_enum",
        "target": target,
        "count": len(results),
        "wildcard": wildcard_info.get("wildcard", False),
        "wildcard_ips": wildcard_ips,
        "results": results
    }
