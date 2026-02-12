import random
import socket
import string
import time


def random_subdomain(domain, length=12):
    rand = "".join(random.choice(string.ascii_lowercase) for _ in range(length))
    return f"{rand}.{domain}"


def resolve(domain):
    try:
        _, _, ips = socket.gethostbyname_ex(domain)
        return list(set(ips))
    except socket.gaierror:
        return []
    except Exception:
        return []


def detect_wildcard(domain, tests=3, delay=0.3):
    """
    Detect DNS wildcard behavior.

    Always returns a dict:
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

        # Small delay to avoid DNS caching / rate-limit issues
        time.sleep(delay)

    # No fake subdomain resolved → no wildcard
    if not results:
        return {
            "wildcard": False,
            "ips": []
        }

    # If all fake subdomains resolve to the same IPs → wildcard
    first = results[0]
    wildcard = all(r == first for r in results)

    return {
        "wildcard": wildcard,
        "ips": list(first) if wildcard else []
    }
