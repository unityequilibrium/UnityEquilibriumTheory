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
TRANSITION_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_negative_shift_zero_transition.py"
NEGATIVE_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_negative_shift_kreiss_symbol.py"
NEGATIVE_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_negative_shift_kreiss_symbol.json"
ZERO_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_zero_shift_kreiss_symbol.py"
ZERO_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_zero_shift_kreiss_symbol.json"
BOUNDARY_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py"
PROJECTOR_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_joint_real_glancing_scale.json"
ZETA_VALUES = (1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5)
POWER_PATHS = (0.5, 2.0)
FIXED_BETA_OVER_ZETA = (0.25, 4.0)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


TRANSITION = _load("_uet_joint_scale_transition", TRANSITION_SCRIPT)
NEGATIVE = TRANSITION.NEGATIVE
ROW, COLUMN, _ = NEGATIVE._source_transforms()
ZERO_ROW, ZERO_COLUMN, _ = NEGATIVE.BASELINE._source_component_basis_map()


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _generic_matrix(zeta: float, beta: float) -> tuple[np.ndarray, float]:
    matrix, _ = TRANSITION._source_matrices(
        zeta, beta, (ROW, COLUMN), (ZERO_ROW, ZERO_COLUMN)
    )
    residual = 0.0
    for family in range(3):
        value, derivative = NEGATIVE._generic_mode(complex(zeta, 0.0), beta, family)
        for component in range(10):
            _, mode_residual, _ = NEGATIVE._boundary_column(
                beta, complex(zeta, 0.0), value, derivative, component
            )
            residual = max(residual, mode_residual)
    return matrix, residual


def _jordan_matrix(beta: float) -> tuple[np.ndarray, float]:
    columns: list[np.ndarray] = []
    residual = 0.0
    for family in range(3):
        value, derivative = NEGATIVE._degenerate_mode(
            beta, family, "source_ode_consistent"
        )
        for component in range(10):
            column, mode_residual, _ = NEGATIVE._boundary_column(
                beta, -beta, value, derivative, component
            )
            columns.append(column)
            residual = max(residual, mode_residual)
    return ROW @ np.column_stack(columns) @ COLUMN, residual


def _near_jordan_matrix(delta: float) -> tuple[np.ndarray, float, float]:
    beta = -delta
    zeta = delta + delta**1.5
    spectral = complex(zeta, 0.0)
    _, lambda1, lambda2 = NEGATIVE._root_and_lambdas(spectral, beta)
    gap = lambda2 - lambda1
    columns: list[np.ndarray] = []
    residual = 0.0
    for component in range(10):
        modes: list[np.ndarray] = []
        for family in range(3):
            value, derivative = NEGATIVE._generic_mode(spectral, beta, family)
            column, mode_residual, _ = NEGATIVE._boundary_column(
                beta, spectral, value, derivative, component
            )
            modes.append(column)
            residual = max(residual, mode_residual)
        generalized = (-1.0j * modes[1] - modes[0]) / gap
        columns.extend((generalized, modes[0], modes[2]))
    matrix = ROW @ np.column_stack(columns) @ COLUMN
    reference = NEGATIVE._near_degenerate_case(beta, delta**1.5, ROW, COLUMN)
    return matrix, residual, float(reference["confluent_reference_log_offset"])


def _scaled_record(matrix: np.ndarray, zeta: float, beta: float, basis: str) -> dict[str, Any]:
    b = abs(beta)
    curl_xy_scale = min(b, zeta)
    row_scale = np.asarray([zeta] * 6 + [1.0] * 4 + [curl_xy_scale] * 10 + [b] * 10)
    scaled = row_scale[:, None] * matrix
    singular = np.linalg.svd(scaled, compute_uv=False)
    raw_singular = np.linalg.svd(matrix, compute_uv=False)
    sign, logdet = np.linalg.slogdet(scaled)
    return {
        "zeta": zeta,
        "beta": beta,
        "basis_chart": basis,
        "row_scale_blocks": [zeta, 1.0, curl_xy_scale, b],
        "scaled_sigma_min": float(singular[-1]),
        "scaled_sigma_max": float(singular[0]),
        "scaled_inverse_norm": float(1.0 / singular[-1]),
        "raw_inverse_norm_in_declared_basis": float(1.0 / raw_singular[-1]),
        "scaled_log_abs_determinant": float(logdet),
        "scaled_determinant_sign": {"real": float(np.real(sign)), "imag": float(np.imag(sign))},
        "matrix_rank": int(np.linalg.matrix_rank(scaled)),
    }


