"""Test Card T011 prediction method: P2 with real data. The record age set by an RV-only orbit fixes the pulsation phase gap.

1. P1/P2 (thought experiment v3, wave O5 in uet_pulsation_timing.py): the received pulsation phase lags
   by nu * tau(t), and tau is the light-travel time across the orbit. Its amplitude follows from the
   spectroscopic orbit alone: a1 sin i / c = K1 P sqrt(1 - e^2) / (2 pi c).
2. Prediction per system: ratio R = (a1 sin i / c)_PM / (a1 sin i / c)_RV = 1.
   The no-delay alternative (instant observation) predicts (a1 sin i / c)_PM = 0.
3. z = |PM - RV| / sqrt(sigma_PM^2 + sigma_RV^2), each sigma taken on the side facing the other value.
   PASS if z <= 2 for every system; FAILED if z > 3 for any system; otherwise INCONCLUSIVE.

Usage: python -m docs.core.03_lanes.observation.t011_pulsation_delay_vs_rv
Prints the numbers only. A Result record needs an APPROVED Test Card (docs/STANDARD.md section 4).
"""

from __future__ import annotations

import csv
import hashlib
import json
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "docs/data/external/stellar/phase_modulation/murphy2016_pm_vs_rv.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "MURPHY2016_PM_VS_RV"
SYSTEMS = ("KIC5705575", "KIC6780873")


def verified_rows() -> list[dict]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
    entry = next(e for e in entries if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch; data changed after registration")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return list(csv.DictReader(lines))


def _get(rows, system, method, quantity):
    r = next(x for x in rows if (x["system"], x["method"], x["quantity"]) == (system, method, quantity))
    return float(r["value"]), float(r["err_plus"]), float(r["err_minus"])


def compare(pm: tuple[float, float, float], rv: tuple[float, float, float]) -> dict:
    (vp, pp, pm_), (vr, rp, rm) = pm, rv
    s_pm, s_rv = (pm_, rp) if vp >= vr else (pp, rm)
    sigma = sqrt(s_pm ** 2 + s_rv ** 2)
    return {"pm_s": vp, "rv_s": vr, "ratio": vp / vr, "z": abs(vp - vr) / sigma,
            "z_no_delay": vp / pm_}


def compute() -> dict:
    rows = verified_rows()
    per = {s: compare(_get(rows, s, "PM", "a1sini_over_c"), _get(rows, s, "RV", "a1sini_over_c")) for s in SYSTEMS}
    zs = [v["z"] for v in per.values()]
    outcome = "PASS" if max(zs) <= 2 else ("FAILED" if max(zs) > 3 else "INCONCLUSIVE")
    return {"systems": per, "max_z": max(zs), "outcome": outcome}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
