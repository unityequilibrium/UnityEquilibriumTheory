from __future__ import annotations

from functools import lru_cache

from docs.core.uet_o2_interacting_sk_kms_action import (
    interacting_sk_kms_action_contract,
    interacting_sk_kms_action_state,
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


@lru_cache(maxsize=1)
def _state():
    return interacting_sk_kms_action_state(0.22, 0.25, 0.15, _config())


def test_local_interacting_contour_is_exact_and_unitary() -> None:
    state = _state()
    assert state.local_interacting_sk_action_completed
    assert state.contour_ra_expansion_residual <= 1.0e-12
    assert state.contour_unitarity_residual <= 1.0e-14
    assert state.contour_reality_residual <= 1.0e-12
    assert state.no_pure_r_interaction_residual <= 1.0e-14
    assert abs(state.ra_interaction_r3a_weight) > 1.0e-8
    assert abs(state.ra_interaction_ra3_weight) > 1.0e-8


def test_charged_kms_and_detailed_balance_interfaces_hold() -> None:
    state = _state()
    assert state.formal_charged_kms_match_completed
    assert state.charged_particle_kms_residual <= 1.0e-12
    assert state.charged_antiparticle_kms_residual <= 1.0e-12
    assert state.charged_collision_detailed_balance_residual <= 1.0e-10
    assert state.charged_collision_kms_residual <= 1.0e-12
    assert state.charged_collision_fdt_residual <= 1.0e-12
    assert state.formal_entropy_witness >= 0.0


def test_nonlocal_and_external_boundaries_remain_open() -> None:
    state = _state()
    contract = interacting_sk_kms_action_contract()
    assert not state.nonlocal_influence_functional_completed
    assert not state.microscopic_retarded_self_energy_completed
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.target_data_used
    assert not state.xie_2026_accessed
    assert contract["excluded"]["nonlocal_influence_functional"]
    assert contract["excluded"]["physical_kubo_coefficient"]
    assert contract["excluded"]["alpha_Phi_K"]
    assert contract["excluded"]["TTG_validation"]
