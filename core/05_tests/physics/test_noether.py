"""Noether coverage of the parent action (wave N1, core/03_lanes/symmetry/uet_noether.py).

1. O(2), first theorem: the implemented current N^mu equals Z(chi_1 d^mu chi_2 - chi_2 d^mu chi_1) built by sympy,
   and its divergence equals chi_1 E_2 - chi_2 E_1 with E_A from the implemented matter residual, portal on,
   at 20 random off-shell points in flat 3+1 (rel < 1e-10).
2. Diffeomorphisms, second theorem: in a Bianchi I universe the Euler-Lagrange expressions of the Theory Card
   action obey N d/dt E_N = sum_q E_q dq/dt off shell at 20 random points; a term that breaks time
   reparametrization makes the identity fail (negative control).
3. Translations and boosts, first theorem: on a 1+1 lattice the O(2) charge is conserved to rounding, and the
   drifts of E, P and the boost charge K converge to zero with order 2 in dx (3 grids); with a different light
   cone for phi, K is not conserved (negative control).
5. Second theorem on a general metric: on an inhomogeneous, non-diagonal metric the implemented metric residual
   equals the Theory Card form and nabla^mu E_mu_nu = -kappa (E_phi d_nu phi + sum_A E_A d_nu chi_A) with the
   implemented residuals at 20 random off-shell points (4 draws x 5 points, rel < 1e-10), and again on a metric
   whose every entry depends on t, x, y and z (2 draws x 10 points); leaving the portal out of the stress breaks
   it (negative control).
4. Rotations, first theorem: on a 2+1 lattice angular momentum, energy and both momenta converge with order 2 in dx
   and the O(2) charge is conserved to rounding.
"""

from __future__ import annotations

import dataclasses
import importlib
import math
import random

import numpy as np
import pytest
import sympy as sp
from sympy.calculus.euler import euler_equations

from ._symbolic_geometry import COORDS, T, X, Y, ZC, derivative_values, einstein_and_scalar, parent_lagrangian_scalar
from .test_parent_derivation import configs, random_params, rel_diff

pytestmark = pytest.mark.physics

m = importlib.import_module("core.03_lanes.symmetry.uet_noether")
cov = m.cov

ETA = sp.diag(-1, 1, 1, 1)


def _poly(rng: random.Random, c0: float, s: float):
    terms = [c0] + [rng.uniform(-s, s) * v for v in COORDS] + [rng.uniform(-s, s) * a * b for a in COORDS for b in COORDS]
    return sum(terms) + rng.uniform(-s, s) * T * X * Y


@pytest.mark.parametrize("seed", range(20))
def test_o2_current_and_its_divergence_with_the_portal_on(seed: int) -> None:
    rng = random.Random(4000 + seed)
    p = random_params(rng)
    p["h"] = rng.uniform(0.3, 1.5)
    response, matter = configs(p)
    chi = [_poly(rng, 0.3, 0.4), _poly(rng, -0.2, 0.4)]
    phi = _poly(rng, p["phi_star"], 0.4)
    point = {v: rng.uniform(-0.5, 0.5) for v in COORDS}
    up = lambda f: [sum(ETA[mu, nu] * sp.diff(f, COORDS[nu]) for nu in range(4)) for mu in range(4)]  # noqa: E731
    N_sym = [p["Z"] * (chi[0] * a - chi[1] * b) for a, b in zip(up(chi[1]), up(chi[0]))]
    div_sym = sum(sp.diff(N_sym[mu], COORDS[mu]) for mu in range(4))
    ev = lambda e: float(sp.N(sp.sympify(e).subs(point), 40))  # noqa: E731

    fields = np.array([ev(c) for c in chi])
    grads = np.array([[ev(sp.diff(c, v)) for v in COORDS] for c in chi])
    code_N = cov.matter_noether_current(np.diag([-1.0, 1, 1, 1]), fields, grads, matter)
    for mu in range(4):
        assert rel_diff(code_N[mu], ev(N_sym[mu])) < 1e-10

    box = np.array([ev(sum(ETA[a, a] * sp.diff(c, v, 2) for a, v in enumerate(COORDS))) for c in chi])
    E = cov.matter_eom_residual(box, fields, ev(phi), response, matter)
    identity = cov.matter_current_divergence_from_eom(E, fields)
    assert abs(identity) > 1e-6  # off shell: the check is not 0 == 0
    assert rel_diff(ev(div_sym), identity) < 1e-10


