"""Physics checks for wave V2-EF (core/03_lanes/scalar_tensor/uet_card_v2_einstein.py), draft Card v2."""

from __future__ import annotations

import importlib
import math
import random

import numpy as np
import pytest
import sympy as sp

v2 = importlib.import_module("core.03_lanes.scalar_tensor.uet_card_v2")
ef = importlib.import_module("core.03_lanes.scalar_tensor.uet_card_v2_einstein")

pytestmark = pytest.mark.physics


def rand_card(rng, beta=None):
    u = rng.uniform
    return v2.CardV2(xi_phi=u(0.01, 2.0), xi_chi=u(-0.1, 1.0), lam_chi=u(0.2, 1.5), alpha=u(0.01, 0.6),
                     beta=u(0.0, 0.3) if beta is None else beta)


def rand_q(rng):
    return np.array([rng.uniform(0.5, 2.0), rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0)])


def test_einstein_frame_kinetic_metric_from_conformal_transformation() -> None:
    """Independent route: transform the Jordan Lagrangian of one scalar with F(phi) and read off K (sympy)."""
    phi, xi = sp.symbols("phi xi", positive=True)
    F = xi * phi**2
    # g_E = F g: sqrt(-g) F R / 2 = sqrt(-g_E) [R_E / 2 - (3/4) (grad ln F)^2_E]; -(1/2)(grad phi)^2 -> -(1/2F)(.)_E
    K_textbook = sp.simplify(sp.Rational(3, 2) * sp.diff(sp.log(F), phi) ** 2 + 1 / F)
    card = v2.CardV2(xi_phi=0.37, xi_chi=0.0, lam_chi=1.0, alpha=0.0, beta=0.0)
    for p in (0.4, 1.3, 2.2):
        num = ef.field_metric(card, (p, 0.0, 0.0))[0, 0]
        assert abs(num - float(K_textbook.subs({phi: p, xi: 0.37}))) < 1e-12
    assert sp.simplify(K_textbook - (1 + 6 * xi) / (xi * phi**2)) == 0


@pytest.mark.parametrize("seed", range(20))
def test_killing_one_form_is_grad_J_over_2F(seed: int) -> None:
    rng = random.Random(6100 + seed)
    card, q = rand_card(rng), rand_q(rng)
    a = ef.killing_one_form(card, q)
    b = ef.grad_J_over_2F(card, q)
    assert np.max(np.abs(a - b)) < 1e-12 * max(1.0, np.max(np.abs(b)))
    norm2 = float(q @ ef.field_metric(card, q) @ q)
    assert abs(norm2 - ef.J_of(card, q) / card.F(q[0], q[1] ** 2 + q[2] ** 2)) < 1e-12 * norm2


@pytest.mark.parametrize("seed", range(20))
def test_einstein_potential_is_flat_along_the_dilaton(seed: int) -> None:
    rng = random.Random(6200 + seed)
    card, q = rand_card(rng), rand_q(rng)
    u0 = ef.U(card, q)
    for s in (-1.3, -0.2, 0.7, 2.1):
        assert abs(ef.U(card, q * math.exp(s)) - u0) < 1e-12 * max(1.0, abs(u0))
    # control: the v1-style trilinear portal (dimensionful) breaks the flatness
    broken = lambda x: ef.U(card, x) - 0.1 * x[0] * (x[1] ** 2 + x[2] ** 2) / card.F(x[0], x[1] ** 2 + x[2] ** 2) ** 2  # noqa: E731
    assert abs(broken(q * math.exp(0.7)) - broken(q)) > 1e-6


@pytest.mark.parametrize("seed", range(20))
def test_degree_one_masses_give_zero_dilaton_charge(seed: int) -> None:
    rng = random.Random(6300 + seed)
    card, q = rand_card(rng), rand_q(rng)
    y1, y2, y3 = rng.uniform(0.1, 2), rng.uniform(0.1, 2), rng.uniform(0.1, 2)
    masses = [
        lambda x: y1 * abs(x[0]),                                           # Yukawa to the dilaton
        lambda x: y2 * math.sqrt(x[1] ** 2 + x[2] ** 2) + 1e-3 * abs(x[0]),  # Higgs-like
        lambda x: (y1 * abs(x[0]) ** 3 + y3 * (x[1] ** 2 + x[2] ** 2) ** 1.5) ** (1 / 3),  # generic degree 1
    ]
    for m in masses:
        assert abs(ef.dilaton_charge_def(card, m, q)) < 1e-8
        assert ef.gamma_minus_1(ef.dilaton_charge_def(card, m, q)) > -1e-15


