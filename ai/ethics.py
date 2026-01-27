def ethical_filter(state, intent, proposed_action):
    # Hard rules
    if state == "CRYING":
        return "SUPPORT_ONLY"

    if state == "ANGRY" and proposed_action in ["PRESSURE", "MOCK"]:
        return "DE_ESCALATE"

    if state == "TIRED" and proposed_action == "PUSH":
        return "REST_SUGGEST"

    # Intent-based ethics
    if intent == "emotional_overload":
        return "COMFORT"

    if intent == "burnout":
        return "BREAK_RECOMMEND"

    if intent == "avoidance" and proposed_action == "SCOLD":
        return "GENTLE_NUDGE"

    return proposed_action