from docs.core.core_paths import canonical_artifact_path, repo_root
import json
from pathlib import Path


ROOT = repo_root()
def _load(name: str):
    return json.loads(canonical_artifact_path(name).read_text(encoding="utf-8"))


def test_axiom_registry_is_complete_and_lane_specific():
    registry = _load("uet_main_theory_axiom_registry.json")
    assert [row["postulate_id"] for row in registry["postulates"]] == [
        f"UET-P{i}" for i in range(9)
    ]
    assert set(registry["collective_coordinate_policy"]["lanes"]) == {
        "phase",
        "charge",
        "density",
        "telegraph",
    }
    assert registry["collective_coordinate_policy"]["universal_identity"].startswith(
        "REJECTED"
    )


def test_each_postulate_has_counterpart_falsification_and_prohibition():
    registry = _load("uet_main_theory_axiom_registry.json")
    for row in registry["postulates"]:
        assert row["standard_physics_counterpart"]
        assert row["falsification_condition"]
        assert row["prohibited_inference"]


def test_ontology_gate_passes_without_promoting_physics():
    gate = _load("uet_main_theory_ontology_gate.json")
    assert gate["audit_status"] == "PASS"
    assert gate["ontology_status"] == "PASS_CONTRACT_ONLY"
    assert all(gate["checks"].values())
    assert gate["controlling_blocker"] == "covariant_parent_contract_not_integrated"
    assert "no physical" in gate["claim_ceiling"]
