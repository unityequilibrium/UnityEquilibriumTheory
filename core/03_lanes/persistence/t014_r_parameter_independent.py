"""Draft Test Card T014 prediction method: layer-3 abundance law vs independent R counts (Gontcharov 2026).

Same prediction as T002 (R = tau_HB / tau_RGB = 6.26 Y - 0.12 with Y = Y_HII_Aver, Little's law with
a common formation rate), compared with an independent count: HST ACS + Gaia DR3, 8 in-situ
clusters, R = 1.31 +0.06/-0.05. Unlike T002, a stellar-model error is fixed in advance from
published physics ranges (t002_model_systematics.sigma_model_cassisi, 0.029 in R).

Fixed method:
    R_pred = 6.26 Y - 0.12
    sigma_tot^2 = (6.26 sigma_Y)^2 + sigma_model^2 + sigma_obs^2,
    sigma_obs = the observed error on the side facing R_pred (upper if R_pred > R_obs)
    z = |R_pred - R_obs| / sigma_tot;  PASS z <= 2, INCONCLUSIVE 2 < z <= 3, FAIL z > 3

Do not run against the data before the card is APPROVED by the author.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent
GC_DIR = REPO / "docs/data/external/astronomy/globular_cluster_r_parameter"
MANIFEST = REPO / "docs/standard/data_manifest.json"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = sys.modules.setdefault(name, importlib.util.module_from_spec(spec))
    spec.loader.exec_module(mod)
    return mod


def _verified_lines(data_id: str, path: Path) -> list[str]:
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == data_id)
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{data_id}: sha256 mismatch")
    return [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]


def outcome(z: float) -> str:
    return "PASS" if z <= 2.0 else ("INCONCLUSIVE" if z <= 3.0 else "FAIL")


def compute() -> dict:
    ayala = {r["quantity"]: r for r in csv.DictReader(_verified_lines("AYALA14_GC_R_PARAMETER", GC_DIR / "ayala2014_r_parameter.csv"))}
    obs = {r["quantity"]: r for r in csv.DictReader(_verified_lines("GONTCHAROV26_GC_R_PARAMETER", GC_DIR / "gontcharov2026_r_parameter.csv"))}
    sysm = _load("t002_model_systematics", Path(__file__).resolve().parent / "t002_model_systematics.py")
    slope, intercept = float(ayala["R_th_slope_Y"]["value"]), float(ayala["R_th_intercept"]["value"])
    y, s_y = float(ayala["Y_HII_Aver"]["value"]), float(ayala["Y_HII_Aver"]["uncertainty"])
    r_pred, s_pred = slope * y + intercept, abs(slope) * s_y
    s_model = sysm.sigma_model_cassisi()
    row = obs["R_in_situ_constant"]
    r_obs = float(row["value"])
    s_obs = float(row["uncertainty_plus"]) if r_pred > r_obs else float(row["uncertainty_minus"])
    z = abs(r_pred - r_obs) / math.sqrt(s_pred**2 + s_model**2 + s_obs**2)
    return {"R_pred": r_pred, "sigma_pred": s_pred, "sigma_model": s_model, "R_obs": r_obs,
            "sigma_obs_used": s_obs, "z": z, "outcome": outcome(z)}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
