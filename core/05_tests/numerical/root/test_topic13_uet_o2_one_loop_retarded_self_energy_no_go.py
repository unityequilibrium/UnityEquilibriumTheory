from __future__ import annotations

from functools import lru_cache

from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_one_loop_retarded_self_energy_no_go import (
    one_loop_retarded_self_energy_no_go_contract,
    one_loop_retarded_self_energy_no_go_state,
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
    return one_loop_retarded_self_energy_no_go_state(0.22, 0.25, 0.15, _config())


def test_one_loop_tadpole_is_real_and_has_no_dissipative_spectral_part() -> None:
    state = _state()
    assert state.one_loop_retarded_self_energy_completed
    assert state.tadpole_finite
    assert state.thermal_tadpole > 0.0
    assert state.imaginary_part_maximum == 0.0
    assert all(value == 0.0 for value in state.self_energy_imaginary)
    assert state.spectral_density_maximum == 0.0
    assert all(value == 0.0 for value in state.self_energy_spectral_density)
    assert state.external_frequency_independence_residual == 0.0


def test_no_go_requires_two_loop_or_microscopic_completion() -> None:
    state = _state()
    contract = one_loop_retarded_self_energy_no_go_contract()
    assert state.two_loop_sunset_or_microscopic_source_required
    assert not state.dissipative_self_energy_completed
    assert contract["excluded"]["physical_retarded_self_energy"]
    assert contract["excluded"]["physical_kubo_coefficient"]


def test_no_go_keeps_external_data_boundaries_closed() -> None:
    state = _state()
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.parameter_fitting_performed
    assert not state.target_data_used
    assert not state.xie_2026_accessed
