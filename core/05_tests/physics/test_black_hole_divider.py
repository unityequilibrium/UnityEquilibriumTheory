"""Wave D5: a black hole as the divider.

(a) Derivation check: complex-step derivatives of the code's S(M) and T_H(M) give dS/dE = 1/T_H and
    dE/dT_H = C = -8 pi G M^2 k/(hbar c) at 24 random masses, rel < 1e-12.
(b) Known limit through the general path: the evaporation ODE reproduces the closed-form time
    5120 pi G^2 (M0^3 - M^3)/(hbar c^4); the full lifetime is F0/(3 P0), one third of the naive
    store-over-power estimate (unregulated burner, P ~ F^-2).
(c) Second law: heat moved from a body hotter than T_H into the hole raises the total entropy, and
    the reverse transfer lowers it; the hole gets colder as it receives energy.
(d) Second route: the crossover mass from T_H(M_eq) = T_CMB solved numerically equals
    hbar c^3/(8 pi G k T_CMB).
(e) Scale: S(Sgr A*) ~ 1.8e90 k, and the Schwarzschild values for one solar mass
    (T_H = 6.17e-8 K, S = 1.05e77 k, lifetime 2.1e67 yr).
"""

from __future__ import annotations

import importlib
import numpy as np
import pytest
from scipy.optimize import brentq

pytestmark = pytest.mark.physics

bh = importlib.import_module("docs.core.03_lanes.persistence.uet_black_hole_divider")
C2 = bh.C_LIGHT ** 2


def _complex_step(f, x: float) -> float:
    h = 1e-20 * x
    return (f(x + 1j * h)).imag / h


@pytest.mark.parametrize("seed", range(24))
def test_thermodynamic_identities_by_complex_step(seed: int) -> None:
    rng = np.random.default_rng(13000 + seed)
    M = bh.M_SUN * 10 ** rng.uniform(-8, 10)
    dS_dM = _complex_step(bh.entropy, M)
    assert abs((dS_dM / C2) * bh.hawking_temperature(M) - 1.0) < 1e-12   # dS/dE = 1/T_H
    dT_dM = _complex_step(bh.hawking_temperature, M)
    assert abs((C2 / dT_dM) / bh.heat_capacity(M) - 1.0) < 1e-12        # dE/dT_H = C
    assert bh.heat_capacity(M) < 0.0


@pytest.mark.parametrize("frac", [0.9, 0.5, 0.1, 1e-3])
def test_evaporation_ode_matches_closed_form(frac: float) -> None:
    M0 = 3.0 * bh.M_SUN
    t_num = bh.evaporation_time_numeric(M0, frac * M0)
    t_exact = bh.evaporation_time_closed_form(M0, frac * M0)
    assert abs(t_num / t_exact - 1.0) < 1e-10


def test_lifetime_is_one_third_of_naive_store_over_power() -> None:
    for M0 in [1e12, bh.M_SUN, bh.M_SGR_A]:
        naive = M0 * C2 / bh.hawking_power(M0)
        assert abs(bh.evaporation_time_closed_form(M0) / (naive / 3.0) - 1.0) < 1e-12


@pytest.mark.parametrize("seed", range(6))
def test_generalised_second_law_and_cooling_on_receipt(seed: int) -> None:
    rng = np.random.default_rng(seed)
    M = bh.M_SUN * 10 ** rng.uniform(-3, 7)
    T_H = bh.hawking_temperature(M)
    dE = 1e-6 * M * C2
    assert bh.entropy_change_of_transfer(dE, 10.0 * T_H, M) > 0.0    # into the colder hole: allowed
    assert bh.entropy_change_of_transfer(dE, 0.1 * T_H, M) < 0.0     # into a hotter hole: forbidden
    # receiving energy makes the hole colder (better divider), unlike a positive-C divider
    assert bh.hawking_temperature(M + dE / C2) < T_H
    # the entropy gained by the hole is exactly the integral of dE/T_H (first-order check)
    gain = bh.entropy(M + dE / C2) - bh.entropy(M)
    assert abs(gain / (dE / T_H) - 1.0) < 2e-6


def test_crossover_mass_two_routes() -> None:
    numeric = brentq(lambda M: bh.hawking_temperature(M) - bh.T_CMB, 1e18, 1e26, xtol=1e6, rtol=1e-14)
    assert abs(numeric / bh.crossover_mass() - 1.0) < 1e-12
    assert 4.4e22 < bh.crossover_mass() < 4.6e22
    assert bh.hawking_temperature(bh.M_SUN) < bh.T_CMB  # stellar holes are colder than the CMB today


def test_reference_scales() -> None:
    assert abs(bh.hawking_temperature(bh.M_SUN) / 6.17e-8 - 1.0) < 2e-3
    assert abs(bh.entropy(bh.M_SUN) / bh.K_B / 1.049e77 - 1.0) < 2e-3
    assert abs(bh.evaporation_time_closed_form(bh.M_SUN) / bh.YEAR / 2.096e67 - 1.0) < 2e-3
    s_sgr = bh.entropy(bh.M_SGR_A) / bh.K_B
    assert 1.7e90 < s_sgr < 1.9e90
    assert abs(s_sgr / (bh.entropy(bh.M_SUN) / bh.K_B * 4.152e6 ** 2) - 1.0) < 1e-12  # S ~ M^2
