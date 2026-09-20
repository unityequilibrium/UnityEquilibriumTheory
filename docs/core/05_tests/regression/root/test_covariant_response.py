"""Focused tests for the conservative covariant response evaluator."""

from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_covariant_response import (
    CovariantResponseConfig,
    conservative_action_density,
    curvature_factor,
    curvature_factor_base_derivative,
    effective_cosmological_constant,
    einstein_gr_residual,
    model_contract,
    response_potential,
    response_potential_derivative,
    response_potential_hessian,
    response_scalar_equation_residual,
    response_stress_tensor,
    uet_metric_residual,
    validate_lorentz_metric,
)


def _geometry() -> tuple[np.ndarray, np.ndarray]:
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    basis = np.array(
        [[1.0, .1, 0, 0], [.03, 1.05, .04, 0], [0, .02, .95, .05], [0, 0, .02, 1.02]]
    )
    metric = basis.T @ eta @ basis
    return metric, np.linalg.inv(metric)


def _symmetric(seed: int, scale: float = 1.0) -> np.ndarray:
    raw = np.random.default_rng(seed).normal(scale=scale, size=(4, 4))
    return 0.5 * (raw + raw.T)


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("epsilon_nc", -1.0, ValueError),
        ("einstein_coupling", 0.0, ValueError),
        ("response_kinetic", 0.0, ValueError),
        ("response_mass_sq", -1.0, ValueError),
        ("response_quartic", 0.0, ValueError),
        ("unit_lane", "SI", NotImplementedError),
    ],
)
def test_config_rejects_out_of_contract_values(
    field: str, value: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        CovariantResponseConfig(**{field: value})


def test_ordered_reference_and_potential_derivative_are_exact() -> None:
    cfg = CovariantResponseConfig(
        epsilon_nc=.4,
        phi_equilibrium=.3,
        response_mass_sq=1.2,
        response_quartic=.7,
        curvature_coupling=.2,
        equilibrium_density=.05,
    )
    p0 = cfg.phi_equilibrium
    assert curvature_factor(p0, cfg) == 1.0
    assert curvature_factor_base_derivative(p0, cfg) == 0.0
    assert response_potential(p0, cfg) == cfg.equilibrium_density
    assert response_potential_derivative(p0, cfg) == 0.0
    assert response_potential_hessian(p0, cfg) == cfg.response_mass_sq

    phi, h = .61, 1e-6
    finite_difference = (
        response_potential(phi + h, cfg) - response_potential(phi - h, cfg)
    ) / (2 * h)
    assert finite_difference == pytest.approx(
        response_potential_derivative(phi, cfg), rel=1e-9, abs=1e-10
    )


def test_gr_closed_limit_is_componentwise_exact_for_arbitrary_response() -> None:
    metric, inverse = _geometry()
    einstein, matter = _symmetric(1), _symmetric(2)
    cfg = CovariantResponseConfig(
        epsilon_nc=0.0,
        einstein_coupling=.37,
        cosmological_constant=.02,
        curvature_coupling=-8.0,
        equilibrium_density=9.0,
    )
    expected = einstein_gr_residual(metric, einstein, matter, cfg)
    actual = uet_metric_residual(
        metric,
        einstein,
        matter,
        phi=1e100,
        gradient_phi=np.full(4, 1e100),
        curvature_factor_base_hessian=np.full((4, 4), 1e200),
        config=cfg,
        inverse_metric=inverse,
    )
    assert np.array_equal(actual, expected)
    assert response_scalar_equation_residual(9.0, -2.0, 1e100, cfg) == 0.0


def test_response_stress_and_metric_residual_transform_as_covariant_tensors() -> None:
    metric, inverse = _geometry()
    einstein, matter, hessian = _symmetric(3), _symmetric(4), _symmetric(5, .1)
    gradient = np.array([.2, -.1, .05, .08])
    cfg = CovariantResponseConfig(
        epsilon_nc=.2,
        einstein_coupling=.7,
        cosmological_constant=.01,
        curvature_coupling=.04,
        equilibrium_density=.02,
    )
    residual = uet_metric_residual(
        metric, einstein, matter, .4, gradient, hessian, cfg, inverse_metric=inverse
    )
    stress = response_stress_tensor(metric, inverse, gradient, .4, cfg)
    np.testing.assert_allclose(stress, stress.T, rtol=0.0, atol=1e-14)

    transform = np.array(
        [[1, .06, 0, 0], [.02, .97, .03, 0], [0, .01, 1.04, .05], [0, 0, .03, .96]],
        dtype=float,
    )
    transform_inverse = np.linalg.inv(transform)
    transformed = uet_metric_residual(
        transform.T @ metric @ transform,
        transform.T @ einstein @ transform,
        transform.T @ matter @ transform,
        .4,
        transform.T @ gradient,
        transform.T @ hessian @ transform,
        cfg,
        inverse_metric=transform_inverse @ inverse @ transform_inverse.T,
    )
    np.testing.assert_allclose(
        transformed, transform.T @ residual @ transform, rtol=1e-12, atol=1e-12
    )


def test_action_density_has_the_expected_coordinate_density_weight() -> None:
    metric, inverse = _geometry()
    gradient = np.array([.12, -.03, .04, .08])
    cfg = CovariantResponseConfig(epsilon_nc=.3, curvature_coupling=.02)
    original = conservative_action_density(
        metric, inverse, .15, gradient, .2, -.04, cfg
    )
    transform = np.diag([1.1, .9, 1.03, .97])
    ti = np.linalg.inv(transform)
    transformed = conservative_action_density(
        transform.T @ metric @ transform,
        ti @ inverse @ ti.T,
        .15,
        transform.T @ gradient,
        .2,
        -.04,
        cfg,
    )
    assert transformed == pytest.approx(abs(np.linalg.det(transform)) * original)


def test_equilibrium_density_is_reported_as_lambda_shift() -> None:
    cfg = CovariantResponseConfig(
        epsilon_nc=.25,
        einstein_coupling=.5,
        cosmological_constant=.01,
        equilibrium_density=.08,
    )
    assert effective_cosmological_constant(cfg) == pytest.approx(.02)


def test_invalid_metric_and_negative_curvature_factor_are_rejected() -> None:
    with pytest.raises(ValueError, match="Lorentz signature"):
        validate_lorentz_metric(np.eye(4))
    cfg = CovariantResponseConfig(epsilon_nc=1.0, curvature_coupling=-2.0)
    with pytest.raises(ValueError, match="positive"):
        curvature_factor(1.0, cfg)


def test_public_contract_keeps_trace_and_physical_claims_disconnected() -> None:
    contract = model_contract()
    assert contract["gr_null_parameter"] == {"epsilon_nc": 0.0}
    assert contract["derived_trace_imported"] is False
    assert contract["derived_trace_backreaction"] is False
    assert "not_a_metric_pde_solver" in contract["claim_boundary"]
