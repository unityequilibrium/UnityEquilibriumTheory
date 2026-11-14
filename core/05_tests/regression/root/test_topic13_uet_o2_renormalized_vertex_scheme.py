"""Regression tests for the declared renormalized O(2) vertex scheme."""

from __future__ import annotations

from functools import lru_cache

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_renormalized_vertex_scheme import (
    renormalized_vertex_scheme_contract,
    renormalized_vertex_scheme_state,
)


def _config() -> FiniteTemperatureO2QuasiparticleConfig:
    return FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(
            matter=CovariantMatterConfig(
                matter_mass_sq=0.5,
                matter_quartic=0.8,
                response_coupling=0.3,
            ),
            response=CovariantResponseConfig(epsilon_nc=0.1),
        ),
        quadrature_order=192,
        cutoff_factor=70.0,
    )


@lru_cache(maxsize=1)
def _state():
    return renormalized_vertex_scheme_state(
        0.22,
        0.0,
        0.15,
        _config(),
        reference_space_response=0.0,
    )


def test_reference_subtraction_reduces_the_one_loop_uv_boundary():
    state = _state()

    assert state.raw_vacuum_growth_ratio > 1.5
    assert state.renormalized_bubble_last_relative_change <= 1.0e-3
    assert state.renormalized_vertex_last_relative_change <= 1.0e-3
    assert state.reference_subtraction_residual == 0.0


def test_finite_thermal_piece_and_equilibrium_kms_are_retained():
    state = _state()

    assert state.thermal_cutoff_relative_change <= 1.0e-8
    assert all(value > 0.0 for value in state.thermal_values)
    assert state.kms_ratio_residual <= 1.0e-12
    assert state.kms_noise_fdt_residual <= 1.0e-12


def test_declared_scheme_does_not_promote_physical_or_external_claims():
    state = _state()
    contract = renormalized_vertex_scheme_contract()

    assert state.renormalized_vertex_scheme_completed is True
    assert state.physical_renormalization_scheme_matched is False
    assert state.finite_density_vertex_completed is False
    assert state.full_interacting_sk_kms_match_completed is False
    assert state.physical_kubo_coefficient_emitted is False
    assert state.numeric_alpha_Phi_K_emitted is False
    assert state.parameter_fitting_performed is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False
    assert contract["excluded"]["unique_physical_renormalization"] is True
    assert contract["excluded"]["finite_chemical_potential_vertex"] is True
    assert contract["excluded"]["alpha_Phi_K"] is True
