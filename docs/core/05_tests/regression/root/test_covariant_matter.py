"""Focused tests for the covariant O(2) matter-action pilot."""

from __future__ import annotations

import inspect

import numpy as np
import pytest

from docs.core.uet_covariant_matter import (
    CovariantMatterConfig,
    coupled_conservative_action_density,
    coupled_matter_lagrangian_scalar,
    coupled_matter_stress_tensor,
    coupled_metric_residual,
    coupled_response_scalar_equation_residual,
    interaction_energy_density,
    joint_potential_energy,
    matter_action_contract,
    matter_current_divergence,
    matter_current_divergence_from_eom,
    matter_eom_residual,
    matter_noether_current,
    matter_on_shell_box,
    matter_potential,
    reciprocal_interaction_derivatives,
)
from docs.core.uet_covariant_response import (
    CovariantResponseConfig,
    einstein_gr_residual,
)


def _geometry() -> tuple[np.ndarray, np.ndarray]:
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    basis = np.array(
        [[1.0, .08, 0, 0], [.02, 1.04, .03, 0], [0, .01, .96, .04], [0, 0, .02, 1.01]]
    )
    metric = basis.T @ eta @ basis
    return metric, np.linalg.inv(metric)


def _configs(epsilon: float = .3) -> tuple[CovariantResponseConfig, CovariantMatterConfig]:
    return (
        CovariantResponseConfig(
            epsilon_nc=epsilon,
            phi_equilibrium=.1,
            response_kinetic=1.2,
            response_mass_sq=.8,
            response_quartic=.4,
            curvature_coupling=.03,
        ),
        CovariantMatterConfig(
            matter_kinetic=.9,
            matter_mass_sq=-.4,
            matter_quartic=.7,
            response_coupling=.25,
        ),
    )


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"matter_kinetic": 0.0}, ValueError),
        ({"matter_quartic": 0.0}, ValueError),
        ({"response_coupling": -1.0}, ValueError),
        ({"matter_mass_sq": float("nan")}, ValueError),
        ({"unit_lane": "SI"}, NotImplementedError),
    ],
)
def test_config_rejects_out_of_contract_values(
    kwargs: dict[str, object], error: type[Exception]
) -> None:
    with pytest.raises(error):
        CovariantMatterConfig(**kwargs)


def test_potential_and_lagrangian_are_global_o2_invariant() -> None:
    response, matter = _configs()
    metric, inverse = _geometry()
    fields = np.array([.31, -.17])
    gradients = np.array([[.1, -.02, .03, .04], [-.04, .06, .01, -.03]])
    theta = .47
    rotation = np.array(
        [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]]
    )
    assert matter_potential(rotation @ fields, matter) == pytest.approx(
        matter_potential(fields, matter)
    )
    original = coupled_matter_lagrangian_scalar(
        inverse, gradients, fields, .26, response, matter
    )
    rotated = coupled_matter_lagrangian_scalar(
        inverse, rotation @ gradients, rotation @ fields, .26, response, matter
    )
    assert rotated == pytest.approx(original, rel=0.0, abs=1e-14)
    assert np.linalg.det(metric) < 0.0


def test_interaction_derivatives_are_reciprocal_finite_differences() -> None:
    response, matter = _configs()
    phi = .28
    fields = np.array([.23, -.19])
    response_derivative, matter_derivative = reciprocal_interaction_derivatives(
        phi, fields, response, matter
    )
    step = 1e-6
    fd_phi = (
        interaction_energy_density(phi + step, fields, response, matter)
        - interaction_energy_density(phi - step, fields, response, matter)
    ) / (2.0 * step)
    assert fd_phi == pytest.approx(response_derivative, rel=1e-9, abs=1e-11)
    for index in range(2):
        plus, minus = fields.copy(), fields.copy()
        plus[index] += step
        minus[index] -= step
        finite_difference = (
            interaction_energy_density(phi, plus, response, matter)
            - interaction_energy_density(phi, minus, response, matter)
        ) / (2.0 * step)
        assert finite_difference == pytest.approx(
            matter_derivative[index], rel=1e-9, abs=1e-11
        )


def test_matter_and_response_equations_receive_same_action_coupling() -> None:
    response, matter = _configs()
    fields = np.array([.27, -.11])
    phi = .34
    uncoupled_matter = matter_eom_residual(
        np.zeros(2), fields, phi, response, matter
    )
    no_coupling = matter_eom_residual(
        np.zeros(2),
        fields,
        phi,
        response,
        CovariantMatterConfig(
            matter_kinetic=matter.matter_kinetic,
            matter_mass_sq=matter.matter_mass_sq,
            matter_quartic=matter.matter_quartic,
            response_coupling=0.0,
        ),
    )
    expected_shift = (
        response.epsilon_nc
        * matter.response_coupling
        * (phi - response.phi_equilibrium)
        * fields
    )
    np.testing.assert_allclose(uncoupled_matter - no_coupling, expected_shift)

    coupled_response = coupled_response_scalar_equation_residual(
        .0, .0, phi, fields, response, matter
    )
    uncoupled_response = coupled_response_scalar_equation_residual(
        .0,
        .0,
        phi,
        fields,
        response,
        CovariantMatterConfig(response_coupling=0.0),
    )
    assert coupled_response - uncoupled_response == pytest.approx(
        .5 * response.epsilon_nc * matter.response_coupling * np.dot(fields, fields)
    )


