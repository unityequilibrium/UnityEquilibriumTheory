"""Checks for the generated-artifact migration review queue."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
GOVERNANCE = ROOT / "docs" / "core" / "00_governance"
QUEUE = ROOT / "docs" / "core" / "07_artifacts" / "gates" / "uet_core_artifact_generator_review_queue.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_review_queue_is_current_and_machine_readable() -> None:
    manifest = load_json(GOVERNANCE / "uet_core_artifact_migration_manifest.json")
    queue = load_json(QUEUE)

    assert queue["schema_version"] == "uet-core-artifact-generator-review-queue-v1"
    assert queue["canonical_path_authority"] == "docs/core/core_paths.py"
    assert queue["source_manifest"]["path"] == "docs/core/00_governance/uet_core_artifact_migration_manifest.json"
    assert queue["source_manifest"]["sha256"] == sha256(GOVERNANCE / "uet_core_artifact_migration_manifest.json")
    assert queue["summary"]["status"] == "PASS_WITH_REVIEW_REQUIRED"
    assert queue["summary"]["claim_boundary"].startswith("organization control only")

    records = queue["records"]
    assert len(records) == queue["summary"]["records_total"]
    pending_records = [row for row in records if row["review_category"] != "MIGRATED"]
    assert queue["summary"]["pending_records"] == len(pending_records)
    assert queue["summary"]["migrated_records"] == 2
    assert len(records) == len(pending_records) + queue["summary"]["migrated_records"]

    manifest_categories = {
        "GENERATOR_IDENTITY_UNRESOLVED": 0,
        "GENERATOR_AND_CONSUMER_REWRITE_REQUIRED": 0,
        "GENERATOR_SWITCH_REQUIRED": 0,
        "MIGRATED": 0,
    }
    for row in records:
        manifest_categories[row["review_category"]] += 1
        assert row["claim_boundary"].startswith("organization control only")
        if row["review_category"] == "GENERATOR_IDENTITY_UNRESOLVED":
            assert row["generator_count"] == 0
            assert row["generator_status"]["status"] == "UNRESOLVED"

    assert queue["summary"]["category_counts"] == manifest_categories
    assert queue["summary"]["category_counts"]["GENERATOR_IDENTITY_UNRESOLVED"] == 536
    assert queue["summary"]["category_counts"]["GENERATOR_SWITCH_REQUIRED"] == 4

    migrated_paths = {
        row["legacy_path"]
        for row in manifest["records"]
        if row["migration_state"] == "MIGRATED"
    }
    assert migrated_paths
    assert not migrated_paths.intersection({row["legacy_path"] for row in pending_records})
