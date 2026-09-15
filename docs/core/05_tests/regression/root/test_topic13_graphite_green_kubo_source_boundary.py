from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_graphite_green_kubo_source_boundary_audit.json"


def test_green_kubo_boundary_rejects_silent_uet_relabel() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    major = artifact["major_result"]

    assert artifact["status"] == "PASS_SCOPED_GRAPHITE_GREEN_KUBO_SOURCE_BOUNDARY"
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["numeric_transport_coefficient_emitted"] is False
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["xie_2026_accessed"] is False
    assert all(
        candidate["u_et_state_mapping"] == "MISSING"
        for candidate in artifact["candidates"]
    )
    assert "physical_Kubo_coefficient_record_missing" in major["open_blockers"]


def test_green_kubo_source_has_primary_locator_and_units_boundary() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert any(
        candidate["numeric_payload"].get("source_reported_300K_rows_W_mK")
        for candidate in artifact["candidates"]
        if isinstance(candidate["numeric_payload"], dict)
    )
    assert all(candidate["source_url"] for candidate in artifact["candidates"])
    assert artifact["major_result"]["units"]["source_comparator"] == "W m^-1 K^-1"

