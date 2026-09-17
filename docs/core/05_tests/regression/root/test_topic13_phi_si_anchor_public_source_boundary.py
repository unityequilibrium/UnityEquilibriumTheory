from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/07_artifacts/topic13/t13_phi_si_anchor_public_source_boundary_audit.json"
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_public_source_boundary_closes_without_base_phi_calibration() -> None:
    lane = load(LANE)
    major = lane["major_result"]
    source = lane["source_availability"]
    checks = lane["checks"]

    assert lane["status"] == "PASS_PUBLIC_SOURCE_BOUNDARY_NO_PAIRED_BASE_PHI_RECORD"
    assert major["major_result_id"] == "T13_PHI_SI_ANCHOR_PUBLIC_SOURCE_BOUNDARY"
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert source["reported_data_availability"].endswith("reasonable request")
    assert source["public_numeric_paired_record_present"] is False
    assert source["numeric_alpha_Phi_K_present"] is False
    assert checks["author_request_not_claimed_sent"] is True
    assert checks["numeric_alpha_Phi_K_not_emitted"] is True
    assert checks["xie_2026_accessed"] is False
    assert lane["controlling_blocker"] == (
        "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing"
    )


def test_full_gate_exposes_anchor_boundary_without_unlocking_dimensional_map() -> None:
    full = load(FULL)
    dimensional = full["verification_status"]["dimensional_observable_map"]
    lane = dimensional["phi_si_anchor_public_source_boundary"]

    assert lane["major_result_id"] == "T13_PHI_SI_ANCHOR_PUBLIC_SOURCE_BOUNDARY"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert dimensional["physical_mapping_ready"] is False
    assert dimensional["controlling_blocker"] == (
        "dimensional_phi_to_thermal_observable_map_missing"
    )
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert any(
        item["path"] == "docs/core/07_artifacts/topic13/t13_phi_si_anchor_public_source_boundary_audit.json"
        for item in full["evidence_artifacts"]
    )
