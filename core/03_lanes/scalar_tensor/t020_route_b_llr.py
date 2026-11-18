"""Test Card T020 prediction method: lunar-laser-ranging bound on the route-B dissipation coupling (topic 0.23).

Route B (AI proposal, topics/0.23_Unity_Scale_Link/Doc/STRESS_03_ROUTE_B_DISSIPATION_COUPLING.md): the rate of
free-energy destruction sources psi, so a body carries psi-charge Q = a M + beta P. Relative to gravity the
extra force between bodies i and j is alpha + tau_m (x_i + x_j) + tau_beta^2 x_i x_j with x = (P/M)/c^2,
tau_beta^2 = beta^2/(4 pi G) and tau_m = sqrt(alpha) tau_beta (sign of a free).

Earth and Moon falling toward the Sun (lambda >> 1 AU):
    Delta = (m_G/m_I)_E - (m_G/m_I)_M = (x_E - x_M) (tau_beta^2 x_S + tau_m)
Primary (decides): a = 0 (pure route B), so Delta_pred = -tau_beta^2 x_S (x_M - x_E) <= 0.
    The data allow Delta >= Delta_obs - 2 sigma; hence tau_beta_max = sqrt((2 sigma - Delta_obs) / (x_S (x_M - x_E)))
    using the primary record (Biskupek et al. 2021).
P of each body: Sun = luminosity; Earth and Moon = absorbed sunlight (1 - Bond albedo) S pi R^2 plus internal heat
(free energy destroyed when sunlight thermalises; AI choice).
Reported, not deciding: tau_beta_max with the Williams et al. (2012) record; the worst-case shift from the mass-portal
cross term with |sqrt(alpha)| <= sqrt(5.1e-12) (T016); the Delta predicted for the benchmark tau_beta = 1/H0.
PASS if tau_beta = 0 is admissible (Delta_obs + 2 sigma >= 0) and tau_beta_max is finite.

Do not run against the data before the card is APPROVED by the author.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/gravity/llr_equivalence/llr_ep_earth_moon.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "LLR_EP_EARTH_MOON"
C2 = 299792458.0 ** 2
SOLAR_CONSTANT = 1361.0  # W/m^2 at 1 AU
BODIES = {  # mass kg, radius m, Bond albedo, internal heat W (NASA planetary fact sheets; AI-fixed values)
    "Earth": (5.9722e24, 6.371e6, 0.306, 4.7e13),
    "Moon": (7.346e22, 1.7374e6, 0.11, 0.0),
}
SUN_L, SUN_M = 3.828e26, 1.98847e30
H0_PER_S = 67.4e3 / 3.0857e22
SQRT_ALPHA_MAX = math.sqrt(5.1e-12)  # T016 envelope for lambda >= 1.9e8 m


def records() -> dict[str, tuple[float, float]]:
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return {r["record"]: (float(r["delta_central"]), float(r["delta_sigma"])) for r in csv.DictReader(lines)}


def specific_dissipation() -> dict[str, float]:
    x = {"Sun": SUN_L / SUN_M / C2}
    for name, (mass, radius, albedo, internal) in BODIES.items():
        x[name] = ((1.0 - albedo) * SOLAR_CONSTANT * math.pi * radius ** 2 + internal) / mass / C2
    return x


def tau_beta_max(delta: float, sigma: float, x: dict[str, float]) -> float:
    allowed = 2.0 * sigma - delta  # largest |Delta| on the negative side
    return math.sqrt(allowed / (x["Sun"] * (x["Moon"] - x["Earth"])))


def compute() -> dict:
    rec, x = records(), specific_dissipation()
    d, s = rec["biskupek2021"]
    t_max = tau_beta_max(d, s, x)
    # worst case with the mass-portal cross term: (x_M - x_E)(tau^2 x_S - sqrt(alpha) tau) = allowed
    allowed, dx = 2.0 * s - d, x["Moon"] - x["Earth"]
    t_cross = (SQRT_ALPHA_MAX + math.sqrt(SQRT_ALPHA_MAX ** 2 + 4.0 * x["Sun"] * allowed / dx)) / (2.0 * x["Sun"])
    t_h0 = 1.0 / H0_PER_S
    return {
        "x_per_s": x,
        "tau_beta_max_s": t_max, "tau_beta_max_yr": t_max / 3.15576e7,
        "outcome": "PASS" if (d + 2.0 * s >= 0.0 and math.isfinite(t_max)) else "FAIL",
        "not_deciding": {
            "tau_beta_max_williams2012_s": tau_beta_max(*rec["williams2012"], x),
            "tau_beta_max_with_cross_term_s": t_cross,
            "benchmark_tau_1_over_H0_s": t_h0,
            "benchmark_delta_pred": -t_h0 ** 2 * x["Sun"] * dx,
            "benchmark_ratio_to_allowed": t_h0 ** 2 * x["Sun"] * dx / allowed,
        },
    }


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
