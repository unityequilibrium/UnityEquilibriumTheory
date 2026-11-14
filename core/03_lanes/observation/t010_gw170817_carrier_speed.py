"""Test Card T010 prediction method: two records of one event travel at the same speed.

1. Layer 1: the parent action propagates tensor waves at c (c_T = 1), derived in
   docs/core/05_tests/physics/test_tensor_speed.py; light also moves at c.
2. Observation layer, principle P1: each carrier delivers the source state at its own retarded time,
   t_o = t_e + D/u. With u_GW = u_EM the arrival delay equals the emission delay only.
3. Prediction: (v_GW - v_EM)/v_EM = 0 exactly. PASS if 0 lies inside the published interval;
   FAILED if outside.

Usage: python -m docs.core.03_lanes.observation.t010_gw170817_carrier_speed
Prints the numbers only. A Result record needs an APPROVED Test Card (docs/STANDARD.md section 4).
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "docs/data/external/gravity/gw170817/abbott2017_gw170817_grb.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "ABBOTT2017_GW170817_GRB"
PREDICTED_SPEED_DIFFERENCE = 0.0  # c_T = 1 from the parent action


def verified_values() -> dict[str, float]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
    entry = next(e for e in entries if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch; data changed after registration")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return {r["quantity"]: float(r["value"]) for r in csv.DictReader(lines)}


def compute() -> dict:
    v = verified_values()
    low, high = v["speed_difference_lower"], v["speed_difference_upper"]
    inside = low <= PREDICTED_SPEED_DIFFERENCE <= high
    return {"predicted_speed_difference": PREDICTED_SPEED_DIFFERENCE, "allowed_interval": [low, high],
            "arrival_delay_s": v["arrival_delay_grb_after_gw"], "outcome": "PASS" if inside else "FAILED"}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
