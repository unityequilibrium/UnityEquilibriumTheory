"""Wave D8 (model B): bodies falling together - frying (dynamical friction) and mixing (merging).

(a) Derivation check: the slower-than-v fraction from integrating the Maxwellian equals
    erf X - (2X/sqrt pi) exp(-X^2) at 24 random X, rel < 1e-10.
(b) Known limits through the general path: f -> 4X^3/(3 sqrt pi) for slow bodies, f -> 1 for fast;
    circular-orbit binding -> Newtonian x/2 in the weak field (error of order x).
(c) Second route: integrating the orbit decay with the full Chandrasekhar force gives the closed-form
    sinking time (rel < 1e-8) at random masses, radii and speeds.
(d) Work-energy identity: the work done by friction along the integrated orbit equals the orbital
    energy lost, M v_c^2 ln(r_i/r_f), the energy handed to the sea.
(e) Innermost stable orbit from minimising E(x) is x = 1/6 and the inspiral loses 1 - sqrt(8/9).
(f) Area theorem through the entropy function: equal total entropy gives M_f = sqrt(m1^2 + m2^2);
    S(2m(1-eps)) / (2 S(m)) = 2 (1 - eps)^2.
"""

from __future__ import annotations

import importlib
from math import log, pi, sqrt

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_falling_together")


@pytest.mark.parametrize("seed", range(24))
def test_slower_fraction_matches_closed_form(seed: int) -> None:
    X = 10 ** np.random.default_rng(19000 + seed).uniform(-1, 0.6)
    assert abs(m.slower_fraction_numeric(X) / m.slower_fraction_closed_form(X) - 1.0) < 1e-10


def test_limits() -> None:
    for X in (1e-2, 1e-3):
        assert abs(m.slower_fraction_numeric(X) / (4 * X ** 3 / (3 * sqrt(pi))) - 1.0) < 2 * X * X
    assert abs(m.slower_fraction_numeric(8.0) - 1.0) < 1e-12
    for x in (1e-4, 1e-5):
        assert abs((1.0 - m.circular_energy(x)) / (x / 2.0) - 1.0) < 2.0 * x


@pytest.mark.parametrize("seed", range(4))
def test_sinking_time_ode_matches_closed_form(seed: int) -> None:
    rng = np.random.default_rng(19100 + seed)
    M = 10 ** rng.uniform(5, 8) * m.M_SUN
    r_i = 10 ** rng.uniform(-0.5, 1) * m.KPC
    v_c = 10 ** rng.uniform(4.8, 5.6)
    lnL = rng.uniform(3, 15)
    r_f = r_i * 10 ** rng.uniform(-3, -0.5)
    a = m.sinking_time_ode(M, r_i, v_c, lnL, r_f)
    b = m.sinking_time_closed_form(M, r_i, v_c, lnL, r_f)
    assert abs(a / b - 1.0) < 1e-8


def test_friction_work_equals_orbital_energy_lost() -> None:
    M, r_i, v_c, lnL = 1e6 * m.M_SUN, m.KPC, 2.2e5, 10.0
    r_f = 0.01 * r_i
    sigma = v_c / sqrt(2.0)

    def rhs(_t, y):
        r = y[0]
        rho = sigma ** 2 / (2 * pi * m.G * r * r)
        F = m.friction_force(M, v_c, sigma, rho, lnL)
        return [-r * F / (M * v_c), F * v_c]

    hit = lambda _t, y: y[0] - r_f  # noqa: E731
    hit.terminal = True
    sol = solve_ivp(rhs, (0, 2 * m.sinking_time_closed_form(M, r_i, v_c, lnL)), [r_i, 0.0], events=hit,
                    rtol=1e-11, atol=[r_f * 1e-12, 1.0], method="DOP853")
    work = sol.y_events[0][0][1]
    lost = M * v_c ** 2 * log(r_i / r_f)
    assert abs(work / lost - 1.0) < 1e-8
    # entropy handed to a sea of solar-mass stars, 2 (M/m) ln(r_i/r_f)
    assert abs(m.entropy_to_sea(M, m.M_SUN, r_i, r_f, v_c) / (2e6 * log(100.0)) - 1.0) < 1e-12


def test_isco_and_inspiral_fraction() -> None:
    assert abs(m.isco_x_numeric() - 1.0 / 6.0) < 1e-7
    assert abs(m.inspiral_fraction_of_mu() / (1.0 - sqrt(8.0 / 9.0)) - 1.0) < 1e-12


@pytest.mark.parametrize("seed", range(10))
def test_area_theorem_through_entropy(seed: int) -> None:
    rng = np.random.default_rng(19200 + seed)
    m1, m2 = 10 ** rng.uniform(0, 2, size=2) * m.M_SUN
    target = m.hole_entropy(m1) + m.hole_entropy(m2)
    M_f = brentq(lambda M: m.hole_entropy(M) - target, max(m1, m2), m1 + m2, xtol=1e-6, rtol=1e-15)
    assert abs((1.0 - M_f / (m1 + m2)) / m.area_theorem_cap(m1, m2) - 1.0) < 1e-10
    eps = rng.uniform(0.0, 0.29)
    ratio = m.hole_entropy(2 * m1 * (1 - eps)) / (2 * m.hole_entropy(m1))
    assert abs(ratio / m.merger_entropy_ratio(eps) - 1.0) < 1e-12
