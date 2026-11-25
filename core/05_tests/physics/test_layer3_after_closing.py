"""Wave D15: the full layer-3 equation (pool + structures) after the supply stops.

(a) Derivation check: the stock identity dM/dt = -(delta R + F n/tau) from the layer-3 right-hand side at
    20 random states, rel < 1e-12, and along integrated trajectories by finite differences.
(b) Second route: long integration with the supply on reaches R* = 1/(a tau) (independent of S) and
    n* = (S - delta R*)/(a F R*) at 20 random systems, rel < 1e-8; few structures grow at a S/delta - 1/tau.
(c) Known limits with convergence order: with no structures (S -> S* = delta R*) the specific loss rate is
    D14's constant delta, deviation of order 1 in (S - S*)/S* over a fixed window; the limit is not uniform
    in time, since any structures left take over in the end; at delta = 1/tau the rate is constant.
(d) Identity and ordering: after closing k -> min(delta, 1/tau) < k(0); k falls monotonically when
    delta > 1/tau and first rises when delta < 1/tau.
"""

from __future__ import annotations

import importlib
from math import log

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_layer3_after_closing")


def draw(seed: int, fast_pool: bool | None = None):
    rng = np.random.default_rng(25000 + seed)
    a, tau, F = 10 ** rng.uniform(-1, 1, size=3)
    if fast_pool is None:
        fast_pool = bool(seed % 2)
    x = rng.uniform(1.25, 10.0) if fast_pool else rng.uniform(0.1, 0.8)
    delta = x / tau
    S = delta * m.threshold_pool(a, tau) * 10 ** rng.uniform(0.1, 1.0)
    return a, tau, F, delta, S


@pytest.mark.parametrize("seed", range(20))
def test_stock_identity(seed: int) -> None:
    a, tau, F, delta, S = draw(seed)
    rng = np.random.default_rng(25100 + seed)
    R, n = 10 ** rng.uniform(-2, 2, size=2)
    dR, dn = m.rhs(0.0, [R, n], a, tau, F, delta, 0.0)
    assert abs((dR + F * dn) / -m.stock_loss_rate(R, n, F, tau, delta) - 1.0) < 1e-12
    t, Rt, nt, _ = m.after_closing(a, tau, F, delta, S, 2.0 * tau, n_t=4001)
    M = m.stock(Rt, nt, F)
    dM = np.gradient(M, t, edge_order=2)[1:-1]
    assert np.max(np.abs(dM / -m.stock_loss_rate(Rt, nt, F, tau, delta)[1:-1] - 1.0)) < 1e-4


@pytest.mark.parametrize("seed", range(20))
def test_supplied_system_settles_on_threshold(seed: int) -> None:
    a, tau, F, delta, S = draw(seed)
    Rs, ns = m.steady_state(a, tau, F, delta, S)
    assert abs(Rs * a * tau - 1.0) < 1e-14
    lam = m.growth_rate(a, tau, delta, S)
    assert lam > 0
    t, R, n = m.while_supplied(a, tau, F, delta, S, 1e-6 * ns, 400.0 / min(lam, delta, 1 / tau), n_t=3)
    assert abs(R[-1] / Rs - 1.0) < 1e-8
    assert abs(n[-1] / ns - 1.0) < 1e-8


@pytest.mark.parametrize("seed", range(10))
def test_few_structures_grow_by_compounding(seed: int) -> None:
    a, tau, F, delta, S = draw(seed)
    lam = m.growth_rate(a, tau, delta, S)
    n0 = 1e-12
    t, R, n = m.while_supplied(a, tau, F, delta, S, n0, 1.0 / lam, n_t=3)
    assert abs(log(n[-1] / n0) / (t[-1] * lam) - 1.0) < 1e-6


@pytest.mark.parametrize("seed", range(20))
def test_loss_slows_to_the_slower_part(seed: int) -> None:
    a, tau, F, delta, S = draw(seed)
    gap = abs(delta - 1.0 / tau)
    t, R, n, k = m.after_closing(a, tau, F, delta, S, 40.0 / gap + 40.0 * tau)
    assert abs(k[0] / m.initial_specific_rate(a, tau, F, delta, S) - 1.0) < 1e-12
    assert abs(k[-1] / m.late_specific_rate(tau, delta) - 1.0) < 1e-6
    assert k[-1] < k[0]
    if delta > 1.0 / tau:
        assert np.all(np.diff(k) <= 1e-12 * k[0])
    else:
        assert k.max() > k[0] * (1 + 1e-6)


def test_one_part_limit_recovers_d14_order_one() -> None:
    a, tau, F, delta = 1.0, 1.0, 2.0, 3.0
    S_star = delta * m.threshold_pool(a, tau)
    xs = [1e-4, 1e-5, 1e-6]
    devs = []
    for x in xs:  # fixed window: the limit is not uniform in time (see the last check)
        _, _, _, k = m.after_closing(a, tau, F, delta, S_star * (1 + x), 1.0 * tau)
        devs.append(np.max(np.abs(k / delta - 1.0)))
    orders = [log(devs[i] / devs[i + 1]) / log(xs[i] / xs[i + 1]) for i in range(2)]
    for o in orders:
        assert abs(o - 1.0) < 0.01
    _, _, _, k = m.after_closing(a, tau, F, delta, 0.5 * S_star, 5.0)
    assert np.max(np.abs(k / delta - 1.0)) < 1e-12
    # however few structures there are, the slower part takes over in the end: k -> 1/tau, not delta
    _, _, _, k = m.after_closing(a, tau, F, delta, S_star * (1 + 1e-5), 60.0 * tau)
    assert abs(k[-1] * tau - 1.0) < 1e-6


def test_equal_rates_give_constant_specific_loss() -> None:
    a, tau, F = 0.7, 2.0, 1.5
    delta = 1.0 / tau
    _, _, _, k = m.after_closing(a, tau, F, delta, 5.0 * delta * m.threshold_pool(a, tau), 30.0)
    assert np.max(np.abs(k * tau - 1.0)) < 1e-12


def test_illustration() -> None:
    out = m.illustration()
    assert out["k_end_tau"] < out["k0_tau"]
    assert out["r_late_over_early"] < 1.0
