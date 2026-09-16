"""Schema checks for the core organization enforcement control plane."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
GOVERNANCE = ROOT / "docs/core/00_governance"


def load(name: str) -> dict:
    return json.loads((GOVERNANCE / name).read_text(encoding="utf-8"))


def test_enforcement_subaudits_exist_and_are_organization_only() -> None:
    audit = load("uet_core_migration_enforcement_audit.json")
    assert audit["artifact"] == "uet_core_migration_enforcement_audit"
    assert "physics-status promotion" in audit["claim_boundary"]
    assert set(audit["subaudits"]) == {"paths", "imports", "links"}


def test_path_audit_preserves_physics_boundary() -> None:
    audit = load("uet_core_paths_audit.json")
    assert audit["artifact"] == "uet_core_paths_audit"
    assert "physics-status promotion" in audit["claim_boundary"]


def test_physical_planner_models_canonical_source_and_archived_alias_without_collision() -> None:
    source = ROOT / "docs/scripts/audit/plan_uet_core_physical_migration.py"
    spec = importlib.util.spec_from_file_location("uet_core_physical_planner", source)
    assert spec is not None and spec.loader is not None
    planner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(planner)
    records, summary = planner.build_records()
    canonical = next(
        item for item in records
        if item["current_path"] == "docs/core/02_equations/covariant/uet_covariant_response.py"
    )
    assert canonical["migration_state"] == "MIGRATED"
    aliases = load("uet_core_legacy_module_aliases.json")
    alias = next(
        item for item in aliases["aliases"]
        if item["legacy_module"] == "docs.core.uet_covariant_response"
    )
    assert alias["canonical_path"] == canonical["canonical_path"]
    assert alias["status"] == "ARCHIVED_ROOT_SHIM"
    assert (ROOT / alias["archive_path"]).exists()
    assert not summary["duplicate_targets"]
