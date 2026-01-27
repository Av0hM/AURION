import time
from memory.rolling_memory import add_state

def log_state(brain: dict):
    if not isinstance(brain, dict):
        print("⚠️ log_state skipped, brain not dict")
        return

    entry = {
        "timestamp": time.time(),   # ✅ MUST be float, not string
        "state": brain.get("state"),
        "intent": brain.get("intent"),
        "decision": brain.get("decision"),
        "persona": brain.get("persona"),
    }

    add_state(entry)