"""Test Card T025 prediction method: T023 repeated with a phylogenetic correction (topic 0.23).

T023 fitted log10 LEP = a + s log10 M + d_bird [bird] + d_bat [Chiroptera] by ordinary least squares,
treating species as independent, and recorded INCONCLUSIVE. Its card and result say the missing
phylogenetic correction makes the intervals too narrow. This module repeats the same fit by
phylogenetic generalized least squares (PGLS) under Brownian motion.

Data:
    AnAge Build 15, selected exactly as in T018 and T023 (298 species).
    TimeTree time-calibrated tree for those names (Kumar et al. 2022), registered as PRIVATE data:
    TimeTree allows personal research use but not redistribution, so the tree stays local and only
    its sha256 is in the manifest.

Placing species on the tree (fixed before any fit; the tree's leaf names were read, no fit was run):
    1. exact binomial leaf;
    2. if the tree holds only subspecies of the species, the alphabetically first subspecies leaf
       (any one gives the same covariances with every other species);
    3. a current name for an AnAge synonym, from the fixed table SYNONYMS;
    4. otherwise the species is dropped and listed (this includes taxa that TimeTree replaced
       with a genus or another species, which would sit on another taxon's tip).
    If more than 30 species are dropped or fewer than 20 bats remain, the outcome is INCONCLUSIVE.

Fit:
    V_ij = time from the root to the most recent common ancestor of i and j (V_ii = root age).
    beta = (X' V^-1 X)^-1 X' V^-1 y, sigma^2 = r' V^-1 r / (n - 4),
    95 percent intervals beta +- t(0.975, n - 4) SE, Delta = d_bat - d_bird from contrast (0, 0, -1, 1).
    PASS / FAILED / INCONCLUSIVE exactly as in T023 (thresholds 0.18 and 0.25).
Reported, not deciding: Pagel's lambda by maximum likelihood on [0, 1] with d_bat and Delta at that
lambda; ordinary least squares on the same placed species; dropped and substituted species.

Do not run against the data before Test Card T025 is APPROVED by the author (compute() checks).
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parents[3]
ANAGE = ROOT / "docs/data/external/biology/anage/anage_build15_data.txt"
TREE = ROOT / "docs/data/external/biology/timetree/private/tree_raw.nwk"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CARD = ROOT / "docs/standard/tests/T025.json"
ANAGE_ID = "ANAGE_BUILD15_LONGEVITY_METABOLISM"
TREE_ID = "TIMETREE_T023_SPECIES"
SECONDS_PER_YEAR = 365.25 * 86400.0
QUALITY = {"acceptable", "high"}
SAMPLE = {"medium", "large", "huge"}
D_BAT_MIN = 0.18
DELTA_BAND = 0.25
MAX_DROPPED = 30
MIN_BATS = 20
SYNONYMS = {
    "Anas_penelope": "Mareca_penelope",
    "Cryptomys_damarensis": "Fukomys_damarensis",
    "Cryptotis_parva": "Cryptotis_parvus",
    "Macropus_eugenii": "Notamacropus_eugenii",
    "Macropus_robustus": "Osphranter_robustus",
    "Macropus_rufus": "Osphranter_rufus",
    "Pecari_tajacu": "Dicotyles_tajacu",
    "Picoides_pubescens": "Dryobates_pubescens",
    "Sylvia_curruca": "Curruca_curruca",
    "Taurotragus_oryx": "Tragelaphus_oryx",
}


# ---------------------------------------------------------------- tree

def parse_newick(text: str) -> dict[str, list[tuple[int, float]]]:
    """Return, for every leaf, its ancestors from the root as (node id, depth from the root)."""
    text = text.strip().rstrip(";")
    pos = 0
    counter = [0]
    paths: dict[str, list[tuple[int, float]]] = {}

    def label() -> str:
        nonlocal pos
        start = pos
        if pos < len(text) and text[pos] == "'":
            end = text.index("'", pos + 1)
            pos = end + 1
            return text[start + 1:end]
        while pos < len(text) and text[pos] not in ",():;":
            pos += 1
        return text[start:pos].strip()

    def length() -> float:
        nonlocal pos
        if pos < len(text) and text[pos] == ":":
            pos += 1
            start = pos
            while pos < len(text) and text[pos] not in ",();":
                pos += 1
            return float(text[start:pos])
        return 0.0

    def node() -> list[tuple[str, list[tuple[int, float]]]]:
        """Parse one subtree; return its leaves with paths relative to this subtree's root (depth 0)."""
        nonlocal pos
        my_id = counter[0]
        counter[0] += 1
        if text[pos] == "(":
            pos += 1
            leaves = []
            while True:
                child = node()
                bl = length()
                leaves += [(name, [(nid, d + bl) for nid, d in path]) for name, path in child]
                if text[pos] == ",":
                    pos += 1
                    continue
                if text[pos] == ")":
                    pos += 1
                    break
                raise ValueError(f"unexpected {text[pos]!r} at {pos}")
            label()
            return [(name, [(my_id, 0.0)] + path) for name, path in leaves]
        name = label()
        return [(name, [(my_id, 0.0)])]

    for name, path in node():
        if name in paths:
            raise ValueError(f"duplicate leaf {name}")
        paths[name] = path
    return paths


