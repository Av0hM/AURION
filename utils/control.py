import json, os

CONTROL_FILE = "memory/control.json"

def read_control():
    if not os.path.exists(CONTROL_FILE):
        return {
            "aurion_mode": "OFF",
            "backend_enabled": False,
            "logging_enabled": False
        }

    try:
        with open(CONTROL_FILE, "r") as f:
            data = json.load(f)
            return {
                "aurion_mode": data.get("aurion_mode", "OFF"),
                "backend_enabled": bool(data.get("backend_enabled", False)),
                "logging_enabled": bool(data.get("logging_enabled", False))
            }
    except Exception:
        return {
            "aurion_mode": "OFF",
            "backend_enabled": False,
            "logging_enabled": False
        }