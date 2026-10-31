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
BASELINE_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_zero_shift_kreiss_symbol.py"
BASELINE_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_zero_shift_kreiss_symbol.json"
POSITIVE_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_positive_shift_kreiss_symbol.py"
POSITIVE_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_positive_shift_kreiss_symbol.json"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_negative_shift_kreiss_symbol.json"
GH_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py"
BOUNDARY_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py"
MODE_SOURCE = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_tangential_cpbc_mode.py"
NORMAL = np.array([-1.0, 0.0, 0.0])
OMEGA = 1.0
GAMMA2 = 1.0
BETA_VALUES = (-0.1, -0.5, -0.9)
OFF_GRID_BETA_VALUES = (-0.01, -0.25, -0.75, -0.99)
CONFLUENT_EPSILON_VALUES = (1.0e-2, 1.0e-4, 1.0e-6, 1.0e-8)
REAL_ZETA = (1.0e-10, 1.0e-8, 1.0e-6, 1.0e-4, 1.0e-2, 0.1, 1.0, 10.0, 1.0e2, 1.0e4, 1.0e6)
IMAG_ZETA = (
    0.0, 0.5, 0.999999, 1.0, 1.000001, 2.0, 10.0, 1.0e2, 1.0e4, 1.0e6,
    -0.5, -0.999999, -1.0, -1.000001, -2.0, -10.0, -1.0e2, -1.0e4, -1.0e6,
)
RANK_RELATIVE_TOLERANCE = 1.0e-10
MODE_RESIDUAL_TOLERANCE = 1.0e-8
DETERMINANT_TOLERANCE = 1.0e-8
CHARACTERISTIC_TOLERANCE = 1.0e-12
RINNE_URL = "https://arxiv.org/abs/gr-qc/0606053"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASELINE = _load_module("_uet_rinne_negative_zero_helpers", BASELINE_SCRIPT)
POSITIVE = _load_module("_uet_rinne_negative_positive_helpers", POSITIVE_SCRIPT)
MODE = BASELINE.MODE


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _root_and_lambdas(zeta: complex, beta: float) -> tuple[complex, complex, complex]:
    gamma_squared = 1.0 / (1.0 - beta * beta)
    root = complex(np.sqrt(zeta * zeta + 1.0 - beta * beta + 0.0j))
    if root.real < 0.0:
        root = -root
    if root.real <= 0.0:
        raise RuntimeError("negative-shift decaying-root branch lost positive real part")
    lambda1 = gamma_squared * (-beta * zeta - root)
    lambda2 = zeta / beta
    if lambda1.real >= 0.0 or lambda2.real >= 0.0:
        raise RuntimeError("a Rinne beta<0 mode is not decaying for Re(zeta)>0")
    return root, lambda1, lambda2


def _local_characteristics(beta: float) -> dict[str, Any]:
    parameters = MODE.CANONICAL_GH.GHParameters(shift=(beta, 0.0, 0.0))
    symbol = MODE.CANONICAL_GH.gh_principal_symbol(NORMAL, parameters)
    speeds = np.asarray(symbol.characteristic_speeds, dtype=float)
    labels = ("u0", "u1_plus", "u1_minus", "u2_tangent_1", "u2_tangent_2")
    incoming = [label for label, speed in zip(labels, speeds) if speed < -CHARACTERISTIC_TOLERANCE]
    return {
        "rinne_coordinate_shift_beta": beta,
        "local_outward_normal": NORMAL.tolist(),
        "local_normal_shift": float(np.asarray(parameters.shift) @ NORMAL),
        "characteristic_speeds_by_label": dict(zip(labels, speeds.tolist())),
        "incoming_modes": incoming,
        "u2_modes_are_incoming": bool(np.all(speeds[3:] < -CHARACTERISTIC_TOLERANCE)),
        "expected_regime": "U1_AND_U2_INCOMING_SUBLUMINAL",
    }


def _generic_mode(zeta: complex, beta: float, family: int) -> tuple[np.ndarray, np.ndarray]:
    _, lambda1, lambda2 = _root_and_lambdas(zeta, beta)
    if family == 0:
        value = np.asarray([zeta - beta * lambda1, -lambda1, -1.0j * OMEGA, 0.0j])
        value = value.astype(complex) / np.linalg.norm(value)
        return value, lambda1 * value
    if family == 1:
        value = np.asarray([0.0j, -1.0j * beta, zeta, 0.0j])
        value = value.astype(complex) / np.linalg.norm(value)
        return value, lambda2 * value
    if family == 2:
        value = np.asarray([0.0j, 0.0j, 0.0j, 1.0j])
        return value, lambda2 * value
    raise ValueError("family must be 0, 1, or 2")


def _degenerate_mode(beta: float, family: int, convention: str) -> tuple[np.ndarray, np.ndarray]:
    vector_a = np.asarray([-beta, 0.0, 1.0j, 0.0j], dtype=complex)
    vector_b = np.asarray([0.0j, 1.0, -1.0j, 0.0j], dtype=complex)
    vector_c = np.asarray([0.0j, 0.0j, 0.0j, 1.0], dtype=complex)
    if convention == "printed_euclidean_norms":
        k1 = float(np.linalg.norm(vector_a))
        k2 = float(np.linalg.norm(vector_b))
        if family == 0:
            return vector_a / k1, -vector_a / k1 + vector_b / k2
        if family == 1:
            return vector_b / k2, -vector_b / k2
    if convention == "source_ode_consistent":
        k1 = float(np.linalg.norm(vector_a))
        k2 = float(np.linalg.norm(vector_b))
        if family == 0:
            return vector_a / k1, -vector_a / k1 + vector_b / k1
        if family == 1:
            return vector_b / k2, -vector_b / k2
    if convention in {"source_common_normalization", "confluent_limit"}:
        k = float(np.sqrt(2.0))
        if family == 0:
            value = vector_a / k
            if convention == "confluent_limit":
                value = value + vector_b / (2.0 * k)
            return value, -value + vector_b / k
        if family == 1:
            return vector_b / k, -vector_b / k
    if family == 2:
        return vector_c, -vector_c
    if family in (0, 1):
        raise ValueError("unknown degenerate normalization convention")
    raise ValueError("family must be 0, 1, or 2")


