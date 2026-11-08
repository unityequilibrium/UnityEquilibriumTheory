"""W4 derivation checks for Theory Card UET_PARENT v1 (docs/STANDARD.md section 6).

Each test derives field equations from the action text of the Theory Card with
sympy (Euler-Lagrange variation, independent geometry helpers) and compares
them with the implemented residual functions at random points. Every sample
has epsilon > 0, so the general code path is used and the epsilon == 0 GR
branch is never exercised.

Criterion: relative difference < 1e-10 at >= 20 random points per equation.
"""

from __future__ import annotations

import random

import numpy as np
import pytest
import sympy as sp
from sympy.calculus.euler import euler_equations

from docs.core.uet_covariant_matter import (
    CovariantMatterConfig,
    coupled_metric_residual,
    coupled_response_scalar_equation_residual,
    matter_eom_residual,
)
from docs.core.uet_covariant_response import CovariantResponseConfig

from ._symbolic_geometry import (
    COORDS,
    T,
    X,
    Y,
    ZC,
    block_det,
    block_inverse,
    box,
    covariant_hessian,
    derivative_values,
    einstein_and_scalar,
    euler_lagrange_at,
    parent_lagrangian_scalar,
)

pytestmark = pytest.mark.physics

TOL = 1e-10
PREC = 40


def rel_diff(a: float, b: float) -> float:
    a, b = float(a), float(b)
    return abs(a - b) / max(1.0, abs(a), abs(b))


def random_params(rng: random.Random) -> dict[str, float]:
    u = rng.uniform
    return {
        "epsilon": u(0.1, 1.0), "kappa": u(0.5, 2.0), "Lambda": u(-0.3, 0.3),
        "phi_star": u(-0.5, 0.5), "k": u(0.5, 2.0), "mu2": u(0.1, 1.5),
        "lambda_phi": u(0.1, 1.5), "xi": u(-0.6, 0.6), "rho_star": u(-0.3, 0.3),
        "Z": u(0.5, 2.0), "m2": u(-0.5, 1.5), "lambda_chi": u(0.1, 1.5), "h": u(0.0, 1.5),
    }


def configs(p: dict[str, float]) -> tuple[CovariantResponseConfig, CovariantMatterConfig]:
    response = CovariantResponseConfig(
        epsilon_nc=p["epsilon"], einstein_coupling=p["kappa"], cosmological_constant=p["Lambda"],
        phi_equilibrium=p["phi_star"], response_kinetic=p["k"], response_mass_sq=p["mu2"],
        response_quartic=p["lambda_phi"], curvature_coupling=p["xi"], equilibrium_density=p["rho_star"],
    )
    matter = CovariantMatterConfig(
        matter_kinetic=p["Z"], matter_mass_sq=p["m2"], matter_quartic=p["lambda_chi"],
        response_coupling=p["h"],
    )
    return response, matter


# ---------------------------------------------------------------------------
# (a) scalar and matter equations on an inhomogeneous, non-diagonal metric
# ---------------------------------------------------------------------------

SCALAR_MODELS = 4
POINTS_PER_MODEL = 5  # 4 x 5 = 20 random spacetime points


def _poly(rng: random.Random, scale: float):
    c = [rng.uniform(-scale, scale) for _ in range(6)]
    return c[0] + c[1] * T + c[2] * X + c[3] * Y * ZC + c[4] * X * T + c[5] * Y**2


