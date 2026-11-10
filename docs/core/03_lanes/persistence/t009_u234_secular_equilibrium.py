"""Test Card T009 prediction method: the abundance law in a nuclear decay chain.

The abundance law N = b tau (Little's law) for a decay chain in secular equilibrium gives
N(234U)/N(238U) = T_half(234U)/T_half(238U). Hu et al. (2025) used exactly this relation to
infer T_half(234U) from equilibrium abundances. If the law holds, that inferred half-life must
equal one measured without secular equilibrium (Varga et al. 2016).

    z = |T_eq - T_direct| / sqrt(sigma_eq^2 + sigma_direct^2)
    z <= 2 PASS, 2 < z <= 3 INCONCLUSIVE, z > 3 FAILED

Usage: python -m docs.core.03_lanes.persistence.t009_u234_secular_equilibrium
Prints the numbers only. A Result record needs an APPROVED Test Card (docs/STANDARD.md section 4).
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "docs/data/external/nuclear/u234_half_life/u234_half_life.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "U234_HALF_LIFE_EQ_VS_DIRECT"


def verified_rows() -> dict[str, tuple[float, float]]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
    entry = next(e for e in entries if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch; data changed after registration")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return {r["record"]: (float(r["value"]), float(r["sigma"])) for r in csv.DictReader(lines)}


def compute() -> dict:
    rows = verified_rows()
    (t_eq, s_eq), (t_dir, s_dir) = rows["equilibrium"], rows["direct"]
    z = abs(t_eq - t_dir) / math.hypot(s_eq, s_dir)
    outcome = "PASS" if z <= 2.0 else ("INCONCLUSIVE" if z <= 3.0 else "FAILED")
    return {"t_half_equilibrium_yr": t_eq, "t_half_direct_yr": t_dir, "difference_yr": t_eq - t_dir,
            "relative_difference": t_eq / t_dir - 1.0, "z": z, "outcome": outcome}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
