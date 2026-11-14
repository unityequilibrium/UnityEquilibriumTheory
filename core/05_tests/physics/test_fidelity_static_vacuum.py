"""Fidelity check for author point 3 ("nothing can stay still"), wave A1.

Question: does the classical parent action (Theory Card UET_PARENT v1) admit a
static solution in which nothing moves? The check goes through the general
residual functions with epsilon > 0, at random parameter points.

Result recorded in docs/core/FIDELITY_MATRIX.md: a static vacuum exists exactly
when Lambda_eff = Lambda + kappa*epsilon*rho_star = 0. With Lambda_eff > 0 the
flat static vacuum is not a solution (the vacuum is de Sitter and expands).
"""

from __future__ import annotations

import random

import numpy as np
import pytest

from docs.core.uet_covariant_matter import (
    CovariantMatterConfig,
    coupled_metric_residual,
    coupled_response_scalar_equation_residual,
    matter_eom_residual,
)
from docs.core.uet_covariant_response import CovariantResponseConfig

pytestmark = pytest.mark.physics

ETA = np.diag([-1.0, 1.0, 1.0, 1.0])
ZERO4 = np.zeros((4, 4))
ZERO_DOUBLET = np.zeros(2)
ZERO_DOUBLET_GRAD = np.zeros((2, 4))
TOL = 1e-12


def _configs(rng: random.Random, lambda_eff: float):
    u = rng.uniform
    eps, kappa, rho = u(0.1, 1.0), u(0.5, 2.0), u(-0.3, 0.3)
    response = CovariantResponseConfig(
        epsilon_nc=eps, einstein_coupling=kappa,
        cosmological_constant=lambda_eff - kappa * eps * rho,
        phi_equilibrium=u(-0.5, 0.5), response_kinetic=u(0.5, 2.0), response_mass_sq=u(0.1, 1.5),
        response_quartic=u(0.1, 1.5), curvature_coupling=u(-0.6, 0.6), equilibrium_density=rho,
    )
    matter = CovariantMatterConfig(
        matter_kinetic=u(0.5, 2.0), matter_mass_sq=u(0.1, 1.5), matter_quartic=u(0.1, 1.5),
        response_coupling=u(0.0, 1.5),
    )
    return response, matter


def _residuals(response: CovariantResponseConfig, matter: CovariantMatterConfig):
    phi = response.phi_equilibrium
    scalar = coupled_response_scalar_equation_residual(0.0, 0.0, phi, ZERO_DOUBLET, response, matter)
    chi = matter_eom_residual(ZERO_DOUBLET, ZERO_DOUBLET, phi, response, matter)
    metric = coupled_metric_residual(
        ETA, ZERO4, phi, np.zeros(4), ZERO4, ZERO_DOUBLET, ZERO_DOUBLET_GRAD, response, matter,
    )
    return float(abs(scalar)), float(np.max(np.abs(chi))), float(np.max(np.abs(metric)))


@pytest.mark.parametrize("seed", range(20))
def test_static_vacuum_solves_all_equations_when_lambda_eff_vanishes(seed: int) -> None:
    response, matter = _configs(random.Random(seed), lambda_eff=0.0)
    scalar, chi, metric = _residuals(response, matter)
    assert scalar < TOL and chi < TOL and metric < TOL


@pytest.mark.parametrize("seed", range(20))
def test_flat_static_vacuum_fails_when_lambda_eff_is_positive(seed: int) -> None:
    # Negative control: with Lambda_eff > 0 the metric equation is not satisfied by
    # Minkowski space, so the residual must be detected.
    rng = random.Random(1000 + seed)
    response, matter = _configs(rng, lambda_eff=rng.uniform(0.05, 0.3))
    _, _, metric = _residuals(response, matter)
    assert metric > 1e-3
