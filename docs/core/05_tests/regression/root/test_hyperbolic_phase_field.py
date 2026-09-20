"""Tests for the external first-order hyperbolic phase-field comparator."""

from __future__ import annotations

import inspect

import numpy as np
import pytest

from docs.core.uet_hyperbolic_phase_field import (
    HYPERBOLIC_PHASE_FIELD_SOURCE_ARXIV,
    HYPERBOLIC_PHASE_FIELD_SOURCE_DOI,
    HYPERBOLIC_PHASE_FIELD_STATUS,
    HyperbolicPhaseFieldConfig,
    HyperbolicPhaseFieldState,
    analytic_characteristic_speeds,
    augmented_chemical_potential,
    compare_augmented_to_cahn_hilliard_chemical,
    double_well_curvature,
    double_well_derivative,
    double_well_potential,
    gradient_constraint_rate_residual,
    gradient_constraint_residual,
    hyperbolic_phase_field_contract,
    hyperbolic_phase_field_energy,
    hyperbolic_phase_field_energy_balance,
    hyperbolic_phase_field_rhs,
    hyperbolicity_diagnostics,
    paper_asymptotic_scaling_diagnostics,
    periodic_central_derivative,
    principal_matrix,
    quasistatic_auxiliary_phase,
)
from docs.core.uet_spatial import integral_1d


def _state(seed: int = 719, n: int = 96) -> HyperbolicPhaseFieldState:
    rng = np.random.default_rng(seed)
    return HyperbolicPhaseFieldState(
        C=rng.normal(scale=0.15, size=n),
        flux_impulse=rng.normal(scale=0.04, size=n),
        auxiliary_rate=rng.normal(scale=0.03, size=n),
        gradient_proxy=rng.normal(scale=0.08, size=n),
        auxiliary_phase=rng.normal(scale=0.12, size=n),
    )


def test_status_is_external_comparator() -> None:
    assert HYPERBOLIC_PHASE_FIELD_STATUS == (
        "EXTERNAL_FORMULA_COMPARATOR_NOT_UET_DERIVATION"
    )
    assert HYPERBOLIC_PHASE_FIELD_SOURCE_DOI == "10.1098/rspa.2024.0606"
    assert HYPERBOLIC_PHASE_FIELD_SOURCE_ARXIV == "2408.03862"


@pytest.mark.parametrize(
    "field",
    [
        "alpha_penalty",
        "beta_wave",
        "tau_flux",
        "gamma_gradient",
        "normalized_light_speed",
    ],
)
def test_config_rejects_nonpositive_coefficients(field: str) -> None:
    with pytest.raises(ValueError, match=field):
        HyperbolicPhaseFieldConfig(**{field: 0.0})


def test_config_rejects_nonperiodic_v1() -> None:
    with pytest.raises(NotImplementedError, match="periodic"):
        HyperbolicPhaseFieldConfig(boundary_condition="zero_flux")


def test_config_rejects_si_lane() -> None:
    with pytest.raises(NotImplementedError, match="normalized"):
        HyperbolicPhaseFieldConfig(unit_lane="SI")


def test_state_requires_matching_one_dimensional_fields() -> None:
    with pytest.raises(ValueError, match="must match C"):
        HyperbolicPhaseFieldState(
            np.zeros(8), np.zeros(7), np.zeros(8), np.zeros(8), np.zeros(8)
        )
    with pytest.raises(ValueError, match="one-dimensional"):
        HyperbolicPhaseFieldState(
            np.zeros((4, 4)),
            np.zeros(16),
            np.zeros(16),
            np.zeros(16),
            np.zeros(16),
        )


def test_state_copy_is_independent() -> None:
    state = _state()
    copied = state.copy()
    copied.C[0] += 1.0
    assert copied.C[0] != state.C[0]


def test_double_well_derivatives_close() -> None:
    values = np.linspace(-1.1, 1.1, 21)
    step = 1e-6
    first_fd = (
        double_well_potential(values + step)
        - double_well_potential(values - step)
    ) / (2.0 * step)
    second_fd = (
        double_well_derivative(values + step)
        - double_well_derivative(values - step)
    ) / (2.0 * step)
    assert np.max(np.abs(first_fd - double_well_derivative(values))) <= 1e-9
    assert np.max(np.abs(second_fd - double_well_curvature(values))) <= 1e-9


def test_periodic_derivative_has_zero_integral() -> None:
    field = _state().C
    assert abs(integral_1d(periodic_central_derivative(field, 0.2), 0.2)) <= 1e-14


