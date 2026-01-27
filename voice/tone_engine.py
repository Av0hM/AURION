def get_tone(state, user_traits=None):
    discipline = 0.5
    stress_prone = 0.5

    if user_traits:
        discipline = user_traits.get("discipline", 0.5)
        stress_prone = user_traits.get("stress_prone", 0.5)

    # Base tone from state
    if state in ["CRYING", "STRESSED"]:
        tone = "calm"
    elif state == "ANGRY":
        tone = "de_escalate"
    elif state == "PROCRASTINATING":
        tone = "strict"
    elif state == "TIRED":
        tone = "gentle"
    elif state == "VICTORY":
        tone = "hype"
    elif state == "DEEP_WORK":
        tone = "silent"
    else:
        tone = "neutral"

    # 🎯 Dynamic strictness curve
    if tone == "strict":
        if discipline < 0.3:
            tone = "very_strict"
        elif discipline < 0.5:
            tone = "strict"
        else:
            tone = "soft_strict"

    # 🧠 Personality override
    if stress_prone > 0.7:
        tone = "extra_calm"

    # 🔒 Safety: only DEEP_WORK is allowed to silence voice
    if tone == "silent" and state != "DEEP_WORK":
        tone = "calm"

    return tone