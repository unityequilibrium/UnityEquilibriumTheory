"""Test Card T006 prediction method: the Sun's energy use written into its gravity.

Method (fixed before the comparison is run; docs/standard/tests/T006.json):
1. Prediction with no free parameter (GR, Gdot = 0):
       d(GM)/dt / GM = -(L / (c^2 M) + wind fraction)   per year,  M = GM_sun / G
2. sigma_pred = wind sigma (luminosity and GM taken as exact nominal values).
3. z = |measured - predicted| / sqrt(sigma_meas^2 + sigma_pred^2).
4. Also reported (not the decision): z of the null hypothesis "energy use leaves no
   gravitational trace" (prediction 0) and of the radiation-only prediction.

Usage: python -m docs.core.03_lanes.open_system.t006_solar_mass_loss
Prints the numbers only. A Result record needs an APPROVED Test Card (docs/STANDARD.md section 4).
"""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "docs/data/external/gravity/solar_mass_loss/t006_solar_mass_loss.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "T006_SOLAR_MASS_LOSS"


def verified_rows() -> dict[str, dict[str, float]]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
    entry = next(e for e in entries if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch; data changed after registration")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return {r["record"]: {"value": float(r["value"]), "sigma": float(r["sigma"])} for r in csv.DictReader(lines)}


def compute() -> dict:
    r1 = importlib.import_module("docs.core.03_lanes.open_system.uet_r1_writing_channels")
    rows = verified_rows()
    mass = rows["gm_sun"]["value"] / r1.G_NEWTON
    radiative = r1.radiative_mass_loss_fraction_per_year(rows["luminosity"]["value"], mass)
    wind, wind_sigma = rows["wind_fraction"]["value"], rows["wind_fraction"]["sigma"]
    meas, meas_sigma = rows["measured_gm_rate"]["value"], rows["measured_gm_rate"]["sigma"]
    pred = -(radiative + wind)
    z = abs(meas - pred) / math.hypot(meas_sigma, wind_sigma)
    if z <= 2.0:
        outcome = "PASS"
    elif z <= 3.0:
        outcome = "INCONCLUSIVE"
    else:
        outcome = "FAILED"
    return {
        "radiative_fraction_per_year": radiative,
        "predicted_gm_rate_per_year": pred, "predicted_sigma": wind_sigma,
        "measured_gm_rate_per_year": meas, "measured_sigma": meas_sigma,
        "z": z, "outcome": outcome,
        "z_null_no_trace": abs(meas) / meas_sigma,
        "z_radiation_only": abs(meas + radiative) / meas_sigma,
    }


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
