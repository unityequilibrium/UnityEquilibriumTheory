"""Engine pilot (stars, layers 2-3): recompute the registered stellar results through core/engine.

Lane card: core/engine/lane_cards/stars_layer23.json. Inputs are the hash-locked data of the
closed Test Cards T002, T014 and T008; methods are the ones fixed in those cards. This is a
reproduction through the shared engine, not a new comparison: the Test Card outcomes stand.

1. HB/RGB (T002, T014): R = N_HB/N_RGB = abundance_ratio(tau_HB, tau_RGB) with tau_HB/tau_RGB = 6.26 Y - 0.12.
2. White dwarfs (T008): n = burn_exponent(7/2); slope d log10 N / d M_bol two ways:
   closed form 0.4 (n-1)/n, and numerically from the engine lifetime t(L) = integral dF/P with
   dN/dlog L proportional to t(L) (cooling-time law), evaluated deep in the faint tail.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from core.engine import layer23  # noqa: E402
from core.engine._load import load  # noqa: E402

MANIFEST = REPO / "docs/standard/data_manifest.json"
GC = REPO / "docs/data/external/astronomy/globular_cluster_r_parameter"
WD = REPO / "docs/data/external/astronomy/white_dwarf_lf/hu2007_sdss_da_wd_lf.csv"


def _rows(data_id: str, path: Path) -> list[dict]:
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == data_id)
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{data_id}: sha256 mismatch")
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return list(csv.DictReader(lines))


def hb_rgb() -> dict:
    ay = {r["quantity"]: r for r in _rows("AYALA14_GC_R_PARAMETER", GC / "ayala2014_r_parameter.csv")}
    go = {r["quantity"]: r for r in _rows("GONTCHAROV26_GC_R_PARAMETER", GC / "gontcharov2026_r_parameter.csv")}
    sysm = load("03_lanes/persistence/t002_model_systematics.py")
    slope, intercept = float(ay["R_th_slope_Y"]["value"]), float(ay["R_th_intercept"]["value"])
    y, s_y = float(ay["Y_HII_Aver"]["value"]), float(ay["Y_HII_Aver"]["uncertainty"])
    tau_ratio = slope * y + intercept  # tau_HB / tau_RGB from stellar models (fuel / luminosity)
    r_pred = layer23.abundance_ratio(tau_ratio, 1.0)
    s_pred = abs(slope) * s_y
    r_obs2, s_obs2 = float(ay["R_ave"]["value"]), float(ay["R_ave"]["uncertainty"])
    z_t002 = abs(r_pred - r_obs2) / math.hypot(s_pred, s_obs2)
    row = go["R_in_situ_constant"]
    r_obs14 = float(row["value"])
    s_obs14 = float(row["uncertainty_plus"]) if r_pred > r_obs14 else float(row["uncertainty_minus"])
    s_model = sysm.sigma_model_cassisi()
    z_t014 = abs(r_pred - r_obs14) / math.sqrt(s_pred**2 + s_model**2 + s_obs14**2)
    return {"R_pred": r_pred, "z_T002": z_t002, "z_T014": z_t014}


def wd_slope_numerical(n: float, l_ratio: float = 1e-8) -> float:
    """Slope from engine lifetimes: dN/dlog L ~ t(L); t(L) = lifetime from F0 down to F(L)."""
    f0, p0 = 1.0, 1.0

    def t_of(lum: float) -> float:
        return layer23.lifetime(f0, p0, n, f_min=f0 * lum ** (1.0 / n))

    lum_a, lum_b = l_ratio, l_ratio / 10.0
    dlog_t = math.log10(t_of(lum_b)) - math.log10(t_of(lum_a))  # per -1 in log10 L
    return 0.4 * dlog_t  # d log10 N / d M_bol, with d M_bol = -2.5 d log10 L


def white_dwarfs() -> dict:
    v = {r["quantity"]: float(r["value"]) for r in _rows("HU2007_SDSS_DA_WD_LF", WD)}
    n = layer23.burn_exponent(v["luminosity_power_of_core_temperature"])
    closed = layer23.luminosity_function_slope_per_mag(n)
    numeric = wd_slope_numerical(n)
    obs = v["lf_slope_per_mag"]
    return {"n": n, "slope_closed": closed, "slope_engine_lifetime": numeric, "slope_obs": obs,
            "log10_deviation": abs(math.log10(closed / obs))}


def compute() -> dict:
    return {"hb_rgb": hb_rgb(), "white_dwarfs": white_dwarfs()}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