@pytest.mark.parametrize("seed", range(20))
def test_fixed_masses_make_the_dilaton_brans_dicke(seed: int) -> None:
    rng = random.Random(6400 + seed)
    card, q = rand_card(rng), rand_q(rng)
    a = ef.dilaton_charge_def(card, lambda x: 0.938, q)
    F = card.F(q[0], q[1] ** 2 + q[2] ** 2)
    assert abs(a * a - 2 * F / ef.J_of(card, q)) < 1e-7
    # X -> 0 limit through the general path: alpha^2 -> 2 xi / (1 + 6 xi), the Brans-Dicke omega = 1 / (4 xi)
    q0 = np.array([q[0], 0.0, 0.0])
    a0 = ef.dilaton_charge_def(card, lambda x: 0.938, q0)
    omega = 1 / (4 * card.xi_phi)
    assert abs(a0 * a0 - 1 / (3 + 2 * omega)) < 1e-7


def test_cassini_bound_when_masses_are_fixed() -> None:
    xi = ef.brans_dicke_xi_bound()
    assert abs(xi - 5.75e-6) / 5.75e-6 < 2e-3
    card = v2.CardV2(xi_phi=xi, xi_chi=0.0, lam_chi=1.0, alpha=0.0, beta=0.0)
    a = ef.dilaton_charge_def(card, lambda x: 1.0, (1.0, 0.0, 0.0))
    assert abs(abs(ef.gamma_minus_1(a)) - ef.CASSINI_GAMMA) / ef.CASSINI_GAMMA < 1e-5


@pytest.mark.parametrize("seed", range(20))
def test_vacuum_spectrum_two_massless_one_heavy(seed: int) -> None:
    rng = random.Random(6500 + seed)
    card = rand_card(rng, beta=0.0)
    phi0 = rng.uniform(0.5, 2.0)
    m2 = ef.canonical_masses(card, phi0)
    # finite-difference Hessian (h = 1e-4): zero modes resolved to 1e-4 of the heavy mass
    assert abs(m2[0]) < 1e-4 * m2[2] and abs(m2[1]) < 1e-4 * m2[2]
    assert m2[2] > 0


@pytest.mark.parametrize("xi", [1e-2, 3e-3, 1e-3])
def test_radial_mass_decoupling_limit_converges(xi: float) -> None:
    """m_r^2 F -> 2 alpha phi0^2 (1 + alpha / lambda) as xi -> 0; the error falls linearly with xi."""
    errs = []
    for x in (xi, xi / 2, xi / 4):
        card = v2.CardV2(xi_phi=x, xi_chi=x / 3, lam_chi=0.8, alpha=0.05, beta=0.0)
        q = ef.vacuum(card, 1.0)
        F = card.F(q[0], q[1] ** 2)
        m2 = ef.canonical_masses(card, 1.0)[2] * F
        errs.append(abs(m2 / ef.jordan_radial_mass2_decoupled(card, 1.0) - 1))
    assert errs[-1] < 5 * xi
    assert 1.6 < errs[0] / errs[1] < 2.4 and 1.6 < errs[1] / errs[2] < 2.4


def test_beta_gives_a_constant_einstein_vacuum_energy() -> None:
    card = v2.CardV2(xi_phi=0.3, xi_chi=0.1, lam_chi=1.0, alpha=0.2, beta=0.05)
    q = ef.vacuum(card, 1.0)
    u = [ef.U(card, q * math.exp(s)) for s in (-2, 0, 3)]
    assert u[0] > 0 and max(u) - min(u) < 1e-14


def test_yukawa_ranges() -> None:
    assert abs(ef.yukawa_range_m(0.938) - 2.10e-16) / 2.10e-16 < 0.01
    assert abs(ef.yukawa_range_m(125.0) - 1.58e-18) / 1.58e-18 < 0.01


def test_fixed_mass_coupling_has_no_scalarisation_term() -> None:
    """With fixed masses and X = 0, ln A = -ln F / 2 is linear in the canonical dilaton: alpha_DEF is the same at
    every point of the orbit, so beta0 = d alpha / d phi_D = 0 and DEF spontaneous scalarisation (beta0 <= -4.35)
    cannot occur, unlike v1's beta0 = -2 xi_c (C_UET_DEF_MAPPING)."""
    card = v2.CardV2(xi_phi=0.8, xi_chi=0.2, lam_chi=1.0, alpha=0.0, beta=0.0)
    vals = [ef.dilaton_charge_def(card, lambda x: 1.0, (math.exp(s), 0.0, 0.0)) for s in (-2.0, 0.0, 1.5, 4.0)]
    assert max(vals) - min(vals) < 1e-8
    assert abs(vals[0] ** 2 - 2 * 0.8 / (1 + 6 * 0.8)) < 1e-8
