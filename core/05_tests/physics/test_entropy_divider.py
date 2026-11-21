"""Wave D1: the divider temperature sets the usable resource and the ability to persist.

(a) Derivation check: the general exergy integral equals the constant-C closed form at 24 random
    (C, T0, T_c), rel < 1e-10.
(b) Known limits through the general path: T_c -> T0 (alone) gives C (T0 - T_c)^2 / (2 T0) -> 0
    with a second-order approach; T_c -> 0 gives all the stored heat as work.
(c) Conservation and second law: heat drawn = work + heat to the divider, and the divider gains
    exactly the entropy the store loses (reversible extraction), for a temperature-dependent C(T).
(d) Second route: direct numerical maximisation of the endoreversible power over the inner
    efficiency equals K (sqrt(T_h) - sqrt(T_c))^2 at efficiency 1 - sqrt(T_c/T_h).
(e) Threshold: just below T_c* a steady operating point with power W_m exists, just above none
    does; a warmer divider always shortens the lifetime of a store.
"""

from __future__ import annotations

import importlib
from math import log, sqrt

import numpy as np
import pytest
from scipy.optimize import brentq

pytestmark = pytest.mark.physics

dv = importlib.import_module("docs.core.03_lanes.persistence.uet_entropy_divider")


@pytest.mark.parametrize("seed", range(24))
def test_general_exergy_matches_closed_form(seed: int) -> None:
    rng = np.random.default_rng(2000 + seed)
    C = 10 ** rng.uniform(-2, 3)
    T0 = 10 ** rng.uniform(0, 4)
    T_c = T0 * rng.uniform(0.001, 0.999)
    general = dv.exergy(lambda T: C, T0, T_c)
    exact = dv.exergy_constant_c(C, T0, T_c)
    assert abs(general / exact - 1.0) < 1e-10


def test_alone_limit_second_order_through_general_path() -> None:
    C, T0 = 3.0, 500.0
    errors = []
    for dT in [10.0, 5.0, 2.5, 1.25]:
        T_c = T0 - dT
        ex = dv.exergy(lambda T: C, T0, T_c)
        leading = C * dT ** 2 / (2.0 * T0)
        errors.append(abs(ex / leading - 1.0))
        assert ex > 0.0
    # relative error of the leading term shrinks linearly with dT (next term is O(dT^3))
    ratios = [errors[i] / errors[i + 1] for i in range(len(errors) - 1)]
    assert all(abs(r - 2.0) < 0.05 for r in ratios)


def test_cold_divider_limit_through_general_path() -> None:
    C, T0 = 2.0, 300.0
    for T_c in [1e-3, 1e-5, 1e-7]:
        ex = dv.exergy(lambda T: C, T0, T_c)
        # Ex = C T0 - C T_c (1 + ln(T0/T_c)) -> C T0
        assert abs(ex / (C * T0) - 1.0) < 2.0 * T_c / T0 * (1.0 + log(T0 / T_c))


@pytest.mark.parametrize("seed", range(6))
def test_energy_and_entropy_balance_with_varying_heat_capacity(seed: int) -> None:
    rng = np.random.default_rng(seed)
    a, b = rng.uniform(0.1, 2.0, 2)

    def C(T: float) -> float:
        return a + b * (T / 100.0) ** 3  # Debye-like rise plus a constant part

    T0 = rng.uniform(150.0, 900.0)
    T_c = T0 * rng.uniform(0.01, 0.9)
    bal = dv.entropy_balance(C, T0, T_c)
    assert abs((bal["work"] + bal["heat_to_divider"]) / bal["heat_drawn"] - 1.0) < 1e-12
    assert abs(bal["divider_entropy_gain"] / bal["store_entropy_loss"] - 1.0) < 1e-10
    assert 0.0 < bal["work"] < bal["heat_drawn"] * (1.0 - T_c / T0)  # below the Carnot bound at T0


@pytest.mark.parametrize("seed", range(10))
def test_max_power_numeric_equals_closed_form(seed: int) -> None:
    rng = np.random.default_rng(3000 + seed)
    T_h = 10 ** rng.uniform(2, 4)
    T_c = T_h * rng.uniform(0.001, 0.9)
    K_h, K_c = 10 ** rng.uniform(-1, 2, 2)
    p_num, eta_num = dv.max_power_numeric(T_h, T_c, K_h, K_c)
    p_exact = dv.max_power_closed_form(T_h, T_c, K_h, K_c)
    assert abs(p_num / p_exact - 1.0) < 1e-10
    assert abs(eta_num - (1.0 - sqrt(T_c / T_h))) < 1e-6  # flat maximum: eta is less sharp than P


def test_divider_threshold_and_monotone_lifetime() -> None:
    T_h, K_h, K_c, W_m = 5000.0, 2.0, 3.0, 1000.0
    T_star = dv.divider_threshold(T_h, W_m, K_h, K_c)
    assert T_star is not None and 0.0 < T_star < T_h
    carnot = lambda Tc: 1.0 - Tc / T_h  # noqa: E731

    def has_operating_point(T_c: float) -> bool:
        p_max, eta_star = dv.max_power_numeric(T_h, T_c, K_h, K_c)
        if p_max < W_m:
            return False
        eta = brentq(lambda e: dv.endoreversible_power(e, T_h, T_c, K_h, K_c) - W_m, 1e-15, eta_star)
        return abs(dv.endoreversible_power(eta, T_h, T_c, K_h, K_c) / W_m - 1.0) < 1e-10

    assert has_operating_point(T_star * (1.0 - 1e-6))
    assert not has_operating_point(T_star * (1.0 + 1e-6))
    assert carnot(T_star) > 0.0
    # too large a need: no divider is cold enough
    assert dv.divider_threshold(T_h, 1.01 * dv.effective_conductance(K_h, K_c) * T_h, K_h, K_c) is None

    # lifetime of a store falls monotonically as the divider warms, and vanishes when alone
    taus = [dv.lifetime(lambda T: 1.0, 300.0, T_c, 1.0) for T_c in [3.0, 30.0, 100.0, 200.0, 299.0]]
    assert all(x > y for x, y in zip(taus, taus[1:]))
    assert taus[-1] < 1e-2 * taus[0]
