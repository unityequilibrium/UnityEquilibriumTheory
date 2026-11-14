"""Gravitational-wave speed of the parent action (Theory Card UET_PARENT v1): c_T = 1.

A transverse-traceless wave g = eta + eps h, h_xx = -h_yy = A sin(k (t - z/v)), on the static vacuum of the
parent action (psi at equilibrium, chi = 0, Lambda_eff = 0) solves the implemented metric equation at first
order in eps only when v = 1. The Einstein tensor comes from the independent sympy geometry helpers; the
residual comes from the implementation. A negative control at v = 0.9 must leave a non-zero residual.

This is the structural reason the parent action passes the GW170817 speed test: F(phi) R couples to R
without derivatives of phi (Horndeski G4 independent of X), so tensor modes move at the speed of light.
"""

from __future__ import annotations

import random

import numpy as np
import pytest
import sympy as sp

from docs.core.uet_covariant_matter import CovariantMatterConfig, coupled_metric_residual
from docs.core.uet_covariant_response import CovariantResponseConfig

from ._symbolic_geometry import T, ZC, einstein_and_scalar

pytestmark = pytest.mark.physics

EPS, AMP, K, V = sp.symbols("eps A k v", positive=True)


def _first_order_einstein():
    h = AMP * sp.sin(K * (T - ZC / V))
    g = sp.diag(-1, 1 + EPS * h, 1 - EPS * h, 1)
    G, _, _, _ = einstein_and_scalar(g)
    return sp.Matrix(4, 4, lambda i, j: sp.diff(G[i, j], EPS).subs(EPS, 0))


G1 = _first_order_einstein()


def _configs(seed: int):
    rng = random.Random(seed)
    u = rng.uniform
    eps, kappa, rho = u(0.1, 1.0), u(0.5, 2.0), u(-0.3, 0.3)
    response = CovariantResponseConfig(
        epsilon_nc=eps, einstein_coupling=kappa, cosmological_constant=-kappa * eps * rho,  # Lambda_eff = 0
        phi_equilibrium=u(-0.5, 0.5), response_kinetic=u(0.5, 2.0), response_mass_sq=u(0.1, 1.5),
        response_quartic=u(0.1, 1.5), curvature_coupling=u(-0.6, 0.6), equilibrium_density=rho)
    matter = CovariantMatterConfig(matter_kinetic=u(0.5, 2.0), matter_mass_sq=u(0.1, 1.5),
                                   matter_quartic=u(0.1, 1.5), response_coupling=u(0.0, 1.5))
    return response, matter


def _linear_residual(speed: float, seed: int) -> float:
    """Max |d residual / d eps| at eps = 0 over random spacetime points, from the implemented metric equation."""
    rng = random.Random(100 + seed)
    response, matter = _configs(seed)
    worst = 0.0
    for _ in range(5):
        pt = {T: rng.uniform(0, 3), ZC: rng.uniform(-3, 3), AMP: 1.0, K: rng.uniform(0.5, 2.0), V: speed}
        g1 = np.array([[float(G1[i, j].subs(pt)) for j in range(4)] for i in range(4)])
        h_val = float((sp.sin(K * (T - ZC / V))).subs(pt))
        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        dg = np.diag([0.0, h_val, -h_val, 0.0])
        step = 1e-6
        res = []
        for s in (+step, -step):
            metric = eta + s * dg
            res.append(coupled_metric_residual(
                metric, s * g1, response.phi_equilibrium, np.zeros(4), np.zeros((4, 4)),
                np.zeros(2), np.zeros((2, 4)), response, matter))
        worst = max(worst, float(np.max(np.abs((res[0] - res[1]) / (2 * step)))))
    return worst


def test_first_order_einstein_tensor_vanishes_only_for_unit_speed() -> None:
    at_light = G1.subs(V, 1)
    assert all(sp.simplify(at_light[i, j]) == 0 for i in range(4) for j in range(4))
    off = sp.simplify(G1.subs(V, sp.Rational(9, 10))[1, 1])
    assert off != 0


@pytest.mark.parametrize("seed", range(5))
def test_parent_metric_equation_propagates_tensor_waves_at_c(seed: int) -> None:
    assert _linear_residual(1.0, seed) < 1e-8


def test_negative_control_slower_wave_is_not_a_solution() -> None:
    assert _linear_residual(0.9, 0) > 1e-3
