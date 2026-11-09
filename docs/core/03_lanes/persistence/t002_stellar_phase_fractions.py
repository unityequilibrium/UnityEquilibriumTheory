"""Test Card T002 prediction method: layer-3 abundance law vs globular-cluster star counts.

Layer 3 (docs/core/AUTHOR_PROPOSITION.md): systems disappear when their free-
energy store is exhausted, so the steady number of systems in a phase is
N = b * tau with tau = F / P (Little's law; uet_persistence_selection.py).

Every low-mass star in an old globular cluster passes through the upper red
giant branch (RGB, hydrogen-shell burning) and then the horizontal branch (HB,
core helium burning) exactly once. The formation rate b is therefore the same
for both phases and cancels:

    R = N_HB / N_RGB = tau_HB / tau_RGB

The phase lifetimes come from stellar-evolution models (fuel / luminosity),
independently of the star counts. The fit R_th(Y) = 6.26 Y - 0.12 and the
helium abundance Y measured in low-metallicity H II regions are registered
as data_id AYALA14_GC_R_PARAMETER.

Fixed method (Test Card T002):
    R_pred  = slope * Y + intercept,   sigma_pred = |slope| * sigma_Y
    z       = |R_pred - R_obs| / sqrt(sigma_pred^2 + sigma_obs^2)
    PASS if z <= 2;  INCONCLUSIVE if 2 < z <= 3;  FAIL if z > 3
The primary Y is Y_HII_Aver. Y_SBBN_as_used is reported as a sensitivity
input and does not decide the outcome.

Usage (from the repository root):
    python -m docs.core.03_lanes.persistence.t002_stellar_phase_fractions
This prints numbers only. A Result record requires an APPROVED Test Card.
"""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "docs/data/external/astronomy/globular_cluster_r_parameter/ayala2014_r_parameter.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "AYALA14_GC_R_PARAMETER"


def verified_rows() -> dict[str, tuple[float, float | None]]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
    entry = next(e for e in entries if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch; data changed after registration")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    out = {}
    for row in csv.DictReader(lines):
        unc = row["uncertainty"].strip()
        out[row["quantity"]] = (float(row["value"]), float(unc) if unc else None)
    return out


def outcome(z: float) -> str:
    if z <= 2.0:
        return "PASS"
    if z <= 3.0:
        return "INCONCLUSIVE"
    return "FAIL"


def compare(rows: dict, helium_key: str) -> dict:
    sel = importlib.import_module("docs.core.03_lanes.persistence.uet_persistence_selection")
    slope = rows["R_th_slope_Y"][0]
    intercept = rows["R_th_intercept"][0]
    Y, sY = rows[helium_key]
    r_obs, s_obs = rows["R_ave"]
    r_pred = slope * Y + intercept                      # = tau_HB / tau_RGB from stellar models
    # Little's law with a common formation rate: N_HB / N_RGB = (b tau_HB)/(b tau_RGB)
    b = 1.0
    ratio_check = sel.steady_abundance(b, r_pred) / sel.steady_abundance(b, 1.0)
    assert abs(ratio_check - r_pred) < 1e-12
    s_pred = abs(slope) * sY if sY is not None else 0.0
    z = abs(r_pred - r_obs) / math.sqrt(s_pred**2 + s_obs**2)
    return {"helium_input": helium_key, "Y": Y, "R_pred": r_pred, "sigma_pred": s_pred,
            "R_obs": r_obs, "sigma_obs": s_obs, "z": z, "outcome": outcome(z)}


def compute() -> dict:
    rows = verified_rows()
    return {"primary": compare(rows, "Y_HII_Aver"),
            "sensitivity_not_decisive": compare(rows, "Y_SBBN_as_used")}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
