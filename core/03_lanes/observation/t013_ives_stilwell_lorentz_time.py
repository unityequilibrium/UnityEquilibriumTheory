"""Test Card T013 prediction method: P3 with real data, through the Ives-Stilwell observable.

1. P3 (thought experiment v3) with the Lorentzian local frame of the parent action (wave O7,
   uet_lorentz_time.py): two inertial observers are related by a boost, the "now" of distant events differs
   by dt' = -gamma beta dx, and the Doppler-shift product of counter- and co-propagating resonant lasers is
   nu_a nu_p / (nu_1 nu_2) = 1 exactly.
2. Prediction: epsilon = sqrt(nu_a nu_p / (nu_1 nu_2)) - 1 = 0.
3. epsilon and its 1-sigma uncertainty come from the four registered frequencies and their uncertainties,
   propagated as independent errors: sigma_epsilon = (1 + epsilon)/2 * sqrt(sum (sigma_i / nu_i)^2).
   z = |epsilon| / sigma_epsilon. PASS if z <= 2; FAILED if z > 3; otherwise INCONCLUSIVE.
4. Consistency check, part of the outcome: the registered frequencies must reproduce the published
   epsilon = (1.5 +- 2.3) e-9 to within 0.1e-9 and 0.1e-9, otherwise the record is INCONCLUSIVE.
5. Diagnostic (not part of the outcome): the absolute-time alternative gives epsilon = gamma - 1 at the
   registered beta; its z is reported.

Usage: python -m docs.core.03_lanes.observation.t013_ives_stilwell_lorentz_time
Prints the numbers only. A Result record needs an APPROVED Test Card (docs/STANDARD.md section 4).
"""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "docs/data/external/atomic/ives_stilwell/botermann2014_li_doppler_frequencies.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "BOTERMANN2014_LI_DOPPLER_FREQUENCIES"
PUBLISHED_EPSILON = 1.5e-9
PUBLISHED_SIGMA = 2.3e-9
PUBLISHED_TOLERANCE = 0.1e-9

lor = importlib.import_module("docs.core.03_lanes.observation.uet_lorentz_time")


def verified_values() -> dict[str, tuple[float, float]]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
    entry = next(e for e in entries if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch; data changed after registration")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return {r["quantity"]: (float(r["value_mhz"]), float(r["uncertainty_mhz"])) for r in csv.DictReader(lines)}


def compute() -> dict:
    v = verified_values()
    (n1, s1), (n2, s2) = v["nu_1_rest"], v["nu_2_rest"]
    (na, sa), (npar, sp) = v["nu_a_antiparallel"], v["nu_p_parallel"]
    beta = v["beta"][0]
    eps = sqrt(na * npar / (n1 * n2)) - 1.0
    sigma = (1.0 + eps) / 2.0 * sqrt(sum((s / n) ** 2 for s, n in ((s1, n1), (s2, n2), (sa, na), (sp, npar))))
    z = abs(eps) / sigma
    consistent = abs(eps - PUBLISHED_EPSILON) <= PUBLISHED_TOLERANCE and abs(sigma - PUBLISHED_SIGMA) <= PUBLISHED_TOLERANCE
    outcome = "INCONCLUSIVE" if not consistent else ("PASS" if z <= 2 else ("FAILED" if z > 3 else "INCONCLUSIVE"))
    eps_abs = lor.gamma(beta) - 1.0
    return {"epsilon": eps, "sigma_epsilon": sigma, "z": z, "matches_published": consistent,
            "alpha_reduced": eps / beta**2, "sigma_alpha_reduced": sigma / beta**2,
            "diagnostic_absolute_time_epsilon": eps_abs, "diagnostic_absolute_time_z": eps_abs / sigma,
            "outcome": outcome}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
