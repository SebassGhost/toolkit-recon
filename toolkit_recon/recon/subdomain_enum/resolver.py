import socket
import random
import string


def resolve(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None


def detect_wildcard(target):
    """
    Generates a random subdomain and checks if it resolves.
    If it does, the domain uses wildcard DNS.
    """
    random_label = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=12)
    )
    test_domain = f"{random_label}.{target}"

    return resolve(test_domain)  # None = no wildcard
