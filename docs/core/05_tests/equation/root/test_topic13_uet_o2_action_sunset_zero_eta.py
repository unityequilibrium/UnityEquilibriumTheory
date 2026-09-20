"""Regression tests for the Topic 13 zero-eta sunset interface."""

from __future__ import annotations

import pytest

from docs.core.uet_o2_action_sunset_zero_eta import (
    ZERO_ETA_CONVERGENCE_THRESHOLD,
    zero_eta_sunset_contract,
    zero_eta_sunset_state,
)
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig


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
    return zero_eta_sunset_state(
        0.22,
        0.0,
        0.15,
        _config(),
        radial_order=16,
        center_of_mass_order=16,
        frequency_order=12,
        cutoff_factor=16.0,
        frequency_cutoff_factor=5.0,
    )


def test_zero_eta_distribution_and_subtraction_controls_pass(state):
    assert state.zero_eta_distributional_interface_completed is True
    assert state.declared_bphz_subtraction_interface_completed is True
    assert state.subtraction_at_reference_residual <= 1.0e-24
    assert state.subtraction_derivative_at_reference_residual <= 1.0e-24
    assert state.imaginary_distribution_match_residual <= 1.0e-24
    assert state.kms_max_residual <= 1.0e-12
    assert state.principal_value_convergence_residual <= ZERO_ETA_CONVERGENCE_THRESHOLD


def test_zero_eta_imaginary_response_has_retarded_sign(state):
    assert all(value <= 1.0e-30 for value in state.physical_imaginary_response)
    assert all(value >= -1.0e-30 for value in state.spectral_density)


def test_zero_eta_lane_does_not_promote_physical_claims():
    contract = zero_eta_sunset_contract()
    assert contract["excluded"]["unique_physical_renormalization"] is True
    assert contract["excluded"]["physical_Kubo_coefficient"] is True
    assert contract["excluded"]["Xie_2026_holdout"] is True
