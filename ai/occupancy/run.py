import argparse, json
from .detector import run_video

p = argparse.ArgumentParser()
p.add_argument("--video", required=True)
p.add_argument("--out", default="data/observations.json")
p.add_argument("--every", type=float, default=5.0, help="seconds between sampled frames")
a = p.parse_args()

obs = run_video(a.video, sample_every_s=a.every)
with open(a.out, "w") as f:
    json.dump(obs, f, indent=2)
print(f"{len(obs)} observations -> {a.out}")
