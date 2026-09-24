"""AI-4: Cross-verification engine. Compares reported vs observed vs historical evidence
and returns CONSISTENT / INCONSISTENT with an explanation and priority score.
It never accuses: it recommends human verification."""
from dataclasses import dataclass, field
from statistics import mean


@dataclass
class Evidence:
    reported_attendance: int
    observed_occupancy: list[int]                 # CCTV time series in operating hours
    historical_attendance: list[int] = field(default_factory=list)
    prior_inspection_flags: int = 0               # count of past negative inspections
    activity_labels: list[str] = field(default_factory=list)
    anomaly_status: str = "Normal"                # from AI-3
    has_geotagged_evidence: bool = False


def verify(e: Evidence, tolerance: float = 0.25) -> dict:
    reasons, score = [], 0.0
    obs = mean(e.observed_occupancy) if e.observed_occupancy else 0
    peak = max(e.observed_occupancy) if e.observed_occupancy else 0

    # 1. reported vs observed (peak is used to be fair to arrivals/departures)
    gap = (e.reported_attendance - peak) / e.reported_attendance if e.reported_attendance else 0
    if gap > tolerance:
        score += min(45, gap * 60)
        reasons.append(f"Reported attendance {e.reported_attendance} but observed peak occupancy was {peak} "
                       f"(average {obs:.0f}).")

    # 2. sudden occupancy drop
    if len(e.observed_occupancy) >= 4:
        hi, lo = max(e.observed_occupancy), min(e.observed_occupancy)
        if hi > 0 and (hi - lo) / hi > 0.6:
            score += 20
            reasons.append(f"Large occupancy drop detected (from {hi} to {lo}).")

    # 3. deviation from history
    if e.historical_attendance:
        h = mean(e.historical_attendance)
        if h and abs(obs - h) / h > 0.35:
            score += 15
            reasons.append(f"Observed average {obs:.0f} deviates from historical norm of about {h:.0f}.")

    # 4. AI-3 anomaly, activity, past inspections, evidence
    if e.anomaly_status == "Anomalous":
        score += 10
        reasons.append("Occupancy time series flagged anomalous by the anomaly model.")
    if e.activity_labels and e.activity_labels.count("Low activity") / len(e.activity_labels) > 0.5:
        score += 5
        reasons.append("Mostly low activity observed during operating hours.")
    if e.prior_inspection_flags:
        score += min(10, 3 * e.prior_inspection_flags)
        reasons.append(f"{e.prior_inspection_flags} previous inspection issue(s) on record.")
    if not e.has_geotagged_evidence:
        score += 3
        reasons.append("No recent geo-tagged inspection evidence.")

    score = round(min(score, 100), 1)
    inconsistent = score >= 40
    return {
        "verdict": "INCONSISTENT" if inconsistent else "CONSISTENT",
        "priority_score": score,
        "priority": "High" if score >= 60 else "Medium" if score >= 40 else "Low",
        "explanation": reasons or ["Reported attendance is consistent with observed evidence."],
        "recommendation": "Priority human verification." if inconsistent else "No action required.",
    }
