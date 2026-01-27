import json
import time
from memory.learner import Learner

LOG_FILE = "memory/logs/states.json"

def run_daily_learning():
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        return

    states = [d["state"] for d in data]
    learner = Learner()
    learner.learn_from_day(states)
