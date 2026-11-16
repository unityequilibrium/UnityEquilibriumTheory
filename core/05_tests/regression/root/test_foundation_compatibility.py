"""Regression tests for the repository-level foundation compatibility audit."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT = (repo_root() / "docs")
SCRIPT = ROOT / "scripts/audit/audit_uet_foundation_compatibility.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("uet_foundation_compatibility", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load audit module: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_audit_runs_and_keeps_foundation_blocked_by_remaining_dependencies():
    report = load_audit_module().build_report()

    assert report["audit_status"] == "PASS"
    assert report["compatibility_status"] == "BLOCKED"
    assert "legacy_potential_derivative_pair" not in report["controlling_blockers"]
    assert "legacy_information_operator" not in report["controlling_blockers"]
    assert "legacy_beta_unit_semantics" not in report["controlling_blockers"]
    assert "legacy_potential_derivative_pair" in {
        finding["finding_id"] for finding in report["findings"]
    }


def test_audit_distinguishes_canonical_closure_from_legacy_comparators():
    findings = {item["finding_id"]: item for item in load_audit_module().build_report()["findings"]}

    assert findings["legacy_potential_derivative_pair"]["status"] == "COMPATIBLE_CONDITIONAL"
    assert findings["legacy_potential_derivative_pair"]["metrics"]["canonical_max_absolute_residual"] <= findings["legacy_potential_derivative_pair"]["metrics"]["threshold"]
    assert findings["legacy_potential_derivative_pair"]["metrics"]["legacy_comparator_max_absolute_residual"] > findings["legacy_potential_derivative_pair"]["metrics"]["threshold"]
    assert findings["legacy_information_gradient_sign"]["status"] == "COMPATIBLE_CONDITIONAL"
    assert findings["legacy_information_operator"]["status"] == "COMPATIBLE_CONDITIONAL"
    assert findings["legacy_beta_unit_semantics"]["status"] == "COMPATIBLE_CONDITIONAL"
    assert findings["legacy_energy_conservation_claim"]["status"] == "NOT_ESTABLISHED"
    assert findings["covariant_gr_closed_limit"]["status"] == "COMPATIBLE_CONDITIONAL"
    assert findings["o2_to_legacy_double_well"]["status"] == "REJECTED_REDUCTION"


def test_missing_compatibility_input_is_not_treated_as_empty_or_success(tmp_path):
    module = load_audit_module()
    module.ROOT = tmp_path
    module.REGISTRY_PATH = tmp_path / "missing.json"
    report = module.build_report()
    assert report["audit_status"] == "FAIL"
    assert report["compatibility_status"] == "BLOCKED"
    assert "missing input: missing.json" in report["errors"]


def test_no_write_compatibility_cli_preserves_historical_artifact(tmp_path):
    module = load_audit_module()
    before = module.ARTIFACT_PATH.read_bytes()
    completed = subprocess.run([sys.executable, str(SCRIPT), "--no-write"], cwd=tmp_path,
                               capture_output=True, text=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "compatibility_status=BLOCKED" in completed.stdout
    assert module.ARTIFACT_PATH.read_bytes() == before
