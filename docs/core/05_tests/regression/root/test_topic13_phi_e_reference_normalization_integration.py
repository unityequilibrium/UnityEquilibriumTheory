"""Integration checks for the named Topic 13 Phi_E reference lane."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path


ROOT = repo_root()
ACTION = "docs/core/07_artifacts/topic13/t13_phi_e_reference_normalization_audit.json"
FULL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def test_phi_e_reference_lane_remains_separate_from_base_phi() -> None:
    full = load(FULL)
    route = full["verification_status"]["phi_e_reference_normalization"]
    assert route["closure_level"] == "CLOSED_FOR_LANE"
    assert route["numeric_base_alpha_Phi_K_emitted"] is False
    assert route["target_data_used"] is False
    assert route["xie_2026_accessed"] is False
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False


def test_phi_e_reference_hashes_are_linked() -> None:
    register = load(REGISTER)
    entry = next(item for item in register["entries"] if item["major_result_id"] == "T13_PHI_E_REFERENCE_NORMALIZATION")
    evidence = entry["evidence_artifacts"][0]
    assert evidence["sha256"] == digest(ACTION)
    dependency = load(DEPENDENCY)
    route = dependency["topic13_partial_evidence"]["phi_e_reference_normalization"]
    assert route["sha256"] == digest(ACTION)
    assert route["summary"]["full_core_unlock"] is False
    assert dependency["register"]["sha256"] == digest(REGISTER)
