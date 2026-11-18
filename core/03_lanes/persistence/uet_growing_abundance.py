"""Layer 3 with a growing formation rate: abundance law for an exponentially growing population.

The steady abundance law N = b tau (Little's law) assumes a constant formation rate b. In a
population that grows as e^{lambda t}, structures that entered a phase at age a were formed at
rate b(t - a) = b_now e^{-lambda a}, so the number in a phase entered at age a1 and left at a1 + tau is
    N = integral_{a1}^{a1+tau} b_now e^{-lambda a} da = b_now (e^{-lambda a1} - e^{-lambda (a1+tau)}) / lambda,
which tends to b_now tau as lambda -> 0.

Dividing cells with a fixed cycle length T (each division doubles the count, lambda = ln 2 / T):
the age density is f(a) = (2 ln 2 / T) 2^{-a/T} on [0, T], and the fraction of cells in the phase
[a1, a2] is
    phi = 2 (2^{-a1/T} - 2^{-a2/T}).
For the last phase of the cycle (mitosis, duration t_M): phi = 2^{t_M/T} - 1, which differs from
the steady value t_M/T (factor ln 2 at small t_M/T). This is the standard age-distribution
correction for asynchronous exponential growth (cell kinetics); not UET-distinct.
"""

from __future__ import annotations

from math import exp, log

import numpy as np


def abundance_growing(b_now: float, growth_rate: float, entry_age: float, duration: float) -> float:
    if abs(growth_rate) * (entry_age + duration) < 1e-12:
        return b_now * duration
    return b_now * (exp(-growth_rate * entry_age) - exp(-growth_rate * (entry_age + duration))) / growth_rate


def phase_fraction_dividing(a1: float, a2: float, cycle: float) -> float:
    """Fraction of an asynchronous, exponentially growing population with age in [a1, a2] of a fixed cycle."""
    if not 0.0 <= a1 <= a2 <= cycle:
        raise ValueError("need 0 <= a1 <= a2 <= cycle")
    return 2.0 * (2.0 ** (-a1 / cycle) - 2.0 ** (-a2 / cycle))


def mitotic_index(t_mitosis: float, cycle: float) -> float:
    return phase_fraction_dividing(cycle - t_mitosis, cycle, cycle)


def phase_duration_from_fraction_last_phase(fraction: float, cycle: float) -> float:
    """Invert phi = 2^{t/T} - 1 for the last phase: t = T log2(1 + phi)."""
    return cycle * log(1.0 + fraction) / log(2.0)


def simulate_dividing_population(cycle: float, a1: float, a2: float, n_max: int, generations: float,
                                 dt: float, rng: np.random.Generator, cv: float = 0.0) -> float:
    """Agent model: every cell draws its own cycle length (mean T, coefficient of variation cv); ages
    advance; a cell reaching its cycle length becomes two cells of age 0; the population is randomly
    thinned to n_max (unbiased). Phases are measured in each cell's own fractional age, so the
    returned fraction of cells with age/cycle_i in [a1/T, a2/T] can be compared with phi.
    With cv = 0 a fixed cycle never relaxes to the stable age distribution (renewal B(t) = 2 B(t - T)
    keeps any initial pattern); some cycle-time variability is needed for mixing."""

    def draw(n):
        return cycle * np.clip(1.0 + cv * rng.standard_normal(n), 0.2, 3.0)

    cycles = draw(n_max)
    ages = rng.uniform(0.0, 1.0, n_max) * cycles
    steps = int(round(generations * cycle / dt))
    for _ in range(steps):
        ages += dt
        divided = ages >= cycles
        if divided.any():
            k = 2 * int(divided.sum())
            ages = np.concatenate([ages[~divided], np.zeros(k)])
            cycles = np.concatenate([cycles[~divided], draw(k)])
        if ages.size > n_max:
            keep = rng.choice(ages.size, n_max, replace=False)
            ages, cycles = ages[keep], cycles[keep]
    frac_age = ages / cycles
    return float(np.mean((frac_age >= a1 / cycle) & (frac_age < a2 / cycle)))
