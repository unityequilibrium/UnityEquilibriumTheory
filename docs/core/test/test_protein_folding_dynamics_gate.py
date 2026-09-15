"""Regression checks for the protein-folding dynamics Wave-0 gate."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
import json
from pathlib import Path


ROOT = repo_root()
TOPIC = ROOT / "docs" / "topics" / "0.22_Biophysics_Origin_of_Life"
SCRIPT = TOPIC / "Code" / "03_Research" / "Research_Protein_Folding_Dynamics_Gate.py"


def _module():
    spec = importlib.util.spec_from_file_location(
        "protein_folding_dynamics_gate", SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_wave_zero_gate_is_explicitly_blocked_without_source_or_runtime() -> None:
    module = _module()
    artifact = module.build_gate()

    assert artifact["gate_status"] == "BLOCKED"
    assert artifact["claim_class"] == "B"
    assert artifact["data_class"] == "source_referenced_only"
    assert artifact["controlling_blocker"] == (
        "source_locked_cohort_and_atomistic_runtime_missing"
    )
    assert artifact["checks"]["external_download_performed"] is False
    assert artifact["checks"]["atomistic_result_generated"] is False
    assert artifact["source_summary"]["cohort_entries_present"] == 0


def test_gate_inputs_are_repository_relative_and_hashed() -> None:
    module = _module()
    artifact = module.build_gate()

    assert artifact["resolution_base"] == "repository_root"
    assert artifact["resolution_status"] == "resolved"
    assert len(artifact["resolved_input_paths"]) == 3
    assert set(artifact["resolved_input_paths"]) == set(artifact["input_hashes"])
    assert all(len(value) == 64 for value in artifact["input_hashes"].values())
    assert all(not Path(value).is_absolute() for value in artifact["resolved_input_paths"])


def test_dynamic_manifests_are_valid_json_and_keep_source_rows_unfrozen() -> None:
    data = json.loads(
        (TOPIC / "DYNAMICS_DATA_MANIFEST.json").read_text(encoding="utf-8")
    )
    runtime = json.loads(
        (TOPIC / "DYNAMICS_RUNTIME_MANIFEST.json").read_text(encoding="utf-8")
    )

    assert data["cohort_contract"]["target_total"] == 12
    assert data["cohort_contract"]["development_total"] == 8
    assert data["cohort_contract"]["holdout_total"] == 4
    assert data["cohort_contract"]["entries"] == []
    assert all(record["status"] == "source_target_only" for record in data["source_records"])
    assert runtime["force_field_contract"]["asset_status"] == "not_present"
    assert all(item["status"] == "not_checked" for item in runtime["required_packages"])
