"""Draft Test Card T015 prediction method: can the parent action's O(2) sector at tree level describe He II?

Lane under test (the one Topic 13 assumed): chi = the He-4 atom, He II = the condensed phase of the
parent action's O(2) sector, lam fixed by the measured He-He s-wave scattering length (no fit):
    lam = 8 pi a m  (wave SI-1)  ->  tree-level (Bogoliubov) sound speed c = hbar sqrt(4 pi a n) / m
compared with the measured first sound u1 of He II at 1.70 K, saturated vapour pressure.

Fixed method:
    c_lo, c_hi = c(a - sigma_minus), c(a + sigma_plus)
    D = 0 if c_lo <= u1 <= c_hi, else min(|c_lo - u1|, |c_hi - u1|) / u1
    PASS D <= 0.10; INCONCLUSIVE 0.10 < D <= 0.30; FAIL D > 0.30
Also reported (not a criterion): diluteness n a^3.

Do not run against the data before the card is APPROVED by the author.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent
DATA = REPO / "docs/data/external/condensed_matter/helium4/he_ii_tree_level_inputs.csv"
MANIFEST = REPO / "docs/standard/data_manifest.json"
DATA_ID = "HE_II_TREE_LEVEL_INPUTS"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = sys.modules.setdefault(name, importlib.util.module_from_spec(spec))
    spec.loader.exec_module(mod)
    return mod


def _verified_rows() -> dict:
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return {r["quantity"]: r for r in csv.DictReader(lines)}


def outcome(d: float) -> str:
    return "PASS" if d <= 0.10 else ("INCONCLUSIVE" if d <= 0.30 else "FAIL")


def compute() -> dict:
    sb = _load("uet_si_bose_fluid", Path(__file__).resolve().parent / "uet_si_bose_fluid.py")
    rows = _verified_rows()
    u1 = float(rows["u1_first_sound_1p70K"]["value"])
    rho = float(rows["rho_total_1p70K"]["value"])
    a_row = rows["a_He_He_s_wave"]
    a = float(a_row["value"])
    a_lo, a_hi = a - float(a_row["uncertainty_minus"]), a + float(a_row["uncertainty_plus"])
    mass_kg = sb.MASS_EV["He4"] * sb.EV_J / 299792458.0**2
    n = rho / mass_kg
    c_mid, c_lo, c_hi = (sb.bogoliubov_speed_si(n, x, mass_kg) for x in (a, a_lo, a_hi))
    d = 0.0 if c_lo <= u1 <= c_hi else min(abs(c_lo - u1), abs(c_hi - u1)) / u1
    return {"u1_obs_m_s": u1, "c_pred_m_s": c_mid, "c_pred_range_m_s": [c_lo, c_hi],
            "n_a3": sb.diluteness(n, a), "D": d, "outcome": outcome(d)}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
