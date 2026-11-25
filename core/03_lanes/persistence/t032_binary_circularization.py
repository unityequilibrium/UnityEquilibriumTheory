"""Test Card T032 method: are short-period binaries the settled ones (D18)?

Claim (C_L3_TIDAL_SETTLING, wave D18): a body on an eccentric orbit is flexed at F ~ (G M/a^3)^2 n^2 e^2,
zero only when circular and synchronous; flexing dissipates until the orbit settles. F grows as a^-9 at
fixed masses (P^-6), so the settled (circular) state must be reached first by the shortest periods: the
fraction of circular orbits must fall as the period grows.

Comparison: orbital period P and eccentricity e of spectroscopic binaries in the SB9 catalogue (Pourbaix
et al. 2004 and updates; VizieR B/sb9/orbits), downloaded after approval into
docs/data/external/astro/sb9/sb9_orbits.tsv. One orbit per system (the lowest orbit number of each Seq).
    bins in P (days): [1, 3), [3, 10), [10, 30), [30, 100), [100, 300); P < 1 d excluded (contact systems)
    circular: e < 0.05 (orbits with e fixed at 0 count as circular)
    f_k = circular fraction in bin k; rho = Spearman rank correlation of (k, f_k)
    PASS:   f_1 >= 0.7 and rho <= -0.9
    FAILED: f_1 <= 0.5 or rho >= 0
    INCONCLUSIVE otherwise, or any bin with fewer than 30 systems.

Do not run against the comparison data before Test Card T032 is APPROVED.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/astro/sb9/sb9_orbits.tsv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CARD = ROOT / "docs/standard/tests/T032.json"
DATA_ID = "SB9_ORBITS_VIZIER"
EDGES = [1.0, 3.0, 10.0, 30.0, 100.0, 300.0]
E_CIRC = 0.05
MIN_PER_BIN = 30


def decide(periods, eccs) -> dict:
    P, e = np.asarray(periods, float), np.asarray(eccs, float)
    fr, counts = [], []
    for lo, hi in zip(EDGES[:-1], EDGES[1:]):
        sel = (P >= lo) & (P < hi)
        counts.append(int(sel.sum()))
        fr.append(float(np.mean(e[sel] < E_CIRC)) if sel.any() else float("nan"))
    if min(counts) < MIN_PER_BIN:
        return {"outcome": "INCONCLUSIVE", "reason": "a bin has fewer than 30 systems", "counts": counts, "f": fr}
    rho = float(spearmanr(range(len(fr)), fr).statistic)
    if fr[0] >= 0.7 and rho <= -0.9:
        out = "PASS"
    elif fr[0] <= 0.5 or rho >= 0.0:
        out = "FAILED"
    else:
        out = "INCONCLUSIVE"
    return {"outcome": out, "f": fr, "counts": counts, "rho": rho}


def load(path: Path):
    """VizieR TSV with columns Seq, o (orbit number), Per, e; '#' comments, a header, a unit line and a dash line."""

    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]
    head = [h.strip() for h in lines[0].split("\t")]
    best: dict[str, tuple[int, float, float]] = {}
    for ln in lines[1:]:
        parts = [p.strip() for p in ln.split("\t")]
        if len(parts) != len(head) or parts[0].startswith("-") or not parts[0][:1].isdigit():
            continue
        row = dict(zip(head, parts))
        try:
            seq, orb, per, ecc = row["Seq"], int(row["o"]), float(row["Per"]), float(row["e"] or 0.0)
        except ValueError:
            continue
        if seq not in best or orb < best[seq][0]:
            best[seq] = (orb, per, ecc)
    P = [v[1] for v in best.values()]
    e = [v[2] for v in best.values()]
    return P, e


def compute() -> dict:
    if json.loads(CARD.read_text(encoding="utf-8")).get("status") != "APPROVED":
        raise RuntimeError("Test Card T032 is not APPROVED")
    entry = next(x for x in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if x["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    P, e = load(DATA)
    out = decide(P, e)
    out["n_systems"] = len(P)
    return out


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
