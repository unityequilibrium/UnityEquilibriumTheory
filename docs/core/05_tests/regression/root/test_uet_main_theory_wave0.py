from docs.core.core_paths import canonical_artifact_path, repo_root
import json
from pathlib import Path


ROOT = repo_root()
def _load(name: str):
    return json.loads(canonical_artifact_path(name).read_text(encoding="utf-8"))


def test_wave0_gate_closes_accounting_without_physics_promotion():
    gate = _load("uet_main_theory_wave0_gate.json")
    assert gate["audit_status"] == "PASS"
    assert gate["research_status"] == "ACCOUNTING_CLOSED_PHYSICS_NOT_PROMOTED"
    assert gate["claim_impact"] == "NO_PHYSICAL_PROMOTION"
    assert gate["controlling_blocker"] == "main_axioms_and_parent_action_not_unified"
    assert all(gate["checks"].values())


def test_dependency_graph_has_all_waves_and_secondary_track_is_isolated():
    graph = _load("uet_main_theory_dependency_graph.json")
    nodes = {node["wave_id"]: node for node in graph["nodes"]}
    assert set(nodes) == {f"W{i}" for i in range(13)}
    assert nodes["W10"]["track"] == "secondary_hypothesis"
    assert all(
        node["track"] == "primary_effective"
        for wave_id, node in nodes.items()
        if wave_id != "W10"
    )
    assert set(nodes["W12"]["depends_on"]) == {f"W{i}" for i in range(12)}


def test_case_insensitive_json_key_drift_is_absent():
    gate = _load("uet_main_theory_wave0_gate.json")
    assert gate["case_insensitive_duplicate_keys"] == []
    assert gate["parse_errors"] == []
    assert gate["missing_inputs"] == []
