import json
import os
import re
from datetime import datetime

from toolkit_recon import SCHEMA_VERSION


def _sanitize_target(target: str) -> str:
    cleaned = (target or "").strip()
    cleaned = cleaned.replace("\\", "_").replace("/", "_")
    cleaned = cleaned.replace("..", "_")
    cleaned = re.sub(r"[^A-Za-z0-9._()-]", "_", cleaned)
    cleaned = cleaned.strip("._")
    return cleaned or "unknown_target"


def _target_output_dir(target: str) -> str:
    return os.path.join("output", _sanitize_target(target))


def save_output(target: str, name: str, data: dict):
    base_dir = _target_output_dir(target)
    os.makedirs(base_dir, exist_ok=True)

    path = os.path.join(base_dir, f"{name}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"[+] Saved {name}.json")


def save_recon(target: str, module_name: str, module_data: dict):
    base_dir = _target_output_dir(target)
    os.makedirs(base_dir, exist_ok=True)

    recon_path = os.path.join(base_dir, "recon.json")

    # Create base structure when file does not exist.
    if not os.path.exists(recon_path):
        recon_data = {
            "schema_version": SCHEMA_VERSION,
            "target": target,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "modules": {}
        }
    else:
        try:
            with open(recon_path, "r", encoding="utf-8") as f:
                recon_data = json.load(f)
        except Exception:
            recon_data = {
                "schema_version": SCHEMA_VERSION,
                "target": target,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "modules": {}
            }

    recon_data["schema_version"] = SCHEMA_VERSION
    recon_data["timestamp"] = datetime.utcnow().isoformat() + "Z"
    recon_data["modules"][module_name] = module_data

    with open(recon_path, "w", encoding="utf-8") as f:
        json.dump(recon_data, f, indent=4)

    print(f"[+] Updated recon.json ({module_name})")


def save_full_recon(target: str, recon_data: dict):
    base_dir = _target_output_dir(target)
    os.makedirs(base_dir, exist_ok=True)

    recon_path = os.path.join(base_dir, "recon.json")
    data = dict(recon_data)
    data["schema_version"] = SCHEMA_VERSION
    data["timestamp"] = datetime.utcnow().isoformat() + "Z"

    with open(recon_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("[+] Saved recon.json")
