import socket
import random
import string


def resolve(domain):
    """
    Resolve a domain to an IP.
    Returns IP string or None.
    """
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None


def random_subdomain(domain, length=12):
    rand = "".join(random.choice(string.ascii_lowercase) for _ in range(length))
    return f"{rand}.{domain}"


def detect_wildcard(domain, tests=2):
    """
    Detect wildcard DNS.
    Returns a dict ALWAYS:
    {
        "wildcard": bool,
        "ip": str | None
    }
    """

    ips = []

    for _ in range(tests):
        fake = random_subdomain(domain)
        ip = resolve(fake)
        if ip:
            ips.append(ip)

    # No random subdomain resolved → no wildcard
    if not ips:
        return {
            "wildcard": False,
            "ip": None
        }

    # If all resolved to same IP → wildcard
    if all(ip == ips[0] for ip in ips):
        return {
            "wildcard": True,
            "ip": ips[0]
        }

    return {
        "wildcard": False,
        "ip": None
    }
