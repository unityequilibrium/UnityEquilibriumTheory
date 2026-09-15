from __future__ import annotations
from docs.core.core_paths import repo_root

import json
import math
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/artifacts/t13_mp48_phi_e_dimensional_comparator_audit.json"
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_phi_e_dimensional_comparator_closes_without_base_phi_promotion() -> None:
    lane = load(LANE)
    major = lane["major_result"]
    assert lane["status"] == "PASS_SCOPED_PHI_E_DIMENSIONAL_COMPARATOR"
    assert major["major_result_id"] == "T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR"
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert major["data_role"] == "EXTERNAL_INPUT_STANDARD_HARMONIC_COMPARATOR_NOT_BASE_PHI_CALIBRATION"
    assert all(lane["checks"].values())
    assert lane["source"]["reference_temperature_K"] == 300.0
    assert math.isclose(lane["reference_alpha_Phi_E_K"], 126.72529975005031, rel_tol=1.0e-12)
    assert lane["numeric_alpha_Phi_K_emitted"] is False
    assert lane["alpha_Phi_K_fit_performed"] is False
    assert lane["holdout_accessed"] is False
    assert "base-Phi calibration" in major["claim_boundary"]
    assert "base_Phi_to_Phi_E_mapping_missing" in major["open_blockers"]


def test_full_gate_keeps_phi_e_comparator_below_base_phi_alpha_closure() -> None:
    lane = load(LANE)
    full = load(FULL)
    dimensional = full["verification_status"]["dimensional_observable_map"]
    comparator = dimensional["mp48_phi_e_dimensional_anchor_comparator"]
    assert comparator["major_result_id"] == "T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR"
    assert comparator["closure_level"] == "CLOSED_FOR_LANE"
    assert dimensional["status"] == "BLOCKED"
    assert dimensional["physical_mapping_ready"] is False
    assert full["verification_status"]["alpha_Phi_K"]["status"] == "BLOCKED"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert any(
        item["path"] == "docs/core/artifacts/t13_mp48_phi_e_dimensional_comparator_audit.json"
        for item in full["evidence_artifacts"]
    )
