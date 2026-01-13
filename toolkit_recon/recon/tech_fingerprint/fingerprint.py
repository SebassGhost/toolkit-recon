import requests
from toolkit_recon.config.profiles import PROFILES


# =========================
# MAIN RUNNER
# =========================
def run(target: str, profile: str = "balanced") -> dict:
    cfg = PROFILES.get(profile)
    if not cfg:
        raise ValueError(f"Invalid profile: {profile}")

    tech_cfg = cfg["tech"]
    timeout = tech_cfg.get("timeout", 6)

    enable_graphql = tech_cfg.get("graphql", False)
    extra_paths = tech_cfg.get("extra_paths", False)

    # -------------------------
    # Normalize base URL
    # -------------------------
    if target.startswith("http"):
        base_url = target.rstrip("/")
    else:
        base_url = f"https://{target}".rstrip("/")

    data = {
        "module": "tech_fingerprint",
        "target": target,
        "profile": profile,
        "technologies": {
            "server": None,
            "cdn": None,
            "framework": None,
            "language": None,
            "cookies": [],
            "headers": {},
            "graphql": False
        }
    }

    # -------------------------
    # Base request
    # -------------------------
    try:
        r = requests.get(
            base_url,
            timeout=timeout,
            allow_redirects=True
        )
    except Exception:
        return data

    headers = {k.lower(): v for k, v in r.headers.items()}
    tech = data["technologies"]
    tech["headers"] = headers

    # -------------------------
    # CDN / Server detection
    # -------------------------
    server = headers.get("server", "")
    via = headers.get("via", "")
    cf_ray = headers.get("cf-ray")

    if cf_ray:
        tech["cdn"] = "cloudflare"
    elif "akamai" in via.lower():
        tech["cdn"] = "akamai"
    elif "fastly" in via.lower():
        tech["cdn"] = "fastly"

    tech["server"] = server or None

    # -------------------------
    # Cookies fingerprint
    # -------------------------
    cookies = r.cookies.get_dict()
    tech["cookies"] = list(cookies.keys())

    if "sessionid" in cookies:
        tech["framework"] = "django"
        tech["language"] = "python"
    elif "phpsessid" in cookies:
        tech["language"] = "php"
    elif "connect.sid" in cookies:
        tech["framework"] = "express"
        tech["language"] = "nodejs"

    # -------------------------
    # Headers fingerprint
    # -------------------------
    powered = headers.get("x-powered-by", "").lower()
    if powered:
        if "express" in powered:
            tech["framework"] = "express"
            tech["language"] = "nodejs"
        elif "php" in powered:
            tech["language"] = "php"

    # -------------------------
    # GraphQL probe (profile-based)
    # -------------------------
    if enable_graphql:
        try:
            g = requests.post(
                f"{base_url}/graphql",
                json={"query": "{__typename}"},
                timeout=timeout
            )
            if g.status_code in [200, 400]:
                tech["graphql"] = True
        except Exception:
            pass

    # -------------------------
    # Extra probes (aggressive only)
    # -------------------------
    if extra_paths:
        common_paths = ["/api", "/api/v1", "/admin"]
        for p in common_paths:
            try:
                r2 = requests.get(
                    base_url + p,
                    timeout=timeout,
                    allow_redirects=False
                )
                if r2.status_code in [200, 401, 403]:
                    tech.setdefault("extra_endpoints", []).append(p)
            except Exception:
                pass

    return data