@pytest.mark.parametrize("seed", range(SCALAR_MODELS))
def test_scalar_and_matter_equations_match_euler_lagrange(seed: int) -> None:
    rng = random.Random(1000 + seed)
    p = random_params(rng)
    response, matter = configs(p)
    s = 0.08
    g = sp.diag(-(1 + s * _poly(rng, 1) ** 2), 1 + s * _poly(rng, 1) ** 2,
                1 + s * _poly(rng, 1) ** 2, 1 + s * _poly(rng, 1) ** 2)
    g[0, 1] = g[1, 0] = rng.uniform(-0.05, 0.05) * (1 + X * Y)
    ginv = block_inverse(g)
    root = sp.sqrt(-block_det(g))
    R_ext = rng.uniform(-1, 1) + rng.uniform(-1, 1) * X * T  # curvature is given data for the phi equation

    names = ("phi", "chi1", "chi2")
    ph = {n: (sp.Symbol(f"{n}_v"), tuple(sp.Symbol(f"{n}_{c}") for c in "txyz")) for n in names}
    sq = lambda n: sum(ginv[m, v] * ph[n][1][m] * ph[n][1][v] for m in range(4) for v in range(4))  # noqa: E731
    Ltilde = root * parent_lagrangian_scalar(
        R_ext, ph["phi"][0], sq("phi"), ph["chi1"][0] ** 2 + ph["chi2"][0] ** 2, sq("chi1") + sq("chi2"), p)

    fields = {"phi": p["phi_star"] + 0.3 * _poly(rng, 1), "chi1": 0.5 * _poly(rng, 1), "chi2": 0.5 * _poly(rng, 1)}
    concrete = {}
    for n in names:
        concrete[ph[n][0]] = fields[n]
        for mu, gs in enumerate(ph[n][1]):
            concrete[gs] = sp.diff(fields[n], COORDS[mu])
    boxes = {n: box(fields[n], g, ginv) for n in names}

    for _ in range(POINTS_PER_MODEL):
        point = {T: rng.uniform(0, 0.4), X: rng.uniform(-0.4, 0.4), Y: rng.uniform(-0.4, 0.4), ZC: rng.uniform(-0.4, 0.4)}
        ev = lambda e: float(sp.N(e.evalf(PREC, subs=point), PREC))  # noqa: E731
        root_v = ev(root)
        el = {n: float(euler_lagrange_at(Ltilde, ph[n], concrete, COORDS, point, PREC)) / root_v for n in names}
        phi = ev(fields["phi"])
        doublet = np.array([ev(fields["chi1"]), ev(fields["chi2"])])
        box_chi = np.array([ev(boxes["chi1"]), ev(boxes["chi2"])])

        code_phi = coupled_response_scalar_equation_residual(ev(R_ext), ev(boxes["phi"]), phi, doublet, response, matter)
        assert rel_diff(code_phi, el["phi"]) < TOL, (code_phi, el["phi"])

        code_chi = matter_eom_residual(box_chi, doublet, phi, response, matter)
        assert rel_diff(code_chi[0], el["chi1"]) < TOL, (code_chi[0], el["chi1"])
        assert rel_diff(code_chi[1], el["chi2"]) < TOL, (code_chi[1], el["chi2"])


# ---------------------------------------------------------------------------
# (b) metric equation from the Bianchi I minisuperspace action
# ---------------------------------------------------------------------------

_N, _A, _B, _C = (sp.Function(n)(T) for n in ("N", "a", "b", "c"))
_PHI, _CH1, _CH2 = (sp.Function(n)(T) for n in ("phi_t", "chi1_t", "chi2_t"))
_PSYM = {k: sp.Symbol(k) for k in ("epsilon", "kappa", "Lambda", "phi_star", "k", "mu2", "lambda_phi",
                                   "xi", "rho_star", "Z", "m2", "lambda_chi", "h")}


@pytest.fixture(scope="module")
def bianchi():
    """Symbolic Bianchi I geometry, Euler-Lagrange equations and Hessian of f, built once."""
    g = sp.diag(-_N**2, _A**2, _B**2, _C**2)
    G, R, gamma, ginv = einstein_and_scalar(g)
    root = _N * _A * _B * _C
    dphi = sp.diff(_PHI, T)
    L = root * parent_lagrangian_scalar(
        R, _PHI, ginv[0, 0] * dphi**2, _CH1**2 + _CH2**2,
        ginv[0, 0] * (sp.diff(_CH1, T) ** 2 + sp.diff(_CH2, T) ** 2), _PSYM)
    el = [e.lhs for e in euler_equations(L, [_N, _A, _B, _C], [T])]
    hess = covariant_hessian(_PSYM["xi"] * (_PHI - _PSYM["phi_star"]) ** 2, gamma)
    return {"G": G, "el": el, "hess": hess}