_N, _A, _B, _C = (sp.Function(n)(T) for n in ("N", "a", "b", "c"))
_PHI, _CH1, _CH2 = (sp.Function(n)(T) for n in ("phi_t", "chi1_t", "chi2_t"))
_Q = [_A, _B, _C, _PHI, _CH1, _CH2]
_PSYM = {k: sp.Symbol(k) for k in ("epsilon", "kappa", "Lambda", "phi_star", "k", "mu2", "lambda_phi",
                                   "xi", "rho_star", "Z", "m2", "lambda_chi", "h")}
_BREAK = sp.Symbol("break")


@pytest.fixture(scope="module")
def minisuperspace():
    g = sp.diag(-_N**2, _A**2, _B**2, _C**2)
    _, R, _, ginv = einstein_and_scalar(g)
    root = _N * _A * _B * _C
    dphi = sp.diff(_PHI, T)
    L = root * parent_lagrangian_scalar(
        R, _PHI, ginv[0, 0] * dphi**2, _CH1**2 + _CH2**2,
        ginv[0, 0] * (sp.diff(_CH1, T) ** 2 + sp.diff(_CH2, T) ** 2), _PSYM)
    L = L + _BREAK * _A * _B * _C * _PHI**2  # not multiplied by N: breaks reparametrization unless break = 0
    el = {f: e.lhs for f, e in zip([_N] + _Q, euler_equations(L, [_N] + _Q, [T]))}
    lhs = _N * sp.diff(el[_N], T)
    rhs = sum(el[q] * sp.diff(q, T) for q in _Q)
    return lhs, rhs


def _eval_identity(minisuperspace, seed: int, broken: float) -> tuple[float, float]:
    rng = random.Random(5000 + seed)
    p = random_params(rng)
    poly = lambda c0, s: c0 + rng.uniform(-s, s) * T + rng.uniform(-s, s) * T**2 + rng.uniform(-s, s) * T**3  # noqa: E731
    funcs = {_N: poly(1.0, 0.2), _A: poly(1.0, 0.3), _B: poly(1.1, 0.3), _C: poly(0.9, 0.3),
             _PHI: poly(p["phi_star"], 0.4), _CH1: poly(0.3, 0.4), _CH2: poly(-0.2, 0.4)}
    values = derivative_values(funcs, T, rng.uniform(0.0, 0.5))
    values.update({_PSYM[k]: sp.Float(v, 50) for k, v in p.items()})
    values[_BREAK] = sp.Float(broken, 50)
    lhs, rhs = minisuperspace
    return float(sp.N(lhs.xreplace(values), 40)), float(sp.N(rhs.xreplace(values), 40))


@pytest.mark.parametrize("seed", range(20))
def test_diffeomorphism_identity_preserves_the_energy_constraint(seed: int, minisuperspace) -> None:
    lhs, rhs = _eval_identity(minisuperspace, seed, 0.0)
    assert abs(lhs) > 1e-3
    assert rel_diff(lhs, rhs) < 1e-10


def test_identity_fails_when_reparametrization_is_broken(minisuperspace) -> None:
    lhs, rhs = _eval_identity(minisuperspace, 0, 0.7)
    assert rel_diff(lhs, rhs) > 1e-3


def _flat(seed: int) -> "m.FlatParams":
    rng = random.Random(6000 + seed)
    return m.FlatParams(epsilon=rng.uniform(0.4, 1.0), k=rng.uniform(0.8, 1.5), mu2=rng.uniform(0.4, 1.2),
                        lambda_phi=rng.uniform(0.2, 0.8), phi_star=rng.uniform(-0.3, 0.3), Z=rng.uniform(0.8, 1.5),
                        m2=rng.uniform(0.3, 1.0), lambda_chi=rng.uniform(0.2, 0.8), h=rng.uniform(0.3, 1.2))


