"""Test Card T022 prediction method: the rest of the Lorentz transformation with real data.

1. The parent action's local frame is Lorentzian (wave O7). Its boost fixes the Robertson-Mansouri-Sexl
   parameters alpha = -1/2, beta = 1/2, delta = 0 (wave O8, uet_rms_light_speed.py), so both
   combinations vanish: P_MM = 0 (no orientation dependence of the two-way speed of light) and
   P_KT = 0 (no dependence on the laboratory velocity). The model value is computed, not typed in.
2. Data: P_MM from Herrmann et al. 2009 and P_KT (weighted mean) from Tobar et al. 2010, registered as
   RMS_MM_KT_2009_2010. z = |P_measured - P_model| / sigma for each.
3. PASS if both z <= 2. FAILED if either z > 3. Otherwise INCONCLUSIVE.
4. Diagnostics (not part of the outcome): z of the Galilean and contraction-only controls.

Usage: python core/03_lanes/observation/t022_michelson_morley_kennedy_thorndike.py
Prints the numbers only. A Result record needs an APPROVED Test Card (docs/STANDARD.md section 4).
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _core_module(relative: str):
    """Load core/<relative> by file path (folders start with digits)."""
    import importlib.util
    import sys
    path = ROOT / "core" / relative
    name = "uet_producer_dep_" + path.stem
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        sys.modules[name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sys.modules[name])
    return sys.modules[name]


DATA = ROOT / "docs/data/external/relativity/rms_lorentz/rms_mm_kt.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "RMS_MM_KT_2009_2010"

rms = _core_module("03_lanes/observation/uet_rms_light_speed.py")


def verified_values() -> dict[str, tuple[float, float]]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
    entry = next(e for e in entries if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch; data changed after registration")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return {r["quantity"]: (float(r["value"]), float(r["uncertainty"])) for r in csv.DictReader(lines)}


def compute() -> dict:
    v = verified_values()
    model = rms.rms_combinations(rms.lorentz_from_boost, v=1e-3)
    out: dict = {"model_P_MM": model["P_MM"], "model_P_KT": model["P_KT"]}
    zs = []
    for key in ("P_MM", "P_KT"):
        value, sigma = v[key]
        z = abs(value - model[key]) / sigma
        out[f"measured_{key}"] = value
        out[f"sigma_{key}"] = sigma
        out[f"z_{key}"] = z
        zs.append(z)
    out["outcome"] = "PASS" if max(zs) <= 2 else ("FAILED" if max(zs) > 3 else "INCONCLUSIVE")
    for name, kin in (("galilean", rms.galilean), ("contraction_only", rms.contraction_only)):
        c = rms.rms_combinations(kin, v=1e-3)
        out[f"diagnostic_{name}_z_MM"] = abs(v["P_MM"][0] - c["P_MM"]) / v["P_MM"][1]
        out[f"diagnostic_{name}_z_KT"] = abs(v["P_KT"][0] - c["P_KT"]) / v["P_KT"][1]
    return out


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
