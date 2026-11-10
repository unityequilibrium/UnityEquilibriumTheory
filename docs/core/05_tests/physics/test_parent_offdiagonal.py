"""Wave A2: derivation check of the off-diagonal metric equation (Theory Card UET_PARENT v1).

W4 checked only the diagonal metric components (Bianchi I minisuperspace). Here the
minisuperspace metric carries a time-dependent off-diagonal entry s(t) = g_tx:

    g = [[-N^2, s, 0, 0], [s, a^2, 0, 0], [0, 0, b^2, 0], [0, 0, 0, c^2]]

With S = int sqrt(-g) L and delta S / delta g^{mu nu} = sqrt(-g)/(2 kappa) E_{mu nu},
every metric function q obeys

    dS/dq = -sqrt(-g)/(2 kappa) * E^{mu nu} * d g_{mu nu}/dq     (E^{mu nu} raised with g^-1)

so the Euler-Lagrange equation of s tests E^{tx}, and those of N, a, b, c test the
diagonal components on a non-diagonal background. The residual E_{mu nu} comes from
the implementation; the left side comes from sympy acting on the Theory Card action.
Criterion: relative difference < 1e-10 at 12 random off-shell samples.
"""

from __future__ import annotations

import random

import numpy as np
import pytest
import sympy as sp
from sympy.calculus.euler import euler_equations

from docs.core.uet_covariant_matter import coupled_metric_residual

from ._symbolic_geometry import T, block_det, covariant_hessian, derivative_values, einstein_and_scalar, parent_lagrangian_scalar
from .test_parent_derivation import PREC, TOL, configs, random_params, rel_diff

pytestmark = pytest.mark.physics

_N, _S, _A, _B, _C = (sp.Function(n)(T) for n in ("N", "s", "a", "b", "c"))
_PHI, _CH1, _CH2 = (sp.Function(n)(T) for n in ("phi_t", "chi1_t", "chi2_t"))
_Q = [_N, _S, _A, _B, _C]
_PSYM = {k: sp.Symbol(k) for k in ("epsilon", "kappa", "Lambda", "phi_star", "k", "mu2", "lambda_phi",
                                   "xi", "rho_star", "Z", "m2", "lambda_chi", "h")}


def _metric():
    return sp.Matrix([[-_N**2, _S, 0, 0], [_S, _A**2, 0, 0], [0, 0, _B**2, 0], [0, 0, 0, _C**2]])


@pytest.fixture(scope="module")
def shifted():
    g = _metric()
    G, R, gamma, ginv = einstein_and_scalar(g)
    root = sp.sqrt(-block_det(g))
    dphi = sp.diff(_PHI, T)
    dchi_sq = sp.diff(_CH1, T) ** 2 + sp.diff(_CH2, T) ** 2
    L = root * parent_lagrangian_scalar(
        R, _PHI, ginv[0, 0] * dphi**2, _CH1**2 + _CH2**2, ginv[0, 0] * dchi_sq, _PSYM)
    el = [e.lhs for e in euler_equations(L, _Q, [T])]
    hess = covariant_hessian(_PSYM["xi"] * (_PHI - _PSYM["phi_star"]) ** 2, gamma)
    dg = [g.diff(q) for q in _Q]
    return {"g": g, "G": G, "el": el, "hess": hess, "root": root, "dg": dg}


def _sample(rng: random.Random, p: dict, shifted, wrong_xi: bool = False):
    poly = lambda c0, s: c0 + rng.uniform(-s, s) * T + rng.uniform(-s, s) * T**2 + rng.uniform(-s, s) * T**3  # noqa: E731
    funcs = {_N: poly(1.0, 0.2), _S: poly(0.0, 0.3), _A: poly(1.0, 0.3), _B: poly(1.1, 0.3), _C: poly(0.9, 0.3),
             _PHI: poly(p["phi_star"] + 0.2, 0.4), _CH1: poly(0.3, 0.4), _CH2: poly(-0.2, 0.4)}
    values = derivative_values(funcs, T, rng.uniform(0.0, 0.5))
    values.update({_PSYM[k]: sp.Float(v, 50) for k, v in p.items()})
    ev = lambda e: float(sp.N(sp.sympify(e).xreplace(values), PREC))  # noqa: E731
    mat = lambda m: np.array([[ev(m[i, j]) for j in range(4)] for i in range(4)])  # noqa: E731

    metric = mat(shifted["g"])
    hessian = mat(shifted["hess"])
    bad = dict(p)
    if wrong_xi:
        bad["xi"] = -p["xi"]
        hessian = -hessian
    response, matter = configs(bad)
    grads = np.array([[ev(sp.diff(f, T)), 0.0, 0.0, 0.0] for f in (_CH1, _CH2)])
    residual = coupled_metric_residual(
        metric, mat(shifted["G"]), ev(_PHI), np.array([ev(sp.diff(_PHI, T)), 0.0, 0.0, 0.0]), hessian,
        np.array([ev(_CH1), ev(_CH2)]), grads, response, matter)
    ginv = np.linalg.inv(metric)
    e_up = ginv @ residual @ ginv
    pref = -ev(shifted["root"]) / (2 * p["kappa"])
    expected = [pref * float(np.sum(e_up * mat(d))) for d in shifted["dg"]]
    derived = [ev(e) for e in shifted["el"]]
    return derived, expected, residual


@pytest.mark.parametrize("seed", range(12))
def test_offdiagonal_metric_equation_matches_variation(seed: int, shifted) -> None:
    rng = random.Random(4000 + seed)
    p = random_params(rng)
    derived, expected, residual = _sample(rng, p, shifted)
    assert abs(residual[0, 1]) > 1e-6  # the off-diagonal component is genuinely tested
    assert abs(expected[1]) > 1e-6     # off-shell: not 0 == 0
    for i, (d, e) in enumerate(zip(derived, expected)):
        assert rel_diff(d, e) < TOL, (i, d, e)


def test_offdiagonal_check_detects_wrong_curvature_coupling(shifted) -> None:
    rng = random.Random(4999)
    p = random_params(rng)
    p["xi"] = 0.5
    derived, expected, _ = _sample(rng, p, shifted, wrong_xi=True)
    assert max(rel_diff(d, e) for d, e in zip(derived, expected)) > 1e-6
