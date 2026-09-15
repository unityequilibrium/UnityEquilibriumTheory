"""Tests for the preregistered Gaia 3D query/holdout contract."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
from pathlib import Path


ROOT = (repo_root() / "docs")
SCRIPT = ROOT / "scripts/audit/audit_gaia_3d_query_manifest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("gaia_3d_query_manifest", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Gaia query audit: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_query_manifest_is_auditable_but_data_intake_is_blocked():
    artifact = load_module().build_artifact()
    assert artifact["audit_status"] == "PASS_WITH_BLOCKED_DATA_INTAKE"
    assert artifact["claim_status"] == "PREREGISTERED_QUERY_AND_HOLDOUT_ONLY"
    assert artifact["gates"]["raw_data_absence_is_explicit"]
    assert artifact["gates"]["fit_and_tuning_are_blocked"]


def test_distance_and_holdout_controls_are_explicit():
    artifact = load_module().build_artifact()
    assert artifact["gates"]["parallax_bias_policy_is_not_silent"]
    assert artifact["gates"]["distance_estimator_policy_is_explicit"]
    assert artifact["gates"]["calibration_holdout_split_is_disjoint_and_unconsumed"]
    assert "source counts as rho_3D" in artifact["forbidden_uses"][0]
