"""Regression checks for non-destructive Topic 13 audit regeneration."""

from __future__ import annotations

from docs.scripts.audit.audit_topic13_energy_response_bridge import (
    merge_prior_artifact,
)


def test_merge_preserves_prior_provenance_and_refreshes_current_fields() -> None:
    prior = {
        "schema_version": "t13-energy-response-bridge-audit-v1",
        "artifact": "t13_energy_response_bridge_audit",
        "source_anchor": {"status": "SOURCE_CP_ANCHOR"},
        "standard_pbte_source_anchor": {"status": "PBTE_ANCHOR"},
        "major_result": {
            "what_is_closed": ["prior source-backed detail"],
            "evidence_artifacts": [
                {"path": "docs/core/artifacts/prior_detail.json"},
                {"path": "docs/core/artifacts/current.json", "sha256": "old"},
            ],
            "controlling_blocker": "stale-blocker-detail",
        },
        "controlling_blocker": "stale-top-level-blocker",
    }
    report = {
        "schema_version": "t13-energy-response-bridge-audit-v1",
        "artifact": "t13_energy_response_bridge_audit",
        "major_result": {
            "what_is_closed": "current generated detail",
            "evidence_artifacts": [
                {"path": "docs/core/artifacts/current.json", "sha256": "new"},
            ],
            "controlling_blocker": "current-blocker-detail",
        },
        "controlling_blocker": "current-top-level-blocker",
    }

    merged = merge_prior_artifact(report, prior)

    assert merged["source_anchor"] == prior["source_anchor"]
    assert merged["standard_pbte_source_anchor"] == prior["standard_pbte_source_anchor"]
    assert merged["controlling_blocker"] == "current-top-level-blocker"
    assert merged["major_result"]["controlling_blocker"] == "current-blocker-detail"
    assert merged["major_result"]["what_is_closed"] == [
        "prior source-backed detail",
        "current generated detail",
    ]
    evidence = merged["major_result"]["evidence_artifacts"]
    assert evidence[0]["sha256"] == "new"
    assert {item["path"] for item in evidence} == {
        "docs/core/artifacts/current.json",
        "docs/core/artifacts/prior_detail.json",
    }
    assert merged["artifact_provenance"]["prior_artifact_preserved"] is True
    assert "docs/core/artifacts/prior_detail.json" in merged["artifact_provenance"][
        "preserved_evidence_artifacts"
    ]


def test_merge_without_prior_report_is_identity() -> None:
    report = {"artifact": "t13_energy_response_bridge_audit", "status": "PASS"}
    assert merge_prior_artifact(report, None) is report
