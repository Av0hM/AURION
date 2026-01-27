import json, os

CONTROL_FILE = "memory/control.json"

def read_control():
    if not os.path.exists(CONTROL_FILE):
        return {
            "omni_mode": "OFF",
            "backend_enabled": False,
            "logging_enabled": False
        }

    try:
        with open(CONTROL_FILE, "r") as f:
            data = json.load(f)
            return {
                "omni_mode": data.get("omni_mode", "OFF"),
                "backend_enabled": bool(data.get("backend_enabled", False)),
                "logging_enabled": bool(data.get("logging_enabled", False))
            }
    except Exception:
        return {
            "omni_mode": "OFF",
            "backend_enabled": False,
            "logging_enabled": False
        }