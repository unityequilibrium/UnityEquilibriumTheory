from __future__ import annotations

from functools import lru_cache

from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_nonlocal_sk_kms_memory_kernel import (
    causal_memory_time_kernel,
    nonlocal_sk_kms_memory_contract,
    nonlocal_sk_kms_memory_state,
    retarded_memory_kernel,
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
    return nonlocal_sk_kms_memory_state(0.22, 0.25, 0.15, _config())


def test_nonlocal_memory_is_causal_and_retarded() -> None:
    state = _state()
    assert state.formal_nonlocal_influence_functional_completed
    assert state.negative_time_support_residual == 0.0
    assert state.positive_time_memory_value > 0.0
    assert state.memory_pole_imaginary_part < 0.0
    assert max(state.causal_transform_residuals) <= 1.0e-10
    assert max(state.kernel_reality_residuals) <= 1.0e-12
    assert all(value <= 1.0e-12 for value in state.retarded_imag)
    assert state.spectral_density_minimum >= -1.0e-14


def test_nonlocal_memory_satisfies_kms_fdt_and_entropy_witness() -> None:
    state = _state()
    assert max(state.kms_ratio_residuals) <= 2.0e-12
    assert max(state.fdt_residuals) <= 2.0e-12
    assert state.entropy_production_witness >= 0.0


def test_memory_kernel_boundary_is_not_physical_transport() -> None:
    state = _state()
    contract = nonlocal_sk_kms_memory_contract()
    assert state.source_collision_widths[0] > 0.0
    assert not state.physical_retarded_self_energy_completed
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.target_data_used
    assert not state.xie_2026_accessed
    assert contract["excluded"]["physical_retarded_self_energy"]
    assert contract["excluded"]["physical_kubo_coefficient"]
    assert causal_memory_time_kernel(-1.0, _parameters_from_state(state)) == 0.0


def _parameters_from_state(state):
    from docs.core.uet_o2_nonlocal_sk_kms_memory_kernel import (
        NonlocalSKKMSMemoryParameters,
    )

    return NonlocalSKKMSMemoryParameters(
        beta_th=state.beta_th,
        kappa=state.kappa,
        chi=state.chi,
        gamma_memory=state.gamma_memory,
        memory_time=state.memory_time,
    )
