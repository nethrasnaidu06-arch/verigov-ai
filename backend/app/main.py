from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai.cross_verification.engine import Evidence, verify
from ai.anomaly.anomaly import detect

app = FastAPI(title="VeriGov AI API", version="0.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class VerifyRequest(BaseModel):
    institution_id: str
    reported_attendance: int
    observed_occupancy: list[int]
    historical_attendance: list[int] = []
    historical_series: list[list[int]] = []
    prior_inspection_flags: int = 0
    activity_labels: list[str] = []
    has_geotagged_evidence: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/verify")
def verify_institution(r: VerifyRequest):
    status = "Normal"
    if r.historical_series:
        status = detect(r.historical_series, r.observed_occupancy)["status"]
    result = verify(Evidence(r.reported_attendance, r.observed_occupancy, r.historical_attendance,
                             r.prior_inspection_flags, r.activity_labels, status, r.has_geotagged_evidence))
    return {"institution_id": r.institution_id, **result}
