from __future__ import annotations

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_condensed_relative_flow_kubo_admission import (
    KUBO_EVIDENCE_STATUS,
    KUBO_FORMULA_ID,
    condensed_relative_flow_kubo_admission_state,
)
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


def _config() -> FiniteTemperatureO2QuasiparticleConfig:
    return FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(
            matter=CovariantMatterConfig(
                matter_mass_sq=0.5,
                matter_quartic=0.8,
                response_coupling=0.3,
            ),
            response=CovariantResponseConfig(
                epsilon_nc=0.1,
                phi_equilibrium=0.0,
            ),
        ),
        quadrature_order=192,
        cutoff_factor=70.0,
    )


def test_state_matched_kubo_record_is_admitted_for_declared_lane() -> None:
    state = condensed_relative_flow_kubo_admission_state(
        0.20,
        1.28,
        0.15,
        source_path_or_url="docs/core/uet_o2_condensed_loop_renormalized_vertex.py",
        source_hash="a" * 64,
        reference_space_response=0.0,
        config=_config(),
        loop_state=None,
    )

    assert state.evidence_status == KUBO_EVIDENCE_STATUS
    assert state.correlator_formula_id == KUBO_FORMULA_ID
    assert state.state_match is True
    assert state.value > 0.0
    assert 0.0 <= state.uncertainty <= 1.0e-2
    assert state.independent_of_target_data is True
    assert state.holdout_accessed is False
    assert state.parameter_fitting_performed is False
    assert state.physical_kubo_admission_completed is True
    assert state.full_core_unlock is False


def test_record_contains_required_kubo_fields() -> None:
    state = condensed_relative_flow_kubo_admission_state(
        0.20,
        1.28,
        0.15,
        source_path_or_url="docs/core/uet_o2_condensed_loop_renormalized_vertex.py",
        source_hash="b" * 64,
        reference_space_response=0.0,
        config=_config(),
    )
    record = state.record()

    for key in (
        "coefficient_name",
        "value",
        "units",
        "hydrodynamic_frame",
        "temperature",
        "chemical_potential",
        "space_response",
        "correlator_formula_id",
        "source_path_or_url",
        "source_hash",
        "evidence_status",
        "uncertainty",
    ):
        assert key in record
