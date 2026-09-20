from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_density_charged_vertex import (
    charged_euclidean_inverse,
    finite_density_charged_vertex_contract,
    finite_density_charged_vertex_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_renormalized_vertex_scheme import (
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
        )
    )


def test_finite_density_charged_lane_closes_declared_scheme() -> None:
    state = finite_density_charged_vertex_state(0.22, 0.25, 0.15, _config())
    assert state.finite_density_charged_vertex_completed
    assert state.static_gap > 0.0
    assert state.particle_mode_energy > 0.0
    assert state.antiparticle_mode_energy > state.particle_mode_energy
    assert state.raw_vacuum_growth_ratio > 1.5
    assert state.charged_thermal_cutoff_relative_change <= 1.0e-8
    assert state.renormalized_vertex_last_relative_change <= 1.0e-6
    assert state.particle_kms_residual <= 1.0e-12
    assert state.antiparticle_kms_residual <= 1.0e-12
    assert state.charge_conjugation_bubble_residual <= 1.0e-12
    assert state.charge_density_odd_residual <= 1.0e-12
    assert not state.unique_physical_renormalization_scheme_matched
    assert not state.full_interacting_sk_kms_match_completed
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.target_data_used
    assert not state.xie_2026_accessed


def test_zero_density_matches_the_previous_renormalized_vertex_lane() -> None:
    config = _config()
    charged = finite_density_charged_vertex_state(0.22, 0.0, 0.15, config)
    neutral = renormalized_vertex_scheme_state(0.22, 0.0, 0.15, config)
    assert np.max(
        np.abs(
            np.asarray(charged.renormalized_bubble_values)
            - np.asarray(neutral.renormalized_bubble_values)
        )
    ) <= 1.0e-12
    assert np.max(
        np.abs(
            np.asarray(charged.renormalized_vertex_norms)
            - np.asarray(neutral.renormalized_vertex_norms)
        )
    ) <= 1.0e-12
    assert abs(charged.thermal_charge_density) <= 1.0e-14


def test_charged_propagator_rejects_condensed_domain_and_preserves_factorization() -> None:
    with pytest.raises(ValueError, match="stable normal branch"):
        finite_density_charged_vertex_state(0.22, 0.8, 0.15, _config())
    inverse = charged_euclidean_inverse(0.31, 0.27, 0.18, 0.71)
    energy = float(np.sqrt(0.27**2 + 0.71**2))
    factorized = ((0.31 + 1j * 0.18) - 1j * energy) * (
        (0.31 + 1j * 0.18) + 1j * energy
    )
    assert abs(inverse - factorized) <= 1.0e-14
    contract = finite_density_charged_vertex_contract()
    assert contract["excluded"]["alpha_Phi_K"]
    assert contract["excluded"]["TTG_validation"]
