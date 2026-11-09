"""W5 checks for the Jordan-to-DEF map of the UET parent (docs/STANDARD.md section 6).

- known limit: Brans-Dicke (alpha0^2 = 1/(2 omega + 3), beta = 0,
  gamma_PPN = (1 + omega)/(2 + omega)) through the general code path
- derivation: Jordan and Einstein frame FRW minisuperspace Lagrangians differ
  by a total derivative when (d phi/d psi)^2 = kappa K/(2F) + (3/4)(F'/F)^2
- the implemented closed-form chain rule for alpha, beta equals sympy
  differentiation at 20 random points; beta0 = -2 xi_c at psi0 = 0
- Einstein-frame mass at the origin equals sympy's second derivative
"""

from __future__ import annotations

import importlib
import random

import pytest
import sympy as sp
from sympy.calculus.euler import euler_equations

from ._symbolic_geometry import T, einstein_and_scalar

mapping = importlib.import_module("docs.core.02_equations.covariant.uet_scalar_tensor_mapping")

pytestmark = pytest.mark.physics
TOL = 1e-10


def rel_diff(a: float, b: float) -> float:
    return abs(float(a) - float(b)) / max(1.0, abs(float(a)), abs(float(b)))


@pytest.mark.parametrize("omega", [0.5, 3.0, 40.0, 4.0e4])
def test_brans_dicke_limit_through_general_path(omega: float) -> None:
    # Brans-Dicke: F = Phi, K = omega/(kappa Phi); evaluate at an arbitrary Phi.
    kappa, Phi = 1.7, 0.83
    alpha, beta = mapping.general_def_alpha_beta(
        F=lambda x: x, dF=lambda x: 1.0, d2F=lambda x: 0.0,
        K=lambda x: omega / (kappa * x), dK=lambda x: -omega / (kappa * x * x),
        psi=Phi, kappa=kappa,
    )
    assert rel_diff(alpha**2, 1.0 / (2.0 * omega + 3.0)) < TOL
    assert abs(beta) < TOL
    gamma_m1, beta_ppn_m1 = mapping.ppn_from_def(alpha, beta)
    assert rel_diff(1.0 + gamma_m1, (1.0 + omega) / (2.0 + omega)) < TOL
    assert abs(beta_ppn_m1) < TOL  # Brans-Dicke has beta_PPN = 1


@pytest.mark.parametrize("coefficient, equivalent", [(sp.Rational(3, 4), True), (sp.Rational(1, 2), False)])
def test_conformal_frames_differ_by_total_derivative(coefficient, equivalent) -> None:
    kappa = sp.Symbol("kappa", positive=True)
    N, a, psi = (sp.Function(n)(T) for n in ("N", "a", "psi"))
    Ff, Kf, Vf = (sp.Function(n) for n in ("F", "K", "V"))
    F, K, V = Ff(psi), Kf(psi), Vf(psi)
    dpsi = sp.diff(psi, T)

    _, R_J, _, _ = einstein_and_scalar(sp.diag(-N**2, a**2, a**2, a**2))
    L_J = N * a**3 * (F * R_J / (2 * kappa) + K * dpsi**2 / (2 * N**2) - V)

    Ns, As = sp.sqrt(F) * N, sp.sqrt(F) * a
    _, R_E, _, _ = einstein_and_scalar(sp.diag(-Ns**2, As**2, As**2, As**2))
    Fp = sp.diff(F, psi)
    s2 = kappa * K / (2 * F) + coefficient * (Fp / F) ** 2
    L_E = Ns * As**3 * (R_E / (2 * kappa) + s2 * dpsi**2 / (kappa * Ns**2) - V / F**2)

    residues = [sp.simplify(eq.lhs) for eq in euler_equations(L_J - L_E, [N, a, psi], [T])]
    if equivalent:
        assert all(r == 0 for r in residues)
    else:  # negative control: a wrong kinetic coefficient is detected
        assert any(r != 0 for r in residues)


def _sympy_alpha_beta():
    psi, kappa, xi = sp.symbols("psi kappa xi_c", real=True)
    F = 1 + kappa * xi * psi**2
    s = sp.sqrt(kappa / (2 * F) + sp.Rational(3, 4) * (sp.diff(F, psi) / F) ** 2)
    alpha = -sp.diff(F, psi) / F / (2 * s)
    beta = sp.diff(alpha, psi) / s
    return sp.lambdify((psi, kappa, xi), alpha, "mpmath"), sp.lambdify((psi, kappa, xi), beta, "mpmath")


def test_uet_alpha_beta_match_sympy_at_random_points() -> None:
    alpha_s, beta_s = _sympy_alpha_beta()
    rng = random.Random(5000)
    for _ in range(20):
        kappa, xi = rng.uniform(0.3, 3.0), rng.uniform(-0.15, 3.0)
        psi = rng.uniform(-0.4, 0.4)
        c = mapping.uet_couplings(psi, xi, kappa)
        alpha, beta = mapping.def_alpha_beta(c, kappa)
        assert rel_diff(alpha, alpha_s(psi, kappa, xi)) < TOL
        assert rel_diff(beta, beta_s(psi, kappa, xi)) < TOL
    for xi in (-0.1, 0.5, 2.0, 2.4):
        params = mapping.uet_def_parameters(xi, kappa=1.3)
        assert params["alpha0"] == 0.0 or abs(params["alpha0"]) < 1e-15
        assert rel_diff(params["beta0"], -2.0 * xi) < TOL
        assert abs(params["gamma_ppn_minus_1"]) < 1e-15


def test_einstein_frame_mass_at_origin_matches_sympy() -> None:
    psi, kappa, xi, m2, lam, Lam, rho = sp.symbols("psi kappa xi_c m2 lambda Lambda rho", real=True)
    F = 1 + kappa * xi * psi**2
    V_J = m2 * psi**2 / 2 + lam * psi**4 / 4 + F * Lam / kappa + rho
    V_star = V_J / F**2
    # canonical Einstein-frame field equals psi to second order at psi = 0 (s'(0) = 0)
    m_star2 = sp.diff(V_star, psi, 2).subs(psi, 0)
    rng = random.Random(6000)
    for _ in range(20):
        vals = {kappa: rng.uniform(0.3, 3), xi: rng.uniform(-1, 3), m2: rng.uniform(0, 2),
                lam: rng.uniform(0, 2), Lam: rng.uniform(-0.5, 0.5), rho: rng.uniform(-0.5, 0.5)}
        expected = float(m_star2.subs(vals))
        got = mapping.uet_einstein_frame_mass_sq_at_origin(
            vals[m2], vals[xi], vals[kappa], Lambda=vals[Lam], vacuum_density=vals[rho])
        assert rel_diff(got, expected) < TOL
