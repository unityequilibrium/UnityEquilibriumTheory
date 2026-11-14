"""Physics tests for layer 3 of the Author Proposition (persistence selection).

docs/STANDARD.md section 6:
- known result: Little's law N* = b tau, reached by the exhaustion model alone,
  with measured first-order convergence in dt
- known solution: consumer-resource equilibrium R* = 1/(a tau),
  N* = (S - delta R*)/(a F R*), and competitive exclusion by lowest R*
- derivation check (sympy): frequencies of the exhaustion model obey
  replicator dynamics dx_i/dt = x_i (g_i - g_bar) identically
- identity: bits written over a lifetime do not depend on burn power
- negative control: without exhaustion there is no steady abundance
"""

from __future__ import annotations

import importlib
import math

import pytest
import sympy as sp

sel = importlib.import_module("docs.core.03_lanes.persistence.uet_persistence_selection")

pytestmark = pytest.mark.physics


def test_littles_law_emerges_from_exhaustion_with_first_order_convergence() -> None:
    b, F, P = 3.0, 2.0, 0.75          # tau = 2.666..., deliberately not a multiple of dt
    tau = sel.lifetime(F, P)
    exact = sel.steady_abundance(b, tau)
    # grids with tau/dt = m + 1/2 keep the cohort-rounding phase fixed, so the
    # discretization error is a clean first-order term
    grids = [tau / (m + 0.5) for m in (10, 21, 43)]
    errors = []
    for dt in grids:
        (n,) = sel.simulate_cohorts([b], [F], [P], horizon=4 * tau, dt=dt)
        errors.append(abs(n - exact))
        assert abs(n - exact) <= b * dt + 1e-12          # at most one cohort of discretization error
    orders = [math.log(errors[i] / errors[i + 1]) / math.log(grids[i] / grids[i + 1]) for i in range(2)]
    assert all(abs(o - 1.0) < 0.2 for o in orders), orders


def test_abundance_ratio_follows_lifetime_ratio() -> None:
    # same formation rate, different burn power: the slow burner is seen more often
    b, F = 1.0, 1.0
    slow, fast = sel.simulate_cohorts([b, b], [F, F], [0.1, 0.4], horizon=40.0, dt=0.005)
    assert abs(slow / fast - 4.0) < 0.01


def test_single_type_converges_to_analytic_equilibrium() -> None:
    t = sel.SystemType(capture=2.0, free_energy_store=0.5, burn_power=0.25)   # tau = 2, R* = 0.25
    S, delta = 1.0, 0.4
    N_star, R_star = sel.single_type_equilibrium(t, S, delta)
    N, R = sel.simulate_competition([0.1], 1.0, [t], S, delta, horizon=400.0, dt=0.01)
    assert abs(R - R_star) < 1e-8
    assert abs(N[0] - N_star) / N_star < 1e-8


@pytest.mark.parametrize("seed", range(5))
def test_lowest_r_star_excludes_competitors(seed: int) -> None:
    import random
    rng = random.Random(7000 + seed)
    types = [sel.SystemType(rng.uniform(0.5, 3.0), rng.uniform(0.2, 2.0), rng.uniform(0.1, 1.0)) for _ in range(3)]
    stars = sorted(t.r_star() for t in types)
    if stars[1] - stars[0] < 0.05 * stars[0]:
        pytest.skip("near-tie in R*; exclusion too slow to resolve in the horizon")
    S, delta = 2.0, 0.1
    if S <= delta * stars[0]:
        pytest.skip("no type can persist")
    N, R = sel.simulate_competition([0.2, 0.2, 0.2], 1.0, types, S, delta, horizon=3000.0, dt=0.02)
    winner = sel.predicted_winner(types)
    N_star, R_star = sel.single_type_equilibrium(types[winner], S, delta)
    assert abs(R - R_star) / R_star < 1e-4
    assert abs(N[winner] - N_star) / N_star < 1e-3
    assert all(N[i] < 1e-6 * N_star for i in range(3) if i != winner)


def test_replicator_dynamics_is_an_identity_of_the_exhaustion_model() -> None:
    R = sp.Symbol("R", positive=True)
    a = sp.symbols("a0:3", positive=True)
    tau = sp.symbols("tau0:3", positive=True)
    N = sp.symbols("N0:3", positive=True)
    g = [a[i] * R - 1 / tau[i] for i in range(3)]
    dN = [g[i] * N[i] for i in range(3)]
    total = sum(N)
    x = [N[i] / total for i in range(3)]
    dtotal = sum(dN)
    gbar = sum(x[i] * g[i] for i in range(3))
    for i in range(3):
        dx_quotient = (dN[i] * total - N[i] * dtotal) / total**2
        assert sp.simplify(dx_quotient - x[i] * (g[i] - gbar)) == 0


@pytest.mark.parametrize("power", [1e-3, 1.0, 1e3])
def test_bits_written_do_not_depend_on_burn_power(power: float) -> None:
    F, T = 5.0, 300.0
    tau = sel.lifetime(F, power)
    steps = 1000
    integral = sum(power / (sel.K_B * T * math.log(2.0)) * (tau / steps) for _ in range(steps))
    assert abs(integral - sel.bits_written(F, T)) / sel.bits_written(F, T) < 1e-12


def test_negative_control_no_exhaustion_means_no_steady_state() -> None:
    # burn power -> 0 makes tau -> infinity; abundance keeps growing with the horizon
    b, F = 1.0, 1.0
    (n1,) = sel.simulate_cohorts([b], [F], [1e-9], horizon=10.0, dt=0.01)
    (n2,) = sel.simulate_cohorts([b], [F], [1e-9], horizon=20.0, dt=0.01)
    assert n2 > 1.9 * n1