def _boundary_column(
    beta: float,
    zeta: complex,
    value: np.ndarray,
    derivative_xi: np.ndarray,
    component: int,
) -> tuple[np.ndarray, float, float]:
    tensor = np.zeros((4, 4), dtype=complex)
    i, j = MODE.PAIRS[component]
    tensor[i, j] = tensor[j, i] = 1.0
    tensor /= np.sqrt(MODE.TENSOR_WEIGHTS[component])

    pi = value[0] * tensor
    phi = np.stack([entry * tensor for entry in value[1:]])
    dmetric = np.zeros((3, 4, 4), dtype=complex)
    dpi = np.zeros_like(dmetric)
    dphi = np.zeros((3, 3, 4, 4), dtype=complex)
    dpi[0] = derivative_xi[0] * tensor
    dpi[1] = 1.0j * OMEGA * pi
    dphi[0] = np.stack([entry * tensor for entry in derivative_xi[1:]])
    dphi[1] = 1.0j * OMEGA * phi

    residuals = []
    for part in ("real", "imag"):
        pick = lambda array: getattr(array, part)
        residuals.append(
            MODE.BOUNDARY.gh_linear_boundary_residuals(
                metric_perturbation=np.zeros((4, 4)),
                pi_perturbation=pick(pi),
                phi_perturbation=pick(phi),
                metric_gradient=np.zeros((3, 4, 4)),
                pi_gradient=pick(dpi),
                phi_gradient=pick(dphi),
                normal=NORMAL,
                lapse=1.0,
                normal_shift=-beta,
                gamma2=GAMMA2,
            )
        )
    real, imag = residuals
    if real.boundary_regime != imag.boundary_regime:
        raise RuntimeError("complex split changed the incoming characteristic regime")

    complex_value = lambda name: np.asarray(getattr(real, name)) + 1.0j * np.asarray(
        getattr(imag, name)
    )
    constraint = complex_value("constraint_incoming")
    physical = complex_value("physical_weyl_incoming")
    gauge = complex_value("gauge_incoming")
    u2_curl = complex_value("u2_curl_incoming")
    normal_maps = MODE.BOUNDARY.gh_boundary_normal_maps(NORMAL)
    projectors = MODE.PROJECTORS.build_gh_boundary_projectors(NORMAL)
    gauge_basis = np.linalg.svd(projectors.gauge)[0]
    gauge_basis = gauge_basis[:, : projectors.ranks["gauge"]]
    top_rows = np.concatenate(
        (
            constraint,
            normal_maps["physical"] @ BASELINE._pack_symmetric(physical),
            gauge_basis.conj().T @ BASELINE._pack_symmetric(gauge),
        )
    )
    # Local tangents are +y and -z; the (x,y) source curl row has opposite sign.
    u2_rows = np.concatenate(
        (
            -BASELINE._pack_symmetric(u2_curl[0]),
            BASELINE._pack_symmetric(u2_curl[1]),
        )
    )
    source_curl_rows = np.concatenate(
        (
            BASELINE._pack_symmetric(dphi[0, 1] - 1.0j * OMEGA * phi[0]),
            BASELINE._pack_symmetric(dphi[0, 2]),
        )
    )
    curl_map_residual = float(np.max(np.abs(u2_rows - source_curl_rows)))
    if zeta == 0.0:
        raise ValueError("the preregistered symbol excludes zeta=0")
    top_rows[:6] /= zeta
    u2_rows /= zeta
    boundary_column = np.concatenate((top_rows, u2_rows))

    effective_pi = zeta * pi - beta * dpi[0]
    effective_phi = zeta * phi - beta * dphi[0]
    bulk = np.asarray(
        [
            effective_pi + dphi[0, 0] + 1.0j * OMEGA * phi[1],
            effective_phi[0] + dpi[0],
            effective_phi[1] + 1.0j * OMEGA * pi,
            effective_phi[2],
        ]
    )
    return boundary_column, float(np.max(np.abs(bulk))), curl_map_residual


def _source_transforms() -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    top_rows, tensor_columns, map_audit = BASELINE._source_component_basis_map()
    row_transform = np.eye(30)
    row_transform[:10, :10] = top_rows
    column_transform = np.kron(np.eye(3), tensor_columns)
    return row_transform, column_transform, map_audit


def _matrix_metrics(
    columns: list[np.ndarray],
    row_transform: np.ndarray,
    column_transform: np.ndarray,
) -> dict[str, Any]:
    boundary_data = np.column_stack(columns)
    row_norms = np.linalg.norm(boundary_data, axis=1)
    if np.any(row_norms == 0.0):
        raise RuntimeError("boundary-symbol row equilibration encountered a zero row")
    row_equilibrated = boundary_data / row_norms[:, None]
    singular_values = np.linalg.svd(row_equilibrated, compute_uv=False)
    rank = int(
        np.count_nonzero(singular_values > RANK_RELATIVE_TOLERANCE * singular_values[0])
    )
    source_matrix = row_transform @ boundary_data @ column_transform
    sign, log_abs_determinant = np.linalg.slogdet(source_matrix)
    return {
        "boundary_matrix_rank": rank,
        "boundary_relative_smallest_singular_value": float(
            singular_values[-1] / singular_values[0]
        ),
        "source_determinant_sign": complex(sign),
        "source_determinant_log_abs": float(log_abs_determinant),
    }


