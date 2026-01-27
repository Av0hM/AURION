def derive_intensity(state: str) -> float:
    """
    Returns cognitive intensity [0–1] from state
    """
    return {
        "DEEP_WORK": 0.90,
        "NORMAL_WORK": 0.70,
        "VICTORY": 0.85,
        "STRESSED": 0.30,
        "PROCRASTINATING": 0.20,
        "TIRED": 0.40
    }.get(state, 0.50)


def derive_confidence(state: str) -> float:
    """
    Returns confidence estimate [0–1] from state
    """
    return {
        "DEEP_WORK": 0.80,
        "NORMAL_WORK": 0.70,
        "VICTORY": 0.85,
        "STRESSED": 0.40,
        "PROCRASTINATING": 0.30,
        "TIRED": 0.45
    }.get(state, 0.50)