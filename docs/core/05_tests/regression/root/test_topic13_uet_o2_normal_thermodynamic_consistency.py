from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_normal_thermodynamic_consistency_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_normal_thermodynamic_consistency_lane_passes() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_ACTION_DERIVED_NORMAL_THERMODYNAMIC_CONSISTENCY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_normal_thermodynamic_consistency_does_not_promote_physics() -> None:
    audit = load(AUDIT)
    assert audit["numeric_alpha_Phi_K_emitted"] is False
    assert audit["numeric_e0_emitted"] is False
    assert audit["physical_transport_coefficients_emitted"] is False
    assert audit["parameter_fitting_performed"] is False
    assert audit["target_data_used"] is False
    assert audit["xie_2026_accessed"] is False
    assert "alpha_Phi_K_missing" in audit["major_result"]["open_blockers"]
