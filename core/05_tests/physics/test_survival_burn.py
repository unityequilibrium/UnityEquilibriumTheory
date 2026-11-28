"""Wave D20: a burn that follows the store, P = P0 (R/R0)^beta.

(a) Derivation check: the closed form R(t) equals the ODE solution at 20 random (beta, P0, R0), rel < 1e-9.
(b) Known limit with convergence order: as beta -> 1 the closed form tends to D14's exponential with
    deviation of order 1 in (beta - 1); beta = 0 is the straight line R0 - P0 t exactly.
(c) Second route and identities: the time to reach R* from the closed form equals the ODE event time
    (rel < 1e-9); the specific rate falls with time exactly when beta > 1.
(d) Convergence test: the two-window estimator recovers beta with an error that falls with order 2 in the
    window's fractional mass change.
"""

from __future__ import annotations

import importlib
from math import log

import numpy as np
import pytest
from scipy.integrate import solve_ivp

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_survival_burn")


def draw(seed: int):
    rng = np.random.default_rng(30000 + seed)
    return rng.uniform(0.0, 4.0), 10 ** rng.uniform(-1, 1), 10 ** rng.uniform(0, 3)


@pytest.mark.parametrize("seed", range(20))
def test_closed_form_matches_ode(seed: int) -> None:
    beta, P0, R0 = draw(seed)
    t_end = 0.5 * m.time_to_threshold(R0, 0.2 * R0, P0, beta)
    ts, R = m.store_numeric(t_end, R0, P0, beta)
    assert np.max(np.abs(R / m.store(ts, R0, P0, beta) - 1.0)) < 1e-9  # closed form loses digits as beta -> 1


def test_beta_one_limit_order_one() -> None:
    R0, P0, t = 10.0, 1.0, 3.0
    exact = R0 * np.exp(-P0 * t / R0)
    eps = [1e-2, 1e-3, 1e-4]
    devs = [abs(float(m.store(t, R0, P0, 1.0 + e)) / exact - 1.0) for e in eps]
    orders = [log(devs[i] / devs[i + 1]) / log(eps[i] / eps[i + 1]) for i in range(2)]
    for o in orders:
        assert abs(o - 1.0) < 0.01
    ts = np.linspace(0, 5, 11)
    assert np.allclose(m.store(ts, R0, P0, 0.0), R0 - P0 * ts, rtol=0, atol=1e-12)


@pytest.mark.parametrize("seed", range(10))
def test_time_to_threshold_second_route(seed: int) -> None:
    beta, P0, R0 = draw(seed)
    R_star = R0 * np.random.default_rng(30100 + seed).uniform(0.05, 0.9)

    def hit(t, y):
        return y[0] - R_star
    hit.terminal = True
    sol = solve_ivp(lambda t, y: [-m.burn(max(y[0], 0.0), P0, R0, beta)], (0.0, 1e9), [R0], events=hit,
                    method="DOP853", rtol=1e-12, atol=1e-14 * R0)
    assert abs(sol.t_events[0][0] / m.time_to_threshold(R0, R_star, P0, beta) - 1.0) < 1e-9


@pytest.mark.parametrize("beta", [0.0, 0.5, 0.99, 1.01, 2.0, 3.5])
def test_specific_rate_falls_iff_beta_above_one(beta: float) -> None:
    R0, P0 = 50.0, 1.0
    ts = np.linspace(0, 0.6 * m.time_to_threshold(R0, 0.3 * R0, P0, beta), 50)
    k = m.specific_rate(m.store(ts, R0, P0, beta), P0, R0, beta)
    d = np.diff(k)
    assert (np.all(d < 0) if beta > 1 else np.all(d > 0))


def test_two_window_estimator_converges_order_two() -> None:
    beta, R0, P0 = 2.0, 50.0, 1.0
    errs, fr = [], []
    for T in (8.0, 4.0, 2.0):
        t = np.linspace(0.0, T, 41)
        R = m.store(t, R0, P0, beta)
        est = m.beta_from_two_windows(list(zip(t, R)))
        errs.append(abs(est["beta"] - beta))
        fr.append(1.0 - R[-1] / R0)
    orders = [log(errs[i] / errs[i + 1]) / log(fr[i] / fr[i + 1]) for i in range(2)]
    for o in orders:
        assert abs(o - 2.0) < 0.15
