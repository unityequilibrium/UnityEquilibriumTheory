"""Wave J1: the portal inside cosmology (core/03_lanes/scalar_tensor/uet_portal_cosmology.py).

1. Identity (Bianchi): with baryons of field-dependent mass, d rho_b/dt = -3 H rho_b + (d rho_b/d psi) psi' and the
   code's dH/dt and psi'' keep the Friedmann constraint at 20 random points (rel < 1e-10); dropping the portal
   force from the field equation breaks it (negative control).
2. Known limit through the general code path: with c = 0 the coupled integrator gives the same psi today as the C2
   integrator uet_frw_cmb.integrate (rel < 1e-12).
3. Linear response: for small c the change of 1 + w0 is linear in c (doubling c doubles it within 1e-3).
"""

from __future__ import annotations

import importlib
import random

import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("core.03_lanes.scalar_tensor.uet_portal_cosmology")
cmbm = m.cmbm


def _rate(cp, psi, pi, a, drop_force=False):
    md = cp.md
    H = float(m.hubble(cp, psi, pi, a))
    if drop_force:
        cp_nf = m.Coupled(md, cp.f_b, cp.c, cp.psi_ref)
        F, dF = md.F(psi), md.dF(psi)
        rho_m = (1.0 - cp.f_b) * a**-3 + cp.rho_b(a, psi)
        A0 = -3.0 * H * pi + 6.0 * dF * H * H - md.dW(psi)
        B0 = -rho_m - 4.0 / 3.0 * md.r * a**-4 - pi * pi - 2.0 * md.xi * pi * pi + H * dF * pi
        Hdot = (B0 - dF * A0) / (2.0 * F + 3.0 * dF * dF)
        acc = A0 + 3.0 * dF * Hdot
    else:
        Hdot, acc = m.accelerations(cp, psi, pi, a, H)
    F, dF, ddF = md.F(psi), md.dF(psi), 2.0 * md.xi
    rho_c, rho_b, rho_r = (1.0 - cp.f_b) * a**-3, cp.rho_b(a, psi), md.r * a**-4
    lhs = (3.0 * dF * pi * H * H + 6.0 * F * H * Hdot + 3.0 * ddF * pi * pi * H + 3.0 * dF * acc * H
           + 3.0 * dF * pi * Hdot)
    rhs = (-3.0 * H * rho_c - 3.0 * H * rho_b + cp.drho_b(a, psi) * pi - 4.0 * H * rho_r
           + pi * acc + md.dW(psi) * pi)
    scale = abs(6.0 * F * H * Hdot) + abs(3.0 * H * (rho_c + rho_b)) + abs(4.0 * H * rho_r)
    return abs(lhs - rhs) / scale


def test_constraint_preserved_with_portal():
    rng = random.Random(27)
    worst = 0.0
    for _ in range(20):
        md = cmbm.Model(rng.uniform(1.0, 3.0), rng.uniform(0.1, 4.0), rng.uniform(0.0, 0.5),
                        rng.uniform(-0.3, 0.3), rng.uniform(1e-4, 1.0))
        cp = m.Coupled(md, rng.uniform(0.05, 0.5), rng.uniform(0.01, 0.3), 0.0)
        psi, pi, a = rng.uniform(-1.0, 1.0), rng.uniform(-0.5, 0.5), rng.uniform(1e-3, 1.0)
        worst = max(worst, _rate(cp, psi, pi, a))
    assert worst < 1e-10


def test_dropping_portal_force_breaks_constraint():
    md = cmbm.Model(2.0, 1.0, 0.0, 0.1, 0.01)
    cp = m.Coupled(md, 0.3, 0.2, 0.0)
    assert _rate(cp, 0.5, 0.2, 0.5, drop_force=True) > 1e-4


def test_zero_portal_matches_c2_integrator():
    cp, psi_i = m.t041_coupled(0.0)
    psi, _ = m.integrate(cp, psi_i, steps=1500)
    ref = cmbm.integrate(cp.md, psi_i, steps=1500)[1][-1, 0]
    assert abs(psi / ref - 1.0) < 1e-12


def test_response_is_linear_in_c():
    cp0, psi_i = m.t041_coupled(0.0)
    w0 = m.one_plus_w0(cp0, psi_i, 1500)
    d1 = m.one_plus_w0(m.t041_coupled(1e-5)[0], psi_i, 1500) - w0
    d2 = m.one_plus_w0(m.t041_coupled(2e-5)[0], psi_i, 1500) - w0
    assert abs(d2 / d1 - 2.0) < 1e-3
