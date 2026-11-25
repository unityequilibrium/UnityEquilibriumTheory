"""Wave C1: flat FRW background of the parent action and the apparent dark-energy w(a)
(core/03_lanes/scalar_tensor/uet_frw_background.py).

1. Derivation: the FRW minisuperspace Euler-Lagrange equations of the Theory Card action (built independently with
   sympy from the card text, original non-canonical parameters, dust as -N rho_m0) vanish on the code's H, dH/dt and
   psi'' at 20 random points (rel < 1e-10), after the canonical map psi = sqrt(eps k) delta.
2. Known limit through the general code path: psi = 0 gives w = -1 and H(a) = H0 sqrt(Om a^-3 + 1 - Om).
3. Identity (Bianchi): the time derivative of the constraint H, taken with sympy along psi' = pi and the code's psi'',
   equals the code's dH/dt at 20 random off-equilibrium points with xi != 0; dropping the F' R term from the psi
   equation breaks it (negative control).
4. Identity: with xi = 0, rho_DE + p_DE = pi^2 >= 0 exactly, so w >= -1 (no phantom without the coupling).
5. Convergence: the fixed-step RK4 value of w today converges with order 4 on 3 grids.
"""

from __future__ import annotations

import importlib
import math
import random

import numpy as np
import pytest
import sympy as sp
from sympy.calculus.euler import euler_equations

from ._symbolic_geometry import T, einstein_and_scalar, parent_lagrangian_scalar

pytestmark = pytest.mark.physics

m = importlib.import_module("core.03_lanes.scalar_tensor.uet_frw_background")

_N, _A, _PHI = (sp.Function(n)(T) for n in ("N", "a", "phi"))
_PS = {k: sp.Symbol(k) for k in ("epsilon", "kappa", "Lambda", "phi_star", "k", "mu2", "lambda_phi", "xi",
                                 "rho_star", "Z", "m2", "lambda_chi", "h")}
_RHO0 = sp.Symbol("rho0")


def rel(a: float, b: float) -> float:
    return abs(a - b) / max(abs(a), abs(b), 1e-300)


@pytest.fixture(scope="module")
def minisuperspace():
    g = sp.diag(-_N**2, _A**2, _A**2, _A**2)
    _, R, _, ginv = einstein_and_scalar(g)
    dphi = sp.diff(_PHI, T)
    L = _N * _A**3 * parent_lagrangian_scalar(R, _PHI, ginv[0, 0] * dphi**2, 0, 0, _PS) - _N * _RHO0
    eqs = euler_equations(L, [_N, _A, _PHI], [T])
    return [(e.lhs, sp.Add.make_args(sp.expand(e.lhs))) for e in eqs]


def _random_card(rng: random.Random) -> dict:
    return {"epsilon": rng.uniform(0.3, 1.0), "kappa": 1.0, "Lambda": rng.uniform(0.5, 2.0),
            "phi_star": rng.uniform(-0.3, 0.3), "k": rng.uniform(0.6, 1.6), "mu2": rng.uniform(0.2, 2.0),
            "lambda_phi": rng.uniform(0.0, 0.5), "xi": rng.uniform(-0.4, 0.4), "rho_star": rng.uniform(0.0, 1.0),
            "Z": 1.0, "m2": 1.0, "lambda_chi": 0.1, "h": 0.0}


def _canonical(p: dict) -> m.Background:
    ek = p["epsilon"] * p["k"]
    return m.Background(lambda_eff=p["Lambda"] + p["epsilon"] * p["rho_star"],
                        m2=p["mu2"] / p["k"] + 2.0 * p["xi"] / p["k"] * p["Lambda"],
                        lam=p["lambda_phi"] / (p["epsilon"] * p["k"] ** 2), xi=p["xi"] / p["k"])


@pytest.mark.parametrize("seed", range(20))
def test_frw_equations_follow_from_the_action(seed: int, minisuperspace) -> None:
    rng = random.Random(9100 + seed)
    p = _random_card(rng)
    bg = _canonical(p)
    s = math.sqrt(p["epsilon"] * p["k"])
    a, phi, dphi, rho0 = rng.uniform(0.5, 1.5), p["phi_star"] + rng.uniform(-0.5, 0.5), rng.uniform(-0.4, 0.4), \
        rng.uniform(0.2, 2.0)
    psi, pi, rho_m = s * (phi - p["phi_star"]), s * dphi, rho0 / a**3
    H = float(m.hubble(bg, psi, pi, rho_m))
    Hdot, psidd = m.accelerations(bg, psi, pi, rho_m, H)
    vals = {_N: 1, _A: a, _PHI: phi}
    derivs = {sp.diff(_N, T): 0, sp.diff(_N, T, 2): 0, sp.diff(_A, T): a * H, sp.diff(_A, T, 2): a * (Hdot + H * H),
              sp.diff(_A, T, 3): 0, sp.diff(_PHI, T): dphi, sp.diff(_PHI, T, 2): psidd / s}
    subs = {_PS[k]: v for k, v in p.items()} | {_RHO0: rho0}
    for i, (e, terms) in enumerate(minisuperspace):
        expr = e.subs(subs).subs(derivs).subs(vals)
        scale = max(abs(float(t.subs(subs).subs(derivs).subs(vals))) for t in terms)
        assert abs(float(expr)) < 1e-10 * scale, (i, float(expr), scale)


