"""AI-1: person detection + tracking -> occupancy time series."""
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone


@dataclass
class Observation:
    timestamp: str
    occupancy: int
    activity: str
    confidence: float


def run_video(video_path: str, sample_every_s: float = 5.0, model_name: str = "yolov8n.pt",
              conf: float = 0.4, start_time: datetime | None = None) -> list[dict]:
    import cv2
    from ultralytics import YOLO

    model = YOLO(model_name)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    step = max(1, int(fps * sample_every_s))
    start = start_time or datetime.now(timezone.utc)
    out, prev_gray, idx = [], None, 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            res = model.predict(frame, classes=[0], conf=conf, verbose=False)[0]  # class 0 = person
            confs = res.boxes.conf.tolist() if res.boxes is not None else []
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            motion = 0.0
            if prev_gray is not None:
                motion = float((cv2.absdiff(gray, prev_gray) > 25).mean())
            prev_gray = gray
            out.append(asdict(Observation(
                timestamp=(start + timedelta(seconds=idx / fps)).isoformat(),
                occupancy=len(confs),
                activity=classify_activity(motion, len(confs)),
                confidence=round(sum(confs) / len(confs), 3) if confs else 0.0,
            )))
        idx += 1
    cap.release()
    return out


def classify_activity(motion_ratio: float, people: int) -> str:
    """AI-2 baseline: motion energy -> Normal / Low / Unusual."""
    if people == 0:
        return "Low activity"
    if motion_ratio < 0.005:
        return "Low activity"
    if motion_ratio > 0.25:
        return "Unusual activity"
    return "Normal activity"
