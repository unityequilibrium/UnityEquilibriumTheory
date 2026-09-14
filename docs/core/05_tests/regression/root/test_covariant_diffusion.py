"""Verification tests for the covariant conserved-current bridge."""

from __future__ import annotations

import inspect

import numpy as np
import pytest

from docs.core.uet_covariant_diffusion import (
    COVARIANT_DIFFUSION_STATUS,
    ConservedCurrentBridgeConfig,
    ConservedCurrentState,
    causal_current_rhs,
    compare_adiabatic_limit,
    compare_matter_space_conserved_rhs,
    conditioned_matter_chemical_potential,
    conditioned_matter_free_energy,
    current_bridge_contract,
    current_energy_balance,
    decompose_noether_current,
    face_divergence_1d,
    matter_equation_config_from_current_bridge,
    model_b_rhs,
    normalize_local_charge_and_current,
    principal_symbol_diagnostics,
)
from docs.core.uet_spatial import integral_1d


def _fields(seed: int = 190061, n: int = 64) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    return rng.normal(scale=0.12, size=n), rng.normal(scale=0.08, size=n)


def _state(
    boundary: str,
    *,
    seed: int = 190062,
    n: int = 64,
) -> ConservedCurrentState:
    rng = np.random.default_rng(seed)
    C = rng.normal(scale=0.12, size=n)
    count = n if boundary == "periodic" else n + 1
    flux = rng.normal(scale=0.04, size=count)
    if boundary == "zero_flux":
        flux[[0, -1]] = 0.0
    return ConservedCurrentState(C, flux)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("b_matter", 0.0),
        ("kappa_matter", -1.0),
        ("mobility_matter", 0.0),
        ("tau_current", 0.0),
        ("coupling_base", -0.1),
        ("epsilon_nc", -0.1),
        ("density_scale", 0.0),
    ],
)
def test_config_rejects_invalid_controls(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        ConservedCurrentBridgeConfig(**{field: value})


def test_noether_current_frame_decomposition_reconstructs_and_is_orthogonal() -> None:
    metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    velocity = 0.4
    gamma = 1.0 / np.sqrt(1.0 - velocity**2)
    four_velocity = np.array([gamma, gamma * velocity, 0.0, 0.0])
    current = np.array([1.7, -0.3, 0.2, -0.1])
    result = decompose_noether_current(metric, four_velocity, current)
    reconstructed = result.density * four_velocity + result.spatial_current
    assert np.max(np.abs(reconstructed - current)) <= 1e-15
    assert result.reconstruction_error <= 1e-15
    assert result.orthogonality_error <= 1e-15


def test_noether_current_decomposition_rejects_nonunit_velocity() -> None:
    with pytest.raises(ValueError, match=r"u_mu u\^mu"):
        decompose_noether_current(
            np.diag([-1.0, 1.0, 1.0, 1.0]),
            np.array([1.0, 0.2, 0.0, 0.0]),
            np.ones(4),
        )


def test_natural_to_normalized_charge_current_scaling() -> None:
    config = ConservedCurrentBridgeConfig(
        density_scale=2.0,
        length_scale=4.0,
        time_scale=0.5,
    )
    density, current = normalize_local_charge_and_current(
        np.array([4.0, -2.0]), np.array([32.0, 16.0]), config
    )
    np.testing.assert_allclose(density, [2.0, -1.0], rtol=0.0, atol=0.0)
    np.testing.assert_allclose(current, [2.0, 1.0], rtol=0.0, atol=0.0)


@pytest.mark.parametrize("boundary", ["periodic", "zero_flux"])
def test_continuity_rhs_conserves_total_charge(boundary: str) -> None:
    state = _state(boundary)
    _, response = _fields()
    config = ConservedCurrentBridgeConfig(
        a_matter=-0.4,
        kappa_matter=0.3,
        mobility_matter=0.7,
        tau_current=0.2,
        epsilon_nc=0.35,
        boundary_condition=boundary,
    )
    dC, _, _, _ = causal_current_rhs(state, response, 0.2, config)
    assert abs(integral_1d(dC, 0.2)) <= 1e-13


@pytest.mark.parametrize("boundary", ["periodic", "zero_flux"])
def test_semi_discrete_extended_energy_identity_closes(boundary: str) -> None:
    state = _state(boundary)
    _, response = _fields()
    config = ConservedCurrentBridgeConfig(
        a_matter=-0.35,
        b_matter=0.8,
        kappa_matter=0.25,
        mobility_matter=0.6,
        tau_current=0.3,
        coupling_base=0.2,
        epsilon_nc=0.4,
        boundary_condition=boundary,
    )
    result = current_energy_balance(state, response, 0.2, config)
    assert result["current_dissipation"] >= 0.0
    assert abs(result["closure_residual"]) <= 2e-13


@pytest.mark.parametrize("boundary", ["periodic", "zero_flux"])
def test_adiabatic_flux_limit_is_exact_discrete_model_b(boundary: str) -> None:
    C, response = _fields()
    config = ConservedCurrentBridgeConfig(
        a_matter=-0.5,
        b_matter=0.9,
        kappa_matter=0.2,
        mobility_matter=0.75,
        tau_current=0.25,
        epsilon_nc=0.4,
        boundary_condition=boundary,
    )
    result = compare_adiabatic_limit(C, response, 0.2, config)
    assert result["max_abs_difference"] <= 2e-13


@pytest.mark.parametrize("epsilon", [0.0, 0.3, 1.0])
def test_model_b_limit_maps_to_existing_conserved_matter_rhs(epsilon: float) -> None:
    C, response = _fields()
    config = ConservedCurrentBridgeConfig(
        a_matter=-0.5,
        b_matter=0.9,
        kappa_matter=0.2,
        mobility_matter=0.75,
        tau_current=0.25,
        coupling_base=0.3,
        epsilon_nc=epsilon,
    )
    result = compare_matter_space_conserved_rhs(C, response, 0.2, config)
    assert result["max_abs_difference"] <= 2e-13
    assert result["mapped_config"].coupling_g == pytest.approx(
        epsilon * config.coupling_base
    )


def test_gr_null_matter_equation_is_independent_of_space_response() -> None:
    C, response = _fields()
    config = ConservedCurrentBridgeConfig(
        a_matter=-0.5,
        kappa_matter=0.2,
        epsilon_nc=0.0,
        coupling_base=1e6,
    )
    first = model_b_rhs(C, response, 0.2, config)
    second = model_b_rhs(C, response + 1e9, 0.2, config)
    np.testing.assert_allclose(first, second, rtol=0.0, atol=0.0)


def test_conditioned_free_energy_derivative_matches_chemical_potential() -> None:
    C, response = _fields()
    rng = np.random.default_rng(190063)
    direction = rng.normal(size=C.size)
    direction /= np.linalg.norm(direction)
    config = ConservedCurrentBridgeConfig(
        a_matter=-0.3,
        b_matter=0.7,
        kappa_matter=0.25,
        coupling_base=0.2,
        epsilon_nc=0.6,
    )
    step = 1e-6
    finite_difference = (
        conditioned_matter_free_energy(C + step * direction, response, 0.2, config)
        - conditioned_matter_free_energy(C - step * direction, response, 0.2, config)
    ) / (2.0 * step)
    chemical = conditioned_matter_chemical_potential(C, response, 0.2, config)
    predicted = integral_1d(chemical * direction, 0.2)
    assert abs(finite_difference - predicted) <= 1e-9


def test_local_convex_control_has_bounded_characteristic_speed() -> None:
    C = np.linspace(-0.1, 0.1, 64)
    response = np.zeros_like(C)
    config = ConservedCurrentBridgeConfig(
        a_matter=0.4,
        b_matter=0.2,
        kappa_matter=0.0,
        mobility_matter=0.1,
        tau_current=0.5,
    )
    result = principal_symbol_diagnostics(C, response, config)
    assert result["status"] == "PASS_LOCAL_CONVEX_MAXWELL_CATTANEO"
    assert result["strict_causal_claim_allowed"] is True
    assert result["within_normalized_light_cone"] is True


def test_local_convex_control_rejects_superluminal_parameterization() -> None:
    C = np.zeros(64)
    response = np.zeros_like(C)
    result = principal_symbol_diagnostics(
        C,
        response,
        ConservedCurrentBridgeConfig(
            a_matter=1.0,
            kappa_matter=0.0,
            mobility_matter=2.0,
            tau_current=0.1,
        ),
    )
    assert result["status"] == "FAIL_SUPERLUMINAL_PARAMETERIZATION"
    assert result["strict_causal_claim_allowed"] is False


def test_gradient_phase_field_keeps_uv_causality_blocked() -> None:
    C = np.zeros(64)
    response = np.zeros_like(C)
    result = principal_symbol_diagnostics(
        C,
        response,
        ConservedCurrentBridgeConfig(
            a_matter=1.0,
            kappa_matter=0.2,
            mobility_matter=0.1,
            tau_current=0.5,
        ),
    )
    assert result["status"] == "BLOCKED_FOURTH_ORDER_UV_CAUSALITY"
    assert result["high_k_phase_speed_coefficient"] > 0.0
    assert result["strict_causal_claim_allowed"] is False


def test_spinodal_lane_keeps_hyperbolicity_blocked() -> None:
    C = np.zeros(64)
    response = np.zeros_like(C)
    result = principal_symbol_diagnostics(
        C,
        response,
        ConservedCurrentBridgeConfig(a_matter=-1.0, kappa_matter=0.0),
    )
    assert result["status"] == "BLOCKED_NONCONVEX_OR_SPINODAL"
    assert result["local_convex"] is False


def test_local_control_is_not_silently_mapped_to_positive_kappa_operator() -> None:
    with pytest.raises(ValueError, match="kappa_matter > 0"):
        matter_equation_config_from_current_bridge(
            ConservedCurrentBridgeConfig(kappa_matter=0.0)
        )


def test_face_divergence_rejects_wrong_boundary_shape() -> None:
    with pytest.raises(ValueError, match="shape"):
        face_divergence_1d(np.zeros(64), 64, 0.2, "zero_flux")


def test_contract_preserves_ontology_and_trace_boundary() -> None:
    contract = current_bridge_contract()
    assert contract["status"] == COVARIANT_DIFFUSION_STATUS
    assert "not_the_scalar_amplitude" in contract["forbidden_identification"]
    assert contract["derived_trace_backreaction"] is False
    assert contract["full_gradient_phase_field_causality"].startswith("BLOCKED")
    assert contract["next_controller"] == (
        "uniform_subluminal_hyperbolic_phase_field_and_covariant_mapping_missing"
    )
    assert "trace" not in inspect.signature(causal_current_rhs).parameters
