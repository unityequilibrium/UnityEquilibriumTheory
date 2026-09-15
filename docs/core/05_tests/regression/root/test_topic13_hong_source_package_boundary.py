from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_hong_final_source_package_boundary.json"


def load() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8-sig"))


def test_hong_final_source_boundary_closes_only_identity_lane() -> None:
    artifact = load()
    assert artifact["status"] == "PASS_SCOPED_HONG_FINAL_SOURCE_BOUNDARY"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["verification_status"].values())
    assert artifact["claim_promotion"] is False


def test_hong_legacy_row_is_not_selected_as_calibration_data() -> None:
    artifact = load()
    assert artifact["numeric_rows_emitted"] == 0
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["parameter_fitting_performed"] is False
    assert artifact["target_data_used"] is False
    assert artifact["xie_2026_accessed"] is False
    assert "hong_machine_readable_numeric_row_parity_and_legacy_row_policy_not_closed" in artifact["open_blockers"]
