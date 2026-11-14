from __future__ import annotations

import numpy as np

from docs.core.uet_o2_action_1pi_sunset_tensor import (
    action_1pi_sunset_tensor_contract,
    action_1pi_sunset_tensor_state,
    expected_sunset_tensor_prefactor,
    sunset_vertex_contraction,
)


def test_o2_sunset_tensor_contraction_and_symmetry_factor():
    contraction = sunset_vertex_contraction(0.8, species_count=2)
    assert np.allclose(contraction, np.eye(2) * 30.72, atol=1.0e-12)
    assert abs(expected_sunset_tensor_prefactor(0.8, species_count=2) - 5.12) <= 1.0e-12


def test_action_1pi_sunset_state_keeps_scattering_comparator_separate():
    state = action_1pi_sunset_tensor_state(0.8)
    assert state.tensor_contraction_residual <= 1.0e-12
    assert abs(state.sunset_tensor_prefactor - 5.12) <= 1.0e-12
    assert abs(state.action_scattering_matrix_element_squared - 17.92) <= 1.0e-12
    assert abs(state.sunset_to_scattering_prefactor_ratio - 2.0 / 7.0) <= 1.0e-12
    assert not state.loop_integral_evaluated


def test_contract_preserves_ontology_and_open_boundaries():
    contract = action_1pi_sunset_tensor_contract()
    assert contract["excluded"]["full_off_shell_loop_integral"]
    assert contract["excluded"]["unique_physical_renormalization"]
    assert "not temperature" in contract["unit_contract"]["Phi"]
    assert "not mass or charge" in contract["unit_contract"]["C"]
    assert "derived history trace" in contract["unit_contract"]["R_gen"]
