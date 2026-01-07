import dns.resolver
import random
import string


def resolve_a(domain: str):
    """
    Resolve A records for a domain.
    Returns list of IPs or None.
    """
    try:
        answers = dns.resolver.resolve(domain, "A")
        return [str(rdata) for rdata in answers]
    except Exception:
        return None


def generate_random_subdomain(base_domain: str) -> str:
    """
    Generate a random subdomain to test wildcard DNS.
    """
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    return f"{rand}.{base_domain}"


def detect_wildcard(domain: str):
    """
    Detect wildcard DNS by resolving a random subdomain.
    Returns list of wildcard IPs or None.
    """
    fake_sub = generate_random_subdomain(domain)
    return resolve_a(fake_sub)
