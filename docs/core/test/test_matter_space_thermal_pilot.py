"""Artifact and claim-boundary checks for the 0.13 matter-space thermal pilot."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path


ROOT = repo_root()
TOPIC = ROOT / "docs" / "topics" / "0.13_Thermodynamic_Bridge"
DATA = TOPIC / "Data" / "03_Research"
ARTIFACT = TOPIC / "Result" / "artifacts" / "matter_space_thermal_control.json"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_source_package_exposes_figure_derived_comparison_and_holdout_boundary() -> None:
    package = _read(DATA / "matter_space_second_sound_source_package.json")
    assert package["status"] == "FIGURE_DERIVED_NORMALIZED_COMPARISON_READY_RAW_AUTHOR_C_SRC_OPEN"
    assert package["usage_policy"]["numeric_fitting_allowed"] is False
    assert package["usage_policy"]["observable_map_status"] == "NORMALIZED_DEFINED_DIMENSIONAL_BLOCKED"
    assert any(source.get("local_numeric_path") for source in package["sources"] if "holdout" not in source["source_id"])
    assert all(source.get("local_numeric_path") is None for source in package["sources"] if "holdout" in source["source_id"])
    holdout = next(source for source in package["sources"] if "holdout" in source["source_id"])
    assert holdout["status"] == "HOLDOUT_LOCKED_METADATA_ONLY"
    assert "prohibited" in holdout["benchmark_role"]


def test_preregistration_and_amendment_preserve_parameter_boundary() -> None:
    prereg = _read(DATA / "matter_space_thermal_preregistration.json")
    amendment = _read(DATA / "matter_space_thermal_numerical_amendment_001.json")
    assert prereg["status"] == "LOCKED_BEFORE_EXECUTION"
    assert prereg["external_numeric_inputs"] == []
    assert amendment["status"] == "POST_DIAGNOSTIC_NUMERICAL_AMENDMENT"
    assert amendment["blind_preregistration"] is False
    assert amendment["trigger"]["locked_dt"] == prereg["nonlinear_primary"]["dt"]
    assert amendment["amendment"]["analysis_dt"] < amendment["trigger"]["locked_dt"]
    for key in (
        "physical_parameters_changed",
        "thresholds_changed",
        "external_data_added",
        "parameter_fitting",
        "seed_changed",
    ):
        assert amendment["amendment"][key] is False


def test_artifact_stays_simulation_only_and_reports_failed_dependencies() -> None:
    artifact = _read(ARTIFACT)
    assert artifact["status"] == "SIMULATION_ONLY"
    assert artifact["internal_gate_status"] == "FAIL"
    assert artifact["external_validation"] is False
    assert artifact["controlling_blocker"] == "core_prearrival_leakage"
    assert artifact["gates"]["prearrival_leakage"] is False
    assert artifact["gates"]["external_source_ready"] is False
    assert artifact["run_integrity"]["trace_backreaction"] is False
    assert artifact["run_integrity"]["external_numeric_data_used"] is False


def test_control_and_refined_ledger_gates_are_machine_readable() -> None:
    artifact = _read(ARTIFACT)
    for gate in (
        "cattaneo_analytical_residual",
        "cattaneo_phase",
        "cattaneo_lag",
        "cattaneo_hysteresis",
        "cattaneo_convergence",
        "homogeneous_core_crosscheck",
        "ledger_closure_refined",
        "source_sign",
        "trace_source_sign",
        "causal_arrival_speed",
    ):
        assert artifact["gates"][gate] is True
    assert artifact["locked_primary_observation"]["ledger_gate_passed"] is False
    assert artifact["numerical_amendment"]["blind_preregistration"] is False


def test_artifact_input_and_output_hashes_match_local_files() -> None:
    artifact = _read(ARTIFACT)
    for block in ("preregistration", "numerical_amendment", "source_package", "core_dependency"):
        path = ROOT / artifact[block]["path"]
        assert path.is_file()
        assert artifact[block]["sha256"] == _sha256(path)
    timeseries = artifact["outputs"]["timeseries_csv"]
    assert timeseries["sha256"] == _sha256(ROOT / timeseries["path"])
    for figure in artifact["outputs"]["figures"]:
        assert figure["sha256"] == _sha256(ROOT / figure["path"])


def test_landauer_and_phi_claim_boundaries_are_explicit() -> None:
    artifact = _read(ARTIFACT)
    interpretation = " ".join(artifact["interpretation"])
    assert "not temperature or heat flux" in interpretation
    assert "Landauer" in interpretation
    assert "not used to derive beta" in interpretation
    assert "no backreaction" in artifact["controls"]["trace_only"]
