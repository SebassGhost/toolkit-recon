from unittest.mock import Mock, patch

from toolkit_recon import SCHEMA_VERSION
from toolkit_recon.recon.osint_username.username import run as osint_user_run


@patch("toolkit_recon.recon.osint_username.username._build_sherlock_command")
@patch("toolkit_recon.recon.osint_username.username.subprocess.run")
def test_osint_username_parses_found_profiles(mock_subprocess_run, mock_build_cmd):
    mock_build_cmd.return_value = ["sherlock", "alice", "--print-found", "--no-color"]
    mock_subprocess_run.return_value = Mock(
        returncode=0,
        stdout="https://github.com/alice\nhttps://x.com/alice\n",
        stderr="",
    )

    data = osint_user_run("alice", profile="balanced")

    assert data["schema_version"] == SCHEMA_VERSION
    assert data["module"] == "osint_username"
    assert data["metrics"]["found"] == 2
    assert data["metrics"]["sites_checked_known"] is False
    assert len(data["results"]) == 2


@patch("toolkit_recon.recon.osint_username.username._build_sherlock_command")
def test_osint_username_handles_missing_command(mock_build_cmd):
    mock_build_cmd.return_value = None
    data = osint_user_run("alice", profile="balanced")

    assert data["metrics"]["command_available"] is False
    assert data["metrics"]["errors"] == 1
    assert "error" in data
