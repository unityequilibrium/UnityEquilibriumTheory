"""Wave C3: growth of matter perturbations in the parent action (core/03_lanes/scalar_tensor/uet_frw_growth.py).

1. Derivation check (independent route): solving the three quasi-static equations as a linear system gives
   (k/a)^2 Phi = -X g / 2 with the closed form g = (2F + 4F'^2) / (F (2F + 3F'^2)) at 20 random points (rel < 1e-12),
   and Psi / Phi equals the PPN gamma that C1 uses for the Cassini bound.
2. Known limit: with F'^2 = F / omega the closed form is the Brans-Dicke result G_eff = (2 omega + 4) / ((2 omega + 3) F)
   at 20 random points (rel < 1e-12).
3. Known limit through the general code path: psi_i = 0 and no radiation is LambdaCDM, and the RK4 growth factor
   D(1) / D(0.5) equals the Heath (1977) integral (rel < 1e-9) for three values of Omega_m.
4. Known limit through the general code path: with radiation and psi_i = 0, D at a = 1e-3 equals the Meszaros
   growing mode r + 3a/2 (rel < 1e-8; Lambda contributes about 2e-10 there).
5. Convergence: the RK4 growth factor today (xi != 0, psi oscillating) converges with order 4 on 3 grids.
"""

from __future__ import annotations

import importlib
import math
import random

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("core.03_lanes.scalar_tensor.uet_frw_growth")
cmbm = m.cmbm


def test_quasi_static_system_matches_closed_form():
    rng = random.Random(20261126)
    worst_phi = worst_gamma = 0.0
    for _ in range(20):
        F, dF = rng.uniform(0.3, 3.0), rng.uniform(-2.0, 2.0)
        X, k2 = rng.uniform(0.1, 10.0), rng.uniform(0.1, 100.0)
        Phi, Psi, _ = m.quasi_static(F, dF, X, k2)
        worst_phi = max(worst_phi, abs(k2 * Phi / (-0.5 * X * m.g_eff(F, dF)) - 1.0))
        gamma = 1.0 - dF * dF / (F + 2.0 * dF * dF)          # C1 / C2: gamma - 1 = -F'^2 / (F + 2 F'^2)
        worst_gamma = max(worst_gamma, abs(Psi / Phi / gamma - 1.0))
    assert worst_phi < 1e-12
    assert worst_gamma < 1e-12


def test_brans_dicke_limit():
    rng = random.Random(7)
    worst = 0.0
    for _ in range(20):
        F, omega = rng.uniform(0.3, 3.0), rng.uniform(0.5, 5.0e4)
        g = m.g_eff(F, math.sqrt(F / omega))
        worst = max(worst, abs(g / ((2.0 * omega + 4.0) / ((2.0 * omega + 3.0) * F)) - 1.0))
    assert worst < 1e-12


@pytest.mark.parametrize("Om", [0.25, 0.30, 0.35])
def test_lcdm_growth_equals_heath_integral(Om):
    md = cmbm.Model(3.0 / (3.0 * Om) * (1.0 - Om), 0.0, 0.0, 0.0, 0.0)
    gr = m.integrate(md, 0.0, steps=6000)
    i = int(np.searchsorted(gr.N, math.log(0.5)))
    a_i = math.exp(gr.N[i])
    ratio = gr.D[-1] / gr.D[i]
    assert abs(ratio / (m.heath_lcdm(1.0, Om) / m.heath_lcdm(a_i, Om)) - 1.0) < 1e-9


def test_meszaros_growing_mode_with_radiation():
    r = cmbm.r_ratio(0.14237)
    Om = 0.30
    md = cmbm.Model(1.0 / Om * (1.0 - Om) - r, 0.0, 0.0, 0.0, r)
    gr = m.integrate(md, 0.0, steps=6000)
    i = int(np.searchsorted(gr.N, math.log(1.0e-3)))
    a_i = math.exp(gr.N[i])
    assert abs(gr.D[i] / (r + 1.5 * a_i) - 1.0) < 1e-8


def test_rk4_order_four_growth():
    md = cmbm.Model(2.0, 20.0, 0.0, 0.02, cmbm.r_ratio(0.14237))   # psi oscillates before today
    ref = m.integrate(md, 1.0, steps=12800).D[-1]
    e = [abs(m.integrate(md, 1.0, steps=s).D[-1] - ref) for s in (200, 400, 800)]
    for coarse, fine in zip(e, e[1:]):
        assert 3.7 < math.log2(coarse / fine) < 4.3
