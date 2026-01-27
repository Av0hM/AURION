# cognition/intervention.py

def recommend_intervention(state: str, stress_risk: float, focus: int):
    """
    Returns a human‑readable intervention or None
    """
    if stress_risk > 0.75:
        return "🧯 High stress incoming — take a 5–10 minute break"

    if state == "TIRED" and focus < 40:
        return "💧 Low energy detected — hydrate and move"

    if state == "PROCRASTINATING":
        return "🔄 Context reset recommended — switch task or environment"

    return None