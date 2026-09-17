from __future__ import annotations

import numpy as np

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_condensed_loop_renormalized_vertex import (
    condensed_loop_renormalized_vertex_contract,
    condensed_loop_renormalized_vertex_state,
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

def test_condensed_loop_renormalized_vertex_state_closes_declared_lane() -> None:
    state = condensed_loop_renormalized_vertex_state(
        0.20,
        1.28,
        0.15,
        _config(),
        reference_space_response=0.0,
        radial_orders=(20, 28, 36),
        angular_order=20,
        angular_refined_order=28,
    )

    assert state.branch == "condensed"
    assert state.reference_branch == "condensed"
    assert state.loop_integrals_finite is True
    assert state.loop_renormalization_convergence_passes is True
    assert state.state_matched_retarded_response_completed is True
    assert state.physical_kubo_coefficient_emitted is False
    assert state.physical_anchor_supplied is False
    assert state.kms_residual <= 1.0e-12
    assert state.fdt_residual <= 1.0e-12
    assert min(state.collision_eigenvalues) >= -1.0e-12
    assert state.common_flow_conservation_residual <= 1.0e-12
    assert np.all(np.asarray(state.effective_coupling_matrix) > 0.0)


def test_condensed_loop_contract_keeps_physical_kubo_admission_open() -> None:
    contract = condensed_loop_renormalized_vertex_contract()

    assert contract["physical_kubo_admission"]["status"] == "OPEN_PHYSICAL_KUBO"
    assert "coefficient_name" in contract["physical_kubo_admission"]["required_external_or_microscopic_fields"]
    assert "not temperature" in contract["unit_contract"]["Phi"]
    assert "not mass or charge" in contract["unit_contract"]["C"]
