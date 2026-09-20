"""Tests for the Noether-density to phase-field state-coordinate map."""

from __future__ import annotations

import inspect

import numpy as np
import pytest

from docs.core.uet_covariant_diffusion import (
    ConservedCurrentBridgeConfig,
    normalize_local_charge_and_current,
)
from docs.core.uet_covariant_matter import (
    CovariantMatterConfig,
    matter_noether_current,
)
from docs.core.uet_noether_phase_field_map import (
    NOETHER_PHASE_FIELD_MAP_CONTROLLER,
    NOETHER_PHASE_FIELD_MAP_STATUS,
    NoetherPhaseFieldMapConfig,
    denormalize_phase_field_coordinates,
    local_cell_average_1d,
    map_continuity_terms,
    map_external_comparator_state,
    map_normalized_constitutive_scales,
    noether_phase_field_map_contract,
    normalize_noether_hydrodynamic_state,
    symmetric_double_well_equilibrium_contract,
    symmetric_double_well_thermodynamic_map,
)


def _config(**overrides: float | str) -> NoetherPhaseFieldMapConfig:
    values: dict[str, float | str] = {
        "density_reference": 2.5,
        "density_scale": 1.7,
        "length_scale": 0.8,
        "time_scale": 1.3,
        "chemical_potential_scale": 2.2,
    }
    values.update(overrides)
    return NoetherPhaseFieldMapConfig(**values)