def test_periodic_derivative_is_skew_adjoint() -> None:
    rng = np.random.default_rng(720)
    left = rng.normal(size=96)
    right = rng.normal(size=96)
    dx = 0.125
    residual = integral_1d(
        left * periodic_central_derivative(right, dx)
        + right * periodic_central_derivative(left, dx),
        dx,
    )
    assert abs(residual) <= 1e-13


def test_rhs_conserves_mass() -> None:
    rates = hyperbolic_phase_field_rhs(
        _state(), 0.125, HyperbolicPhaseFieldConfig()
    )
    assert abs(integral_1d(rates.C, 0.125)) <= 1e-13


def test_rhs_uses_q_over_tau_as_physical_flux() -> None:
    state = _state()
    config = HyperbolicPhaseFieldConfig(tau_flux=0.7)
    rates = hyperbolic_phase_field_rhs(state, 0.2, config)
    expected = -periodic_central_derivative(
        state.flux_impulse / config.tau_flux, 0.2
    )
    assert np.max(np.abs(rates.C - expected)) == 0.0


def test_augmented_chemical_formula() -> None:
    state = _state()
    config = HyperbolicPhaseFieldConfig(alpha_penalty=1.7)
    expected = double_well_derivative(state.C) + 1.7 * (
        state.C - state.auxiliary_phase
    )
    assert np.max(
        np.abs(
            augmented_chemical_potential(
                state.C, state.auxiliary_phase, config
            )
            - expected
        )
    ) == 0.0


def test_semi_discrete_energy_identity_closes() -> None:
    balance = hyperbolic_phase_field_energy_balance(
        _state(), 0.125, HyperbolicPhaseFieldConfig()
    )
    assert balance["flux_dissipation"] >= 0.0
    assert abs(balance["closure_residual"]) <= 1e-12


def test_energy_directional_derivative_matches_rate() -> None:
    state = _state()
    config = HyperbolicPhaseFieldConfig()
    dx = 0.125
    rates = hyperbolic_phase_field_rhs(state, dx, config)
    step = 1e-7

    def displaced(sign: float) -> HyperbolicPhaseFieldState:
        return HyperbolicPhaseFieldState(
            state.C + sign * step * rates.C,
            state.flux_impulse + sign * step * rates.flux_impulse,
            state.auxiliary_rate + sign * step * rates.auxiliary_rate,
            state.gradient_proxy + sign * step * rates.gradient_proxy,
            state.auxiliary_phase + sign * step * rates.auxiliary_phase,
        )

    finite_difference = (
        hyperbolic_phase_field_energy(displaced(1.0), dx, config)
        - hyperbolic_phase_field_energy(displaced(-1.0), dx, config)
    ) / (2.0 * step)
    balance = hyperbolic_phase_field_energy_balance(state, dx, config)
    assert abs(finite_difference - balance["energy_rate"]) <= 2e-8


def test_gradient_constraint_is_preserved() -> None:
    state = _state()
    residual = gradient_constraint_rate_residual(
        state, 0.125, HyperbolicPhaseFieldConfig()
    )
    assert np.max(np.abs(residual)) == 0.0


def test_prepared_gradient_constraint_is_zero() -> None:
    state = _state()
    state.gradient_proxy = periodic_central_derivative(
        state.auxiliary_phase, 0.125
    )
    assert np.max(np.abs(gradient_constraint_residual(state, 0.125))) == 0.0


def test_uniform_pure_phase_is_equilibrium() -> None:
    n = 64
    state = HyperbolicPhaseFieldState(
        np.ones(n), np.zeros(n), np.zeros(n), np.zeros(n), np.ones(n)
    )
    rates = hyperbolic_phase_field_rhs(
        state, 0.1, HyperbolicPhaseFieldConfig()
    )
    for field in (
        rates.C,
        rates.flux_impulse,
        rates.auxiliary_rate,
        rates.gradient_proxy,
        rates.auxiliary_phase,
    ):
        assert np.max(np.abs(field)) == 0.0


def test_principal_eigenvalues_match_analytic_speeds() -> None:
    config = HyperbolicPhaseFieldConfig(
        alpha_penalty=1.4, tau_flux=0.8, gamma_gradient=0.2, beta_wave=0.7
    )
    numeric = np.sort(np.linalg.eigvals(principal_matrix(0.2, config)).real)
    analytic = np.sort(analytic_characteristic_speeds(0.2, config))
    assert np.max(np.abs(numeric - analytic)) <= 1e-14


