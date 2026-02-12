PROFILES = {
    "passive": {
        "network": {
            "timeout": 6,
            "follow_redirects": False,
            "retries": 2,
            "backoff_factor": 0.3,
            "max_rps": 3,
        },
        "stealth": {
            "random_user_agent": True,
            "delay": 0.3,
            "respect_robots": True,
        },
        "dns": {
            "bruteforce": False,
            "max_subdomains": 100,
        },
        "http": {
            "threads": 5,
        },
        "endpoint": {
            "wordlist": "small",
            "methods": ["GET"],
            "max_paths": 200,
        },
        "tech": {
            "graphql": False,
            "extra_paths": False,
        },
    },
    "balanced": {
        "network": {
            "timeout": 6,
            "follow_redirects": False,
            "retries": 3,
            "backoff_factor": 0.25,
            "max_rps": 10,
        },
        "stealth": {
            "random_user_agent": True,
            "delay": 0.1,
            "respect_robots": False,
        },
        "dns": {
            "bruteforce": True,
            "max_subdomains": 500,
        },
        "http": {
            "threads": 15,
        },
        "endpoint": {
            "wordlist": "medium",
            "methods": ["GET", "HEAD"],
            "max_paths": 800,
        },
        "tech": {
            "graphql": True,
            "extra_paths": False,
        },
    },
    "aggressive": {
        "network": {
            "timeout": 4,
            "follow_redirects": True,
            "retries": 2,
            "backoff_factor": 0.2,
            "max_rps": 30,
        },
        "stealth": {
            "random_user_agent": False,
            "delay": 0.0,
            "respect_robots": False,
        },
        "dns": {
            "bruteforce": True,
            "max_subdomains": 2000,
        },
        "http": {
            "threads": 40,
        },
        "endpoint": {
            "wordlist": "large",
            "methods": ["GET", "HEAD", "OPTIONS"],
            "max_paths": 3000,
        },
        "tech": {
            "graphql": True,
            "extra_paths": True,
        },
    },
}


def get_profile(profile: str) -> dict:
    return PROFILES.get(profile, PROFILES["balanced"])


def get_http_config(profile: str) -> dict:
    cfg = get_profile(profile)
    network_cfg = cfg.get("network", {})
    http_cfg = cfg.get("http", {})
    return {
        "timeout": network_cfg.get("timeout", 6),
        "follow_redirects": network_cfg.get("follow_redirects", False),
        "retries": network_cfg.get("retries", 2),
        "backoff_factor": network_cfg.get("backoff_factor", 0.2),
        "max_rps": network_cfg.get("max_rps", 10),
        "threads": http_cfg.get("threads", 10),
    }
