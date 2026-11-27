"""Test Card T042: red-blue antisymmetry of dynamical backaction read from two published figures.

Claim C_O8_OPTOMECHANICS_LANE: one coupling forces Gamma_opt(-Delta) = -Gamma_opt(+Delta) at the same power, i.e.
the layer-2 friction on the red side equals the layer-3 capture on the blue side.

This script REFUSES TO RUN until docs/standard/tests/T042.json has status APPROVED, and it checks the sha256 of both
figure files against docs/standard/data_manifest.json.

Pre-registered reading method (fixed by the card; only the calibration values in CALIBRATION are entered after
approval, from the figure itself, before any data value is computed):
1. Crop the panel; map pixels to data with two known ticks per axis (linear axes).
2. For each series colour, mask pixels within the colour tolerance, label connected components (scipy.ndimage) and
   keep components whose area lies in [area_min, area_max]; their centroids are the data points. Fit lines are not
   read (they are excluded by the area window or by colour).
3. y = plotted damping ratio minus 1 (Arcizet: Gamma_eff/Gamma_m - 1) or the plotted linewidth change (Benevides:
   gamma_OM, or gamma_m - gamma_i if the panel plots gamma_m, with gamma_i from the panel's far-detuned level).
4. Per series, split points by the sign of the detuning; on the overlap of |detuning| interpolate the side with more
   points linearly onto the |detuning| of the side with fewer points.
5. R = sum(y+ + y-) / sum(|y+| + |y-|) pooled over all pairs of a figure; R = 0 for exact antisymmetry.
6. Reading uncertainty: 200 draws jittering every centroid by +/-1 pixel (uniform) in x and y; report the
   standard deviation of R (not used in the criteria).
Criteria (card): PASS if |R| <= 0.15 in both figures; FAIL if |R| > 0.35 in either figure; otherwise INCONCLUSIVE;
also INCONCLUSIVE if a figure gives fewer than 3 pairs.
Requires Pillow (not pinned in .github/requirements-research.txt; local run only).
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
CARD = ROOT / "docs/standard/tests/T042.json"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
FIGS = {
    "ARCIZET2006_FIG4_PNG": "docs/data/external/optomechanics/arcizet2006/private/Cohadon_fig4.png",
    "BENEVIDES2017_FIG3_JPG": "docs/data/external/optomechanics/cmos_foundry2017/41598_2017_2515_Fig3_HTML.jpg",
}

# Entered after approval, from the figure, before computing R (see docstring). Structure per figure:
# {"crop": [x0, y0, x1, y1], "x_ticks": [[px, value], [px, value]], "y_ticks": [[py, value], [py, value]],
#  "y_kind": "ratio_minus_1" | "direct" | "minus_far_level", "far_level": float | None,
#  "series": [{"rgb": [r, g, b], "tol": int, "area_min": int, "area_max": int}, ...]}
CALIBRATION: dict = {}


def _check_preconditions() -> None:
    card = json.loads(CARD.read_text(encoding="utf-8"))
    if card.get("status") != "APPROVED" or "approval" not in card:
        raise SystemExit("T042 is not approved: refusing to open the figures")
    entries = {e["data_id"]: e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]}
    for did, rel in FIGS.items():
        h = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        if h != entries[did]["sha256"]:
            raise SystemExit(f"sha256 mismatch for {did}")
    if set(CALIBRATION) != set(FIGS):
        raise SystemExit("calibration not entered for every figure")


def to_data(px, py, cal):
    (x1p, x1), (x2p, x2) = cal["x_ticks"]
    (y1p, y1), (y2p, y2) = cal["y_ticks"]
    x = x1 + (px - x1p) * (x2 - x1) / (x2p - x1p)
    y = y1 + (py - y1p) * (y2 - y1) / (y2p - y1p)
    return x, y


def markers(img: np.ndarray, cal: dict) -> list[list[tuple[float, float]]]:
    from scipy import ndimage
    x0, y0, x1, y1 = cal["crop"]
    sub = img[y0:y1, x0:x1, :3].astype(int)
    out = []
    for s in cal["series"]:
        mask = np.all(np.abs(sub - np.array(s["rgb"])) <= s["tol"], axis=2)
        lab, nlab = ndimage.label(mask)
        pts = []
        for k in range(1, nlab + 1):
            ys, xs = np.nonzero(lab == k)
            if s["area_min"] <= xs.size <= s["area_max"]:
                pts.append((x0 + xs.mean(), y0 + ys.mean()))
        out.append(pts)
    return out


def transform_y(y: float, cal: dict) -> float:
    if cal["y_kind"] == "ratio_minus_1":
        return y - 1.0
    if cal["y_kind"] == "minus_far_level":
        return y - cal["far_level"]
    return y


def antisymmetry(series_pts: list[list[tuple[float, float]]]) -> tuple[float, int]:
    num = den = 0.0
    pairs = 0
    for pts in series_pts:
        neg = sorted((-x, y) for x, y in pts if x < 0)
        pos = sorted((x, y) for x, y in pts if x > 0)
        if len(neg) < 2 or len(pos) < 2:
            continue
        lo, hi = max(neg[0][0], pos[0][0]), min(neg[-1][0], pos[-1][0])
        few, many = (neg, pos) if len(neg) <= len(pos) else (pos, neg)
        mx, my = np.array([p[0] for p in many]), np.array([p[1] for p in many])
        for ax, ay in few:
            if lo <= ax <= hi:
                other = float(np.interp(ax, mx, my))
                num += ay + other
                den += abs(ay) + abs(other)
                pairs += 1
    return (num / den if den > 0 else float("nan")), pairs


def read_figure(did: str, rng: random.Random) -> dict:
    from PIL import Image
    cal = CALIBRATION[did]
    img = np.asarray(Image.open(ROOT / FIGS[did]).convert("RGB"))
    raw = markers(img, cal)

    def to_series(jit: bool):
        res = []
        for pts in raw:
            ser = []
            for px, py in pts:
                if jit:
                    px += rng.uniform(-1, 1); py += rng.uniform(-1, 1)
                x, y = to_data(px, py, cal)
                ser.append((x, transform_y(y, cal)))
            res.append(ser)
        return res

    R, pairs = antisymmetry(to_series(False))
    draws = [antisymmetry(to_series(True))[0] for _ in range(200)]
    return {"R": R, "pairs": pairs, "R_reading_sd": float(np.nanstd(draws)),
            "points_per_series": [len(p) for p in raw]}


def run() -> dict:
    _check_preconditions()
    rng = random.Random(42)
    res = {did: read_figure(did, rng) for did in FIGS}
    Rs = [abs(r["R"]) for r in res.values()]
    if any(r["pairs"] < 3 for r in res.values()):
        outcome = "INCONCLUSIVE"
    elif any(x > 0.35 for x in Rs):
        outcome = "FAIL"
    elif all(x <= 0.15 for x in Rs):
        outcome = "PASS"
    else:
        outcome = "INCONCLUSIVE"
    res["outcome"] = outcome
    return res


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
