"""Test Card T026 prediction method: switch glucose of cooperative yeast growth against direct growth on glucose.

Prediction (C_L3_TRACE_YEAST): G* = (1 - eps) h N_c / gamma_low from registered values only
(uet_layer3_trace_yeast.switch_glucose), about 1.56 mM, an upper estimate.
Comparison: Gore, Youk and van Oudenaarden (2009) growth rate against glucose, digitised into
docs/data/external/biology/yeast_sucrose/gore2009_growth_vs_glucose.csv (columns glucose_percent, growth_per_h,
glucose_halfwidth_log10, growth_halfwidth).

G_high = lowest glucose at which the growth rate reaches THRESHOLD = 0.457 per hour, linear in log10(glucose)
between neighbouring points. Its interval comes from shifting every point by its digitisation half-widths
(growth up and glucose left for the low end, growth down and glucose right for the high end).
    PASS: interval inside [G*/30, G*]
    FAILED: interval wholly above 3 G* or wholly below G*/30
    INCONCLUSIVE: otherwise, or if the threshold is never reached.

Do not run against the comparison data before Test Card T026 is APPROVED.
"""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
from math import log10
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/biology/yeast_sucrose/gore2009_growth_vs_glucose.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CARD = ROOT / "docs/standard/tests/T026.json"
DATA_ID = "GORE2009_GROWTH_VS_GLUCOSE"
THRESHOLD = 0.457
GLUCOSE_MOLAR_MASS = 180.16


def percent_to_mM(p: float) -> float:
    return p * 10.0 / GLUCOSE_MOLAR_MASS * 1e3


def first_crossing(points: list[tuple[float, float]], threshold: float) -> float | None:
    """Lowest glucose (mM) where growth reaches threshold, linear in log10(glucose); None if never reached."""
    pts = sorted(points)
    if pts[0][1] >= threshold:
        return pts[0][0]
    for (g0, r0), (g1, r1) in zip(pts, pts[1:]):
        if r0 < threshold <= r1:
            f = (threshold - r0) / (r1 - r0)
            return 10 ** (log10(g0) + f * (log10(g1) - log10(g0)))
    return None


def outcome(interval: tuple[float | None, float | None], g_star: float) -> str:
    lo, hi = interval
    if lo is None or hi is None:
        return "INCONCLUSIVE"
    if g_star / 30.0 <= lo and hi <= g_star:
        return "PASS"
    if lo > 3.0 * g_star or hi < g_star / 30.0:
        return "FAILED"
    return "INCONCLUSIVE"


def compute() -> dict:
    if json.loads(CARD.read_text(encoding="utf-8")).get("status") != "APPROVED":
        raise RuntimeError("Test Card T026 is not APPROVED")
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    rows = list(csv.DictReader(ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")))
    yeast = importlib.import_module("core.03_lanes.persistence.uet_layer3_trace_yeast")
    g_star = yeast.switch_glucose()["G_star_mM"]
    central, low, high = [], [], []
    for r in rows:
        g, rate = percent_to_mM(float(r["glucose_percent"])), float(r["growth_per_h"])
        dg, dr = 10 ** float(r["glucose_halfwidth_log10"]), float(r["growth_halfwidth"])
        central.append((g, rate))
        low.append((g / dg, rate + dr))
        high.append((g * dg, rate - dr))
    interval = (first_crossing(low, THRESHOLD), first_crossing(high, THRESHOLD))
    return {"G_star_mM": g_star, "G_high_mM": first_crossing(central, THRESHOLD), "G_high_interval_mM": interval,
            "max_growth_per_h": max(r for _, r in central), "n_points": len(central),
            "outcome": outcome(interval, g_star)}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
