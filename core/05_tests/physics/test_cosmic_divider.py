"""Wave D6: the expanding universe as the last divider.

(a) Derivation check: the Friedmann integral t(a) = int da/(a H) equals the closed form
    (2/3H_L) asinh(sqrt(OL/Om) a^1.5) at 24 random a from 1e-4 to 1e12, rel < 1e-10, and a(t)
    inverts it.
(b) Known limits through the general path: matter era t ~ (2/3) a^1.5 / (H0 sqrt(Om)); Lambda era
    d ln a / dt -> H_L.
(c) Identities: T_H(M_max) = T_dS with M_max = c^3/(4 G H) found by root search (second route);
    S_dS = pi k c^5/(G hbar H^2) obeys dS/dH = -2 S/H (complex step).
(d) Order of hand-over: the background becomes colder than a solar-mass hole before Sgr A*, and
    both before it falls below T_dS; the age today is 13.8 Gyr.
"""

from __future__ import annotations

import importlib
from math import log, sqrt

import numpy as np
import pytest
from scipy.optimize import brentq

pytestmark = pytest.mark.physics

cd = importlib.import_module("docs.core.03_lanes.persistence.uet_cosmic_divider")


@pytest.mark.parametrize("seed", range(24))
def test_friedmann_integral_matches_closed_form(seed: int) -> None:
    rng = np.random.default_rng(14000 + seed)
    a = 10 ** rng.uniform(-4, 12)
    numeric = cd.time_of_a_numeric(a)
    exact = cd.time_of_a(a)
    assert abs(numeric / exact - 1.0) < 1e-10
    assert abs(cd.a_of_time(exact) / a - 1.0) < 1e-10


@pytest.mark.parametrize("a", [1e-6, 1e-5, 1e-4])
def test_matter_era_limit(a: float) -> None:
    matter_only = 2.0 / 3.0 * a ** 1.5 / (cd.H0 * sqrt(cd.OMEGA_M))
    # correction is O(OL/Om a^3)
    assert abs(cd.time_of_a_numeric(a) / matter_only - 1.0) < 10.0 * cd.OMEGA_L / cd.OMEGA_M * a ** 3 + 1e-12


def test_lambda_era_limit() -> None:
    def rate(a: float) -> float:
        h = 1e-6
        dt = cd.time_of_a_numeric(a * (1 + h)) - cd.time_of_a_numeric(a * (1 - h))
        return (log(a * (1 + h)) - log(a * (1 - h))) / dt

    # H(a)/H_L - 1 = Om/(2 OL) a^-3 to leading order: matched at a = 100
    dev = rate(100.0) / cd.H_L - 1.0
    assert abs(dev / (cd.OMEGA_M / (2.0 * cd.OMEGA_L) * 100.0 ** -3) - 1.0) < 0.01
    # far into the Lambda era the rate is H_L to the finite-difference noise floor
    for a in [1e4, 1e6]:
        assert abs(rate(a) / cd.H_L - 1.0) < 1e-8


def test_largest_evaporating_mass_two_routes() -> None:
    T_dS = cd.de_sitter_temperature()
    root = brentq(lambda lm: log(cd.hawking_temperature(10 ** lm) / T_dS), 40.0, 60.0, xtol=1e-14, rtol=1e-15)
    assert abs(10 ** root / cd.largest_mass_that_evaporates() - 1.0) < 1e-10
    assert 5.5e52 < cd.largest_mass_that_evaporates() < 5.7e52


def test_de_sitter_entropy_scaling_by_complex_step() -> None:
    H = cd.H_L
    h = 1e-20 * H
    dS_dH = cd.de_sitter_entropy(H + 1j * h).imag / h
    assert abs(dS_dH / (-2.0 * cd.de_sitter_entropy(H) / H) - 1.0) < 1e-12
    assert 3.2e122 < cd.de_sitter_entropy() / cd.K_B < 3.4e122
    assert 2.1e-30 < cd.de_sitter_temperature() < 2.3e-30


def test_order_of_hand_over_and_age() -> None:
    t_sun = cd.time_background_reaches(cd.hawking_temperature(cd.M_SUN))
    t_sgr = cd.time_background_reaches(cd.hawking_temperature(4.152e6 * cd.M_SUN))
    t_ds = cd.time_background_reaches(cd.de_sitter_temperature())
    assert cd.time_of_a(1.0) < t_sun < t_sgr < t_ds
    assert abs(cd.time_of_a(1.0) / cd.YEAR / 1e9 - 13.8) < 0.05
    # in the Lambda era the hand-over times are spaced by ln(T ratio)/H_L
    gap = t_sgr - t_sun
    expected = log(cd.hawking_temperature(cd.M_SUN) / cd.hawking_temperature(4.152e6 * cd.M_SUN)) / cd.H_L
    assert abs(gap / expected - 1.0) < 1e-6
