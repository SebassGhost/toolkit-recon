import asyncio
from unittest.mock import AsyncMock, patch

from toolkit_recon.recon.subdomain_enum.sources.passive import _is_target_subdomain
from toolkit_recon.utils.output import _sanitize_target, save_output


def test_output_target_sanitization_prevents_traversal(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    save_output("..\\..//evil/target", "sample", {"ok": True})

    output_dir = tmp_path / "output"
    assert output_dir.exists()

    files = list(output_dir.rglob("sample.json"))
    assert len(files) == 1
    assert ".." not in str(files[0].relative_to(output_dir))


def test_sanitize_target_normalizes_invalid_chars():
    assert _sanitize_target("..\\demo/target:*?") == "demo_target"


def test_passive_source_domain_boundary_check():
    assert _is_target_subdomain("api.example.com", "example.com")
    assert _is_target_subdomain("*.example.com", "example.com")
    assert not _is_target_subdomain("badexample.com", "example.com")


def test_endpoint_run_works_inside_running_event_loop():
    from toolkit_recon.recon.endpoint_discovery import endpoints

    async def _inner():
        with patch.object(endpoints, "_run_async", new=AsyncMock(return_value={"ok": True})):
            result = endpoints.run("example.com", profile="passive")
            assert result == {"ok": True}

    asyncio.run(_inner())
