from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path, repo_root

import json
from pathlib import Path


ROOT = (repo_root() / "docs")
ARTIFACT = canonical_artifact_path(
    "t13_huberman_2019_public_pbte_boundary_audit.json"
)


def test_huberman_public_pbte_boundary_is_source_locked_without_accepted_payload() -> None:
    result = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert result["status"] == "PASS_HUBERMAN_PUBLIC_PBTE_BOUNDARY_NO_ACCEPTED_NUMERIC_PAYLOAD"
    assert result["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert result["source"]["reviewed_page_count"] == 22
    assert result["source"]["machine_readable_payload_files"] == []
    assert result["review_boundary"]["target_fit_performed"] is False
    assert result["review_boundary"]["alpha_Phi_K_fit_performed"] is False
    assert result["review_boundary"]["holdout_accessed"] is False
    assert result["major_result"]["dependency_unlocked"].startswith("Huberman graphite PBTE comparator provenance only")
