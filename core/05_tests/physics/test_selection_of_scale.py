"""Wave C1: selection by persistence and the scale of the parent action
(core/03_lanes/scalar_tensor/uet_selection_of_scale.py).

1. Identity (Little's law, the layer-3 law N = b tau): a stochastic birth-death simulation of three phases gives
   time-averaged fractions b_i tau_i / sum b_j tau_j within 0.02.
2. Identity (neutral selection): in the scale-invariant restriction every psi0 is static de Sitter (S1), so all
   values of the scale persist equally; checked at 20 random psi0 with one model (residual < 1e-12).
3. Derivation check (independent route): integrating the Jordan-frame equations of S1 plus the mass term gives
   d ln F / dN = 4 xi / (1 + 4 xi) on the attractor, the value derived from the Einstein-frame attractor and the
   frame change (rel < 1e-8, three values of xi).
"""

from __future__ import annotations

import importlib
import random

import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("core.03_lanes.scalar_tensor.uet_selection_of_scale")
s1 = m.s1


def test_littles_law_for_phases():
    b, tau = [1.0, 3.0, 0.5], [2.0, 0.4, 5.0]
    sim = m.simulate_phases(b, tau, t_end=20000.0, seed=3)
    for x, y in zip(sim, m.steady_state_fractions(b, tau)):
        assert abs(x - y) < 0.02


def test_flat_direction_is_neutral():
    rng = random.Random(9)
    md = s1.SIModel(0.05, 0.4)
    worst = 0.0
    for _ in range(20):
        worst = max(worst, *map(abs, s1.static_de_sitter_residual(md, rng.uniform(0.01, 100.0))))
    assert worst < 1e-12


@pytest.mark.parametrize("xi", [0.01, 0.05, 0.2])
def test_planck_mass_drift_on_attractor(xi):
    assert abs(m.jordan_drift_numeric(xi) / m.drift_rate(xi) - 1.0) < 1e-8
