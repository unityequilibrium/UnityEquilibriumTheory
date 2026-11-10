"""Path-A model checks (general code path, known limits, negative control).

(a) White dwarf cooling: the A4 burn-law lifetime with n = 7/2 gives t ~ L^(-5/7); the slope of
    log N per M_bol obtained by differentiating the general lifetime_power_law numerically equals
    the closed form 2/7.
(b) Secular equilibrium: integrating a two-member decay chain from pure parent converges to the
    abundance law N_d/N_p = T_d/T_p.
(c) Negative control: non-autocatalytic channels sharing a reagent keep a fixed product ratio
    k1/k2 (no winner), while the autocatalytic version of the same competition excludes one.
"""

from __future__ import annotations

import importlib
import math

import numpy as np
import pytest
from scipy.integrate import solve_ivp

pytestmark = pytest.mark.physics

pa = importlib.import_module("docs.core.03_lanes.persistence.uet_path_a_models")
l23 = importlib.import_module("docs.core.03_lanes.persistence.uet_layer2_to_3")


def test_mestel_slope_from_general_burn_law_lifetime() -> None:
    n = pa.burn_exponent_from_luminosity_law(3.5)
    f0, p0 = 1.0, 1.0

    def log10_t_at_log10_l(log10_l: float) -> float:
        f = (10.0 ** log10_l / p0) ** (1.0 / n) * f0  # L = P0 (F/F0)^n
        return math.log10(l23.lifetime_power_law(f0, p0, n, f))

    devs = []
    for log10_l in (-3.0, -4.0, -5.0):  # deeper in the Mestel regime (F << F0) as L falls
        h = 1e-4
        dlogt_dlogl = (log10_t_at_log10_l(log10_l + h) - log10_t_at_log10_l(log10_l - h)) / (2 * h)
        devs.append(abs(-0.4 * dlogt_dlogl - pa.luminosity_function_slope_per_mag(n)))
    assert devs[0] > devs[1] > devs[2] and devs[2] < 1e-3, devs  # converges to the closed form
    assert pa.luminosity_function_slope_per_mag(n) == pytest.approx(2.0 / 7.0)


def test_secular_equilibrium_emerges_from_decay_chain() -> None:
    t_p, t_d = 1000.0, 3.0  # half-lives, daughter much shorter
    lp, ld = math.log(2) / t_p, math.log(2) / t_d
    sol = solve_ivp(lambda t, y: [-lp * y[0], lp * y[0] - ld * y[1]], (0, 60.0), [1.0, 0.0],
                    method="LSODA", rtol=1e-11, atol=1e-14)
    ratio = sol.y[1, -1] / sol.y[0, -1]
    # transient equilibrium: N_d/N_p = lp/(ld - lp) -> T_d/T_p as T_d/T_p -> 0
    assert abs(ratio / (lp / (ld - lp)) - 1.0) < 1e-6
    assert abs(ratio / pa.secular_equilibrium_ratio(t_d, t_p) - 1.0) < 5e-3


def test_negative_control_no_winner_without_autocatalysis() -> None:
    k1, k2 = 0.7, 0.3
    for t in (0.5, 2.0, 10.0):
        _, p1, p2 = pa.parallel_channels(k1, k2, 1.0, t)
        assert p1 / p2 == pytest.approx(k1 / k2)  # fixed ratio, both channels persist
    # same two channels made autocatalytic (growth ~ own amount x shared reagent) -> exclusion
    def rhs(t, y):
        a, x1, x2 = y
        return [0.5 - 0.1 * a - a * (k1 * x1 + k2 * x2), x1 * (k1 * a - 0.2), x2 * (k2 * a - 0.2)]
    sol = solve_ivp(rhs, (0, 600), [1.0, 1e-3, 1e-3], rtol=1e-9, atol=1e-12)
    x1, x2 = sol.y[1, -1], sol.y[2, -1]
    assert x2 < 1e-6 < x1
