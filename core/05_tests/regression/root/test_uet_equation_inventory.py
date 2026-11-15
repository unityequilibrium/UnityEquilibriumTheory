"""Regression tests for the F0 topic formula inventory."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
import subprocess
import sys
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


def test_inventory_uses_current_root_without_reading_historical_copy(tmp_path):
    module = load_inventory_module()
    current = tmp_path / "topics/0.40_Fixture/FORMULA_AUDIT.md"
    current.parent.mkdir(parents=True)
    current.write_text("| Formula ID | Relation | Proof status |\n"
                       "| --- | --- | --- |\n| CURRENT | x = y | open |\n",
                       encoding="utf-8", newline="\n")
    old = tmp_path / "docs/topics/0.40_Fixture/FORMULA_AUDIT.md"
    old.parent.mkdir(parents=True)
    old.write_text("| Formula ID | Relation |\n| --- | --- |\n| OLD | x = z |\n", encoding="utf-8", newline="\n")
    result = module.build_inventory(tmp_path)
    assert [row["formula_id"] for row in result["records"]] == ["CURRENT"]
    assert result["records"][0]["source"]["path"] == "topics/0.40_Fixture/FORMULA_AUDIT.md"
    assert result["records"][0]["topic_id"] == "0.40"


def test_empty_inventory_is_not_a_pass_and_missing_topic_audit_is_visible(tmp_path):
    module = load_inventory_module()
    (tmp_path / "topics/0.40_Fixture").mkdir(parents=True)
    result = module.build_inventory(tmp_path)
    assert result["audit_status"] == "FAIL"
    assert result["inventory_gate_status"] == "BLOCKED"
    assert result["coverage"]["numbered_topic_count"] == 1
    assert result["coverage"]["topics_without_formula_audit"] == ["0.40_Fixture"]


def test_in_memory_inventory_does_not_write_old_scientific_artifact(tmp_path):
    module = load_inventory_module()
    artifact = tmp_path / "previous.json"
    artifact.write_bytes(b'{"historical":true}\n')
    module.OUTPUT = artifact
    before = artifact.read_bytes()
    module.build_inventory()
    assert artifact.read_bytes() == before


def test_no_write_cli_works_outside_repository_and_preserves_saved_artifact(tmp_path):
    module = load_inventory_module()
    before = module.OUTPUT.read_bytes()
    completed = subprocess.run([sys.executable, str(SCRIPT), "--no-write"], cwd=tmp_path,
                               capture_output=True, text=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "audit_status=PASS_WITH_DISCLOSED_GAPS" in completed.stdout
    assert "inventory_gate_status=BLOCKED" in completed.stdout
    assert "formula_audits_without_parsed_rows_count=" in completed.stdout
    assert "formula_audit_file_count=0\n" not in completed.stdout
    assert module.OUTPUT.read_bytes() == before


def test_ontology_header_adapter_preserves_combined_status_as_failure_not_proof(tmp_path):
    module = load_inventory_module()
    path = tmp_path / "topics/0.22_Fixture/FORMULA_AUDIT.md"
    path.parent.mkdir(parents=True)
    path.write_text("| ID | Ontology and relation | Variables / units | Conversion and unit closure | Parameter origin / derivation | Observable and code/artifact link | Status and failure mode | Next hardening |\n"
                    "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    "| T22-FIXTURE | x=y | normalized | no SI map | candidate mapping | example.py | not a physical proof | review |\n",
                    encoding="utf-8", newline="\n")
    row, = module.build_inventory(tmp_path)["records"]
    assert row["formula_id"] == "T22-FIXTURE"
    assert row["proof_status"] == ""
    assert row["failure_mode"] == "not a physical proof"
    assert row["source_fields"]["conversion and unit closure"] == "no SI map"
    assert row["source_fields"]["status and failure mode"] == "not a physical proof"


def test_mixed_inventory_discloses_files_without_supported_formula_rows(tmp_path):
    module = load_inventory_module()
    for topic, text in (("0.40_Valid", "| Formula ID | Relation |\n| --- | --- |\n| F | x=y |\n"),
                        ("0.41_Empty", "# Formula Audit\nProse only; no registered formula rows.\n")):
        path = tmp_path / f"topics/{topic}/FORMULA_AUDIT.md"
        path.parent.mkdir(parents=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    result = module.build_inventory(tmp_path)
    assert result["coverage"]["formula_audit_file_count"] == 2
    assert result["coverage"]["formula_audit_files_with_rows"] == 1
    assert result["coverage"]["formula_audits_without_parsed_rows"] == ["topics/0.41_Empty/FORMULA_AUDIT.md"]
    assert result["inventory_gate_status"] == "BLOCKED"
