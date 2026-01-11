import requests

TIMEOUT = 6


def run(target: str):
    if target.startswith("http"):
        base_url = target.rstrip("/")
    else:
        base_url = f"https://{target}".rstrip("/")

    data = {
        "server": None,
        "cdn": None,
        "framework": None,
        "language": None,
        "cookies": [],
        "headers": {},
        "graphql": False
    }

    try:
        r = requests.get(base_url, timeout=TIMEOUT, allow_redirects=True)
    except Exception:
        return data

    headers = {k.lower(): v for k, v in r.headers.items()}
    data["headers"] = headers

    # -------------------------
    # Server / CDN detection
    # -------------------------
    server = headers.get("server", "")
    via = headers.get("via", "")
    cf_ray = headers.get("cf-ray")

    if cf_ray:
        data["cdn"] = "cloudflare"
    elif "akamai" in via.lower():
        data["cdn"] = "akamai"
    elif "fastly" in via.lower():
        data["cdn"] = "fastly"

    data["server"] = server or None

    # -------------------------
    # Cookies fingerprint
    # -------------------------
    cookies = r.cookies.get_dict()
    data["cookies"] = list(cookies.keys())

    if "sessionid" in cookies:
        data["framework"] = "django"
        data["language"] = "python"
    elif "phpsessid" in cookies:
        data["language"] = "php"
    elif "connect.sid" in cookies:
        data["framework"] = "express"
        data["language"] = "nodejs"

    # -------------------------
    # Headers fingerprint
    # -------------------------
    if "x-powered-by" in headers:
        powered = headers["x-powered-by"].lower()
        if "express" in powered:
            data["framework"] = "express"
            data["language"] = "nodejs"
        elif "php" in powered:
            data["language"] = "php"

    # -------------------------
    # GraphQL quick probe
    # -------------------------
    try:
        g = requests.post(
            f"{base_url}/graphql",
            json={"query": "{__typename}"},
            timeout=TIMEOUT
        )
        if g.status_code in [200, 400]:
            data["graphql"] = True
    except Exception:
        pass

    return data