def covariance(paths: dict[str, list[tuple[int, float]]], leaves: list[str]) -> np.ndarray:
    """Brownian-motion covariance: shared path length from the root."""
    anc = [dict(paths[leaf]) for leaf in leaves]
    n = len(leaves)
    v = np.empty((n, n))
    for i in range(n):
        for j in range(i, n):
            common = anc[i].keys() & anc[j].keys()
            v[i, j] = v[j, i] = max(anc[i][k] for k in common)
    return v


def place(binomial: str, leaves: set[str]) -> tuple[str | None, str]:
    """Rules 1-4 of the module docstring. Returns (leaf or None, rule)."""
    if binomial in leaves:
        return binomial, "exact"
    subspecies = sorted(leaf for leaf in leaves if leaf.startswith(binomial + "_"))
    if subspecies:
        return subspecies[0], "subspecies"
    current = SYNONYMS.get(binomial)
    if current:
        if current in leaves:
            return current, "synonym"
        subspecies = sorted(leaf for leaf in leaves if leaf.startswith(current + "_"))
        if subspecies:
            return subspecies[0], "synonym"
    return None, "dropped"


# ---------------------------------------------------------------- fit

def gls(x: np.ndarray, y: np.ndarray, v: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Generalized least squares; returns beta, covariance of beta, residual variance."""
    c = np.linalg.cholesky(v)
    xw = np.linalg.solve(c, x)
    yw = np.linalg.solve(c, y)
    beta, *_ = np.linalg.lstsq(xw, yw, rcond=None)
    r = yw - xw @ beta
    n, p = x.shape
    sigma2 = float(r @ r) / (n - p)
    cov = sigma2 * np.linalg.inv(xw.T @ xw)
    return beta, cov, sigma2


def interval(est: float, se: float, dof: int) -> tuple[float, float]:
    q = stats.t.ppf(0.975, dof)
    return float(est - q * se), float(est + q * se)


def lambda_transform(v: np.ndarray, lam: float) -> np.ndarray:
    out = lam * v
    np.fill_diagonal(out, np.diag(v))
    return out


def neg_log_likelihood(lam: float, x: np.ndarray, y: np.ndarray, v: np.ndarray) -> float:
    """Profile (ML) negative log-likelihood of Pagel's lambda."""
    vl = lambda_transform(v, lam)
    c = np.linalg.cholesky(vl)
    xw = np.linalg.solve(c, x)
    yw = np.linalg.solve(c, y)
    beta, *_ = np.linalg.lstsq(xw, yw, rcond=None)
    r = yw - xw @ beta
    n = len(y)
    s2 = float(r @ r) / n
    return 0.5 * (n * np.log(2 * np.pi * s2) + 2 * np.sum(np.log(np.diag(c))) + n)


def outcome(d_bat_ci: tuple[float, float], delta_ci: tuple[float, float], n_dropped: int, n_bats: int) -> str:
    if n_dropped > MAX_DROPPED or n_bats < MIN_BATS:
        return "INCONCLUSIVE"
    if d_bat_ci[0] > D_BAT_MIN and -DELTA_BAND <= delta_ci[0] and delta_ci[1] <= DELTA_BAND:
        return "PASS"
    if d_bat_ci[1] < D_BAT_MIN or delta_ci[0] > DELTA_BAND or delta_ci[1] < -DELTA_BAND:
        return "FAILED"
    return "INCONCLUSIVE"


def summarize(x: np.ndarray, y: np.ndarray, v: np.ndarray) -> dict:
    beta, cov, _ = gls(x, y, v)
    dof = len(y) - x.shape[1]
    contrast = np.array([0.0, 0.0, -1.0, 1.0])
    delta = float(contrast @ beta)
    delta_se = float(np.sqrt(contrast @ cov @ contrast))
    return {"s": float(beta[1]), "d_bird": float(beta[2]), "d_bat": float(beta[3]),
            "d_bat_ci95": interval(float(beta[3]), float(np.sqrt(cov[3, 3])), dof),
            "delta": delta, "delta_ci95": interval(delta, delta_se, dof)}


# ---------------------------------------------------------------- data

def _checked(path: Path, data_id: str) -> bytes:
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == data_id)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{data_id}: sha256 mismatch")
    return raw


