import random
import string
from functools import lru_cache

import dns.resolver

from toolkit_recon.config.profiles import get_http_config


# -------------------------
# DNS Resolve (cached)
# -------------------------
@lru_cache(maxsize=4096)
def _resolve_cached(domain: str, timeout: float):
    resolver = dns.resolver.Resolver(configure=True)
    resolver.lifetime = timeout
    resolver.timeout = timeout
    try:
        answers = resolver.resolve(domain, "A")
        return sorted({r.to_text() for r in answers})
    except Exception:
        return []


def resolve(domain: str, profile: str = "balanced"):
    """
    Resolve domain to IPs.
    Uses cache to avoid repeated queries.
    """
    http_cfg = get_http_config(profile)
    timeout = http_cfg.get("timeout", 6)

    ips = _resolve_cached(domain, float(timeout))
    return ips if ips else None


# -------------------------
# Wildcard detection
# -------------------------
def detect_wildcard(target: str, profile: str = "balanced") -> dict:
    """
    Detects wildcard DNS by resolving random subdomains.
    """
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
