"""Test Card T034 method: does protein loss rise as fat is used up after food stops (D15, AI mapping)?

Claim (C_L3_AFTER_CLOSING, wave D15): in the full layer-3 model a pool R feeds structures n,
    dn/dt = (a R - 1/tau) n,     dR/dt = S - delta R - a F R n.
Supplied, the pool sits at R* = 1/(a tau) and the structures are in balance. After the supply stops (S = 0)
the pool falls, so the structures' specific loss rate 1/tau - a R(t) starts at 0 and rises monotonically.
AI mapping tested here (not the author's): fat = pool R, lean tissue (protein) = structures n, a fast =
supply stopped. Prediction: daily protein loss (urinary nitrogen) does not fall during the fast; it rises
as fat is used up.

Comparison: daily total urinary nitrogen excretion (g N/day) on each fasting day of a 10-day water fast in
healthy men, Laurens et al. (2021) J Cachexia Sarcopenia Muscle 12, 1690 (PMC8718030), figure "protein
oxidation" (panel B of the body-composition figure), read off the figure after approval into
docs/data/external/biology/fasting/laurens2021_nitrogen.csv (columns day, n_g_per_day); group means as plotted.
    q = mean of the last 3 fasting-day points / mean of the first 3 fasting-day points
    PASS:   q >= 0.95       (protein loss does not fall, as D15 requires)
    FAILED: q <= 0.80       (protein loss falls by a fifth or more)
    INCONCLUSIVE otherwise, or fewer than 6 fasting-day points.

Do not run against the comparison data before Test Card T034 is APPROVED.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/biology/fasting/laurens2021_nitrogen.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CARD = ROOT / "docs/standard/tests/T034.json"
DATA_ID = "LAURENS2021_FASTING_NITROGEN"


def decide(points) -> dict:
    pts = sorted(points)
    if len(pts) < 6:
        return {"outcome": "INCONCLUSIVE", "reason": "fewer than 6 fasting-day points", "n": len(pts)}
    early = sum(v for _, v in pts[:3]) / 3.0
    late = sum(v for _, v in pts[-3:]) / 3.0
    q = late / early
    out = "PASS" if q >= 0.95 else ("FAILED" if q <= 0.80 else "INCONCLUSIVE")
    return {"outcome": out, "q": q, "early_mean_g_per_day": early, "late_mean_g_per_day": late, "n": len(pts)}


def compute() -> dict:
    if json.loads(CARD.read_text(encoding="utf-8")).get("status") != "APPROVED":
        raise RuntimeError("Test Card T034 is not APPROVED")
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    rows = csv.DictReader(ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#"))
    return decide([(float(r["day"]), float(r["n_g_per_day"])) for r in rows])


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
