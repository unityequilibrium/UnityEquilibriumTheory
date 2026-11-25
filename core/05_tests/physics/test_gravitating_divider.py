"""Wave D4: a divider for systems with negative heat capacity (held together by gravity).

(a) Derivation check: the general ODE path equals T_c + (T0 - T_c) exp(-G t/C) for linear contacts,
    for both signs of C, at 24 random cases, rel < 1e-9.
(b) Known limits through the general path: C > 0 relaxes to the divider (wave D1 behaviour);
    C < 0 radiating to 0 K follows t(T) = (4|C|/3G)(T0^-3 - T^-3) and so diverges at t*.
(c) Conservation and second law for two bodies in contact: C1 T1 + C2 T2 is constant and the total
    entropy C1 ln T1 + C2 ln T2 never decreases, also in the runaway.
(d) Second route: the gap growth rate from the ODE equals the non-zero eigenvalue of the system
    matrix, and its sign switches exactly at C2 = |C1| (Lynden-Bell and Wood).
(e) The usable fraction 1 - T_c/T rises with time for C < 0 and falls for C > 0; the virial heat
    capacity is -(3/2) N k, and the solar Kelvin-Helmholtz time is about 31 Myr.
"""

from __future__ import annotations

import importlib
from math import exp, log

import numpy as np
import pytest

pytestmark = pytest.mark.physics

gd = importlib.import_module("docs.core.03_lanes.persistence.uet_gravitating_divider")


@pytest.mark.parametrize("seed", range(24))
def test_general_path_matches_linear_closed_form(seed: int) -> None:
    rng = np.random.default_rng(11000 + seed)
    sign = -1.0 if seed % 2 == 0 else 1.0
    C = sign * 10 ** rng.uniform(-1, 2)
    T0 = 10 ** rng.uniform(1, 4)
    T_c = T0 * rng.uniform(0.0, 0.9)
    G = 10 ** rng.uniform(-1, 1)
    t_end = rng.uniform(0.5, 3.0) * abs(C) / G  # up to e^3 growth for C < 0
    sol = gd.evolve_against_divider(C, T0, T_c, G, 1.0, t_end, t_eval=[t_end])
    exact = gd.linear_closed_form(C, T0, T_c, G, t_end)
    assert abs(sol.y[0][-1] / exact - 1.0) < 1e-9


def test_positive_heat_capacity_relaxes_to_divider() -> None:
    C, T0, T_c, G = 2.0, 300.0, 3.0, 1.0
    sol = gd.evolve_against_divider(C, T0, T_c, G, 4.0, 200.0, t_eval=[200.0])
    assert abs(sol.y[0][-1] - T_c) / T_c < 0.05  # radiative relaxation is slow near T_c (power law tail)
    assert sol.y[0][-1] > T_c * (1.0 - 1e-10)  # never crosses the divider beyond round-off


@pytest.mark.parametrize("ratio", [2.0, 10.0, 100.0])
def test_negative_heat_capacity_radiative_runaway(ratio: float) -> None:
    C, T0, G = gd.virial_heat_capacity(1.0e4), 50.0, 1e-3
    T_target = ratio * T0
    t_expected = gd.radiative_time_to(T_target, C, T0, G)
    sol = gd.evolve_against_divider(C, T0, 0.0, G, 4.0, 2.0 * gd.radiative_blowup_time(C, T0, G),
                                    T_stop=T_target)
    assert sol.status == 1  # stopped by the event: the temperature really reached the target
    assert abs(sol.t_events[0][0] / t_expected - 1.0) < 1e-9
    assert t_expected < gd.radiative_blowup_time(C, T0, G)


@pytest.mark.parametrize("seed", range(6))
def test_two_body_energy_and_entropy(seed: int) -> None:
    rng = np.random.default_rng(seed)
    C1 = -10 ** rng.uniform(0, 2)
    C2 = abs(C1) * 10 ** rng.uniform(-1, 1)
    T1, T2 = 10 ** rng.uniform(1.5, 2.5), 10 ** rng.uniform(0.5, 1.4)
    G = 1.0
    lam = gd.gap_rate(C1, C2, G)
    t_end = 2.0 / abs(lam)
    ts = np.linspace(0.0, t_end, 60)
    sol = gd.evolve_two_body(C1, C2, T1, T2, G, t_end, t_eval=ts)
    E = C1 * sol.y[0] + C2 * sol.y[1]
    assert np.max(np.abs(E / E[0] - 1.0)) < 1e-10
    S = np.array([gd.two_body_entropy(C1, C2, a, b) for a, b in zip(sol.y[0], sol.y[1])])
    assert np.all(np.diff(S) >= -1e-12 * np.max(np.abs(S)))


@pytest.mark.parametrize("seed", range(10))
def test_gap_rate_two_routes_and_stability_switch(seed: int) -> None:
    rng = np.random.default_rng(12000 + seed)
    C1 = -10 ** rng.uniform(-1, 2)
    C2 = abs(C1) * 10 ** rng.uniform(-1.5, 1.5)
    G = 10 ** rng.uniform(-1, 1)
    lam = gd.gap_rate(C1, C2, G)
    eig = gd.jacobian_eigenvalues(C1, C2, G)
    nonzero = eig[np.argmax(np.abs(eig))].real
    # G/C1 + G/C2 cancels near C2 = |C1|; the non-symmetric eigen solver loses ~1e-12 per unit of cancellation
    cancel = (G / abs(C1) + G / C2) / abs(lam)
    assert abs(nonzero / lam - 1.0) < 1e-10 + 1e-12 * cancel
    assert np.min(np.abs(eig)) < 1e-12 * (G / abs(C1) + G / C2)  # the zero mode is energy conservation
    # ODE route: the gap grows or decays at exactly this rate
    t_end = 1.0 / abs(lam)
    sol = gd.evolve_two_body(C1, C2, 100.0, 40.0, G, t_end, t_eval=[t_end])
    gap = sol.y[0][-1] - sol.y[1][-1]
    assert abs(log(gap / 60.0) / (lam * t_end) - 1.0) < 1e-8
    assert (lam > 0.0) == (C2 > abs(C1))


def test_unlimited_divider_always_runs_away() -> None:
    C1, G = -5.0, 1.0
    for C2 in [6.0, 60.0, 6e3, 6e6]:
        assert gd.gap_rate(C1, C2, G) > 0.0
    # the limit C2 -> infinity is the single-body law with rate G/|C1|
    assert abs(gd.gap_rate(C1, 1e15, G) / (G / abs(C1)) - 1.0) < 1e-12


def test_usable_fraction_trend_and_constants() -> None:
    T_c, G, ts = 3.0, 1.0, np.linspace(0.0, 2.0, 21)
    hot = gd.evolve_against_divider(-1.0, 50.0, T_c, G, 1.0, 2.0, t_eval=ts).y[0]
    cool = gd.evolve_against_divider(+1.0, 50.0, T_c, G, 1.0, 2.0, t_eval=ts).y[0]
    assert np.all(np.diff(1.0 - T_c / hot) > 0.0)
    assert np.all(np.diff(1.0 - T_c / cool) < 0.0)
    assert gd.virial_heat_capacity(2.0, k=3.0) == -9.0
    t_kh_myr = gd.kelvin_helmholtz_time() / gd.YEAR / 1e6
    assert 30.0 < t_kh_myr < 33.0
