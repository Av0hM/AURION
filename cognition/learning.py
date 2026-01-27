import numpy as np

def best_focus_window(df):
    """
    Returns hour of day with highest deep‑work probability
    """
    if df is None or df.empty:
        return None

    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour

    focus_by_hour = (
        df.groupby("hour")["state"]
        .apply(lambda s: (s == "DEEP_WORK").mean())
    )

    return int(focus_by_hour.idxmax())


def cognitive_entropy(df):
    """
    Measures cognitive stability (lower = better)
    """
    if df is None or df.empty:
        return 0.0

    probs = df["state"].value_counts(normalize=True)
    return float(-np.sum(probs * np.log2(probs)))