def test_noether_current_identity_and_on_shell_conservation_are_exact() -> None:
    response, matter = _configs()
    fields = np.array([.29, -.13])
    box = np.array([.07, -.03])
    residual = matter_eom_residual(box, fields, .25, response, matter)
    direct = matter_current_divergence(box, fields, matter)
    from_eom = matter_current_divergence_from_eom(residual, fields)
    assert direct == pytest.approx(from_eom, rel=0.0, abs=1e-15)

    on_shell = matter_on_shell_box(fields, .25, response, matter)
    np.testing.assert_allclose(
        matter_eom_residual(on_shell, fields, .25, response, matter),
        0.0,
        atol=1e-15,
    )
    assert matter_current_divergence(on_shell, fields, matter) == pytest.approx(
        0.0, abs=1e-15
    )


def test_noether_current_transforms_as_a_contravariant_vector() -> None:
    _, matter = _configs()
    metric, inverse = _geometry()
    fields = np.array([.2, -.14])
    gradients = np.array([[.09, -.03, .04, .02], [-.02, .05, .01, -.04]])
    current = matter_noether_current(inverse, fields, gradients, matter)
    transform = np.array(
        [[1.0, .05, 0, 0], [.02, .98, .03, 0], [0, .01, 1.03, .02], [0, 0, .02, .97]]
    )
    transform_inverse = np.linalg.inv(transform)
    transformed_inverse_metric = transform_inverse @ inverse @ transform_inverse.T
    transformed = matter_noether_current(
        transformed_inverse_metric,
        fields,
        np.einsum("mn,an->am", transform.T, gradients),
        matter,
    )
    np.testing.assert_allclose(
        transformed, transform_inverse @ current, rtol=1e-13, atol=1e-13
    )
    assert np.linalg.det(metric) < 0.0


def test_stress_tensor_and_total_action_density_are_covariant() -> None:
    response, matter = _configs()
    metric, inverse = _geometry()
    fields = np.array([.22, .16])
    matter_gradients = np.array([[.08, -.02, .03, .01], [.01, .05, -.04, .02]])
    gradient_phi = np.array([.07, -.01, .02, .04])
    stress = coupled_matter_stress_tensor(
        metric, inverse, fields, matter_gradients, .24, response, matter
    )
    np.testing.assert_allclose(stress, stress.T, atol=1e-14)
    action = coupled_conservative_action_density(
        metric,
        inverse,
        .13,
        gradient_phi,
        .24,
        fields,
        matter_gradients,
        response,
        matter,
    )
    transform = np.diag([1.08, .94, 1.03, .97])
    transform_inverse = np.linalg.inv(transform)
    transformed_action = coupled_conservative_action_density(
        transform.T @ metric @ transform,
        transform_inverse @ inverse @ transform_inverse.T,
        .13,
        transform.T @ gradient_phi,
        .24,
        fields,
        np.einsum("mn,an->am", transform.T, matter_gradients),
        response,
        matter,
    )
    assert transformed_action == pytest.approx(abs(np.linalg.det(transform)) * action)


def test_exact_gr_branch_keeps_scalar_matter_and_removes_response_coupling() -> None:
    response, matter = _configs(0.0)
    metric, inverse = _geometry()
    fields = np.array([.24, -.18])
    gradients = np.array([[.06, -.02, .01, .03], [-.03, .04, .02, -.01]])
    einstein = np.array(
        [[.2, .01, 0, 0], [.01, -.1, .02, 0], [0, .02, .07, .01], [0, 0, .01, .03]]
    )
    matter_stress = coupled_matter_stress_tensor(
        metric, inverse, fields, gradients, 1e50, response, matter
    )
    expected = einstein_gr_residual(metric, einstein, matter_stress, response)
    actual = coupled_metric_residual(
        metric,
        einstein,
        phi=1e50,
        gradient_phi=np.full(4, 1e50),
        curvature_factor_base_hessian=np.full((4, 4), 1e100),
        matter_doublet=fields,
        matter_gradients=gradients,
        response_config=response,
        matter_config=matter,
        inverse_metric=inverse,
    )
    assert np.array_equal(actual, expected)
    assert interaction_energy_density(1e50, fields, response, matter) == 0.0
    assert coupled_response_scalar_equation_residual(
        1e20, -1e20, 1e50, fields, response, matter
    ) == 0.0


def test_joint_potential_has_positive_quartic_asymptotics() -> None:
    response, matter = _configs()
    for direction in (
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([.4, .7, -.5]),
    ):
        direction = direction / np.linalg.norm(direction)
        phi = response.phi_equilibrium + 1e3 * direction[0]
        fields = 1e3 * direction[1:]
        assert joint_potential_energy(phi, fields, response, matter) >= 0.0


def test_contract_blocks_density_diffusion_particle_and_trace_claims() -> None:
    contract = matter_action_contract()
    assert contract["reciprocal_variation"] == "IMPLEMENTED_ACTION_LEVEL"
    assert contract["matter_current"] == "ON_SHELL_GLOBAL_O2_NOETHER_CURRENT"
    assert contract["diffusive_matter_dynamics"] == "NOT_DERIVED"
    assert contract["regular_normalized_epsilon_limit"] == "NOT_IMPLEMENTED"
    assert contract["particle_identity"] == "NOT_ESTABLISHED"
    assert contract["derived_trace_backreaction"] is False
    assert "trace" not in inspect.signature(matter_eom_residual).parameters
