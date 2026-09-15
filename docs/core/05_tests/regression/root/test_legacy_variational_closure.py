from docs.core.core_paths import repo_root
import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/uet_legacy_variational_closure.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))


def findings_by_id(artifact):
    return {item["finding_id"]: item for item in artifact["findings"]}


def test_legacy_variational_audit_is_generated_and_conditionally_closed():
    artifact = load_artifact()
    assert artifact["audit_status"] == "PASS"
    assert artifact["closure_status"] == "PASS_CONDITIONAL"
    assert artifact["controlling_blockers"] == []
    assert artifact["canonical_mode"] == "legacy_variational_v1"
    assert artifact["legacy_default_mode"] == "legacy_local"
    assert artifact["legacy_behavior_preserved"] is True
    assert artifact["unresolved_scope_conflicts"] == []


def test_canonical_potential_pair_passes_and_legacy_comparator_is_quarantined():
    finding = findings_by_id(load_artifact())["legacy_potential_derivative_pair"]
    assert finding["status"] == "COMPATIBLE_CONDITIONAL"
    assert finding["metrics"]["canonical_finite_difference_max_absolute_residual"] <= finding["metrics"]["threshold"]
    assert finding["metrics"]["legacy_comparator_finite_difference_max_absolute_residual"] > finding["metrics"]["threshold"]
    assert finding["legacy_comparator"]["status"] == "QUARANTINED_COMPARATOR"
    assert finding["legacy_comparator"]["preserved"] is True


def test_canonical_information_source_sign_passes_and_legacy_comparator_is_quarantined():
    finding = findings_by_id(load_artifact())["legacy_information_gradient_sign"]
    assert finding["status"] == "COMPATIBLE_CONDITIONAL"
    assert finding["expected_source_sign"] == -1
    assert finding["canonical_source_sign"] == -1
    assert finding["legacy_comparator_source_sign"] == 1
    assert finding["c_source_sign_matches"] is True
    assert finding["legacy_comparator"]["status"] == "QUARANTINED_COMPARATOR"

def test_canonical_information_operator_is_conditionally_closed():
    finding = findings_by_id(load_artifact())["legacy_information_operator"]
    assert finding["status"] == "COMPATIBLE_CONDITIONAL"
    assert finding["contract"]["periodic_laplacian"] is True
    assert finding["contract"]["periodic_gradient_energy"] is True
    assert finding["contract"]["historical_box_is_comparator"] is True
