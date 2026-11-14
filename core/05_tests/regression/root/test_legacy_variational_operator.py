import numpy as np
import pytest

from docs.core.uet_master_equation import (
    LEGACY_OPERATOR_MODE,
    LEGACY_VARIATIONAL_OPERATOR_MODE,
    SUPPORTED_OPERATOR_MODES,
    dynamics_step_complete,
    information_propagator_step,
    legacy_reaction_derivative,
    potential_V,
    potential_derivative,
    conserved_laplacian,
    omega_functional_complete,
)
from docs.core.uet_parameters import UETParameters, landauer_minimum_energy


def _pure_params(**overrides):
    values = dict(
        alpha=1.0,
        gamma=0.025,
        C0=1.0,
        kappa=0.0,
        beta=0.0,
        W_N=0.0,
        a0_viscosity=0.0,
        tau_inertia=0.0,
    )
    values.update(overrides)
    return UETParameters(**values)


def test_variational_mode_is_explicitly_opt_in():
    assert LEGACY_VARIATIONAL_OPERATOR_MODE == "legacy_variational_v1"
    assert LEGACY_VARIATIONAL_OPERATOR_MODE in SUPPORTED_OPERATOR_MODES
    assert UETParameters().operator_mode == LEGACY_OPERATOR_MODE


def test_declared_radial_potential_and_derivative_are_a_pair():
    params = _pure_params()
    C = np.array([-1.5, -0.75, 0.0, 0.5, 1.0, 1.5, 2.0])
    epsilon = 1.0e-6
    finite_difference = (
        potential_V(C + epsilon, params) - potential_V(C - epsilon, params)
    ) / (2.0 * epsilon)
    np.testing.assert_allclose(
        potential_derivative(C, params), finite_difference, rtol=0.0, atol=1.0e-8
    )


def test_legacy_local_preserves_historical_reaction_while_variational_mode_uses_exact_pair():
    params = _pure_params()
    C = np.array([0.5, 1.5])
    dt = 0.01
    legacy = dynamics_step_complete(C, dt=dt, params=params)
    variational = dynamics_step_complete(
        C, dt=dt, params=params, operator_mode=LEGACY_VARIATIONAL_OPERATOR_MODE
    )
    np.testing.assert_allclose(
        legacy, C - dt * legacy_reaction_derivative(C, params), rtol=0.0, atol=1.0e-14
    )
    np.testing.assert_allclose(
        variational, C - dt * potential_derivative(C, params), rtol=0.0, atol=1.0e-14
    )
    assert not np.allclose(legacy, variational)


def test_variational_information_source_matches_positive_coupling_gradient():
    params = _pure_params(beta=0.2, kappa_I=0.0)
    C = np.ones(4)
    I = np.zeros(4)
    dt = 0.1
    updated = information_propagator_step(
        I, C, dx=1.0, dt=dt, params=params,
        operator_mode=LEGACY_VARIATIONAL_OPERATOR_MODE,
    )
    np.testing.assert_allclose(updated, -dt * params.beta * C)


def test_variational_mode_rejects_unclosed_legacy_forces():
    params = _pure_params(W_N=0.1)
    with pytest.raises(ValueError, match="pure normalized gradient terms"):
        dynamics_step_complete(
            np.ones(4), dt=0.01, params=params,
            operator_mode=LEGACY_VARIATIONAL_OPERATOR_MODE,
        )

def test_variational_information_operator_uses_periodic_laplacian():
    params = _pure_params(beta=0.0, kappa_I=0.0)
    I = np.array([0.0, 1.0, 0.0, 0.0, 0.0])
    C = np.zeros_like(I)
    updated = information_propagator_step(
        I, C, dx=1.0, dt=0.1, params=params,
        operator_mode=LEGACY_VARIATIONAL_OPERATOR_MODE,
    )
    expected = I + 0.1 * conserved_laplacian(I, 1.0)
    np.testing.assert_allclose(updated, expected, rtol=0.0, atol=1.0e-14)
    assert updated[0] > 0.0
    assert updated[-1] == 0.0


def test_canonical_functional_has_matching_C_and_I_directional_derivative():
    params = _pure_params(
        kappa=0.2,
        beta=0.4,
        kappa_I=0.3,
    )
    dx = 0.25
    C = np.array([0.2, -0.1, 0.35, 0.05, -0.25, 0.15])
    I = np.array([-0.3, 0.1, 0.2, -0.15, 0.05, 0.25])
    dC = np.array([0.1, -0.2, 0.05, 0.3, -0.1, 0.15])
    dI = np.array([-0.2, 0.1, 0.25, -0.05, 0.2, -0.1])
    epsilon = 1.0e-6

    def omega(c_field, i_field):
        return omega_functional_complete(
            c_field,
            I=i_field,
            dx=dx,
            params=params,
            operator_mode=LEGACY_VARIATIONAL_OPERATOR_MODE,
        )

    finite_difference = (omega(C + epsilon * dC, I + epsilon * dI) - omega(
        C - epsilon * dC, I - epsilon * dI
    )) / (2.0 * epsilon)
    grad_C = potential_derivative(C, params) - params.kappa * conserved_laplacian(C, dx) + params.beta * I
    grad_I = -conserved_laplacian(I, dx) + params.kappa_I * I + params.beta * C
    directional = float(np.sum((grad_C * dC + grad_I * dI) * dx))
    np.testing.assert_allclose(finite_difference, directional, rtol=1.0e-6, atol=1.0e-8)


def test_beta_normalized_alias_is_not_the_SI_Landauer_energy():
    params = _pure_params(beta=0.23)
    assert params.beta_normalized == params.beta
    assert landauer_minimum_energy(300.0) > 0.0
    assert params.beta_normalized != landauer_minimum_energy(300.0)
