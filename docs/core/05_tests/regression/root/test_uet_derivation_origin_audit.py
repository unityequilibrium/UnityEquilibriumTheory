"""Regression tests for the derivation-origin audit."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path, repo_root

import json
from pathlib import Path


ROOT = (repo_root() / "docs")


def test_derivation_origin_audit_is_complete_without_physical_promotion():
    path = canonical_artifact_path("uet_derivation_origin_audit.json")
    report = json.loads(path.read_text(encoding="utf-8"))
    assert report["audit_status"] == "PASS"
    assert report["status"] == "PASS_WITH_DECLARED_OPEN_ORIGINS"
    assert report["metrics"]["registry_entry_count"] == 24
    assert report["metrics"]["open_or_candidate_relations"] > 0
    assert "UNCLASSIFIED_OPEN" not in report["metrics"]["origin_family_counts"]
    assert report["metrics"]["physical_promotions_allowed"] == 0
    assert report["gates"]["derived_is_distinguished_from_comparator"] is True
    assert report["gates"]["no_physical_promotion_from_relation_audit"] is True
