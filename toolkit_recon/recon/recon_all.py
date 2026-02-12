from datetime import datetime

from toolkit_recon.recon.subdomain_enum.sub_enum import run as subdomain_enum_run
from toolkit_recon.recon.endpoint_discovery.endpoints import run as endpoint_discovery_run
from toolkit_recon.recon.tech_fingerprint.fingerprint import run as tech_fingerprint_run
from toolkit_recon.utils.output import save_output, save_recon


def run(target: str, profile: str = "balanced") -> dict:
    results = {
        "target": target,
        "profile": profile,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "modules": {},
    }

    # =========================
    # Subdomain Enumeration
    # =========================
    print("[*] Subdomain enumeration")
    try:
        sub_data = subdomain_enum_run(target, profile=profile)
        results["modules"]["subdomain_enum"] = sub_data
        save_output(target, "subdomains", sub_data)
        save_recon(target, "subdomain_enum", sub_data)
    except Exception as e:
        results["modules"]["subdomain_enum"] = {"error": str(e)}

    subdomains = [
        r["subdomain"]
        for r in results["modules"]
            .get("subdomain_enum", {})
            .get("results", [])
    ]

    if target not in subdomains:
        subdomains.insert(0, target)

    # =========================
    # Endpoint Discovery
    # =========================
    print("[*] Endpoint discovery")
    endpoint_data = {}

    for sub in subdomains:
        try:
            endpoint_data[sub] = endpoint_discovery_run(
                sub,
                profile=profile
            )
        except Exception as e:
            endpoint_data[sub] = {"error": str(e)}

    results["modules"]["endpoint_discovery"] = endpoint_data
    save_output(target, "endpoints", endpoint_data)
    save_recon(target, "endpoint_discovery", endpoint_data)

    # =========================
    # Tech Fingerprint
    # =========================
    print("[*] Tech fingerprint")
    tech_data = {}

    for sub in subdomains:
        try:
            tech_data[sub] = tech_fingerprint_run(
                sub,
                profile=profile
            )
        except Exception as e:
            tech_data[sub] = {"error": str(e)}

    results["modules"]["tech_fingerprint"] = tech_data
    save_output(target, "tech_fingerprint", tech_data)
    save_recon(target, "tech_fingerprint", tech_data)

    return results
