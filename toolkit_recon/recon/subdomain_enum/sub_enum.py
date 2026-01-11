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

    wildcard_info = detect_wildcard(target)

    if wildcard_info["wildcard"]:
        ips = ", ".join(wildcard_info["ips"])
        print(f"[!] Wildcard DNS detected ({ips})")
    else:
        print("[+] No wildcard DNS detected")


    # — Active / Bruteforce
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

    # — Passive sources (crt.sh, ThreatCrowd, etc)
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
