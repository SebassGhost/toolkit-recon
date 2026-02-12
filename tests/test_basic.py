from unittest.mock import patch, Mock

from toolkit_recon.config.profiles import get_http_config
from toolkit_recon.recon.endpoint_discovery.endpoints import run as endpoint_run
from toolkit_recon.recon.tech_fingerprint.fingerprint import run as fingerprint_run


def test_get_http_config_contains_timeout_and_redirect_flags():
    cfg = get_http_config("balanced")
    assert "timeout" in cfg
    assert "follow_redirects" in cfg
    assert "threads" in cfg


@patch("toolkit_recon.recon.endpoint_discovery.endpoints.requests.get")
def test_endpoint_discovery_returns_non_404_results(mock_get):
    response = Mock()
    response.status_code = 200
    response.content = b"ok"
    response.headers = {"Content-Type": "text/html"}
    mock_get.return_value = response

    results = endpoint_run("example.com", profile="passive")

    assert isinstance(results, list)
    assert all(item["status"] != 404 for item in results)


@patch("toolkit_recon.recon.tech_fingerprint.fingerprint.requests.Session.post")
@patch("toolkit_recon.recon.tech_fingerprint.fingerprint.requests.Session.get")
def test_fingerprint_respects_passive_graphql_flag(mock_get, mock_post):
    get_response = Mock()
    get_response.headers = {"server": "nginx"}
    get_response.cookies.get_dict.return_value = {}
    mock_get.return_value = get_response

    data = fingerprint_run("example.com", profile="passive")

    assert data["technologies"]["graphql"] is False
    mock_post.assert_not_called()
