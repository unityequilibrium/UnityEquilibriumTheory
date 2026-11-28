"""Test Card T036 method: does the survival-burn exponent of subject L. hold for the other fasts of Benedict 1915 (D20)?

Claim (C_L3_SURVIVAL_BURN, wave D20, L0): a closed living store lowers its burn as it shrinks,
dR/dt = -P0 (R/R0)^beta; subject L. (Benedict 1915) calibrates beta = 1.95 (1.5-2.6 with the window).
Comparison: the daily body weights of every other fast in Benedict (1915) Table 2 (pp. 72-73: Succi's fasts,
Jacques, Beaute, Schenk; L. excluded), transcribed after approval into
docs/data/external/biology/fasting/benedict1915_other_fasts.csv (columns fast, day, mass_kg), as printed.
    A fast is used if it has at least 9 daily weights from day 6 on.
    One joint least-squares fit of the D20 closed form with a shared beta and its own (R0, P0) per fast.
    PASS:   1.5 <= beta <= 2.6 and the 95 percent interval of beta is narrower than 2
    FAILED: beta < 1.2 or beta > 3.3, with the interval narrower than 2
    INCONCLUSIVE otherwise, if the interval is 2 or wider, or with fewer than 3 usable fasts.

Do not run against the comparison data before Test Card T036 is APPROVED.
"""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/biology/fasting/benedict1915_other_fasts.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CARD = ROOT / "docs/standard/tests/T036.json"
DATA_ID = "BENEDICT1915_OTHER_FASTS"
FIRST_DAY, MIN_POINTS, MIN_FASTS = 6, 9, 3

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sb = importlib.import_module("core.03_lanes.persistence.uet_survival_burn")


def joint_fit(series: dict) -> dict:
    names = sorted(series)
    data = [(np.array([d for d, _ in series[n]]) - series[n][0][0], np.array([m for _, m in series[n]])) for n in names]

    def unpack(x):
        return x[0], x[1::2], x[2::2]

    def resid(x):
        beta, R0s, P0s = unpack(x)
        return np.concatenate([sb.store(t, R0, P0, beta) - R for (t, R), R0, P0 in zip(data, R0s, P0s)])

    x0 = [1.5]
    lo, hi = [-2.0], [8.0]
    for t, R in data:
        x0 += [R[0], max((R[0] - R[-1]) / max(t[-1], 1.0), 1e-3)]
        lo += [0.8 * R[0], 1e-6]
        hi += [1.2 * R[0], 10.0]
    sol = least_squares(resid, x0, bounds=(lo, hi), x_scale="jac")
    J = sol.jac
    dof = max(len(sol.fun) - len(sol.x), 1)
    s2 = float(sol.fun @ sol.fun) / dof
    cov = np.linalg.pinv(J.T @ J) * s2
    se = float(np.sqrt(cov[0, 0]))
    return {"beta": float(sol.x[0]), "beta_se": se, "ci95": [float(sol.x[0] - 1.96 * se), float(sol.x[0] + 1.96 * se)],
            "rms_kg": float(np.sqrt(s2)), "fasts": names, "points": int(len(sol.fun))}


def decide(rows) -> dict:
    series = defaultdict(list)
    for fast, day, m in rows:
        if day >= FIRST_DAY:
            series[fast].append((day, m))
    series = {k: sorted(v) for k, v in series.items() if len(v) >= MIN_POINTS}
    if len(series) < MIN_FASTS:
        return {"outcome": "INCONCLUSIVE", "reason": "fewer than 3 usable fasts", "usable": sorted(series)}
    f = joint_fit(series)
    width = f["ci95"][1] - f["ci95"][0]
    b = f["beta"]
    if width >= 2.0:
        f["outcome"] = "INCONCLUSIVE"
    elif 1.5 <= b <= 2.6:
        f["outcome"] = "PASS"
    elif b < 1.2 or b > 3.3:
        f["outcome"] = "FAILED"
    else:
        f["outcome"] = "INCONCLUSIVE"
    return f


def compute() -> dict:
    if json.loads(CARD.read_text(encoding="utf-8")).get("status") != "APPROVED":
        raise RuntimeError("Test Card T036 is not APPROVED")
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    rows = csv.DictReader(ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#"))
    return decide([(r["fast"], float(r["day"]), float(r["mass_kg"])) for r in rows])


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