def _generic_case(
    beta: float,
    zeta: complex,
    row_transform: np.ndarray,
    column_transform: np.ndarray,
) -> dict[str, Any]:
    columns: list[np.ndarray] = []
    maximum_mode_residual = 0.0
    maximum_curl_map_residual = 0.0
    for family in range(3):
        value, derivative = _generic_mode(zeta, beta, family)
        for component in range(10):
            column, mode_residual, curl_residual = _boundary_column(
                beta, zeta, value, derivative, component
            )
            columns.append(column)
            maximum_mode_residual = max(maximum_mode_residual, mode_residual)
            maximum_curl_map_residual = max(maximum_curl_map_residual, curl_residual)

    metrics = _matrix_metrics(columns, row_transform, column_transform)
    _, lambda1, _ = _root_and_lambdas(zeta, beta)
    k1 = float(np.linalg.norm([zeta - beta * lambda1, -lambda1, -1.0j, 0.0j]))
    k2 = float(np.linalg.norm([0.0j, -1.0j * beta, zeta, 0.0j]))
    determinant_factor = zeta - (1.0 + beta) * lambda1
    speed_factor = zeta * zeta - beta * beta
    expected_log_abs = float(
        16.0 * np.log(abs(determinant_factor))
        + 10.0 * np.log(abs(speed_factor))
        - np.log(8.0)
        - 16.0 * np.log(abs(zeta))
        - 20.0 * np.log(abs(beta))
        - 10.0 * np.log(k1)
        - 10.0 * np.log(k2)
    )
    expected_phase = float(
        np.angle(-1.0 + 0.0j)
        + 16.0 * np.angle(determinant_factor)
        + 10.0 * np.angle(speed_factor)
        - 16.0 * np.angle(zeta)
    )
    sign = metrics.pop("source_determinant_sign")
    log_abs = metrics.pop("source_determinant_log_abs")
    metrics.update(
        {
            "beta": beta,
            "zeta_real": float(zeta.real),
            "zeta_imag": float(zeta.imag),
            "decaying_subspace_dimension": len(columns),
            "maximum_principal_mode_residual": maximum_mode_residual,
            "maximum_u2_source_row_map_residual": maximum_curl_map_residual,
            "source_eq_123_log_offset": float(log_abs - expected_log_abs),
            "source_eq_123_phase_offset_radians": float(
                np.angle(np.exp(1.0j * (np.angle(sign) - expected_phase)))
            ),
        }
    )
    return metrics


def _degenerate_case(
    beta: float,
    convention: str,
    row_transform: np.ndarray,
    column_transform: np.ndarray,
) -> dict[str, Any]:
    zeta = -beta
    columns: list[np.ndarray] = []
    maximum_mode_residual = 0.0
    maximum_curl_map_residual = 0.0
    for family in range(3):
        value, derivative = _degenerate_mode(beta, family, convention)
        for component in range(10):
            column, mode_residual, curl_residual = _boundary_column(
                beta, zeta, value, derivative, component
            )
            columns.append(column)
            maximum_mode_residual = max(maximum_mode_residual, mode_residual)
            maximum_curl_map_residual = max(maximum_curl_map_residual, curl_residual)

    metrics = _matrix_metrics(columns, row_transform, column_transform)
    vector_a = np.asarray([-beta, 0.0, 1.0j, 0.0j])
    vector_b = np.asarray([0.0j, 1.0, -1.0j, 0.0j])
    if convention in {"printed_euclidean_norms", "source_ode_consistent"}:
        k1 = float(np.linalg.norm(vector_a))
        k2 = float(np.linalg.norm(vector_b))
        if convention == "printed_euclidean_norms":
            expected_log_abs = float(
                10.0 * np.log(k1 + k2)
                - np.log(8.0)
                - 26.0 * np.log(abs(beta))
                - 10.0 * np.log(k1)
                - 20.0 * np.log(k2)
            )
        else:
            expected_log_abs = float(
                np.log(4.0)
                - 26.0 * np.log(abs(beta))
                - 5.0 * np.log(1.0 + beta * beta)
            )
    else:
        k1 = k2 = float(np.sqrt(2.0))
        expected_log_abs = float(
            10.0 * np.log(k1 + k2)
            - np.log(8.0)
            - 26.0 * np.log(abs(beta))
            - 10.0 * np.log(k1)
            - 20.0 * np.log(k2)
        )
    sign = metrics.pop("source_determinant_sign")
    log_abs = metrics.pop("source_determinant_log_abs")
    phase_offset = float(np.angle(sign))
    return {
        "beta": beta,
        "zeta": zeta,
        "basis_convention": convention,
        "decaying_subspace_dimension": 30,
        "maximum_principal_mode_residual": maximum_mode_residual,
        "maximum_u2_source_row_map_residual": maximum_curl_map_residual,
        "source_eq_124_log_offset": (
            float(log_abs - expected_log_abs)
            if convention == "printed_euclidean_norms"
            else None
        ),
        "confluent_reference_log_offset": (
            float(log_abs - expected_log_abs)
            if convention == "confluent_limit"
            else None
        ),
        "corrected_jordan_determinant_log_offset": (
            float(log_abs - expected_log_abs)
            if convention == "source_ode_consistent"
            else None
        ),
        "basis_determinant_log_abs": log_abs,
        "source_eq_124_phase_offset_radians": phase_offset,
        **metrics,
    }


