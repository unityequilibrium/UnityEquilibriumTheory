"""Wave D19: the price of resisting free fall.

(a) Derivation check: integrating the vertical ascent ODE gives the gravity loss v_e (1 - 1/Rm)/lam0 at 20
    random rockets, rel < 1e-10; the weak-field proper-time functional integrated along the free-fall path
    gives g^2 T^3/(24 c^2) at 20 random throws, rel < 1e-10.
(b) Second route (maximal aging): every path pushed off free fall between the same two events gains less
    proper time, and the loss is quadratic in the push.
(c) Known limit with convergence order: the exact Schwarzschild radial geodesic tends to g^2 T^3/(24 c^2),
    relative deviation of order 2 in the launch speed.
(d) Identities: a rocket with lam0 -> infinity loses nothing; hovering costs g t; hovering jet power m g v_e/2.
"""

from __future__ import annotations

import importlib
from math import log

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_price_of_resisting")


@pytest.mark.parametrize("seed", range(20))
def test_gravity_loss_ode_matches_closed_form(seed: int) -> None:
    rng = np.random.default_rng(29000 + seed)
    v_e, Rm, lam0 = rng.uniform(1500, 4500), rng.uniform(1.5, 20), rng.uniform(1.05, 4)
    v, loss = m.vertical_ascent(v_e, Rm, lam0)
    assert abs(loss / m.gravity_loss_closed(v_e, Rm, lam0) - 1.0) < 1e-10
    assert abs(loss / (v_e * log(Rm)) / m.gravity_loss_fraction(Rm, lam0) - 1.0) < 1e-10


@pytest.mark.parametrize("seed", range(20))
def test_thrown_clock_weak_field(seed: int) -> None:
    rng = np.random.default_rng(29100 + seed)
    T, g = 10 ** rng.uniform(-1, 2), rng.uniform(1, 30)
    assert abs(m.thrown_clock_gain_weak_numeric(T, g) / m.thrown_clock_gain_closed(T, g) - 1.0) < 1e-10


@pytest.mark.parametrize("k", [1, 2, 3, 5])
def test_pushed_paths_age_less_quadratically(k: int) -> None:
    T = 2.0
    free = m.thrown_clock_gain_weak_numeric(T)
    losses = [free - m.perturbed_path_gain(T, eps, k) for eps in (1e-2, 1e-3)]
    assert all(x > 0 for x in losses)
    assert abs(log(losses[0] / losses[1]) / log(10.0) - 2.0) < 1e-6


def test_schwarzschild_limit_order_two() -> None:
    us = [1e-3, 5e-4, 2.5e-4]
    devs = []
    for u in us:
        gain, T, g = m.thrown_clock_gain_schwarzschild(1e-3, 1.0, u)
        devs.append(abs(gain / (g * g * T ** 3 / 24.0) - 1.0))
    orders = [log(devs[i] / devs[i + 1]) / log(us[i] / us[i + 1]) for i in range(2)]
    for o in orders:
        assert abs(o - 2.0) < 0.02


def test_identities_and_illustration() -> None:
    assert m.gravity_loss_closed(3000.0, 8.0, 1e12) < 1e-8
    assert abs(m.hover_speed_cost(60.0) - 60.0 * m.G_EARTH) < 1e-12
    assert abs(m.hover_jet_power(1000.0, 3000.0) / (0.5 * 1000.0 * m.G_EARTH * 3000.0) - 1.0) < 1e-15
    out = m.illustration()
    assert 0.32 < out["gravity_loss_fraction"] < 0.33
    assert 3.5e-16 < out["thrown_clock_gain_2s_s"] < 3.6e-16
