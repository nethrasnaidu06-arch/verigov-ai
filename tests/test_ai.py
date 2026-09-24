from ai.cross_verification.engine import Evidence, verify
from ai.anomaly.anomaly import detect
import random


def test_consistent():
    r = verify(Evidence(45, [39, 41, 40, 42, 41], [41, 40, 42], has_geotagged_evidence=True))
    assert r["verdict"] == "CONSISTENT"


def test_inconsistent():
    r = verify(Evidence(50, [8, 7, 9, 8], [42, 40, 41]))
    assert r["verdict"] == "INCONSISTENT" and r["priority"] == "High"


def test_anomaly():
    random.seed(1)
    hist = [[random.randint(36, 44) for _ in range(12)] for _ in range(20)]
    bad = [40, 41, 39, 40, 8, 7, 6, 7, 8, 7, 6, 7]
    assert detect(hist, bad)["status"] == "Anomalous"
    assert detect(hist, hist[0])["status"] == "Normal"
