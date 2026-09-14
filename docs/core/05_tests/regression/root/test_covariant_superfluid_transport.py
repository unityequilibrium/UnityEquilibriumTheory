from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_covariant_matter import (
    CovariantMatterConfig,
    matter_noether_current,
)
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_covariant_superfluid_transport import (
    KuboCoefficientRecord,
    SuperfluidHydroState,
    SuperfluidTransportConfig,
    causal_longitudinal_current_rate,
    causal_transport_diagnostics,
    covariant_superfluid_transport_contract,
    entropy_production,
    ideal_superfluid_current,
    ideal_superfluid_stress_tensor,
    josephson_residual,
    linear_mode_spectrum,
    longitudinal_onsager_matrix,
    spatial_projector,
)
from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    o2_equilibrium_state,
)

METRIC = np.diag([-1.0, 1.0, 1.0, 1.0])


def _eos() -> O2FiniteDensityEOSConfig:
    return O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(
            matter_kinetic=1.2,
            matter_mass_sq=0.5,
            matter_quartic=0.8,
            response_coupling=0.3,
        ),
        response=CovariantResponseConfig(epsilon_nc=0.1),
    )


def _state(mu: float = 1.3) -> SuperfluidHydroState:
    return SuperfluidHydroState(
        temperature=0.0,
        chemical_potential=mu,
        four_velocity=np.array([1.0, 0.0, 0.0, 0.0]),
        phase_gradient=np.array([-mu, 0.0, 0.0, 0.0]),
        space_response=0.2,
    )


def _record(name: str, value: float, state: SuperfluidHydroState) -> KuboCoefficientRecord:
    return KuboCoefficientRecord(
        coefficient_name=name,
        value=value,
        units="natural",
        hydrodynamic_frame="Landau",
        temperature=state.temperature,
        chemical_potential=state.chemical_potential,
        space_response=state.space_response,
        correlator_formula_id=f"retarded_{name}_kubo_v1",
        source_path_or_url="internal://synthetic-kubo-control",
        source_hash="0" * 64,
        evidence_status="SYNTHETIC_CONTROL",
    )


def _transport(state: SuperfluidHydroState) -> SuperfluidTransportConfig:
    return SuperfluidTransportConfig(
        eos=_eos(),
        coefficient_records=(
            _record("regular_conductivity", 0.12, state),
            _record("phase_relaxation", 0.20, state),
            _record("charge_phase_cross", 0.03, state),
            _record("relaxation_time", 0.8, state),
        ),
        allow_synthetic_controls=True,
    )


def test_projector_and_josephson_contract() -> None:
    state = _state()
    projector = spatial_projector(METRIC, state.four_velocity)
    u_covariant = METRIC @ state.four_velocity
    assert np.max(np.abs(projector @ u_covariant)) <= 1.0e-12
    mixed = projector @ METRIC
    assert np.max(np.abs(mixed @ mixed - mixed)) <= 1.0e-12
    assert abs(josephson_residual(state, METRIC)) <= 1.0e-12


def test_ideal_current_and_stress_match_o2_action_at_zero_counterflow() -> None:
    state = _state()
    config = SuperfluidTransportConfig(eos=_eos())
    eos_state = o2_equilibrium_state(
        state.chemical_potential, state.space_response, config.eos
    )
    current = ideal_superfluid_current(state, METRIC, config)
    stress = ideal_superfluid_stress_tensor(state, METRIC, config)
    assert current == pytest.approx(
        np.array([eos_state.charge_density, 0.0, 0.0, 0.0]), abs=1.0e-12
    )
    assert stress == pytest.approx(
        np.diag(
            [
                eos_state.energy_density,
                eos_state.pressure,
                eos_state.pressure,
                eos_state.pressure,
            ]
        ),
        abs=1.0e-12,
    )

    amplitude = eos_state.amplitude
    fields = np.array([amplitude, 0.0])
    gradients = np.vstack(
        [np.zeros(4), amplitude * np.asarray(state.phase_gradient)]
    )
    action_current = matter_noether_current(
        METRIC, fields, gradients, config.eos.matter
    )
    assert current == pytest.approx(action_current, abs=1.0e-12)


