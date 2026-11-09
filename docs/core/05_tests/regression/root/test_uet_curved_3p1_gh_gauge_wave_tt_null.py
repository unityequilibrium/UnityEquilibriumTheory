from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_gh_evolution = importlib.import_module(
    "docs.core.02_equations.covariant.uet_curved_3p1_gh_evolution"
)
_gw_response = importlib.import_module(
    "docs.core.02_equations.covariant.uet_curved_3p1_gw_detector_response"
)

AUDIT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_gauge_wave_tt_null_audit.json"


def test_evolved_harmonic_gauge_wave_has_nonzero_metric_but_null_tt_signal() -> None:
    initial, source, source_derivative, spacing = _gh_evolution.harmonic_gauge_wave_state(
        (12, 5, 5), (1.0, 1.0, 1.0), amplitude=0.05
    )
    evolved = _gh_evolution.evolve_periodic_vacuum_gh(
        initial, source, source_derivative, spacing, 0.02
    )
    spatial_mode = evolved.state.spacetime_metric[..., 1:, 1:] - np.eye(3)
    propagation = [1.0, 0.0, 0.0]
    tt_modes = [
        _gw_response.project_spatial_metric_mode_to_tt(mode, propagation)
        for mode in spatial_mode.reshape((-1, 3, 3))
    ]
    strains = [
        _gw_response.equal_arm_interferometer_response(
            mode,
            propagation,
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            frequency_hz=0.0,
            arm_length_m=1.0,
        ).strain_response
        for mode in tt_modes
    ]

    assert float(np.max(np.abs(spatial_mode))) > 0.01
    assert float(np.max(np.abs(tt_modes))) == 0.0
    assert float(np.max(np.abs(strains))) == 0.0
    assert evolved.run_contract["constraint_projection"] is False
    assert evolved.run_contract["numerical_filtering"] is False


def test_audit_registers_the_null_control_without_claim_promotion() -> None:
    artifact = json.loads(AUDIT.read_text(encoding="utf-8"))

    assert artifact["status"] == "PASS_GH_HARMONIC_GAUGE_WAVE_TT_NULL_CONTROL"
    assert all(artifact["checks"].values())
    assert artifact["major_result"]["major_result_id"] == (
        "CORE_CURVED_3P1_GH_GAUGE_WAVE_TT_NULL_CONTROL"
    )
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["claim_promotion"] is False
    assert artifact["major_result"]["dependency_unlocked"] == (
        "none; this is a gauge-false-positive exclusion control only"
    )
    assert artifact["gh_time_series_output"]["metric_snapshot_history_available"] is False


def test_core_parent_registers_null_control_but_keeps_general_gates_open() -> None:
    from docs.scripts.audit.audit_uet_curved_3p1_constraints import build_artifacts

    _, _, gate, _ = build_artifacts()

    assert gate["requirements"]["gh_gauge_wave_tt_null_control"] == (
        "PASS_DIAGNOSTIC_ONLY"
    )
    assert gate["requirements"]["dimensional_observable_mapping"] == "OPEN"
    assert gate["requirements"]["constraint_preserving_boundaries"] == "OPEN"
    assert gate["major_result"]["closure_level"] == "PARTIAL"
