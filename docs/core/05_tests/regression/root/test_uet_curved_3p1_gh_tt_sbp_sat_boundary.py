from __future__ import annotations

import importlib
import json
from pathlib import Path

import numpy as np


AUDIT = importlib.import_module(
    "docs.scripts.audit.audit_curved_3p1_gh_tt_sbp_sat_boundary"
)
ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_tt_sbp_sat_boundary_pilot.json"
)


def test_lobatto_sbp_operator_is_polynomial_exact_and_summation_by_parts() -> None:
    for order in (4, 8, 12, 24):
        operators = AUDIT.legendre_lobatto_operators(order)
        boundary = np.zeros((order + 1, order + 1))
        boundary[0, 0] = -1.0
        boundary[-1, -1] = 1.0
        weighted = operators.norm_weights[:, None] * operators.derivative
        assert np.max(np.abs(weighted + weighted.T - boundary)) < 2.0e-12
        for power in range(order + 1):
            exact = (
                np.zeros_like(operators.nodes)
                if power == 0
                else power * operators.nodes ** (power - 1)
            )
            assert np.max(
                np.abs(operators.derivative @ operators.nodes**power - exact)
            ) < 2.0e-10


def test_sat_energy_rate_is_exactly_nonpositive_for_arbitrary_boundary_state() -> None:
    operators = AUDIT.legendre_lobatto_operators(12)
    rng = np.random.default_rng(1417)
    state = AUDIT.TTWaveState(
        displacement=rng.normal(size=(2, 13)),
        momentum=rng.normal(size=(2, 13)),
        spatial_gradient=rng.normal(size=(2, 13)),
    )
    measured, residual = AUDIT._semi_discrete_energy_identity_residual(
        state, operators
    )
    assert measured <= 0.0
    assert residual < 2.0e-11


def test_reduction_constraint_is_invariant_under_rk4_evolution() -> None:
    operators = AUDIT.legendre_lobatto_operators(12)
    state = AUDIT.gaussian_right_going_state(operators)
    initial = AUDIT.reduction_constraint_linf(state, operators)
    for _ in range(40):
        state = AUDIT.rk4_step(state, operators, 1.0e-4)
    final = AUDIT.reduction_constraint_linf(state, operators)
    assert initial < 2.0e-10
    assert final < 2.0e-9


def test_frozen_background_packet_is_absorbed_and_temporal_order_converges() -> None:
    artifact = AUDIT.build_artifact()
    assert artifact["status"] == "PASS_GH_LINEAR_TT_SBP_SAT_BOUNDARY_PILOT"
    assert all(artifact["checks"].values())
    assert artifact["metrics"]["pulse_final_to_initial_energy_ratio"] <= 2.0e-6
    assert artifact["metrics"]["left_pulse_final_to_initial_energy_ratio"] <= 2.0e-6
    assert artifact["metrics"]["maximum_rk4_amplification_at_selected_dt"] <= 1.0 + 1.0e-10
    assert 10.0 <= artifact["metrics"]["temporal_refinement_difference_ratio"] <= 22.0


def test_persisted_artifact_preserves_lane_and_claim_boundary() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["major_result"]["dependency_unlocked"].startswith("none;")
    assert artifact["scope"]["full_rinne_cpbc_implemented"] is False
    assert artifact["scope"]["periodic_gh_solver_modified"] is False
    assert artifact["claim_promotion"] is False
    assert "full_first_order_gh_differential_cpbc" in artifact["controlling_blocker"]
