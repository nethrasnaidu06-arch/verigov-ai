from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ai.cross_verification.engine import Evidence, verify
from ai.anomaly.anomaly import detect
from .db import SessionLocal, Base, engine
from .models import Institution, Attendance, AIObservation, Anomaly

Base.metadata.create_all(engine)
app = FastAPI(title="VeriGov AI API", version="0.2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class VerifyRequest(BaseModel):
    institution_id: str
    reported_attendance: int
    observed_occupancy: list[int]
    historical_attendance: list[int] = []
    historical_series: list[list[int]] = []
    prior_inspection_flags: int = 0
    activity_labels: list[str] = []
    has_geotagged_evidence: bool = False


class ReportedAttendance(BaseModel):
    reported_attendance: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/verify")
def verify_raw(r: VerifyRequest):
    status = "Normal"
    if r.historical_series:
        status = detect(r.historical_series, r.observed_occupancy)["status"]
    result = verify(Evidence(r.reported_attendance, r.observed_occupancy, r.historical_attendance,
                             r.prior_inspection_flags, r.activity_labels, status, r.has_geotagged_evidence))
    return {"institution_id": r.institution_id, **result}


@app.get("/institutions")
def institutions(db: Session = Depends(get_db)):
    return db.query(Institution).all()


@app.post("/institutions/{inst_id}/verify")
def verify_institution(inst_id: int, body: ReportedAttendance, db: Session = Depends(get_db)):
    inst = db.get(Institution, inst_id)
    if not inst:
        raise HTTPException(404, "Institution not found")

    obs = db.query(AIObservation).filter_by(institution_id=inst_id).order_by(AIObservation.observed_at).all()
    if not obs:
        raise HTTPException(400, "No AI observations for this institution yet")
    hist = [a.reported_count for a in
            db.query(Attendance).filter_by(institution_id=inst_id, source="historical").all()]

    db.add(Attendance(institution_id=inst_id, reported_count=body.reported_attendance, source="institution"))
    result = verify(Evidence(body.reported_attendance, [o.occupancy for o in obs], hist,
                             activity_labels=[o.activity for o in obs]))
    if result["verdict"] == "INCONSISTENT":
        db.add(Anomaly(institution_id=inst_id, kind="attendance_mismatch", severity=result["priority"],
                       priority_score=result["priority_score"], explanation=" ".join(result["explanation"])))
    db.commit()
    return {"institution": inst.name, **result}


@app.get("/anomalies")
def anomalies(db: Session = Depends(get_db)):
    return db.query(Anomaly).order_by(Anomaly.priority_score.desc()).all()