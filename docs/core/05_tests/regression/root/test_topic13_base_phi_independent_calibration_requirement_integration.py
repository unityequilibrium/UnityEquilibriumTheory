"""Integration checks for the Topic 13 open calibration controller."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path


ROOT = repo_root()
ACTION = "docs/core/07_artifacts/topic13/t13_base_phi_independent_calibration_requirement.json"
FULL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
FORMULA = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def test_open_requirement_is_linked_without_unlock() -> None:
    action = load(ACTION)
    assert action["status"] == "PASS_OPEN_CALIBRATION_REQUIREMENT"
    assert action["major_result"]["closure_level"] == "OPEN"
    full = load(FULL)
    route = full["verification_status"]["base_phi_independent_calibration_requirement"]
    assert route["status"] == "OPEN_REQUIREMENT"
    assert route["closure_level"] == "OPEN"
    assert route["numeric_alpha_Phi_K_emitted"] is False
    assert full["claim_promotion"] is False


def test_register_dependency_and_formula_hashes_are_current() -> None:
    action = load(ACTION)
    register = load(REGISTER)
    entry = next(item for item in register["entries"] if item["major_result_id"] == action["major_result"]["major_result_id"])
    assert entry["closure_level"] == "OPEN"
    assert entry["evidence_artifacts"][0]["sha256"] == digest(ACTION)
    dependency = load(DEPENDENCY)
    route = dependency["topic13_partial_evidence"]["base_phi_independent_calibration_requirement"]
    assert route["sha256"] == digest(ACTION)
    assert route["summary"]["full_core_unlock"] is False
    assert dependency["register"]["sha256"] == digest(REGISTER)
    assert "T13-020" in (ROOT / FORMULA).read_text(encoding="utf-8-sig")
