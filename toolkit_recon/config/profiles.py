PROFILES = {

    "passive": {
        "network": {
            "timeout": 6,
            "follow_redirects": False
        },
        "stealth": {
            "random_user_agent": True,
            "delay": 0.3,
            "respect_robots": True
        },
        "dns": {
            "bruteforce": False,
            "max_subdomains": 100
        },
        "http": {
            "threads": 5
        },
        "endpoint": {
            "wordlist": "small",
            "methods": ["GET"],
            "max_paths": 200
        },
        "tech": {
            "graphql": False,
            "extra_paths": False
        }
    },

    "balanced": {
        "network": {
            "timeout": 6,
            "follow_redirects": False
        },
        "stealth": {
            "random_user_agent": True,
            "delay": 0.1,
            "respect_robots": False
        },
        "dns": {
            "bruteforce": True,
            "max_subdomains": 500
        },
        "http": {
            "threads": 15
        },
        "endpoint": {
            "wordlist": "medium",
            "methods": ["GET", "HEAD"],
            "max_paths": 800
        },
        "tech": {
            "graphql": True,
            "extra_paths": False
        }
    },

    "aggressive": {
        "network": {
            "timeout": 4,
            "follow_redirects": True
        },
        "stealth": {
            "random_user_agent": False,
            "delay": 0
        },
        "dns": {
            "bruteforce": True,
            "max_subdomains": 2000
        },
        "http": {
            "threads": 40
        },
        "endpoint": {
            "wordlist": "large",
            "methods": ["GET", "HEAD", "OPTIONS"],
            "max_paths": 3000
        },
        "tech": {
            "graphql": True,
            "extra_paths": True
        }
    }
}