def _polar_state(
    amplitude: float,
    phase: float,
    phase_gradient_covariant: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    fields = np.array(
        [amplitude * np.cos(phase), amplitude * np.sin(phase)], dtype=float
    )
    gradients = np.vstack(
        [
            -amplitude * np.sin(phase) * phase_gradient_covariant,
            amplitude * np.cos(phase) * phase_gradient_covariant,
        ]
    )
    return fields, gradients


def test_config_scales_are_exact() -> None:
    config = _config()
    assert config.current_scale == pytest.approx(1.7 * 0.8 / 1.3)
    assert config.free_energy_density_scale == pytest.approx(1.7 * 2.2)
    assert config.mobility_scale == pytest.approx(1.7 * 0.8**2 / (1.3 * 2.2))


@pytest.mark.parametrize(
    "field",
    ["density_scale", "length_scale", "time_scale", "chemical_potential_scale"],
)
def test_config_rejects_nonpositive_scales(field: str) -> None:
    with pytest.raises(ValueError, match="positive"):
        _config(**{field: 0.0})


def test_config_rejects_mass_or_particle_number_shortcuts() -> None:
    with pytest.raises(NotImplementedError, match="signed global-O2"):
        _config(charge_convention="mass_density")
    with pytest.raises(NotImplementedError, match="signed global-O2"):
        _config(charge_convention="particle_number_density")


def test_affine_hydrodynamic_map_roundtrips() -> None:
    rng = np.random.default_rng(9031)
    density = rng.normal(size=128)
    current = rng.normal(size=128)
    result = normalize_noether_hydrodynamic_state(density, current, _config())
    assert result.density_roundtrip_error <= 1e-15
    assert result.current_roundtrip_error <= 1e-15
    recovered = denormalize_phase_field_coordinates(
        result.C, result.normalized_current, _config()
    )
    assert np.max(np.abs(recovered[0] - density)) <= 1e-15
    assert np.max(np.abs(recovered[1] - current)) <= 1e-15


def test_zero_reference_map_reproduces_existing_current_bridge_scaling() -> None:
    density = np.linspace(-2.0, 2.0, 17)
    current = np.linspace(1.5, -0.5, 17)
    old = ConservedCurrentBridgeConfig(
        density_scale=2.4,
        length_scale=0.7,
        time_scale=1.6,
    )
    new = NoetherPhaseFieldMapConfig(
        density_reference=0.0,
        density_scale=old.density_scale,
        length_scale=old.length_scale,
        time_scale=old.time_scale,
    )
    old_C, old_J = normalize_local_charge_and_current(density, current, old)
    mapped = normalize_noether_hydrodynamic_state(density, current, new)
    assert np.max(np.abs(mapped.C - old_C)) == 0.0
    assert np.max(np.abs(mapped.normalized_current - old_J)) == 0.0


def test_continuity_residual_scales_exactly() -> None:
    rng = np.random.default_rng(9032)
    density_rate = rng.normal(size=64)
    current_divergence = rng.normal(size=64)
    mapped = map_continuity_terms(density_rate, current_divergence, _config())
    assert mapped.max_abs_scaling_error <= 5e-16
    assert np.max(
        np.abs(
            mapped.normalized_residual
            - _config().time_scale
            / _config().density_scale
            * mapped.natural_residual
        )
    ) <= 5e-16


def test_closed_continuity_remains_closed_after_mapping() -> None:
    density_rate = np.linspace(-1.0, 1.0, 32)
    mapped = map_continuity_terms(density_rate, -density_rate, _config())
    assert np.max(np.abs(mapped.natural_residual)) == 0.0
    assert np.max(np.abs(mapped.normalized_residual)) == 0.0


def test_external_comparator_C_and_q_map_only_after_flux_declaration() -> None:
    C = np.linspace(-1.2, 1.2, 41)
    q = np.cos(np.linspace(0.0, 2.0 * np.pi, C.size, endpoint=False))
    tau = 0.35
    mapped = map_external_comparator_state(C, q, tau, _config())
    assert np.max(np.abs(mapped.normalized_current - q / tau)) == 0.0
    assert mapped.density_roundtrip_error <= 1e-15
    assert mapped.current_roundtrip_error <= 1e-15
    assert np.max(
        np.abs(
            mapped.coarse_charge_density
            - (_config().density_reference + _config().density_scale * C)
        )
    ) == 0.0


def test_external_state_map_rejects_nonpositive_tau() -> None:
    with pytest.raises(ValueError, match="tau_flux must be positive"):
        map_external_comparator_state(np.ones(4), np.ones(4), 0.0, _config())


def test_double_well_minima_map_to_two_declared_charge_densities() -> None:
    config = _config()
    result = symmetric_double_well_thermodynamic_map(
        np.array([-1.0, 1.0]), config
    )
    expected_density = np.array(
        [
            config.density_reference - config.density_scale,
            config.density_reference + config.density_scale,
        ]
    )
    assert np.max(np.abs(result.coarse_charge_density - expected_density)) == 0.0
    assert np.max(np.abs(result.normalized_chemical_potential)) == 0.0
    assert np.min(result.natural_inverse_susceptibility) > 0.0


def test_physical_free_energy_derivative_matches_mapped_chemical_potential() -> None:
    config = _config()
    C = np.linspace(-1.4, 1.4, 51)
    density = config.density_reference + config.density_scale * C
    step = 1e-6
    plus_C = (density + step - config.density_reference) / config.density_scale
    minus_C = (density - step - config.density_reference) / config.density_scale
    plus = symmetric_double_well_thermodynamic_map(plus_C, config)
    minus = symmetric_double_well_thermodynamic_map(minus_C, config)
    finite_difference = (
        plus.natural_free_energy_density
        - minus.natural_free_energy_density
    ) / (2.0 * step)
    mapped = symmetric_double_well_thermodynamic_map(C, config)
    assert np.max(
        np.abs(finite_difference - mapped.natural_chemical_potential)
    ) <= 2e-9


def test_double_well_local_derivative_is_exact_uet_a_minus_one_b_one() -> None:
    C = np.linspace(-2.0, 2.0, 101)
    mapped = symmetric_double_well_thermodynamic_map(C, _config())
    uet_local_derivative = -C + np.power(C, 3)
    assert np.max(
        np.abs(mapped.normalized_chemical_potential - uet_local_derivative)
    ) == 0.0


def test_equilibrium_susceptibility_contract_is_positive() -> None:
    contract = symmetric_double_well_equilibrium_contract(_config())
    assert contract["density_minus"] < contract["density_plus"]
    assert contract["natural_chemical_potential_at_both_minima"] == 0.0
    assert contract["natural_susceptibility_at_both_minima"] > 0.0


def test_constitutive_scale_map_is_dimensional_coordinate_change_only() -> None:
    config = _config()
    mapped = map_normalized_constitutive_scales(0.4, 0.2, config)
    assert mapped.natural_relaxation_time == pytest.approx(0.4 * config.time_scale)
    assert mapped.natural_current_scale == pytest.approx(config.current_scale)
    assert mapped.natural_mobility == pytest.approx(config.mobility_scale)
    assert mapped.natural_density_gradient_coefficient == pytest.approx(
        config.chemical_potential_scale
        * 0.2
        * config.length_scale**2
        / config.density_scale
    )


def test_polar_O2_identity_matches_matter_noether_current() -> None:
    inverse_metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    phase_gradient = np.array([-0.7, 0.2, -0.1, 0.05])
    amplitude = 1.3
    fields, gradients = _polar_state(amplitude, 0.37, phase_gradient)
    matter = CovariantMatterConfig(matter_kinetic=1.8)
    current = matter_noether_current(inverse_metric, fields, gradients, matter)
    expected = (
        matter.matter_kinetic
        * amplitude**2
        * (inverse_metric @ phase_gradient)
    )
    assert np.max(np.abs(current - expected)) <= 5e-16


def test_microscopic_O2_state_is_not_invertible_from_noether_current() -> None:
    inverse_metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    matter = CovariantMatterConfig()
    gradient_a = np.array([-2.0, 0.4, 0.0, 0.0])
    gradient_b = gradient_a / 2.0
    fields_a, gradients_a = _polar_state(1.0, 0.2, gradient_a)
    fields_b, gradients_b = _polar_state(np.sqrt(2.0), 1.1, gradient_b)
    current_a = matter_noether_current(
        inverse_metric, fields_a, gradients_a, matter
    )
    current_b = matter_noether_current(
        inverse_metric, fields_b, gradients_b, matter
    )
    assert np.max(np.abs(current_a - current_b)) <= 5e-16
    assert np.max(np.abs(fields_a - fields_b)) > 0.5


def test_global_phase_is_an_independent_microscopic_degeneracy() -> None:
    inverse_metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    phase_gradient = np.array([-0.8, 0.25, 0.0, 0.0])
    fields_a, gradients_a = _polar_state(1.2, 0.1, phase_gradient)
    fields_b, gradients_b = _polar_state(1.2, 2.0, phase_gradient)
    matter = CovariantMatterConfig()
    current_a = matter_noether_current(
        inverse_metric, fields_a, gradients_a, matter
    )
    current_b = matter_noether_current(
        inverse_metric, fields_b, gradients_b, matter
    )
    assert np.max(np.abs(current_a - current_b)) <= 5e-16
    assert np.max(np.abs(fields_a - fields_b)) > 1.0


def test_nontrivial_cell_average_is_many_to_one() -> None:
    micro_a = np.array([0.0, 2.0, 1.0, 3.0, -1.0, 1.0, 2.0, 4.0])
    micro_b = np.array([1.0, 1.0, 0.0, 4.0, 0.0, 0.0, 3.0, 3.0])
    assert np.max(np.abs(micro_a - micro_b)) > 0.0
    coarse_a = local_cell_average_1d(micro_a, 4)
    coarse_b = local_cell_average_1d(micro_b, 4)
    assert np.max(np.abs(coarse_a - coarse_b)) == 0.0


def test_cell_average_rejects_ambiguous_shapes() -> None:
    with pytest.raises(ValueError, match="one-dimensional"):
        local_cell_average_1d(np.ones((2, 4)), 2)
    with pytest.raises(ValueError, match="divisible"):
        local_cell_average_1d(np.ones(7), 3)


def test_contract_closes_only_hydrodynamic_coordinate_layer() -> None:
    contract = noether_phase_field_map_contract()
    assert contract["status"] == NOETHER_PHASE_FIELD_MAP_STATUS
    assert contract["microscopic_inverse"] == "IMPOSSIBLE_WITHOUT_ADDITIONAL_STATE"
    assert contract["equation_of_state_origin"] == (
        "CONSTITUTIVE_NOT_DERIVED_FROM_O2_ACTION"
    )
    assert contract["external_auxiliary_phase_to_UET_Phi"] == "FORBIDDEN"
    assert contract["trace_input"] is False
    assert contract["trace_backreaction"] is False
    assert contract["next_controller"] == NOETHER_PHASE_FIELD_MAP_CONTROLLER


def test_public_mapping_functions_have_no_trace_or_space_response_input() -> None:
    for function in (
        normalize_noether_hydrodynamic_state,
        denormalize_phase_field_coordinates,
        map_continuity_terms,
        map_external_comparator_state,
        symmetric_double_well_thermodynamic_map,
    ):
        parameters = inspect.signature(function).parameters
        assert "trace" not in parameters
        assert "space_response" not in parameters
        assert "Phi" not in parameters
