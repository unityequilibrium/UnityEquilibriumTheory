"""Regression tests for the core equation-family ownership contract."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
from pathlib import Path


ROOT = (repo_root() / "docs")
SCRIPT = ROOT / "scripts/audit/build_uet_core_equation_family_contract.py"


def load_contract_module():
    spec = importlib.util.spec_from_file_location("uet_core_family_contract", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load family contract module: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_all_core_code_surface_modules_have_an_owner():
    contract = load_contract_module().build_contract()

    assert contract["audit_status"] == "PASS"
    assert contract["contract_status"] == "BLOCKED"
    assert contract["coverage"]["core_code_surface_file_count"] >= 32
    assert contract["coverage"]["assigned_module_path_count"] >= contract["coverage"]["core_code_surface_file_count"]
    assert contract["coverage"]["missing_core_paths"] == []
    assert contract["coverage"]["equation_family_count"] >= 9


def test_family_contract_preserves_conflict_and_conditional_boundaries():
    families = {item["family_id"]: item for item in load_contract_module().build_contract()["families"]}

    assert families["core.legacy_master"]["mathematical_compatibility_status"] == "CONTRADICTION_AND_CONFLICT"
    assert families["core.matter_space"]["mathematical_compatibility_status"].endswith("CAUSAL_GATE_FAILS")
    assert families["core.covariant_response"]["old_theory_special_case_status"].endswith("only")
    assert families["core.o2_superfluid"]["unit_lane"] == "natural_units"
    assert families["core.parameter_contract"]["equation_family"] is False