def _near_degenerate_case(
    beta: float,
    epsilon: float,
    row_transform: np.ndarray,
    column_transform: np.ndarray,
) -> dict[str, Any]:
    zeta = complex(-beta + epsilon, 0.0)
    _, lambda1, lambda2 = _root_and_lambdas(zeta, beta)
    eigenvalue_gap = lambda2 - lambda1
    if abs(eigenvalue_gap) == 0.0:
        raise RuntimeError("confluent basis requires distinct generic eigenvalues")

    raw_columns: list[np.ndarray] = []
    confluent_columns: list[np.ndarray] = []
    maximum_mode_residual = 0.0
    maximum_curl_map_residual = 0.0
    for component in range(10):
        mode_columns: list[np.ndarray] = []
        for family in range(3):
            value, derivative = _generic_mode(zeta, beta, family)
            column, mode_residual, curl_residual = _boundary_column(
                beta, zeta, value, derivative, component
            )
            mode_columns.append(column)
            maximum_mode_residual = max(maximum_mode_residual, mode_residual)
            maximum_curl_map_residual = max(maximum_curl_map_residual, curl_residual)
        mode1, mode2, mode3 = mode_columns
        raw_columns.extend(mode_columns)
        generalized = (-1.0j * mode2 - mode1) / eigenvalue_gap
        confluent_columns.extend((generalized, mode1, mode3))

    raw_metrics = _matrix_metrics(raw_columns, row_transform, column_transform)
    confluent_metrics = _matrix_metrics(
        confluent_columns, row_transform, column_transform
    )
    jordan_norm = float(np.sqrt(2.0))
    expected_log_abs = float(
        10.0 * np.log(2.0 * jordan_norm)
        - np.log(8.0)
        - 26.0 * np.log(abs(beta))
        - 30.0 * np.log(jordan_norm)
    )
    confluent_sign = confluent_metrics.pop("source_determinant_sign")
    confluent_log_abs = confluent_metrics.pop("source_determinant_log_abs")
    return {
        "beta": beta,
        "epsilon_from_degenerate_zeta": epsilon,
        "zeta": [float(zeta.real), float(zeta.imag)],
        "eigenvalue_gap": [float(eigenvalue_gap.real), float(eigenvalue_gap.imag)],
        "raw_generic_rank": raw_metrics["boundary_matrix_rank"],
        "raw_generic_row_equilibrated_singular_ratio": raw_metrics[
            "boundary_relative_smallest_singular_value"
        ],
        "confluent_rank": confluent_metrics["boundary_matrix_rank"],
        "confluent_row_equilibrated_singular_ratio": confluent_metrics[
            "boundary_relative_smallest_singular_value"
        ],
        "maximum_principal_mode_residual": maximum_mode_residual,
        "maximum_u2_source_row_map_residual": maximum_curl_map_residual,
        "confluent_determinant_log_abs": float(confluent_log_abs),
        "confluent_reference_log_offset": float(
            confluent_log_abs - expected_log_abs
        ),
        "eq_124_phase_offset_radians": float(np.angle(confluent_sign)),
    }


