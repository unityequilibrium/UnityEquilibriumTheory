"""Tests for fixed-cone feasibility and the local current-law map."""

from __future__ import annotations

import inspect

import numpy as np
import pytest

from docs.core.uet_hyperbolic_phase_field import (
    HyperbolicPhaseFieldConfig,
    hyperbolicity_diagnostics,
)
from docs.core.uet_hyperbolic_phase_field_bridge import (
    HYPERBOLIC_PHASE_FIELD_BRIDGE_CONTROLLER,
    HYPERBOLIC_PHASE_FIELD_BRIDGE_STATUS,
    evaluate_parameter_sequence,
    fixed_cone_parabolic_limit_no_go,
    fixed_light_cone_feasibility,
    hyperbolic_phase_field_bridge_contract,
    map_external_flux_law_to_current,
    shifted_curvature_domain_bounds,
    subluminal_parameter_bounds,
)


def _config_at_bounds(max_abs_C: float = 1.0) -> HyperbolicPhaseFieldConfig:
    alpha = 1.5
    gamma = 0.2
    light_speed = 1.0
    tau = (alpha + 3.0 * max_abs_C**2 - 1.0) / light_speed**2
    beta = gamma / light_speed**2
    return HyperbolicPhaseFieldConfig(
        alpha_penalty=alpha,
        gamma_gradient=gamma,
        tau_flux=tau,
        beta_wave=beta,
        normalized_light_speed=light_speed,
    )


def test_bridge_status_is_analytic_not_covariant_derivation() -> None:
    assert HYPERBOLIC_PHASE_FIELD_BRIDGE_STATUS == (
        "ANALYTIC_NORMALIZED_CAUSAL_FEASIBILITY_NOT_COVARIANT_DERIVATION"
    )


def test_shifted_curvature_bounds_are_exact_on_symmetric_domain() -> None:
    result = shifted_curvature_domain_bounds(1.25, 1.4)
    assert result["minimum_shifted_curvature"] == pytest.approx(0.4)
    assert result["maximum_shifted_curvature"] == pytest.approx(
        1.4 + 3.0 * 1.25**2 - 1.0
    )
    grid = np.linspace(-1.25, 1.25, 10001)
    shifted = 1.4 + 3.0 * grid**2 - 1.0
    assert np.min(shifted) == pytest.approx(
        result["minimum_shifted_curvature"], abs=1e-14
    )
    assert np.max(shifted) == pytest.approx(
        result["maximum_shifted_curvature"], abs=1e-14
    )


def test_curvature_bounds_reject_invalid_domain() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        shifted_curvature_domain_bounds(-0.1, 1.2)
    with pytest.raises(ValueError, match="positive"):
        shifted_curvature_domain_bounds(1.0, 0.0)


def test_subluminal_bounds_follow_characteristic_speeds() -> None:
    config = HyperbolicPhaseFieldConfig(
        alpha_penalty=1.6,
        gamma_gradient=0.18,
        tau_flux=9.0,
        beta_wave=0.7,
        normalized_light_speed=1.25,
    )
    result = subluminal_parameter_bounds(1.1, config)
    assert result["minimum_tau_flux_for_cone"] == pytest.approx(
        (1.6 + 3.0 * 1.1**2 - 1.0) / 1.25**2
    )
    assert result["minimum_beta_wave_for_cone"] == pytest.approx(
        0.18 / 1.25**2
    )


def test_exact_bound_saturates_both_speed_families() -> None:
    result = fixed_light_cone_feasibility(1.0, _config_at_bounds())
    assert result["status"] == "PASS_NORMALIZED_FIXED_LIGHT_CONE_DOMAIN"
    assert result["within_fixed_light_cone"] is True
    assert result["matter_characteristic_speed_max"] == pytest.approx(1.0)
    assert result["auxiliary_characteristic_speed"] == pytest.approx(1.0)


def test_analytic_domain_bound_matches_sampled_wave7_diagnostics() -> None:
    config = HyperbolicPhaseFieldConfig(
        alpha_penalty=1.7,
        gamma_gradient=0.1,
        tau_flux=8.0,
        beta_wave=0.5,
    )
    density = np.linspace(-1.2, 1.2, 20001)
    sampled = hyperbolicity_diagnostics(density, config)
    analytic = fixed_light_cone_feasibility(1.2, config)
    assert analytic["matter_characteristic_speed_max"] == pytest.approx(
        sampled["matter_characteristic_speed_max"], abs=1e-14
    )
    assert analytic["auxiliary_characteristic_speed"] == pytest.approx(
        sampled["auxiliary_characteristic_speed"], abs=1e-14
    )


def test_tau_violation_fails_only_matter_family() -> None:
    base = _config_at_bounds()
    config = HyperbolicPhaseFieldConfig(
        alpha_penalty=base.alpha_penalty,
        gamma_gradient=base.gamma_gradient,
        tau_flux=0.99 * base.tau_flux,
        beta_wave=1.01 * base.beta_wave,
    )
    result = fixed_light_cone_feasibility(1.0, config)
    assert result["status"] == "FAIL_MATTER_CHARACTERISTIC_OUTSIDE_FIXED_CONE"
    assert result["matter_family_within_cone"] is False
    assert result["auxiliary_family_within_cone"] is True


