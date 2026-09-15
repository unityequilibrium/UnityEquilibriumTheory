"""Tests for the explicit thermal dimensional calibration contract."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
from pathlib import Path

from docs.core.thermal_source_observable_map import (
    ThermalPhiCalibration,
    quasi_temperature_difference_from_calibration,
)


ROOT = (repo_root() / "docs")
SCRIPT = ROOT / "scripts/audit/audit_thermal_dimensional_calibration.py"


def load_module():
    spec = importlib.util.spec_from_file_location("thermal_dimensional_calibration", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load thermal calibration audit: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def open_record() -> ThermalPhiCalibration:
    return ThermalPhiCalibration(
        temperature_scale_K_per_phi=None,
        uncertainty_K_per_phi=None,
        source_id="open:test",
        source_locator="not-yet-sourced",
        source_hash="NOT_AVAILABLE",
    )


def test_open_calibration_is_valid_but_cannot_emit_kelvin():
    record = open_record()
    record.validate()
    assert not record.physical_mapping_ready()
    assert quasi_temperature_difference_from_calibration(0.25, -0.25, record) is None


def test_fitted_independent_calibration_is_rejected():
    record = ThermalPhiCalibration(
        temperature_scale_K_per_phi=4.0,
        uncertainty_K_per_phi=0.2,
        source_id="synthetic:fitted",
        source_locator="synthetic://fitted",
        source_hash="synthetic-fitted",
        status="INDEPENDENTLY_CALIBRATED",
        fitted=True,
    )
    try:
        record.validate()
    except ValueError:
        return
    raise AssertionError("fitted independent calibration must be rejected")


def test_calibration_contract_artifact_stays_blocked():
    artifact = load_module().build_artifact()
    assert artifact["audit_status"] == "PASS_WITH_BLOCKED_INDEPENDENT_CALIBRATION"
    assert artifact["claim_status"] == "CONTRACT_DEFINED_CALIBRATION_OPEN"
    assert artifact["gates"]["fitted_calibration_is_rejected"]
    assert artifact["gates"]["normalized_observable_is_scale_invariant"]
    assert artifact["gates"]["absolute_scale_and_calibration_are_degenerate"]
    assert artifact["gates"]["identifiability_blocker_is_explicit"]
    assert artifact["structural_identifiability"]["status"] == "NON_IDENTIFIABLE_FROM_NORMALIZED_PHI"
    assert artifact["gates"]["dimensional_map_remains_blocked"]
