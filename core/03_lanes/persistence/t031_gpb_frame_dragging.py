"""Test Card T031 method: Earth's frame dragging on the Gravity Probe B gyroscopes (weak-field part of D17).

Claim (C_L3_MACH_FRAME_DRAGGING, wave D17): rotating matter drags local inertial frames; in the weak field
the drag is the gravitomagnetic precession Omega(r) = G/(c^2 r^3) [3 (J.r) r - J] (r unit vector). A
gyroscope on a circular orbit with normal n averages this to
    <Omega> = G/(c^2 a^3) [J/2 - (3/2)(J.n) n],
which for a polar orbit is G J/(2 c^2 a^3) along J. The gyroscope points at the guide star (declination
delta), so its pointing drifts at |<Omega> x s| = G J cos(delta)/(2 c^2 a^3), east-west.

Inputs (AI-chosen literature constants, fixed before the comparison is read):
    Earth polar moment of inertia C = 8.034e37 kg m^2, rotation rate 7.292115e-5 rad/s,
    GP-B orbit: circular polar, altitude 642 km above R_E = 6378.137 km (a = 7020.137 km),
    guide star IM Pegasi, declination +16.84 deg.
Comparison: the measured frame-dragging drift rate and its 1-sigma uncertainty from Everitt et al. (2011)
PRL 106, 221101 (arXiv:1105.3456), transcribed after approval into
docs/data/external/gravity/gpb/everitt2011_frame_dragging.csv (columns quantity, value_mas_per_yr, sigma).
    PASS:   |pred - meas| <= 2 sigma
    FAILED: |pred - meas| >  3 sigma
    INCONCLUSIVE otherwise.

Do not run against the comparison data before Test Card T031 is APPROVED.
"""

from __future__ import annotations

import csv
import hashlib
import json
from math import cos, pi, radians
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/gravity/gpb/everitt2011_frame_dragging.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CARD = ROOT / "docs/standard/tests/T031.json"
DATA_ID = "EVERITT2011_GPB_FRAME_DRAGGING"

G, C_LIGHT = 6.67430e-11, 299792458.0
C_EARTH, OMEGA_EARTH = 8.034e37, 7.292115e-5
A_ORBIT = (6378.137 + 642.0) * 1e3
DEC_GUIDE = radians(16.84)
MAS_PER_YR = 180.0 / pi * 3600e3 * 3.15576e7  # rad/s -> mas/yr


def averaged_precession_numeric(J_vec, n_vec, a: float, N: int = 4096):
    """Orbit average of the gravitomagnetic precession, sampled on the circular orbit."""

    n = np.asarray(n_vec, float) / np.linalg.norm(n_vec)
    e1 = np.cross(n, [0.0, 0.0, 1.0]) if abs(n[2]) < 0.9 else np.cross(n, [1.0, 0.0, 0.0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    th = 2.0 * pi * np.arange(N) / N
    r = np.outer(np.cos(th), e1) + np.outer(np.sin(th), e2)
    J = np.asarray(J_vec, float)
    om = G / (C_LIGHT ** 2 * a ** 3) * (3.0 * (r @ J)[:, None] * r - J)
    return om.mean(axis=0)


def predicted_drift_mas_per_yr() -> float:
    J = np.array([0.0, 0.0, C_EARTH * OMEGA_EARTH])
    n = np.array([1.0, 0.0, 0.0])  # polar orbit: normal in the equatorial plane
    om = averaged_precession_numeric(J, n, A_ORBIT)
    s = np.array([0.0, np.cos(DEC_GUIDE), np.sin(DEC_GUIDE)])  # guide star in the orbit plane
    return float(np.linalg.norm(np.cross(om, s)) * MAS_PER_YR)


def predicted_closed_form_mas_per_yr() -> float:
    return G * C_EARTH * OMEGA_EARTH * cos(DEC_GUIDE) / (2.0 * C_LIGHT ** 2 * A_ORBIT ** 3) * MAS_PER_YR


def decide(pred: float, meas: float, sigma: float) -> dict:
    z = abs(pred - meas) / sigma
    out = "PASS" if z <= 2.0 else ("FAILED" if z > 3.0 else "INCONCLUSIVE")
    return {"outcome": out, "predicted_mas_per_yr": pred, "measured_mas_per_yr": meas, "sigma": sigma, "z": z}


def compute() -> dict:
    if json.loads(CARD.read_text(encoding="utf-8")).get("status") != "APPROVED":
        raise RuntimeError("Test Card T031 is not APPROVED")
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    rows = {r["quantity"]: r for r in csv.DictReader(
        ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#"))}
    fd = rows["frame_dragging"]
    return decide(predicted_drift_mas_per_yr(), float(fd["value_mas_per_yr"]), float(fd["sigma"]))


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
