import json
import os
from datetime import datetime

DAILY_DIR = "data/daily"
MEMORY_FILE = "data/memory.json"

os.makedirs(DAILY_DIR, exist_ok=True)

def log_state(state):
    """
    Logs current state to today's file
    """
    today = datetime.now().strftime("%Y-%m-%d")
    path = f"{DAILY_DIR}/{today}.json"

    if os.path.exists(path):
        with open(path, "r") as f:
            states = json.load(f)
    else:
        states = []

    states.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "state": state
    })

    with open(path, "w") as f:
        json.dump(states, f, indent=2)
