"""Layer 3 for unequal division (budding yeast): growth rate and phase abundances from cycle times.

Model (Hartwell and Unger 1977, Fig. 4): every division gives one parent cycle of length P and
one daughter cycle of length D (D > P). Both cycles end with the same budded period B; the
unbudded periods are U_p = P - B and U_d = D - B.

1. Growth rate (Euler-Lotka for two offspring cycle lengths). In exponential growth N ~ 2^{t/T},
   each division at time t was seeded by divisions at t - P and t - D, so
       2^{-P/T} + 2^{-D/T} = 1.
   For P = D this gives T = P (equal division).
2. Abundance with a growing formation rate (C_L3_GROWING_ABUNDANCE): both cycle types are entered
   at the same rate b(t) = b_now e^{-alpha a} (alpha = ln 2 / T), so the number in the first U of a
   cycle is proportional to 1 - e^{-alpha U}. Fraction of unbudded cells that are daughters:
       u_d = (1 - e^{-alpha U_d}) / [(1 - e^{-alpha U_d}) + (1 - e^{-alpha U_p})].
3. Budded fraction: every budded cell yields exactly one new cell when its budded period ends,
   so f_budded = 2^{B/T} - 1, independent of the asymmetry.
"""

from __future__ import annotations

from math import exp, log

import numpy as np
from scipy.optimize import brentq


def doubling_time(parent_cycle: float, daughter_cycle: float) -> float:
    if parent_cycle <= 0.0 or daughter_cycle <= 0.0:
        raise ValueError("cycle times must be positive")
    lo, hi = min(parent_cycle, daughter_cycle), max(parent_cycle, daughter_cycle)
    return brentq(lambda t: 2.0 ** (-parent_cycle / t) + 2.0 ** (-daughter_cycle / t) - 1.0, lo, hi, rtol=1e-13)


def unbudded_daughter_fraction(parent_cycle: float, daughter_cycle: float, budded: float, doubling: float) -> float:
    alpha = log(2.0) / doubling
    u_p, u_d = parent_cycle - budded, daughter_cycle - budded
    if u_p < 0.0 or u_d < 0.0:
        raise ValueError("budded period longer than a cycle")
    nd, np_ = 1.0 - exp(-alpha * u_d), 1.0 - exp(-alpha * u_p)
    return nd / (nd + np_)


def budded_fraction(budded: float, doubling: float) -> float:
    return 2.0 ** (budded / doubling) - 1.0


def simulate(parent_cycle: float, daughter_cycle: float, budded: float, cv: float, n_max: int,
             duration: float, dt: float, rng: np.random.Generator) -> dict:
    """Agent model: each cell has a type (parent or daughter), its own cycle length (mean P or D,
    coefficient of variation cv on the unbudded part) and a fixed budded period. At division a cell
    becomes a parent again and adds one daughter. The population is thinned to n_max (unbiased);
    the log of the true count is tracked to measure the doubling time."""

    def unbudded_len(kind):
        mean = np.where(kind == 1, daughter_cycle - budded, parent_cycle - budded)
        return np.maximum(mean * (1.0 + cv * rng.standard_normal(kind.size)), 0.0)

    kind = rng.integers(0, 2, n_max)  # 1 = daughter cycle, 0 = parent cycle
    total = unbudded_len(kind) + budded
    age = rng.uniform(0.0, 1.0, n_max) * total
    log_count, times, logs = 0.0, [], []
    steps = int(round(duration / dt))
    for i in range(steps):
        age += dt
        done = age >= total
        k = int(done.sum())
        if k:
            n_before = age.size
            kind = np.concatenate([np.where(done, 0, kind), np.ones(k, dtype=kind.dtype)])
            age = np.concatenate([np.where(done, 0.0, age), np.zeros(k)])
            new_total = unbudded_len(kind)
            total = np.concatenate([np.where(done, new_total[:n_before] + budded, total), new_total[n_before:] + budded])
            log_count += log(age.size / n_before)
        if age.size > n_max:
            keep = rng.choice(age.size, n_max, replace=False)
            kind, age, total = kind[keep], age[keep], total[keep]
        if i > steps // 2:
            times.append((i + 1) * dt)
            logs.append(log_count)
    slope = np.polyfit(times, logs, 1)[0]
    unbudded = age < total - budded
    return {"doubling": log(2.0) / slope,
            "unbudded_daughter_fraction": float(np.mean(kind[unbudded] == 1)),
            "budded_fraction": float(np.mean(~unbudded))}
