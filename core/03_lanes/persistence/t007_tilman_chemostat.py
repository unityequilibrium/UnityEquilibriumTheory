"""Test Card T007 prediction method: layer-3 resource selection versus Tilman (1977).

Layer 3 with two essential resources (phosphate P, silicate Si; growth set by the scarcer
one, Liebig's law) is the chemostat resource-ratio model. Using ONLY the monoculture
physiology of Table 1 (measured separately from the competition runs):

1. Persistence threshold (layer-3 R*) of species i on resource j at flow rate f:
       R*_ij = K_ij f / (mu_ij - f),   mu_ij = r_ij ln 2  (r in doublings/day)
2. Trade-off check: the species with the lower R*_P must have the higher R*_Si,
   otherwise one species wins everywhere and no coexistence region exists.
3. Each new cell uses 1/Y_ij of resource j, so species i consumes Si:P in the ratio
       c_i = Y_iP / Y_iSi
   For supply concentrations well above the R* values, the supply ratio Si/P decides:
       Si/P > c_P-better species  -> the P-better species wins
       Si/P < c_Si-better species -> the Si-better species wins
       between                    -> coexistence (mixed equilibrium, A4)
4. Compare the predicted boundaries with the observed ones (~80 and ~6) and the predicted
   outcome of each reported ratio group with the observed outcome.

Usage: python -m docs.core.03_lanes.persistence.t007_tilman_chemostat
Prints the numbers only. A Result record needs an APPROVED Test Card (docs/STANDARD.md section 4).
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "docs/data/external/ecology/tilman1977_chemostat/tilman1977_chemostat.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "TILMAN1977_CHEMOSTAT"
REFERENCE_FLOW = 0.25  # per day; used only for the R* trade-off check
GROUP_RATIOS = {"si_p_1000_455_100": [1000.0, 455.0, 100.0], "si_p_38": [38.0], "si_p_0.6": [0.6]}


def verified_rows() -> list[dict[str, str]]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]
    entry = next(e for e in entries if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch; data changed after registration")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return list(csv.DictReader(lines))


def r_star(k: float, r_doublings: float, flow: float) -> float:
    mu = r_doublings * math.log(2.0)
    if flow >= mu:
        return math.inf
    return k * flow / (mu - flow)


def predicted_outcome(ratio: float, p_better: str, si_better: str, c: dict[str, float]) -> str:
    if ratio > c[p_better]:
        return p_better
    if ratio < c[si_better]:
        return si_better
    return "coexistence"


def compute() -> dict:
    rows = verified_rows()
    phys: dict[str, dict[str, dict[str, float]]] = {}
    for r in rows:
        if r["record"] == "physiology":
            phys.setdefault(r["species"], {}).setdefault(r["nutrient"], {})[r["quantity"]] = float(r["value"])
    observed = {r["quantity"]: float(r["value"]) for r in rows if r["record"] == "outcome"}
    groups = {r["quantity"]: r["value"] for r in rows if r["record"] == "group"}

    rstar = {s: {n: r_star(v["K"], v["r"], REFERENCE_FLOW) for n, v in d.items()} for s, d in phys.items()}
    p_better = min(rstar, key=lambda s: rstar[s]["PO4"])
    si_better = min(rstar, key=lambda s: rstar[s]["SiO2"])
    tradeoff = p_better != si_better
    c = {s: d["PO4"]["Y"] / d["SiO2"]["Y"] for s, d in phys.items()}

    upper_pred, lower_pred = c[p_better], c[si_better]
    upper_obs = observed["observed_dominance_lower_si_p_boundary"]
    lower_obs = observed["observed_dominance_upper_si_p_boundary"]
    dev = {
        "upper_boundary_log10_ratio": abs(math.log10(upper_pred / upper_obs)),
        "lower_boundary_log10_ratio": abs(math.log10(lower_pred / lower_obs)),
    }
    short = {"Asterionella formosa": "A", "Cyclotella meneghiniana": "C", "coexistence": "coexistence"}
    group_results = {}
    for g, ratios in GROUP_RATIOS.items():
        preds = sorted({short[predicted_outcome(x, p_better, si_better, c)] for x in ratios})
        group_results[g] = {"predicted": preds, "observed": groups[g]}

    worst = max(dev.values())
    if not tradeoff:
        outcome = "FAILED"
    elif worst <= 0.1:
        outcome = "PASS"
    elif worst <= 0.3:
        outcome = "INCONCLUSIVE"
    else:
        outcome = "FAILED"
    return {
        "r_star_at_reference_flow_uM": rstar, "p_better": p_better, "si_better": si_better,
        "tradeoff": tradeoff, "consumption_ratio_si_per_p": c,
        "predicted_boundaries": {"upper": upper_pred, "lower": lower_pred},
        "observed_boundaries": {"upper": upper_obs, "lower": lower_obs},
        "boundary_deviation": dev, "groups": group_results, "outcome": outcome,
    }


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
