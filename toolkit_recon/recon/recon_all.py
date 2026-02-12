from datetime import datetime
import time

from toolkit_recon.recon.subdomain_enum.sub_enum import run as subdomain_enum_run
from toolkit_recon.recon.endpoint_discovery.endpoints import run as endpoint_discovery_run
from toolkit_recon.recon.tech_fingerprint.fingerprint import run as tech_fingerprint_run
from toolkit_recon.utils.output import save_full_recon, save_output


def run(target: str, profile: str = "balanced") -> dict:
    results = {
        "target": target,
        "profile": profile,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "modules": {},
        "metrics": {},
    }

    # =========================
    # Subdomain Enumeration
    # =========================
    print("[*] Subdomain enumeration")
    start = time.perf_counter()
    try:
        sub_data = subdomain_enum_run(target, profile=profile)
        results["modules"]["subdomain_enum"] = sub_data
        save_output(target, "subdomains", sub_data)
    except Exception as e:
        results["modules"]["subdomain_enum"] = {"error": str(e)}
    sub_fallback_duration = round(time.perf_counter() - start, 4)
    results["metrics"]["subdomain_enum"] = (
        results["modules"]
        .get("subdomain_enum", {})
        .get("metrics", {"duration_seconds": sub_fallback_duration})
    )
    results["metrics"]["subdomain_enum"]["count"] = (
        results["modules"].get("subdomain_enum", {}).get("count", 0)
    )

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
    endpoint_metrics = {
        "targets_scanned": 0,
        "total_paths": 0,
        "attempted": 0,
        "completed": 0,
        "errors": 0,
        "retried_requests": 0,
        "duration_seconds": 0.0,
    }
    start = time.perf_counter()

    for sub in subdomains:
        try:
            data = endpoint_discovery_run(
                sub,
                profile=profile
            )
            endpoint_data[sub] = data
            m = data.get("metrics", {})
            endpoint_metrics["targets_scanned"] += 1
            endpoint_metrics["total_paths"] += m.get("total_paths", 0)
            endpoint_metrics["attempted"] += m.get("attempted", 0)
            endpoint_metrics["completed"] += m.get("completed", 0)
            endpoint_metrics["errors"] += m.get("errors", 0)
            endpoint_metrics["retried_requests"] += m.get("retried_requests", 0)
        except Exception as e:
            endpoint_data[sub] = {"error": str(e)}

    endpoint_metrics["duration_seconds"] = round(time.perf_counter() - start, 4)
    results["modules"]["endpoint_discovery"] = endpoint_data
    results["metrics"]["endpoint_discovery"] = endpoint_metrics
    save_output(target, "endpoints", endpoint_data)

    # =========================
    # Tech Fingerprint
    # =========================
    print("[*] Tech fingerprint")
    tech_data = {}
    start = time.perf_counter()

    for sub in subdomains:
        try:
            tech_data[sub] = tech_fingerprint_run(
                sub,
                profile=profile
            )
        except Exception as e:
            tech_data[sub] = {"error": str(e)}

    results["modules"]["tech_fingerprint"] = tech_data
    tech_duration = round(time.perf_counter() - start, 4)
    tech_requests_attempted = 0
    tech_requests_successful = 0
    tech_errors = 0
    tech_graphql_probes = 0
    for item in tech_data.values():
        if not isinstance(item, dict):
            continue
        m = item.get("metrics", {})
        tech_requests_attempted += m.get("requests_attempted", 0)
        tech_requests_successful += m.get("requests_successful", 0)
        tech_errors += m.get("errors", 0)
        tech_graphql_probes += 1 if m.get("graphql_probe_attempted") else 0

    results["metrics"]["tech_fingerprint"] = {
        "duration_seconds": tech_duration,
        "targets_scanned": len(tech_data),
        "requests_attempted": tech_requests_attempted,
        "requests_successful": tech_requests_successful,
        "errors": tech_errors,
        "graphql_probes_attempted": tech_graphql_probes,
    }
    save_output(target, "tech_fingerprint", tech_data)
    save_full_recon(target, results)

    return results
