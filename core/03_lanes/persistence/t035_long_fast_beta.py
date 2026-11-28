"""Test Card T035 method: does the survival-burn exponent of one fast carry to another (D20)?

Claim (C_L3_SURVIVAL_BURN, wave D20, L0): a closed living store lowers its burn as it shrinks,
dR/dt = -P0 (R/R0)^beta, and the fast of subject L. (Benedict 1915) calibrates beta = 1.95 (1.5-2.6 with the
window). Tested: an independent long fast follows the same law with beta in that range; D14's constant
leak (beta = 1) and constant burn (beta = 0) lie outside it.

Comparison: body weight against time during the 382-day supervised fast of Stewart and Fleming (1973)
Postgrad Med J 49, 203 (PMC2495396), read off the paper's body-weight figure (or a weight table, if the
paper has one) after approval into docs/data/external/biology/fasting/stewart1973_weight.csv (columns day,
mass_kg); points from day 6 on.
    beta_obs from a least-squares fit of R(t) = [R0^(1-beta) + (beta - 1) P0 R0^(-beta) t]^(1/(1-beta))
    (R0, P0, beta free) to all points
    PASS:   1.5 <= beta_obs <= 2.6
    FAILED: beta_obs < 1.2 or beta_obs > 3.3
    INCONCLUSIVE otherwise, or fewer than 6 points.

Do not run against the comparison data before Test Card T035 is APPROVED.
"""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/biology/fasting/stewart1973_weight.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CARD = ROOT / "docs/standard/tests/T035.json"
DATA_ID = "STEWART1973_FAST_WEIGHT"
FIRST_DAY = 6

import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sb = importlib.import_module("core.03_lanes.persistence.uet_survival_burn")


def fit_beta(points) -> dict:
    pts = sorted(p for p in points if p[0] >= FIRST_DAY)
    t = np.array([p[0] for p in pts]) - pts[0][0]
    R = np.array([p[1] for p in pts])

    def model(tt, R0, P0, beta):
        return sb.store(tt, R0, P0, beta)

    p0 = [R[0], (R[0] - R[-1]) / max(t[-1], 1.0), 1.5]
    popt, pcov = curve_fit(model, t, R, p0=p0, bounds=([0.5 * R[0], 1e-6, -2.0], [1.5 * R[0], 10 * p0[1] + 1, 8.0]),
                           maxfev=20000)
    return {"beta": float(popt[2]), "beta_se": float(np.sqrt(pcov[2, 2])), "R0": float(popt[0]), "P0": float(popt[1]),
            "n": len(pts), "rms_kg": float(np.sqrt(np.mean((model(t, *popt) - R) ** 2)))}


def decide(points) -> dict:
    if len([p for p in points if p[0] >= FIRST_DAY]) < 6:
        return {"outcome": "INCONCLUSIVE", "reason": "fewer than 6 points"}
    f = fit_beta(points)
    b = f["beta"]
    f["outcome"] = "PASS" if 1.5 <= b <= 2.6 else ("FAILED" if (b < 1.2 or b > 3.3) else "INCONCLUSIVE")
    return f


def compute() -> dict:
    if json.loads(CARD.read_text(encoding="utf-8")).get("status") != "APPROVED":
        raise RuntimeError("Test Card T035 is not APPROVED")
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    rows = csv.DictReader(ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#"))
    return decide([(float(r["day"]), float(r["mass_kg"])) for r in rows])


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
