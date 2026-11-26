"""Wave C2: the parent action's FRW background with radiation and the CMB acoustic angle
(core/03_lanes/scalar_tensor/uet_frw_cmb.py).

1. Identity (Bianchi): along the code's dH/dt and psi'', with rho_m' = -3 H rho_m and rho_r' = -4 H rho_r, the time
   derivative of the constraint 3 F H^2 + 3 F' pi H - (rho_m + rho_r + pi^2/2 + W) vanishes at 20 random
   off-equilibrium points with xi != 0 (rel < 1e-10); giving radiation the pressure of dust breaks it (negative control).
2. Known limit through the general code path: psi_i = 0 runs the ODE, calibration and Simpson grid, and its theta*
   equals LambdaCDM theta* from an independent Gauss-Legendre quadrature in a (rel < 1e-9).
3. Identity: with xi = 0 the late-time w(a) does not depend on when the frozen field is released (z = 1e6 here, z = 99
   in C1) beyond 1e-3 in w0 and wa, because a minimally coupled field at rest stays at rest under Hubble friction.
4. Convergence: the RK4 value of psi today (xi != 0, psi oscillating) converges with order 4 on 3 grids.
"""

from __future__ import annotations

import importlib
import math
import random

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("core.03_lanes.scalar_tensor.uet_frw_cmb")
c1 = importlib.import_module("core.03_lanes.scalar_tensor.uet_frw_background")

OB, OM = 0.02237, 0.14237


def _constraint_rate(md, psi, pi, a, radiation_pressure=4.0 / 3.0):
    H = float(m.hubble(md, psi, pi, a))
    rho_m, rho_r = a**-3, md.r * a**-4
    if radiation_pressure == 4.0 / 3.0:
        Hdot, acc = m.accelerations(md, psi, pi, a, H)
    else:  # same equations with radiation given the pressure of dust
        F, dF = md.F(psi), md.dF(psi)
        A0 = -3.0 * H * pi + 6.0 * dF * H * H - md.dW(psi)
        B0 = -rho_m - radiation_pressure * rho_r - pi * pi - 2.0 * md.xi * pi * pi + H * dF * pi
        Hdot = (B0 - dF * A0) / (2.0 * F + 3.0 * dF * dF)
        acc = A0 + 3.0 * dF * Hdot
    F, dF, ddF = md.F(psi), md.dF(psi), 2.0 * md.xi
    lhs = (3.0 * dF * pi * H * H + 6.0 * F * H * Hdot + 3.0 * ddF * pi * pi * H + 3.0 * dF * acc * H
           + 3.0 * dF * pi * Hdot)
    rhs = -3.0 * H * rho_m - 4.0 * H * rho_r + pi * acc + md.dW(psi) * pi
    scale = abs(6.0 * F * H * Hdot) + abs(3.0 * H * rho_m) + abs(4.0 * H * rho_r)
    return abs(lhs - rhs) / scale


def test_constraint_preserved_with_radiation():
    rng = random.Random(20261126)
    worst = 0.0
    for _ in range(20):
        md = m.Model(rng.uniform(1.0, 3.0), rng.uniform(0.1, 4.0), rng.uniform(0.0, 0.5), rng.uniform(-0.3, 0.3),
                     rng.uniform(1e-4, 1.0))
        psi, pi, a = rng.uniform(-1.0, 1.0), rng.uniform(-0.5, 0.5), rng.uniform(1e-3, 1.0)
        worst = max(worst, _constraint_rate(md, psi, pi, a))
    assert worst < 1e-10


def test_negative_control_radiation_as_dust():
    md = m.Model(2.0, 1.0, 0.1, 0.2, 0.5)
    assert _constraint_rate(md, 0.4, 0.2, 0.05, radiation_pressure=1.0) > 1e-3


@pytest.mark.parametrize("Om", [0.28, 0.315, 0.34])
def test_lcdm_limit_through_general_path(Om):
    md, rn = m.calibrated(1.0, 0.0, 0.0, Om, m.r_ratio(OM))
    assert abs(rn.omega_m0 - Om) < 1e-10
    ang = m.cmb_angle(md, rn, OB, OM)
    assert abs(ang.theta_star / m.theta_lcdm(OB, OM, Om) - 1.0) < 1e-9
    assert ang.G_star_over_G0 == 1.0


def _late_cpl(md, rn):
    sel = rn.N >= math.log(0.4)
    a, psi, pi, H = np.exp(rn.N[sel]), rn.psi[sel], rn.pi[sel], rn.H[sel]
    F0 = float(md.F(rn.psi[-1]))
    Hdot, _ = m.accelerations(md, psi, pi, a, H)
    rho_de = 3.0 * F0 * H**2 - a**-3 - md.r * a**-4
    p_de = -2.0 * F0 * Hdot - a**-3 - 4.0 / 3.0 * md.r * a**-4 - rho_de
    A = np.column_stack([np.ones(sel.sum()), 1.0 - a])
    (w0, wa), *_ = np.linalg.lstsq(A, p_de / rho_de, rcond=None)
    return float(w0), float(wa)


@pytest.mark.parametrize("psi_i,m_h", [(0.6, 2.0), (1.0, 1.0)])
def test_minimal_coupling_release_time_irrelevant(psi_i, m_h):
    md, rn = m.calibrated(m_h, 0.0, psi_i, 0.30, m.r_ratio(OM))
    w0, wa = _late_cpl(md, rn)
    _, h = c1.calibrated(m_h, 0.0, psi_i, omega_m0=0.30, steps=1500)
    w0_c1, wa_c1 = c1.cpl_fit(h)
    assert abs(w0 - w0_c1) < 1e-3 and abs(wa - wa_c1) < 1e-3


def test_rk4_order_four():
    md = m.Model(2.0, 20.0, 0.0, 0.02, m.r_ratio(OM))   # heavy enough that psi oscillates before today
    ref = m.integrate(md, 1.0, steps=12800)[1][-1, 0]
    e = [abs(m.integrate(md, 1.0, steps=s)[1][-1, 0] - ref) for s in (200, 400, 800)]
    for coarse, fine in zip(e, e[1:]):
        assert 3.7 < math.log2(coarse / fine) < 4.3
