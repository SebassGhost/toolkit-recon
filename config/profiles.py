PROFILES = {
    "passive": {
        "dns": {
            "bruteforce": False,
            "max_subdomains": 100,
        },
        "http": {
            "threads": 5,
            "timeout": 6,
            "follow_redirects": False,
        },
        "endpoint": {
            "wordlist": "small",
            "methods": ["GET"],
        }
    },

    "balanced": {
        "dns": {
            "bruteforce": True,
            "max_subdomains": 500,
        },
        "http": {
            "threads": 15,
            "timeout": 6,
            "follow_redirects": False,
        },
        "endpoint": {
            "wordlist": "medium",
            "methods": ["GET", "HEAD"],
        }
    },

    "aggressive": {
        "dns": {
            "bruteforce": True,
            "max_subdomains": 2000,
        },
        "http": {
            "threads": 40,
            "timeout": 4,
            "follow_redirects": True,
        },
        "endpoint": {
            "wordlist": "large",
            "methods": ["GET", "HEAD", "OPTIONS"],
        }
    }
}