@pytest.mark.parametrize("seed", range(20))
def test_metric_equation_matches_minisuperspace_variation(seed: int, bianchi) -> None:
    rng = random.Random(2000 + seed)
    p = random_params(rng)
    response, matter = configs(p)
    poly = lambda c0, s: c0 + rng.uniform(-s, s) * T + rng.uniform(-s, s) * T**2 + rng.uniform(-s, s) * T**3  # noqa: E731
    funcs = {_N: poly(1.0, 0.2), _A: poly(1.0, 0.3), _B: poly(1.1, 0.3), _C: poly(0.9, 0.3),
             _PHI: poly(p["phi_star"], 0.4), _CH1: poly(0.3, 0.4), _CH2: poly(-0.2, 0.4)}
    t0 = rng.uniform(0.0, 0.5)
    values = derivative_values(funcs, T, t0)
    values.update({_PSYM[k]: sp.Float(v, 50) for k, v in p.items()})
    ev = lambda e: float(sp.N(e.xreplace(values), PREC))  # noqa: E731

    Nv, av, bv, cv = (ev(f) for f in (_N, _A, _B, _C))
    metric = np.diag([-Nv**2, av**2, bv**2, cv**2])
    einstein = np.array([[ev(bianchi["G"][i, j]) for j in range(4)] for i in range(4)])
    hessian = np.array([[ev(bianchi["hess"][i, j]) for j in range(4)] for i in range(4)])
    phi = ev(_PHI)
    grad_phi = np.array([ev(sp.diff(_PHI, T)), 0.0, 0.0, 0.0])
    doublet = np.array([ev(_CH1), ev(_CH2)])
    grads = np.array([[ev(sp.diff(f, T)), 0.0, 0.0, 0.0] for f in (_CH1, _CH2)])

    residual = coupled_metric_residual(metric, einstein, phi, grad_phi, hessian, doublet, grads, response, matter)

    root = Nv * av * bv * cv
    # delta S / delta g^{mu nu} = sqrt(-g)/(2 kappa) * residual_{mu nu};
    # d g^{tt}/dN = 2/N^3 and d g^{ii}/d a_i = -2/a_i^3.
    expected = [
        root / (2 * p["kappa"]) * residual[0, 0] * 2 / Nv**3,
        -root / (2 * p["kappa"]) * residual[1, 1] * 2 / av**3,
        -root / (2 * p["kappa"]) * residual[2, 2] * 2 / bv**3,
        -root / (2 * p["kappa"]) * residual[3, 3] * 2 / cv**3,
    ]
    assert max(abs(e) for e in expected) > 1e-3  # off-shell sample: the comparison is not 0 == 0
    for i, el in enumerate(bianchi["el"]):
        derived = ev(el)
        assert rel_diff(derived, expected[i]) < TOL, (i, derived, expected[i])


