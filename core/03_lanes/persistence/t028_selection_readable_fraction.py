"""Test Card T028 prediction method: does selection raise the readable fraction r of energy-written bits?

r per species = 2 x genome size (bp) / (C_G x E_ATP / (k T ln 2)), with C_G the growth cost per cell division
(10^9 ATP) and cell volume V from Lynch and Marinov (2015), and effective population size Ne from Sung et al. (2012).
Fit: log10 r = a + b_V log10 V + b_Ne log10 Ne (ordinary least squares), 95 percent t-interval of b_Ne.
    PASS: interval wholly above 0
    FAILED: interval wholly at or below 0
    INCONCLUSIVE: otherwise, or fewer than 8 species in both tables.
Reported, not deciding: the simple slope of log10 r on log10 Ne.

Data files (digitised or transcribed after approval):
    docs/data/external/biology/readable_fraction/lynch_marinov2015_costs.csv  species, volume_um3, cg_1e9_atp, genome_bp
    docs/data/external/biology/readable_fraction/sung2012_ne.csv              species, ne

Do not run against the data before Test Card T028 is APPROVED.
"""

from __future__ import annotations

import csv
import hashlib
import json
from math import log
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
DIR = ROOT / "docs/data/external/biology/readable_fraction"
COSTS, NE = DIR / "lynch_marinov2015_costs.csv", DIR / "sung2012_ne.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CARD = ROOT / "docs/standard/tests/T028.json"
IDS = {"LYNCH_MARINOV2015_CELL_COSTS": COSTS, "SUNG2012_NE_TABLE": NE}
K_B, N_A = 1.380649e-23, 6.02214076e23
E_ATP = 50e3 / N_A   # J per ATP
T = 303.0
MIN_SPECIES = 8


def _rows(path: Path) -> list[dict]:
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return list(csv.DictReader(lines))


def readable_fraction(genome_bp: float, cg_1e9_atp: float) -> float:
    energy = cg_1e9_atp * 1e9 * E_ATP
    return 2.0 * genome_bp / (energy / (K_B * T * log(2.0)))


def fit(log_r: np.ndarray, log_v: np.ndarray, log_ne: np.ndarray) -> dict:
    x = np.column_stack([np.ones_like(log_r), log_v, log_ne])
    beta, *_ = np.linalg.lstsq(x, log_r, rcond=None)
    resid = log_r - x @ beta
    dof = len(log_r) - 3
    s2 = float(resid @ resid) / dof
    cov = s2 * np.linalg.inv(x.T @ x)
    q = stats.t.ppf(0.975, dof)
    se = float(np.sqrt(cov[2, 2]))
    return {"b_V": float(beta[1]), "b_Ne": float(beta[2]), "b_Ne_ci95": (float(beta[2] - q * se), float(beta[2] + q * se))}


def outcome(n: int, ci: tuple[float, float]) -> str:
    if n < MIN_SPECIES:
        return "INCONCLUSIVE"
    if ci[0] > 0.0:
        return "PASS"
    if ci[1] <= 0.0:
        return "FAILED"
    return "INCONCLUSIVE"


def compute() -> dict:
    if json.loads(CARD.read_text(encoding="utf-8")).get("status") != "APPROVED":
        raise RuntimeError("Test Card T028 is not APPROVED")
    entries = {e["data_id"]: e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]}
    for data_id, path in IDS.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != entries[data_id]["sha256"]:
            raise RuntimeError(f"{data_id}: sha256 mismatch")
    costs = {r["species"]: r for r in _rows(COSTS)}
    ne = {r["species"]: float(r["ne"]) for r in _rows(NE)}
    both = sorted(set(costs) & set(ne))
    dropped = sorted(set(costs) ^ set(ne))
    log_r = np.array([np.log10(readable_fraction(float(costs[s]["genome_bp"]), float(costs[s]["cg_1e9_atp"]))) for s in both])
    log_v = np.array([np.log10(float(costs[s]["volume_um3"])) for s in both])
    log_ne = np.array([np.log10(ne[s]) for s in both])
    out = {"species": both, "n": len(both), "dropped_or_unmatched": dropped}
    if len(both) >= 4:
        f = fit(log_r, log_v, log_ne)
        simple = stats.linregress(log_ne, log_r)
        out.update(f)
        out["outcome"] = outcome(len(both), f["b_Ne_ci95"])
        out["not_deciding_simple_slope"] = float(simple.slope)
        out["r_by_species"] = {s: float(10 ** v) for s, v in zip(both, log_r)}
    else:
        out["outcome"] = "INCONCLUSIVE"
    return out


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
