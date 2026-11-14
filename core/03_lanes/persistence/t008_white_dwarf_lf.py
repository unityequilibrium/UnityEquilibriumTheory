"""Test Card T008 prediction method: white dwarf luminosity function slope from the burn law.

1. Mestel cooling: L ~ T_c^(7/2), stored thermal energy F ~ T_c, so P ~ F^n with n = 7/2
   (uet_path_a_models.burn_exponent_from_luminosity_law).
2. A4 lifetime + abundance law: dN/dlog L ~ t(L) ~ L^(-5/7), slope d log10 N / d M_bol = 0.4 (n-1)/n.
3. Compare with the observed SDSS DA slope (Hu, Wu & Wu 2007) over M_bol 6.0-13.5 using the
   path-A ratio rule: |log10(predicted/observed)| <= 0.1 PASS, <= 0.3 INCONCLUSIVE, else FAILED.

Usage: python -m docs.core.03_lanes.persistence.t008_white_dwarf_lf
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
DATA = ROOT / "docs/data/external/astronomy/white_dwarf_lf/hu2007_sdss_da_wd_lf.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "HU2007_SDSS_DA_WD_LF"


def verified_values() -> dict[str, float]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
    entry = next(e for e in entries if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch; data changed after registration")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return {r["quantity"]: float(r["value"]) for r in csv.DictReader(lines)}


def compute() -> dict:
    pa = importlib.import_module("docs.core.03_lanes.persistence.uet_path_a_models")
    v = verified_values()
    n = pa.burn_exponent_from_luminosity_law(v["luminosity_power_of_core_temperature"])
    pred = pa.luminosity_function_slope_per_mag(n)
    obs = v["lf_slope_per_mag"]
    dev = abs(math.log10(pred / obs))
    outcome = "PASS" if dev <= 0.1 else ("INCONCLUSIVE" if dev <= 0.3 else "FAILED")
    return {"burn_exponent_n": n, "predicted_slope": pred, "observed_slope": obs,
            "fit_range_mbol": [v["fit_range_min_mbol"], v["fit_range_max_mbol"]],
            "relative_difference": obs / pred - 1.0, "log10_deviation": dev, "outcome": outcome}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
