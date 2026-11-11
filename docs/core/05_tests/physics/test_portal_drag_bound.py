"""Wave B5: orbit survival bounds the portal drag (module uet_portal_drag_bound.py).

1. The decay rate of the semi-major axis for a linear drag a = -lambda v on a circular orbit is 2 lambda:
   checked by integrating the perturbed Kepler problem (general code path), not by the formula.
2. The charge and the drag coefficient agree with wave B4 (uet_portal_drag.py) in the light limit.
3. Units: the natural-unit and the SI routes to the decay rate agree.
4. The bound scales as expected: inversely with M / R, and the bound on Gamma scales as 1 / g_c^2.
5. Negative control: with Gamma at 100 times the bound the orbit does NOT survive the age of the Solar System.
"""

from __future__ import annotations

import importlib
from math import exp, pi

import numpy as np
import pytest
from scipy.integrate import solve_ivp

pytestmark = pytest.mark.physics

pb = importlib.import_module("docs.core.03_lanes.open_system.uet_portal_drag_bound")
pd = importlib.import_module("docs.core.03_lanes.open_system.uet_portal_drag")

JUPITER = (1.8982e27, 7.1492e7)
EARTH = (5.9722e24, 6.371e6)


def _semi_major_axis(state: np.ndarray) -> float:
    r, v2 = np.hypot(state[0], state[1]), state[2] ** 2 + state[3] ** 2
    return 1.0 / (2.0 / r - v2)  # GM = 1


@pytest.mark.parametrize("lam", [1e-4, 1e-3, 4e-3])
def test_linear_drag_shrinks_the_semi_major_axis_at_twice_the_drag_rate(lam: float) -> None:
    def rhs(_t, s):
        r3 = np.hypot(s[0], s[1]) ** 3
        return [s[2], s[3], -s[0] / r3 - lam * s[2], -s[1] / r3 - lam * s[3]]

    t_end = 0.5 / lam
    sol = solve_ivp(rhs, (0.0, t_end), [1.0, 0.0, 0.0, 1.0], rtol=1e-11, atol=1e-13, method="DOP853")
    ratio = _semi_major_axis(sol.y[:, -1]) / 1.0
    assert ratio == pytest.approx(exp(-2.0 * lam * t_end), rel=2e-2 + 5 * lam)


def test_charge_and_light_limit_force_agree_with_wave_b4() -> None:
    g_c, (mass, radius) = 3.0e-10, EARTH
    q = pb.portal_charge(g_c, mass)
    m_chi2 = pb.NUCLEON_MASS_EV**2
    assert q == pytest.approx(pd.portal_charge(g_c, mass * pb.KG_TO_EV, m_chi2), rel=1e-12)
    # F / v from wave B4 (eV^2 per unit v/c) divided by M gives lambda; the decay rate is twice that, in eV.
    radius_inverse = pb.HBAR_C_EV_M / radius
    force_per_v = pd.drag_force_light_limit(1.0e-12, 1.0, q, 1.0 / radius_inverse)
    lam_ev = force_per_v / (mass * pb.KG_TO_EV)
    assert pb.decay_rate_ev(1.0e-12, g_c, mass, radius) == pytest.approx(2.0 * lam_ev, rel=1e-12)


@pytest.mark.parametrize("body", [JUPITER, EARTH])
def test_natural_and_si_routes_to_the_decay_rate_agree(body) -> None:
    mass, radius = body
    a = pb.decay_rate_per_second(1.0e-20, 4.0e-10, mass, radius)
    b = pb.decay_rate_per_second_si(1.0e-20, 4.0e-10, mass, radius)
    assert a == pytest.approx(b, rel=1e-9)


def test_bound_scales_with_radius_over_mass_and_inverse_g_c_squared() -> None:
    mass, radius = JUPITER
    base = pb.max_gamma_g_c_squared_ev3(mass, radius)
    assert pb.max_gamma_g_c_squared_ev3(2 * mass, radius) == pytest.approx(base / 2.0, rel=1e-12)
    assert pb.max_gamma_g_c_squared_ev3(mass, 3 * radius) == pytest.approx(3.0 * base, rel=1e-12)
    assert pb.max_gamma_ev(2.0e-10, mass, radius) == pytest.approx(pb.max_gamma_ev(4.0e-10, mass, radius) * 4.0, rel=1e-12)


def test_jupiter_is_more_constraining_than_earth() -> None:
    assert pb.max_gamma_g_c_squared_ev3(*JUPITER) < pb.max_gamma_g_c_squared_ev3(*EARTH)


def test_negative_control_a_hundred_times_the_bound_does_not_survive() -> None:
    mass, radius = JUPITER
    g_c = 5.12e-10
    gamma_max = pb.max_gamma_ev(g_c, mass, radius)
    survive = pb.decay_rate_per_second(gamma_max, g_c, mass, radius) * pb.SOLAR_SYSTEM_AGE_S
    doomed = pb.decay_rate_per_second(100.0 * gamma_max, g_c, mass, radius) * pb.SOLAR_SYSTEM_AGE_S
    assert survive == pytest.approx(1.0, rel=1e-9)  # one e-folding of the semi-major axis at the bound
    assert doomed == pytest.approx(100.0, rel=1e-9)
    assert exp(-doomed) < 1e-40
