import json
import os


def save_output(target: str, name: str, data: dict):
    base_dir = os.path.join("output", target)
    os.makedirs(base_dir, exist_ok=True)

    path = os.path.join(base_dir, f"{name}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"[+] Saved {name}.json")
