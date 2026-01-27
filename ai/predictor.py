def predict_next(memory):
    states = memory.last_n(5)

    # Escalation chains
    if states[-3:] == ["STRESSED", "STRESSED", "STRESSED"]:
        return "ANGRY"

    if states[-3:] == ["ANGRY", "ANGRY", "ANGRY"]:
        return "CRYING"

    if states[-3:] == ["TIRED", "TIRED", "TIRED"]:
        return "BURNOUT"

    # Avoidance patterns
    if states[-3:] == ["PROCRASTINATING", "PROCRASTINATING", "PROCRASTINATING"]:
        return "DEEP_DISTRACTION"

    # Recovery pattern
    if states[-3:] == ["STRESSED", "DEEP_WORK", "DEEP_WORK"]:
        return "RECOVERY"

    return None
