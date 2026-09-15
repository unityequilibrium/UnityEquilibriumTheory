"""Regression tests for the F0 topic formula inventory."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
from pathlib import Path


ROOT = (repo_root() / "docs")
SCRIPT = ROOT / "scripts/audit/build_uet_equation_inventory.py"


def load_inventory_module():
    spec = importlib.util.spec_from_file_location("uet_equation_inventory", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load inventory module: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_inventory_discloses_scope_and_blocks_incomplete_foundation():
    inventory = load_inventory_module().build_inventory()

    assert inventory["audit_status"] == "PASS_WITH_DISCLOSED_GAPS"
    assert inventory["inventory_gate_status"] == "BLOCKED"
    assert inventory["coverage"]["formula_audit_file_count"] >= 20
    assert inventory["coverage"]["parsed_formula_row_count"] >= 200
    assert "0.1" in inventory["coverage"]["scaffold_topics"]
    assert inventory["summary"]["duplicate_formula_ids"] == {}


def test_inventory_keeps_standard_baselines_separate_from_uet_bridges():
    records = {
        row["formula_id"]: row for row in load_inventory_module().build_inventory()["records"]
    }

    assert records["T13-004"]["correspondence_status"] == "STANDARD_COUNTERPART_NOT_UET_DERIVATION"
    assert records["EW-01"]["correspondence_status"] == "UET_BRIDGE_OPEN"
    assert records["T01-001"]["evidence_class"] == "SCAFFOLD_BLOCKED"
    assert records["PT-CH-EVOLUTION"]["evidence_class"] == "INTERNAL_CHECKED"
