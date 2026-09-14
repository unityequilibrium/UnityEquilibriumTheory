"""Schema checks for the core organization enforcement control plane."""

from __future__ import annotations

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
