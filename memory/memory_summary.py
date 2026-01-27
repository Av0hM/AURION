import json
from collections import Counter

LOG_FILE = "memory/logs/states.json"

def get_memory_context():
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        return ""

    states = [d["state"] for d in data]

    if not states:
        return ""

    freq = Counter(states)
    top = freq.most_common(1)[0][0]

    context = f"""
Recent behaviour pattern:
- Most frequent state: {top}
- Stress count: {freq.get("STRESSED", 0)}
- Procrastination count: {freq.get("PROCRASTINATING", 0)}
- Deep work count: {freq.get("DEEP_WORK", 0)}
"""

    return context.strip()