"""Tests for the non-promoting Core composition reference audit."""

import importlib.util
import json
from pathlib import Path


MODULE = Path(__file__).with_name("Research_T13_He4_Composition_Reference_Lineage.py")
SPEC = importlib.util.spec_from_file_location("t13_composition_reference_lineage", MODULE)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def test_current_composition_references_are_classified_without_promotion():
    result = AUDIT.audit()
    saved = json.loads(AUDIT.OUTPUT.read_text(encoding="utf-8"))
    # The historical commit exists in the original worktree but is not part of
    # this PR's ancestry. Its absence on CI must remain visible, not promoted.
    stable = lambda record: {key: value for key, value in record.items()
                             if key != "committed_snapshot_comparison"}
    assert stable(saved) == stable(result)
    assert len(result["records"]) == 12
    assert result["counts"]["RELOCATED_HASH_DRIFT"] == 12
    assert result["recorded_status_matches"] == 12
    historical = saved["committed_snapshot_comparison"]
    assert historical["counts"]["BYTE_IDENTICAL_TO_COMMIT"] == 9
    assert historical["counts"]["CHANGED_SINCE_COMMIT"] == 3
    if result["committed_snapshot_comparison"]["counts"]["COMMITTED_OBJECT_UNAVAILABLE"]:
        assert result["committed_snapshot_comparison"]["counts"]["COMMITTED_OBJECT_UNAVAILABLE"] == 12
    else:
        assert result["committed_snapshot_comparison"] == historical
    deltas = [delta["path"] for record in historical["records"] for delta in record.get("field_deltas", [])]
    assert "/major_result/evidence_artifacts/1/summary/closure_level" in deltas
    assert result["g0_baseline_ready"] is False
    assert result["full_core_unlock"] is False
    assert result["dependency_unlocked"] == []


def test_missing_reference_is_not_mistaken_for_relocation(tmp_path):
    row = {"path": "docs/core/artifacts/missing.json", "sha256": "0" * 64, "status": "PASS"}
    result = AUDIT._resolve(row, tmp_path, tmp_path / "docs/core/07_artifacts")
    assert result["classification"] == "MISSING"
    assert result["candidates"] == []


def test_ambiguous_basename_is_not_silently_selected(tmp_path):
    row = {"path": "docs/core/artifacts/a.json", "sha256": "0" * 64, "status": "PASS"}
    for folder in ("one", "two"):
        path = tmp_path / "docs/core/07_artifacts" / folder / "a.json"
        path.parent.mkdir(parents=True)
        path.write_text('{"status":"PASS"}', encoding="utf-8")
    result = AUDIT._resolve(row, tmp_path, tmp_path / "docs/core/07_artifacts")
    assert result["classification"] == "AMBIGUOUS"
    assert len(result["candidates"]) == 2


def test_field_delta_reports_nested_values_and_json_pointers():
    changes = AUDIT._field_deltas({"a/b": [{"status": None}]}, {"a/b": [{"status": "CLOSED_FOR_LANE"}]})
    assert changes == [{"path": "/a~1b/0/status", "before": None, "after": "CLOSED_FOR_LANE"}]
