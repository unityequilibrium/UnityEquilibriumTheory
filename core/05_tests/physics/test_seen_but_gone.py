"""Wave S2: of the sources we see, what fraction is still alive now?

(a) Derivation check: the numerically averaged alive probability equals the closed form A_D(lambda)
    at 24 random (d, c, tau, D) on both branches, rel < 1e-10.
(b) Known limits through the general path: lambda -> 0 gives A -> 1 with slope -D/(D+1); the two
    branches meet at lambda = 1 with value 1/(D+1) and the same slope.
(c) Scaling identity: lambda ~ eps^(1/2) P^(3/2) / F from the general depth_ratio path.
(d) Second route (space-time Monte Carlo, seeded): births in space and time, seen if alive when the
    light left; the seen count equals n V d^D (delay does not change how many) and the alive
    fraction matches A_D within Poisson errors, on both branches.
"""

from __future__ import annotations

import importlib
from math import gamma, log, pi, sqrt

import numpy as np
import pytest

pytestmark = pytest.mark.physics

sg = importlib.import_module("docs.core.03_lanes.persistence.uet_seen_but_gone")


@pytest.mark.parametrize("seed", range(24))
def test_numeric_alive_fraction_matches_closed_form(seed: int) -> None:
    rng = np.random.default_rng(16000 + seed)
    D = 1 + seed % 3
    c = 10 ** rng.uniform(-1, 1)
    tau = 10 ** rng.uniform(-1, 2)
    lam = 10 ** rng.uniform(-1.5, 1.5)
    d = lam * c * tau
    numeric = sg.alive_fraction_numeric(d, c, tau, D)
    exact = sg.alive_fraction_closed_form(lam, D)
    assert abs(numeric / exact - 1.0) < 1e-10


@pytest.mark.parametrize("D", [1, 2, 3])
def test_limits_and_branch_matching(D: int) -> None:
    c, tau = 1.0, 1.0
    # small lambda: A -> 1 and (1 - A)/lambda -> D/(D+1)
    for lam in (1e-3, 1e-5):
        A = sg.alive_fraction_numeric(lam, c, tau, D)
        assert abs((1.0 - A) / lam - D / (D + 1.0)) < 1e-8
    # at lambda = 1 both sides give 1/(D+1); one-sided slopes agree
    h = 1e-6
    below = sg.alive_fraction_numeric(1.0 - h, c, tau, D)
    above = sg.alive_fraction_numeric(1.0 + h, c, tau, D)
    at = sg.alive_fraction_numeric(1.0, c, tau, D)
    assert abs(at * (D + 1.0) - 1.0) < 1e-12
    slope_l = (at - below) / h
    slope_r = (above - at) / h
    for s in (slope_l, slope_r):
        assert abs(s + D / (D + 1.0)) < 1e-4


def test_depth_ratio_scales_as_eps_half_P_three_halves_over_F() -> None:
    f, c = 1e-3, 3.0
    base = sg.depth_ratio(1.0, 1.0, 0.5, f, c)
    for P, F, eps in [(10.0, 1.0, 0.5), (1.0, 7.0, 0.5), (1.0, 1.0, 0.05), (100.0, 3.0, 0.2)]:
        ratio = sg.depth_ratio(P, F, eps, f, c) / base
        expected = (eps / 0.5) ** 0.5 * P ** 1.5 / F
        assert abs(ratio / expected - 1.0) < 1e-12
    # the S1 pair: a 100 times faster burner has 1000 times the lambda
    assert abs(log(sg.depth_ratio(100.0, 1.0, 1.0, f, c) / sg.depth_ratio(1.0, 1.0, 1.0, f, c))
               / log(1000.0) - 1.0) < 1e-12


@pytest.mark.parametrize("lam,seed", [(0.5, 11), (3.0, 12)])
def test_light_cone_monte_carlo(lam: float, seed: int) -> None:
    rng = np.random.default_rng(seed)
    D, c, tau, b = 3, 1.0, 1.0, 4000.0
    d = lam * c * tau
    R = d
    T = tau + R / c + 1.0           # every source that could be seen was born inside [-T, 0]
    seen, alive = sg.simulate_light_cone(b, tau, c, d, D, R, T, rng)
    V_d = pi ** 1.5 / gamma(2.5) * d ** 3
    expected_seen = b * tau * V_d   # steady density n = b tau times surveyed volume
    assert abs(seen - expected_seen) < 5.0 * sqrt(expected_seen)
    A = sg.alive_fraction_closed_form(lam, D)
    p = alive / seen
    assert abs(p - A) < 5.0 * sqrt(A * (1.0 - A) / seen)
