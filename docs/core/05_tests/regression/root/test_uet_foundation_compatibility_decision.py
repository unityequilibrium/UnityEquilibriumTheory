from docs.core.core_paths import repo_root
import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/uet_foundation_compatibility_decision.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))


def test_decision_does_not_promote_global_mathematical_consistency():
    artifact = load_artifact()
    assert artifact["audit_status"] == "PASS"
    assert artifact["decision"]["mathematical_consistency"] == "CONDITIONAL_SCOPED_CANONICAL"
    assert artifact["hard_contradictions"] == []
    blocker_ids = {item["id"] for item in artifact["remaining_dependency_blockers"]}
    assert "matter_space_causal_response" in blocker_ids
    closure_ids = {item["id"] for item in artifact["conditional_closures"]}
    assert "legacy_potential_derivative_pair" in closure_ids
    assert "legacy_information_gradient_sign" in closure_ids
    assert "legacy_information_operator" in closure_ids
    assert "legacy_beta_unit_semantics" in closure_ids


def test_special_case_statuses_are_conditional_and_lane_specific():
    artifact = load_artifact()
    special = artifact["special_case_summary"]
    assert artifact["decision"]["old_theory_nesting"] == "CONDITIONAL_ONLY"
    assert special["gr"] == "COMPATIBLE_CONDITIONAL_LOCAL_ALGEBRAIC_ONLY"
    assert special["o2_finite_density"] == (
        "COMPATIBLE_CONDITIONAL_TREE_LEVEL_NATURAL_UNITS"
    )
    assert special["legacy_double_well"] == "REJECTED_REDUCTION"


def test_causal_reference_does_not_promote_full_candidate():
    artifact = load_artifact()
    rows = {row["principle_id"]: row for row in artifact["principle_matrix"]}
    assert rows["P7_causal_response"]["verdict"] == (
        "FULL_CANDIDATE_BLOCKED_REFERENCE_LANE_PASS"
    )
    assert artifact["decision"]["global_uet_status"] == "FOUNDATION_NOT_CLOSED"


def test_coverage_boundary_remains_visible():
    artifact = load_artifact()
    coverage = artifact["coverage"]
    assert coverage["topic_formula_rows"] == 260
    assert coverage["topic_formula_files"] == 27
    assert coverage["inventory_gate_status"] == "BLOCKED"
    assert coverage["registry_coverage_status"] == "INITIAL_SEED_NOT_EXHAUSTIVE"

def test_family_matrix_covers_all_declared_core_families():
    artifact = load_artifact()
    declared = {
        "core.legacy_master",
        "core.matter_space",
        "core.trace",
        "core.covariant_response",
        "core.covariant_diffusion",
        "core.hyperbolic_phase",
        "core.o2_superfluid",
        "core.noether_mapping",
        "core.lorentz",
        "core.parameter_contract",
        "core.observable_contract",
        "core.support_and_adapters",
    }
    matrix_ids = {row["family_id"] for row in artifact["family_matrix"]}
    assert declared <= matrix_ids
