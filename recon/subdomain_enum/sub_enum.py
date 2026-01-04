import socket

def run(domain):
    subdomains = []
    wordlist = ["www", "mail", "ftp", "dev", "test", "api"]

    for sub in wordlist:
        subdomain = f"{sub}.{domain}"
        try:
            socket.gethostbyname(subdomain)
            subdomains.append(subdomain)
        except socket.gaierror:
            pass

    return {
        "module": "subdomain_enum",
        "target": domain,
        "results": subdomains
    }
