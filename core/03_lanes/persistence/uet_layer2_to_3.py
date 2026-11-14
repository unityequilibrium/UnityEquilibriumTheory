"""Link from layer 2 (burning free energy) to layer 3 (selection), wave A4.

A3 found that passive friction burns at P proportional to F, while layer 3 assumed
a constant burn power. This module replaces the assumption tau = F/P by the law that
follows from layer 2 for any burn rule:

    dF/dt = -P(F)   =>   tau = integral_{F_min}^{F0} dF / P(F)

For the power-law family P(F) = P0 (F/F0)^n:
    n = 0  (regulated burner, e.g. a star)      tau = (F0 - F_min)/P0
    n = 1  (passive linear friction, A3)        tau = (F0/P0) ln(F0/F_min)
    n != 1                                      tau = F0/(P0 (1-n)) [1 - (F_min/F0)^(1-n)]
For n >= 1 the lifetime diverges as F_min -> 0: a passive system never fully dies,
so a finite threshold F_min (the level below which the structure no longer counts
as present) is part of the model, not a detail.

Selection with fixed lifetimes (no exponential-death approximation):
    dN_i/dt = B_i(t) - B_i(t - tau_i),   B_i = sum_j a_ij R_j N_i
    dR_j/dt = S_j - delta_j R_j - R_j sum_i a_ij F_i N_i
A steady state needs sum_j a_ij R_j tau_i = 1 for every surviving type. With one
resource this is R* = 1/(a tau): only the lowest R* survives. With two resources two
types can coexist: a mixed equilibrium in which no present type can gain (Nash).

Bits written (reversed Landauer) when the environment temperature is set by the burn
itself (blackbody emitter, P = c T^4, radiation entropy 4E/3T):
    bits = (4/3) F c^(1/4) P^(-1/4) / ln 2      (k_B = 1)
so, unlike the fixed-T identity bits = F/(T ln 2), slow burners write more bits.
"""

from __future__ import annotations

from math import log
from typing import Callable, Sequence

import numpy as np


def power_law_burn(f: float, f0: float, p0: float, n: float) -> float:
    return p0 * (f / f0) ** n


def lifetime_power_law(f0: float, p0: float, n: float, f_min: float = 0.0) -> float:
    """Closed-form tau for P(F) = P0 (F/F0)^n burned from F0 down to f_min."""

    if not (f0 > 0.0 and p0 > 0.0 and 0.0 <= f_min < f0):
        raise ValueError("need f0 > 0, p0 > 0 and 0 <= f_min < f0")
    if n >= 1.0 and f_min == 0.0:
        raise ValueError("passive burners (n >= 1) never reach F = 0; a threshold f_min > 0 is required")
    if abs(n - 1.0) < 1e-12:
        return f0 / p0 * log(f0 / f_min)
    return f0 / (p0 * (1.0 - n)) * (1.0 - (f_min / f0) ** (1.0 - n))


def lifetime_by_integration(burn: Callable[[float], float], f0: float, f_min: float, dt: float) -> float:
    """Integrate dF/dt = -P(F) with RK4 until F crosses f_min; linear interpolation of the crossing."""

    f, t = f0, 0.0
    while True:
        k1 = -burn(f)
        k2 = -burn(max(f + 0.5 * dt * k1, 1e-300))
        k3 = -burn(max(f + 0.5 * dt * k2, 1e-300))
        k4 = -burn(max(f + dt * k3, 1e-300))
        f_new = f + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        if f_new <= f_min:
            return t + dt * (f - f_min) / (f - f_new)
        f, t = f_new, t + dt


def simulate_fixed_lifetime_competition(
    capture: Sequence[Sequence[float]], stores: Sequence[float], taus: Sequence[float],
    supply: Sequence[float], decay: Sequence[float], n0: Sequence[float], r0: Sequence[float],
    horizon: float, dt: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Delay model: every system lives exactly tau_i. Returns final (N, R).

    capture[i][j] = a_ij. History before t = 0: births constant at N0_i / tau_i
    (uniform ages). Explicit Euler with a birth-history buffer.
    """

    a = np.asarray(capture, dtype=float)
    f = np.asarray(stores, dtype=float)
    tau = np.asarray(taus, dtype=float)
    s, d = np.asarray(supply, dtype=float), np.asarray(decay, dtype=float)
    n, r = np.array(n0, dtype=float), np.array(r0, dtype=float)
    steps = int(round(horizon / dt))
    lag = np.maximum(1, np.rint(tau / dt).astype(int))
    births = np.zeros((steps + 1, len(n)))
    past = n / tau  # birth rate before t = 0
    for k in range(steps):
        b = (a @ r) * n
        births[k] = b
        old = np.array([births[k - lag[i], i] if k >= lag[i] else past[i] for i in range(len(n))])
        dr = s - d * r - r * ((a * f[:, None] * n[:, None]).sum(axis=0))
        n = np.maximum(n + dt * (b - old), 0.0)
        r = np.maximum(r + dt * dr, 0.0)
    return n, r


def coexistence_resources(capture: Sequence[Sequence[float]], taus: Sequence[float]) -> np.ndarray:
    """Resource levels R* at which every listed type exactly replaces itself: a R* = 1/tau."""

    return np.linalg.solve(np.asarray(capture, dtype=float), 1.0 / np.asarray(taus, dtype=float))


def invasion_fitness(capture_row: Sequence[float], tau: float, resources: Sequence[float]) -> float:
    """Lifetime reproductive number minus one of a rare type at fixed resources: a.R tau - 1."""

    return float(np.dot(capture_row, resources) * tau - 1.0)


def bits_fixed_temperature(f: float, temperature: float) -> float:
    return f / (temperature * log(2.0))


def bits_blackbody(f: float, burn_power: float, emission_constant: float) -> float:
    """Entropy (in bits, k_B = 1) radiated when F is emitted as blackbody light at constant power P = c T^4."""

    temperature = (burn_power / emission_constant) ** 0.25
    return 4.0 / 3.0 * f / (temperature * log(2.0))