def species() -> list[dict]:
    _checked(ANAGE, ANAGE_ID)
    out = []
    with ANAGE.open(encoding="latin-1", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["Class"] not in ("Aves", "Mammalia"):
                continue
            if not (r["Maximum longevity (yrs)"] and r["Metabolic rate (W)"] and r["Body mass (g)"]):
                continue
            if r["Data quality"] not in QUALITY or r["Sample size"] not in SAMPLE:
                continue
            mass = float(r["Body mass (g)"])
            lep_kj_g = float(r["Metabolic rate (W)"]) / mass * float(r["Maximum longevity (yrs)"]) * SECONDS_PER_YEAR / 1e3
            out.append({"name": f'{r["Genus"]}_{r["Species"]}', "bird": r["Class"] == "Aves",
                        "bat": r["Order"] == "Chiroptera", "log_m": np.log10(mass), "log_lep": np.log10(lep_kj_g)})
    return out


def compute() -> dict:
    if json.loads(CARD.read_text(encoding="utf-8")).get("status") != "APPROVED":
        raise RuntimeError("Test Card T025 is not APPROVED; do not run against the data")
    paths = parse_newick(_checked(TREE, TREE_ID).decode("utf-8"))
    rows = species()
    leaves = set(paths)
    placed, dropped, substituted = [], [], []
    for r in rows:
        leaf, rule = place(r["name"], leaves)
        if leaf is None:
            dropped.append(r["name"])
            continue
        if rule != "exact":
            substituted.append(f'{r["name"]} -> {leaf} ({rule})')
        placed.append({**r, "leaf": leaf})
    x = np.column_stack([np.ones(len(placed)), [r["log_m"] for r in placed],
                         [1.0 if r["bird"] else 0.0 for r in placed], [1.0 if r["bat"] else 0.0 for r in placed]])
    y = np.array([r["log_lep"] for r in placed])
    v = covariance(paths, [r["leaf"] for r in placed])
    deciding = summarize(x, y, v)
    n_bats = sum(r["bat"] for r in placed)
    lam = optimize.minimize_scalar(neg_log_likelihood, bounds=(0.0, 1.0), args=(x, y, v), method="bounded")
    return {
        "n_species": {"placed": len(placed), "dropped": len(dropped), "birds": sum(r["bird"] for r in placed),
                      "bats": n_bats, "other_mammals": sum(not r["bird"] and not r["bat"] for r in placed)},
        "root_age_mya": float(v[0, 0]),
        **deciding,
        "outcome": outcome(deciding["d_bat_ci95"], deciding["delta_ci95"], len(dropped), n_bats),
        "not_deciding": {
            "pagel_lambda": float(lam.x),
            "at_pagel_lambda": summarize(x, y, lambda_transform(v, float(lam.x))),
            "ols_same_species": summarize(x, y, np.eye(len(y))),
            "dropped": dropped,
            "substituted": substituted,
        },
    }


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