@pytest.mark.parametrize("seed", range(2))
def test_poincare_and_o2_charges_on_the_lattice(seed: int) -> None:
    p = _flat(seed)
    drifts = []
    for n in (800, 1600, 3200):
        a, b = m.run(p, n, 8.0)
        assert abs(b["Q"] - a["Q"]) < 1e-12 * max(1.0, abs(a["Q"]))
        drifts.append({k: abs(b[k] - a[k]) for k in ("E", "P", "K")})
    for key in ("E", "P", "K"):
        for coarse, fine in zip(drifts, drifts[1:]):
            assert math.log2(coarse[key] / fine[key]) == pytest.approx(2.0, abs=0.2)
    assert drifts[-1]["K"] < 1e-3 * max(1.0, abs(a["K"]))


def test_boost_charge_fails_without_a_common_light_cone() -> None:
    p = dataclasses.replace(_flat(0), phi_speed_sq=0.5)
    k_drift = []
    for n in (800, 1600):
        a, b = m.run(p, n, 8.0)
        k_drift.append(abs(b["K"] - a["K"]))
    assert k_drift[1] > 0.5 * k_drift[0] and k_drift[1] > 1e-2  # does not converge to zero


def test_angular_momentum_on_a_2d_lattice() -> None:
    p = _flat(1)
    drifts = []
    for n in (128, 256, 512):
        a, b = m.run_2d(p, n, 4.0)
        assert abs(b["Q"] - a["Q"]) < 1e-12 * max(1.0, abs(a["Q"]))
        drifts.append({k: abs(b[k] - a[k]) for k in ("E", "Px", "Py", "L")})
    for key in ("E", "Px", "Py", "L"):
        for coarse, fine in zip(drifts, drifts[1:]):
            assert math.log2(coarse[key] / fine[key]) == pytest.approx(2.0, abs=0.2)
    assert drifts[-1]["L"] < 1e-3 * max(1.0, abs(a["L"]))


# ---------------------------------------------------------------------------
# Second theorem on an inhomogeneous, non-diagonal metric (beyond Bianchi I)
# ---------------------------------------------------------------------------

def _general_draw(seed: int, p_override: dict | None = None, all_coords: bool = False):
    rng = random.Random((8000 if all_coords else 7000) + seed)
    p = random_params(rng)
    p["h"] = rng.uniform(0.3, 1.5)
    if all_coords:
        poly = lambda c0, s: (c0 + sum(rng.uniform(-s, s) * v for v in COORDS)  # noqa: E731
                              + rng.uniform(-s, s) * T * X + rng.uniform(-s, s) * Y * ZC)
    else:
        poly = lambda c0, s: (c0 + rng.uniform(-s, s) * T + rng.uniform(-s, s) * X + rng.uniform(-s, s) * T * X  # noqa: E731
                              + rng.uniform(-s, s) * X**2 + rng.uniform(-s, s) * T**2)
    N, s, a, b, c = poly(1.0, 0.15), poly(0.0, 0.15), poly(1.0, 0.15), poly(1.1, 0.15), poly(0.9, 0.15)
    g = sp.Matrix([[-N**2, s, 0, 0], [s, a**2, 0, 0], [0, 0, b**2, 0], [0, 0, 0, c**2]])
    G, R, gamma, ginv = einstein_and_scalar(g)
    phi, chi = poly(p["phi_star"], 0.4), [poly(0.3, 0.4), poly(-0.2, 0.4)]
    E, hess = m.metric_residual_symbolic(g, ginv, G, gamma, phi, chi, dict(p, **(p_override or {})), COORDS)
    div = m.divergence_evaluator(E, ginv, gamma, COORDS, (0, 1, 2, 3) if all_coords else (0, 1))
    return rng, p, g, G, R, ginv, phi, chi, E, hess, div