def test_alpha_above_critical_is_strictly_hyperbolic() -> None:
    density = np.linspace(-1.0, 1.0, 101)
    diagnostics = hyperbolicity_diagnostics(
        density,
        HyperbolicPhaseFieldConfig(
            alpha_penalty=1.2,
            tau_flux=8.0,
            gamma_gradient=0.1,
            beta_wave=1.0,
        ),
    )
    assert diagnostics["strictly_hyperbolic"] is True
    assert diagnostics["status"] == (
        "PASS_FIXED_PARAMETER_HYPERBOLIC_SUBLUMINAL_CONTROL"
    )


def test_alpha_at_critical_is_not_strict_at_spinodal_origin() -> None:
    diagnostics = hyperbolicity_diagnostics(
        np.zeros(64), HyperbolicPhaseFieldConfig(alpha_penalty=1.0)
    )
    assert diagnostics["strictly_hyperbolic"] is False
    assert diagnostics["status"] == "BLOCKED_NOT_STRICTLY_HYPERBOLIC"


def test_hyperbolic_does_not_automatically_mean_subluminal() -> None:
    diagnostics = hyperbolicity_diagnostics(
        np.zeros(64),
        HyperbolicPhaseFieldConfig(alpha_penalty=2.0, tau_flux=1e-3),
    )
    assert diagnostics["strictly_hyperbolic"] is True
    assert diagnostics["within_normalized_light_cone"] is False
    assert diagnostics["status"] == (
        "HYPERBOLIC_BUT_FAILS_NORMALIZED_LIGHT_CONE"
    )


def test_quasistatic_auxiliary_relation_closes() -> None:
    density = _state().C
    config = HyperbolicPhaseFieldConfig(alpha_penalty=20.0)
    comparison = compare_augmented_to_cahn_hilliard_chemical(
        density, 0.125, config
    )
    assert comparison["quasistatic_constraint_max_abs"] <= 1e-13


def test_augmented_chemical_converges_as_penalty_increases() -> None:
    x = np.linspace(0.0, 2.0 * np.pi, 128, endpoint=False)
    density = 0.2 * np.cos(2.0 * x) + 0.04 * np.sin(5.0 * x)
    dx = float(x[1] - x[0])
    errors = []
    for alpha in (8.0, 32.0, 128.0, 512.0):
        result = compare_augmented_to_cahn_hilliard_chemical(
            density,
            dx,
            HyperbolicPhaseFieldConfig(
                alpha_penalty=alpha,
                gamma_gradient=0.05,
                tau_flux=alpha + 1.0,
            ),
        )
        errors.append(result["relative_l2_difference"])
    assert all(later < earlier for earlier, later in zip(errors, errors[1:]))
    assert errors[-1] < 0.02 * errors[0]


def test_quasistatic_phase_approaches_density() -> None:
    density = _state().C
    low = quasistatic_auxiliary_phase(
        density, 0.125, HyperbolicPhaseFieldConfig(alpha_penalty=4.0)
    )
    high = quasistatic_auxiliary_phase(
        density, 0.125, HyperbolicPhaseFieldConfig(alpha_penalty=400.0)
    )
    assert np.linalg.norm(high - density) < np.linalg.norm(low - density)


def test_paper_scaling_has_nonuniform_causal_limit() -> None:
    result = paper_asymptotic_scaling_diagnostics(
        np.array([0.2, 0.1, 0.05, 0.025])
    )
    assert result["speed_increases_as_gamma_decreases"] is True
    assert result["all_subluminal"] is False
    assert result["uniform_subluminal_parabolic_limit"] is False


def test_contract_keeps_auxiliary_phase_separate_from_uet_space() -> None:
    contract = hyperbolic_phase_field_contract()
    assert contract["role"] == (
        "external_first_order_hyperbolic_phase_field_comparator"
    )
    assert "auxiliary_phase_is_not_UET_space_response" in contract[
        "forbidden_identifications"
    ]
    assert contract["uet_covariant_derivation"] == "BLOCKED"


def test_contract_keeps_trace_out_of_dynamics() -> None:
    contract = hyperbolic_phase_field_contract()
    assert contract["trace_input"] is False
    assert contract["trace_backreaction"] is False
    assert "trace" not in inspect.signature(hyperbolic_phase_field_rhs).parameters


def test_next_controller_is_uniform_covariant_mapping() -> None:
    assert hyperbolic_phase_field_contract()["next_controller"] == (
        "uniform_subluminal_hyperbolic_phase_field_and_covariant_mapping_missing"
    )
