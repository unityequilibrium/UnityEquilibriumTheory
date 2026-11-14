from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/provenance/ding_2022_source_mapping_audit.json"
MAPPING = ROOT / "docs/core/07_artifacts/archive/ding_2022_fig1d_series_mapping.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_ding_numeric_intake_has_permitted_figure_route_but_is_not_raw_data() -> None:
    artifact = load(ARTIFACT)
    # The permitted figure route is usable for normalized comparison, but the
    # missing author numeric payload must keep the full source lane blocked.
    assert artifact["status"] == "PASS"
    assert artifact["source_route_ready_for_full_closure"] is False
    assert artifact["normalized_comparison_route_ready"] is True
    checks = artifact["checks"]
    assert checks["numeric_hash_matches_manifest"] is True
    assert checks["figure_hash_matches_manifest"] is True
    assert checks["mapping_hash_matches_manifest"] is True
    assert checks["row_identity_complete"] is True
    assert checks["units_declared"] is True
    assert checks["uncertainty_declared"] is True
    assert checks["preprocessing_declared"] is True
    assert checks["license_declared"] is True
    assert checks["raw_author_numeric_source_present"] is False
    assert checks["permitted_figure_numeric_route_ready"] is True
    assert checks["color_to_period_mapping_closed"] is True
    assert checks["holdout_not_accessed"] is True
    assert artifact["controlling_blocker"] is None


def test_ding_legend_mapping_is_explicit_and_not_dip_inferred() -> None:
    mapping = load(MAPPING)
    assert mapping["status"] == "PASS"
    assert mapping["series_to_grating_period_um"] == {
        "blue_trace": 2.0,
        "red_trace": 3.0,
        "green_trace": 4.0,
    }
    assert mapping["checks"]["mapping_is_read_from_printed_legend"] is True
    assert mapping["checks"]["mapping_not_derived_from_dip_order"] is True
    assert mapping["checks"]["xie_2026_not_accessed"] is True


def test_ding_mapping_diagnostic_does_not_override_printed_legend() -> None:
    artifact = load(ARTIFACT)
    diagnostic = artifact["mapping_diagnostic"]
    assert diagnostic["candidate_assignment_count"] == 6
    assert "direct printed-legend mapping artifact" in diagnostic["diagnostic_use"]
