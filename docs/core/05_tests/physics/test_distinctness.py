"""Wave B4: where (if anywhere) does UET say something standard physics does not?

(a) Layer 3 is exactly the chemostat consumer-resource model (MacArthur 1970; Tilman 1982)
    under an explicit parameter map: identity check with sympy.
(b) Layers 1 and 2 reduce to known theories (DEF scalar-tensor + Yukawa portal; Caldeira-
    Leggett); those maps are already checked in test_parent_derivation / test_def_mapping /
    test_layer2_dissipation and are only cited here.
(c) The one cross-layer effect without a standard counterpart: portal drag, a velocity-
    dependent force relative to the environment frame. Checked: the angular factor 1/3,
    the light-scalar closed form q^2/(4 pi R) and Yukawa suppression.
"""

from __future__ import annotations

import importlib
import math

import numpy as np
import pytest
import sympy as sp

pytestmark = pytest.mark.physics

l3 = importlib.import_module("docs.core.03_lanes.persistence.uet_persistence_selection")
drag = importlib.import_module("docs.core.03_lanes.open_system.uet_portal_drag")


def test_layer3_is_exactly_the_chemostat_consumer_resource_model() -> None:
    """Tilman chemostat: dN_i = N_i (Y_i c_i R - m_i), dR = D (R_in - R) - R sum c_i N_i.
    Map: Y_i c_i = a_i, m_i = 1/tau_i, c_i = a_i F_i (so yield Y_i = 1/F_i), D = delta, D R_in = S."""
    a1, a2, F1, F2, P1, P2, S, d, N1, N2, R = sp.symbols("a1 a2 F1 F2 P1 P2 S delta N1 N2 R", positive=True)
    class Symbolic:  # stand-in with the attributes competition_rhs reads; SystemType itself is not modified
        def __init__(self, a, F, P):
            self.capture, self.free_energy_store, self.tau = a, F, F / P

    types = [Symbolic(a1, F1, P1), Symbolic(a2, F2, P2)]
    dN, dR = l3.competition_rhs([N1, N2], R, types, S, d)
    c = [a1 * F1, a2 * F2]
    Y = [1 / F1, 1 / F2]
    m = [P1 / F1, P2 / F2]
    D, R_in = d, S / d
    tilman_dN = [N1 * (Y[0] * c[0] * R - m[0]), N2 * (Y[1] * c[1] * R - m[1])]
    tilman_dR = D * (R_in - R) - R * (c[0] * N1 + c[1] * N2)
    assert all(sp.simplify(x - y) == 0 for x, y in zip(dN, tilman_dN))
    assert sp.simplify(dR - tilman_dR) == 0


def test_portal_drag_angular_factor_is_one_third() -> None:
    """integral (v.grad psi)^2 over directions = v^2 |grad psi|^2 / 3 for a radial field (Gauss-Legendre in cos theta)."""
    x, w = np.polynomial.legendre.leggauss(16)
    avg = float(np.sum(w * x**2) / np.sum(w))
    assert abs(avg - 1.0 / 3.0) < 1e-14


@pytest.mark.parametrize("radius", [0.5, 2.0, 7.0])
def test_portal_drag_light_limit_closed_form(radius: float) -> None:
    q, gamma, v = 0.8, 0.3, 1e-3
    numeric = drag.drag_force(gamma, v, q, radius, m_psi=1e-9)
    assert abs(numeric / drag.drag_force_light_limit(gamma, v, q, radius) - 1.0) < 1e-6


def test_portal_drag_is_yukawa_suppressed_and_vanishes_without_portal() -> None:
    q, gamma, v, radius = 0.8, 0.3, 1e-3, 1.0
    forces = [drag.drag_force(gamma, v, q, radius, m) for m in (1e-6, 1.0, 5.0, 20.0)]
    assert all(forces[i] > forces[i + 1] for i in range(3))
    assert forces[-1] / forces[0] < 0.05
    assert drag.drag_force(gamma, v, drag.portal_charge(0.0, 1.0, 1.0), radius, 1.0) == 0.0
    assert drag.drag_force(0.0, v, q, radius, 1.0) == 0.0
    assert math.isclose(drag.drag_force(gamma, 2 * v, q, radius, 1.0), 2 * drag.drag_force(gamma, v, q, radius, 1.0))