def build_artifact() -> dict[str, Any]:
    row_transform, column_transform, basis_map_audit = _source_transforms()
    generic_cases: list[dict[str, Any]] = []
    for beta in BETA_VALUES:
        for real in REAL_ZETA:
            for imag in IMAG_ZETA:
                zeta = complex(real, imag)
                if zeta == complex(-beta, 0.0):
                    continue
                generic_cases.append(_generic_case(beta, zeta, row_transform, column_transform))

    degenerate_cases = [
        _degenerate_case(beta, convention, row_transform, column_transform)
        for beta in BETA_VALUES
        for convention in (
            "printed_euclidean_norms",
            "source_ode_consistent",
            "source_common_normalization",
            "confluent_limit",
        )
    ]
    confluent_cases = [
        _near_degenerate_case(beta, epsilon, row_transform, column_transform)
        for beta in BETA_VALUES
        for epsilon in CONFLUENT_EPSILON_VALUES
    ]
    off_grid_corrected_cases = [
        _degenerate_case(beta, "source_ode_consistent", row_transform, column_transform)
        for beta in OFF_GRID_BETA_VALUES
    ]
    maximum_mode_residual = max(
        row["maximum_principal_mode_residual"] for row in generic_cases
    )
    maximum_curl_map_residual = max(
        row["maximum_u2_source_row_map_residual"]
        for row in generic_cases + degenerate_cases + confluent_cases
    )
    maximum_eq_123_log_offset = max(
        abs(row["source_eq_123_log_offset"]) for row in generic_cases
    )
    maximum_eq_123_phase_offset = max(
        abs(row["source_eq_123_phase_offset_radians"]) for row in generic_cases
    )
    maximum_eq_123_phase_offset_from_global_sign = min(
        max(
            abs(
                np.angle(
                    np.exp(1.0j * (row["source_eq_123_phase_offset_radians"] - target))
                )
            )
            for row in generic_cases
        )
        for target in (0.0, np.pi)
    )
    determinant_orientation_sign = (
        "-1"
        if all(
            abs(np.angle(np.exp(1.0j * (row["source_eq_123_phase_offset_radians"] - np.pi))))
            < DETERMINANT_TOLERANCE
            for row in generic_cases
        )
        else "+1"
        if all(
            abs(np.angle(np.exp(1.0j * row["source_eq_123_phase_offset_radians"])))
            < DETERMINANT_TOLERANCE
            for row in generic_cases
        )
        else "NOT_GLOBAL"
    )
    generic_grid_count = len(REAL_ZETA) * len(IMAG_ZETA)
    generic_expected_count = generic_grid_count * len(BETA_VALUES) - sum(
        complex(-beta, 0.0) in {complex(real, imag) for real in REAL_ZETA for imag in IMAG_ZETA}
        for beta in BETA_VALUES
    )
    per_beta: list[dict[str, Any]] = []
    for beta in BETA_VALUES:
        generic = [row for row in generic_cases if row["beta"] == beta]
        literal = next(
            row
            for row in degenerate_cases
            if row["beta"] == beta
            and row["basis_convention"] == "printed_euclidean_norms"
        )
        corrected = next(
            row
            for row in degenerate_cases
            if row["beta"] == beta
            and row["basis_convention"] == "source_ode_consistent"
        )
        common = next(
            row
            for row in degenerate_cases
            if row["beta"] == beta
            and row["basis_convention"] == "source_common_normalization"
        )
        confluent = next(
            row
            for row in degenerate_cases
            if row["beta"] == beta and row["basis_convention"] == "confluent_limit"
        )
        limit_rows = [row for row in confluent_cases if row["beta"] == beta]
        characteristic = _local_characteristics(beta)
        source_k1 = float(np.sqrt(1.0 + beta * beta))
        source_k2 = float(np.sqrt(2.0))
        per_beta.append(
            {
                "rinne_beta": beta,
                "local_normal_shift": characteristic["local_normal_shift"],
                "incoming_modes": characteristic["incoming_modes"],
                "generic_case_count": len(generic),
                "generic_minimum_boundary_rank": min(
                    row["boundary_matrix_rank"] for row in generic
                ),
                "generic_minimum_row_equilibrated_singular_ratio": min(
                    row["boundary_relative_smallest_singular_value"] for row in generic
                ),
                "generic_maximum_principal_mode_residual": max(
                    row["maximum_principal_mode_residual"] for row in generic
                ),
                "generic_maximum_eq_123_log_offset": max(
                    abs(row["source_eq_123_log_offset"]) for row in generic
                ),
                "generic_maximum_eq_123_phase_offset_radians": max(
                    abs(row["source_eq_123_phase_offset_radians"]) for row in generic
                ),
                "source_eq_124_to_corrected_jordan_determinant_ratio": float(
                    (source_k1 + source_k2) ** 10
                    / (32.0 * source_k2**20)
                ),
                "degenerate_literal_euclidean_norm_basis": {
                    key: literal[key]
                    for key in (
                        "maximum_principal_mode_residual",
                        "boundary_matrix_rank",
                        "boundary_relative_smallest_singular_value",
                        "source_eq_124_log_offset",
                        "source_eq_124_phase_offset_radians",
                    )
                },
                "degenerate_ode_consistent_source_norm_basis": {
                    key: corrected[key]
                    for key in (
                        "maximum_principal_mode_residual",
                        "boundary_matrix_rank",
                        "boundary_relative_smallest_singular_value",
                        "basis_determinant_log_abs",
                        "corrected_jordan_determinant_log_offset",
                    )
                },
                "degenerate_source_common_normalization_basis": {
                    key: common[key]
                    for key in (
                        "maximum_principal_mode_residual",
                        "boundary_matrix_rank",
                        "boundary_relative_smallest_singular_value",
                        "confluent_reference_log_offset",
                        "source_eq_124_phase_offset_radians",
                    )
                },
                "degenerate_confluent_limit_basis": {
                    key: confluent[key]
                    for key in (
                        "maximum_principal_mode_residual",
                        "boundary_matrix_rank",
                        "boundary_relative_smallest_singular_value",
                        "basis_determinant_log_abs",
                        "confluent_reference_log_offset",
                        "source_eq_124_phase_offset_radians",
                    )
                },
                "near_degenerate_confluence_sequence": limit_rows,
            }
        )

    literal_cases = [
        row for row in degenerate_cases
        if row["basis_convention"] == "printed_euclidean_norms"
    ]
    common_cases = [
        row for row in degenerate_cases
        if row["basis_convention"] == "source_common_normalization"
    ]
    confluent_exact_cases = [
        row for row in degenerate_cases if row["basis_convention"] == "confluent_limit"
    ]
    corrected_cases = [
        row for row in degenerate_cases if row["basis_convention"] == "source_ode_consistent"
    ]
    maximum_literal_degenerate_residual = max(
        row["maximum_principal_mode_residual"] for row in literal_cases
    )
    maximum_common_degenerate_residual = max(
        row["maximum_principal_mode_residual"] for row in common_cases
    )
    maximum_confluent_exact_residual = max(
        row["maximum_principal_mode_residual"] for row in confluent_exact_cases
    )
    maximum_corrected_degenerate_residual = max(
        row["maximum_principal_mode_residual"] for row in corrected_cases
    )
    maximum_corrected_jordan_determinant_log_offset = max(
        abs(row["corrected_jordan_determinant_log_offset"])
        for row in corrected_cases + off_grid_corrected_cases
    )
    maximum_literal_eq_124_offset = max(
        abs(row["source_eq_124_log_offset"]) for row in literal_cases
    )
    maximum_confluent_exact_reference_offset = max(
        abs(row["confluent_reference_log_offset"]) for row in confluent_exact_cases
    )
    maximum_near_confluent_reference_offset = max(
        abs(row["confluent_reference_log_offset"])
        for row in confluent_cases
        if row["epsilon_from_degenerate_zeta"] == CONFLUENT_EPSILON_VALUES[-1]
    )
    maximum_near_to_exact_confluent_determinant_log_difference = max(
        abs(
            row["confluent_determinant_log_abs"]
            - next(
                exact["basis_determinant_log_abs"]
                for exact in confluent_exact_cases
                if exact["beta"] == row["beta"]
            )
        )
        for row in confluent_cases
        if row["epsilon_from_degenerate_zeta"] == CONFLUENT_EPSILON_VALUES[-1]
    )
    generic_checks = {
        "three_preregistered_negative_sub_luminal_shifts": all(
            -1.0 < beta < 0.0 for beta in BETA_VALUES
        ),
        "mapped_local_shift_is_minus_rinne_beta": all(
            np.isclose(row["local_normal_shift"], -row["rinne_beta"], atol=1.0e-15)
            for row in per_beta
        ),
        "u1_minus_and_both_u2_families_are_incoming": all(
            row["incoming_modes"]
            == ["u1_minus", "u2_tangent_1", "u2_tangent_2"]
            for row in per_beta
        ),
        "generic_grid_count_matches_preregistered_grid": len(generic_cases)
        == generic_expected_count,
        "generic_decaying_subspace_dimension_is_30": all(
            row["decaying_subspace_dimension"] == 30 for row in generic_cases
        ),
        "generic_boundary_matrices_have_rank_30": all(
            row["boundary_matrix_rank"] == 30 for row in generic_cases
        ),
        "generic_principal_modes_pass": maximum_mode_residual < MODE_RESIDUAL_TOLERANCE,
        "all_20_u2_rows_match_source_equations_113_114": (
            maximum_curl_map_residual < MODE_RESIDUAL_TOLERANCE
        ),
        "generic_eq_123_determinant_log_passes": (
            maximum_eq_123_log_offset < DETERMINANT_TOLERANCE
        ),
        "generic_eq_123_phase_is_one_global_orientation_sign": (
            determinant_orientation_sign != "NOT_GLOBAL"
            and bool(
                maximum_eq_123_phase_offset_from_global_sign
                < DETERMINANT_TOLERANCE
            )
        ),
        "fixed_source_basis_map_identities_pass": bool(
            basis_map_audit["all_projector_and_coordinate_identities_within_tolerance"]
        ),
    }
    degenerate_findings = {
        "printed_eq_74_basis_reproduces_printed_eq_124_determinant": (
            maximum_literal_eq_124_offset < DETERMINANT_TOLERANCE
        ),
        "printed_eq_74_basis_satisfies_principal_ode": (
            maximum_literal_degenerate_residual < MODE_RESIDUAL_TOLERANCE
        ),
        "ode_consistent_source_norm_jordan_repair_passes_principal_ode": (
            maximum_corrected_degenerate_residual < MODE_RESIDUAL_TOLERANCE
        ),
        "ode_consistent_source_norm_jordan_repair_has_rank_30_and_finite_determinant": all(
            row["boundary_matrix_rank"] == 30
            and np.isfinite(row["basis_determinant_log_abs"])
            for row in corrected_cases
        ),
        "corrected_jordan_determinant_matches_analytic_confluent_limit": (
            maximum_corrected_jordan_determinant_log_offset
            < DETERMINANT_TOLERANCE
        ),
        "off_grid_corrected_jordan_cases_have_rank_30_and_pass_ode": all(
            row["boundary_matrix_rank"] == 30
            and row["maximum_principal_mode_residual"] < MODE_RESIDUAL_TOLERANCE
            for row in off_grid_corrected_cases
        ),
        "generic_confluent_limit_basis_passes_principal_ode": (
            maximum_confluent_exact_residual < MODE_RESIDUAL_TOLERANCE
        ),
        "near_degenerate_confluence_remains_full_rank": all(
            row["confluent_rank"] == 30 for row in confluent_cases
        ),
        "near_degenerate_determinant_converges_to_exact_generic_limit_basis": (
            maximum_near_to_exact_confluent_determinant_log_difference < 2.0e-6
        ),
    }
    generic_passed = all(generic_checks.values())
    source_degeneracy_issue_confirmed = (
        degenerate_findings[
            "printed_eq_74_basis_reproduces_printed_eq_124_determinant"
        ]
        and not degenerate_findings["printed_eq_74_basis_satisfies_principal_ode"]
        and degenerate_findings[
            "ode_consistent_source_norm_jordan_repair_passes_principal_ode"
        ]
        and degenerate_findings[
            "ode_consistent_source_norm_jordan_repair_has_rank_30_and_finite_determinant"
        ]
        and degenerate_findings[
            "corrected_jordan_determinant_matches_analytic_confluent_limit"
        ]
        and degenerate_findings[
            "off_grid_corrected_jordan_cases_have_rank_30_and_pass_ode"
        ]
    )
    status = (
        "PASS_SOURCE_MATCHED_NEGATIVE_SHIFT_SAMPLE_WITH_EXACT_DEGENERACY_CORRECTION"
        if generic_passed
        and source_degeneracy_issue_confirmed
        and degenerate_findings[
            "near_degenerate_determinant_converges_to_exact_generic_limit_basis"
        ]
        else "FAIL_OR_UNRESOLVED_NEGATIVE_SHIFT_SYMBOL_AUDIT"
    )
    major_result = {
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_NEGATIVE_SHIFT_SYMBOL",
        "topic": "core_curved_3p1",
        "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS_") else "PARTIAL",
        "subresult_closure": {
            "preregistered_non_degenerate_grid": (
                "CLOSED_FOR_LANE" if generic_passed else "OPEN"
            ),
            "exact_degenerate_source_mode": (
                "CLOSED_FOR_LANE_WITH_ODE_CONSISTENT_JORDAN_CORRECTION"
                if source_degeneracy_issue_confirmed
                and degenerate_findings[
                    "corrected_jordan_determinant_matches_analytic_confluent_limit"
                ]
                else "OPEN_SOURCE_NORMALIZATION_MISMATCH"
            ),
        },
        "what_is_closed": [
            "For beta={-0.1,-0.5,-0.9}, the preregistered 626-point nondegenerate Fourier-Laplace grid reproduces the 30-dimensional decaying subspace, all incoming boundary rows, principal modes, Eqs. (113)-(114), and Eq. (123) magnitude up to one global determinant-orientation sign.",
            "At zeta=-beta, direct substitution shows the source-printed Eq. (74) normalization reproduces the printed Eq. (124) determinant but fails the principal ODE. Replacing the generalized xi*B/K2 term by xi*B/K1 gives a valid Jordan chain. Taking the confluent limit of Eq. (123) and applying the determinant of the explicit basis rescaling gives |det C|=4/(|beta|^26*(1+beta^2)^5); this matches the registered 30x30 determinant at the preregistered shifts and four off-grid beta checks. The exact sampled lane is therefore closed under this explicit correction, while the discrepancy with the source-printed Eq. (124) remains visible.",
        ] if generic_passed else [],
        "equation_or_mapping": {
            "rinne_shift_to_core_normal_shift": "beta_Rinne=N^x in x>0; with outward normal n=-x, beta_n=-beta_Rinne",
            "decaying_roots": "lambda1=gamma^2*(-beta*zeta-sqrt(zeta^2+1-beta^2)); lambda2=zeta/beta; gamma^2=(1-beta^2)^-1",
            "generic_mode_families": "v1=K1^-1*(zeta-beta*lambda1,-lambda1,-i,0); v2=K2^-1*(0,-i*beta,zeta,0); v3=(0,0,0,1), with lambda2 for v2,v3",
            "additional_source_rows": "c4_xy=partial_xi(Phi_y)-i*Phi_x; c4_xz=partial_xi(Phi_z); local tangents +y,-z map to source rows with signs (-,+)",
            "source_eq_74_as_printed": "K1=norm(A), K2=norm(B); e^-xi*[sigma1*A/K1+(sigma1*xi+sigma2)*B/K2+sigma3*C]; reproduces printed Eq. (124) determinant but fails the principal ODE under the declared K norms.",
            "ode_consistent_jordan_repair": "K1=norm(A)=sqrt(1+beta^2), K2=norm(B)=sqrt(2); e^-xi*[sigma1*(A+xi*B)/K1+sigma2*B/K2+sigma3*C]. Its confluent determinant is |det C|=4/(|beta|^26*(1+beta^2)^5), derived from Eq. (123) with the column transform (i/(lambda2-lambda1)) per tensor component.",
            "printed_eq_124_to_corrected_determinant_ratio": "With source-declared K1=sqrt(1+beta^2), K2=sqrt(2), |det C_Eq124|/|det C_corrected|=(K1+K2)^10/(32*K2^20); sampled ratios are about 0.20954, 0.33084, 0.78158 for beta=-0.1,-0.5,-0.9.",
            "generic_confluent_limit_basis": "KJ=sqrt(2); e^-xi*[sigma1*(A+B/2+xi*B)/KJ+sigma2*B/KJ+sigma3*C]; checked against the normalized generic-mode limit, not identified with source Eq. (124).",
        },
        "units": "Frozen local orthonormal geometric units; omega normalized to 1 and zeta=s/omega dimensionless.",
        "derivation_class": "source-matched Fourier-Laplace mode, registered boundary-row reconstruction, finite complex-frequency sampling, and analytic confluent determinant limit",
        "observable": "30x30 boundary-data symbol rank, equilibrated singular ratio, determinant, curl-row residual, and principal-mode residual",
        "data_role": "primary-literature formula cross-check; no empirical data, fitting, or calibration",
        "verification_status": status,
        "open_blockers": [
            "The arXiv/published source text's Eq. (74) normalization and Eq. (124) determinant are not mutually reproduced by an ODE-consistent exact Jordan chain. The corrected determinant closes the registered lane, but whether the discrepancy is a typographical error or reflects a different source convention requires an authoritative correction or independent source confirmation.",
            "The finite frequency grid is not a uniform Kreiss bound over every beta and zeta; nonlinear/variable-coefficient GH, corners, matter boundaries, dimensional observables, and the Core curved-parent gate remain open.",
        ],
        "dependency_unlocked": "none; Core curved 3+1 remains PARTIAL and Gravity remains blocked",
        "claim_boundary": "Frozen-coefficient standard-GR boundary-symbol result for the preregistered finite grid at three negative shifts, including the exact degenerate point under an explicitly ODE-consistent Jordan correction with an analytically derived determinant. The correction does not silently rewrite Rinne's printed Eq. (74)/(124), and no independent uniform Kreiss theorem, nonlinear/variable-coefficient well-posedness result, UET physical result, curved-parent closure, or Gravity unlock is claimed.",
    }
    source_hashes = {
        _rel(path): _sha256(path)
        for path in (
            Path(__file__),
            BASELINE_SCRIPT,
            BASELINE_ARTIFACT,
            POSITIVE_SCRIPT,
            POSITIVE_ARTIFACT,
            MODE_SOURCE,
            BOUNDARY_SOURCE,
            GH_SOURCE,
        )
    }
    return {
        "schema_version": "core-curved-3p1-gh-rinne-negative-shift-kreiss-symbol-v3",
        "artifact": "curved_3p1_gh_rinne_negative_shift_kreiss_symbol",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "major_result_id": major_result["major_result_id"],
        "major_result": major_result,
        "closure_level": major_result["closure_level"],
        "MAJOR_RESULT_CLOSURE": major_result["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": major_result["what_is_closed"],
        "WHAT_REMAINS_OPEN": major_result["open_blockers"],
        "DEPENDENCY_UNLOCKED": major_result["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Added an isolated beta<0 GH boundary-symbol audit. The nondegenerate grid passes, and the exact-degenerate Jordan chain now has an ODE-consistent normalization and determinant derived by confluence from Eq. (123). The distinct source-printed Eq. (74)/(124) discrepancy is retained explicitly. Frozen zero- and positive-shift artifacts, production equations, parent gate, and dependency gates were not modified.",
        "EQUATION_OR_MAPPING": major_result["equation_or_mapping"],
        "VERIFICATION": {
            "generic_checks": generic_checks,
            "degenerate_findings": degenerate_findings,
            "subresult_closure": major_result["subresult_closure"],
            "generic_grid_passed": generic_passed,
            "source_exact_degeneracy_issue_confirmed": source_degeneracy_issue_confirmed,
            "off_grid_corrected_jordan_cases": [
                {
                    "beta": row["beta"],
                    "rank": row["boundary_matrix_rank"],
                    "principal_ode_residual": row[
                        "maximum_principal_mode_residual"
                    ],
                    "determinant_log_offset": row[
                        "corrected_jordan_determinant_log_offset"
                    ],
                }
                for row in off_grid_corrected_cases
            ],
            "generic_case_count": len(generic_cases),
            "degenerate_beta_count": len(BETA_VALUES),
            "exact_degenerate_basis_cases": len(degenerate_cases),
            "near_degenerate_confluence_cases": len(confluent_cases),
            "total_symbol_cases_including_basis_and_confluence_checks": (
                len(generic_cases)
                + len(degenerate_cases)
                + len(confluent_cases)
                + len(off_grid_corrected_cases)
            ),
            "maximum_generic_principal_mode_residual": maximum_mode_residual,
            "maximum_u2_source_row_map_residual": maximum_curl_map_residual,
            "maximum_generic_eq_123_log_offset": maximum_eq_123_log_offset,
            "maximum_generic_eq_123_phase_offset_radians": maximum_eq_123_phase_offset,
            "generic_eq_123_global_orientation_sign": determinant_orientation_sign,
            "maximum_generic_eq_123_phase_deviation_from_global_sign": (
                maximum_eq_123_phase_offset_from_global_sign
            ),
            "maximum_literal_norm_degenerate_principal_residual": maximum_literal_degenerate_residual,
            "maximum_common_jordan_degenerate_principal_residual": maximum_common_degenerate_residual,
            "maximum_ode_consistent_source_norm_jordan_residual": maximum_corrected_degenerate_residual,
            "maximum_corrected_jordan_determinant_log_offset": (
                maximum_corrected_jordan_determinant_log_offset
            ),
            "maximum_confluent_limit_degenerate_principal_residual": maximum_confluent_exact_residual,
            "maximum_literal_norm_eq_124_log_offset": maximum_literal_eq_124_offset,
            "maximum_confluent_basis_reference_log_offset": maximum_confluent_exact_reference_offset,
            "maximum_near_confluent_reference_log_offset_at_smallest_epsilon": (
                maximum_near_confluent_reference_offset
            ),
            "maximum_near_to_exact_confluent_determinant_log_difference": (
                maximum_near_to_exact_confluent_determinant_log_difference
            ),
            "confluent_epsilon_values": list(CONFLUENT_EPSILON_VALUES),
            "per_beta": per_beta,
            "source_basis_map_audit": basis_map_audit,
            "source_hashes": source_hashes,
        },
        "PREREGISTRATION": {
            "rinne_beta_values": list(BETA_VALUES),
            "negative_shift_domain": "-1<beta<0; Rinne coordinate shift points toward decreasing x, outward from x>0",
            "real_zeta_grid": list(REAL_ZETA),
            "imaginary_zeta_grid": list(IMAG_ZETA),
            "exact_degenerate_points": "zeta=-beta evaluated under source-declared separate K norms, an explicitly ODE-consistent generalized-mode rescaling, a common-normalization control, and the normalized generic confluent basis; the corrected determinant is derived from Eq. (123) and compared with the registered boundary matrix",
            "off_grid_corrected_jordan_beta_values": list(OFF_GRID_BETA_VALUES),
            "off_grid_beta_role": "post-derivation implementation cross-check only; not part of the preregistered 626-point generic grid",
            "confluent_epsilon_values": list(CONFLUENT_EPSILON_VALUES),
            "parameter_fitting": False,
            "threshold_changes": False,
            "clipping_or_cone_padding": False,
            "basis_map_refit": False,
        },
        "literature_basis": [
            {
                "source_id": "rinne_2006_first_order_gh_radiation_controlling_cpbc",
                "url": RINNE_URL,
                "equations": "Eq. (73)-(74), Eqs. (113)-(114), Eq. (123)-(124) in arXiv HTML; corresponding PDF Eqs. (73)-(74), (75)-(86), and (89)-(90)",
                "scope": "Specified frozen-coefficient first-order GH Fourier-Laplace system with subluminal normal shift; source result is imported only after basis correspondence",
            }
        ],
        "CONTROLLING_BLOCKER": "uniform_negative_shift_kreiss_bound_over_beta_and_closed_frequency_domain_not_independently_established",
        "NEXT_ACTION": "Derive uniform lower bounds from the corrected confluent determinant and normalized boundary map toward beta=0,-1, zeta->0, the imaginary axis, and |zeta|->infinity. Keep the source Eq. (74)/(124) discrepancy flagged pending authoritative correction; do not promote the Core parent.",
        "CLAIM_BOUNDARY": major_result["claim_boundary"],
        "claim_promotion": False,
        "full_core_unlock": False,
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
                "artifact": _rel(OUTPUT),
                "status": artifact["STATUS"],
                "generic_case_count": artifact["VERIFICATION"]["generic_case_count"],
                "degenerate_findings": artifact["VERIFICATION"]["degenerate_findings"],
            },
            indent=2,
        )
    )
    return 0 if artifact["STATUS"].startswith(("PASS_", "PARTIAL_")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
