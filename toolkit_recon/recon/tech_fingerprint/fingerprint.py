import time
import random
import requests

USER_AGENTS = [
    "Mozilla/5.0",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
]


def run(target: str, profile: dict) -> dict:
    network = profile.get("network", {})
    stealth = profile.get("stealth", {})
    tech_cfg = profile.get("tech", {})

    timeout = network.get("timeout", 6)
    follow_redirects = network.get("follow_redirects", False)

    delay = stealth.get("delay", 0)
    random_ua = stealth.get("random_user_agent", False)

    headers = {}
    if random_ua:
        headers["User-Agent"] = random.choice(USER_AGENTS)

    if delay > 0:
        time.sleep(delay)

    if target.startswith("http"):
        base_url = target.rstrip("/")
    else:
        base_url = f"https://{target}".rstrip("/")

    data = {
        "module": "tech_fingerprint",
        "target": target,
        "server": None,
        "cdn": None,
        "framework": None,
        "language": None,
        "cookies": [],
        "headers": {},
        "graphql": False
    }

    try:
        r = requests.get(
            base_url,
            timeout=timeout,
            allow_redirects=follow_redirects,
            headers=headers
        )
    except Exception as e:
        data["error"] = str(e)
        return data

    response_headers = {k.lower(): v for k, v in r.headers.items()}
    data["headers"] = response_headers

    # --- CDN / Server ---
    if "cf-ray" in response_headers:
        data["cdn"] = "cloudflare"
    elif "akamai" in response_headers.get("via", "").lower():
        data["cdn"] = "akamai"

    data["server"] = response_headers.get("server")

    # --- Cookies ---
    cookies = r.cookies.get_dict()
    data["cookies"] = list(cookies.keys())

    if "sessionid" in cookies:
        data["framework"] = "django"
        data["language"] = "python"
    elif "phpsessid" in cookies:
        data["language"] = "php"

    # --- GraphQL (controlado por perfil) ---
    if tech_cfg.get("graphql", False):
        try:
            g = requests.post(
                f"{base_url}/graphql",
                json={"query": "{__typename}"},
                timeout=timeout,
                headers=headers
            )
            if g.status_code in (200, 400):
                data["graphql"] = True
        except Exception:
            pass

    return data
