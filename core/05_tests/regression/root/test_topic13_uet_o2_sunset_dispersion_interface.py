"""Regression tests for the Topic 13 formal sunset dispersion lane."""

from __future__ import annotations

import pytest

from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_sunset_dispersion_interface import (
    DISPERSION_CONVERGENCE_THRESHOLD,
)
from docs.core.uet_o2_sunset_dispersion_interface_verified import (
    sunset_dispersion_interface_verified_state,
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
        )
    )


@pytest.fixture(scope="module")
def state():
    return sunset_dispersion_interface_verified_state(
        0.22,
        0.0,
        0.15,
        _config(),
        radial_order=48,
        center_of_mass_order=40,
        frequency_order=12,
        cutoff_factor=24.0,
    )


def test_formal_dispersion_contract_passes(state):
    assert state.continuum_dispersion_interface_completed is True
    assert state.real_part_subtraction_interface_completed is True
    assert state.off_shell_matching_interface_completed is True
    assert state.kms_max_residual <= 1.0e-12
    assert state.spectral_positivity_witness is True
    assert state.retarded_imaginary_sign_witness is True
    assert state.reference_subtraction_residual <= 1.0e-24
    assert state.dispersion_convergence_residual <= DISPERSION_CONVERGENCE_THRESHOLD


def test_interface_does_not_promote_physical_claims(state):
    assert state.continuum_sunset_self_energy_completed is False
    assert state.full_1pi_retarded_self_energy_completed is False
    assert state.real_part_subtraction_completed is False
    assert state.off_shell_matching_completed is False
    assert state.unique_physical_renormalization_scheme_match_completed is False
    assert state.physical_retarded_self_energy_completed is False
    assert state.physical_kubo_coefficient_emitted is False
    assert state.numeric_alpha_Phi_K_emitted is False
    assert state.parameter_fitting_performed is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False


def test_lane_keeps_neutral_ontology_and_rejects_charged_shortcut():
    with pytest.raises(ValueError, match="chemical_potential=0"):
        sunset_dispersion_interface_verified_state(0.22, 0.01, 0.15, _config())
