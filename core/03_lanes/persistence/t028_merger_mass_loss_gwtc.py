"""Test Card T028 method: mass radiated in black-hole mergers against the GWTC catalogue.

Claim (C_L3_FALLING_TOGETHER, wave D8): a non-spinning black-hole merger radiates at least the inspiral loss to the
innermost stable orbit, L = eta (1 - sqrt(8/9)) = 0.0572 eta of the total mass (eta = m1 m2/(m1 + m2)^2), and at most
the area-theorem cap U = 1 - sqrt(m1^2 + m2^2)/(m1 + m2).

Comparison: GWOSC event API, cumulative GWTC list, retrieved 2026-11-22
(docs/data/external/gravity/gwtc/gwosc_gwtc_events_2026-11-22.json). Per event the catalogue gives medians of the
source-frame component masses, the final mass and chi_eff. Sample, fixed before the values are read:
    events with m1, m2, M_f and chi_eff all reported, m2 >= 3 M_sun (both components black holes by mass),
    and |chi_eff| < 0.2 (nearly non-spinning, the scope of the claim).
Radiated fraction from medians: f = 1 - M_f/(m1 + m2).
    PASS: at least 90 % of the sample has L <= f <= U
    FAILED: more than 25 % of the sample lies outside [L, U]
    INCONCLUSIVE: otherwise, or fewer than 20 events in the sample
Reported but not deciding: median of f/L (how much of the loss the inspiral alone accounts for), the same count for
all spins, and which side each outside event falls on.

Do not run against the comparison data before Test Card T028 is APPROVED.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/gravity/gwtc/gwosc_gwtc_events_2026-11-22.json"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CARD = ROOT / "docs/standard/tests/T028.json"
OUT = ROOT / "core/07_artifacts/t028/t028_merger_mass_loss_gwtc.json"
DATA_ID = "GWOSC_GWTC_EVENTS_2026_11_22"
M2_MIN = 3.0
CHI_MAX = 0.2
PASS_SHARE = 0.90
FAIL_SHARE = 0.25
MIN_EVENTS = 20


def bounds(m1: float, m2: float, ft) -> tuple[float, float]:
    eta = m1 * m2 / (m1 + m2) ** 2
    return eta * ft.inspiral_fraction_of_mu(), ft.area_theorem_cap(m1, m2)


def classify(events: list[dict], ft) -> dict:
    inside, below, above, ratios = [], [], [], []
    for ev in events:
        m1, m2, mf = ev["mass_1_source"], ev["mass_2_source"], ev["final_mass_source"]
        f = 1.0 - mf / (m1 + m2)
        lo, hi = bounds(m1, m2, ft)
        ratios.append(f / lo)
        row = {"event": ev["commonName"], "f": f, "L": lo, "U": hi, "chi_eff": ev["chi_eff"]}
        (below if f < lo else above if f > hi else inside).append(row)
    n = len(events)
    return {"n": n, "inside": len(inside), "share_inside": len(inside) / n if n else None,
            "below": below, "above": above, "median_f_over_L": median(ratios) if ratios else None}


def outcome(c: dict) -> str:
    if c["n"] < MIN_EVENTS:
        return "INCONCLUSIVE"
    if c["share_inside"] >= PASS_SHARE:
        return "PASS"
    if 1.0 - c["share_inside"] > FAIL_SHARE:
        return "FAILED"
    return "INCONCLUSIVE"


def compute() -> dict:
    if json.loads(CARD.read_text(encoding="utf-8")).get("status") != "APPROVED":
        raise RuntimeError("Test Card T028 is not APPROVED")
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    ft = importlib.import_module("core.03_lanes.persistence.uet_falling_together")
    events = json.loads(DATA.read_text(encoding="utf-8"))["events"].values()
    complete = [e for e in events if all(e.get(k) is not None for k in
                                         ("mass_1_source", "mass_2_source", "final_mass_source", "chi_eff"))]
    bbh = [e for e in complete if e["mass_2_source"] >= M2_MIN]
    sample = [e for e in bbh if abs(e["chi_eff"]) < CHI_MAX]
    main, all_spins = classify(sample, ft), classify(bbh, ft)
    return {"test_id": "T028", "outcome": outcome(main), "data_sha256": entry["sha256"],
            "n_complete": len(complete), "n_bbh": len(bbh), "sample": main, "all_spins_descriptive": all_spins}


def main() -> None:
    res = compute()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8", newline="\n")
    s = res["sample"]
    print(f"T028 {res['outcome']}: {s['inside']}/{s['n']} inside [L, U] ({s['share_inside']:.3f}); "
          f"below {len(s['below'])}, above {len(s['above'])}; median f/L = {s['median_f_over_L']:.2f}")


if __name__ == "__main__":
    main()
