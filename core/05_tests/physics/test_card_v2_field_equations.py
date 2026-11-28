"""W4-v2 derivation checks for the DRAFT Theory Card UET_PARENT v2 (core/THEORY_CARD_V2_DRAFT.md).

The action text of the draft card is varied with sympy (independent geometry helpers, nothing imported from the
code under test) and compared with core/03_lanes/scalar_tensor/uet_card_v2.py at random points.
Criterion: relative difference < 1e-10 at >= 20 random points per equation.
"""

from __future__ import annotations

import importlib
import random

import numpy as np
import pytest
import sympy as sp
from sympy.calculus.euler import euler_equations

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
)

v2 = importlib.import_module("core.03_lanes.scalar_tensor.uet_card_v2")

pytestmark = pytest.mark.physics

TOL = 1e-10
PREC = 40
NAMES = ("xi_phi", "xi_chi", "lam_chi", "alpha", "beta")


def rel_diff(a: float, b: float) -> float:
    a, b = float(a), float(b)
    return abs(a - b) / max(1.0, abs(a), abs(b))


def random_card(rng: random.Random) -> dict[str, float]:
    u = rng.uniform
    return {"xi_phi": u(0.05, 1.5), "xi_chi": u(-0.6, 0.8), "lam_chi": u(0.2, 1.5), "alpha": u(-0.8, 0.8),
            "beta": u(0.0, 0.8)}


def lagrangian(R, phi, dphi2, X2, dchi2, p):
    """Draft card v2 integrand (before sqrt(-g)), written from the card text."""
    F = p["xi_phi"] * phi**2 + p["xi_chi"] * X2
    V = p["lam_chi"] / 4 * (X2 - p["alpha"] / p["lam_chi"] * phi**2) ** 2 + p["beta"] / 4 * phi**4
    return F * R / 2 - dphi2 / 2 - dchi2 / 2 - V


def _poly(rng: random.Random, scale: float):
    c = [rng.uniform(-scale, scale) for _ in range(6)]
    return c[0] + c[1] * T + c[2] * X + c[3] * Y * ZC + c[4] * X * T + c[5] * Y**2


# (a) scalar equations on an inhomogeneous metric with a t-x off-diagonal entry ------------------------------

@pytest.mark.parametrize("seed", range(4))
def test_dilaton_and_matter_equations_match_euler_lagrange(seed: int) -> None:
    rng = random.Random(5100 + seed)
    p = random_card(rng)
    card = v2.CardV2(**p)
    s = 0.08
    g = sp.diag(-(1 + s * _poly(rng, 1) ** 2), 1 + s * _poly(rng, 1) ** 2,
                1 + s * _poly(rng, 1) ** 2, 1 + s * _poly(rng, 1) ** 2)
    g[0, 1] = g[1, 0] = rng.uniform(-0.05, 0.05) * (1 + X * Y)
    ginv = block_inverse(g)
    root = sp.sqrt(-block_det(g))
    R_ext = rng.uniform(-1, 1) + rng.uniform(-1, 1) * X * T

    names = ("phi", "chi1", "chi2")
    ph = {n: (sp.Symbol(f"{n}_v"), tuple(sp.Symbol(f"{n}_{c}") for c in "txyz")) for n in names}
    sq = lambda n: sum(ginv[m, v] * ph[n][1][m] * ph[n][1][v] for m in range(4) for v in range(4))  # noqa: E731
    Lt = root * lagrangian(R_ext, ph["phi"][0], sq("phi"), ph["chi1"][0] ** 2 + ph["chi2"][0] ** 2,
                           sq("chi1") + sq("chi2"), p)
    fields = {"phi": 1.0 + 0.3 * _poly(rng, 1), "chi1": 0.5 * _poly(rng, 1), "chi2": 0.5 * _poly(rng, 1)}
    concrete = {}
    for n in names:
        concrete[ph[n][0]] = fields[n]
        for mu, gs in enumerate(ph[n][1]):
            concrete[gs] = sp.diff(fields[n], COORDS[mu])
    boxes = {n: box(fields[n], g, ginv) for n in names}

    for _ in range(5):
        point = {T: rng.uniform(0, 0.4), X: rng.uniform(-0.4, 0.4), Y: rng.uniform(-0.4, 0.4), ZC: rng.uniform(-0.4, 0.4)}
        ev = lambda e: float(sp.N(e.evalf(PREC, subs=point), PREC))  # noqa: E731
        rv = ev(root)
        el = {n: float(euler_lagrange_at(Lt, ph[n], concrete, COORDS, point, PREC)) / rv for n in names}
        phi = ev(fields["phi"])
        chi = np.array([ev(fields["chi1"]), ev(fields["chi2"])])
        code_phi = v2.dilaton_residual(card, ev(R_ext), ev(boxes["phi"]), phi, chi)
        code_chi = v2.matter_residual(card, ev(R_ext), [ev(boxes["chi1"]), ev(boxes["chi2"])], chi, phi)
        assert abs(el["phi"]) > 1e-3  # off shell
        assert rel_diff(code_phi, el["phi"]) < TOL
        assert rel_diff(code_chi[0], el["chi1"]) < TOL
        assert rel_diff(code_chi[1], el["chi2"]) < TOL


