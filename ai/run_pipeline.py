import argparse, json
import matplotlib.pyplot as plt
from ai.cross_verification.engine import Evidence, verify

p = argparse.ArgumentParser()
p.add_argument("--obs", default="data/observations.json")
p.add_argument("--reported", type=int, required=True)
p.add_argument("--historical", type=int, nargs="*", default=[])
a = p.parse_args()

obs = json.load(open(a.obs))
occ = [o["occupancy"] for o in obs]
labels = [o["activity"] for o in obs]

result = verify(Evidence(a.reported, occ, a.historical, activity_labels=labels))
print(json.dumps(result, indent=2))

plt.figure(figsize=(8, 4))
plt.plot(occ, marker="o", label="Observed (CCTV)")
plt.axhline(a.reported, color="red", linestyle="--", label="Reported")
plt.title(f"{result['verdict']} - priority {result['priority']}")
plt.xlabel("Sample")
plt.ylabel("People")
plt.legend()
plt.tight_layout()
plt.savefig("data/occupancy_chart.png")
print("Chart saved to data/occupancy_chart.png")