"""Test Card T018 prediction method: cross-species lifespan as reserve / metabolic rate (topic 0.23).

Scope (declared by the author on 2026-11-17, STRESS_02 section 3): the lifespan of an animal is its
lifetime reserve divided by its metabolic rate, with the same reserve per gram in every species.
Then the lifetime energy potential LEP = (metabolic rate / body mass) * maximum longevity is the
same in every species (rate-of-living theory).

Data: AnAge Build 15, classes Aves and Mammalia with maximum longevity, metabolic rate and body
mass all present, data quality acceptable or high, sample size medium, large or huge. No species
is removed after the outcome is seen.

Fit (ordinary least squares): log10 LEP = a + s log10 M + d [bird], M = the body mass that belongs
to the metabolic-rate measurement. 95 percent intervals come from 10,000 species-level bootstrap
resamples with seed 20261117 (percentile method).
    PASS: the 95 percent interval of s lies inside [-0.05, 0.05] and that of d inside [-0.18, 0.18].
    FAILED: the 95 percent interval of s lies wholly outside [-0.10, 0.10], or that of d lies wholly
    above 0.30 (birds more than 2 times mammals).
    Otherwise INCONCLUSIVE.

Reported, not deciding: the fit with mammals only; the bird/mammal median LEP ratio; the fit on
records with specimen origin "captivity" only.

Do not run against the data before the card is APPROVED by the author.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/biology/anage/anage_build15_data.txt"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "ANAGE_BUILD15_LONGEVITY_METABOLISM"
SECONDS_PER_YEAR = 365.25 * 86400.0
QUALITY = {"acceptable", "high"}
SAMPLE = {"medium", "large", "huge"}
N_BOOT = 10_000
SEED = 20261117
S_PASS, D_PASS = 0.05, 0.18
S_FAIL, D_FAIL = 0.10, 0.30


def species() -> list[dict]:
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    out = []
    with DATA.open(encoding="latin-1", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["Class"] not in ("Aves", "Mammalia"):
                continue
            if not (r["Maximum longevity (yrs)"] and r["Metabolic rate (W)"] and r["Body mass (g)"]):
                continue
            if r["Data quality"] not in QUALITY or r["Sample size"] not in SAMPLE:
                continue
            mass = float(r["Body mass (g)"])
            lep_kj_g = float(r["Metabolic rate (W)"]) / mass * float(r["Maximum longevity (yrs)"]) * SECONDS_PER_YEAR / 1e3
            out.append({"bird": r["Class"] == "Aves", "log_m": np.log10(mass), "log_lep": np.log10(lep_kj_g),
                        "origin": r["Specimen origin"]})
    return out


def fit(rows: list[dict], with_bird: bool = True) -> np.ndarray:
    cols = [np.ones(len(rows)), [r["log_m"] for r in rows]]
    if with_bird:
        cols.append([1.0 if r["bird"] else 0.0 for r in rows])
    x = np.column_stack(cols)
    y = np.array([r["log_lep"] for r in rows])
    return np.linalg.lstsq(x, y, rcond=None)[0]


def outcome(s_ci: tuple[float, float], d_ci: tuple[float, float]) -> str:
    if -S_PASS <= s_ci[0] and s_ci[1] <= S_PASS and -D_PASS <= d_ci[0] and d_ci[1] <= D_PASS:
        return "PASS"
    if s_ci[0] > S_FAIL or s_ci[1] < -S_FAIL or d_ci[0] > D_FAIL:
        return "FAIL"
    return "INCONCLUSIVE"


def compute() -> dict:
    rows = species()
    _, s, d = fit(rows)
    rng = np.random.default_rng(SEED)
    boot = np.array([fit([rows[i] for i in rng.integers(0, len(rows), len(rows))]) for _ in range(N_BOOT)])
    s_ci = tuple(float(v) for v in np.percentile(boot[:, 1], [2.5, 97.5]))
    d_ci = tuple(float(v) for v in np.percentile(boot[:, 2], [2.5, 97.5]))
    birds = [10 ** r["log_lep"] for r in rows if r["bird"]]
    mammals = [10 ** r["log_lep"] for r in rows if not r["bird"]]
    captive = [r for r in rows if r["origin"] == "captivity"]
    return {
        "n_species": {"Aves": len(birds), "Mammalia": len(mammals)},
        "s": float(s), "s_ci95": s_ci,
        "d": float(d), "d_ci95": d_ci, "bird_factor": float(10 ** d),
        "outcome": outcome(s_ci, d_ci),
        "not_deciding": {
            "median_LEP_kJ_per_g": {"Aves": float(np.median(birds)), "Mammalia": float(np.median(mammals))},
            "mammals_only_slope": float(fit([r for r in rows if not r["bird"]], with_bird=False)[1]),
            "captivity_only_s_d": [float(v) for v in fit(captive)[1:]] if len(captive) > 10 else None,
            "n_captivity": len(captive),
        },
    }


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
