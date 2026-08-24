from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_mp48_mode_resolved_csrc_diagnostic.json"
PAYLOAD = ROOT / "docs/core/artifacts/t13_mp48_mode_resolved_csrc_diagnostic.npz"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_mp48_mode_resolved_diagnostic_is_row_addressable_and_not_core_acceptance() -> None:
    artifact = load(ARTIFACT)
    assert artifact["status"] == "PASS_MP48_MODE_RESOLVED_DERIVED_COMPARISON"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["major_result"]["data_role"] == "DERIVED_COMPARISON"
    assert artifact["derived_payload"]["uncertainty_status"] == "NOT_SOURCE_GRADE"
    assert artifact["derived_payload"]["material_mapping_status"] == "OPEN"
    assert artifact["holdout_policy"]["xie_2026_accessed"] is False
    assert artifact["derived_payload"]["sha256"] == digest(PAYLOAD)
    assert all(artifact["checks"].values())


def test_mp48_mode_resolved_diagnostic_keeps_core_blockers_explicit() -> None:
    artifact = load(ARTIFACT)
    blockers = set(artifact["major_result"]["open_blockers"])
    assert "third_order_PBTE_transport_and_Ding_material_state_equivalence_missing" in blockers
    assert "source_grade_uncertainty_missing" in blockers
    assert artifact["major_result"]["dependency_unlocked"].startswith("Only a row-level")
