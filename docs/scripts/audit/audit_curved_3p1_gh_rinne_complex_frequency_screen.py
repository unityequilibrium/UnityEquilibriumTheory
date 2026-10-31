from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
JOINT_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_joint_real_kreiss_operator.py"
JOINT_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_joint_real_kreiss_operator.json"
NEGATIVE_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_negative_shift_kreiss_symbol.py"
NEGATIVE_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_negative_shift_kreiss_symbol.json"
JORDAN_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_jordan_normalization.py"
JORDAN_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_jordan_normalization.json"
NORM_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_norm_interface.py"
NORM_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_norm_interface.json"
RATIO_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_compactified_ratio_screen.py"
RATIO_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_compactified_ratio_screen.json"
BOUNDARY_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py"
PROJECTOR_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py"
HIGH_ENDPOINT_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_high_frequency_transfer_endpoint.py"
HIGH_ENDPOINT_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_high_frequency_transfer_endpoint.json"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_complex_frequency_screen.json"

BETA_VALUES = (-0.1, -0.5, -0.9)
HIGH_RADII = (1.0e3, 1.0e5, 1.0e7)
HIGH_ANGLES = (0.0, np.pi / 4.0, -np.pi / 4.0, np.pi / 2.0 - 1.0e-3, -np.pi / 2.0 + 1.0e-3)
HIGH_SWEEP_BETA_VALUES = (-0.01, -0.03, -0.1, -0.2, -0.35, -0.5, -0.65, -0.8, -0.9, -0.95, -0.98, -0.99)
HIGH_SWEEP_RADII = (1.0e3, 1.0e5)
HIGH_SWEEP_NORM_ERROR_LIMIT = 2.0e-9
LOW_RADII = (1.0e-4, 1.0e-6, 1.0e-8, 1.0e-10)
DIRECTIONS = (0.0, np.pi / 4.0, -np.pi / 4.0, np.pi / 2.0 - 1.0e-3, -np.pi / 2.0 + 1.0e-3)
GLANCING_OFFSETS = (1.0e-2, 1.0e-4, 1.0e-6, 1.0e-8, 1.0e-10)
JORDAN_OFFSETS = (1.0e-2, 1.0e-4, 1.0e-6, 1.0e-8)
MODE_RESIDUAL_LIMIT = 1.0e-7
DETERMINANT_LOG_LIMIT = 1.0e-6


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


JOINT = _load("_uet_rinne_complex_joint_operator", JOINT_SCRIPT)
NEGATIVE = JOINT.NEGATIVE
ROW, COLUMN, _ = NEGATIVE._source_transforms()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _state_operator(boundary: np.ndarray, state: np.ndarray) -> np.ndarray:
    return np.linalg.solve(boundary.T, state.T).T


def _eq123_log_abs(zeta: complex, beta: float) -> float:
    _, lambda1, _ = NEGATIVE._root_and_lambdas(zeta, beta)
    k1 = float(np.linalg.norm([zeta - beta * lambda1, -lambda1, -1.0j, 0.0j]))
    k2 = float(np.linalg.norm([0.0j, -1.0j * beta, zeta, 0.0j]))
    factor = zeta - (1.0 + beta) * lambda1
    speed_factor = zeta * zeta - beta * beta
    return float(
        16.0 * np.log(abs(factor))
        + 10.0 * np.log(abs(speed_factor))
        - np.log(8.0)
        - 16.0 * np.log(abs(zeta))
        - 20.0 * np.log(abs(beta))
        - 10.0 * np.log(k1)
        - 10.0 * np.log(k2)
    )


