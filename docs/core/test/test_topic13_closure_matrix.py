from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MATRIX = ROOT / "docs/core/artifacts/t13_topic13_closure_matrix.json"
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_topic13_closure_matrix_reports_major_requirements_without_promotion() -> None:
    matrix = load(MATRIX)
    gate = load(GATE)
    required = {
        "causal_structure",
        "dimensional_phi_to_thermal_observable_map",
        "independent_alpha_Phi_K",
        "beta_and_si_correspondence",
        "charge_density_eos",
        "covariant_thermal_transport",
        "sk_kms_matching",
        "entropy_current_and_dissipative_balance",
        "source_and_uncertainty",
    }
    assert matrix["major_result"]["major_result_id"] == "T13_TOPIC13_CLOSURE_MATRIX"
    assert {item["requirement_id"] for item in matrix["requirements"]} == required
    assert matrix["status"] == gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert matrix["major_result"]["closure_level"] == "PARTIAL"
    assert matrix["claim_promotion"] is False
    assert matrix["full_core_unlock"] is False
    assert matrix["holdout_policy"]["xie_2026_accessed"] is False
    assert matrix["holdout_policy"]["calibration_path_may_read_holdout"] is False
    assert matrix["major_result"]["open_blockers"] == gate["major_result"]["what_remains_open"]
    assert matrix["closure_summary"]["open_blocker_groups"] == gate["major_result"]["closure_summary"]["open_blocker_groups"]
    alpha = next(item for item in matrix["requirements"] if item["requirement_id"] == "independent_alpha_Phi_K")
    assert alpha["closure_level"] == "OPEN"
    assert alpha["gate_status"] == "BLOCKED"
    assert "alpha_Phi_K" in alpha["what_remains_open"]


def test_topic13_closure_matrix_is_projected_into_register_and_dependency_gate() -> None:
    matrix = load(MATRIX)
    register = load(REGISTER)
    dependency = load(DEPENDENCY)
    entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_TOPIC13_CLOSURE_MATRIX")
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    projection = dependency["topic13_partial_evidence"]["closure_matrix"]
    assert entry["closure_level"] == "PARTIAL"
    assert entry["claim_promotion"] is False
    assert entry["evidence_artifacts"][0]["path"] == "docs/core/artifacts/t13_topic13_closure_matrix.json"
    assert entry["evidence_artifacts"][0]["sha256"] == digest(MATRIX)
    assert full_entry["closure_matrix"]["sha256"] == digest(MATRIX)
    assert projection["path"] == "docs/core/artifacts/t13_topic13_closure_matrix.json"
    assert projection["sha256"] == digest(MATRIX)
    assert projection["full_core_unlock"] is False
