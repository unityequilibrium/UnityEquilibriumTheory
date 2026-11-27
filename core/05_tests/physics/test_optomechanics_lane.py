"""Wave O8: optomechanics lane for the layer 1 -> 2 -> 3 chain (core/03_lanes/optomechanics/uet_optomechanics_lane.py).

1. Derivation check (independent route): the exact linear stability of the coupled light-mechanics equations gives a
   mechanical damping whose optical part equals the weak-coupling Gamma_opt (the layer-2/3 rate) within 1 percent at
   four detunings (g / kappa ~ 0.01).
2. Independent route: integrating the full nonlinear classical equations after a small kick gives the same decay rate
   as the exact linear stability (rel < 1e-3) on the red and the blue side.
3. Identity (single coupling across layers): Gamma_opt(-Delta) = -Gamma_opt(+Delta) at 20 random points
   (rel < 1e-12), so the threshold computed from the red-side cooling rate equals the layer-3 threshold R* = 1/(a tau).
4. Layer-3 threshold: with blue detuning the exact linear rate is positive (the mode decays) at 0.8 n* and
   negative (the mode grows) at 1.2 n*.
"""

from __future__ import annotations

import importlib
import math
import random

import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("core.03_lanes.optomechanics.uet_optomechanics_lane")
OM = m.OM(Omega=1.0, kappa=0.5, Gamma_m=1e-3, g0=1e-3)


@pytest.mark.parametrize("D0", [-1.0, -0.6, 0.6, 1.0])
def test_exact_linear_matches_backaction_formula(D0):
    rate, D, n = m.linear_rates(OM, D0, 5.0)
    assert abs((rate - OM.Gamma_m) / m.gamma_opt(OM, n, D) - 1.0) < 1e-2


@pytest.mark.parametrize("D0", [-1.0, 1.0])
def test_nonlinear_time_domain_matches_linear(D0):
    rate, _, _ = m.linear_rates(OM, D0, 5.0)
    assert abs(m.time_domain_rate(OM, D0, 5.0, 3000.0) / rate - 1.0) < 1e-3


def test_red_blue_antisymmetry_and_cross_layer_threshold():
    rng = random.Random(8)
    worst = 0.0
    for _ in range(20):
        om = m.OM(rng.uniform(0.5, 2.0), rng.uniform(0.1, 3.0), rng.uniform(1e-4, 1e-2), rng.uniform(1e-4, 1e-2))
        D, n = rng.uniform(0.1, 3.0), rng.uniform(1.0, 1e4)
        worst = max(worst, abs(m.gamma_opt(om, n, -D) / -m.gamma_opt(om, n, D) - 1.0))
        worst = max(worst, abs(m.threshold_from_cooling(om, D, n) / m.threshold_photons(om, D) - 1.0))
    assert worst < 1e-12


def test_threshold_separates_decay_from_growth():
    n_star = m.threshold_photons(OM, 1.0)
    for frac, sign in ((0.8, 1.0), (1.2, -1.0)):
        E = math.sqrt(frac * n_star) * math.hypot(OM.kappa / 2, 1.0)   # n ~ E^2 / (kappa^2/4 + Delta^2)
        rate, D, n = m.linear_rates(OM, 1.0, E)
        assert sign * rate > 0
