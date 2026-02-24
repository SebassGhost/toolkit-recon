import time
from datetime import datetime

from toolkit_recon import SCHEMA_VERSION
from toolkit_recon.core.correlation import build_correlation
from toolkit_recon.core.plugins import build_default_plugins
from toolkit_recon.recon.domain_enum.domain_enum import run as domain_enum_run
from toolkit_recon.recon.endpoint_discovery.endpoints import run as endpoint_discovery_run
from toolkit_recon.recon.osint_username.username import run as osint_username_run
from toolkit_recon.recon.subdomain_enum.sub_enum import run as subdomain_enum_run
from toolkit_recon.recon.tech_fingerprint.fingerprint import run as tech_fingerprint_run
from toolkit_recon.utils.output import save_full_recon, save_output


def _subdomains_for_followup(target: str, subdomain_data: dict) -> list[str]:
    subdomains = [
        item.get("subdomain")
        for item in subdomain_data.get("results", [])
        if isinstance(item, dict) and item.get("subdomain")
    ]
    if target not in subdomains:
        subdomains.insert(0, target)
    return subdomains


def run(target: str, profile: str = "balanced", osint_user: str | None = None) -> dict:
    results = {
        "schema_version": SCHEMA_VERSION,
        "target": target,
        "profile": profile,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "modules": {},
        "metrics": {},
        "analysis": {},
    }

    runners = {
        "domain_enum": domain_enum_run,
        "subdomain_enum": subdomain_enum_run,
        "endpoint_discovery": endpoint_discovery_run,
        "tech_fingerprint": tech_fingerprint_run,
        "osint_username": osint_username_run,
    }
    plugins = build_default_plugins(runners)
    context = {
        "target": target,
        "profile": profile,
        "osint_user": osint_user,
        "followup_targets": [target],
    }

    for plugin in plugins:
        if plugin.optional and not osint_user:
            continue

        print(f"[*] {plugin.name}")
        start = time.perf_counter()

        if plugin.scope == "target":
            try:
                data = plugin.runner(target, profile)
            except Exception as exc:
                data = {"error": str(exc)}

            results["modules"][plugin.name] = data
            results["metrics"][plugin.name] = plugin.aggregator(data, context)
            results["metrics"][plugin.name]["duration_seconds_total"] = round(
                time.perf_counter() - start, 4
            )
            save_output(target, plugin.output_name, data)

            if plugin.name == "subdomain_enum" and isinstance(data, dict):
                context["followup_targets"] = _subdomains_for_followup(target, data)

        elif plugin.scope == "per_subdomain":
            by_target = {}
            for host in context["followup_targets"]:
                try:
                    by_target[host] = plugin.runner(host, profile)
                except Exception as exc:
                    by_target[host] = {"error": str(exc)}

            results["modules"][plugin.name] = by_target
            results["metrics"][plugin.name] = plugin.aggregator(by_target, context)
            results["metrics"][plugin.name]["duration_seconds_total"] = round(
                time.perf_counter() - start, 4
            )
            save_output(target, plugin.output_name, by_target)

        elif plugin.scope == "optional_target":
            try:
                data = plugin.runner(osint_user or "", profile)
            except Exception as exc:
                data = {"error": str(exc)}

            results["modules"][plugin.name] = data
            results["metrics"][plugin.name] = plugin.aggregator(data, context)
            results["metrics"][plugin.name]["duration_seconds_total"] = round(
                time.perf_counter() - start, 4
            )
            save_output(target, plugin.output_name, data)

    correlation = build_correlation(results)
    results["analysis"]["correlation"] = correlation
    save_output(target, "correlation", correlation)

    save_full_recon(target, results)
    return results

