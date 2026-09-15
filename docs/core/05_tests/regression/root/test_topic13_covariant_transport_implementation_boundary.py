from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_covariant_transport_implementation_boundary_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_transport_implementation_boundary_is_closed_for_lane() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_CLOSED_TRANSPORT_IMPLEMENTATION_BOUNDARY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_transport_boundary_does_not_emit_physical_result() -> None:
    audit = load(AUDIT)
    major = audit["major_result"]
    assert major["data_role"] == "INTERNAL_IMPLEMENTATION_SCOPE_NOT_PHYSICAL_TRANSPORT"
    assert "physical_Kubo_coefficient_record_missing" in major["open_blockers"]
    assert "finite_temperature_normal_component_not_derived" in major["open_blockers"]
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False
