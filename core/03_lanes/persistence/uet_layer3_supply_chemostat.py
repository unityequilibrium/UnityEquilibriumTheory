"""Layer 3 supply S in a measurable system: the chemostat (stage 3, wave L3-3).

Question: wave L3-2 (uet_layer3_supply.py) showed that the action fixes the pool loss delta and the
structure cost R* but not the supply S, which is a flux through the system's boundary, and that a
structure persists only if S > S* = delta R*_min. In which real system can S, delta and R* all be read
off, and does the threshold survive the saturating uptake that real consumers have (the action-derived
layer 3 is linear in R)?

Answer [AI derivation]:
1. A chemostat is a vessel of volume V fed at flow F with medium at resource concentration S0; the
   culture leaves at the same flow. With dilution rate D = F/V, consumers n_i, uptake-driven growth mu_i(R)
   and yield Y_i (new consumers per unit resource),
       dR/dt   = D S0 - D R - sum_i mu_i(R) n_i / Y_i
       dn_i/dt = (mu_i(R) - D) n_i.
   Term by term against the layer 3 pool equation dR/dt = S - delta R - R sum_i a_i F_i n_i:
       S = D S0 (boundary supply flux), delta = D (pool loss), 1/tau_i = D (washout),
       a_i R -> mu_i(R) (capture), F_i -> 1/Y_i (resource per unit structure).
   All of these are set or measured by the experimenter: S is no longer free.
2. Threshold for any increasing mu_i(R) with mu_i(0) = 0. An empty vessel holds R = S0; consumer i can
   invade iff mu_i(S0) > D, i.e. iff S0 > R*_i with mu_i(R*_i) = D. In layer 3 units this is
       S > S* = delta R*_min,
   the L3-2 threshold, so it does not need the linear uptake of the action-derived layer.
3. Steady state with species i alone: R = R*_i and n_i* = Y_i (S0 - R*_i) = Y_i (S - delta R*_i) / delta.
   For mu = a R (the action-derived case, F = 1/Y) this equals the layer 3 result
   n* = (S - delta R*)/(a F R*), because a R* = D = delta.
4. Monod uptake mu = mu_max R/(K + R) gives R* = K D/(mu_max - D) (Tilman 1977; Test Card T007).
   With the registered Table 1 physiology, the smallest supply flux that lets each diatom persist at
   D = 0.25 per day is S* = D R*: numbers in thresholds_tilman().

Not UET-distinct: this is chemostat theory (Monod 1950; Novick and Szilard 1950) and Tilman's R* rule.
What it adds to UET: the boundary supply that the action leaves open is, in this system, the product of
two quantities the experimenter controls, and the threshold holds for saturating uptake.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Callable, Sequence

import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[3]
l3 = importlib.import_module("core.03_lanes.persistence.uet_layer3_from_action")
supply = importlib.import_module("core.03_lanes.persistence.uet_layer3_supply")

Uptake = Callable[[float], float]


def monod(mu_max: float, k: float) -> Uptake:
    return lambda r: mu_max * r / (k + r)


def r_star(mu: Uptake, dilution: float, r_max: float = 1e9) -> float:
    """R* with mu(R*) = D for an increasing uptake; inf if D is never reached below r_max."""
    if mu(r_max) <= dilution:
        return float("inf")
    lo, hi = 0.0, 1.0
    while mu(hi) <= dilution:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if mu(mid) < dilution else (lo, mid)
    return 0.5 * (lo + hi)


def layer3_map(dilution: float, s0: float, yields: Sequence[float]) -> dict:
    """Chemostat quantities in layer 3 units."""
    return {"S": dilution * s0, "delta": dilution, "death": dilution, "quantum": [1.0 / y for y in yields]}


def simulate(mus: Sequence[Uptake], yields: Sequence[float], dilution: float, s0: float,
             n0: Sequence[float], r0: float, horizon: float) -> tuple[np.ndarray, float]:
    """Integrate the chemostat with arbitrary uptake functions; returns final (n, R)."""
    y_arr = np.asarray(yields, dtype=float)

    def rhs(_t: float, y: np.ndarray) -> np.ndarray:
        n, r = y[:-1], max(y[-1], 0.0)
        growth = np.array([m(r) for m in mus])
        dn = (growth - dilution) * n
        dr = dilution * s0 - dilution * r - float(np.sum(growth * n / y_arr))
        return np.append(dn, dr)

    sol = solve_ivp(rhs, (0.0, horizon), np.append(np.asarray(n0, float), r0), method="LSODA",
                    rtol=1e-10, atol=1e-13)
    return sol.y[:-1, -1], float(sol.y[-1, -1])


def steady_abundance(y: float, s0: float, rstar: float) -> float:
    return max(0.0, y * (s0 - rstar))


def thresholds_tilman(dilution: float = 0.25) -> dict:
    """S* = D R* (umol per litre per day) for each diatom and nutrient, from Test Card T007's registered data."""
    path = ROOT / "core/03_lanes/persistence/t007_tilman_chemostat.py"
    spec = importlib.util.spec_from_file_location("uet_t007_for_supply", path)
    t007 = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = t007
    spec.loader.exec_module(t007)
    phys: dict[str, dict[str, dict[str, float]]] = {}
    for row in t007.verified_rows():
        if row["record"] == "physiology":
            phys.setdefault(row["species"], {}).setdefault(row["nutrient"], {})[row["quantity"]] = float(row["value"])
    out = {}
    for species, nutrients in phys.items():
        for nutrient, p in nutrients.items():
            rs = r_star(monod(p["r"] * np.log(2.0), p["K"]), dilution)
            out[f"{species}/{nutrient}"] = {"R_star_uM": rs, "S_star_uM_per_day": supply.persistence_threshold(
                dilution, np.array([rs])), "R_star_t007_uM": t007.r_star(p["K"], p["r"], dilution)}
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(thresholds_tilman(), indent=2))
