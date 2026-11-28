"""Physics checks for the game-physics lane (core/03_lanes/game_physics)."""

from __future__ import annotations

import importlib
import math
import random

import numpy as np
import pytest

db = importlib.import_module("core.03_lanes.game_physics.debris_bath")
eb = importlib.import_module("core.03_lanes.game_physics.energy_budget")

pytestmark = pytest.mark.physics


# drag law ---------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("seed", range(20))
def test_G_equals_truncated_second_moment_by_quadrature(seed: int) -> None:
    """Independent route: E[s^2; s < 0] for s ~ N(-c, 1) by direct quadrature equals G(c)."""
    c = random.Random(8100 + seed).uniform(-3, 3)
    s = np.linspace(-c - 12, 0, 400001)
    pdf = np.exp(-0.5 * (s + c) ** 2) / math.sqrt(2 * math.pi)
    quad = np.trapezoid(s * s * pdf, s)
    assert abs(quad - float(db.G(c))) < 1e-8


def test_slow_limit_is_linear_friction_with_quadratic_correction() -> None:
    g0 = db.gamma0(1.0, 5.0, 1.0, 1.0)
    dev = [abs(db.drag(V, 1.0, 5.0, 1.0, 1.0) / (-g0 * V) - 1) for V in (0.2, 0.1, 0.05)]
    assert dev[2] < 1e-3
    assert 3.5 < dev[0] / dev[1] < 4.5 and 3.5 < dev[1] / dev[2] < 4.5      # O(V^2)


def test_fast_limit_is_newton_drag() -> None:
    dev = [abs(db.drag(V, 1.0, 5.0, 1.0, 1.0) / (-(8 / 3) * 5.0 * V * V) - 1) for V in (10.0, 20.0, 40.0)]
    assert dev[2] < 1e-3 and dev[0] > dev[1] > dev[2]


def test_drag_law_matches_full_collision_simulation() -> None:
    sc = db.Scene()
    for V in (0.5, 2.0):
        Fs = [sc.full_run(V, 300, 0.01, 10 * k + int(V * 7), fixed_velocity=True) for k in range(6)]
        se = np.std(Fs) / math.sqrt(len(Fs))
        assert abs(np.mean(Fs) - db.drag(V, sc.m, sc.n, sc.R, sc.T)) < 3 * se + 1e-9


# reduced debris model ----------------------------------------------------------------------------------------

def test_reduced_model_relaxes_to_closed_box_equilibrium() -> None:
    sc = db.Scene()
    V0 = 1.0
    runs = np.array([sc.reduced_run(V0, 4000, 0.01, 40 + k) for k in range(60)])
    late = (runs[:, 3000:] ** 2).sum(2).mean()
    assert abs(late / sc.equilibrium_V2(V0) - 1) < 0.12
    lin = np.array([sc.linear_langevin_run(V0, 4000, 0.01, 90 + k) for k in range(60)])
    assert (lin[:, 3000:] ** 2).sum(2).mean() < 0.7 * sc.equilibrium_V2(V0)   # control: no momentum bookkeeping


# energy budget ------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("v0", [0.5, 2.0, 5.0])
def test_stop_distance_is_the_limit_of_friction_integration(v0: float) -> None:
    errs = []
    for dt in (1 / 120, 1 / 240, 1 / 480):
        x, v = np.zeros((1, 2)), np.array([[v0, 0.0]])
        aw = np.ones(1, bool)
        for _ in range(int(2 * v0 / (eb.MU * eb.G) / dt) + 2):
            eb.friction_step(v, aw, dt)
            x[aw] += v[aw] * dt
        errs.append(abs(x[0, 0] - float(eb.stop_distance(v0))))
    assert errs[2] < 0.02 * float(eb.stop_distance(v0)) + 1e-3
    assert 1.6 < errs[0] / errs[1] < 2.4 and 1.6 < errs[1] / errs[2] < 2.4    # first order in dt


@pytest.mark.parametrize("seed", range(20))
def test_collisions_conserve_momentum_and_never_add_energy(seed: int) -> None:
    rng = np.random.default_rng(8200 + seed)
    x = rng.uniform(0, 1.0, (40, 2))
    v = rng.normal(0, 2.0, (40, 2))
    aw = np.ones(40, bool)
    p0, k0 = v.sum(0), (v ** 2).sum()
    eb.collide(x, v, aw)
    assert np.allclose(v.sum(0), p0, atol=1e-10)
    assert (v ** 2).sum() <= k0 * (1 + 1e-12)


def test_reach_rule_frees_only_bodies_that_cannot_meet() -> None:
    """Two bodies far apart are freed and land exactly at their stopping points; two bodies on a collision course
    are not freed."""
    x = np.array([[0.0, 0.0], [5.0, 0.0]])
    v = np.array([[1.0, 0.0], [0.0, 1.0]])
    free, spd, _ = eb.reach_free(x, v, np.ones(2, bool))
    assert sorted(free) == [0, 1]
    x2 = np.array([[0.0, 0.0], [0.5, 0.0]])
    v2 = np.array([[1.5, 0.0], [-1.5, 0.0]])
    free2, _, _ = eb.reach_free(x2, v2, np.ones(2, bool))
    assert free2 == []