# (b) metric equation from the Bianchi I minisuperspace action ------------------------------------------------

_N, _A, _B, _C = (sp.Function(n)(T) for n in ("N", "a", "b", "c"))
_PHI, _CH1, _CH2 = (sp.Function(n)(T) for n in ("phi_t", "chi1_t", "chi2_t"))
_PS = {k: sp.Symbol(k) for k in NAMES}


@pytest.fixture(scope="module")
def bianchi():
    g = sp.diag(-_N**2, _A**2, _B**2, _C**2)
    G, R, gamma, ginv = einstein_and_scalar(g)
    root = _N * _A * _B * _C
    L = root * lagrangian(R, _PHI, ginv[0, 0] * sp.diff(_PHI, T) ** 2, _CH1**2 + _CH2**2,
                          ginv[0, 0] * (sp.diff(_CH1, T) ** 2 + sp.diff(_CH2, T) ** 2), _PS)
    el = [e.lhs for e in euler_equations(L, [_N, _A, _B, _C], [T])]
    Fexpr = _PS["xi_phi"] * _PHI**2 + _PS["xi_chi"] * (_CH1**2 + _CH2**2)
    hess = covariant_hessian(Fexpr, gamma)
    J = (1 + 6 * _PS["xi_phi"]) * _PHI**2 + (1 + 6 * _PS["xi_chi"]) * (_CH1**2 + _CH2**2)
    return {"G": G, "R": R, "el": el, "hess": hess, "g": g, "ginv": ginv,
            "boxes": [box(f, g, ginv) for f in (_PHI, _CH1, _CH2)], "boxJ": box(J, g, ginv)}


def _sample(rng: random.Random, p: dict, bianchi):
    poly = lambda c0, s: c0 + rng.uniform(-s, s) * T + rng.uniform(-s, s) * T**2 + rng.uniform(-s, s) * T**3  # noqa: E731
    funcs = {_N: poly(1.0, 0.2), _A: poly(1.0, 0.3), _B: poly(1.1, 0.3), _C: poly(0.9, 0.3),
             _PHI: poly(1.0, 0.4), _CH1: poly(0.3, 0.4), _CH2: poly(-0.2, 0.4)}
    values = derivative_values(funcs, T, rng.uniform(0.0, 0.5))
    values.update({_PS[k]: sp.Float(v, 50) for k, v in p.items()})
    ev = lambda e: float(sp.N(e.xreplace(values), PREC))  # noqa: E731
    Nv, av, bv, cv = (ev(f) for f in (_N, _A, _B, _C))
    out = {
        "ev": ev, "Nv": Nv, "av": av, "bv": bv, "cv": cv,
        "metric": np.diag([-Nv**2, av**2, bv**2, cv**2]),
        "G": np.array([[ev(bianchi["G"][i, j]) for j in range(4)] for i in range(4)]),
        "H": np.array([[ev(bianchi["hess"][i, j]) for j in range(4)] for i in range(4)]),
        "phi": ev(_PHI), "dphi": np.array([ev(sp.diff(_PHI, T)), 0.0, 0.0, 0.0]),
        "chi": np.array([ev(_CH1), ev(_CH2)]),
        "dchi": np.array([[ev(sp.diff(f, T)), 0.0, 0.0, 0.0] for f in (_CH1, _CH2)]),
        "R": ev(bianchi["R"]), "boxes": [ev(b) for b in bianchi["boxes"]], "boxJ": ev(bianchi["boxJ"]),
    }
    return out


@pytest.mark.parametrize("seed", range(20))
def test_metric_equation_matches_minisuperspace_variation(seed: int, bianchi) -> None:
    rng = random.Random(5200 + seed)
    p = random_card(rng)
    card = v2.CardV2(**p)
    s = _sample(rng, p, bianchi)
    E = v2.metric_residual(card, s["metric"], s["G"], s["phi"], s["dphi"], s["chi"], s["dchi"], s["H"])
    root = s["Nv"] * s["av"] * s["bv"] * s["cv"]
    # delta S / delta g^{mn} = sqrt(-g) E_mn / 2; d g^tt / dN = 2 / N^3, d g^ii / d a_i = -2 / a_i^3.
    expected = [root * E[0, 0] / s["Nv"] ** 3, -root * E[1, 1] / s["av"] ** 3,
                -root * E[2, 2] / s["bv"] ** 3, -root * E[3, 3] / s["cv"] ** 3]
    assert max(abs(e) for e in expected) > 1e-3
    for i, el in enumerate(bianchi["el"]):
        assert rel_diff(s["ev"](el), expected[i]) < TOL, (i, s["ev"](el), expected[i])