@pytest.mark.parametrize("wrong", ["xi_sign", "kinetic", "portal"])
def test_metric_check_detects_wrong_implementation(wrong: str, bianchi) -> None:
    """Negative control: a residual built from a deliberately wrong config must disagree."""
    rng = random.Random(3000)
    p = random_params(rng)
    p["xi"], p["h"] = 0.5, 1.0
    poly = lambda c0, s: c0 + rng.uniform(-s, s) * T + rng.uniform(-s, s) * T**2 + rng.uniform(-s, s) * T**3  # noqa: E731
    funcs = {_N: poly(1.0, 0.2), _A: poly(1.0, 0.3), _B: poly(1.1, 0.3), _C: poly(0.9, 0.3),
             _PHI: p["phi_star"] + 0.3 + 0.8 * T, _CH1: poly(0.3, 0.4), _CH2: poly(-0.2, 0.4)}
    values = derivative_values(funcs, T, 0.2)
    values.update({_PSYM[k]: sp.Float(v, 50) for k, v in p.items()})
    ev = lambda e: float(sp.N(e.xreplace(values), PREC))  # noqa: E731

    bad = dict(p)
    if wrong == "xi_sign":
        bad["xi"] = -p["xi"]
    elif wrong == "kinetic":
        bad["k"] = 2 * p["k"]
    else:
        bad["h"] = 0.0
    response, matter = configs(bad)
    Nv, av, bv, cv = (ev(f) for f in (_N, _A, _B, _C))
    metric = np.diag([-Nv**2, av**2, bv**2, cv**2])
    einstein = np.array([[ev(bianchi["G"][i, j]) for j in range(4)] for i in range(4)])
    hessian = np.array([[ev(bianchi["hess"][i, j]) for j in range(4)] for i in range(4)])
    if wrong == "xi_sign":
        hessian = -hessian
    grads = np.array([[ev(sp.diff(f, T)), 0.0, 0.0, 0.0] for f in (_CH1, _CH2)])
    residual = coupled_metric_residual(
        metric, einstein, ev(_PHI), np.array([ev(sp.diff(_PHI, T)), 0, 0, 0]), hessian,
        np.array([ev(_CH1), ev(_CH2)]), grads, response, matter)
    root = Nv * av * bv * cv
    scale = root / p["kappa"]
    expected = [scale * residual[0, 0] / Nv**3, -scale * residual[1, 1] / av**3,
                -scale * residual[2, 2] / bv**3, -scale * residual[3, 3] / cv**3]
    worst = max(rel_diff(ev(el), e) for el, e in zip(bianchi["el"], expected))
    assert worst > 1e-6  # four orders above TOL: the derivation check would catch this defect


# ---------------------------------------------------------------------------
# (c) canonical map and epsilon redundancy (Theory Card sections 3 and 5)
# ---------------------------------------------------------------------------


def test_canonical_map_and_epsilon_redundancy() -> None:
    eps, k, xi, kap, mu2, lphi, rho, h, Z, m2, lchi, Lam = sp.symbols(
        "epsilon k xi kappa mu2 lambda_phi rho_star h Z m2 lambda_chi Lambda", positive=True)
    d, psi, chi2, chit2, R, Xp, Xc, Xps, Xct = sp.symbols("delta psi chi2 chit2 R Xp Xc Xpsi Xchit")
    p = {"epsilon": eps, "kappa": kap, "Lambda": Lam, "phi_star": 0, "k": k, "mu2": mu2, "lambda_phi": lphi,
         "xi": xi, "rho_star": rho, "Z": Z, "m2": m2, "lambda_chi": lchi, "h": h}
    L = parent_lagrangian_scalar(R, d, Xp, chi2, Xc, p)
    Lc = sp.expand(L.subs({d: psi / sp.sqrt(eps * k), Xp: Xps / (eps * k), chi2: chit2 / Z, Xc: Xct / Z}))

    xi_c, m_psi2, l_psi, g_c = xi / (kap * k), mu2 / k, lphi / (eps * k**2), h * sp.sqrt(eps / k) / Z
    target = ((1 + kap * xi_c * psi**2) * (R - 2 * Lam) / (2 * kap) - Xps / 2 - eps * rho
              - m_psi2 * psi**2 / 2 - l_psi * psi**4 / 4 - Xct / 2
              - (m2 / Z) * chit2 / 2 - (lchi / Z**2) * chit2**2 / 4 + g_c * psi * chit2 / 2)
    assert sp.simplify(Lc - target) == 0

    # epsilon -> 0+: xi_c and m_psi2 unchanged, lambda_psi diverges, g_c vanishes.
    assert sp.diff(xi_c, eps) == 0 and sp.diff(m_psi2, eps) == 0
    assert sp.limit(l_psi, eps, 0, "+") == sp.oo
    assert sp.limit(g_c, eps, 0, "+") == 0
