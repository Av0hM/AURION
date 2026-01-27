# cognition/predictor.py
import numpy as np

def stress_risk(recent_df) -> float:
    """
    Predict probability [0–1] of entering STRESSED soon
    """
    if recent_df is None or len(recent_df) < 5:
        return 0.0

    stress_ratio = (recent_df["state"] == "STRESSED").mean()

    confidence_drop = (
        recent_df["confidence"]
        .diff()
        .dropna()
        .mean()
        if "confidence" in recent_df
        else 0
    )

    volatility = (
        recent_df["intensity"]
        .diff()
        .abs()
        .dropna()
        .mean()
        if "intensity" in recent_df
        else 0
    )

    risk = (
        0.4 * stress_ratio +
        0.3 * max(0, -confidence_drop) +
        0.3 * volatility
    )

    return float(min(1.0, max(0.0, risk)))