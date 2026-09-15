"""Integration checks for the Topic 13 causal branch-selection record."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path


ROOT = repo_root()
ACTION_REL = "docs/core/artifacts/t13_causal_branch_selection_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def test_causal_selection_is_visible_without_promoting_full_topic13() -> None:
    full = load(FULL_REL)
    causal = full["verification_status"]["causal_branch_selection"]
    assert causal["status"] == "PASS_CLOSED_AS_NO_GO_WITH_NAMED_COUPLED_BRANCH"
    assert causal["closure_level"] == "CLOSED_FOR_LANE"
    assert causal["baseline_full_candidate_pass"] is False
    assert causal["baseline_replaced"] is False
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False


def test_causal_selection_register_and_dependency_hashes_match() -> None:
    register = load(REGISTER_REL)
    result_id = "T13_CAUSAL_THERMAL_BRANCH_SELECTION"
    entry = next(item for item in register["entries"] if item.get("major_result_id") == result_id)
    assert entry["closure_level"] == "CLOSED_FOR_LANE"
    evidence = next(item for item in entry["evidence_artifacts"] if item["path"] == ACTION_REL)
    assert evidence["sha256"] == sha256(ACTION_REL)

    flux_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_CAUSAL_FLUX_TELEGRAPH_BRANCH")
    assert "full coupled Phi integration" not in flux_entry["open_blockers"]
    assert "full-candidate leakage rerun" not in flux_entry["open_blockers"]

    dependency = load(DEPENDENCY_REL)
    route = dependency["topic13_partial_evidence"]["causal_branch_selection"]
    assert route["summary"]["full_core_unlock"] is False
    assert route["summary"]["baseline_replaced"] is False
    assert route["sha256"] == sha256(ACTION_REL)
    assert dependency["register"]["sha256"] == sha256(REGISTER_REL)
