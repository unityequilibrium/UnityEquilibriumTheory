from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_auxiliary_field_condensed_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_auxiliary_field_condensed_lane_closes_formal_ward_boundary() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_FORMAL_WARD_PRESERVING_AUXILIARY_FIELD_CONDENSED_LANE"
    assert audit["major_result"]["major_result_id"] == (
        "T13_UET_O2_AUXILIARY_FIELD_WARD_PRESERVING_CONDENSED_LANE"
    )
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_auxiliary_field_lane_is_ward_gapless_without_statewise_counterterm() -> None:
    audit = load(AUDIT)
    records = audit["state_records"]
    assert max(abs(record["ward_phase_gap_sq"]) for record in records) <= 1.0e-10
    assert max(abs(record["auxiliary_gap_residual"]) for record in records) <= 1.0e-10
    assert all(record["condensate_amplitude_sq"] > 0.0 for record in records)
    assert audit["parameter_policy"]["counterterm"] == (
        "no state-dependent Ward coefficient is introduced"
    )
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["target_curve_used"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False


def test_auxiliary_field_lane_does_not_unlock_full_topic() -> None:
    audit = load(AUDIT)
    full = load(FULL)
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_auxiliary_field_ward_preserving_condensed_lane"
    ]
    assert lane["status"] == audit["status"]
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
