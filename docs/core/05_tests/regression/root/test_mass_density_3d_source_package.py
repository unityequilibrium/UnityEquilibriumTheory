"""Regression tests for the metadata-only external 3D source gate."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
from pathlib import Path


ROOT = (repo_root() / "docs")
SCRIPT = ROOT / "scripts/audit/audit_mass_density_3d_source_package.py"


def load_module():
    spec = importlib.util.spec_from_file_location("mass_density_3d_source_package", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load source-package audit: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_metadata_only_source_package_is_structurally_auditable():
    artifact = load_module().build_artifact()
    assert artifact["audit_status"] == "PASS_WITH_BLOCKED_EXTERNAL_SOURCE_PACKAGE"
    assert artifact["claim_status"] == "SOURCE_CANDIDATE_METADATA_ONLY"
    assert artifact["gates"]["local_raw_path_and_hash_are_explicitly_missing"]
    assert artifact["gates"]["fit_and_parameter_tuning_are_blocked"]


def test_source_package_does_not_promote_c_to_mass():
    artifact = load_module().build_artifact()
    finding = artifact["research_finding"]
    assert "not automatically" in finding["non_equivalence"]
    assert artifact["gates"]["synthetic_operator_does_not_promote_physical_map"]
    assert artifact["unit_and_observable_boundary"]["C_to_shape_status"] == "OPEN"
