"""Regression tests for the implementation-only equation surface scan."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
from pathlib import Path


ROOT = (repo_root() / "docs")
SCRIPT = ROOT / "scripts/audit/build_uet_code_surface_inventory.py"


def load_surface_module():
    spec = importlib.util.spec_from_file_location("uet_code_surface_inventory", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load code-surface module: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_code_surface_scan_blocks_unclassified_implementation_surfaces():
    inventory = load_surface_module().build_inventory()

    assert inventory["audit_status"] == "PASS_WITH_DISCLOSED_GAPS"
    assert inventory["inventory_gate_status"] == "BLOCKED"
    assert inventory["coverage"]["core_python_file_count"] >= 30
    assert inventory["coverage"]["candidate_surface_count"] > 1000
    assert inventory["coverage"]["unlinked_core_file_count"] > 0
    assert all(row["claim_status"] == "NOT_EVIDENCE" for row in inventory["records"][:50])
