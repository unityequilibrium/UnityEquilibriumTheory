"""Benchmark (no claim): does Benedict's own energy accounting explain how subject L.'s weight loss slowed?

Mainstream method (Benedict 1915; the same balance Hall's models are built on): the heat a faster produces each day,
split by Benedict into carbohydrate, fat and protein (Table 64, from gas exchange and urinary nitrogen), fixes how much
of each tissue was burned. Converted with Hall (2010) densities, fat 9.44 kcal/g, protein 4.7 kcal/g with 1.6 g water
per g, glycogen 4.18 kcal/g with 2.7 g water per g, it gives a predicted daily tissue loss, compared with the measured
daily weight loss (benedict1915_L_body_weight.csv). Nothing is fitted. Seen data; this tests no UET claim.

Result (2026-11-26), days 6-31: the heat-based tissue loss bends like the weights (late/early specific-rate ratio 0.90
predicted vs 0.92 observed) while heat per kilogram stays about constant (27.5 -> 27.0 kcal/kg/day); the slowing comes
from the fuel shift (protein's share of heat falls, protein sparing) and from the smaller body, not from a lower burn
per kilogram. The level is 28 percent short (0.25 vs 0.35 kg/day): water and salt loss are not in the heat balance.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HEAT = ROOT / "docs/data/external/biology/fasting/benedict1915_L_heat_table64.csv"
WEIGHT = ROOT / "docs/data/external/biology/fasting/benedict1915_L_body_weight.csv"
RHO_FAT, RHO_PROT, RHO_GLY = 9.44, 4.7, 4.18      # kcal/g (Hall 2010, Table 1)
H_PROT, H_GLY = 1.6, 2.7                           # g water per g (Hall 2010, Table 1)


def _rows(path: Path):
    return list(csv.DictReader(ln for ln in path.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")))


def tissue_loss_kg(rows):
    out = []
    for r in rows:
        fat = float(r["from_fat_kcal"]) / RHO_FAT
        prot = float(r["from_protein_kcal"]) / RHO_PROT
        gly = float(r["from_carbohydrate_kcal"]) / RHO_GLY
        out.append((fat + prot * (1 + H_PROT) + gly * (1 + H_GLY)) / 1000.0)
    return np.array(out)


def late_early_ratio(loss, weights, first=6):
    """Specific loss rate of days 19-31 over days 6-18 (same halves as T030)."""

    e = slice(first - 1, 18)
    l = slice(18, 31)
    k_e = loss[e].sum() / weights[first:19].mean() / 13.0
    k_l = loss[l].sum() / weights[19:32].mean() / 13.0
    return k_l / k_e


def compute() -> dict:
    heat = _rows(HEAT)
    W = np.array([float(r["mass_kg"]) for r in _rows(WEIGHT)])
    obs = W[:-1] - W[1:]
    pred = tissue_loss_kg(heat)
    D = np.array([float(r["total_heat_kcal"]) for r in heat])
    C = np.array([float(r["from_protein_kcal"]) for r in heat])
    w = slice(5, 31)
    return {"pred_kg_per_day_6_31": float(pred[w].mean()), "obs_kg_per_day_6_31": float(obs[w].mean()),
            "r_pred": float(late_early_ratio(pred, W)), "r_obs": float(late_early_ratio(obs, W)),
            "heat_per_kg_day6": float(D[5] / W[6]), "heat_per_kg_day31": float(D[30] / W[31]),
            "protein_share_of_heat_days_6_18": float(C[5:18].sum() / D[5:18].sum()),
            "protein_share_of_heat_days_19_31": float(C[18:31].sum() / D[18:31].sum())}


if __name__ == "__main__":
    import json
    print(json.dumps(compute(), indent=2))
