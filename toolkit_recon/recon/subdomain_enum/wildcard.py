import random
import string
import socket


def random_subdomain(domain, length=12):
    rand = "".join(random.choice(string.ascii_lowercase) for _ in range(length))
    return f"{rand}.{domain}"


def resolve(domain):
    try:
        return list(set(socket.gethostbyname_ex(domain)[2]))
    except socket.gaierror:
        return []


def detect_wildcard(domain, tests=3):
    """
    Detects DNS wildcard behavior.
    Returns:
        {
            "wildcard": bool,
            "ips": list
        }
    """

    results = []

    for _ in range(tests):
        fake = random_subdomain(domain)
        ips = resolve(fake)
        if ips:
            results.append(tuple(sorted(ips)))

    if not results:
        return {
            "wildcard": False,
            "ips": []
        }

    # All fake subdomains resolve to same IPs
    wildcard = all(r == results[0] for r in results)

    return {
        "wildcard": wildcard,
        "ips": list(results[0]) if wildcard else []
    }
