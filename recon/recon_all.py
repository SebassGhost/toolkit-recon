import json
import os

from recon.domain_enum.domain_enum import run as domain_enum_run
from recon.subdomain_enum.sub_enum import run as subdomain_enum_run
from recon.endpoint_discovery.endpoints import run as endpoint_discovery_run
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

    # Crear carpeta de salida
    output_dir = os.path.join("output", target)
    os.makedirs(output_dir, exist_ok=True)

    # Guardar resultados en JSON
    output_file = os.path.join(output_dir, "recon.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"[+] Results saved to {output_file}")

    return results
