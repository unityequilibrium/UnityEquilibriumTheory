from docs.core.core_paths import repo_root
import json
import sys
from collections import Counter
from pathlib import Path

from docs.scripts.audit import build_uet_foundation_status_aggregate as builder


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/gates/uet_foundation_status_aggregate.json"


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
    assert {gate["id"] for gate in gates if gate["status"] == "PASS_CONDITIONAL"} == {"F0", "F1", "F5"}
    assert artifact["gate_summary"]["status_counts"] == Counter(gate["status"] for gate in gates)
    assert artifact["gate_summary"]["status_counts"] == {"PASS_CONDITIONAL": 3, "BLOCKED": 6}
    assert gates[6]["status"] == "BLOCKED"
    assert "reference lane=PASS" in gates[6]["controller"]


def test_aggregate_check_rejects_drift_without_writing(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["aggregate", "--check"])
    json_before = builder.OUT.read_bytes()
    markdown_before = builder.SUMMARY_DOC.read_bytes()
    assert builder.main() == 0
    assert builder.OUT.read_bytes() == json_before
    assert builder.SUMMARY_DOC.read_bytes() == markdown_before

    stale = tmp_path / "stale.md"
    bad = markdown_before.replace(b"`6 BLOCKED`", b"`7 BLOCKED`")
    assert bad != markdown_before
    stale.write_bytes(bad)
    monkeypatch.setattr(builder, "SUMMARY_DOC", stale)
    assert builder.main() == 1
    assert stale.read_bytes() == bad
    assert builder.OUT.read_bytes() == json_before


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
