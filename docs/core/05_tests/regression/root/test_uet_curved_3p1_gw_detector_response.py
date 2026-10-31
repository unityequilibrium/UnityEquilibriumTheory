from __future__ import annotations

import json
import importlib
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_gw_response = importlib.import_module(
    "docs.core.02_equations.covariant.uet_curved_3p1_gw_detector_response"
)
SPEED_OF_LIGHT_M_S = _gw_response.SPEED_OF_LIGHT_M_S
equal_arm_interferometer_response = _gw_response.equal_arm_interferometer_response
equal_arm_round_trip_transfer = _gw_response.equal_arm_round_trip_transfer
project_spatial_metric_mode_to_tt = _gw_response.project_spatial_metric_mode_to_tt
spatial_metric_perturbation_from_gh_metric = (
    _gw_response.spatial_metric_perturbation_from_gh_metric
)


def test_gh_metric_to_tt_plus_mode_and_low_frequency_strain() -> None:
    amplitude = 2.5e-6
    metric = np.diag([-1.0, 1.0 + amplitude, 1.0 - amplitude, 1.0])
    spatial = spatial_metric_perturbation_from_gh_metric(metric)
    tt = project_spatial_metric_mode_to_tt(spatial, [0.0, 0.0, 1.0])
    result = equal_arm_interferometer_response(
        tt,
        [0.0, 0.0, 1.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        frequency_hz=0.0,
        arm_length_m=4000.0,
    )

    assert np.allclose(tt, np.diag([amplitude, -amplitude, 0.0]), atol=1e-15)
    assert result.strain_response == pytest.approx(amplitude)
    assert result.equivalent_differential_length_m == pytest.approx(4000.0 * amplitude)
    assert result.arm_u_transfer == pytest.approx(1.0)
    assert result.arm_v_transfer == pytest.approx(1.0)


def test_finite_frequency_response_matches_source_transfer_formula() -> None:
    amplitude = 0.7
    frequency = 37.0
    length = 4000.0
    q = np.pi * frequency * length / SPEED_OF_LIGHT_M_S
    expected_transfer = (np.sin(q) / q) * np.exp(-2j * q) * np.cos(q)
    tt = np.diag([amplitude, -amplitude, 0.0]).astype(complex)

    result = equal_arm_interferometer_response(
        tt,
        [0.0, 0.0, 1.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        frequency,
        length,
    )

    assert result.arm_u_transfer == pytest.approx(expected_transfer)
    assert result.arm_v_transfer == pytest.approx(expected_transfer)
    assert result.strain_response == pytest.approx(amplitude * expected_transfer)
    assert result.transfer_frequency_hz == pytest.approx(
        SPEED_OF_LIGHT_M_S / (2.0 * np.pi * length)
    )


def test_cross_polarization_rotated_arms_have_expected_response() -> None:
    amplitude = -0.3
    tt = np.array(
        [[0.0, amplitude, 0.0], [amplitude, 0.0, 0.0], [0.0, 0.0, 0.0]],
        dtype=complex,
    )
    arm_u = np.array([1.0, 1.0, 0.0]) / np.sqrt(2.0)
    arm_v = np.array([-1.0, 1.0, 0.0]) / np.sqrt(2.0)

    result = equal_arm_interferometer_response(
        tt, [0.0, 0.0, 1.0], arm_u, arm_v, 0.0, 10.0
    )

    assert result.strain_response == pytest.approx(amplitude)


def test_tt_projection_removes_a_plane_wave_spatial_gauge_mode() -> None:
    direction = np.array([0.0, 0.0, 1.0])
    gauge_vector = np.array([0.2, -0.7, 0.5])
    gauge_mode = np.outer(direction, gauge_vector) + np.outer(gauge_vector, direction)

    tt = project_spatial_metric_mode_to_tt(gauge_mode, direction)

    assert np.max(np.abs(tt)) < 1e-14


def test_response_is_rotation_covariant() -> None:
    angle_y, angle_z = 0.37, -0.81
    rotation_y = np.array(
        [
            [np.cos(angle_y), 0.0, np.sin(angle_y)],
            [0.0, 1.0, 0.0],
            [-np.sin(angle_y), 0.0, np.cos(angle_y)],
        ]
    )
    rotation_z = np.array(
        [
            [np.cos(angle_z), -np.sin(angle_z), 0.0],
            [np.sin(angle_z), np.cos(angle_z), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    rotation = rotation_z @ rotation_y
    direction = np.array([0.0, 0.0, 1.0])
    plus = np.diag([0.4, -0.4, 0.0]).astype(complex)
    arms = (np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]))
    baseline = equal_arm_interferometer_response(
        plus, direction, *arms, frequency_hz=83.0, arm_length_m=16.0
    )
    rotated = equal_arm_interferometer_response(
        rotation @ plus @ rotation.T,
        rotation @ direction,
        rotation @ arms[0],
        rotation @ arms[1],
        frequency_hz=83.0,
        arm_length_m=16.0,
    )

    assert rotated.strain_response == pytest.approx(baseline.strain_response)


def test_frequency_response_has_real_signal_conjugacy() -> None:
    direction = [0.0, 0.0, 1.0]
    arm = [1.0, 0.0, 0.0]
    positive = equal_arm_round_trip_transfer(91.0, 2500.0, arm, direction)
    negative = equal_arm_round_trip_transfer(-91.0, 2500.0, arm, direction)

    assert negative == pytest.approx(np.conjugate(positive))


def test_equal_length_equivalent_displacement_scales_linearly() -> None:
    tt = np.diag([0.1, -0.1, 0.0])
    short = equal_arm_interferometer_response(
        tt, [0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], 0.0, 2.0
    )
    long = equal_arm_interferometer_response(
        tt, [0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], 0.0, 5.0
    )

    assert short.strain_response == pytest.approx(long.strain_response)
    assert long.equivalent_differential_length_m == pytest.approx(
        2.5 * short.equivalent_differential_length_m
    )


@pytest.mark.parametrize(
    "arguments",
    [
        (0.0, 1.0, [2.0, 0.0, 0.0], [0.0, 0.0, 1.0]),
        (0.0, 1.0, [1.0, 0.0, 0.0], [0.0, 0.0, 2.0]),
        (float("nan"), 1.0, [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]),
    ],
)
def test_transfer_rejects_invalid_inputs(arguments: tuple[object, ...]) -> None:
    with pytest.raises(ValueError):
        equal_arm_round_trip_transfer(*arguments)


def test_projection_rejects_nonsymmetric_metric_mode() -> None:
    with pytest.raises(ValueError, match="symmetric"):
        project_spatial_metric_mode_to_tt(
            [[0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
            [0.0, 0.0, 1.0],
        )


def test_audit_artifact_is_source_hashed_and_keeps_lane_boundary() -> None:
    artifact_path = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_gw_detector_response_audit.json"
    source_record = ROOT / "docs/data/external/gr_3p1/gw_interferometer_response/source_record.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["status"] == "PASS_GH_LINEAR_GW_INTERFEROMETER_RESPONSE"
    assert all(artifact["checks"].values())
    assert artifact["source_hashes"][source_record.relative_to(ROOT).as_posix()]
    assert artifact["claim_promotion"] is False
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert "not a UET prediction" in artifact["major_result"]["claim_boundary"]


def test_core_parent_records_only_diagnostic_lane_and_keeps_global_blockers() -> None:
    from docs.scripts.audit.audit_uet_curved_3p1_constraints import build_artifacts

    _, _, gate, addendum = build_artifacts()
    requirements = gate["requirements"]
    assert requirements["linearized_gw_detector_response"] == "PASS_DIAGNOSTIC_ONLY"
    assert requirements["dimensional_observable_mapping"] == "OPEN"
    assert requirements["constraint_preserving_boundaries"] == "OPEN"
    assert gate["major_result"]["closure_level"] == "PARTIAL"
    assert gate["major_result"]["claim_boundary"].endswith("not Gravity/GR compatibility")
    entries = addendum["equation_entries"]
    assert any(
        entry["equation_id"]
        == "uet.main_theory.curved_3p1.linear_gw_detector_response"
        for entry in entries
    )

    closure_register = json.loads(
        (ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json").read_text(
            encoding="utf-8"
        )
    )
    dependency_gate = json.loads(
        (ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json").read_text(
            encoding="utf-8"
        )
    )
    lane = next(
        entry
        for entry in closure_register["entries"]
        if entry.get("major_result_id")
        == "CORE_CURVED_3P1_GW_DETECTOR_RESPONSE_LANE"
    )
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["claim_promotion"] is False
    assert "CORE_CURVED_3P1_GW_DETECTOR_RESPONSE_LANE" not in dependency_gate[
        "unlock_order"
    ]
    assert dependency_gate["curved_3p1_progress"][
        "linearized_gw_detector_response_lane"
    ]["closure_level"] == "CLOSED_FOR_LANE"
    assert dependency_gate["decisions"]["GR_CLASSICAL_COMPATIBILITY_LANE"][
        "status"
    ] == "BLOCKED_DEPENDENCY"
