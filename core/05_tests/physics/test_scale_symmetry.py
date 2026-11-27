"""Wave S1: scale-invariant restriction of the parent action (core/03_lanes/scalar_tensor/uet_scale_symmetry.py).

1. Derivation check (independent route): the Theory Card integrand (_symbolic_geometry.parent_lagrangian_scalar,
   written from the card text) times sqrt(-g), with R and the gradients computed by sympy from a concrete metric,
   is unchanged under g -> s^-2 g, phi -> s phi, chi -> s chi at 20 random points once the terms the code forbids are
   switched off (rel < 1e-10).
2. Derivation check: each term of the card, switched on alone, picks up exactly the power of s that
   uet_scale_symmetry.scaling_exponent assigns to it (13 terms; the phi* != 0 cross term is covered by 1 failing
   when phi* != 0).
3. Identity (flat direction): in the scale-invariant restriction every psi0 is a static de Sitter solution of the
   general FRW equations (20 random points, residual < 1e-12); an explicit mass m^2 psi^2 / 2 breaks it (negative
   control).
4. Known limit: gamma - 1 of the C1 formula with F = xi psi^2 equals the Brans-Dicke value -1 / (omega + 2) with
   omega = 1 / (4 xi) at 20 random points (rel < 1e-12); the Cassini xi_max saturates the bound.
"""

from __future__ import annotations

import importlib
import math
import random

import pytest
import sympy as sp

from ._symbolic_geometry import COORDS, einstein_and_scalar, parent_lagrangian_scalar

pytestmark = pytest.mark.physics

m = importlib.import_module("core.03_lanes.scalar_tensor.uet_scale_symmetry")

T = COORDS[0]
S = sp.Symbol("s", positive=True)
T0 = 0.37


def _geometry():
    a = 1 + sp.Rational(3, 10) * T + sp.Rational(1, 10) * T**2
    N = 1 + sp.Rational(1, 5) * T
    g = sp.diag(-N**2, a**2, a**2, a**2)
    phi = sp.Rational(1, 2) + sp.Rational(2, 5) * T
    chi1, chi2 = sp.Rational(3, 10) - sp.Rational(1, 10) * T, sp.Rational(1, 5) * T
    out = {}
    for tag, gg, f, c1, c2 in (("1", g, phi, chi1, chi2), ("s", g / S**2, S * phi, S * chi1, S * chi2)):
        _, R, _, ginv = einstein_and_scalar(gg)
        sqrtg = sp.sqrt(-gg.det())
        out[tag] = dict(R=R, sqrtg=sqrtg, phi=f, chi_sq=c1**2 + c2**2,
                        gphi=ginv[0, 0] * sp.diff(f, T) ** 2,
                        gchi=ginv[0, 0] * (sp.diff(c1, T) ** 2 + sp.diff(c2, T) ** 2))
    return {k: {q: sp.lambdify(S, v.subs(T, T0), "mpmath") for q, v in d.items()} for k, d in out.items()}


GEO = _geometry()

ZERO = dict(epsilon=1.0, xi=0.0, phi_star=0.0, kappa=1.0, Lambda=0.0, k=0.0, rho_star=0.0, mu2=0.0,
            lambda_phi=0.0, Z=0.0, m2=0.0, lambda_chi=0.0, h=0.0)


def _density(tag: str, s: float, p: dict, drop_einstein_hilbert: bool) -> float:
    q = {k: float(v(s)) for k, v in GEO[tag].items()}
    L = parent_lagrangian_scalar(q["R"], q["phi"], q["gphi"], q["chi_sq"], q["gchi"], p)
    if drop_einstein_hilbert:
        L -= q["R"] / (2.0 * p["kappa"])          # the "1" in F = 1 + eps xi delta^2: forbidden, removed here
    return q["sqrtg"] * L


