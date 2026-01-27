def infer_intent(state, macro_state, intensity, recent_states):
    # Emotional patterns
    if state == "EATING" and macro_state == "NEGATIVE":
        return "emotional_eating"

    if state == "PROCRASTINATING" and "STRESSED" in recent_states:
        return "avoidance"

    if state == "PROCRASTINATING" and "TIRED" in recent_states:
        return "fatigue_escape"

    if state == "CRYING":
        return "emotional_overload"

    if state == "ANGRY":
        return "frustration_release"

    # Positive patterns
    if state == "DEEP_WORK" and intensity > 0.7:
        return "goal_driven"

    if state == "VICTORY":
        return "achievement_reward"

    return "neutral"