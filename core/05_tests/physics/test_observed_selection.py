"""Wave S1: a flux-limited sample selects by brightness, against persistence.

(a) Derivation check: the numerically integrated surveyed volume equals the D-ball closed form at
    24 random (L, flux limit, D), rel < 1e-10.
(b) Known limits through the general path: equal luminosities give observed ratios equal to the
    space ratios; a survey deeper than the distribution (volume-limited) counts n V_ball.
(c) Exponent: d ln N / d ln P = D/2 - 1 from the numerical volume route for D = 1, 2, 3.
(d) Second route (Monte Carlo, seeded): in D = 3 a type burning 100 times faster is 100 times
    rarer in space but 10 times more common in the sample, within Poisson errors; in D = 2 the two
    are seen equally often; 1/V_max weighting recovers the true space densities.
"""

from __future__ import annotations

import importlib
from math import log, sqrt

import numpy as np
import pytest

pytestmark = pytest.mark.physics

os_ = importlib.import_module("docs.core.03_lanes.persistence.uet_observed_selection")


@pytest.mark.parametrize("seed", range(24))
def test_numeric_volume_matches_closed_form(seed: int) -> None:
    rng = np.random.default_rng(15000 + seed)
    D = 1 + seed % 3
    L = 10 ** rng.uniform(-2, 4)
    f = 10 ** rng.uniform(-6, -1)
    numeric = os_.surveyed_volume_numeric(L, f, D, r_max=1e12)
    exact = os_.surveyed_volume(L, f, D)
    assert abs(numeric / exact - 1.0) < 1e-10


def test_equal_luminosity_and_volume_limited_limits() -> None:
    f, D = 1e-4, 3
    # two types with the same luminosity (P eps equal): observed ratio = space ratio
    n1, n2 = os_.space_density(1.0, 2.0, 1.0), os_.space_density(3.0, 1.0, 1.0)
    N1 = os_.observed_count(1.0, 2.0, 1.0, 1.0, f, D)
    N2 = os_.observed_count(3.0, 1.0, 1.0, 1.0, f, D)
    assert abs((N1 / N2) / (n1 / n2) - 1.0) < 1e-12
    # survey deeper than the whole distribution: every source is seen
    R = 5.0
    V = os_.surveyed_volume_numeric(1e6, f, D, r_max=R)
    assert abs(V / (os_.unit_ball_volume(D) * R ** D) - 1.0) < 1e-12


@pytest.mark.parametrize("D", [1, 2, 3])
def test_observed_count_scales_as_P_to_D_over_2_minus_1(D: int) -> None:
    f, b, F, eps = 1e-3, 1.0, 1.0, 0.5
    Ps = [1.0, 10.0, 100.0]
    counts = [os_.space_density(b, F, P) * os_.surveyed_volume_numeric(eps * P, f, D, r_max=1e12) for P in Ps]
    slopes = [log(counts[i + 1] / counts[i]) / log(Ps[i + 1] / Ps[i]) for i in range(2)]
    for s in slopes:
        assert abs(s - os_.observed_exponent_of_P(D)) < 1e-10


def _two_types():
    # equal birth rate, store and light fraction; the bright type burns 100 times faster
    return [{"b": 1.0, "F": 1.0, "P": 1.0, "eps": 1.0}, {"b": 1.0, "F": 1.0, "P": 100.0, "eps": 1.0}]


def _flux_for_distance(L: float, d: float) -> float:
    return L / (4.0 * np.pi * d * d)


def test_monte_carlo_three_dimensions_reverses_persistence() -> None:
    rng = np.random.default_rng(2026)
    types = _two_types()
    f = _flux_for_distance(1.0, 7.8)          # the slow burner is seen to 7.8, the fast one to 78
    seen, vmax = os_.simulate_survey(types, f, 3, R=100.0, rng=rng)
    expected = np.array([os_.observed_count(t["b"], t["F"], t["P"], t["eps"], f, 3) for t in types])
    for k in range(2):
        assert abs(seen[k] - expected[k]) < 5.0 * sqrt(expected[k])
    # space: slow burner 100 times more common; sample: fast burner about 10 times more common
    assert abs(expected[1] / expected[0] - 10.0) < 1e-9
    assert seen[1] > 5 * seen[0]
    # 1/V_max recovers the space densities (relative Poisson error 1/sqrt(N))
    true = np.array([os_.space_density(t["b"], t["F"], t["P"]) for t in types])
    for k in range(2):
        assert abs(vmax[k] / true[k] - 1.0) < 5.0 / sqrt(seen[k])


def test_monte_carlo_two_dimensions_cancels() -> None:
    rng = np.random.default_rng(7)
    types = _two_types()
    f = _flux_for_distance(1.0, 30.0)
    seen, _ = os_.simulate_survey(types, f, 2, R=400.0, rng=rng)
    expected = np.array([os_.observed_count(t["b"], t["F"], t["P"], t["eps"], f, 2) for t in types])
    assert abs(expected[1] / expected[0] - 1.0) < 1e-12
    for k in range(2):
        assert abs(seen[k] - expected[k]) < 5.0 * sqrt(expected[k])
