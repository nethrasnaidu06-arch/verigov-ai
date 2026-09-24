import json
from datetime import datetime
from .db import SessionLocal, Base, engine
from .models import Institution, Attendance, AIObservation

Base.metadata.create_all(engine)
db = SessionLocal()

if db.query(Institution).count() == 0:
    db.add_all([
        Institution(name="Sunrise Skill Development Centre", scheme="Skill Development",
                    latitude=12.9716, longitude=77.5946, registered_beneficiaries=60),
        Institution(name="Green Valley Community Centre", scheme="Community Welfare",
                    latitude=13.0827, longitude=80.2707, registered_beneficiaries=45),
    ])
    db.commit()

inst = db.query(Institution).first()

if db.query(AIObservation).count() == 0:
    for c in (5, 4, 5, 6):
        db.add(Attendance(institution_id=inst.id, reported_count=c, source="historical"))
    for o in json.load(open("data/observations.json")):
        db.add(AIObservation(
            institution_id=inst.id,
            observed_at=datetime.fromisoformat(o["timestamp"]).replace(tzinfo=None),
            occupancy=o["occupancy"], activity=o["activity"], confidence=o["confidence"]))
    db.commit()

print("Seeded. Institutions:", db.query(Institution).count(),
      "| Observations:", db.query(AIObservation).count())