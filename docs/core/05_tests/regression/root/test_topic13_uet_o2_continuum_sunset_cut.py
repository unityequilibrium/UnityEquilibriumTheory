"""Regression tests for the Topic 13 continuum sunset-cut lane."""

from __future__ import annotations

from docs.core.uet_o2_continuum_sunset_cut import continuum_sunset_cut_state
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
def _config():
    return FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(
            matter=CovariantMatterConfig(
                matter_mass_sq=0.5,
                matter_quartic=0.8,
                response_coupling=0.3,
            ),
            response=CovariantResponseConfig(epsilon_nc=0.1),
        )
    )





def _state():
    return continuum_sunset_cut_state(
        0.22,
        0.0,
        0.15,
        _config(),
        radial_order=48,
        center_of_mass_order=40,
        cutoff_factor=24.0,
    )


def test_continuum_cut_is_positive_and_kms_balanced():
    state = _state()

    assert state.continuum_sunset_cut_completed is True
    assert state.greater_cut > 0.0
    assert state.lesser_cut > 0.0
    assert state.positive_spectral_cut is True
    assert state.noise_cut > 0.0
    assert state.kms_residual <= 1.0e-12


def test_continuum_cut_has_separate_numerical_convergence_controls():
    state = _state()

    assert state.radial_convergence_residual <= state.convergence_threshold
    assert state.angular_convergence_residual <= state.convergence_threshold
    assert state.cutoff_convergence_residual <= state.convergence_threshold
    assert state.convergence_passed is True


def test_continuum_cut_does_not_promote_full_self_energy_or_external_claims():
    state = _state()

    assert state.continuum_sunset_self_energy_completed is False
    assert state.full_1pi_retarded_self_energy_completed is False
    assert state.real_part_subtraction_completed is False
    assert state.off_shell_matching_completed is False
    assert state.physical_retarded_self_energy_completed is False
    assert state.physical_kubo_coefficient_emitted is False
    assert state.numeric_alpha_Phi_K_emitted is False
    assert state.parameter_fitting_performed is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False
