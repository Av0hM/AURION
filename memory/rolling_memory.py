import json
import os
import time

MAX_SECONDS = 24 * 60 * 60
LOG_PATH = "memory/logs/states.json"

os.makedirs("memory/logs", exist_ok=True)

def _load():
    if not os.path.exists(LOG_PATH):
        return []

    with open(LOG_PATH, "r") as f:
        data = json.load(f)

    # 🔒 SAFETY: ensure list
    if isinstance(data, dict):
        return []

    return data


def _save(data):
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)


def add_state(state: dict):
    data = _load()
    now = time.time()

    data.append(state)

    # keep last 24h only
    data = [
        s for s in data
        if now - float(s.get("timestamp", 0)) <= MAX_SECONDS
    ]

    _save(data)


def get_day_states():
    return _load()