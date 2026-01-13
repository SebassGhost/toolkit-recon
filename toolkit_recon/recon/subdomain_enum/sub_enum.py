import os
from toolkit_recon.config.profiles import PROFILES
from .resolver import resolve, detect_wildcard
from .sources.passive import run as passive_enum


WORDLIST_FILE = os.path.join(
    os.path.dirname(__file__),
    "wordlists",
    "subdomains.txt"
)


# -------------------------
# Load wordlist
# -------------------------
def load_wordlist():
    if not os.path.exists(WORDLIST_FILE):
        return []

    with open(WORDLIST_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


# -------------------------
# Main runner
# -------------------------
def run(target: str, profile: str = "balanced") -> dict:
    cfg = PROFILES.get(profile, PROFILES["balanced"])
    dns_cfg = cfg["dns"]

    bruteforce_enabled = dns_cfg.get("bruteforce", True)
    max_subdomains = dns_cfg.get("max_subdomains", 500)

    results = []
    seen = set()

    # -------------------------
    # Wildcard detection
    # -------------------------
    wildcard_info = detect_wildcard(target)
    wildcard_ips = wildcard_info.get("ips", [])
    wildcard_enabled = wildcard_info.get("wildcard", False)

    # -------------------------
    # Active / Bruteforce enum
    # -------------------------
    if bruteforce_enabled:
        wordlist = load_wordlist()

        for word in wordlist:
            if len(results) >= max_subdomains:
                break

            subdomain = f"{word}.{target}"

            if subdomain in seen:
                continue

            ips = resolve(subdomain)
            if not ips:
                continue

            # Skip wildcard-only results
            if wildcard_enabled and all(ip in wildcard_ips for ip in ips):
                continue

            seen.add(subdomain)
            results.append({
                "subdomain": subdomain,
                "ip": ips[0],
                "source": "bruteforce"
            })

    # -------------------------
    # Passive enum
    # -------------------------
    try:
        passive_subs = passive_enum(target)
    except Exception:
        passive_subs = []

    for subdomain in passive_subs:
        if len(results) >= max_subdomains:
            break

        if subdomain in seen:
            continue

        ips = resolve(subdomain)
        if not ips:
            continue

        if wildcard_enabled and all(ip in wildcard_ips for ip in ips):
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
        "profile": profile,
        "count": len(results),
        "wildcard": wildcard_enabled,
        "wildcard_ips": wildcard_ips,
        "results": results
    }