@pytest.mark.parametrize("seed", range(20))
def test_dilatation_identity_off_shell(seed: int, bianchi) -> None:
    """phi E_phi + chi E_chi + g^mn E_mn = box J / 2 for arbitrary (off-shell) fields and metric."""
    rng = random.Random(5300 + seed)
    p = random_card(rng)
    card = v2.CardV2(**p)
    s = _sample(rng, p, bianchi)
    E_phi = v2.dilaton_residual(card, s["R"], s["boxes"][0], s["phi"], s["chi"])
    E_chi = v2.matter_residual(card, s["R"], s["boxes"][1:], s["chi"], s["phi"])
    E_mn = v2.metric_residual(card, s["metric"], s["G"], s["phi"], s["dphi"], s["chi"], s["dchi"], s["H"])
    lhs = v2.dilatation_combination(card, s["metric"], E_phi, E_chi, E_mn, s["phi"], s["chi"])
    assert abs(E_phi) > 1e-3
    assert rel_diff(lhs, 0.5 * s["boxJ"]) < TOL


def test_dilatation_identity_fails_when_scale_symmetry_is_broken(bianchi) -> None:
    """Negative control: a dimensionful term (here a chi mass, added to V by hand) breaks the identity."""
    rng = random.Random(5400)
    p = random_card(rng)
    s = _sample(rng, p, bianchi)
    m2 = 0.3

    class Broken(v2.CardV2):
        def V(self, phi, X):
            return super().V(phi, X) + 0.5 * m2 * X

        def dV_dX(self, phi, X):
            return super().dV_dX(phi, X) + 0.5 * m2

    bad = Broken(**p)
    E_phi = v2.dilaton_residual(bad, s["R"], s["boxes"][0], s["phi"], s["chi"])
    E_chi = v2.matter_residual(bad, s["R"], s["boxes"][1:], s["chi"], s["phi"])
    E_mn = v2.metric_residual(bad, s["metric"], s["G"], s["phi"], s["dphi"], s["chi"], s["dchi"], s["H"])
    lhs = v2.dilatation_combination(bad, s["metric"], E_phi, E_chi, E_mn, s["phi"], s["chi"])
    X2 = float(s["chi"] @ s["chi"])
    assert abs(lhs - 0.5 * s["boxJ"]) > 1e-3
    # the defect equals +m^2 X: the degree-2 term of V does not cancel against the degree-4 trace
    assert rel_diff(lhs - 0.5 * s["boxJ"], m2 * X2) < 1e-9


@pytest.mark.parametrize("seed", range(20))
def test_de_sitter_solution_through_general_path(seed: int) -> None:
    """X = 0, phi = phi0, H^2 = beta_eff phi0^2 / (12 xi_phi) solves all equations, for every phi0."""
    rng = random.Random(5500 + seed)
    card = v2.CardV2(**random_card(rng))
    phi0 = rng.uniform(0.2, 3.0)
    H2 = v2.de_sitter_H2(card, phi0)
    a = rng.uniform(0.5, 2.0)
    g = np.diag([-1.0, a * a, a * a, a * a])
    G = 3.0 * H2 * np.diag([1.0, -a * a, -a * a, -a * a])   # G_mn = -3 H^2 g_mn
    R = 12.0 * H2
    chi = np.zeros(2)
    zero4 = np.zeros(4)
    assert abs(v2.dilaton_residual(card, R, 0.0, phi0, chi)) < 1e-12 * max(1.0, phi0**3)
    assert np.allclose(v2.matter_residual(card, R, [0.0, 0.0], chi, phi0), 0.0)
    E = v2.metric_residual(card, g, G, phi0, zero4, chi, np.zeros((2, 4)), np.zeros((4, 4)))
    assert np.max(np.abs(E)) < 1e-12 * max(1.0, card.V(phi0, 0.0))
    # a wrong Hubble rate leaves a residual
    E_bad = v2.metric_residual(card, g, 1.1 * G, phi0, zero4, chi, np.zeros((2, 4)), np.zeros((4, 4)))
    assert np.max(np.abs(E_bad)) > 1e-6 * card.V(phi0, 0.0)