def test_beta_violation_fails_only_auxiliary_family() -> None:
    base = _config_at_bounds()
    config = HyperbolicPhaseFieldConfig(
        alpha_penalty=base.alpha_penalty,
        gamma_gradient=base.gamma_gradient,
        tau_flux=1.01 * base.tau_flux,
        beta_wave=0.99 * base.beta_wave,
    )
    result = fixed_light_cone_feasibility(1.0, config)
    assert result["status"] == "FAIL_AUXILIARY_CHARACTERISTIC_OUTSIDE_FIXED_CONE"
    assert result["matter_family_within_cone"] is True
    assert result["auxiliary_family_within_cone"] is False


def test_non_strict_alpha_is_blocked_before_causal_claim() -> None:
    result = fixed_light_cone_feasibility(
        1.0,
        HyperbolicPhaseFieldConfig(
            alpha_penalty=1.0,
            tau_flux=10.0,
            gamma_gradient=0.1,
            beta_wave=1.0,
        ),
    )
    assert result["status"] == (
        "BLOCKED_NOT_STRICTLY_HYPERBOLIC_ON_SYMMETRIC_DOMAIN"
    )
    assert result["within_fixed_light_cone"] is False


def test_source_asymptotic_scaling_violates_uniform_domain_cone() -> None:
    gamma = np.array([0.2, 0.1, 0.05, 0.025])
    result = evaluate_parameter_sequence(
        alpha_values=1.0 / gamma,
        tau_values=gamma**2,
        beta_values=gamma**2,
        gamma_values=gamma,
        max_abs_C=1.0,
    )
    assert result["all_feasible"] is False
    assert not np.any(result["feasible"])
    assert np.all(result["tau_violation_factors"] > 1.0)
    assert np.all(result["beta_violation_factors"] > 1.0)
    assert np.all(np.diff(result["maximum_characteristic_speeds"]) > 0.0)


def test_fixed_cone_sequence_can_be_constructed_at_finite_parameters() -> None:
    alpha = np.array([1.1, 1.5, 2.0, 4.0])
    gamma = np.array([0.05, 0.1, 0.2, 0.4])
    tau_min = alpha + 2.0
    beta_min = gamma
    result = evaluate_parameter_sequence(
        alpha_values=alpha,
        tau_values=1.01 * tau_min,
        beta_values=1.01 * beta_min,
        gamma_values=gamma,
        max_abs_C=1.0,
    )
    assert result["all_feasible"] is True
    assert np.max(result["maximum_characteristic_speeds"]) < 1.0


def test_parabolic_and_fixed_cone_exact_limits_have_no_common_sequence() -> None:
    result = fixed_cone_parabolic_limit_no_go(
        max_abs_C=1.0, normalized_light_speed=1.0
    )
    assert result["status"] == "ANALYTIC_NO_COMMON_EXACT_LIMIT"
    assert result["common_exact_sequence_exists"] is False
    assert "low-wavenumber" in result["allowed_interpretation"]
    assert "all causal phase-field" in result["forbidden_generalization"]


def test_flux_impulse_map_closes_maxwell_cattaneo_law() -> None:
    rng = np.random.default_rng(8118)
    q = rng.normal(size=257)
    gradient = rng.normal(size=257)
    tau = 0.37
    result = map_external_flux_law_to_current(q, gradient, tau)
    assert np.max(np.abs(result.physical_current - q / tau)) == 0.0
    assert result.max_abs_residual <= 2e-15
    expected_q_rate = -gradient - q / tau
    assert np.max(np.abs(result.flux_impulse_rate - expected_q_rate)) == 0.0


def test_flux_map_rejects_nonconstant_invalid_tau_and_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="positive"):
        map_external_flux_law_to_current(np.ones(4), np.ones(4), 0.0)
    with pytest.raises(ValueError, match="matching shape"):
        map_external_flux_law_to_current(np.ones(4), np.ones(5), 1.0)


def test_contract_stops_at_algebraic_map() -> None:
    contract = hyperbolic_phase_field_bridge_contract()
    assert contract["mapping_layers"]["algebraic_local_current_law"] == "PASS"
    assert contract["mapping_layers"][
        "source_order_parameter_to_uet_noether_density"
    ] == "BLOCKED"
    assert contract["mapping_layers"][
        "classical_entropy_current_and_bianchi_closure"
    ] == "BLOCKED"
    assert contract["mapping_layers"][
        "thermal_stochastic_sk_kms_completion"
    ] == "BLOCKED_DOWNSTREAM"


def test_contract_keeps_auxiliary_phase_and_trace_out_of_uet_state_map() -> None:
    contract = hyperbolic_phase_field_bridge_contract()
    assert "external_auxiliary_phase_is_not_UET_space_response" in contract[
        "forbidden_identifications"
    ]
    assert contract["trace_input"] is False
    assert contract["trace_backreaction"] is False
    for function in (
        fixed_light_cone_feasibility,
        evaluate_parameter_sequence,
        map_external_flux_law_to_current,
    ):
        assert "trace" not in inspect.signature(function).parameters


def test_contract_preserves_global_and_topic_claim_boundaries() -> None:
    contract = hyperbolic_phase_field_bridge_contract()
    assert contract["global_universe_closure"] == "UNRESOLVED"
    assert contract["topic_0_11_status_impact"] == "NONE"
    assert contract["topic_0_19_status_impact"] == "NONE"
    assert contract["next_controller"] == (
        HYPERBOLIC_PHASE_FIELD_BRIDGE_CONTROLLER
    )