def test_scale_invariant_restriction_is_invariant():
    rng = random.Random(20261127)
    worst = 0.0
    for _ in range(20):
        p = dict(ZERO, epsilon=rng.uniform(0.1, 2.0), xi=rng.uniform(-1.0, 1.0), kappa=rng.uniform(0.5, 2.0),
                 k=rng.uniform(0.5, 2.0), lambda_phi=rng.uniform(0.0, 1.0), Z=rng.uniform(0.5, 2.0),
                 lambda_chi=rng.uniform(0.0, 1.0))
        s = rng.uniform(0.3, 3.0)
        a, b = _density("1", 1.0, p, True), _density("s", s, p, True)
        worst = max(worst, abs(b / a - 1.0))
    assert worst < 1e-10


TOGGLES = {
    "R / (2 kappa)": dict(),
    "eps xi phi^2 R / (2 kappa)  (phi* = 0)": dict(xi=0.7),
    "F Lambda / kappa": dict(Lambda=0.4),
    "eps k (grad phi)^2 / 2": dict(k=1.3),
    "eps rho*": dict(rho_star=0.9),
    "eps mu^2 phi^2 / 2": dict(mu2=1.1),
    "eps lambda_phi phi^4 / 4": dict(lambda_phi=0.6),
    "Z (grad chi)^2 / 2": dict(Z=1.2),
    "m^2 |chi|^2 / 2": dict(m2=0.8),
    "lambda_chi |chi|^4 / 4": dict(lambda_chi=0.5),
    "eps h phi |chi|^2 / 2  (portal)": dict(h=0.9),
}


def _term(tag, s, name):
    base = dict(ZERO)
    on = dict(ZERO, **TOGGLES[name])
    if name == "R / (2 kappa)":
        return _density(tag, s, base, False)
    return _density(tag, s, on, False) - _density(tag, s, base, False)


@pytest.mark.parametrize("name", list(TOGGLES))
def test_each_term_scales_as_assigned(name):
    entry = next(t for t in m.PARENT_TERMS if t[0] == name)
    expected = m.scaling_exponent(*entry[1:])
    for s in (0.5, 2.0, 3.7):
        ratio = _term("s", s, name) / _term("1", 1.0, name)
        assert abs(math.log(ratio) / math.log(s) - expected) < 1e-9


def test_cross_term_lambda_xi_scales_as_assigned():
    name = "eps xi phi^2 Lambda / kappa"
    entry = next(t for t in m.PARENT_TERMS if t[0] == name)
    for s in (0.5, 2.0):
        val = {}
        for tag, ss in (("1", 1.0), ("s", s)):
            f = lambda **kw: _density(tag, ss, dict(ZERO, **kw), False)
            val[tag] = f(xi=0.7, Lambda=0.4) - f(xi=0.7) - f(Lambda=0.4) + f()
        assert abs(math.log(val["s"] / val["1"]) / math.log(s) - m.scaling_exponent(*entry[1:])) < 1e-9


def test_phi_star_breaks_invariance():
    p = dict(ZERO, xi=0.7, phi_star=0.3, k=1.0)
    a, b = _density("1", 1.0, p, True), _density("s", 2.0, p, True)
    assert abs(b / a - 1.0) > 1e-3


def test_every_psi0_is_static_de_sitter():
    rng = random.Random(11)
    worst = 0.0
    for _ in range(20):
        md = m.SIModel(rng.uniform(1e-6, 1.0), rng.uniform(1e-3, 2.0))
        psi0 = rng.choice((-1, 1)) * rng.uniform(0.1, 10.0)
        worst = max(worst, *map(abs, m.static_de_sitter_residual(md, psi0)))
    assert worst < 1e-12


def test_mass_term_breaks_flat_direction():
    md = m.SIModel(1e-3, 0.3, m2=0.1)
    assert max(map(abs, m.static_de_sitter_residual(md, 0.7))) > 1e-4


def test_brans_dicke_gamma():
    rng = random.Random(5)
    worst = 0.0
    for _ in range(20):
        xi, psi = rng.uniform(1e-7, 5.0), rng.uniform(0.1, 10.0)
        omega = 1.0 / (4.0 * xi)
        worst = max(worst, abs(m.gamma_minus_1(xi, psi) / (-1.0 / (omega + 2.0)) - 1.0))
    assert worst < 1e-12
    assert abs(-m.gamma_minus_1(m.cassini_xi_max()) / m.CASSINI_GAMMA - 1.0) < 1e-12
