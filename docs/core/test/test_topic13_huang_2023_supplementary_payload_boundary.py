from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/t13_huang_2023_supplementary_payload_boundary_audit.json"


def test_huang_public_supplementary_boundary_is_source_locked_without_payload() -> None:
    result = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert result["status"] == "PASS_HUANG_PUBLIC_SUPPLEMENTARY_BOUNDARY_NO_NUMERIC_PBTE_PAYLOAD"
    assert result["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert result["source"]["reviewed_page_count"] == 9
    assert result["source"]["machine_readable_payload_files"] == []
    assert result["review_boundary"]["target_fit_performed"] is False
    assert result["review_boundary"]["alpha_Phi_K_fit_performed"] is False
    assert result["review_boundary"]["holdout_accessed"] is False
    assert result["major_result"]["dependency_unlocked"].startswith("Huang graphite comparator provenance only")
