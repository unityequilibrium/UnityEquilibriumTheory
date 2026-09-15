from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_scheme_identifiability_no_go.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_finite_temperature_scheme_no_go_passes() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_SCOPED_NO_GO_FINITE_TEMPERATURE_SCHEME_IDENTIFIABILITY"
    assert audit["formal_no_go_closure"] == "CLOSED_AS_NO_GO"
    assert (
        audit["major_result"]["major_result_id"]
        == "T13_UET_O2_FINITE_T_SCHEME_IDENTIFIABILITY_NO_GO"
    )
    assert audit["major_result"]["closure_level"] == "CLOSED_AS_NO_GO"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_finite_temperature_scheme_no_go_keeps_named_branch_conditional() -> None:
    audit = load(AUDIT)
    assert "physical_Kubo_coefficient_record_missing" in audit["major_result"][
        "open_blockers"
    ]
    assert "alpha_Phi_K_independent_calibration_missing" in audit["major_result"][
        "open_blockers"
    ]
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["target_curve_used"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False


def test_full_gate_exposes_scheme_no_go_without_promoting_topic() -> None:
    full = load(FULL)
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_finite_t_scheme_identifiability_no_go"
    ]
    assert lane["status"] == "PASS_SCOPED_NO_GO_FINITE_TEMPERATURE_SCHEME_IDENTIFIABILITY"
    assert lane["closure_level"] == "CLOSED_AS_NO_GO"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
