import numpy as np

from docs.core.uet_o2_formal_two_sector_thermodynamics import (
    formal_two_sector_contract,
    formal_two_sector_state,
)


def test_formal_two_sector_identities_close_without_transport_claim() -> None:
    normal = formal_two_sector_state(0.22, 0.35, 0.15)
    condensed = formal_two_sector_state(0.12, 1.18, 0.15)
    for state in (normal, condensed):
        assert np.isclose(
            state.total_pressure,
            state.condensate_pressure + state.normal_pressure,
            rtol=1.0e-10,
            atol=1.0e-12,
        )
        assert np.isclose(
            state.total_charge_density,
            state.condensate_charge_density + state.normal_charge_density,
            rtol=2.0e-5,
            atol=2.0e-8,
        )
        assert np.isclose(
            state.total_entropy_density,
            state.condensate_entropy_density + state.normal_entropy_density,
            rtol=2.0e-5,
            atol=2.0e-8,
        )
        assert np.isclose(
            state.total_energy_density,
            state.condensate_energy_density + state.normal_energy_density,
            rtol=2.0e-5,
            atol=2.0e-8,
        )
        assert all(
            np.isfinite(value)
            for value in (
                state.condensate_susceptibility,
                state.normal_susceptibility,
            )
        )
    assert normal.condensate_pressure == 0.0
    assert condensed.condensate_pressure > 0.0
    assert abs(condensed.condensate_entropy_density) <= 1.0e-12


def test_formal_two_sector_boundary_does_not_promote_transport_or_alpha() -> None:
    contract = formal_two_sector_contract()
    assert "Kubo" in contract["excluded_scope"]
    assert "alpha_Phi_K" in contract["excluded_scope"]
    assert "not Landau mass density" in contract["unit_contract"]["normal_density_label"]
