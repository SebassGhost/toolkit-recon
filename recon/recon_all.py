from recon.domain_enum.domain_enum import run as domain_enum_run
from recon.subdomain_enum.sub_enum import run as subdomain_enum_run
# más módulos se agregarán aquí

def run_all(target):
    results = {
        "target": target,
        "recon": {}
    }

    print("[*] Running domain enumeration...")
    results["recon"]["domain_enum"] = domain_enum_run(target)

    print("[*] Running subdomain enumeration...")
    results["recon"]["subdomain_enum"] = subdomain_enum_run(target)

    return results
