"""Tests for the non-averaged final closure gate."""

from docs.scripts.audit.audit_uet_main_theory_closure import build_artifacts


def test_closure_does_not_average_away_blockers() -> None:
    closure, _, _, _ = build_artifacts()
    assert closure["overall_status"] == "BLOCKED"
    assert closure["categories"]["methodological_closure"]["status"] == "PASS"
    assert closure["categories"]["dimensional_observable_closure"]["status"] == "BLOCKED"
    assert closure["categories"]["empirical_status"]["status"] == "BLOCKED_NO_EXTERNAL_HOLDOUT"
    assert closure["aggregation_policy"].startswith("NO_AVERAGING")


def test_correspondence_and_falsification_boundaries_remain_explicit() -> None:
    _, matrix, falsification, report = build_artifacts()
    assert any(row["uet_layer"] == "C_density" and row["status"] == "MAPPING_INPUT_ONLY" for row in matrix["rows"])
    assert any(item["branch"] == "fundamental_unification" and item["current_state"] == "HYPOTHESIS_TRACK_BLOCKED" for item in falsification["criteria"])
    assert "not closed" in report
