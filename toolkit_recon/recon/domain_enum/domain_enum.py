import socket
import time

from toolkit_recon import SCHEMA_VERSION
from toolkit_recon.config.profiles import get_profile


# =========================
# DNS RESOLUTION
# =========================
def resolve_domain(target: str) -> dict:
    records = {
        "A": [],
        "AAAA": []
    }

    # IPv4
    try:
        for res in socket.getaddrinfo(target, None, socket.AF_INET):
            records["A"].append(res[4][0])
    except Exception:
        pass

    # IPv6
    try:
        for res in socket.getaddrinfo(target, None, socket.AF_INET6):
            records["AAAA"].append(res[4][0])
    except Exception:
        pass

    # eliminar duplicados
    records["A"] = list(set(records["A"]))
    records["AAAA"] = list(set(records["AAAA"]))

    return records


# =========================
# MAIN RUNNER
# =========================
def run(target: str, profile: str = "balanced") -> dict:
    start = time.perf_counter()
    cfg = get_profile(profile)
    if not cfg:
        raise ValueError(f"Invalid profile: {profile}")

    result = {
        "domain": target,
        "records": {
            "A": [],
            "AAAA": []
        },
        "errors": []
    }

    try:
        records = resolve_domain(target)
        result["records"] = records

        if not records["A"] and not records["AAAA"]:
            result["errors"].append("No DNS records resolved")

    except socket.gaierror as e:
        result["errors"].append(str(e))
    except Exception as e:
        result["errors"].append(f"Unhandled error: {str(e)}")

    return {
        "schema_version": SCHEMA_VERSION,
        "module": "domain_enum",
        "target": target,
        "profile": profile,
        "count": len(result["records"]["A"]) + len(result["records"]["AAAA"]),
        "results": result,
        "metrics": {
            "errors": len(result["errors"]),
            "duration_seconds": round(time.perf_counter() - start, 4),
        },
    }
