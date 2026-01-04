from recon.domain_enum.domain_enum import run as domain_enum_run
# más módulos se agregarán aquí

def run_all(target):
    results = {
        "target": target,
        "recon": {}
    }

    print("[*] Running domain enumeration...")
    results["recon"]["domain_enum"] = domain_enum_run(target)

    return results
