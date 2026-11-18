"""Layer 3 pool loss delta from the action and the supply threshold S* (stage 3, wave L3-2).

1. The contact coupling is read from the action: lam = lambda/Z^2 from matter_potential and the kinetic factor.
2. The O(2) amplitude table summed over sink components gives sigma_tot = 3 lam^2/(2 pi s).
3. Known limit through the general path: the relativistic Monte Carlo rate <sigma v_Moller> approaches the
   non-relativistic closed form with an error of order T/M at zero drift (and order v^2 with drift).
4. The Bose sink density approaches the relativistic Boltzmann form M^2 T K2(M/T)/(2 pi^2) for M >> T.
5. Threshold: with the action-derived a_i, tau_i (wave L3-1) and delta, a supply just above S* = delta R*_min keeps
   the lowest-R* mode alive with R = R* and n = (S - delta R*)/(a F R*); just below S*, and at S = 0, every mode dies.
"""

from __future__ import annotations

import importlib
import math
import random

import numpy as np
import pytest
from scipy.special import kve

pytestmark = pytest.mark.physics

sup = importlib.import_module("core.03_lanes.persistence.uet_layer3_supply")
l3 = importlib.import_module("core.03_lanes.persistence.uet_layer3_from_action")
cov = sup.cov


@pytest.mark.parametrize("seed", range(5))
def test_contact_coupling_is_read_from_the_action(seed: int) -> None:
    rng = random.Random(1000 + seed)
    Z, m2, lam = rng.uniform(0.3, 3.0), rng.uniform(0.1, 3.0), rng.uniform(0.05, 2.0)
    mc = cov.CovariantMatterConfig(matter_kinetic=Z, matter_mass_sq=m2, matter_quartic=lam, response_coupling=0.3)
    assert sup.canonical_quartic(mc) == pytest.approx(lam / Z**2, rel=1e-10)


def test_amplitude_table_gives_the_total_cross_section() -> None:
    lam, s = 0.37, 7.3
    m2 = sup.squared_amplitudes(lam)
    assert (m2["aa->aa"], m2["aa->bb"], m2["ab->ab"]) == pytest.approx((36 * lam**2, 4 * lam**2, 4 * lam**2))
    assert sup.sigma_total(s, lam) == pytest.approx(3 * lam**2 / (2 * math.pi * s), rel=1e-12)


@pytest.mark.parametrize("M", [5.0, 50.0, 500.0])
def test_relativistic_rate_approaches_the_closed_form_as_T_over_M(M: float) -> None:
    T, lam = 0.05, 0.3
    mc, se = sup.rate_coefficient_mc(T, T, 0.0, M, lam, n=400_000, seed=1)
    rel = (mc - sup.rate_coefficient(T, T, 0.0, M, lam)) / mc
    assert abs(rel) < 8.0 * T / M + 4.0 * se / mc  # first relativistic correction is about -7 T/M


def test_drifting_stream_rate_matches_the_closed_form() -> None:
    T, M, lam, v = 0.05, 500.0, 0.3, 0.08
    mc, se = sup.rate_coefficient_mc(T, T, v, M, lam, n=400_000, seed=2)
    assert mc == pytest.approx(sup.rate_coefficient(T, T, v, M, lam), rel=v * v + 4.0 * se / mc)


@pytest.mark.parametrize("ratio", [30.0, 100.0])
def test_sink_density_is_relativistic_boltzmann_for_heavy_chi(ratio: float) -> None:
    M = 1.0
    T = M / ratio
    boltz = M * M * T * kve(2, M / T) * math.exp(-M / T) / (2 * math.pi**2)
    assert sup.sink_density(T, M) == pytest.approx(boltz, rel=1e-6)


def _pool_run(S: float, delta: float, r: dict, quantum: np.ndarray, horizon: float):
    return l3.simulate(r["capture"], r["death"], quantum, supply=S, decay=delta,
                       n0=np.full(len(quantum), 1e-3), R0=1.0, horizon=horizon)


def test_supply_threshold_from_action_rates() -> None:
    M, sigma, T, v, lam = 0.5, 0.7, 0.8, 0.6, 0.3
    modes = [(0.2, 1.0), (0.3, 1.2), (0.25, 0.8), (0.4, 1.5)]
    r = l3.layer3_rates(modes, T, T, v, M, sigma)
    coeff, _ = sup.rate_coefficient_mc(T, T, v, M, lam, n=100_000, seed=3)
    delta = sup.sink_density(T, M) * coeff
    s_star = sup.persistence_threshold(delta, r["R_star"])
    quantum = np.array([w for w, _ in modes]) / l3.stream_energy_per_unit(T, v, M)
    win = int(np.argmin(r["R_star"]))
    horizon = 40.0 / delta
    n, R = _pool_run(1.05 * s_star, delta, r, quantum, horizon)
    expected = (1.05 * s_star - delta * r["R_star"][win]) / (r["capture"][win] * quantum[win] * r["R_star"][win])
    assert R == pytest.approx(r["R_star"][win], rel=1e-3)
    assert n[win] == pytest.approx(expected, rel=1e-3) and np.all(np.delete(n, win) < 1e-6 * n[win])
    n, R = _pool_run(0.95 * s_star, delta, r, quantum, horizon)
    assert R == pytest.approx(0.95 * r["R_star"][win], rel=1e-3) and np.all(n < 1e-8)
    n, R = _pool_run(0.0, delta, r, quantum, horizon)
    assert R < 1e-6 and np.all(n < 1e-8)
