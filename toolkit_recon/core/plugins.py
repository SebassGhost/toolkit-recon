from collections.abc import Callable
from dataclasses import dataclass

Scope = str
Runner = Callable[[str, str], dict]
Aggregator = Callable[[dict, dict], dict]


@dataclass(frozen=True)
class PluginSpec:
    name: str
    scope: Scope
    output_name: str
    runner: Runner
    aggregator: Aggregator
    optional: bool = False


def _aggregate_subdomain(data: dict, _ctx: dict) -> dict:
    metrics = dict(data.get("metrics", {}))
    metrics["count"] = data.get("count", 0)
    return metrics


def _aggregate_domain(data: dict, _ctx: dict) -> dict:
    return dict(data.get("metrics", {}))


def _aggregate_per_subdomain(data: dict, _ctx: dict) -> dict:
    total = {
        "targets_scanned": 0,
        "duration_seconds": 0.0,
    }
    for module_data in data.values():
        if not isinstance(module_data, dict):
            continue
        metrics = module_data.get("metrics", {})
        total["targets_scanned"] += 1
        total["duration_seconds"] += float(metrics.get("duration_seconds", 0.0))
        for key in ("total_paths", "attempted", "completed", "errors", "retried_requests"):
            total[key] = total.get(key, 0) + int(metrics.get(key, 0))
    total["duration_seconds"] = round(total["duration_seconds"], 4)
    return total


def _aggregate_tech(data: dict, _ctx: dict) -> dict:
    total = {
        "targets_scanned": 0,
        "duration_seconds": 0.0,
        "requests_attempted": 0,
        "requests_successful": 0,
        "errors": 0,
        "graphql_probes_attempted": 0,
    }
    for module_data in data.values():
        if not isinstance(module_data, dict):
            continue
        metrics = module_data.get("metrics", {})
        total["targets_scanned"] += 1
        total["duration_seconds"] += float(metrics.get("duration_seconds", 0.0))
        total["requests_attempted"] += int(metrics.get("requests_attempted", 0))
        total["requests_successful"] += int(metrics.get("requests_successful", 0))
        total["errors"] += int(metrics.get("errors", 0))
        total["graphql_probes_attempted"] += 1 if metrics.get("graphql_probe_attempted") else 0
    total["duration_seconds"] = round(total["duration_seconds"], 4)
    return total


def _aggregate_osint(data: dict, _ctx: dict) -> dict:
    return dict(data.get("metrics", {}))


def build_default_plugins(runners: dict[str, Runner]) -> list[PluginSpec]:
    return [
        PluginSpec(
            name="domain_enum",
            scope="target",
            output_name="domain",
            runner=runners["domain_enum"],
            aggregator=_aggregate_domain,
        ),
        PluginSpec(
            name="subdomain_enum",
            scope="target",
            output_name="subdomains",
            runner=runners["subdomain_enum"],
            aggregator=_aggregate_subdomain,
        ),
        PluginSpec(
            name="endpoint_discovery",
            scope="per_subdomain",
            output_name="endpoints",
            runner=runners["endpoint_discovery"],
            aggregator=_aggregate_per_subdomain,
        ),
        PluginSpec(
            name="tech_fingerprint",
            scope="per_subdomain",
            output_name="tech_fingerprint",
            runner=runners["tech_fingerprint"],
            aggregator=_aggregate_tech,
        ),
        PluginSpec(
            name="osint_username",
            scope="optional_target",
            output_name="osint_username",
            runner=runners["osint_username"],
            aggregator=_aggregate_osint,
            optional=True,
        ),
    ]
