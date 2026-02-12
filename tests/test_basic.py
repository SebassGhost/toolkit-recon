from unittest.mock import AsyncMock, Mock, patch

from toolkit_recon import SCHEMA_VERSION
from toolkit_recon.config.profiles import get_http_config
from toolkit_recon.recon.endpoint_discovery.endpoints import run as endpoint_run
from toolkit_recon.recon.subdomain_enum.sub_enum import run as subdomain_run
from toolkit_recon.recon.tech_fingerprint.fingerprint import run as fingerprint_run


def test_get_http_config_contains_timeout_and_redirect_flags():
    cfg = get_http_config("balanced")
    assert "timeout" in cfg
    assert "follow_redirects" in cfg
    assert "threads" in cfg


@patch(
    "toolkit_recon.recon.endpoint_discovery.endpoints._scan_path",
    new_callable=AsyncMock,
)
@patch("toolkit_recon.recon.endpoint_discovery.endpoints.load_wordlist")
def test_endpoint_discovery_returns_structured_data(mock_wordlist, mock_scan_path):
    mock_wordlist.return_value = ["/admin"]
    mock_scan_path.return_value = (
        {
            "path": "/admin",
            "url": "https://example.com/admin",
            "status": 200,
            "length": 20,
            "content_type": "text/html",
            "redirect": None,
            "methods": ["GET"],
            "interesting": True,
        },
        {
            "attempted": 1,
            "completed": 1,
            "errors": 0,
            "retried_requests": 0,
        },
    )

    data = endpoint_run("example.com", profile="passive")

    assert isinstance(data, dict)
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["count"] == 1
    assert data["metrics"]["completed"] == 1
    assert all(item["status"] != 404 for item in data["results"])


@patch("toolkit_recon.recon.tech_fingerprint.fingerprint.requests.Session.post")
@patch("toolkit_recon.recon.tech_fingerprint.fingerprint.requests.Session.get")
def test_fingerprint_respects_passive_graphql_flag(mock_get, mock_post):
    get_response = Mock()
    get_response.headers = {"server": "nginx"}
    get_response.cookies.get_dict.return_value = {}
    mock_get.return_value = get_response

    data = fingerprint_run("example.com", profile="passive")

    assert data["schema_version"] == SCHEMA_VERSION
    assert data["technologies"]["graphql"] is False
    assert "metrics" in data
    assert "duration_seconds" in data["metrics"]
    mock_post.assert_not_called()


@patch("toolkit_recon.recon.subdomain_enum.sub_enum.passive_enum")
@patch("toolkit_recon.recon.subdomain_enum.sub_enum.resolve")
@patch("toolkit_recon.recon.subdomain_enum.sub_enum.detect_wildcard")
def test_subdomain_enum_includes_metrics(mock_wildcard, mock_resolve, mock_passive):
    mock_wildcard.return_value = {"wildcard": False, "ips": []}
    mock_passive.return_value = ["api.example.com"]
    mock_resolve.return_value = ["1.2.3.4"]

    data = subdomain_run("example.com", profile="passive")

    assert data["schema_version"] == SCHEMA_VERSION
    assert "metrics" in data
    assert "duration_seconds" in data["metrics"]
    assert data["count"] >= 1
