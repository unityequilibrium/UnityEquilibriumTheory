from __future__ import annotations

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_condensed_sk_kms_kubo_match import (
    condensed_sk_kms_kubo_match_contract,
    condensed_sk_kms_kubo_match_state,
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


def test_condensed_sk_kms_kubo_match_closes_declared_channel() -> None:
    state = condensed_sk_kms_kubo_match_state(
        0.20,
        1.28,
        0.15,
        _config(),
        reference_space_response=0.0,
    )

    assert state.branch == "condensed"
    assert state.declared_channel_sk_kms_match_completed is True
    assert state.physical_retarded_self_energy_completed is False
    assert state.kms_residual <= 1.0e-12
    assert state.fdt_residual <= 1.0e-12
    assert state.retarded_reality_residual <= 1.0e-12
    assert state.spectral_psd_minimum >= -1.0e-12
    assert state.zero_frequency_kubo_match_residual <= 1.0e-12
    assert state.entropy_production_at_unit_force >= 0.0


def test_condensed_sk_kms_contract_keeps_full_self_energy_open() -> None:
    contract = condensed_sk_kms_kubo_match_contract()

    assert "full finite-temperature retarded 1PI self-energy" in " ".join(contract["excluded_scope"])
    assert "not temperature" in contract["unit_contract"]["Phi"]
    assert "not mass or charge" in contract["unit_contract"]["C"]
