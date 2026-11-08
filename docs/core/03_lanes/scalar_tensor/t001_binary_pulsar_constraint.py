"""Test Card T001 prediction method: UET parent vs binary-pulsar DEF bounds.

Method (fixed before the comparison is run; docs/standard/tests/T001.json):
1. Map the UET parent onto DEF with beta0 = -2 xi_c and alpha0 = 0 at psi0 = 0
   (claim C_UET_DEF_MAPPING, L1; module uet_scalar_tensor_mapping.py).
2. Read the published DEF bound (data_id ZFKSW22_DEF_BOUNDS). Its analysis
   covers beta0 in [beta_min, beta_max] and excludes spontaneous scalarization
   there (|alpha_A| <~ 6e-3, 90% CL, massless scalar).
3. Excluded xi_c interval = [-beta_max/2, -beta_min/2].
4. Light-scalar domain: the massless bound is used only when the scalar's
   reduced Compton wavelength exceeds 10 x the largest orbital separation
   among the seven binaries: m_psi c^2 <= hbar c / (10 a_max), where
   a = (G M P^2 / 4 pi^2)^(1/3) from the published P_b and GR masses.

Constants: GM_sun = 1.3271244e20 m^3 s^-2 (IAU 2015 nominal);
hbar c = 1.973269804e-7 eV m (CODATA 2018).

Usage: python docs/core/03_lanes/scalar_tensor/t001_binary_pulsar_constraint.py
Prints the numbers only. Writing a Result record requires an APPROVED
Test Card and is done in a separate, later commit (docs/STANDARD.md §4).
"""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "docs/data/external/gravity/binary_pulsar_def/zfksw22_def_bounds.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "ZFKSW22_DEF_BOUNDS"

GM_SUN = 1.3271244e20  # m^3 s^-2
HBAR_C_EV_M = 1.973269804e-7  # eV m
DAY = 86400.0
DOMAIN_MARGIN = 10.0


def verified_rows() -> list[dict[str, str]]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
    entry = next(e for e in entries if e["data_id"] == DATA_ID)
    digest = hashlib.sha256(DATA.read_bytes()).hexdigest()
    if digest != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch; data changed after registration")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return list(csv.DictReader(lines))


def orbital_separation_m(period_days: float, total_mass_sun: float) -> float:
    period = period_days * DAY
    return (GM_SUN * total_mass_sun * period**2 / (4.0 * math.pi**2)) ** (1.0 / 3.0)


def compute() -> dict:
    rows = verified_rows()
    bound = {r["quantity"]: float(r["value"]) for r in rows if r["record"] == "bound"}
    separations = {}
    for r in rows:
        if r["record"] != "orbit":
            continue
        masses = dict(item.split("=") for item in r["note"].split(";"))
        separations[r["quantity"]] = orbital_separation_m(float(r["value"]), float(masses["mp"]) + float(masses["mc"]))
    widest = max(separations, key=separations.get)
    a_max = separations[widest]

    mapping = importlib.import_module("docs.core.02_equations.covariant.uet_scalar_tensor_mapping")
    beta_per_xi = mapping.uet_def_parameters(1.0, kappa=1.0)["beta0"]  # = -2
    xi_low = bound["beta0_prior_max"] / beta_per_xi
    xi_high = bound["beta0_prior_min"] / beta_per_xi
    return {
        "beta0_per_xi_c": beta_per_xi,
        "excluded_xi_c_min": min(xi_low, xi_high),
        "excluded_xi_c_max": max(xi_low, xi_high),
        "alpha_A_limit_90cl": bound["abs_alpha_A_upper_limit"],
        "widest_binary": widest,
        "a_max_m": a_max,
        "light_domain_max_m_psi_eV": HBAR_C_EV_M / (DOMAIN_MARGIN * a_max),
        "separations_m": separations,
    }


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
