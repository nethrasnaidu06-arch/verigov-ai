"""AI-3: anomaly detection on occupancy history (Isolation Forest)."""
import numpy as np
from sklearn.ensemble import IsolationForest


def features(series: list[int], window: int = 4) -> np.ndarray:
    s = np.asarray(series, dtype=float)
    rows = []
    for i in range(len(s)):
        w = s[max(0, i - window + 1): i + 1]
        drop = (s[i - window] - s[i]) if i >= window else 0.0
        rows.append([s[i], w.mean(), w.std(), drop])
    return np.asarray(rows)


def detect(history: list[list[int]], current: list[int], contamination: float = 0.05) -> dict:
    """history: list of past normal-ish daily occupancy series; current: today's series."""
    X = np.vstack([features(d) for d in history])
    model = IsolationForest(n_estimators=200, contamination=contamination, random_state=42).fit(X)
    Xc = features(current)
    flags = model.predict(Xc) == -1
    scores = -model.score_samples(Xc)
    return {
        "anomalous": bool(flags.mean() > 0.25),
        "anomalous_indices": np.where(flags)[0].tolist(),
        "max_score": float(scores.max()),
        "status": "Anomalous" if flags.mean() > 0.25 else "Normal",
    }
