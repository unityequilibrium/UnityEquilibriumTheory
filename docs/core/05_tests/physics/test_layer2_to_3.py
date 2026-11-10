"""Wave A4: layer 2 -> layer 3. Lifetime from the burn law, selection, mixed equilibria.

(a) tau = integral dF/P(F): numerical integration of dF/dt = -P(F) converges to the closed
    form; the regulated limit n = 0 reproduces the layer-3 lifetime F/P through the general
    path; the passive case n = 1 reproduces the A3 exponential law.
(b) Passive burners never reach F = 0 (lifetime diverges logarithmically).
(c) Selection with exact fixed lifetimes (no exponential-death approximation) across mixed
    burn laws: the lowest R* = 1/(a tau) survives and the pool settles at that R*.
(d) Two resources: two types coexist at the predicted mixed equilibrium, and that state is
    Nash-stable: a rare type invades if and only if its invasion fitness is positive.
(e) Bits written: independent of burn rate at fixed T, but proportional to P^(-1/4) for a
    blackbody emitter (derived relation; the test checks consistency with the fixed-T law).
"""

from __future__ import annotations

import importlib
import math

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_layer2_to_3")
l3 = importlib.import_module("docs.core.03_lanes.persistence.uet_persistence_selection")


@pytest.mark.parametrize("n,f_min", [(0.0, 0.0), (0.5, 0.0), (1.0, 0.05), (1.5, 0.05)])
def test_lifetime_integral_converges_to_closed_form(n: float, f_min: float) -> None:
    f0, p0 = 2.0, 0.7
    exact = m.lifetime_power_law(f0, p0, n, f_min)
    errs = [abs(m.lifetime_by_integration(lambda f: m.power_law_burn(f, f0, p0, n), f0, f_min, dt) / exact - 1.0)
            for dt in (0.02, 0.01, 0.005)]
    assert errs[-1] < 1e-4, errs
    if n in (1.0, 1.5):  # smooth crossing: at least first-order convergence of the interpolated crossing
        assert errs[2] <= errs[0]


def test_regulated_limit_recovers_layer3_lifetime_through_general_path() -> None:
    assert m.lifetime_power_law(3.0, 0.4, 0.0) == pytest.approx(l3.lifetime(3.0, 0.4), rel=1e-14)
    assert m.lifetime_power_law(3.0, 0.4, 1e-9) == pytest.approx(l3.lifetime(3.0, 0.4), rel=1e-6)


def test_passive_burner_never_reaches_zero() -> None:
    taus = [m.lifetime_power_law(1.0, 1.0, 1.0, f) for f in (1e-2, 1e-4, 1e-8)]
    assert taus[1] / taus[0] == pytest.approx(2.0) and taus[2] / taus[0] == pytest.approx(4.0)
    with pytest.raises(ValueError):
        m.lifetime_power_law(1.0, 1.0, 1.0, 0.0)


SPECS = [  # (capture a, F0, P0, n, f_min): regulated, passive, intermediate
    (1.0, 1.0, 0.5, 0.0, 0.0),
    (1.0, 1.0, 0.8, 1.0, 0.05),
    (1.2, 1.0, 1.0, 0.5, 0.0),
]


def test_lowest_r_star_wins_across_mixed_burn_laws() -> None:
    taus = [m.lifetime_power_law(f, p, n, fm) for _, f, p, n, fm in SPECS]
    r_star = [1.0 / (s[0] * t) for s, t in zip(SPECS, taus)]
    winner = int(np.argmin(r_star))
    # the naive rule F0/P0 would rank the passive type last; the burn-law lifetime ranks it first
    assert int(np.argmax([s[1] / s[2] for s in SPECS])) != winner
    for dt in (0.02, 0.01):
        n_fin, r_fin = m.simulate_fixed_lifetime_competition(
            [[s[0]] for s in SPECS], [s[1] for s in SPECS], taus, [1.0], [0.1], [0.1] * 3, [1.0], 600.0, dt)
        assert all(n_fin[i] < 1e-6 for i in range(3) if i != winner)
        # the simulation rounds tau to a whole number of steps; against that lifetime R* is met tightly,
        # and against the exact lifetime within the rounding bound dt / (2 tau)
        tau_grid = round(taus[winner] / dt) * dt
        assert abs(r_fin[0] * SPECS[winner][0] * tau_grid - 1.0) < 1e-4
        assert abs(r_fin[0] / r_star[winner] - 1.0) <= dt / (2 * taus[winner]) + 1e-4


CAPTURE2 = [[1.0, 0.2], [0.2, 1.0]]
TAUS2 = [2.0, 2.5]


def _two_resource_run(extra_capture=None, extra_tau=None):
    cap = [list(r) for r in CAPTURE2]
    taus, n0 = list(TAUS2), [0.1, 0.1]
    if extra_capture is not None:
        cap.append(list(extra_capture))
        taus.append(extra_tau)
        n0.append(1e-3)
    return m.simulate_fixed_lifetime_competition(cap, [1.0] * len(taus), taus, [1.0, 1.0], [0.1, 0.1],
                                                 n0, [1.0, 1.0], 800.0, 0.01)


def test_two_resources_give_a_mixed_equilibrium() -> None:
    r_pred = m.coexistence_resources(CAPTURE2, TAUS2)
    n_fin, r_fin = _two_resource_run()
    assert np.all(n_fin > 0.5)  # both types persist: no competitive exclusion
    assert np.max(np.abs(r_fin / r_pred - 1.0)) < 5e-3
    # with one shared resource the same two types cannot coexist
    n1, _ = m.simulate_fixed_lifetime_competition([[1.0], [1.0]], [1.0, 1.0], TAUS2, [1.0], [0.1],
                                                  [0.1, 0.1], [1.0], 800.0, 0.01)
    assert n1[0] < 1e-6 < n1[1]


@pytest.mark.parametrize("capture,tau", [((0.5, 0.5), 2.5), ((0.7, 0.7), 2.5), ((0.9, 0.1), 2.0), ((0.9, 0.9), 2.0)])
def test_mixed_equilibrium_is_nash_invasion_follows_fitness_sign(capture, tau: float) -> None:
    r_pred = m.coexistence_resources(CAPTURE2, TAUS2)
    fitness = m.invasion_fitness(capture, tau, r_pred)
    assert abs(fitness) > 0.02  # not a marginal case
    n_fin, _ = _two_resource_run(capture, tau)
    if fitness > 0:
        assert n_fin[2] > 1e-2  # grew from 1e-3: invaded
    else:
        assert n_fin[2] < 1e-6  # died out: residents are uninvadable by this strategy


def test_bits_depend_on_burn_rate_only_when_temperature_follows_power() -> None:
    f, c = 5.0, 2.0
    assert m.bits_fixed_temperature(f, 1.3) == pytest.approx(f / (1.3 * math.log(2.0)))
    # P = c T^4 fixes T, so the fixed-T law applies at that T with the radiation factor 4/3
    for p in (0.5, 8.0):
        assert m.bits_blackbody(f, p, c) == pytest.approx(4.0 / 3.0 * m.bits_fixed_temperature(f, (p / c) ** 0.25))
    ratio = m.bits_blackbody(f, 0.5, c) / m.bits_blackbody(f, 8.0, c)
    assert ratio == pytest.approx(16.0 ** 0.25)  # 16x slower burn writes 2x more bits
