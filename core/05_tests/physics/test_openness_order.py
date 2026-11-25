"""Wave D13: openness sets the ceiling on order; the system's own engine makes it.

(a) Derivation check: maximising the work rate over the core temperature numerically gives
    K (sqrt T_h - sqrt T_c)^2 at 20 random (T_h, T_c, g_h, g_c), rel < 1e-10, at the efficiency
    1 - sqrt(T_c/T_h).
(b) Known limits with convergence order: one side perfectly coupled (g_c -> inf) gives K -> g_h with
    deviation of order 1/g_c; near equal temperatures P_max -> K dT^2/(4 T) with relative deviation
    of order dT.
(c) Second law and identities: at every core temperature the entropy made with the engine is >= 0 and
    is largest for pure conduction; the openness threshold K* makes P_max equal T_c sigma_d exactly.
"""

from __future__ import annotations

import importlib
from math import log, sqrt

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_openness_order")


def draw(seed: int):
    rng = np.random.default_rng(23000 + seed)
    T_c = 10 ** rng.uniform(1, 3)
    T_h = T_c * 10 ** rng.uniform(0.05, 1.5)
    g_h, g_c = 10 ** rng.uniform(-2, 2, size=2)
    return T_h, T_c, g_h, g_c


@pytest.mark.parametrize("seed", range(20))
def test_numeric_maximum_matches_closed_form(seed: int) -> None:
    T_h, T_c, g_h, g_c = draw(seed)
    assert abs(m.max_power_numeric(T_h, T_c, g_h, g_c) / m.max_power_closed_form(T_h, T_c, g_h, g_c) - 1.0) < 1e-10
    T1 = (g_h * T_h + g_c * sqrt(T_h * T_c)) / (g_h + g_c)
    P, _ = m.power_at(T1, T_h, T_c, g_h, g_c)
    Q_h = g_h * (T_h - T1)
    assert abs(P / Q_h / m.efficiency_at_max_power(T_h, T_c) - 1.0) < 1e-10


def test_perfect_cold_coupling_limit_order_one() -> None:
    g_h = 2.0
    gcs = [1e4, 1e6, 1e8]
    devs = [1.0 - m.openness(g_h, gc) / g_h for gc in gcs]
    orders = [log(devs[i] / devs[i + 1]) / log(gcs[i + 1] / gcs[i]) for i in range(2)]
    for o in orders:
        assert abs(o - 1.0) < 0.01


def test_small_temperature_difference_limit_order_one() -> None:
    T, g_h, g_c = 300.0, 1.5, 0.7
    K = m.openness(g_h, g_c)
    dTs = [10.0, 1.0, 0.1]
    devs = []
    for dT in dTs:
        P = m.max_power_numeric(T + dT, T, g_h, g_c)
        devs.append(abs(P / (K * dT ** 2 / (4 * T)) - 1.0))
    orders = [log(devs[i] / devs[i + 1]) / log(dTs[i] / dTs[i + 1]) for i in range(2)]
    for o in orders:
        assert abs(o - 1.0) < 0.02


@pytest.mark.parametrize("seed", range(10))
def test_second_law_and_conduction_is_most_wasteful(seed: int) -> None:
    T_h, T_c, g_h, g_c = draw(seed)
    cond = m.conduction_only(T_h, T_c, g_h, g_c)
    assert cond["work"] == 0.0 and cond["entropy_rate"] > 0.0
    for T1 in np.linspace(T_c, T_h, 41)[1:-1]:
        P, T2 = m.power_at(T1, T_h, T_c, g_h, g_c)
        if not np.isfinite(P) or P < 0:
            continue
        s = m.entropy_rate_with_engine(T1, T_h, T_c, g_h, g_c)
        assert s >= -1e-12 * cond["entropy_rate"]
        assert s <= cond["entropy_rate"] * (1 + 1e-12)


@pytest.mark.parametrize("seed", range(10))
def test_openness_threshold_identity(seed: int) -> None:
    T_h, T_c, _, _ = draw(seed)
    sigma = 10 ** np.random.default_rng(23100 + seed).uniform(-4, 1)
    Kstar = m.openness_threshold(T_h, T_c, sigma)
    # symmetric conductances g with K = g/2
    g = 2.0 * Kstar
    assert abs(m.max_power_closed_form(T_h, T_c, g, g) / (T_c * sigma) - 1.0) < 1e-12
    assert m.persists(T_h, T_c, 1.01 * g, 1.01 * g, sigma)
    assert not m.persists(T_h, T_c, 0.99 * g, 0.99 * g, sigma)
    assert not m.persists(T_h, T_c, 1e-30, 1e-30, sigma)  # closed: no order can be kept


def test_sun_earth_illustration() -> None:
    assert abs(m.efficiency_at_max_power(5772.0, 255.0) - 0.7898) < 1e-3
