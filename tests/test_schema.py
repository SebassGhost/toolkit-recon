import json
from pathlib import Path
from unittest.mock import patch

import pytest

from toolkit_recon import SCHEMA_VERSION
from toolkit_recon.recon.recon_all import run as recon_all_run


def _load_recon_schema():
    schema_path = Path("toolkit_recon/schema/recon.schema.json")
    with schema_path.open("r", encoding="utf-8") as f:
        return json.load(f)


@patch("toolkit_recon.recon.recon_all.save_full_recon")
@patch("toolkit_recon.recon.recon_all.save_output")
@patch("toolkit_recon.recon.recon_all.tech_fingerprint_run")
@patch("toolkit_recon.recon.recon_all.endpoint_discovery_run")
@patch("toolkit_recon.recon.recon_all.subdomain_enum_run")
def test_recon_all_output_matches_schema(
    mock_subdomain,
    mock_endpoint,
    mock_tech,
    _mock_save_output,
    _mock_save_full,
):
    jsonschema = pytest.importorskip("jsonschema")
    mock_subdomain.return_value = {
        "schema_version": SCHEMA_VERSION,
        "module": "subdomain_enum",
        "target": "example.com",
        "profile": "balanced",
        "count": 1,
        "wildcard": False,
        "wildcard_ips": [],
        "results": [{"subdomain": "api.example.com", "ip": "1.1.1.1", "source": "passive"}],
        "metrics": {"duration_seconds": 0.1},
    }
    mock_endpoint.return_value = {
        "schema_version": SCHEMA_VERSION,
        "module": "endpoint_discovery",
        "target": "example.com",
        "profile": "balanced",
        "count": 1,
        "results": [{"path": "/admin", "status": 200}],
        "metrics": {
            "total_paths": 1,
            "attempted": 1,
            "completed": 1,
            "errors": 0,
            "retried_requests": 0,
            "duration_seconds": 0.1,
            "throughput_rps": 10.0,
        },
    }
    mock_tech.return_value = {
        "schema_version": SCHEMA_VERSION,
        "module": "tech_fingerprint",
        "target": "example.com",
        "profile": "balanced",
        "technologies": {},
        "headers": {},
        "metrics": {
            "requests_attempted": 1,
            "requests_successful": 1,
            "errors": 0,
            "graphql_probe_attempted": False,
            "duration_seconds": 0.1,
        },
    }

    output = recon_all_run("example.com", profile="balanced")
    jsonschema.validate(instance=output, schema=_load_recon_schema())
