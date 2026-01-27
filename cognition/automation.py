# cognition/automation.py

def emit_actions(state: str):
    """
    Returns list of automation signals
    """
    actions = []

    if state == "DEEP_WORK":
        actions += [
            "mute_notifications",
            "dim_lights"
        ]

    if state == "STRESSED":
        actions += [
            "play_calm_music",
            "reduce_screen_brightness"
        ]

    if state == "TIRED":
        actions += [
            "stand_up_reminder"
        ]

    return actions