def test_current_and_stress_transform_covariantly() -> None:
    state = _state()
    config = SuperfluidTransportConfig(eos=_eos())
    current = ideal_superfluid_current(state, METRIC, config)
    stress = ideal_superfluid_stress_tensor(state, METRIC, config)
    velocity = 0.35
    gamma = 1.0 / np.sqrt(1.0 - velocity**2)
    transform = np.array(
        [
            [gamma, -gamma * velocity, 0.0, 0.0],
            [-gamma * velocity, gamma, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    transformed_state = SuperfluidHydroState(
        temperature=0.0,
        chemical_potential=state.chemical_potential,
        four_velocity=transform @ np.asarray(state.four_velocity),
        phase_gradient=np.linalg.inv(transform).T @ np.asarray(state.phase_gradient),
        space_response=state.space_response,
    )
    transformed_current = ideal_superfluid_current(
        transformed_state, METRIC, config
    )
    transformed_stress = ideal_superfluid_stress_tensor(
        transformed_state, METRIC, config
    )
    assert transformed_current == pytest.approx(transform @ current, abs=1.0e-10)
    assert transformed_stress == pytest.approx(
        transform @ stress @ transform.T, abs=1.0e-10
    )


def test_onsager_entropy_and_causal_diagnostics() -> None:
    state = _state()
    config = _transport(state)
    matrix = longitudinal_onsager_matrix(state, config)
    assert np.min(np.linalg.eigvalsh(matrix)) >= -1.0e-12
    rng = np.random.default_rng(7401)
    for _ in range(128):
        assert entropy_production(rng.normal(size=2), state, config) >= -1.0e-12
    diagnostics = causal_transport_diagnostics(state, METRIC, config)
    assert diagnostics["diffusion_coefficient"] == pytest.approx(
        diagnostics["regular_conductivity"] / diagnostics["susceptibility"]
    )
    assert diagnostics["characteristic_speed_sq"] <= 1.0
    assert diagnostics["within_natural_light_cone"] is True
    assert causal_longitudinal_current_rate(0.0, 1.0, state, config) < 0.0


def test_linear_modes_match_eos_sound_speed() -> None:
    state = _state()
    config = _transport(state)
    k = 0.23
    modes = linear_mode_spectrum(k, state, METRIC, config)
    eos_state = o2_equilibrium_state(
        state.chemical_potential, state.space_response, config.eos
    )
    expected = np.sqrt(eos_state.sound_speed_sq) * k
    assert modes["goldstone_angular_frequencies"] == pytest.approx(
        np.array([-expected, expected]), abs=1.0e-12
    )
    assert np.all(np.real(modes["causal_regular_growth_rates"]) <= 1.0e-12)


def test_missing_or_unmatched_coefficients_block_dissipation() -> None:
    state = _state()
    empty = SuperfluidTransportConfig(eos=_eos())
    with pytest.raises(RuntimeError, match="no default"):
        causal_transport_diagnostics(state, METRIC, empty)
    open_record = KuboCoefficientRecord(
        coefficient_name="regular_conductivity",
        value=None,
        units="natural",
        hydrodynamic_frame="Landau",
        temperature=0.0,
        chemical_potential=state.chemical_potential,
        space_response=state.space_response,
        correlator_formula_id="open",
        source_path_or_url="",
        source_hash="",
        evidence_status="OPEN",
    )
    blocked = SuperfluidTransportConfig(
        eos=_eos(), coefficient_records=(open_record,)
    )
    with pytest.raises(RuntimeError, match="lacks matched provenance"):
        causal_transport_diagnostics(state, METRIC, blocked)


def test_non_psd_matrix_and_finite_temperature_are_rejected() -> None:
    state = _state()
    bad = SuperfluidTransportConfig(
        eos=_eos(),
        coefficient_records=(
            _record("regular_conductivity", 0.01, state),
            _record("phase_relaxation", 0.01, state),
            _record("charge_phase_cross", 1.0, state),
        ),
        allow_synthetic_controls=True,
    )
    with pytest.raises(ValueError, match="positive-semidefinite"):
        longitudinal_onsager_matrix(state, bad)
    hot = SuperfluidHydroState(
        temperature=0.2,
        chemical_potential=state.chemical_potential,
        four_velocity=state.four_velocity,
        phase_gradient=state.phase_gradient,
        space_response=state.space_response,
    )
    with pytest.raises(NotImplementedError, match="T=0"):
        ideal_superfluid_current(hot, METRIC, SuperfluidTransportConfig(eos=_eos()))


def test_contract_blocks_full_two_fluid_and_trace_claims() -> None:
    contract = covariant_superfluid_transport_contract()
    assert contract["temperature_scope"] == "T_ZERO_PURE_SUPERFLUID_ONLY"
    assert contract["normal_component"] == "OPEN_NOT_DERIVED"
    assert contract["transport_values"] == "REQUIRED_EXTERNAL_OR_MICROSCOPIC_MATCH_NO_DEFAULTS"
    assert contract["trace_input"] is False
    assert contract["trace_backreaction"] is False
