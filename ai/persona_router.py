STATE_TO_PERSONA = {
    "DEEP_WORK": "Silent Guardian",
    "NORMAL_WORK": "Silent Guardian",
    "DISTRACTED": "Attention Wrangler",
    "PROCRASTINATING": "Drill Sergeant",
    "TIRED": "Energy Manager",
    "STRESSED": "Calm Coach",
    "ANGRY": "De-escalator",
    "CRYING": "Therapist",
    "EATING": "Health Coach",
    "VICTORY": "Hype Man",
    "BORED": "Motivator",
    "AWAY": "Idle Watcher"
}

def route_persona(state):
    return STATE_TO_PERSONA.get(state, "Silent Guardian")
