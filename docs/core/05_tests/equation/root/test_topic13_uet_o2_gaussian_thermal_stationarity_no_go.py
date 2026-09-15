from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_gaussian_thermal_stationarity_no_go.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_thermal_gaussian_stationarity_no_go_passes() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_SCOPED_NO_GO_THERMAL_GAUSSIAN_CONDENSATE_STATIONARITY"
    assert audit["formal_no_go_closure"] == "CLOSED_AS_NO_GO"
    assert audit["major_result"]["major_result_id"] == "T13_UET_O2_GAUSSIAN_THERMAL_STATIONARITY_NO_GO"
    assert audit["major_result"]["closure_level"] == "CLOSED_AS_NO_GO"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_no_go_keeps_interacting_branch_open() -> None:
    audit = load(AUDIT)
    assert audit["reference"]["interacting_self_energy_included"] is False
    assert audit["reference"]["vacuum_counterterm_included"] is False
    assert "interacting_finite_temperature_self_energy_and_self_consistent_phase_boundary_missing" in audit["major_result"]["open_blockers"]
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["target_curve_used"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False


def test_full_gate_exposes_no_go_without_promoting_topic() -> None:
    full = load(FULL)
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_gaussian_thermal_stationarity_no_go"
    ]
    assert lane["status"] == "PASS_SCOPED_NO_GO_THERMAL_GAUSSIAN_CONDENSATE_STATIONARITY"
    assert lane["closure_level"] == "CLOSED_AS_NO_GO"
    assert lane["renormalized_interacting_branch_required"] is True
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
