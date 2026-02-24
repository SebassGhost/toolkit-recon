def _risk_score_for_path(path: str) -> tuple[int, list[str]]:
    path_l = (path or "").lower()
    score = 0
    reasons = []

    keyword_scores = {
        "admin": 30,
        "login": 25,
        "auth": 20,
        "dashboard": 20,
        "api": 10,
        "graphql": 25,
        "upload": 20,
        "debug": 15,
        "internal": 15,
    }
    for key, value in keyword_scores.items():
        if key in path_l:
            score += value
            reasons.append(f"path:{key}")

    return score, reasons


def build_correlation(results: dict) -> dict:
    modules = results.get("modules", {})
    endpoint_map = modules.get("endpoint_discovery", {})
    tech_map = modules.get("tech_fingerprint", {})
    subdomain_map = modules.get("subdomain_enum", {})

    known_subdomains = {
        item.get("subdomain")
        for item in subdomain_map.get("results", [])
        if isinstance(item, dict) and item.get("subdomain")
    }

    findings = []
    for host, endpoint_data in endpoint_map.items():
        if not isinstance(endpoint_data, dict):
            continue

        tech_data = tech_map.get(host, {})
        tech = tech_data.get("technologies", {}) if isinstance(tech_data, dict) else {}
        framework = tech.get("framework")
        language = tech.get("language")
        graphql = bool(tech.get("graphql"))

        for entry in endpoint_data.get("results", []):
            if not isinstance(entry, dict):
                continue
            base_score, reasons = _risk_score_for_path(entry.get("path", ""))
            if entry.get("status") in (401, 403):
                base_score += 10
                reasons.append("status:restricted")
            if graphql and "graphql" in (entry.get("path", "").lower()):
                base_score += 10
                reasons.append("tech:graphql")
            if framework:
                base_score += 5
                reasons.append(f"framework:{framework}")
            sensitive_tokens = ("admin", "api", "staging", "dev")
            if host in known_subdomains and any(k in host for k in sensitive_tokens):
                base_score += 10
                reasons.append("subdomain:sensitive-name")

            if base_score <= 0:
                continue

            findings.append(
                {
                    "host": host,
                    "path": entry.get("path"),
                    "url": entry.get("url"),
                    "status": entry.get("status"),
                    "score": base_score,
                    "reasons": reasons,
                    "tech": {
                        "framework": framework,
                        "language": language,
                        "graphql": graphql,
                    },
                }
            )

    findings.sort(key=lambda x: x.get("score", 0), reverse=True)
    critical = [f for f in findings if f.get("score", 0) >= 60]
    high = [f for f in findings if 40 <= f.get("score", 0) < 60]
    medium = [f for f in findings if 20 <= f.get("score", 0) < 40]

    return {
        "version": "1",
        "top_findings": findings[:25],
        "stats": {
            "total_findings": len(findings),
            "critical": len(critical),
            "high": len(high),
            "medium": len(medium),
        },
    }
