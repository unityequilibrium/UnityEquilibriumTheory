"""Test Card T033 method: do real thermal power plants run near the efficiency at maximum power (D13)?

Claim (C_L3_OPENNESS_ORDER, wave D13): between a hot side T_h and a cold side T_c with linear heat contacts,
openness sets a ceiling on the work rate, reached at the efficiency eta_CA = 1 - sqrt(T_c/T_h). AI reading
tested here: systems that keep order by drawing work from their openness run near that ceiling, so real
plants have eta_obs close to eta_CA (not to Carnot 1 - T_c/T_h).

Comparison: the plants listed with T_h, T_c and observed efficiency eta_obs in Esposito, Kawai, Lindenberg
and Van den Broeck (2010) PRL 105, 150603 (arXiv:1008.2464), table "Theoretical bounds and observed
efficiency of thermal plants", transcribed after approval into
docs/data/external/thermo/power_plants/esposito2010_plants.csv (columns plant, T_h_K, T_c_K, eta_obs);
the table's own derived columns are not used.
    r_i = eta_obs / eta_CA(T_h, T_c);   m = median |r_i - 1|
    PASS:   m <= 0.10
    FAILED: m >= 0.25
    INCONCLUSIVE otherwise, or fewer than 8 plants.

Do not run against the comparison data before Test Card T033 is APPROVED.
"""

from __future__ import annotations

import csv
import hashlib
import json
from math import sqrt
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/thermo/power_plants/esposito2010_plants.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CARD = ROOT / "docs/standard/tests/T033.json"
DATA_ID = "ESPOSITO2010_POWER_PLANTS"


def eta_ca(T_h: float, T_c: float) -> float:
    return 1.0 - sqrt(T_c / T_h)


def eta_carnot(T_h: float, T_c: float) -> float:
    return 1.0 - T_c / T_h


def decide(rows) -> dict:
    if len(rows) < 8:
        return {"outcome": "INCONCLUSIVE", "reason": "fewer than 8 plants", "n": len(rows)}
    r = np.array([eo / eta_ca(th, tc) for th, tc, eo in rows])
    rc = np.array([eo / eta_carnot(th, tc) for th, tc, eo in rows])
    m = float(np.median(np.abs(r - 1.0)))
    out = "PASS" if m <= 0.10 else ("FAILED" if m >= 0.25 else "INCONCLUSIVE")
    return {"outcome": out, "median_abs_rel_dev_from_CA": m, "ratios_obs_over_CA": r.round(3).tolist(),
            "median_obs_over_carnot": float(np.median(rc)), "n": len(rows)}


def compute() -> dict:
    if json.loads(CARD.read_text(encoding="utf-8")).get("status") != "APPROVED":
        raise RuntimeError("Test Card T033 is not APPROVED")
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    rows = [(float(r["T_h_K"]), float(r["T_c_K"]), float(r["eta_obs"])) for r in csv.DictReader(
        ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#"))]
    return decide(rows)


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
