"""Test Card T012 prediction method: P4 with real data. A correlation front cannot outrun the common-past bound.

1. P4 as corrected by O2 (generalised in uet_two_signal_contact.py): a pair of sites shares a record no
   earlier than t = d / (c_a + c_b), so the front of correlations moves no faster than
   v_bound = c_a + c_b = max_k d(e_d + e_h)/dk (Eq. 17 of the source, from the dispersions of its model).
2. Prediction per system: v_front <= v_bound. The bound is taken as the largest value over U/J +- its
   calibration uncertainty. excess = (v_front - v_bound) / v_front_err; negative means below the bound.
3. Validity: the source states its effective model is reasonable down to U/J ~ 6. Systems with U/J below 6
   are reported but do not decide the outcome (rule fixed here, from the source statement).
4. PASS if excess <= 2 for every valid system; FAILED if excess > 3 for any; otherwise INCONCLUSIVE.
5. Diagnostic (not part of the outcome): the direct-contact-only reading of P4 gives v_bound_direct =
   max single-quasiparticle speed; excess_direct is reported for the valid systems.

Usage: python -m docs.core.03_lanes.observation.t012_correlation_front_bound
Prints the numbers only. A Result record needs an APPROVED Test Card (docs/STANDARD.md section 4).
"""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "docs/data/external/quantum_many_body/correlation_front/cheneau2012_front_velocity.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "CHENEAU2012_FRONT_VELOCITY"
VALID_FROM_U_OVER_J = 6.0

two = importlib.import_module("docs.core.03_lanes.observation.uet_two_signal_contact")


def verified_rows() -> list[dict]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
    entry = next(e for e in entries if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch; data changed after registration")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(lines)]


def _upper(f, u: float, du: float) -> float:
    return max(f(u - du), f(u), f(u + du))


def compute() -> dict:
    systems = {}
    for r in verified_rows():
        u, du, v, dv = r["u_over_j"], r["u_over_j_err"], r["v_front"], r["v_front_err"]
        bound = _upper(two.pair_front_velocity_bound, u, du)
        direct = _upper(lambda x: max(two.single_signal_speeds(x)), u, du)
        systems[f"U/J={u:g}"] = {
            "valid": u >= VALID_FROM_U_OVER_J, "v_front": v, "v_front_err": dv,
            "v_bound_common_past": bound, "excess": (v - bound) / dv,
            "v_bound_direct_only": direct, "excess_direct_only": (v - direct) / dv}
    valid = [s["excess"] for s in systems.values() if s["valid"]]
    outcome = "PASS" if max(valid) <= 2 else ("FAILED" if max(valid) > 3 else "INCONCLUSIVE")
    return {"systems": systems, "max_excess_valid": max(valid), "outcome": outcome}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
