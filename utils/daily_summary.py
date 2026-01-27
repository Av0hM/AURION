import json
from collections import Counter

def summarize_day(log_file):
    with open(log_file, "r") as f:
        data = json.load(f)

    states = [d["state"] for d in data]
    total = len(states)

    count = Counter(states)

    summary = {
        "total_samples": total,
        "deep_work_ratio": round(
            (count["DEEP_WORK"] + count["NORMAL_WORK"]) / total, 2
        ) if total else 0,
        "stress_ratio": round(
            (count["STRESSED"] + count["ANGRY"] + count["CRYING"]) / total, 2
        ) if total else 0,
        "most_common_state": count.most_common(1)[0][0] if total else None
    }

    return summary

