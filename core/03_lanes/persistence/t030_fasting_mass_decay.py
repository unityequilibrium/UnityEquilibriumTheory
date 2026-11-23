"""Test Card T030 method: does a fasting body lose its reserve exponentially (D14) or linearly?

Claim (C_L3_OPENNESS_LAYER3, wave D14): after a system is cut off from its supply, its layer-3 pool
leaks as R = R_ss exp(-delta t), so the specific loss rate -(dR/dt)/R stays constant. The alternative
(constant burn) loses the same absolute amount per day, so the specific rate rises as the body shrinks.

Comparison: daily naked morning body weight of subject L. during a 31-day fast, Benedict (1915)
A Study of Prolonged Fasting (Carnegie Inst. Wash. Pub. 203), transcribed after approval into
docs/data/external/biology/fasting/benedict1915_L_body_weight.csv (columns day, mass_kg).
Days 1-5 are excluded (human phase I); the rest is split into an early and a late half by time.
    k_early, k_late = specific loss rate in each half: (m_start - m_end)/((t_end - t_start) * m_mean)
    r      = k_late / k_early                 (D14: r = 1)
    r_lin  = m_mean_early / m_mean_late        (constant burn: r = r_lin > 1)
    PASS:  |r - 1| <= 0.25 (r_lin - 1)
    FAILED: r >= 1 + 0.75 (r_lin - 1)  or  r <= 1 - 0.75 (r_lin - 1)
    INCONCLUSIVE: otherwise, or fewer than 4 points in the window.

Do not run against the comparison data before Test Card T030 is APPROVED.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/biology/fasting/benedict1915_L_body_weight.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CARD = ROOT / "docs/standard/tests/T030.json"
DATA_ID = "BENEDICT1915_L_DAILY_BODY_WEIGHT"
FIRST_DAY = 6  # days 1-5 of the fast excluded (human phase I)


def half_rate(points: list[tuple[float, float]]) -> tuple[float, float]:
    """Specific loss rate over a run of (day, mass) points and its mean mass."""

    (t0, m0), (t1, m1) = points[0], points[-1]
    m_mean = sum(m for _, m in points) / len(points)
    return (m0 - m1) / ((t1 - t0) * m_mean), m_mean


def decide(points: list[tuple[float, float]]) -> dict:
    pts = sorted(p for p in points if p[0] >= FIRST_DAY)
    if len(pts) < 4:
        return {"outcome": "INCONCLUSIVE", "reason": "fewer than 4 points in the window"}
    t_mid = 0.5 * (pts[0][0] + pts[-1][0])
    early = [p for p in pts if p[0] <= t_mid]
    late = [p for p in pts if p[0] >= t_mid]
    if len(early) < 2 or len(late) < 2:
        return {"outcome": "INCONCLUSIVE", "reason": "a half has fewer than 2 points"}
    k_e, m_e = half_rate(early)
    k_l, m_l = half_rate(late)
    r, r_lin = k_l / k_e, m_e / m_l
    if abs(r - 1.0) <= 0.25 * (r_lin - 1.0):
        out = "PASS"
    elif r >= 1.0 + 0.75 * (r_lin - 1.0) or r <= 1.0 - 0.75 * (r_lin - 1.0):
        out = "FAILED"
    else:
        out = "INCONCLUSIVE"
    return {"outcome": out, "r": r, "r_lin": r_lin, "k_early_per_day": k_e, "k_late_per_day": k_l,
            "n_points": len(pts)}


def compute() -> dict:
    if json.loads(CARD.read_text(encoding="utf-8")).get("status") != "APPROVED":
        raise RuntimeError("Test Card T030 is not APPROVED")
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    rows = csv.DictReader(ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#"))
    return decide([(float(r["day"]), float(r["mass_kg"])) for r in rows])


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
