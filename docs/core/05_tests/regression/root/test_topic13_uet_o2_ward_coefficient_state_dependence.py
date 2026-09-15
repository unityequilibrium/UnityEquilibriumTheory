from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_uet_o2_ward_coefficient_state_dependence_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_fixed_reference_ward_coefficient_state_dependence_is_closed_as_no_go() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_SCOPED_WARD_COEFFICIENT_STATE_DEPENDENCE_NO_GO"
    assert audit["major_result"]["major_result_id"] == (
        "T13_UET_O2_WARD_CONSTRAINED_COEFFICIENT_STATE_DEPENDENCE_NO_GO"
    )
    assert audit["major_result"]["closure_level"] == "CLOSED_AS_NO_GO"
    assert all(audit["checks"].values())
    assert audit["coefficient_range"]["spread"] > 1.0e-4
    assert audit["common_coefficient_interval"]["is_empty"] is True
    assert audit["claim_promotion"] is False


def test_state_dependence_no_go_preserves_holdout_boundary() -> None:
    audit = load(AUDIT)
    policy = audit["holdout_policy"]
    assert policy["xie_2026_accessed"] is False
    assert policy["target_curve_used"] is False
    assert policy["alpha_fit_used"] is False
    assert audit["parameter_policy"]["reference"] == (
        "fixed reference point and scale, held constant across all records"
    )


def test_state_dependence_no_go_does_not_unlock_full_topic() -> None:
    audit = load(AUDIT)
    full = load(FULL)
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_ward_constrained_coefficient_state_dependence_no_go"
    ]
    assert lane["status"] == audit["status"]
    assert lane["closure_level"] == "CLOSED_AS_NO_GO"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
