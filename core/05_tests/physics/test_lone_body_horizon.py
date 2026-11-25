"""Wave D7 (model A): a lone body in Lambda-only space cools into the horizon bath.

(a) Derivation check: closed-form cooling time equals the numerical integral of
    dT / (kappa (T^4 - Tb^4)) at 24 random (T0, T1, Tb, kappa), rel < 1e-10.
(b) Second route: integrating the ODE C dT/dt = -sigma A (T^4 - Tb^4) for the closed-form time
    lands on T1 (rel < 1e-7).
(c) Known limit with convergence: as Tb -> 0 the time tends to (T1^-3 - T0^-3)/(3 kappa) with error
    of order 4 in Tb (three grids).
(d) Second law and relaxation: body plus bath entropy change >= 0, -> C eps^2/2 near the bath;
    late-time rate d ln(T - Tb)/dt -> -4 kappa Tb^3.
(e) Identity: the thermal wavelength of the de Sitter bath is 4 pi^2 horizon radii for any H.
"""

from __future__ import annotations

import importlib
from math import log, pi

import numpy as np
import pytest
from scipy.integrate import solve_ivp

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_lone_body_horizon")


def _draw(rng):
    Tb = 10 ** rng.uniform(-3, 1)
    T1 = Tb * (1.0 + 10 ** rng.uniform(-3, 2))
    T0 = T1 * (1.0 + 10 ** rng.uniform(-2, 2))
    kappa = 10 ** rng.uniform(-3, 1)
    return T0, T1, Tb, kappa


@pytest.mark.parametrize("seed", range(24))
def test_closed_form_matches_numeric_integral(seed: int) -> None:
    T0, T1, Tb, kappa = _draw(np.random.default_rng(18000 + seed))
    a = m.cooling_time_closed_form(T0, T1, Tb, kappa)
    b = m.cooling_time_numeric(T0, T1, Tb, kappa)
    assert abs(a / b - 1.0) < 1e-10


@pytest.mark.parametrize("seed", range(6))
def test_ode_reaches_T1_at_closed_form_time(seed: int) -> None:
    T0, T1, Tb, kappa = _draw(np.random.default_rng(18100 + seed))
    t = m.cooling_time_closed_form(T0, T1, Tb, kappa)
    # integrate in u = ln T for a well-scaled problem
    sol = solve_ivp(lambda _t, u: [-kappa * (np.exp(4 * u[0]) - Tb ** 4) / np.exp(u[0])],
                    (0.0, t), [log(T0)], method="DOP853", rtol=1e-12, atol=1e-14)
    assert abs(np.exp(sol.y[0, -1]) / T1 - 1.0) < 1e-7


def test_zero_bath_limit_converges_at_fourth_order() -> None:
    T0, T1, kappa = 5.0, 1.0, 0.7
    ref = (T1 ** -3 - T0 ** -3) / (3.0 * kappa)
    Tbs = [0.2, 0.1, 0.05]
    errs = [abs(m.cooling_time_closed_form(T0, T1, Tb, kappa) - ref) for Tb in Tbs]
    orders = [log(errs[i] / errs[i + 1]) / log(Tbs[i] / Tbs[i + 1]) for i in range(2)]
    for p in orders:
        assert abs(p - 4.0) < 0.05


@pytest.mark.parametrize("seed", range(10))
def test_second_law_and_near_bath_limit(seed: int) -> None:
    T0, T1, Tb, _ = _draw(np.random.default_rng(18200 + seed))
    C = 3.7
    body, bath = m.entropy_changes(T0, T1, Tb, C)
    assert body < 0 < bath and body + bath > 0
    for eps in (1e-3, 1e-4):
        b, s = m.entropy_changes(Tb * (1 + eps), Tb, Tb, C)
        assert abs((b + s) / (C * eps * eps / 2.0) - 1.0) < 2.0 * eps


def test_late_time_relaxation_rate() -> None:
    Tb, kappa = 1.0, 0.4
    # t(T) from the closed form; slope of ln(T - Tb) against t near the bath
    T_a, T_b = Tb * (1 + 1e-5), Tb * (1 + 1e-6)
    dt = m.cooling_time_closed_form(T_a, T_b, Tb, kappa)
    rate = (log(T_b - Tb) - log(T_a - Tb)) / dt
    assert abs(rate / (-4.0 * kappa * Tb ** 3) - 1.0) < 1e-4


@pytest.mark.parametrize("H", [1e-20, 1.84e-18, 3e-10, 1.0])
def test_bath_wavelength_is_four_pi_squared_horizons(H: float) -> None:
    ratio = m.thermal_wavelength(m.bath_temperature(H)) / (m.C_LIGHT / H)
    assert abs(ratio / (4.0 * pi ** 2) - 1.0) < 1e-12
