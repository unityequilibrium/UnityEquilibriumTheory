from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/artifacts/t13_mp48_spectral_csrc_reproduction_audit.json"
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_mp48_spectral_csrc_lane_is_closed_without_ding_or_uet_promotion() -> None:
    lane = load(LANE)
    major = lane["major_result"]
    assert lane["status"] == "PASS_SCOPED_HARMONIC_DOS_CROSS_FILE_REPRODUCTION"
    assert major["major_result_id"] == "T13_MP48_SPECTRAL_C_SRC_REPRODUCTION"
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert major["data_role"] == "INTERNAL_CROSS_FILE_REPRODUCTION_NOT_DING_SOURCE"
    assert lane["source"]["frequency_grid"]["row_count"] == 201
    assert [row["temperature_K"] for row in lane["source"]["temperature_rows"]] == [
        200.0,
        250.0,
        300.0,
    ]
    assert all(lane["checks"].values())
    assert lane["holdout_accessed"] is False
    assert lane["target_fit_performed"] is False
    assert lane["numeric_alpha_Phi_K_emitted"] is False
    assert "not Ding's PBTE C_src" in major["claim_boundary"]


def test_full_gate_keeps_spectral_lane_separate_from_source_and_alpha_closure() -> None:
    lane = load(LANE)
    full = load(FULL)
    source = full["verification_status"]["source_package"]
    spectral = source["mp48_spectral_csrc_reproduction"]
    assert spectral["major_result_id"] == "T13_MP48_SPECTRAL_C_SRC_REPRODUCTION"
    assert spectral["closure_level"] == "CLOSED_FOR_LANE"
    assert source["status"] == "BLOCKED"
    assert source["controlling_blocker"] == (
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing"
    )
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert full["verification_status"]["alpha_Phi_K"]["status"] == "BLOCKED"
    assert any(
        item["path"] == "docs/core/artifacts/t13_mp48_spectral_csrc_reproduction_audit.json"
        for item in full["evidence_artifacts"]
    )
