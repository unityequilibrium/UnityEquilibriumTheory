"""Test Card T024 prediction method: intervals between lighting innovations against world population (topic 0.25).

Two standard theories that UET can borrow from (synthesis, see SYNTHESIS_AUDIT P12):
    Kremer (1993, QJE 108, 681): invention rate proportional to population   ->  Delta t ~ N^-1        (slope -1)
    Bettencourt et al. (2007, PNAS 104, 7301): innovation output ~ N^beta, beta = 1.27 (new patents), growth
        reaches a finite-time singularity that a new innovation resets      ->  Delta t ~ N^-(beta-1) (slope -0.27)

Data:
    NORDHAUS1997_LIGHTING_MILESTONES   introduction years of lighting technologies (Nordhaus 1997, Table 1.1)
    OWID_POPULATION_WORLD_2026         world population (HYDE 3.3, Gapminder, UN WPP via Our World in Data)

Primary list (fixed before the run; rows of Table 1.1 that name a new lamp or light source for the first time):
    3000 B.C. candles, 2000 B.C. sesame-oil lamps, 1784 Argand lamp, 1792 coal gas, 1860s kerosene lamp,
    1876 arc light, 1879 carbon-filament lamp, 1880s Welsbach mantle, 1920s high-pressure discharge lamps,
    1930s fluorescent tube, 1980s compact fluorescent.
Excluded rows and why: fire (before the population series), stone lamps (date is a range), 1292 tax rolls
(market record), Middle Ages (period), 1798 (second use of the same coal gas), 1800s (candle fuel improvement),
1820 gas street lighting (deployment), 1855 Silliman (experiment), 1860 Royal Society (demonstration),
1882 Pearl Street (utility), 1931 sodium-vapor lamp (covered by the 1920s sodium-discharge row).

Method: Delta t_i = t_{i+1} - t_i; N_i = world population at t_i (log-linear interpolation between listed years);
ordinary least squares log10 Delta t_i = c + b log10 N_i; 95 percent interval of b from Student t with n - 2 dof.
    PASS (Bettencourt, beta = 1.27): the interval contains -0.27 and does not contain -1.
    FAILED (for beta = 1.27): the interval does not contain -0.27.
    INCONCLUSIVE otherwise.
Reported, not deciding: which of -1 and -0.27 the interval contains; the family-first variant
(candles, oil lamps, coal gas, kerosene, arc light, discharge lamps).

Do not run against the data before the card is APPROVED by the author.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
MILESTONES = ROOT / "docs/data/external/economics/lighting/nordhaus1997_table1_1_milestones.csv"
POPULATION = ROOT / "docs/data/external/economics/population/owid_population_world.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
IDS = {"NORDHAUS1997_LIGHTING_MILESTONES": MILESTONES, "OWID_POPULATION_WORLD_2026": POPULATION}
PRIMARY = ["3000 B.C.", "2000 B.C.", "1784", "1792", "1860s", "1876", "1879", "1880s", "1920s", "1930s", "1980s"]
FAMILY_FIRST = ["3000 B.C.", "2000 B.C.", "1792", "1860s", "1876", "1920s"]
BETTENCOURT_SLOPE = -0.27
KREMER_SLOPE = -1.0


def _check_hashes() -> None:
    entries = {e["data_id"]: e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]}
    for data_id, path in IDS.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != entries[data_id]["sha256"]:
            raise RuntimeError(f"{data_id}: sha256 mismatch")


def milestone_years() -> dict[str, float]:
    with MILESTONES.open(encoding="utf-8", newline="") as fh:
        return {r["date_label"]: float(r["year"]) for r in csv.DictReader(fh) if r["year"]}


def population_at(year: float) -> float:
    with POPULATION.open(encoding="utf-8", newline="") as fh:
        pts = sorted((float(r["year"]), float(r["population_historical"])) for r in csv.DictReader(fh))
    ys, ps = np.array([p[0] for p in pts]), np.log(np.array([p[1] for p in pts]))
    if not ys[0] <= year <= ys[-1]:
        raise ValueError(f"year {year} outside the population series")
    return float(np.exp(np.interp(year, ys, ps)))


def fit(labels: list[str]) -> dict:
    years = milestone_years()
    t = sorted(years[label] for label in labels)
    dt = np.diff(t)
    N = np.array([population_at(x) for x in t[:-1]])
    x, y = np.log10(N), np.log10(dt)
    res = stats.linregress(x, y)
    half = stats.t.ppf(0.975, len(x) - 2) * res.stderr
    ci = (float(res.slope - half), float(res.slope + half))
    return {"n_intervals": int(len(dt)), "slope": float(res.slope), "slope_ci95": ci,
            "contains_bettencourt": ci[0] <= BETTENCOURT_SLOPE <= ci[1], "contains_kremer": ci[0] <= KREMER_SLOPE <= ci[1],
            "intervals_years": [float(v) for v in dt], "population_at_start": [float(v) for v in N]}


def outcome(f: dict) -> str:
    if f["contains_bettencourt"] and not f["contains_kremer"]:
        return "PASS"
    if not f["contains_bettencourt"]:
        return "FAILED"
    return "INCONCLUSIVE"


def compute() -> dict:
    _check_hashes()
    primary = fit(PRIMARY)
    return {"primary": primary, "outcome": outcome(primary), "not_deciding": {"family_first": fit(FAMILY_FIRST)}}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