def _code_side(p, g, G, R, ginv, phi, chi, hess, point):
    response, matter = configs(p)
    ev = lambda e: float(sp.N(sp.sympify(e).subs(point), 40))  # noqa: E731
    mat = lambda M: np.array([[ev(M[i, j]) for j in range(4)] for i in range(4)])  # noqa: E731
    dphi = np.array([ev(sp.diff(phi, v)) for v in COORDS])
    fields = np.array([ev(u) for u in chi])
    grads = np.array([[ev(sp.diff(u, v)) for v in COORDS] for u in chi])
    from ._symbolic_geometry import box
    residual = cov.coupled_metric_residual(mat(g), mat(G), ev(phi), dphi, mat(hess), fields, grads, response, matter)
    E_phi = cov.coupled_response_scalar_equation_residual(ev(R), ev(box(phi, g, ginv)), ev(phi), fields, response, matter)
    E_chi = cov.matter_eom_residual(np.array([ev(box(u, g, ginv)) for u in chi]), fields, ev(phi), response, matter)
    rhs = [-p["kappa"] * (E_phi * dphi[nu] + E_chi[0] * grads[0][nu] + E_chi[1] * grads[1][nu]) for nu in range(4)]
    return residual, rhs, ev


@pytest.mark.parametrize("seed", range(4))
def test_diffeomorphism_identity_on_a_general_metric(seed: int) -> None:
    rng, p, g, G, R, ginv, phi, chi, E, hess, div = _general_draw(seed)
    for _ in range(5):  # 4 draws x 5 points = 20 random off-shell points
        t0, x0 = rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3)
        point = {T: sp.Float(t0, 40), X: sp.Float(x0, 40), Y: 0, ZC: 0}
        residual, rhs, ev = _code_side(p, g, G, R, ginv, phi, chi, hess, point)
        for i in range(4):
            for j in range(4):
                assert abs(residual[i, j] - ev(E[i, j])) < 1e-10 * max(1.0, abs(residual[i, j]))
        lhs = div([t0, x0])
        scale = max(abs(v) for v in rhs)
        assert scale > 1e-3  # off shell
        for nu in range(4):
            assert abs(lhs[nu] - rhs[nu]) < 1e-10 * max(1.0, scale)


@pytest.mark.parametrize("seed", range(2))
def test_diffeomorphism_identity_on_a_metric_depending_on_all_four_coordinates(seed: int) -> None:
    rng, p, g, G, R, ginv, phi, chi, E, hess, div = _general_draw(seed, all_coords=True)
    for _ in range(10):  # 2 draws x 10 points = 20 random off-shell points
        pt = [rng.uniform(-0.3, 0.3) for _ in range(4)]
        point = {v: sp.Float(c, 40) for v, c in zip(COORDS, pt)}
        residual, rhs, ev = _code_side(p, g, G, R, ginv, phi, chi, hess, point)
        for i in range(4):
            for j in range(4):
                assert abs(residual[i, j] - ev(E[i, j])) < 1e-10 * max(1.0, abs(residual[i, j]))
        lhs = div(pt)
        scale = max(abs(v) for v in rhs)
        assert scale > 1e-3 and min(abs(v) for v in rhs) > 1e-8  # every component is off shell, y and z included
        for nu in range(4):
            assert abs(lhs[nu] - rhs[nu]) < 1e-10 * max(1.0, scale)


def test_general_identity_fails_without_the_portal_in_the_stress() -> None:
    rng, p, g, G, R, ginv, phi, chi, E, hess, div = _general_draw(0, {"h": 0.0})
    point = {T: sp.Float(0.1, 40), X: sp.Float(-0.2, 40), Y: 0, ZC: 0}
    _, rhs, _ = _code_side(p, g, G, R, ginv, phi, chi, hess, point)
    lhs = div([0.1, -0.2])
    assert max(abs(a - b) for a, b in zip(lhs, rhs)) > 1e-3