def _generic_transfer(
    zeta: complex, beta: float, confluent: bool = False
) -> tuple[np.ndarray, float, float | None]:
    if confluent:
        _, lambda1, lambda2 = NEGATIVE._root_and_lambdas(zeta, beta)
        gap = lambda2 - lambda1
        boundary_groups: list[list[np.ndarray]] = [[], [], []]
        state_groups: list[list[np.ndarray]] = [[], [], []]
        maximum_residual = 0.0
        for component in range(10):
            mode_boundary: list[np.ndarray] = []
            mode_state: list[np.ndarray] = []
            for family in range(3):
                value, derivative = NEGATIVE._generic_mode(zeta, beta, family)
                boundary, residual, _ = NEGATIVE._boundary_column(
                    beta, zeta, value, derivative, component
                )
                mode_boundary.append(boundary)
                mode_state.append(JOINT._state_column(value, component))
                maximum_residual = max(maximum_residual, residual)
            boundary_groups[0].append((-1.0j * mode_boundary[1] - mode_boundary[0]) / gap)
            boundary_groups[1].append(mode_boundary[0])
            boundary_groups[2].append(mode_boundary[2])
            state_groups[0].append((-1.0j * mode_state[1] - mode_state[0]) / gap)
            state_groups[1].append(mode_state[0])
            state_groups[2].append(mode_state[2])
        boundary = ROW @ np.column_stack(sum(boundary_groups, [])) @ COLUMN
        state = np.column_stack(sum(state_groups, [])) @ COLUMN
    else:
        boundary_columns: list[np.ndarray] = []
        state_columns: list[np.ndarray] = []
        maximum_residual = 0.0
        for family in range(3):
            value, derivative = NEGATIVE._generic_mode(zeta, beta, family)
            for component in range(10):
                boundary, residual, _ = NEGATIVE._boundary_column(
                    beta, zeta, value, derivative, component
                )
                boundary_columns.append(boundary)
                state_columns.append(JOINT._state_column(value, component))
                maximum_residual = max(maximum_residual, residual)
        boundary = ROW @ np.column_stack(boundary_columns) @ COLUMN
        state = np.column_stack(state_columns) @ COLUMN

    transfer = _state_operator(boundary, state)
    sign, actual_logdet = np.linalg.slogdet(boundary)
    if confluent or sign == 0.0:
        determinant_error = None
    else:
        determinant_error = abs(float(actual_logdet) - _eq123_log_abs(zeta, beta))
    return transfer, maximum_residual, determinant_error


def _record(zeta: complex, beta: float, region: str, extra: dict[str, Any]) -> dict[str, Any]:
    transfer, residual, determinant_error = _generic_transfer(zeta, beta)
    return {
        "region": region,
        "beta": beta,
        "zeta_real": float(zeta.real),
        "zeta_imag": float(zeta.imag),
        "state_operator_shape": list(transfer.shape),
        "state_operator_norm_2": float(np.linalg.svd(transfer, compute_uv=False)[0]),
        "principal_mode_residual": residual,
        "source_eq123_log_abs_determinant_error": determinant_error,
        "all_operator_entries_finite": bool(np.all(np.isfinite(transfer))),
        **extra,
    }


def _endpoint_determinants(beta: float) -> dict[str, float]:
    a = float(np.sqrt(1.0 - beta * beta))
    return {
        "glancing_abs_det_limit": a**10 / (256.0 * abs(beta) ** 20 * (1.0 - beta) ** 16),
        "high_frequency_abs_det_limit": 256.0 / (abs(beta) ** 20 * (1.0 - beta) ** 6),
        "corrected_jordan_abs_det": 4.0 / (abs(beta) ** 26 * (1.0 + beta * beta) ** 5),
    }


