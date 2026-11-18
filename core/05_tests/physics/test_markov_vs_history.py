"""Wave O3: when does a history of records beat treating the newest record as the present?

(a) Convergence (noise-free, records spaced by the age, delta = a): the Markov error falls as a (ratio 2 per
    halving), the history error as a^2 (ratio 4).
(b) Known limit: for uniform motion the history estimator is exact; the Markov bias is rate x age.
(c) Moments: Monte Carlo reproduces the exact variance sigma^2 [(1 + r)^2 + r^2] and the exact MSE.
(d) Crossover: below sigma* the history estimator has the lower MSE, above it the Markov estimator, in the
    simulation as in the formula.
"""

from __future__ import annotations

import importlib
import math

import numpy as np
import pytest

pytestmark = pytest.mark.physics

est = importlib.import_module("docs.core.03_lanes.observation.uet_estimators")


def source(t: float) -> float:
    return 1.0 * math.sin(1.3 * t) + 0.2 * t


T_E = 0.7


def test_error_orders_one_for_markov_two_for_history() -> None:
    ages = [0.4, 0.2, 0.1, 0.05]
    markov = [abs(est.bias_markov(source, T_E, a)) for a in ages]
    history = [abs(est.bias_history(source, T_E, a, a)) for a in ages]
    m_ratios = [markov[i] / markov[i + 1] for i in range(3)]
    h_ratios = [history[i] / history[i + 1] for i in range(3)]
    # ratios between successive halvings of the age tend to 2 (first order) and 4 (second order) as a -> 0
    assert m_ratios[0] < m_ratios[1] < m_ratios[2] < 2.0 and abs(m_ratios[2] - 2.0) < 0.1, m_ratios
    assert abs(h_ratios[2] - 4.0) < 0.3 and abs(h_ratios[2] - 4.0) <= abs(h_ratios[0] - 4.0), h_ratios
    assert history[-1] < markov[-1] / 10.0


def test_history_is_exact_for_uniform_motion_and_markov_costs_rate_times_age() -> None:
    uniform = lambda t: 2.0 + 0.8 * t  # noqa: E731
    for age, delta in ((0.3, 0.3), (2.0, 0.1), (0.05, 1.0)):
        assert est.bias_history(uniform, 1.0, age, delta) == pytest.approx(0.0, abs=1e-12)
        assert est.bias_markov(uniform, 1.0, age) == pytest.approx(0.8 * age, rel=1e-12)


@pytest.mark.parametrize("age,delta,sigma", [(0.3, 0.3, 0.05), (0.2, 0.4, 0.1), (0.5, 0.25, 0.02)])
def test_monte_carlo_matches_exact_variance_and_mse(age: float, delta: float, sigma: float) -> None:
    rng = np.random.default_rng(1234)
    e_m, e_h = est.simulate_errors(source, T_E, age, delta, sigma, 400_000, rng)
    assert abs(np.var(e_m) / sigma**2 - 1.0) < 0.02
    assert abs(np.var(e_h) / (sigma**2 * est.noise_gain_history(age, delta)) - 1.0) < 0.02
    assert abs(np.mean(e_m**2) / est.mse_markov(source, T_E, age, sigma) - 1.0) < 0.02
    assert abs(np.mean(e_h**2) / est.mse_history(source, T_E, age, delta, sigma) - 1.0) < 0.02


def test_history_wins_below_the_crossover_noise_and_loses_above_it() -> None:
    age = delta = 0.3
    sigma_star = est.crossover_sigma(source, T_E, age, delta)
    assert sigma_star > 0.0
    assert est.mse_history(source, T_E, age, delta, sigma_star) == pytest.approx(
        est.mse_markov(source, T_E, age, sigma_star), rel=1e-10)
    rng = np.random.default_rng(99)
    for factor, history_wins in ((0.5, True), (2.0, False)):
        e_m, e_h = est.simulate_errors(source, T_E, age, delta, factor * sigma_star, 400_000, rng)
        assert bool(np.mean(e_h**2) < np.mean(e_m**2)) == history_wins, factor
