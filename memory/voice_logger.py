import json
import os
import time

VOICE_LOG = "memory/logs/voice_log.json"

os.makedirs("memory/logs", exist_ok=True)

def log_voice(text: str, tone: str):
    entry = {
        "timestamp": time.time(),
        "text": text,
        "tone": tone
    }

    # Load existing log
    if os.path.exists(VOICE_LOG):
        try:
            with open(VOICE_LOG, "r") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
        except Exception:
            data = []
    else:
        data = []

    data.append(entry)

    # Optional: keep last 500 lines only
    data = data[-500:]

    with open(VOICE_LOG, "w") as f:
        json.dump(data, f, indent=2)