from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_berut_source_package_availability_boundary.json"


def load() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8-sig"))


def test_berut_source_boundary_closes_only_the_provenance_lane() -> None:
    artifact = load()
    assert artifact["status"] == "PASS_SCOPED_BERUT_SOURCE_PACKAGE_BOUNDARY"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    checks = artifact["verification_status"]
    positive_checks = [
        value
        for key, value in checks.items()
        if key not in {"xie_2026_accessed", "xie_2026_consumed"}
    ]
    assert all(positive_checks)
    assert checks["xie_2026_accessed"] is False
    assert checks["xie_2026_consumed"] is False
    assert artifact["claim_promotion"] is False


def test_berut_summary_is_not_calibration_data() -> None:
    artifact = load()
    assert artifact["numeric_rows_emitted"] == 0
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["parameter_fitting_performed"] is False
    assert artifact["target_data_used"] is False
    assert artifact["xie_2026_accessed"] is False
    assert artifact["local_source_inventory"]["raw_external_file_present"] is True
    assert artifact["local_source_inventory"]["raw_numeric_table_present"] is False
    assert "berut_permissioned_raw_numeric_package_missing" in artifact["open_blockers"]
