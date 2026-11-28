"""Wave D1: attractors and the initial-condition dependence of the parent action
(core/03_lanes/scalar_tensor/uet_attractor.py).

1. Scaling law through the general code path: the card's thawing field (C2 code, xi_c = 0) gives
   1 + w0 proportional to psi_i^2 between psi_i = 0.01 and 0.08 (exponent 2 within 1e-3).
2. Derivation check (independent route): the Einstein-frame slope -d ln V_E / d sigma, with sigma(psi) integrated
   numerically from the general frame-change formula, equals lambda_E = 2 sqrt(xi / (1 + 6 xi)) at 20 random
   points (rel < 1e-8).
3. Known limit: exponential quintessence with dust reaches w = -1 + lambda^2 / 3 and Omega_phi = 1 from three
   different initial conditions (|dw| < 1e-6) for lambda^2 < 2 (Copeland, Liddle & Wands 1998).
4. Known limit: for lambda^2 > 3 the same code gives the scaling solution Omega_phi = 3 / lambda^2 (|d| < 1e-6).
"""

from __future__ import annotations

import importlib
import math
import random

import pytest
from scipy.integrate import quad

pytestmark = pytest.mark.physics

m = importlib.import_module("core.03_lanes.scalar_tensor.uet_attractor")


def test_thawing_one_plus_w0_scales_as_psi_i_squared():
    w = [m.thawing_one_plus_w0(p) for p in (0.01, 0.02, 0.04, 0.08)]
    for lo, hi in zip(w, w[1:]):
        assert abs(math.log2(hi / lo) - 2.0) < 1e-3


def test_einstein_frame_slope_matches_lambda_E():
    rng = random.Random(42)
    worst = 0.0
    for _ in range(20):
        xi, m2 = rng.uniform(1e-4, 1.0), rng.uniform(0.1, 5.0)
        p1 = rng.uniform(0.2, 3.0)
        p2 = p1 * rng.uniform(1.2, 3.0)
        F = lambda x: xi * x * x
        dF = lambda x: 2.0 * xi * x
        dsig, _ = quad(lambda x: m.dsigma_dpsi_general(F, dF, x), p1, p2, epsabs=0.0, epsrel=1e-13)
        slope = -(math.log(m.V_E(xi, m2, p2)) - math.log(m.V_E(xi, m2, p1))) / dsig
        worst = max(worst, abs(slope / m.lambda_E(xi) - 1.0))
    assert worst < 1e-8


@pytest.mark.parametrize("lam", [0.3, 0.8, 1.2])
def test_attractor_is_independent_of_initial_conditions(lam):
    ws = []
    for x0, y0 in ((1e-3, 1e-3), (0.5, 0.1), (-0.3, 0.6)):
        w, om = m.exponential_quintessence(lam, x0, y0, N=60.0, steps=12000)
        assert abs(om - 1.0) < 1e-6
        ws.append(w)
    for w in ws:
        assert abs(w - m.w_attractor(lam)) < 1e-6


def test_scaling_solution_for_steep_exponential():
    lam = 2.5
    _, om = m.exponential_quintessence(lam, 0.1, 0.1, N=80.0, steps=16000)
    assert abs(om - 3.0 / lam**2) < 1e-6
