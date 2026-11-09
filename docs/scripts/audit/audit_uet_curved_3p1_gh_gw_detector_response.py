"""Verify the bounded linearized GH metric-to-interferometer response lane."""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import canonical_artifact_path
_gw_response = importlib.import_module(
    "docs.core.02_equations.covariant.uet_curved_3p1_gw_detector_response"
)
SPEED_OF_LIGHT_M_S = _gw_response.SPEED_OF_LIGHT_M_S
equal_arm_interferometer_response = _gw_response.equal_arm_interferometer_response
equal_arm_round_trip_transfer = _gw_response.equal_arm_round_trip_transfer
gw_detector_response_contract = _gw_response.gw_detector_response_contract
project_spatial_metric_mode_to_tt = _gw_response.project_spatial_metric_mode_to_tt
spatial_metric_perturbation_from_gh_metric = (
    _gw_response.spatial_metric_perturbation_from_gh_metric
)


SOURCE_RECORD = ROOT / "docs/data/external/gr_3p1/gw_interferometer_response/source_record.json"
MODULE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gw_detector_response.py"
TEST = ROOT / "docs/core/05_tests/regression/root/test_uet_curved_3p1_gw_detector_response.py"
AUDIT = canonical_artifact_path(
    "curved_3p1_gh_gw_detector_response_audit.json", "verification"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifact() -> dict:
    tolerance = 1e-12
    direction = np.array([0.0, 0.0, 1.0])
    plus_amplitude = 2.5e-6
    gh_metric = np.diag([-1.0, 1.0 + plus_amplitude, 1.0 - plus_amplitude, 1.0])
    spatial_mode = spatial_metric_perturbation_from_gh_metric(gh_metric)
    plus_tt = project_spatial_metric_mode_to_tt(spatial_mode, direction)
    low_frequency = equal_arm_interferometer_response(
        plus_tt,
        direction,
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        frequency_hz=0.0,
        arm_length_m=4000.0,
    )

    frequency = 37.0
    arm_length = 4000.0
    q = np.pi * frequency * arm_length / SPEED_OF_LIGHT_M_S
    finite_expected = (np.sin(q) / q) * np.exp(-2j * q) * np.cos(q)
    finite_result = equal_arm_interferometer_response(
        np.diag([plus_amplitude, -plus_amplitude, 0.0]),
        direction,
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        frequency,
        arm_length,
    )

    cross_amplitude = -0.3
    cross_tt = np.array(
        [[0.0, cross_amplitude, 0.0], [cross_amplitude, 0.0, 0.0], [0.0, 0.0, 0.0]]
    )
    arm_u = np.array([1.0, 1.0, 0.0]) / np.sqrt(2.0)
    arm_v = np.array([-1.0, 1.0, 0.0]) / np.sqrt(2.0)
    cross_result = equal_arm_interferometer_response(
        cross_tt, direction, arm_u, arm_v, 0.0, 1.0
    )

    gauge_vector = np.array([0.2, -0.7, 0.5])
    gauge_mode = np.outer(direction, gauge_vector) + np.outer(gauge_vector, direction)
    gauge_tt = project_spatial_metric_mode_to_tt(gauge_mode, direction)

    ay, az = 0.37, -0.81
    rotation_y = np.array(
        [[np.cos(ay), 0.0, np.sin(ay)], [0.0, 1.0, 0.0], [-np.sin(ay), 0.0, np.cos(ay)]]
    )
    rotation_z = np.array(
        [[np.cos(az), -np.sin(az), 0.0], [np.sin(az), np.cos(az), 0.0], [0.0, 0.0, 1.0]]
    )
    rotation = rotation_z @ rotation_y
    rotated_result = equal_arm_interferometer_response(
        rotation @ plus_tt @ rotation.T,
        rotation @ direction,
        rotation @ np.array([1.0, 0.0, 0.0]),
        rotation @ np.array([0.0, 1.0, 0.0]),
        frequency,
        arm_length,
    )

    positive_transfer = equal_arm_round_trip_transfer(
        91.0, 2500.0, [1.0, 0.0, 0.0], direction
    )
    negative_transfer = equal_arm_round_trip_transfer(
        -91.0, 2500.0, [1.0, 0.0, 0.0], direction
    )

    source_paths = (SOURCE_RECORD, MODULE, TEST)
    checks = {
        "gh_spatial_metric_extracts_dimensionless_mode": np.max(
            np.abs(spatial_mode - np.diag([plus_amplitude, -plus_amplitude, 0.0]))
        )
        <= tolerance,
        "tt_projection_is_transverse_and_tracefree": (
            np.max(np.abs(direction @ plus_tt)) <= tolerance
            and abs(np.trace(plus_tt)) <= tolerance
        ),
        "low_frequency_plus_response_matches_analytic_strain": abs(
            low_frequency.strain_response - plus_amplitude
        )
        <= tolerance,
        "finite_frequency_transfer_matches_closed_form_control": abs(
            finite_result.strain_response - plus_amplitude * finite_expected
        )
        <= tolerance,
        "cross_polarization_matches_rotated_arm_control": abs(
            cross_result.strain_response - cross_amplitude
        )
        <= tolerance,
        "plane_wave_spatial_gauge_mode_is_removed_by_tt_projection": np.max(
            np.abs(gauge_tt)
        )
        <= tolerance,
        "detector_response_is_rotation_covariant": abs(
            rotated_result.strain_response - finite_result.strain_response
        )
        <= tolerance,
        "negative_frequency_transfer_is_complex_conjugate": abs(
            negative_transfer - np.conjugate(positive_transfer)
        )
        <= tolerance,
        "equivalent_length_scales_with_si_arm_length": abs(
            low_frequency.equivalent_differential_length_m
            - 4000.0 * low_frequency.strain_response
        )
        <= tolerance,
        "source_record_and_code_hashes_are_available": all(
            path.is_file() for path in source_paths
        ),
    }
    checks = {key: bool(value) for key, value in checks.items()}

    source_hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in source_paths
    }
    contract = gw_detector_response_contract()
    result = {
        "schema_version": "uet-curved-3p1-gw-detector-response-v1",
        "diagnostic_id": "uet.main_theory.curved_3p1.linear_gw_detector_response",
        "artifact": "curved_3p1_gh_gw_detector_response_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": (
            "PASS_GH_LINEAR_GW_INTERFEROMETER_RESPONSE"
            if all(checks.values())
            else "FAIL_GH_LINEAR_GW_INTERFEROMETER_RESPONSE"
        ),
        "claim_promotion": False,
        "checks": checks,
        "metrics": {
            "tt_trace_abs": float(abs(np.trace(plus_tt))),
            "tt_transverse_linf": float(np.max(np.abs(direction @ plus_tt))),
            "low_frequency_strain": [
                float(low_frequency.strain_response.real),
                float(low_frequency.strain_response.imag),
            ],
            "finite_frequency_strain": [
                float(finite_result.strain_response.real),
                float(finite_result.strain_response.imag),
            ],
            "finite_frequency_expected": [
                float((plus_amplitude * finite_expected).real),
                float((plus_amplitude * finite_expected).imag),
            ],
            "transfer_frequency_hz_for_4000m": float(
                low_frequency.transfer_frequency_hz
            ),
            "maximum_rotation_response_difference": float(
                abs(rotated_result.strain_response - finite_result.strain_response)
            ),
        },
        "equation_or_mapping": contract["equations"],
        "units": contract["units"],
        "assumptions": contract["assumptions"],
        "excluded": contract["excluded"],
        "constant_origin": contract["constant_origin"],
        "input_identity": {
            "source_record_path": SOURCE_RECORD.relative_to(ROOT).as_posix(),
            "source_record_sha256": source_hashes[SOURCE_RECORD.relative_to(ROOT).as_posix()],
            "data_rows_consumed": 0,
            "detector_data_consumed": False,
            "holdout_consumed": False,
        },
        "source_hashes": source_hashes,
        "literature_basis": [
            {
                "source": "Liang et al. (2019), Phys. Rev. D 99, 104027",
                "url": "https://arxiv.org/abs/1901.09624",
                "locators": "Eqs. (2)-(6), Sec. II.3",
                "used_for": "TT polarization tensors, equal-arm frequency response, and low-frequency limit",
            },
            {
                "source": "BIPM SI definition of the metre",
                "url": "https://www.bipm.org/en/si-base-units/metre",
                "locator": "fixed exact value of c in m s^-1",
                "used_for": "exact SI conversion constant c=299792458 m s^-1",
            },
        ],
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GW_DETECTOR_RESPONSE_LANE",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
            "what_is_closed": [
                "spatial metric perturbation to plane-wave TT projection in the declared flat wave-zone lane",
                "source-matched finite-frequency equal-arm interferometer response without optical cavities",
                "SI frequency, arm-length, exact-c, dimensionless strain, and equivalent-length contract",
                "analytic plus/cross, pure-gauge, rotational-covariance, and frequency-conjugacy controls",
            ],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": "standard-GR detector response formula with analytic tensor projection and internal controls",
            "observable": "ideal equal-arm interferometer frequency-domain strain response to one TT plane-wave mode",
            "data_role": "synthetic analytic control only; no detector data or parameter fit",
            "verification_status": (
                "PASS_GH_LINEAR_GW_INTERFEROMETER_RESPONSE"
                if all(checks.values())
                else "FAIL_GH_LINEAR_GW_INTERFEROMETER_RESPONSE"
            ),
            "open_blockers": [
                "GH evolution wave-zone extraction and temporal Fourier map not integrated",
                "detector calibration, optical cavities/control loops, noise, and uncertainty package absent",
                "non-periodic CPBC evolution and nonlinear/strong-field mapping remain open",
            ],
            "dependency_unlocked": "bounded linearized TT-mode observable mapping only; Core parent and Gravity remain blocked",
            "claim_boundary": contract["claim_boundary"],
        },
        "claim_boundary": contract["claim_boundary"],
    }
    return result


def main() -> int:
    artifact = build_artifact()
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"status": artifact["status"], "checks": artifact["checks"]}, indent=2))
    return 0 if artifact["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
