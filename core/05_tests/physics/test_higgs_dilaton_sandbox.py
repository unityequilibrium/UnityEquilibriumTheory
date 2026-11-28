"""Wave A2 sandbox (core/03_lanes/scalar_tensor/uet_higgs_dilaton_sandbox.py).

1. Identity: |chi0|^2 = (alpha / lambda_chi) psi0^2 is a stationary point of V (both gradients vanish, beta = 0)
   at 20 random points (central differences, < 1e-8 of the gradient scale).
2. Derivation check (independent route): the numerical second derivative of V along chi at the vacuum equals
   2 alpha psi0^2 at 20 random points (rel < 1e-5), so m_chi^2 / M_Pl^2 = 2 alpha / (xi_psi + xi_chi alpha / lambda_chi).
3. Identity (flat dilaton direction): the Einstein-frame potential V / F^2 is unchanged under (psi, chi) -> s (psi, chi)
   at 20 random points (rel < 1e-12); the card's trilinear portal breaks it (negative control).
"""

from __future__ import annotations

import importlib
import math
import random

import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("core.03_lanes.scalar_tensor.uet_higgs_dilaton_sandbox")


def _rand(rng, **kw):
    base = dict(xi_psi=rng.uniform(0.01, 2.0), xi_chi=rng.uniform(-1.0, 1.0), lam_chi=rng.uniform(0.1, 2.0),
                alpha=rng.uniform(1e-3, 1.0))
    base.update(kw)
    return m.Sandbox(**base)


def test_vacuum_is_stationary():
    rng = random.Random(1)
    worst = 0.0
    for _ in range(20):
        sb = _rand(rng)
        psi0 = rng.uniform(0.2, 5.0)
        X0 = m.vacuum_X(sb, psi0)
        h = 1e-6
        dpsi = (sb.V(psi0 + h, X0) - sb.V(psi0 - h, X0)) / (2 * h)
        dX = (sb.V(psi0, X0 + h) - sb.V(psi0, X0 - h)) / (2 * h)
        scale = sb.alpha * psi0**3 + 1.0
        worst = max(worst, abs(dpsi) / scale, abs(dX) / scale)
    assert worst < 1e-8


def test_chi_mass_matches_closed_form():
    rng = random.Random(2)
    worst = 0.0
    for _ in range(20):
        sb = _rand(rng)
        psi0 = rng.uniform(0.5, 3.0)
        worst = max(worst, abs(m.chi_mass2_numeric(sb, psi0) / (2.0 * sb.alpha * psi0**2) - 1.0))
    assert worst < 1e-5
    sb = m.Sandbox(1.0, 0.0, 1.0, 0.3)
    assert m.mass_ratio2(sb) == pytest.approx(2.0 * 0.3 * 1.0**2 / (1.0 * 1.0**2), rel=1e-14)


def test_einstein_frame_potential_is_scale_free():
    rng = random.Random(3)
    worst = 0.0
    for _ in range(20):
        sb = _rand(rng, beta=rng.uniform(0.0, 0.5), xi_chi=rng.uniform(0.0, 1.0))
        psi, X, s = rng.uniform(0.2, 3.0), rng.uniform(0.0, 4.0), rng.uniform(0.2, 5.0)
        worst = max(worst, abs(sb.V_E(s * psi, s * s * X) / sb.V_E(psi, X) - 1.0))
    assert worst < 1e-12


def test_trilinear_portal_breaks_scale_freedom():
    sb = m.Sandbox(0.5, 0.2, 1.0, 0.3, g_c=0.4)
    assert abs(sb.V_E(2.0 * 1.3, 4.0 * 0.7) / sb.V_E(1.3, 0.7) - 1.0) > 1e-3
