from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/07_artifacts/topic13/t13_ding_fig1d_normalized_source_lane_audit.json"
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_ding_figure_lane_is_closed_without_raw_source_or_calibration_claim() -> None:
    lane = load(LANE)
    major = lane["major_result"]
    assert lane["status"] == "PASS_DING_FIGURE_DERIVED_NORMALIZED_SOURCE_LANE"
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert major["data_role"] == "FIGURE_DERIVED_NORMALIZED_COMPARISON_NOT_RAW_SOURCE"
    assert lane["verification"]["row_count"] == 432
    assert lane["verification"]["holdout_consumed"] is False
    assert lane["verification"]["numeric_fitting_allowed"] is False
    assert lane["verification"]["raw_author_numeric_source_present"] is False
    assert "independent_alpha_Phi_K_calibration_missing" in major["open_blockers"]


def test_full_gate_exposes_ding_lane_but_keeps_full_source_and_alpha_blocked() -> None:
    full = load(FULL)
    source = full["verification_status"]["source_package"]
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "ding_fig1d_normalized_source_lane"
    ]
    assert lane["major_result_id"] == "T13_DING_FIG1D_NORMALIZED_SOURCE_LANE"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert source["status"] == "BLOCKED"
    assert source["raw_author_numeric_source_present"] is False
    assert full["verification_status"]["alpha_Phi_K"]["status"] == "BLOCKED"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False


def test_register_contains_ding_lane_with_required_claim_boundary() -> None:
    register = load(REGISTER)
    entry = next(
        item for item in register["entries"]
        if item["major_result_id"] == "T13_DING_FIG1D_NORMALIZED_SOURCE_LANE"
    )
    assert entry["closure_level"] == "CLOSED_FOR_LANE"
    assert "not raw author numeric data" in entry["claim_boundary"]
