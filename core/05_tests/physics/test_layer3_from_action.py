"""Layer 3 rates from the parent action (stage 3, wave L3-1).

Checks through the general scattering integral with an arbitrary occupation f(p):
1. Known limit: a resting thermal pool reproduces the layer 2 Landau-damping closed form.
2. Lorentz covariance: a moving thermal stream gives the rest-frame value at (w', q') (independent route).
3. Isotropic pools only damp: rho >= 0 for random non-thermal isotropic occupations, including inverted bumps.
4. A stream feeds a mode exactly when w < v q (Cherenkov condition); a resting pool never does.
5. Linearity: rho of a stream of strength R is R times rho of the reference stream, so a_i R - 1/tau_i is exact.
6. Layer 3 selection with the derived rates: the mode with the lowest R* takes the pool and R -> R*.
"""

from __future__ import annotations

import importlib
import math
import random
import warnings

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("core.03_lanes.persistence.uet_layer3_from_action")
l2 = m.l2


def _spacelike(rng: random.Random) -> tuple[float, float]:
    q = rng.uniform(0.3, 2.5)
    return q * rng.uniform(0.05, 0.95), q


@pytest.mark.parametrize("seed", range(6))
def test_resting_pool_reproduces_layer2_landau_damping(seed: int) -> None:
    rng = random.Random(600 + seed)
    M, sigma, T = rng.uniform(0.2, 1.0), rng.uniform(0.1, 1.0), rng.uniform(0.2, 2.0)
    w, q = _spacelike(rng)
    got = m.spectral_scattering(w, q, m.thermal_stream(T, 0.0), M, sigma)
    assert got == pytest.approx(l2.rho_landau(w, q, T, M, sigma), rel=1e-8)


@pytest.mark.parametrize("seed", range(8))
def test_moving_stream_is_the_boosted_rest_frame_value(seed: int) -> None:
    rng = random.Random(700 + seed)
    M, sigma, T, v = rng.uniform(0.2, 1.0), rng.uniform(0.1, 1.0), rng.uniform(0.3, 2.0), rng.uniform(0.1, 0.7)
    w, q = _spacelike(rng)
    if abs(w - v * q) < 0.02 * q:
        w = 0.5 * v * q
    direct = m.spectral_scattering(w, q, m.thermal_stream(T, v), M, sigma)
    assert direct == pytest.approx(m.rho_stream_boost(w, q, T, v, M, sigma), rel=1e-7)


@pytest.mark.parametrize("seed", range(10))
def test_isotropic_pools_only_damp(seed: int) -> None:
    rng = random.Random(800 + seed)
    M, sigma = rng.uniform(0.2, 1.0), rng.uniform(0.1, 1.0)
    w, q = _spacelike(rng)
    a = m._lower_energy(w, q, M)
    E0, width, height = a + rng.uniform(0.0, 2.0), rng.uniform(0.2, 1.0), rng.uniform(0.5, 5.0)
    T = rng.uniform(0.1, 1.0)
    occ = m.isotropic(lambda E: height * math.exp(-((E - E0) / width) ** 2) + l2.bose(E, T))  # inverted below E0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rho = m.spectral_scattering(w, q, occ, M, sigma)
    from scipy.integrate import quad
    telescoped, _ = quad(lambda E: height * math.exp(-((E - E0) / width) ** 2) + l2.bose(E, T), a, a + w)
    assert rho > 0.0
    assert rho == pytest.approx(l2.N_BATH * sigma**2 / 2.0 * 2.0 / (8.0 * math.pi * q) * telescoped, rel=1e-6)


@pytest.mark.parametrize("seed", range(10))
def test_stream_feeds_a_mode_exactly_below_the_cherenkov_line(seed: int) -> None:
    rng = random.Random(900 + seed)
    M, sigma, T, v = rng.uniform(0.2, 1.0), rng.uniform(0.1, 1.0), rng.uniform(0.3, 2.0), rng.uniform(0.1, 0.8)
    w, q = _spacelike(rng)
    if abs(w - v * q) < 0.02 * q:
        w = 0.5 * v * q
    rho = m.spectral_scattering(w, q, m.thermal_stream(T, v), M, sigma)
    assert (rho < 0.0) == (w < v * q)
    assert m.spectral_scattering(w, q, m.thermal_stream(T, 0.0), M, sigma) > 0.0


def test_capture_is_linear_in_stream_strength() -> None:
    M, sigma, T, v, w, q = 0.5, 0.7, 0.8, 0.6, 0.3, 1.0
    base = m.spectral_scattering(w, q, m.thermal_stream(T, v, 1.0), M, sigma)
    for R in (0.1, 0.5, 3.0):
        assert m.spectral_scattering(w, q, m.thermal_stream(T, v, R), M, sigma) == pytest.approx(R * base, rel=1e-12)


def test_selection_with_action_rates_keeps_the_lowest_R_star() -> None:
    M, sigma, T, v = 0.5, 0.7, 0.8, 0.6
    modes = [(0.2, 1.0), (0.3, 1.2), (0.25, 0.8), (0.4, 1.5)]
    r = m.layer3_rates(modes, T, T, v, M, sigma)
    assert np.all(r["capture"] > 0.0)
    e_s = m.stream_energy_per_unit(T, v, M)
    quantum = np.array([w for w, _ in modes]) / e_s
    n, R = m.simulate(r["capture"], r["death"], quantum, supply=0.05, decay=0.01,
                      n0=np.full(len(modes), 1e-3), R0=1.0, horizon=4.0e4)
    win = int(np.argmin(r["R_star"]))
    assert R == pytest.approx(r["R_star"][win], rel=1e-3)
    assert n[win] > 0.0
    others = np.delete(n, win)
    assert np.all(others < 1e-6 * n[win])
