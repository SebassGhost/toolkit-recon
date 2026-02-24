from toolkit_recon.core.correlation import build_correlation


def test_correlation_prioritizes_sensitive_paths():
    data = {
        "modules": {
            "subdomain_enum": {
                "results": [{"subdomain": "admin.example.com"}],
            },
            "endpoint_discovery": {
                "admin.example.com": {
                    "results": [
                        {
                            "path": "/admin/login",
                            "url": "https://admin.example.com/admin/login",
                            "status": 403,
                        }
                    ]
                }
            },
            "tech_fingerprint": {
                "admin.example.com": {
                    "technologies": {"framework": "django", "language": "python", "graphql": False}
                }
            },
        }
    }

    correlation = build_correlation(data)

    assert correlation["stats"]["total_findings"] == 1
    assert correlation["top_findings"][0]["score"] >= 60
    assert "path:admin" in correlation["top_findings"][0]["reasons"]
