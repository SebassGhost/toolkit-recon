import requests

from toolkit_recon.config.profiles import get_profile, get_http_config


# -------------------------
# Utils
# -------------------------
def normalize_url(target: str) -> str:
    if target.startswith("http"):
        return target.rstrip("/")
    return f"https://{target}".rstrip("/")


# -------------------------
# Main runner
# -------------------------
def run(target: str, profile: str = "balanced") -> dict:
    """
    Technology fingerprinting module.
    Lightweight, profile-aware and stealth-conscious.
    """

    cfg = get_profile(profile)
    http_cfg = get_http_config(profile)
    stealth_cfg = cfg.get("stealth", {})
    tech_cfg = cfg.get("tech", {})

    base_url = normalize_url(target)

    data = {
        "module": "tech_fingerprint",
        "target": target,
        "technologies": {
            "server": None,
            "cdn": None,
            "framework": None,
            "language": None,
            "cookies": [],
            "graphql": False,
        },
        "headers": {},
    }

    session = requests.Session()
    session.headers.update(
        {"User-Agent": "toolkit-recon/1.0"}
        if not stealth_cfg.get("random_user_agent", False)
        else {"User-Agent": "Mozilla/5.0 toolkit-recon"}
    )

    # -------------------------
    # Base request
    # -------------------------
    try:
        r = session.get(
            base_url,
            timeout=http_cfg["timeout"],
            allow_redirects=http_cfg["follow_redirects"]
        )
    except Exception:
        return data

    headers = {k.lower(): v for k, v in r.headers.items()}
    data["headers"] = headers

    # -------------------------
    # Server / CDN detection
    # -------------------------
    server = headers.get("server")
    via = headers.get("via", "").lower()
    cf_ray = headers.get("cf-ray")

    if cf_ray:
        data["technologies"]["cdn"] = "cloudflare"
    elif "akamai" in via:
        data["technologies"]["cdn"] = "akamai"
    elif "fastly" in via:
        data["technologies"]["cdn"] = "fastly"

    data["technologies"]["server"] = server

    # -------------------------
    # Cookies fingerprint
    # -------------------------
    cookies = r.cookies.get_dict()
    data["technologies"]["cookies"] = list(cookies.keys())

    if "sessionid" in cookies:
        data["technologies"]["framework"] = "django"
        data["technologies"]["language"] = "python"
    elif "phpsessid" in cookies:
        data["technologies"]["language"] = "php"
    elif "connect.sid" in cookies:
        data["technologies"]["framework"] = "express"
        data["technologies"]["language"] = "nodejs"

    # -------------------------
    # Headers fingerprint
    # -------------------------
    powered = headers.get("x-powered-by", "").lower()

    if powered:
        if "express" in powered:
            data["technologies"]["framework"] = "express"
            data["technologies"]["language"] = "nodejs"
        elif "php" in powered:
            data["technologies"]["language"] = "php"

    # -------------------------
    # GraphQL probe (profile aware)
    # -------------------------
    # Only in balanced / aggressive
    if tech_cfg.get("graphql", profile != "passive"):
        try:
            g = session.post(
                f"{base_url}/graphql",
                json={"query": "{__typename}"},
                timeout=http_cfg["timeout"],
                allow_redirects=http_cfg["follow_redirects"],
            )
            if g.status_code in (200, 400):
                data["technologies"]["graphql"] = True
        except Exception:
            pass

    return data
