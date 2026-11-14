"""R1 physics checks: the two established channels by which energy use writes onto space.

(a) Radiation: the entropy-to-energy ratio of blackbody light, s/u = 4/(3T), derived by
    numerical integration of the Planck spectrum (photon gas, k_B = h = c = 1).
(b) Gravity: a test orbit around a central mass that slowly loses mass expands as
    a ~ 1/(GM) (adiabatic invariant), found by direct integration of Newton's equations.
(c) The radiative mass-loss fraction of the Sun from its nominal luminosity.
"""

from __future__ import annotations

import importlib
import math

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp

pytestmark = pytest.mark.physics

r1 = importlib.import_module("docs.core.03_lanes.open_system.uet_r1_writing_channels")


@pytest.mark.parametrize("temperature", [0.5, 1.0, 3.0])
def test_blackbody_entropy_over_energy_is_four_thirds_over_t(temperature: float) -> None:
    # per mode: u = w n, s = (1+n) ln(1+n) - n ln n, with n = 1/(exp(w/T)-1); density of states ~ w^2
    def n(w):
        return 1.0 / math.expm1(w / temperature)

    u, _ = quad(lambda w: w**2 * w * n(w), 0, 60 * temperature, limit=200)
    s, _ = quad(lambda w: w**2 * ((1 + n(w)) * math.log1p(n(w)) - n(w) * math.log(n(w))), 1e-12, 60 * temperature, limit=200)
    assert abs((s / u) * temperature / (4.0 / 3.0) - 1.0) < 1e-8


def _orbit_expansion(epsilon: float, t_end: float) -> float:
    """GM(t) = 1 - epsilon t; start on a circular orbit of radius 1; return mean radius near t_end."""
    def rhs(t, y):
        gm = 1.0 - epsilon * t
        r3 = (y[0] ** 2 + y[1] ** 2) ** 1.5
        return [y[2], y[3], -gm * y[0] / r3, -gm * y[1] / r3]

    sol = solve_ivp(rhs, (0.0, t_end), [1.0, 0.0, 0.0, 1.0], method="DOP853", rtol=1e-11, atol=1e-13,
                    dense_output=True)
    ts = np.linspace(t_end - 4 * math.pi, t_end, 4000)  # average over about two orbits
    xs = sol.sol(ts)
    return float(np.mean(np.hypot(xs[0], xs[1])))


def test_orbits_expand_as_inverse_gm_when_the_centre_loses_mass() -> None:
    t_end = 200.0
    ratios = []
    for eps in (4e-4, 2e-4, 1e-4):  # slower mass loss -> closer to the adiabatic limit
        r_mean = _orbit_expansion(eps, t_end)
        ratios.append(r_mean * (1.0 - eps * t_end))  # a * GM should stay 1
    errs = [abs(x - 1.0) for x in ratios]
    assert errs[-1] < 2e-3, ratios
    assert errs[0] > errs[-1]


def test_sun_radiative_mass_loss_fraction() -> None:
    frac = r1.radiative_mass_loss_fraction_per_year()
    assert 6.7e-14 < frac < 6.85e-14
    # bits per second at the photosphere: (4/3) L / (k T ln 2), order 1e46
    assert 9.0e45 < r1.radiation_bits_per_second(r1.L_SUN, r1.T_EFF_SUN) < 9.5e45
