"""Draft Test Card T016 prediction method: MICROSCOPE bound on the UET portal (topic 0.19 via the engine).

Lane: chi = nucleon, portal charge = nucleon number (module uet_portal_composition.py). The portal
then gives eta(Ti, Pt) = alpha eps_E (eps_TA6V - eps_PtRh10) Phi(r, R_E, lambda) >= 0.

Fixed method:
    eps from natural isotopic mean A and atomic weights, mass-fraction weighted over each alloy; eps_E = 1
    eta_allowed_max = eta_obs + 2 sqrt(stat^2 + syst^2)   (alpha >= 0, so only the positive side constrains)
    alpha_max(lambda) = eta_allowed_max / (eps_E d_eps Phi),  g_c_max = 5.1198e-10 eV sqrt(alpha_max)
    reported at lambda = 1e5, 1e6, 7e6, 1.922e8 (the T005 lunar range) and 1e12 m
    PASS if every alpha_max is positive and finite (g_c = 0 admissible); FAILED only if eta_obs - 2 sigma > 0
    while the portal is required to be non-zero (not the case here).

Do not run against the data before the card is APPROVED by the author.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/gravity/microscope/microscope2022_eta_and_composition.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "MICROSCOPE22_ETA_COMPOSITION"
G_C_FOR_ALPHA_1_EV = 5.119820210530964e-10  # T005 producer, m_chi = mean nucleon mass
LAMBDAS_M = (1e5, 1e6, 7e6, 1.922e8, 1e12)


def _module():
    path = ROOT / "core/03_lanes/scalar_tensor/uet_portal_composition.py"
    name = "uet_producer_dep_uet_portal_composition"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        sys.modules[name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sys.modules[name])
    return sys.modules[name]


def _values() -> dict[str, float]:
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return {r["quantity"]: float(r["value"]) for r in csv.DictReader(lines)}


def compute() -> dict:
    pc, v = _module(), _values()
    eps = {el: pc.charge_per_mass(v[f"{el}_mean_A"], v[f"{el}_atomic_weight"]) for el in ("Ti", "Al", "V", "Pt", "Rh")}
    ta6v = pc.alloy_charge_per_mass([(v["TA6V_mass_fraction_Ti"], eps["Ti"]), (v["TA6V_mass_fraction_Al"], eps["Al"]),
                                     (v["TA6V_mass_fraction_V"], eps["V"])])
    ptrh = pc.alloy_charge_per_mass([(v["PtRh10_mass_fraction_Pt"], eps["Pt"]), (v["PtRh10_mass_fraction_Rh"], eps["Rh"])])
    d_eps = ta6v - ptrh
    eta_max = v["eta_Ti_Pt"] + 2.0 * (v["eta_stat"] ** 2 + v["eta_syst"] ** 2) ** 0.5
    radius = v["earth_radius"]
    r = radius + v["orbit_altitude"]
    bounds = {}
    for lam in LAMBDAS_M:
        a = pc.alpha_max(eta_max, 1.0, d_eps, r, radius, lam)
        bounds[f"{lam:.3e}"] = {"alpha_max": a, "g_c_max_eV": G_C_FOR_ALPHA_1_EV * a**0.5, "m_psi_eV": 1.973269804e-7 / lam}
    finite = all(0.0 < b["alpha_max"] < float("inf") for b in bounds.values())
    return {"eps_TA6V": ta6v, "eps_PtRh10": ptrh, "d_eps": d_eps, "eta_allowed_max": eta_max,
            "bounds": bounds, "outcome": "PASS" if finite else "FAIL"}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