def _eq123_scaled_logdet(zeta: float, beta: float) -> float:
    _, lambda1, _ = NEGATIVE._root_and_lambdas(complex(zeta, 0.0), beta)
    k1 = float(np.linalg.norm([zeta - beta * lambda1, -lambda1, -1.0j, 0.0j]))
    k2 = float(np.linalg.norm([0.0j, -1.0j * beta, zeta, 0.0j]))
    factor = zeta - (1.0 + beta) * lambda1
    speed = zeta * zeta - beta * beta
    logdet = (
        16.0 * np.log(abs(factor))
        + 10.0 * np.log(abs(speed))
        - np.log(8.0)
        - 16.0 * np.log(zeta)
        - 20.0 * np.log(abs(beta))
        - 10.0 * np.log(k1)
        - 10.0 * np.log(k2)
    )
    scales = [zeta] * 6 + [1.0] * 4 + [min(abs(beta), zeta)] * 10 + [abs(beta)] * 10
    return float(logdet + sum(np.log(scales)))


def build_artifact() -> dict[str, Any]:
    generic: list[dict[str, Any]] = []
    for exponent in POWER_PATHS:
        for zeta in ZETA_VALUES:
            beta = -(zeta**exponent)
            matrix, residual = _generic_matrix(zeta, beta)
            row = _scaled_record(matrix, zeta, beta, "unit_generic_eigenmodes")
            row["path_id"] = f"beta=-zeta^{exponent:g}"
            row["principal_mode_residual"] = residual
            row["eq123_scaled_logdet_abs_error"] = abs(
                row["scaled_log_abs_determinant"] - _eq123_scaled_logdet(zeta, beta)
            )
            generic.append(row)
    for ratio in FIXED_BETA_OVER_ZETA:
        for zeta in ZETA_VALUES:
            beta = -ratio * zeta
            matrix, residual = _generic_matrix(zeta, beta)
            row = _scaled_record(matrix, zeta, beta, "unit_generic_eigenmodes")
            row["path_id"] = f"abs(beta)/zeta={ratio:g}"
            row["principal_mode_residual"] = residual
            row["eq123_scaled_logdet_abs_error"] = abs(
                row["scaled_log_abs_determinant"] - _eq123_scaled_logdet(zeta, beta)
            )
            generic.append(row)

    jordan: list[dict[str, Any]] = []
    near_jordan: list[dict[str, Any]] = []
    for delta in ZETA_VALUES:
        beta = -delta
        matrix, residual = _jordan_matrix(beta)
        row = _scaled_record(matrix, delta, beta, "source_ode_consistent_jordan")
        row["path_id"] = "beta=-zeta; exact corrected Jordan chain"
        row["principal_mode_residual"] = residual
        expected_scaled_logdet = np.log(4.0) - 5.0 * np.log(1.0 + beta * beta)
        row["analytic_scaled_logdet_abs_error"] = abs(
            row["scaled_log_abs_determinant"] - expected_scaled_logdet
        )
        jordan.append(row)

        confluent, confluent_residual, confluent_det_offset = _near_jordan_matrix(delta)
        near_zeta = delta + delta**1.5
        near = _scaled_record(
            confluent, near_zeta, beta, "normalized_confluent_divided_difference"
        )
        near["path_id"] = "zeta=abs(beta)+abs(beta)^1.5; confluent chart"
        near["principal_mode_residual"] = confluent_residual
        near["confluent_reference_logdet_abs_offset"] = confluent_det_offset
        near_jordan.append(near)

    all_generic = generic
    checks = {
        "generic_path_eq123_determinants_match": max(
            row["eq123_scaled_logdet_abs_error"] for row in all_generic
        ) < 1.0e-8,
        "generic_scaled_maps_full_rank_and_bounded_on_declared_paths": all(
            row["matrix_rank"] == 30
            and row["scaled_sigma_min"] > 0.04
            and row["scaled_sigma_max"] < 3.0
            and row["principal_mode_residual"] < 1.0e-8
            for row in all_generic
        ),
        "exact_jordan_chain_matches_corrected_analytic_determinant": all(
            row["matrix_rank"] == 30
            and row["analytic_scaled_logdet_abs_error"] < 1.0e-8
            and row["scaled_sigma_min"] > 0.07
            and row["principal_mode_residual"] < 1.0e-12
            for row in jordan
        ),
        "near_jordan_confluent_chart_remains_full_rank": all(
            row["matrix_rank"] == 30
            and row["scaled_sigma_min"] > 0.06
            and row["principal_mode_residual"] < 1.0e-8
            for row in near_jordan
        ),
        "near_jordan_determinant_converges_to_registered_confluent_limit": abs(
            near_jordan[-1]["confluent_reference_logdet_abs_offset"]
        ) < abs(near_jordan[0]["confluent_reference_logdet_abs_offset"]),
    }
    status = "PASS_JOINT_REAL_PATH_SCREEN_ONLY" if all(checks.values()) else "FAIL_OR_UNRESOLVED_JOINT_REAL_PATH_SCREEN"
    rescaling = {
        "source_matrix_factorization": "S=D(beta,zeta)*C; inverse C^-1=S^-1*D",
        "row_scaling": "D=diag(zeta*I6, I4, min(abs(beta),zeta)*I10, abs(beta)*I10)",
        "curl_block_identity": "beta*E=diag(((zeta^2-beta^2)/(zeta*sqrt(zeta^2+beta^2)))*I10, i*I10)",
        "bounded_scaled_curl_factors": "min(abs(beta),zeta)*E_xy and abs(beta)*E_xz are bounded on positive-real beta<0,zeta>0 away from the coalesced generic basis; use the corrected Jordan/confluent chart at zeta=-beta",
        "generic_fixed_ratio_determinant_limit": "abs(det S)->(1/256)*[min(1,r)*abs(1-r^2)/(r*sqrt(1+r^2))]^10, r=abs(beta)/zeta != 1; it tends to 1/256 as r->0 or infinity, while the generic eigenbasis determinant vanishes at r=1 because its columns coalesce",
        "exact_jordan_determinant": "abs(det C_J)=4/(abs(beta)^26*(1+beta^2)^5); at zeta=abs(beta), abs(det S)=4/(1+beta^2)^5 -> 4 in the source ODE-consistent Jordan chart",
        "claim_boundary": "finite positive-real path screen and exact row-factor analysis only; no uniform complex-frequency Kreiss estimate or full parent closure",
    }
    source_hashes = {
        _relative(path): _hash(path)
        for path in (
            Path(__file__), TRANSITION_SCRIPT, NEGATIVE_SCRIPT, NEGATIVE_ARTIFACT,
            ZERO_SCRIPT, ZERO_ARTIFACT, BOUNDARY_SOURCE, PROJECTOR_SOURCE,
        )
    }
    major = {
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_JOINT_REAL_GLANCING_RESCALED_PATH_SCREEN",
        "topic": "core_curved_3p1",
        "closure_level": "PARTIAL",
        "what_is_closed": [
            "The determinant growth near beta=0,zeta=0 is separated into explicit source-row scale factors and a rescaled boundary matrix on the declared positive-real generic, exact-Jordan, and near-Jordan paths.",
            "The apparent generic-basis singularity at zeta=-beta is treated with the ODE-consistent Jordan chain; all sampled rescaled matrices remain full rank with finite inverse norms.",
        ],
        "what_remains_open": [
            "The path grid is not a proof of a common positive singular-value floor over every beta/zeta ratio or the complex closed right half-plane; a uniform chart-compatible Kreiss estimate remains unproved.",
            "The source mode-amplitude norm and normalization across generic/Jordan charts, imaginary-frequency glancing, high frequency, and full variable-coefficient CPBC evolution remain open.",
        ],
        "dependency_unlocked": "none; Core curved 3+1 remains PARTIAL and Gravity remains blocked",
        "equation_or_mapping": rescaling,
        "units": "Dimensionless frozen-coefficient Fourier-Laplace variables with tangential omega=1.",
        "derivation_class": "exact row-factor algebra and corrected Jordan determinant, cross-checked by finite positive-real path matrices",
        "observable": "rescaled 30x30 source boundary matrix singular values, determinant, and inverse norm in separately declared mode-basis charts",
        "data_role": "primary-literature formula reproduction and internal numerical path diagnostic; no empirical data or fitting",
        "verification_status": status,
        "claim_boundary": rescaling["claim_boundary"],
    }
    return {
        "schema_version": "core-curved-3p1-gh-rinne-joint-real-glancing-scale-v1",
        "artifact": "curved_3p1_gh_rinne_joint_real_glancing_scale",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "major_result_id": major["major_result_id"],
        "major_result": major,
        "closure_level": "PARTIAL",
        "MAJOR_RESULT_CLOSURE": "PARTIAL",
        "WHAT_IS_ACTUALLY_CLOSED": major["what_is_closed"],
        "WHAT_REMAINS_OPEN": major["what_remains_open"],
        "DEPENDENCY_UNLOCKED": major["dependency_unlocked"],
        "STATUS": status,
        "EQUATION_OR_MAPPING": rescaling,
        "VERIFICATION": {
            "checks": checks,
            "zeta_values": list(ZETA_VALUES),
            "generic_paths": generic,
            "exact_jordan_path": jordan,
            "near_jordan_confluent_path": near_jordan,
            "source_hashes": source_hashes,
            "source_reference": "https://arxiv.org/abs/gr-qc/0606053",
        },
        "CONTROLLING_BLOCKER": "uniform_chart_compatible_kreiss_bound_over_joint_beta_zeta_and_complex_frequency_domain_missing",
        "NEXT_ACTION": "Derive a chart-compatible lower bound for the rescaled matrix over the compactified positive-real ratio and then extend it to the imaginary-frequency boundary; do not infer Core-parent stability from path screens.",
        "CLAIM_BOUNDARY": major["claim_boundary"],
        "full_core_unlock": False,
        "gravity_unlock": False,
        "claim_promotion": False,
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifact": _relative(OUTPUT), "status": artifact["STATUS"], "checks": artifact["VERIFICATION"]["checks"], "generic_cases": len(artifact["VERIFICATION"]["generic_paths"])}, indent=2))
    return 0 if artifact["STATUS"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
