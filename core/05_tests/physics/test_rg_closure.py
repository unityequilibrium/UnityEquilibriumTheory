"""Wave B1: RG closure of the parent action (core/03_lanes/scalar_tensor/uet_rg_closure.py).

1. Identity (Weyl covariance, independent sympy geometry): for a metric g and Omega(t, x), the operator
   box - R/6 satisfies (box' - R'/6)(Omega^-1 phi) = Omega^-3 (box - R/6) phi with g' = Omega^2 g, at 20 random
   points (rel < 1e-10); with xi = 0.2 instead of 1/6 the identity fails (negative control). This is why xi = 1/6
   is the fixed point of beta_xi.
2. Known limits of the flow: beta_xi vanishes at xi = 1/6 for any lambda and N; for N = 1 the coefficients reduce to
   the single-scalar values 9 lambda^2 / (8 pi^2) and 3 lambda (xi - 1/6) / (8 pi^2); for chi (N = 2) the value at
   xi_chi = 0 equals -lambda_chi / (12 pi^2).
3. Integration check: integrating beta_lambda from lambda_0 over t = ln(mu / mu_0) reproduces the closed one-loop
   solution lambda_0 / (1 - b lambda_0 t) with b = (N + 8) / (8 pi^2) (rel < 1e-10), so the flow code is consistent.
"""

from __future__ import annotations

import importlib
import math
import random

import pytest
import sympy as sp

from ._symbolic_geometry import COORDS, box, einstein_and_scalar

pytestmark = pytest.mark.physics

m = importlib.import_module("core.03_lanes.scalar_tensor.uet_rg_closure")

T, X = COORDS[0], COORDS[1]


def _weyl_operator_pair(xi):
    a = 1 + sp.Rational(3, 10) * T + sp.Rational(1, 10) * T**2 + sp.Rational(1, 20) * X
    g = sp.diag(-1, a**2, a**2, a**2)
    Om = 1 + sp.Rational(1, 5) * T + sp.Rational(1, 7) * X * T
    phi = sp.Rational(1, 2) + sp.Rational(2, 5) * T + sp.Rational(1, 3) * X**2
    _, R, _, ginv = einstein_and_scalar(g)
    gp = Om**2 * g
    _, Rp, _, ginvp = einstein_and_scalar(gp)
    lhs = box(phi / Om, gp, ginvp) - xi * Rp * phi / Om
    rhs = Om**-3 * (box(phi, g, ginv) - xi * R * phi)
    return sp.lambdify((T, X), lhs, "mpmath"), sp.lambdify((T, X), rhs, "mpmath")


def test_conformal_coupling_is_weyl_covariant():
    lhs, rhs = _weyl_operator_pair(sp.Rational(1, 6))
    rng = random.Random(6)
    worst = 0.0
    for _ in range(20):
        t, x = rng.uniform(0.0, 1.0), rng.uniform(0.0, 1.0)
        a, b = float(lhs(t, x)), float(rhs(t, x))
        worst = max(worst, abs(a - b) / max(abs(b), 1e-30))
    assert worst < 1e-10


def test_non_conformal_coupling_breaks_weyl_covariance():
    lhs, rhs = _weyl_operator_pair(sp.Rational(1, 5))
    a, b = float(lhs(0.4, 0.3)), float(rhs(0.4, 0.3))
    assert abs(a - b) / abs(b) > 1e-3


def test_flow_limits():
    rng = random.Random(2)
    for _ in range(20):
        lam, N = rng.uniform(0.0, 2.0), rng.choice((1, 2, 3, 4))
        assert m.beta_xi(lam, 1.0 / 6.0, N) == pytest.approx(0.0, abs=1e-15)
        xi = rng.uniform(-1.0, 1.0)
        assert m.beta_lambda(lam, 1) == pytest.approx(9.0 * lam**2 / (8.0 * math.pi**2), rel=1e-14)
        assert m.beta_xi(lam, xi, 1) == pytest.approx(3.0 * lam * (xi - 1.0 / 6.0) / (8.0 * math.pi**2), rel=1e-14)
    assert m.generated_xi_chi_rate(0.7) == pytest.approx(-0.7 / (12.0 * math.pi**2), rel=1e-14)


@pytest.mark.parametrize("N", [1, 2])
def test_one_loop_flow_integrates_to_closed_form(N):
    lam0, t_end, steps = 0.3, 5.0, 2000
    h = t_end / steps
    lam = lam0
    for _ in range(steps):
        k1 = m.beta_lambda(lam, N); k2 = m.beta_lambda(lam + h / 2 * k1, N)
        k3 = m.beta_lambda(lam + h / 2 * k2, N); k4 = m.beta_lambda(lam + h * k3, N)
        lam += h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    b = (N + 8) / (8.0 * math.pi**2)
    assert abs(lam / (lam0 / (1.0 - b * lam0 * t_end)) - 1.0) < 1e-10
