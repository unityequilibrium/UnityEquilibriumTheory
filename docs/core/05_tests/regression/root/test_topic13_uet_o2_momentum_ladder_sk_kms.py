from __future__ import annotations

import pytest

from docs.core.uet_o2_momentum_ladder_sk_kms import (
    momentum_ladder_sk_kms_state,
)


def _state(**overrides):
    parameters = {
        "temperature": 0.22,
        "chemical_potential": 0.35,
        "space_response": 0.15,
        "quadrature_order": 24,
        "collision_integration_order": 24,
        "angular_order": 24,
        "cutoff_factor": 28.0,
    }
    parameters.update(overrides)
    return momentum_ladder_sk_kms_state(**parameters)


def test_momentum_ladder_is_charge_conserving_and_positive() -> None:
    state = _state()
    assert len(state.collision_widths) == 2 * len(state.momentum_nodes)
    assert state.collision_width_relative_spread > 0.1
    assert abs(state.collision_operator_eigenvalues[0]) <= 1.0e-12
    assert state.charge_conservation_residual <= 1.0e-12
    assert state.operator_symmetry_residual <= 1.0e-12
    assert state.positive_semidefinite_min_eigenvalue >= -1.0e-12
    assert state.entropy_production_witness > 0.0


def test_momentum_ladder_kms_and_fdt_interface_matches_targets() -> None:
    state = _state()
    assert all(value > 0.0 for value in state.kms_spectral_density)
    assert state.kms_ratio == pytest.approx(state.kms_target_ratio, rel=1.0e-12)
    assert state.kms_noise == pytest.approx(state.kms_noise_target, rel=1.0e-12)
    assert all(
        later <= earlier + 1.0e-10
        for earlier, later in zip(
            state.retarded_response_real,
            state.retarded_response_real[1:],
        )
    )
    assert all(value > 0.0 for value in state.retarded_response_imag[1:])


def test_momentum_ladder_refines_at_fixed_cutoff_without_physical_promotion() -> None:
    reference = _state()
    refined = _state(quadrature_order=32)
    assert refined.momentum_cutoff == reference.momentum_cutoff
    assert refined.retarded_response_real == pytest.approx(
        reference.retarded_response_real,
        rel=0.02,
    )
    assert reference.microscopic_bethe_salpeter_match_completed is False
    assert reference.microscopic_sk_kms_match_completed is False
    assert reference.physical_kubo_coefficient_emitted is False
    with pytest.raises(ValueError, match="corrected quantum collision width"):
        _state(include_final_state_bose_enhancement=False)
