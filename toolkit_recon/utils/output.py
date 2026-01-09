import json
import os
from datetime import datetime


def save_output(target: str, name: str, data: dict):
    base_dir = os.path.join("output", target)
    os.makedirs(base_dir, exist_ok=True)

    path = os.path.join(base_dir, f"{name}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"[+] Saved {name}.json")


def save_recon(target: str, module_name: str, module_data: dict):
    base_dir = os.path.join("output", target)
    os.makedirs(base_dir, exist_ok=True)

    recon_path = os.path.join(base_dir, "recon.json")

    # Si no existe, crear estructura base
    if not os.path.exists(recon_path):
        recon_data = {
            "target": target,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "modules": {}
        }
    else:
        with open(recon_path, "r", encoding="utf-8") as f:
            recon_data = json.load(f)

    recon_data["modules"][module_name] = module_data

    with open(recon_path, "w", encoding="utf-8") as f:
        json.dump(recon_data, f, indent=4)

    print(f"[+] Updated recon.json ({module_name})")
