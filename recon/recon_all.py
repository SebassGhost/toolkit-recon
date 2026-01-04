from recon.domain_enum.domain_enum import run as domain_enum
# luego agregamos más

def run_all(target):
    results = {}

    print("[*] Domain enumeration...")
    results["domain_enum"] = domain_enum(target)

    return results
