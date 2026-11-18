"""Draft Test Card T017 prediction method: budding-yeast growth from single-cell cycle times (topic 0.22).

Primary (decides the outcome): population doubling time from single-cell parent and daughter
generation times through 2^{-P/T} + 2^{-D/T} = 1 (uet_asymmetric_division.doubling_time), against
the doubling time counted in the same fields, for the five Table I conditions.
    sigma_T = |dT/dP| sd_P / sqrt(n) (+) |dT/dD| sd_D / sqrt(n),  n = 22 cells per mean (AI choice,
    the largest group visible in Fig. 3; the paper does not list n per condition)
    z_i = |T_pred - T_obs| / sigma_T;  PASS if max z <= 2;  FAILED if max z > 3;  else INCONCLUSIVE.
Secondary (reported, not deciding): percent of unbudded cells that are daughters, predicted with the
authors' budded-interval regression B = 0.17 T + 87.4 min (B was derived from budded-cell counts in
other experiments, so this comparison is not independent), against Table II, pairing plates
165/167, 220/220, 250/245, 300/321 as the authors did.

Do not run against the data before the card is APPROVED by the author.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/biology/yeast_cell_cycle/hartwell_unger1977_cycle_times.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "HARTWELL_UNGER1977_YEAST_CYCLES"
N_CELLS = 22
CONDITIONS = ("0.000a", "0.000b", "0.020", "0.030", "0.060")
SECONDARY_PAIRS = (("plate_165", "0.000b"), ("plate_220", "0.020"), ("plate_250", "0.030"), ("plate_300", "0.060"))


def _module():
    path = ROOT / "core/03_lanes/persistence/uet_asymmetric_division.py"
    name = "uet_producer_dep_uet_asymmetric_division"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        sys.modules[name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sys.modules[name])
    return sys.modules[name]


def _rows() -> dict:
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    out = {}
    for r in csv.DictReader(lines):
        out[(r["cycloheximide_ug_ml"], r["quantity"])] = (float(r["value"]), float(r["sd"]) if r["sd"] else None)
    return out


def outcome(max_z: float) -> str:
    return "PASS" if max_z <= 2.0 else ("INCONCLUSIVE" if max_z <= 3.0 else "FAIL")


def compute() -> dict:
    ad, v = _module(), _rows()
    primary = {}
    for c in CONDITIONS:
        p, sp = v[(c, "parent_gen_1st")]
        d, sd = v[(c, "daughter_gen")]
        t_obs = v[(c, "population_doubling_obs")][0]
        t = ad.doubling_time(p, d)
        h = 1e-3
        dp = (ad.doubling_time(p + h, d) - ad.doubling_time(p - h, d)) / (2 * h)
        dd = (ad.doubling_time(p, d + h) - ad.doubling_time(p, d - h)) / (2 * h)
        sig = math.hypot(dp * sp, dd * sd) / math.sqrt(N_CELLS)
        primary[c] = {"T_pred": t, "T_obs": t_obs, "sigma": sig, "z": abs(t - t_obs) / sig}
    slope = v[("all", "budded_interval_slope")][0]
    intercept = v[("all", "budded_interval_intercept")][0]
    secondary = {}
    for plate, c in SECONDARY_PAIRS:
        t = primary[c]["T_pred"]
        u = 100.0 * ad.unbudded_daughter_fraction(v[(c, "parent_gen_1st")][0], v[(c, "daughter_gen")][0], slope * t + intercept, t)
        obs, err = v[(plate, "unbudded_no_scar_percent")]
        secondary[plate] = {"pred_percent": u, "obs_percent": obs, "z": abs(obs - u) / err}
    max_z = max(r["z"] for r in primary.values())
    return {"primary": primary, "max_z": max_z, "outcome": outcome(max_z), "secondary_not_deciding": secondary}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
