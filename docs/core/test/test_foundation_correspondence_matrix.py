"""Regression tests for the focused cross-topic correspondence matrix."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
from pathlib import Path


ROOT = (repo_root() / "docs")
SCRIPT = ROOT / "scripts/audit/build_uet_foundation_correspondence_matrix.py"


def load_matrix_module():
    spec = importlib.util.spec_from_file_location("uet_correspondence_matrix", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load matrix module: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_matrix_keeps_standard_baseline_open_bridge_and_conflict_distinct():
    matrix = load_matrix_module().build_matrix()
    rows = {row["matrix_id"]: row for row in matrix["rows"]}

    assert matrix["audit_status"] == "PASS"
    assert matrix["matrix_status"] == "BLOCKED"
    assert rows["T13-004"]["compatibility_status"] == "COMPATIBLE_STANDARD_IDENTITY"
    assert rows["EW-01"]["uet_derivation_status"] == "NOT_ESTABLISHED"
    assert rows["uet.legacy.master_potential"]["compatibility_status"] == "CONTRADICTION"
    assert rows["T01-001"]["special_case_status"] == "NOT_TESTABLE"


def test_foundation_gate_preserves_normalized_subgates_without_physical_promotion():
    import json
    gate = json.loads((ROOT / "core/artifacts/uet_foundation_dependency_gate.json").read_text(encoding="utf-8"))
    assert gate["gates"]["F3_units"]["status"] == "BLOCKED"
    assert gate["gates"]["F3_units"]["normalized_subgate"]["status"] == "PASS_NORMALIZED_OR_NATURAL_ONLY"
    assert gate["gates"]["F7_observable_mapping"]["status"] == "BLOCKED"
    assert gate["gates"]["F7_observable_mapping"]["normalized_subgate"]["status"] == "PASS_DECLARED_INTERNAL_OPERATORS_ONLY"
    assert gate["gates"]["F7_observable_mapping"]["metrics"]["accepted_physical_observable_lanes"] == 0
    assert gate["source_and_calibration_snapshot"]["gaia_3d_query_manifest_status"] == "PASS_WITH_BLOCKED_DATA_INTAKE"
    assert gate["source_and_calibration_snapshot"]["gaia_3d_holdout_consumed"] is False
    assert gate["source_and_calibration_snapshot"]["thermal_scale_identifiability_status"] == "NON_IDENTIFIABLE_FROM_NORMALIZED_PHI"
