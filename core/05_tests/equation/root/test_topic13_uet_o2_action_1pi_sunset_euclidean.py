from __future__ import annotations

from docs.core.uet_o2_action_1pi_sunset_euclidean import (
    euclidean_1pi_sunset_contract,
    euclidean_1pi_sunset_state,
)


def test_euclidean_sunset_subtraction_conditions_and_nonzero_response():
    state = euclidean_1pi_sunset_state(0.5, 0.8)
    assert state.reference_subtraction_residual <= 1.0e-30
    assert state.reference_derivative_residual <= 1.0e-30
    assert state.nonzero_subtracted_response_witness
    assert state.twice_subtracted_self_energy_values[0] > 0.0


def test_euclidean_sunset_cutoff_and_quadrature_converge():
    state = euclidean_1pi_sunset_state(0.5, 0.8)
    assert state.cutoff_convergence_passed
    assert state.quadrature_convergence_passed
    assert state.cutoff_convergence_residual <= 2.0e-2
    assert state.quadrature_convergence_residual <= 2.0e-2


def test_euclidean_contract_keeps_retarded_boundary_open():
    contract = euclidean_1pi_sunset_contract()
    assert contract["included"]["off_shell_euclidean_loop_integral"]
    assert contract["excluded"]["retarded_analytic_continuation"]
    assert contract["excluded"]["unique_physical_renormalization"]
    assert "not temperature" in contract["unit_contract"]["Phi"]
    assert "separate observer" in contract["unit_contract"]["R_obs"]
