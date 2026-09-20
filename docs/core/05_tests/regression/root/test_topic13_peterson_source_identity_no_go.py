from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_peterson_source_identity_no_go.json"


def load() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8-sig"))


def test_peterson_identity_conflict_is_closed_as_scoped_no_go() -> None:
    artifact = load()
    assert artifact["status"] == "PASS_SCOPED_PETERSON_SOURCE_IDENTITY_NO_GO"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["verification_status"].values())
    assert artifact["claim_promotion"] is False


def test_peterson_no_go_admits_no_numeric_row() -> None:
    artifact = load()
    assert artifact["numeric_rows_emitted"] == 0
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["parameter_fitting_performed"] is False
    assert artifact["target_data_used"] is False
    assert artifact["xie_2026_accessed"] is False
    assert "peterson_legacy_label_demoted_no_admissible_row_until_exact_source_selected" in artifact["open_blockers"]
