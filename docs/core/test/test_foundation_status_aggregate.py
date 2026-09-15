from docs.core.core_paths import repo_root
import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/uet_foundation_status_aggregate.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))


def test_aggregate_is_generated_and_foundation_remains_blocked():
    artifact = load_artifact()
    assert artifact["audit_status"] == "PASS"
    assert artifact["foundation_status"] == "BLOCKED"
    assert artifact["controlling_blockers"]
    assert "causal_discretization" in artifact["evidence_inputs"]
    assert "legacy_information_gradient_sign" not in artifact["controlling_blockers"]
    assert "legacy_potential_derivative_pair" not in artifact["controlling_blockers"]
    assert "legacy_information_operator" not in artifact["controlling_blockers"]
    assert "legacy_beta_unit_semantics" not in artifact["controlling_blockers"]
    assert "matter_space_causal_response" in artifact["controlling_blockers"]


def test_all_f0_to_f8_gates_are_explicit():
    artifact = load_artifact()
    gates = artifact["gate_summary"]["gates"]
    assert [gate["id"] for gate in gates] == [f"F{i}" for i in range(9)]
    assert all(gate["status"] in {"BLOCKED", "PASS_CONDITIONAL"} for gate in gates)
    assert all(gate["controller"] for gate in gates)


def test_conditional_special_cases_preserve_claim_boundary():
    artifact = load_artifact()
    theories = {item["theory"]: item for item in artifact["conditional_special_cases"]}
    assert set(theories) == {
        "Einstein/GR",
        "relativistic O(2) EOS",
        "Cahn-Hilliard/Markovian comparator",
        "trace/Markovian memory limit",
    }
    for item in theories.values():
        assert item["status"] == "COMPATIBLE_CONDITIONAL"
        assert item["what_is_verified"]
        assert item["what_is_not_verified"]


def test_stopping_criteria_are_machine_reported():
    artifact = load_artifact()
    assert len(artifact["stopping_criteria"]) >= 5
    assert "F1-F7" in artifact["next_controller"]