def test_lcdm_is_the_psi_zero_solution() -> None:
    bg, h = m.calibrated(1.0, 0.2, 0.0, omega_m0=0.3)
    assert np.max(np.abs(h.w + 1.0)) < 1e-12
    _, y = m.integrate(bg, 0.0)
    H = m.hubble(bg, y[:, 0], y[:, 1], h.a ** -3)
    lcdm = h.H0 * np.sqrt(0.3 * h.a ** -3 + 0.7)
    assert np.max(np.abs(H / lcdm - 1.0)) < 1e-10


def _constraint_rate(bg: m.Background, psi: float, pi: float, rho_m: float, H: float, psidd: float) -> float:
    ps, pp, rr = sp.symbols("psi pi rho", real=True)
    F = 1 + bg.xi * ps**2
    dF = sp.diff(F, ps)
    W = bg.lambda_eff + bg.m2 * ps**2 / 2 + bg.lam * ps**4 / 4
    Hs = (-3 * dF * pp + sp.sqrt(9 * dF**2 * pp**2 + 12 * F * (rr + pp**2 / 2 + W))) / (6 * F)
    at = {ps: psi, pp: pi, rr: rho_m}
    return float(sp.diff(Hs, ps).subs(at) * pi + sp.diff(Hs, pp).subs(at) * psidd
                 + sp.diff(Hs, rr).subs(at) * (-3 * H * rho_m))


def _random_state(rng: random.Random):
    bg = m.Background(rng.uniform(0.5, 2.0), rng.uniform(0.1, 3.0), rng.uniform(0.0, 0.5), rng.uniform(-0.4, 0.4))
    return bg, rng.uniform(-0.8, 0.8), rng.uniform(-0.5, 0.5), rng.uniform(0.1, 3.0)


@pytest.mark.parametrize("seed", range(20))
def test_constraint_is_preserved_by_the_dynamics(seed: int) -> None:
    rng = random.Random(9200 + seed)
    bg, psi, pi, rho_m = _random_state(rng)
    H = float(m.hubble(bg, psi, pi, rho_m))
    Hdot, psidd = m.accelerations(bg, psi, pi, rho_m, H)
    assert abs(Hdot) > 1e-3
    assert rel(_constraint_rate(bg, psi, pi, rho_m, H, psidd), Hdot) < 1e-10


def test_identity_fails_without_the_curvature_term() -> None:
    rng = random.Random(9300)
    bg, psi, pi, rho_m = _random_state(rng)
    bg = m.Background(bg.lambda_eff, bg.m2, bg.lam, 0.3)
    H = float(m.hubble(bg, psi, pi, rho_m))
    Hdot, _ = m.accelerations(bg, psi, pi, rho_m, H)
    psidd_wrong = -3.0 * H * pi - bg.dW(psi)  # psi equation without F' R / 2
    assert rel(_constraint_rate(bg, psi, pi, rho_m, H, psidd_wrong), Hdot) > 1e-3


@pytest.mark.parametrize("seed", range(20))
def test_minimal_coupling_cannot_be_phantom(seed: int) -> None:
    rng = random.Random(9400 + seed)
    bg, psi, pi, rho_m = _random_state(rng)
    bg = m.Background(bg.lambda_eff, bg.m2, bg.lam, 0.0)
    H = float(m.hubble(bg, psi, pi, rho_m))
    Hdot, _ = m.accelerations(bg, psi, pi, rho_m, H)
    rho_de = 3.0 * H * H - rho_m
    p_de = -2.0 * Hdot - rho_m - rho_de
    assert rel(rho_de + p_de, pi * pi) < 1e-10


def test_rk4_converges_with_order_four() -> None:
    bg = m.Background(lambda_eff=2.2, m2=4.0, lam=0.0, xi=0.02)
    ws = []
    for steps in (100, 200, 400, 800):
        N, y = m.integrate(bg, 0.6, z_i=9.0, steps=steps)
        psi, pi = y[-1]
        H = float(m.hubble(bg, psi, pi, 1.0))
        Hdot, _ = m.accelerations(bg, psi, pi, 1.0, H)
        ws.append(Hdot)
    errs = [abs(ws[i] - ws[i + 1]) for i in range(3)]
    for coarse, fine in zip(errs, errs[1:]):
        assert math.log2(coarse / fine) == pytest.approx(4.0, abs=0.3)
