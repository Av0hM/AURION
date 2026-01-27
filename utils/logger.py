import json
import os
from utils.timebase import now_unix

LOG_DIR = "data/logs"

os.makedirs(LOG_DIR, exist_ok=True)

def log_state(brain_output):
    today = now_unix()
    log_file = os.path.join(LOG_DIR, f"{today}.json")

    entry = {
        "timestamp": now_unix(),
        "state": brain_output.get("state"),
        "intensity": brain_output.get("intensity"),
        "intent": brain_output.get("intent"),
        "decision": brain_output.get("decision"),
        "persona": brain_output.get("persona")
    }

    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    with open(log_file, "w") as f:
        json.dump(data, f, indent=2)

