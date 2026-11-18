"""Test Card T023 prediction method: lifetime energy of bats against birds (topic 0.23).

Author (2026-11-18): an organism does not have to manage its resources for itself; it may do so for
its species. AI translation: the lifetime reserve per gram is set at species level by how much the
environment kills (extrinsic mortality). Flight lowers extrinsic mortality, so flying lineages invest
more in maintenance and spend more energy per gram over a lifetime. T018 found birds about 2.5 times
above mammals. If flight, not being a bird, sets the reserve, bats (flying mammals) sit with the birds.

Data and selection: identical to T018 (AnAge Build 15, Aves and Mammalia, longevity, metabolic rate
and body mass present, data quality acceptable or high, sample size medium, large or huge).

Fit (ordinary least squares):
    log10 LEP = a + s log10 M + d_bird [bird] + d_bat [order Chiroptera]
95 percent percentile intervals from 10,000 species-level bootstrap resamples, seed 20261118.
Delta = d_bat - d_bird.
    PASS: the 95 percent interval of d_bat lies wholly above 0.18 and the 95 percent interval of Delta
          lies inside [-0.25, 0.25].
    FAILED: the upper end of the 95 percent interval of d_bat is below 0.18, or the 95 percent interval
          of Delta lies wholly outside [-0.25, 0.25].
    Otherwise INCONCLUSIVE.
Null (rate of living, no species-level allocation): d_bat = 0.

Reported, not deciding: d_bat with captivity records only; the two flightless birds (ostrich order and
penguin order) as single residuals.

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
SEED = 20261118
D_BAT_MIN = 0.18
DELTA_BAND = 0.25
FLIGHTLESS_ORDERS = {"Struthioniformes", "Rheiformes", "Casuariiformes", "Apterygiformes", "Tinamiformes", "Sphenisciformes"}


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
            out.append({"bird": r["Class"] == "Aves", "bat": r["Order"] == "Chiroptera",
                        "flightless_bird": r["Class"] == "Aves" and r["Order"] in FLIGHTLESS_ORDERS,
                        "log_m": np.log10(mass), "log_lep": np.log10(lep_kj_g), "origin": r["Specimen origin"]})
    return out


def fit(rows: list[dict]) -> np.ndarray:
    x = np.column_stack([np.ones(len(rows)), [r["log_m"] for r in rows],
                         [1.0 if r["bird"] else 0.0 for r in rows], [1.0 if r["bat"] else 0.0 for r in rows]])
    y = np.array([r["log_lep"] for r in rows])
    return np.linalg.lstsq(x, y, rcond=None)[0]


def outcome(d_bat_ci: tuple[float, float], delta_ci: tuple[float, float]) -> str:
    if d_bat_ci[0] > D_BAT_MIN and -DELTA_BAND <= delta_ci[0] and delta_ci[1] <= DELTA_BAND:
        return "PASS"
    if d_bat_ci[1] < D_BAT_MIN or delta_ci[0] > DELTA_BAND or delta_ci[1] < -DELTA_BAND:
        return "FAILED"
    return "INCONCLUSIVE"


def compute() -> dict:
    rows = species()
    a, s, d_bird, d_bat = fit(rows)
    rng = np.random.default_rng(SEED)
    boot = []
    while len(boot) < N_BOOT:
        sample = [rows[i] for i in rng.integers(0, len(rows), len(rows))]
        if any(r["bat"] for r in sample) and any(r["bird"] for r in sample):
            boot.append(fit(sample))
    boot = np.array(boot)
    ci = lambda v: tuple(float(x) for x in np.percentile(v, [2.5, 97.5]))
    d_bat_ci, delta_ci = ci(boot[:, 3]), ci(boot[:, 3] - boot[:, 2])
    captive = [r for r in rows if r["origin"] == "captivity"]
    flightless = [{"log_lep_residual": float(r["log_lep"] - (a + s * r["log_m"] + d_bird))} for r in rows if r["flightless_bird"]]
    return {
        "n_species": {"birds": sum(r["bird"] for r in rows), "bats": sum(r["bat"] for r in rows),
                      "other_mammals": sum(not r["bird"] and not r["bat"] for r in rows)},
        "s": float(s), "d_bird": float(d_bird), "d_bat": float(d_bat), "d_bat_ci95": d_bat_ci,
        "delta": float(d_bat - d_bird), "delta_ci95": delta_ci, "bat_factor": float(10 ** d_bat),
        "outcome": outcome(d_bat_ci, delta_ci),
        "not_deciding": {
            "captivity_only_d_bat": float(fit(captive)[3]) if sum(r["bat"] for r in captive) >= 3 else None,
            "n_captive_bats": sum(r["bat"] for r in captive),
            "flightless_bird_residuals_vs_flying_birds": flightless,
        },
    }


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
