"""Ensure the causal-branch major result has explicit holdout fields."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_causal_branch_selection_audit.json"


def test_causal_branch_audit_has_explicit_no_data_use_fields() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["parameter_fitting_performed"] is False
    assert artifact["source_rows_consumed"] is False
    assert artifact["target_data_used"] is False
    assert artifact["xie_2026_accessed"] is False
