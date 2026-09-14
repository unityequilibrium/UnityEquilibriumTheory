"""Regression checks for a completed bounded generated-artifact move."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
GOVERNANCE = ROOT / "docs" / "core" / "00_governance"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_bounded_artifact_move_has_one_canonical_copy_and_history() -> None:
    manifest = load_json(GOVERNANCE / "uet_core_artifact_migration_manifest.json")
    history = load_json(GOVERNANCE / "uet_core_artifact_migration_history.json")
    audit = load_json(GOVERNANCE / "uet_core_artifact_migration_audit.json")
    name = "matter_interaction_forward_verification.json"
    row = next(item for item in manifest["records"] if item["legacy_path"].endswith(name))
    history_row = next(item for item in history["records"] if item["legacy_path"] == row["legacy_path"])

    assert row["migration_state"] == "MIGRATED"
    assert history_row["migration_state"] == "MIGRATED"
    assert not (ROOT / row["legacy_path"]).exists()
    target = ROOT / row["canonical_path"]
    assert target.exists()
    assert target.read_bytes()
    assert row["sha256_after"] == history_row["sha256_after"]
    assert row["consumer_count"] == 0
    assert row["downstream_dependencies"] == []
    assert manifest["summary"]["migrated_files"] >= 2
    assert audit["status"] == "PASS"
    checks = {item["check_id"]: item for item in audit["checks"]}
    assert checks["migrated_canonical_targets_exist"]["status"] == "PASS"
    assert checks["migrated_legacy_sources_absent"]["status"] == "PASS"
    assert checks["migration_history_matches_manifest"]["status"] == "PASS"


def test_migrated_generators_use_canonical_path_authority() -> None:
    generators = {
        "audit_matter_interaction_forward.py": "matter_interaction_forward_verification.json",
        "audit_resource_selection_physical_cost_map.py": "resource_selection_physical_cost_map_verification.json",
    }
    for generator_name, artifact_name in generators.items():
        generator = ROOT / "docs" / "scripts" / "audit" / generator_name
        text = generator.read_text(encoding="utf-8")
        assert "canonical_artifact_path" in text
        assert f"docs/core/artifacts/{artifact_name}" not in text
