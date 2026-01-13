import socket
import random
import string
from functools import lru_cache
from toolkit_recon.config.profiles import PROFILES


# -------------------------
# DNS Resolve (cached)
# -------------------------
@lru_cache(maxsize=4096)
def _resolve_cached(domain: str):
    try:
        return socket.gethostbyname_ex(domain)[2]
    except Exception:
        return []


def resolve(domain: str, profile: str = "balanced"):
    """
    Resolve domain to IPs.
    Uses cache to avoid repeated queries.
    """
    cfg = PROFILES.get(profile, PROFILES["balanced"])
    timeout = cfg["http"].get("timeout", 6)

    # socket timeout (stealth / network)
    socket.setdefaulttimeout(timeout)

    ips = _resolve_cached(domain)
    return ips if ips else None


# -------------------------
# Wildcard detection
# -------------------------
def detect_wildcard(target: str, profile: str = "balanced") -> dict:
    """
    Detects wildcard DNS by resolving random subdomains.
    """
    cfg = PROFILES.get(profile, PROFILES["balanced"])
    timeout = cfg["http"].get("timeout", 6)

    socket.setdefaulttimeout(timeout)

    random_labels = [
        "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
        for _ in range(2)
    ]

    resolved_ips = set()

    for label in random_labels:
        test_domain = f"{label}.{target}"
        ips = resolve(test_domain, profile=profile)
        if ips:
            resolved_ips.update(ips)

    return {
        "wildcard": bool(resolved_ips),
        "ips": list(resolved_ips)
    }
