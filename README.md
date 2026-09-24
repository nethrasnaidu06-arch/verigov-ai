# VeriGov AI
**From reported compliance to evidence-backed verification.**

AI-driven cross-verification and anomaly prioritization for government-supported institutions.

## Components
| Layer | Folder | Status |
|---|---|---|
| AI-1 Person/occupancy detection | `ai/occupancy` | working (Milestone 1) |
| AI-2 Activity analysis | `ai/activity` | motion-based baseline |
| AI-3 Anomaly detection | `ai/anomaly` | Isolation Forest |
| AI-4 Cross-verification engine | `ai/cross_verification` | working, tested |
| Backend (FastAPI + DB) | `backend` | skeleton |
| Inspector app (Flutter) | `mobile` | Phase 6 |
| Official dashboard (React) | `dashboard` | Phase 7 |

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                                              # cross-verification + anomaly tests
python -m ai.occupancy.run --video path/to/video.mp4 --out data/observations.json
uvicorn backend.app.main:app --reload               # http://127.0.0.1:8000/docs
```

## Validation honesty
- Level 1: model metrics on public datasets (COCO, UCF-QNRF, UCF-Crime, XD-Violence).
- Level 2: system-level cross-verification is tested on synthetic/simulated scenarios and authorized footage. It is NOT claimed as government-validated.
