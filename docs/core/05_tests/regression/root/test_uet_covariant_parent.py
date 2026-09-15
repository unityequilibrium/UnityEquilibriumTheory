from docs.core.core_paths import repo_root
import json
from pathlib import Path

import numpy as np
import pytest

from docs.core.uet_covariant_matter import (
    CovariantMatterConfig,
    matter_on_shell_box,
)
from docs.core.uet_covariant_parent import (
    CovariantParentConfig,
    CovariantParentState,
    covariant_parent_contract,
    evaluate_conservative_parent,
)
from docs.core.uet_covariant_response import CovariantResponseConfig


ROOT = repo_root()
ARTIFACTS = ROOT / "docs/core/artifacts"


def _sample(epsilon_nc: float):
    response = CovariantResponseConfig(
        epsilon_nc=epsilon_nc,
        response_mass_sq=0.9,
        response_quartic=1.1,
        curvature_coupling=0.2,
    )
    matter = CovariantMatterConfig(
        matter_kinetic=1.2,
        matter_mass_sq=0.8,
        matter_quartic=1.3,
        response_coupling=0.6,
    )
    fields = np.array([0.2, -0.35])
    state = CovariantParentState(
        metric=np.diag([-1.0, 1.0, 1.0, 1.0]),
        inverse_metric=np.diag([-1.0, 1.0, 1.0, 1.0]),
        einstein_tensor=np.zeros((4, 4)),
        curvature_scalar=0.0,
        phi=0.15,
        gradient_phi=np.array([0.1, 0.02, -0.03, 0.0]),
        box_phi=0.04,
        curvature_factor_base_hessian=np.zeros((4, 4)),
        matter_doublet=fields,
        matter_gradients=np.array(
            [[0.01, 0.02, 0.0, -0.01], [-0.02, 0.01, 0.03, 0.0]]
        ),
        matter_box=matter_on_shell_box(fields, 0.15, response, matter),
    )
    return CovariantParentConfig(response, matter), state


def test_parent_exactly_nests_gr_at_null_response():
    config, state = _sample(0.0)
    result = evaluate_conservative_parent(state, config)
    assert result.exact_gr_null_nesting
    assert np.max(np.abs(result.gr_null_difference)) <= 1e-12
    assert result.response_equation_residual == 0.0
    assert result.exchange_ledger.closed


def test_parent_preserves_o2_noether_and_reciprocal_exchange_structure():
    config, state = _sample(0.25)
    result = evaluate_conservative_parent(state, config)
    assert np.max(np.abs(result.matter_equation_residual)) <= 1e-12
    assert abs(result.noether_current_divergence) <= 1e-12
    assert result.exchange_ledger.closed
    assert np.allclose(result.matter_stress_energy, result.matter_stress_energy.T)
    assert np.allclose(result.response_stress_energy, result.response_stress_energy.T)


def test_parent_rejects_unsupported_unit_lane():
    response = CovariantResponseConfig()
    matter = CovariantMatterConfig()
    with pytest.raises(NotImplementedError):
        CovariantParentConfig(response, matter, unit_lane="si")


def test_parent_contract_excludes_trace_dissipation_and_metric_solver():
    contract = covariant_parent_contract()
    assert contract["generated_trace_present"] is False
    assert contract["dissipative_sector_present"] is False
    assert contract["metric_pde_solver_present"] is False


def test_generated_parent_gate_is_scoped_and_registered():
    gate = json.loads(
        (ARTIFACTS / "uet_main_theory_wave2_gate.json").read_text(encoding="utf-8")
    )
    verification = json.loads(
        (ARTIFACTS / "covariant_parent_verification.json").read_text(
            encoding="utf-8"
        )
    )
    registry = json.loads(
        (ARTIFACTS / "uet_equation_correspondence_registry.json").read_text(
            encoding="utf-8"
        )
    )
    assert gate["parent_status"] == "PASS_CONSERVATIVE_PARENT_ONLY"
    assert gate["claim_promotion"] is False
    assert verification["audit_status"] == "PASS"
    assert "uet.main_theory.covariant_parent" in {
        row["equation_id"] for row in registry["entries"]
    }
