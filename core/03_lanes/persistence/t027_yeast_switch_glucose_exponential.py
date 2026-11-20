"""Test Card T027 prediction method: switch glucose of cooperative yeast growth against exponential growth on glucose.

Prediction (C_L3_TRACE_YEAST): G* = (1 - eps) h N_c / gamma_low from registered values only, about 1.56 mM.
Comparison: wild-type CEN.PK2-1C exponential growth rate against glucose, Youk and van Oudenaarden (2009) Figure 1,
digitised into docs/data/external/biology/yeast_sucrose/youk2009_wt_growth_vs_glucose.csv (columns glucose_percent,
growth_per_h, glucose_halfwidth_log10, growth_halfwidth).

G_fast = lowest glucose where the rate reaches RELATIVE = 0.968 of the strain's own maximum over the measured range,
linear in log10(glucose). Interval from shifting every point by its digitisation half-widths (rate up and glucose
left for the low end, rate down and glucose right for the high end; the maximum moves with its point).
    PASS: interval inside [G*/30, G*]
    FAILED: interval wholly above 3 G* or wholly below G*/30
    INCONCLUSIVE: otherwise, or if the crossing is not bracketed by measured points above G*/30.

Do not run against the comparison data before Test Card T027 is APPROVED.
"""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
from math import log10
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/biology/yeast_sucrose/youk2009_wt_growth_vs_glucose.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CARD = ROOT / "docs/standard/tests/T027.json"
DATA_ID = "YOUK2009_WT_GROWTH_VS_GLUCOSE"
RELATIVE = 0.968
GLUCOSE_MOLAR_MASS = 180.16


def percent_to_mM(p: float) -> float:
    return p * 10.0 / GLUCOSE_MOLAR_MASS * 1e3


def first_crossing(points: list[tuple[float, float]], relative: float) -> tuple[float | None, bool]:
    """(glucose in mM where rate first reaches relative x max, bracketed?) linear in log10(glucose)."""
    pts = sorted(points)
    target = relative * max(r for _, r in pts)
    if pts[0][1] >= target:
        return pts[0][0], False  # already above at the lowest measured point: crossing lies below it
    for (g0, r0), (g1, r1) in zip(pts, pts[1:]):
        if r0 < target <= r1:
            f = (target - r0) / (r1 - r0)
            return 10 ** (log10(g0) + f * (log10(g1) - log10(g0))), True
    return None, False


def outcome(low: tuple[float | None, bool], high: tuple[float | None, bool], g_star: float) -> str:
    (lo, lo_br), (hi, hi_br) = low, high
    if lo is None or hi is None:
        return "INCONCLUSIVE"
    floor = g_star / 30.0
    if not (lo_br and hi_br):
        # crossing at or below the lowest measured point (an upper bound only): it is wholly below the floor
        # only if that bound is below the floor at both ends; otherwise the card rules INCONCLUSIVE
        if hi < floor:
            return "FAILED"
        return "INCONCLUSIVE"
    if floor <= lo and hi <= g_star:
        return "PASS"
    if lo > 3.0 * g_star or hi < floor:
        return "FAILED"
    return "INCONCLUSIVE"


def compute() -> dict:
    if json.loads(CARD.read_text(encoding="utf-8")).get("status") != "APPROVED":
        raise RuntimeError("Test Card T027 is not APPROVED")
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
    c, lo, hi = first_crossing(central, RELATIVE), first_crossing(low, RELATIVE), first_crossing(high, RELATIVE)
    return {"G_star_mM": g_star, "G_fast_mM": c[0], "G_fast_interval_mM": (lo[0], hi[0]),
            "bracketed": (lo[1], hi[1]), "max_growth_per_h": max(r for _, r in central),
            "glucose_range_mM": (min(g for g, _ in central), max(g for g, _ in central)),
            "n_points": len(central), "outcome": outcome(lo, hi, g_star)}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
