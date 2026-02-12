import importlib.util
import re
import shutil
import subprocess
import sys
import time
from urllib.parse import urlparse

from toolkit_recon import SCHEMA_VERSION
from toolkit_recon.config.profiles import get_http_config


URL_PATTERN = re.compile(r"https?://[^\s]+")


def _build_sherlock_command(username: str) -> list[str] | None:
    sherlock_bin = shutil.which("sherlock")
    if sherlock_bin:
        return [sherlock_bin, username, "--print-found", "--no-color"]

    if importlib.util.find_spec("sherlock"):
        return [sys.executable, "-m", "sherlock", username, "--print-found", "--no-color"]

    return None


def _site_from_url(url: str) -> str:
    hostname = urlparse(url).hostname or "unknown"
    parts = hostname.split(".")
    if len(parts) >= 2:
        return parts[-2]
    return hostname


def _extract_results(stdout: str) -> list[dict]:
    urls = set(URL_PATTERN.findall(stdout or ""))
    return [
        {
            "site": _site_from_url(url),
            "url": url,
            "status": "found",
        }
        for url in sorted(urls)
    ]


def run(target: str, profile: str = "balanced") -> dict:
    start = time.perf_counter()
    http_cfg = get_http_config(profile)
    timeout = max(10, http_cfg.get("timeout", 6) * 5)

    data = {
        "schema_version": SCHEMA_VERSION,
        "module": "osint_username",
        "target": target,
        "profile": profile,
        "results": [],
        "metrics": {
            "command_available": False,
            "executed": False,
            "return_code": None,
            "sites_checked": 0,
            "found": 0,
            "errors": 0,
            "duration_seconds": 0.0,
        },
    }

    cmd = _build_sherlock_command(target)
    if not cmd:
        data["error"] = "Sherlock no esta instalado o no es accesible en el entorno."
        data["metrics"]["errors"] = 1
        data["metrics"]["duration_seconds"] = round(time.perf_counter() - start, 4)
        return data

    data["metrics"]["command_available"] = True
    data["metrics"]["executed"] = True

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        data["metrics"]["return_code"] = proc.returncode
        data["results"] = _extract_results(proc.stdout)
        data["metrics"]["found"] = len(data["results"])
        data["metrics"]["sites_checked"] = len(data["results"])
        if proc.returncode not in (0, 1):
            data["error"] = (proc.stderr or "Error ejecutando Sherlock").strip()
            data["metrics"]["errors"] = 1
    except Exception as exc:
        data["error"] = str(exc)
        data["metrics"]["errors"] = 1

    data["metrics"]["duration_seconds"] = round(time.perf_counter() - start, 4)
    return data