def build_artifact() -> dict[str, Any]:
    high_endpoint_artifact = json.loads(HIGH_ENDPOINT_ARTIFACT.read_text(encoding="utf-8"))
    low_frequency: list[dict[str, Any]] = []
    glancing: list[dict[str, Any]] = []
    high_frequency: list[dict[str, Any]] = []
    high_frequency_parameter_sweep: list[dict[str, Any]] = []
    for beta in BETA_VALUES:
        for radius in LOW_RADII:
            for angle in DIRECTIONS:
                zeta = radius * np.exp(1.0j * angle)
                low_frequency.append(
                    _record(zeta, beta, "zeta_to_zero", {"radius": radius, "angle": float(angle)})
                )
        a = float(np.sqrt(1.0 - beta * beta))
        for offset in GLANCING_OFFSETS:
            for sign in (-1, 1):
                zeta = complex(offset, sign * a)
                glancing.append(
                    _record(
                        zeta,
                        beta,
                        "glancing_approach",
                        {"real_offset": offset, "glancing_sign": sign},
                    )
                )
        for radius in HIGH_RADII:
            for angle in HIGH_ANGLES:
                zeta = radius * np.exp(1.0j * angle)
                high_frequency.append(
                    _record(
                        zeta,
                        beta,
                        "high_frequency",
                        {
                            "radius": radius,
                            "angle": float(angle),
                            "asymptotic_norm_candidate": 1.0 - beta,
                        },
                    )
                )
    for beta in HIGH_SWEEP_BETA_VALUES:
        for radius in HIGH_SWEEP_RADII:
            for angle in HIGH_ANGLES:
                zeta = radius * np.exp(1.0j * angle)
                high_frequency_parameter_sweep.append(
                    _record(
                        zeta,
                        beta,
                        "high_frequency_parameter_sweep",
                        {
                            "radius": radius,
                            "angle": float(angle),
                            "asymptotic_norm_candidate": 1.0 - beta,
                        },
                    )
                )

    jordan_beta = -0.5
    jordan_zeta = -jordan_beta
    jordan_boundary, jordan_state, jordan_residual = JOINT._jordan_matrices(jordan_zeta)
    jordan_transfer = _state_operator(jordan_boundary, jordan_state)
    jordan_sign, jordan_logdet = np.linalg.slogdet(jordan_boundary)
    jordan_expected_logdet = float(
        np.log(4.0)
        - 26.0 * np.log(abs(jordan_beta))
        - 5.0 * np.log(1.0 + jordan_beta * jordan_beta)
    )
    jordan_reference_norm = float(np.linalg.svd(jordan_transfer, compute_uv=False)[0])
    jordan_approach: list[dict[str, Any]] = []
    for offset in JORDAN_OFFSETS:
        for angle in DIRECTIONS:
            zeta = jordan_zeta + offset * np.exp(1.0j * angle)
            transfer, residual, _ = _generic_transfer(zeta, jordan_beta, confluent=True)
            jordan_approach.append(
                {
                    "offset": offset,
                    "angle": float(angle),
                    "state_operator_norm_2": float(np.linalg.svd(transfer, compute_uv=False)[0]),
                    "frobenius_distance_to_corrected_jordan_operator": float(
                        np.linalg.norm(transfer - jordan_transfer, ord="fro")
                    ),
                    "principal_mode_residual": residual,
                    "all_operator_entries_finite": bool(np.all(np.isfinite(transfer))),
                }
            )

    zero_direction_spreads = []
    for beta in BETA_VALUES:
        rows = [
            row for row in low_frequency
            if row["beta"] == beta and row["radius"] == min(LOW_RADII)
        ]
        norms = [row["state_operator_norm_2"] for row in rows]
        zero_direction_spreads.append(
            {
                "beta": beta,
                "radius": min(LOW_RADII),
                "norm_min": min(norms),
                "norm_max": max(norms),
                "relative_spread": (max(norms) - min(norms)) / max(norms),
            }
        )

    glancing_sign_spreads = []
    for beta in BETA_VALUES:
        for offset in GLANCING_OFFSETS:
            rows = [
                row for row in glancing
                if row["beta"] == beta and row["real_offset"] == offset
            ]
            norms = [row["state_operator_norm_2"] for row in rows]
            glancing_sign_spreads.append(
                {
                    "beta": beta,
                    "real_offset": offset,
                    "relative_sign_spread": (max(norms) - min(norms)) / max(norms),
                }
            )

    glancing_limit_log_offsets = []
    for beta in BETA_VALUES:
        exact_limit = _endpoint_determinants(beta)["glancing_abs_det_limit"]
        a = float(np.sqrt(1.0 - beta * beta))
        for offset in GLANCING_OFFSETS:
            for sign in (-1, 1):
                zeta = complex(offset, sign * a)
                glancing_limit_log_offsets.append(
                    {
                        "beta": beta,
                        "offset": offset,
                        "sign": sign,
                        "abs_log_difference": abs(_eq123_log_abs(zeta, beta) - np.log(exact_limit)),
                    }
                )

    high_frequency_errors = []
    high_frequency_parameter_sweep_errors = []
    high_frequency_determinant_offsets = []
    for beta in BETA_VALUES:
        exact_limit_logdet = float(np.log(_endpoint_determinants(beta)["high_frequency_abs_det_limit"]))
        for radius in HIGH_RADII:
            rows = [
                row for row in high_frequency
                if row["beta"] == beta and row["radius"] == radius
            ]
            high_frequency_errors.append(
                {
                    "beta": beta,
                    "radius": radius,
                    "maximum_abs_norm_error_to_candidate": max(
                        abs(row["state_operator_norm_2"] - (1.0 - beta)) for row in rows
                    ),
                }
            )
            for angle in HIGH_ANGLES:
                zeta = radius * np.exp(1.0j * angle)
                high_frequency_determinant_offsets.append(
                    {
                        "beta": beta,
                        "radius": radius,
                        "angle": float(angle),
                        "abs_log_difference": abs(_eq123_log_abs(zeta, beta) - exact_limit_logdet),
                    }
                )

    for beta in HIGH_SWEEP_BETA_VALUES:
        for radius in HIGH_SWEEP_RADII:
            rows = [
                row for row in high_frequency_parameter_sweep
                if row["beta"] == beta and row["radius"] == radius
            ]
            norms = [row["state_operator_norm_2"] for row in rows]
            high_frequency_parameter_sweep_errors.append(
                {
                    "beta": beta,
                    "radius": radius,
                    "case_count": len(rows),
                    "maximum_abs_norm_error_to_candidate": max(
                        abs(value - (1.0 - beta)) for value in norms
                    ),
                    "angular_norm_spread": max(norms) - min(norms),
                }
            )

    jordan_error_by_offset = []
    for offset in JORDAN_OFFSETS:
        rows = [row for row in jordan_approach if row["offset"] == offset]
        jordan_error_by_offset.append(
            {
                "offset": offset,
                "case_count": len(rows),
                "maximum_frobenius_distance": max(
                    row["frobenius_distance_to_corrected_jordan_operator"] for row in rows
                ),
                "maximum_operator_norm": max(row["state_operator_norm_2"] for row in rows),
            }
        )

    endpoint_values = {str(beta): _endpoint_determinants(beta) for beta in BETA_VALUES}
    generic_rows = low_frequency + glancing + high_frequency + high_frequency_parameter_sweep
    determinant_errors = [
        row["source_eq123_log_abs_determinant_error"]
        for row in generic_rows
        if row["source_eq123_log_abs_determinant_error"] is not None
    ]
    maximum_mode_residual = max(
        [row["principal_mode_residual"] for row in generic_rows + jordan_approach]
        + [jordan_residual]
    )
    maximum_determinant_log_error = max(determinant_errors)
    high_last_radius_errors = [
        row["maximum_abs_norm_error_to_candidate"]
        for row in high_frequency_errors
        if row["radius"] == max(HIGH_RADII)
    ]
    high_last_radius_det_offsets = [
        row["abs_log_difference"]
        for row in high_frequency_determinant_offsets
        if row["radius"] == max(HIGH_RADII)
    ]
    high_sweep_last_radius_errors = [
        row["maximum_abs_norm_error_to_candidate"]
        for row in high_frequency_parameter_sweep_errors
        if row["radius"] == max(HIGH_SWEEP_RADII)
    ]
    high_sweep_angular_spreads = [
        row["angular_norm_spread"]
        for row in high_frequency_parameter_sweep_errors
        if row["radius"] == max(HIGH_SWEEP_RADII)
    ]
    checks = {
        "all_screen_operators_are_finite_40_by_30": all(
            row["all_operator_entries_finite"] and row["state_operator_shape"] == [40, 30]
            for row in generic_rows
        ) and all(row["all_operator_entries_finite"] for row in jordan_approach),
        "principal_mode_residuals_below_limit": maximum_mode_residual < MODE_RESIDUAL_LIMIT,
        "generic_source_determinants_match_eq123": maximum_determinant_log_error < DETERMINANT_LOG_LIMIT,
        "zeta_to_zero_operator_norm_is_directionally_stable_on_screen": max(
            row["relative_spread"] for row in zero_direction_spreads
        ) < 5.0e-8,
        "glancing_plus_minus_approaches_agree_on_screen": max(
            row["relative_sign_spread"] for row in glancing_sign_spreads
        ) < 1.0e-10,
        "complex_jordan_chart_converges_to_corrected_chain": all(
            right["maximum_frobenius_distance"] < left["maximum_frobenius_distance"]
            for left, right in zip(jordan_error_by_offset, jordan_error_by_offset[1:])
        ) and jordan_error_by_offset[-1]["maximum_frobenius_distance"] < 1.0e-6,
        "high_frequency_norms_converge_to_numeric_candidate": all(
            right["maximum_abs_norm_error_to_candidate"]
            < left["maximum_abs_norm_error_to_candidate"]
            for beta in BETA_VALUES
            for left, right in zip(
                [row for row in high_frequency_errors if row["beta"] == beta],
                [row for row in high_frequency_errors if row["beta"] == beta][1:],
            )
        ) and max(high_last_radius_errors) < 1.0e-10,
        "expanded_high_frequency_beta_grid_converges_to_candidate": all(
            finer["maximum_abs_norm_error_to_candidate"]
            < coarser["maximum_abs_norm_error_to_candidate"]
            for beta in HIGH_SWEEP_BETA_VALUES
            for coarser, finer in zip(
                [
                    row for row in high_frequency_parameter_sweep_errors
                    if row["beta"] == beta
                ],
                [
                    row for row in high_frequency_parameter_sweep_errors
                    if row["beta"] == beta
                ][1:],
            )
        ) and len(high_frequency_parameter_sweep) == (
            len(HIGH_SWEEP_BETA_VALUES) * len(HIGH_SWEEP_RADII) * len(HIGH_ANGLES)
        ) and max(high_sweep_last_radius_errors) < HIGH_SWEEP_NORM_ERROR_LIMIT
        and max(high_sweep_angular_spreads) < HIGH_SWEEP_NORM_ERROR_LIMIT,
        "analytic_endpoint_determinants_are_positive": all(
            value > 0.0 and np.isfinite(value)
            for limits in endpoint_values.values()
            for value in limits.values()
        ),
        "corrected_exact_jordan_determinant_matches_matrix": jordan_sign != 0.0
        and abs(float(jordan_logdet) - jordan_expected_logdet) < 1.0e-8,
        "glancing_determinant_limit_is_approached_monotonically": all(
            right < left
            for beta in BETA_VALUES
            for left, right in zip(
                [
                    max(
                        row["abs_log_difference"]
                        for row in glancing_limit_log_offsets
                        if row["beta"] == beta and row["offset"] == offset
                    )
                    for offset in GLANCING_OFFSETS
                ],
                [
                    max(
                        row["abs_log_difference"]
                        for row in glancing_limit_log_offsets
                        if row["beta"] == beta and row["offset"] == offset
                    )
                    for offset in GLANCING_OFFSETS
                ][1:],
            )
        ) and max(
            row["abs_log_difference"]
            for row in glancing_limit_log_offsets
            if row["offset"] == min(GLANCING_OFFSETS)
        ) < 5.0e-4,
        "high_frequency_determinant_limit_matches_eq123_screen": max(
            high_last_radius_det_offsets
        ) < 1.0e-5,
        "exact_high_frequency_endpoint_artifact_is_current_and_lane_closed": (
            high_endpoint_artifact["major_result_id"]
            == "CORE_CURVED_3P1_GH_RINNE_HIGH_FREQUENCY_TRANSFER_MATRIX_ENDPOINT"
            and high_endpoint_artifact["closure_level"] == "CLOSED_FOR_LANE"
            and high_endpoint_artifact["STATUS"]
            == "PASS_EXACT_HIGH_FREQUENCY_TRANSFER_MATRIX_ENDPOINT"
            and high_endpoint_artifact["VERIFICATION"]["source_hashes"].get(
                _relative(Path(__file__))
            )
            == _sha256(Path(__file__))
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    status = (
        "PASS_COMPLEX_FREQUENCY_ENDPOINT_SCREEN"
        if all(checks.values())
        else "FAIL_OR_UNRESOLVED_COMPLEX_FREQUENCY_SCREEN"
    )
    blocker = "zero_frequency_transfer_extension_and_compactified_continuous_transfer_bound_unproved"
    claim_boundary = (
        "Source-matched frozen-coefficient standard-GR negative-normal-shift diagnostic: analytic determinant-factor analysis, an exact high-frequency endpoint-matrix construction, and finite complex-frequency screens at three base beta values plus an exploratory 12-value high-frequency beta grid. "
        "It is not a continuous all-frequency Kreiss operator-norm proof, a uniform-in-beta bound, a variable-coefficient/nonlinear GH IBVP result, or Core-parent closure."
    )
    source_paths = (
        Path(__file__), JOINT_SCRIPT, JOINT_ARTIFACT, NEGATIVE_SCRIPT, NEGATIVE_ARTIFACT,
        JORDAN_SCRIPT, JORDAN_ARTIFACT, NORM_SCRIPT, NORM_ARTIFACT, RATIO_SCRIPT,
        RATIO_ARTIFACT, BOUNDARY_SOURCE, PROJECTOR_SOURCE, HIGH_ENDPOINT_SCRIPT,
        HIGH_ENDPOINT_ARTIFACT,
    )
    source_hashes = {_relative(path): _sha256(path) for path in source_paths}
    what_closed = [
        "For fixed -1<beta<0 and zeta != 0, the generic Eq. (123) factor F=(zeta+R)/(1-beta), R^2=zeta^2+1-beta^2, cannot vanish because R=-zeta would contradict 1-beta^2>0. The only speed-factor zero in Re(zeta)>=0 is zeta=-beta, treated by the corrected ODE-consistent Jordan chart.",
        "At glancing R=0, Eq. (123) has the positive limit (1-beta^2)^5/[256*abs(beta)^20*(1-beta)^16]. At high frequency its determinant tends to 2^8/[abs(beta)^20*(1-beta)^6]; both limits were compared with source-matrix screens.",
        f"The complex Jordan divided-difference chart was screened on {len(jordan_approach)} paths and converges to the corrected exact Jordan operator. The high-frequency transfer screen covers {len(high_frequency)} points and supports, but does not prove, ||T_infinity||_2=1-beta.",
        f"At zeta radii down to {min(LOW_RADII):g}, {len(low_frequency)} complex approaches show directionally stable transfer norms for beta={list(BETA_VALUES)}; this is numerical endpoint evidence, not an exact zeta=0 matrix limit.",
        f"An exploratory high-frequency screen covers {len(high_frequency_parameter_sweep)} points across {len(HIGH_SWEEP_BETA_VALUES)} fixed beta values and {len(HIGH_ANGLES)} complex directions; the maximum norm error at radius {max(HIGH_SWEEP_RADII):g} is {max(high_sweep_last_radius_errors):.3g}. The grid and tolerance followed a preliminary diagnostic preview, so this is not preregistered or independent validation; it remains finite-grid evidence, not an exact limit or continuous beta bound.",
        "The linked high-frequency endpoint artifact constructs T_infinity(beta)=W_infinity*C_infinity^-1 from the exact leading normalized modes. Its analytic determinant limit is nonzero for every fixed -1<beta<0; the norm identity remains numerical only.",
    ]
    what_open = [
        "The zeta->0 transfer extension and a rigorous transfer-operator bound over all finite frequencies for each fixed beta remain unproved. The numerical identity ||T_infinity||_2=1-beta also lacks a symbolic norm proof.",
        "No common Kreiss constant over the full -1<beta<0 family is claimed; the separate beta->-1 no-uniform result remains controlling.",
        "Full first-order variable-coefficient GH boundary evolution, tangential/corner treatment, dimensional-observable mapping, and the Core curved 3+1 parent remain open.",
    ]
    major = {
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_COMPLEX_FREQUENCY_COMPACTIFICATION_SCREEN",
        "topic": "core_curved_3p1",
        "closure_level": "PARTIAL",
        "what_is_closed": what_closed,
        "what_remains_open": what_open,
        "equation_or_mapping": {
            "transfer": "T(beta,zeta)=W(beta,zeta)*C(beta,zeta)^-1",
            "generic_determinant_eq123": "|det C|=|F|^16*|zeta^2-beta^2|^10/(8*|zeta|^16*|beta|^20*K1^10*K2^10)",
            "factor": "F=zeta-(1+beta)*lambda1=(zeta+R)/(1-beta); R^2=zeta^2+1-beta^2, branch Re(R)>0 for Re(zeta)>0",
            "glancing_limit": "(1-beta^2)^5/(256*|beta|^20*(1-beta)^16)",
            "high_frequency_determinant_limit": "2^8/(|beta|^20*(1-beta)^6)",
            "high_frequency_transfer_norm_candidate": "||T_infinity||_2=1-beta; finite-grid support only",
            "expanded_high_frequency_beta_grid": "12 fixed beta values in (-1,0), two radii, and five complex directions; exploratory finite-grid screen only, not preregistered",
        },
        "units": "Dimensionless frozen-coefficient Fourier-Laplace variables; tangential frequency is normalized to one.",
        "derivation_class": "source-matched analytic determinant factor analysis, exact corrected Jordan endpoint, exact high-frequency matrix endpoint construction, and finite complex-frequency matrix screens",
        "observable": "40x30 state-transfer operator norm, source determinant log residual, principal-mode residual, and Jordan-chart convergence",
        "data_role": "internal standard-GR frozen-coefficient diagnostic; no empirical data, fitting, or holdout",
        "evidence_artifacts": [
            {"path": _relative(Path(__file__)), "sha256": source_hashes[_relative(Path(__file__))]},
            {"path": _relative(JOINT_SCRIPT), "sha256": source_hashes[_relative(JOINT_SCRIPT)]},
            {"path": _relative(NEGATIVE_ARTIFACT), "sha256": source_hashes[_relative(NEGATIVE_ARTIFACT)]},
            {"path": _relative(JORDAN_ARTIFACT), "sha256": source_hashes[_relative(JORDAN_ARTIFACT)]},
            {"path": _relative(NORM_ARTIFACT), "sha256": source_hashes[_relative(NORM_ARTIFACT)]},
            {"path": _relative(HIGH_ENDPOINT_ARTIFACT), "sha256": source_hashes[_relative(HIGH_ENDPOINT_ARTIFACT)]},
        ],
        "verification_status": status,
        "open_blockers": [
            blocker,
            "uniform-in-beta Kreiss constant excluded near beta=-1",
            "full variable-coefficient GH boundary and Core-parent gates remain open",
        ],
        "dependency_unlocked": "none; Core parent remains PARTIAL and Gravity remains blocked",
        "claim_boundary": claim_boundary,
    }
    return {
        "schema_version": "core-curved-3p1-gh-rinne-complex-frequency-screen-v1",
        "artifact": "curved_3p1_gh_rinne_complex_frequency_screen",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "major_result_id": major["major_result_id"],
        "major_result": major,
        "closure_level": "PARTIAL",
        "MAJOR_RESULT_CLOSURE": "PARTIAL",
        "WHAT_IS_ACTUALLY_CLOSED": what_closed,
        "WHAT_REMAINS_OPEN": what_open,
        "DEPENDENCY_UNLOCKED": major["dependency_unlocked"],
        "STATUS": status,
        "status": status,
        "EQUATION_OR_MAPPING": major["equation_or_mapping"],
        "VERIFICATION": {
            "checks": checks,
            "beta_values": list(BETA_VALUES),
            "low_frequency_radii": list(LOW_RADII),
            "complex_directions": list(DIRECTIONS),
            "low_frequency_cases": low_frequency,
            "glancing_offsets": list(GLANCING_OFFSETS),
            "glancing_cases": glancing,
            "glancing_sign_spreads": glancing_sign_spreads,
            "glancing_limit_log_offsets": glancing_limit_log_offsets,
            "high_frequency_radii": list(HIGH_RADII),
            "high_frequency_angles": list(HIGH_ANGLES),
            "high_frequency_cases": high_frequency,
            "high_frequency_errors": high_frequency_errors,
            "high_frequency_parameter_sweep_beta_values": list(HIGH_SWEEP_BETA_VALUES),
            "high_frequency_parameter_sweep_radii": list(HIGH_SWEEP_RADII),
            "high_frequency_parameter_sweep_angles": list(HIGH_ANGLES),
            "high_frequency_parameter_sweep_cases": high_frequency_parameter_sweep,
            "high_frequency_parameter_sweep_errors": high_frequency_parameter_sweep_errors,
            "high_frequency_parameter_sweep_design": {
                "status": "EXPLORATORY_NOT_PREREGISTERED",
                "grid_role": "finite numerical consistency screen after preliminary diagnostic preview",
                "tolerance_origin": "2e-9 norm-error tolerance declared after preliminary preview; not an independent acceptance threshold",
            },
            "high_frequency_determinant_offsets": high_frequency_determinant_offsets,
            "jordan_beta": jordan_beta,
            "jordan_exact_operator_norm": jordan_reference_norm,
            "jordan_exact_principal_mode_residual": jordan_residual,
            "jordan_exact_determinant_log_error": abs(float(jordan_logdet) - jordan_expected_logdet),
            "jordan_approach_cases": jordan_approach,
            "jordan_error_by_offset": jordan_error_by_offset,
            "zeta_to_zero_direction_spreads": zero_direction_spreads,
            "analytic_endpoint_determinants": endpoint_values,
            "maximum_principal_mode_residual": maximum_mode_residual,
            "maximum_source_eq123_log_abs_determinant_error": maximum_determinant_log_error,
            "source_hashes": source_hashes,
            "high_frequency_endpoint_result": {
                "path": _relative(HIGH_ENDPOINT_ARTIFACT),
                "sha256": source_hashes[_relative(HIGH_ENDPOINT_ARTIFACT)],
                "major_result_id": high_endpoint_artifact["major_result_id"],
                "closure_level": high_endpoint_artifact["closure_level"],
                "status": high_endpoint_artifact["STATUS"],
            },
            "primary_source": {
                "locator": "https://arxiv.org/abs/gr-qc/0606053",
                "sections": ["3.1", "3.2"],
                "equations": ["(51)-(55)", "(69)-(74)", "(109)-(124)"],
                "note": "Eq. (123) generic factor is checked against the registered source matrix. The printed Jordan normalization discrepancy is retained; the exact point uses the separately audited ODE-consistent chain.",
            },
        },
        "CONTROLLING_BLOCKER": blocker,
        "NEXT_ACTION": "Derive the zeta->0 transfer extension, then use the source-matched determinant criterion and normalized-mode assumptions to prove or interval-certify the finite-frequency transfer bound for each fixed beta. Keep the beta-family no-uniform result separate and do not promote the Core parent.",
        "CLAIM_BOUNDARY": claim_boundary,
        "full_core_unlock": False,
        "gravity_unlock": False,
        "claim_promotion": False,
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "artifact": _relative(OUTPUT),
                "status": artifact["STATUS"],
                "checks": artifact["VERIFICATION"]["checks"],
                "summary": {
                    "low_frequency_cases": len(artifact["VERIFICATION"]["low_frequency_cases"]),
                    "glancing_cases": len(artifact["VERIFICATION"]["glancing_cases"]),
                    "high_frequency_cases": len(artifact["VERIFICATION"]["high_frequency_cases"]),
                    "high_frequency_parameter_sweep_cases": len(artifact["VERIFICATION"]["high_frequency_parameter_sweep_cases"]),
                    "jordan_approach_cases": len(artifact["VERIFICATION"]["jordan_approach_cases"]),
                    "max_mode_residual": artifact["VERIFICATION"]["maximum_principal_mode_residual"],
                    "max_eq123_log_error": artifact["VERIFICATION"]["maximum_source_eq123_log_abs_determinant_error"],
                    "jordan_error_by_offset": artifact["VERIFICATION"]["jordan_error_by_offset"],
                    "high_frequency_errors": artifact["VERIFICATION"]["high_frequency_errors"],
                    "high_frequency_parameter_sweep_errors": artifact["VERIFICATION"]["high_frequency_parameter_sweep_errors"],
                },
            },
            indent=2,
        )
    )
    return 0 if all(artifact["VERIFICATION"]["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
