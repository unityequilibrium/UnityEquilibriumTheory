"""Test Card T005 prediction method: UET portal fifth force vs published Yukawa bounds.

Method (fixed before the comparison is run; docs/standard/tests/T005.json):
1. With chi = ordinary matter (author decision 2026-11-10) the portal gives a
   composition-independent Yukawa force with
       alpha = g_c^2 / (2 kappa m_chi^4),  lambda = hbar c / (m_psi c^2)
   (claim C_PORTAL_FIFTH_FORCE, L1; module uet_portal_fifth_force.py).
2. m_chi = mean nucleon mass (single-species idealization), kappa = 1/M_red^2.
3. Each registered bound alpha < alpha_max at a range lambda converts to
       g_c < g_c_max = m_chi^2 sqrt(2 kappa alpha_max).
   * lee2020: for every m_psi <= hbar c / 38.6 um.
   * merkowitz2010_llr: only at m_psi = hbar c / (a/2), a = 3.844e8 m.
4. Report the parent-coupling form h sqrt(eps/k)/Z = g_c (Theory Card canonical map).

Constants: M_red = 2.435e27 eV, m_N = 0.9389e9 eV, hbar c = 1.973269804e-7 eV m,
Earth-Moon mean distance a = 3.844e8 m.

Usage: python -m docs.core.03_lanes.scalar_tensor.t005_fifth_force_constraint
Prints the numbers only. A Result record needs an APPROVED Test Card (docs/STANDARD.md section 4).
"""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "docs/data/external/gravity/yukawa_fifth_force/t005_yukawa_bounds.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "T005_YUKAWA_BOUNDS"
EARTH_MOON_M = 3.844e8


def verified_rows() -> list[dict[str, str]]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
    entry = next(e for e in entries if e["data_id"] == DATA_ID)
    digest = hashlib.sha256(DATA.read_bytes()).hexdigest()
    if digest != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch; data changed after registration")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return list(csv.DictReader(lines))


def compute() -> dict:
    ff = importlib.import_module("docs.core.03_lanes.scalar_tensor.uet_portal_fifth_force")
    kappa = 1.0 / ff.REDUCED_PLANCK_MASS_EV**2
    m_chi = ff.NUCLEON_MASS_EV
    out = {"m_chi_eV": m_chi, "kappa_eV^-2": kappa,
           "g_c_for_alpha_1_eV": ff.g_c_for_alpha(1.0, m_chi, kappa), "bounds": {}}
    for row in verified_rows():
        alpha_max = float(row["alpha_upper"])
        if row["lambda_rule"] == "lambda_min_excluded":
            lam = float(row["lambda_value"])
            scope = "all m_psi <= m_psi_max"
        else:
            lam = float(row["lambda_value"]) * EARTH_MOON_M
            scope = "only at m_psi = m_psi_at_bound"
        m_psi = ff.HBAR_C_EV_M / lam
        out["bounds"][row["record"]] = {
            "alpha_max": alpha_max, "lambda_m": lam, "m_psi_eV": m_psi, "scope": scope,
            "g_c_max_eV": ff.g_c_for_alpha(alpha_max, m_chi, kappa),
        }
    return out


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
