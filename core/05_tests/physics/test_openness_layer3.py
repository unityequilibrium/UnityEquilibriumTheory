"""Wave D14: the openness ceiling of D13 composes with the layer-3 pool equation of L3-2.

(a) Derivation check: integrating dR/dt = S - delta R after closing (S = 0) and after opening (S from
    D13's P_max) gives the closed-form survival and appearance times at 20 random systems, rel < 1e-9.
(b) Identity: the pool threshold built from L3-2's persistence_threshold equals D13's openness
    threshold with T_c sigma_d = e delta R*_min / eta, at random parameters, rel < 1e-12.
(c) Known limit with convergence order: the appearance time diverges as K -> K*_i like
    ln(1/(K - K*_i)); delta * t_appear + ln((K - K*)/K*) -> 0 with order 1 in (K - K*)/K*.
"""

from __future__ import annotations

import importlib
from math import log

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_openness_layer3")


def draw(seed: int):
    rng = np.random.default_rng(24000 + seed)
    T_c = 10 ** rng.uniform(1, 3)
    T_h = T_c * 10 ** rng.uniform(0.1, 1.5)
    eta, e, delta = rng.uniform(0.05, 0.9), 10 ** rng.uniform(-3, 1), 10 ** rng.uniform(-3, 0)
    r_star = 10 ** rng.uniform(-2, 1, size=3)
    return T_h, T_c, eta, e, delta, r_star


@pytest.mark.parametrize("seed", range(20))
def test_lifetimes_from_ode_match_closed_forms(seed: int) -> None:
    T_h, T_c, eta, e, delta, r_star = draw(seed)
    K_star = m.pool_threshold_openness(T_h, T_c, eta, e, delta, r_star)
    K = K_star * 10 ** np.random.default_rng(24100 + seed).uniform(0.3, 2)
    R_ss = m.steady_pool(K, T_h, T_c, eta, e, delta)
    ri = r_star.min()
    t_surv = m.pool_ode(lambda t: 0.0, delta, R_ss, 100.0 / delta, ri)
    assert abs(t_surv / m.survival_after_closing(R_ss, ri, delta) - 1.0) < 1e-9
    S = m.supply(K, T_h, T_c, eta, e)
    t_app = m.pool_ode(lambda t: S, delta, 0.0, 100.0 / delta, ri)
    assert abs(t_app / m.appearance_after_opening(R_ss, ri, delta) - 1.0) < 1e-9


@pytest.mark.parametrize("seed", range(10))
def test_pool_threshold_equals_d13_threshold(seed: int) -> None:
    T_h, T_c, eta, e, delta, r_star = draw(seed)
    K_pool = m.pool_threshold_openness(T_h, T_c, eta, e, delta, r_star)
    sigma = m.equivalent_decay_entropy(T_c, eta, e, delta, r_star.min())
    K_d13 = m.oo.openness_threshold(T_h, T_c, sigma)
    assert abs(K_pool / K_d13 - 1.0) < 1e-12
    # at that openness the steady pool sits exactly on the cheapest structure's threshold
    assert abs(m.steady_pool(K_pool, T_h, T_c, eta, e, delta) / r_star.min() - 1.0) < 1e-12


def test_appearance_time_diverges_logarithmically_at_threshold() -> None:
    T_h, T_c, eta, e, delta, r_star = 600.0, 300.0, 0.3, 1.0, 0.1, np.array([2.0, 5.0])
    K_star = m.pool_threshold_openness(T_h, T_c, eta, e, delta, r_star)
    xs = [1e-2, 1e-3, 1e-4]
    devs = []
    for x in xs:
        R_ss = m.steady_pool(K_star * (1 + x), T_h, T_c, eta, e, delta)
        t = m.appearance_after_opening(R_ss, r_star.min(), delta)
        devs.append(abs(delta * t + log(x)))
    orders = [log(devs[i] / devs[i + 1]) / log(xs[i] / xs[i + 1]) for i in range(2)]
    for o in orders:
        assert abs(o - 1.0) < 0.01


def test_closed_system_keeps_nothing() -> None:
    assert m.steady_pool(0.0, 600.0, 300.0, 0.3, 1.0, 0.1) == 0.0
    assert m.appearance_after_opening(0.0 + 1e-300, 1.0, 0.1) == float("inf")
