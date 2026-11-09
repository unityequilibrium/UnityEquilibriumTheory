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
SCREEN_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_complex_frequency_screen.py"
NEGATIVE_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_negative_shift_kreiss_symbol.py"
JOINT_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_joint_real_kreiss_operator.py"
NEGATIVE_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_negative_shift_kreiss_symbol.json"
BOUNDARY_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py"
PROJECTOR_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_high_frequency_transfer_endpoint.json"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCREEN = _load("_uet_rinne_high_frequency_screen", SCREEN_SCRIPT)
MODE = SCREEN.NEGATIVE.MODE
BASELINE = SCREEN.NEGATIVE.BASELINE
JOINT = SCREEN.JOINT
BETA_VALUES = SCREEN.HIGH_SWEEP_BETA_VALUES
RADII = (1.0e3, 1.0e5, 1.0e7)
ANGLES = SCREEN.HIGH_ANGLES
DETERMINANT_LOG_LIMIT = 1.0e-10
NORM_CANDIDATE_LIMIT = 1.0e-12


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _limit_modes(beta: float, phase: complex = 1.0 + 0.0j):
    # The common phase is zeta/|zeta| for the first two normalized families.
    return (
        (phase * np.asarray([1.0, 1.0, 0.0, 0.0], dtype=complex) / np.sqrt(2.0), -1.0 / (1.0 - beta)),
        (phase * np.asarray([0.0, 0.0, 1.0, 0.0], dtype=complex), 1.0 / beta),
        (np.asarray([0.0, 0.0, 0.0, 1.0], dtype=complex), 1.0 / beta),
    )


def _limit_boundary_column(
    beta: float, value: np.ndarray, normal_derivative_ratio: float, component: int
) -> np.ndarray:
    tensor = np.zeros((4, 4), dtype=complex)
    i, j = MODE.PAIRS[component]
    tensor[i, j] = tensor[j, i] = 1.0
    tensor /= np.sqrt(MODE.TENSOR_WEIGHTS[component])

    pi = value[0] * tensor
    phi = np.stack([entry * tensor for entry in value[1:]])
    pi_gradient = np.zeros((3, 4, 4), dtype=complex)
    phi_gradient = np.zeros((3, 3, 4, 4), dtype=complex)
    pi_gradient[0] = normal_derivative_ratio * value[0] * tensor
    phi_gradient[0] = np.stack(
        [normal_derivative_ratio * entry * tensor for entry in value[1:]]
    )

    residuals = []
    for part in ("real", "imag"):
        pick = lambda array: getattr(array, part)
        residuals.append(
            MODE.BOUNDARY.gh_linear_boundary_residuals(
                metric_perturbation=np.zeros((4, 4)),
                pi_perturbation=pick(pi),
                phi_perturbation=pick(phi),
                metric_gradient=np.zeros((3, 4, 4)),
                pi_gradient=pick(pi_gradient),
                phi_gradient=pick(phi_gradient),
                normal=SCREEN.NEGATIVE.NORMAL,
                lapse=1.0,
                normal_shift=-beta,
                gamma2=SCREEN.NEGATIVE.GAMMA2,
            )
        )
    real, imag = residuals
    complex_value = lambda name: np.asarray(getattr(real, name)) + 1.0j * np.asarray(
        getattr(imag, name)
    )
    constraint = complex_value("constraint_incoming")
    physical = complex_value("physical_weyl_incoming")
    gauge = complex_value("gauge_incoming")
    u2_curl = complex_value("u2_curl_incoming")

    normal_maps = MODE.BOUNDARY.gh_boundary_normal_maps(SCREEN.NEGATIVE.NORMAL)
    projectors = MODE.PROJECTORS.build_gh_boundary_projectors(SCREEN.NEGATIVE.NORMAL)
    gauge_basis = np.linalg.svd(projectors.gauge)[0]
    gauge_basis = gauge_basis[:, : projectors.ranks["gauge"]]
    top_rows = np.concatenate(
        (
            constraint,
            normal_maps["physical"] @ BASELINE._pack_symmetric(physical),
            gauge_basis.conj().T @ BASELINE._pack_symmetric(gauge),
        )
    )
    u2_rows = np.concatenate(
        (
            -BASELINE._pack_symmetric(u2_curl[0]),
            BASELINE._pack_symmetric(u2_curl[1]),
        )
    )
    # Scaled constraint/physical/curl rows retain only normal derivatives;
    # unscaled gauge rows retain the fields themselves in this limit.
    return np.concatenate((top_rows, u2_rows))


def _limit_matrices(beta: float, phase: complex = 1.0 + 0.0j) -> tuple[np.ndarray, np.ndarray]:
    boundary_columns: list[np.ndarray] = []
    state_columns: list[np.ndarray] = []
    for value, derivative_ratio in _limit_modes(beta, phase):
        for component in range(10):
            boundary_columns.append(
                _limit_boundary_column(beta, value, derivative_ratio, component)
            )
            state_columns.append(JOINT._state_column(value, component))

    boundary = SCREEN.ROW @ np.column_stack(boundary_columns) @ SCREEN.COLUMN
    state = np.column_stack(state_columns) @ SCREEN.COLUMN
    return boundary, state


def _limit_operator(beta: float, phase: complex = 1.0 + 0.0j) -> tuple[np.ndarray, np.ndarray]:
    boundary, state = _limit_matrices(beta, phase)
    return boundary, SCREEN._state_operator(boundary, state)


def build_artifact() -> dict[str, Any]:
    endpoint_cases: list[dict[str, Any]] = []
    matrix_convergence_cases: list[dict[str, Any]] = []
    phase_errors: list[dict[str, Any]] = []
    limit_cache: dict[float, tuple[np.ndarray, np.ndarray]] = {}

    for beta in BETA_VALUES:
        boundary, state_operator = _limit_operator(beta)
        limit_cache[beta] = (boundary, state_operator)
        sign, log_abs_det = np.linalg.slogdet(boundary)
        expected_log_abs_det = float(
            np.log(256.0) - 20.0 * np.log(abs(beta)) - 6.0 * np.log(1.0 - beta)
        )
        singular_values = np.linalg.svd(state_operator, compute_uv=False)
        endpoint_cases.append(
            {
                "beta": beta,
                "boundary_shape": list(boundary.shape),
                "state_operator_shape": list(state_operator.shape),
                "boundary_minimum_singular_value": float(
                    np.linalg.svd(boundary, compute_uv=False)[-1]
                ),
                "boundary_log_abs_determinant": float(log_abs_det),
                "eq123_asymptotic_log_abs_determinant": expected_log_abs_det,
                "eq123_asymptotic_log_error": abs(float(log_abs_det) - expected_log_abs_det),
                "state_operator_norm_2": float(singular_values[0]),
                "candidate_norm_1_minus_beta": 1.0 - beta,
                "candidate_norm_abs_error": abs(float(singular_values[0]) - (1.0 - beta)),
                "boundary_determinant_nonzero": bool(sign != 0.0),
                "all_entries_finite": bool(
                    np.all(np.isfinite(boundary)) and np.all(np.isfinite(state_operator))
                ),
            }
        )

        for angle in ANGLES:
            phase = np.exp(1.0j * angle)
            _, phased_operator = _limit_operator(beta, phase)
            phase_error = float(
                np.linalg.norm(phased_operator - state_operator, ord="fro")
                / np.linalg.norm(state_operator, ord="fro")
            )
            phase_errors.append(
                {"beta": beta, "angle": float(angle), "relative_operator_error": phase_error}
            )

        for radius in RADII:
            rows = []
            for angle in ANGLES:
                zeta = radius * np.exp(1.0j * angle)
                finite_operator, mode_residual, determinant_error = SCREEN._generic_transfer(
                    zeta, beta
                )
                relative_error = float(
                    np.linalg.norm(finite_operator - state_operator, ord="fro")
                    / np.linalg.norm(state_operator, ord="fro")
                )
                rows.append(
                    {
                        "angle": float(angle),
                        "relative_frobenius_error_to_limit": relative_error,
                        "principal_mode_residual": mode_residual,
                        "finite_matrix_eq123_log_error": determinant_error,
                    }
                )
            matrix_convergence_cases.append(
                {
                    "beta": beta,
                    "radius": radius,
                    "case_count": len(rows),
                    "maximum_relative_frobenius_error": max(
                        row["relative_frobenius_error_to_limit"] for row in rows
                    ),
                    "direction_cases": rows,
                }
            )

    max_det_error = max(row["eq123_asymptotic_log_error"] for row in endpoint_cases)
    max_norm_candidate_error = max(row["candidate_norm_abs_error"] for row in endpoint_cases)
    max_phase_error = max(row["relative_operator_error"] for row in phase_errors)
    max_last_radius_matrix_error = max(
        row["maximum_relative_frobenius_error"]
        for row in matrix_convergence_cases
        if row["radius"] == max(RADII)
    )
    matrix_error_by_beta = {
        beta: [
            row["maximum_relative_frobenius_error"]
            for row in matrix_convergence_cases
            if row["beta"] == beta
        ]
        for beta in BETA_VALUES
    }
    checks = {
        "all_endpoint_matrices_are_finite_with_expected_shapes": all(
            row["all_entries_finite"]
            and row["boundary_shape"] == [30, 30]
            and row["state_operator_shape"] == [40, 30]
            for row in endpoint_cases
        ),
        "analytic_eq123_endpoint_determinant_matches_direct_matrix": max_det_error
        < DETERMINANT_LOG_LIMIT,
        "endpoint_matrices_are_nonsingular_on_sampled_beta_grid": all(
            row["boundary_determinant_nonzero"]
            and row["boundary_minimum_singular_value"] > 0.0
            for row in endpoint_cases
        ),
        "candidate_norm_matches_on_exploratory_beta_grid": max_norm_candidate_error
        < NORM_CANDIDATE_LIMIT,
        "asymptotic_phase_cancels_from_the_state_transfer": max_phase_error < 1.0e-12,
        "finite_frequency_matrices_converge_to_endpoint_on_screen": all(
            right < left for errors in matrix_error_by_beta.values() for left, right in zip(errors, errors[1:])
        ) and max_last_radius_matrix_error < 5.0e-7,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    status = (
        "PASS_EXACT_HIGH_FREQUENCY_TRANSFER_MATRIX_ENDPOINT"
        if all(checks.values())
        else "FAIL_OR_UNRESOLVED_HIGH_FREQUENCY_TRANSFER_MATRIX_ENDPOINT"
    )
    blocker = "zero_frequency_transfer_extension_and_compactified_continuous_transfer_bound_unproved"
    claim_boundary = (
        "Exact source-matched high-frequency endpoint matrix construction for the frozen-coefficient "
        "standard-GR negative-normal-shift lane, with an analytic nonzero determinant limit. The norm "
        "identity ||T_infinity||_2=1-beta is only numerically checked on an exploratory beta grid; "
        "this is not a continuous all-frequency Kreiss proof or Core-parent closure."
    )
    source_paths = (
        Path(__file__), SCREEN_SCRIPT, NEGATIVE_SCRIPT, JOINT_SCRIPT, NEGATIVE_ARTIFACT,
        BOUNDARY_SOURCE, PROJECTOR_SOURCE,
    )
    source_hashes = {_relative(path): _sha256(path) for path in source_paths}
    what_closed = [
        "For every fixed beta in (-1,0), the normalized decaying modes have exact leading limits v1=(zeta/|zeta|)*(1,1,0,0)/sqrt(2), v2=(zeta/|zeta|)*(0,0,1,0), v3=(0,0,0,1), with lambda1/zeta -> -1/(1-beta) and lambda2/zeta=1/beta.",
        "Substitution into the registered scaled GH boundary rows defines finite matrices C_infinity(beta) and W_infinity(beta); the common phase cancels in T_infinity=W_infinity*C_infinity^{-1}.",
        "The exact determinant asymptote is |det C_infinity|=2^8/(|beta|^20*(1-beta)^6)>0 for each fixed beta in (-1,0), so the endpoint boundary matrix is invertible throughout that open lane.",
        f"Direct construction and finite-frequency convergence were checked on {len(endpoint_cases)} beta values and {len(matrix_convergence_cases) * len(ANGLES)} complex-frequency points. The operator norm matches 1-beta numerically on this grid, not as a proved identity.",
    ]
    what_open = [
        "A symbolic proof of ||T_infinity||_2=1-beta is open; the singular norm equality is only a numerical candidate.",
        "The zeta->0 transfer extension and a uniform transfer bound over all finite frequencies for each fixed beta remain open.",
        "No family-uniform Kreiss constant near beta endpoints, full variable-coefficient GH boundary evolution, tangential/corner treatment, observable mapping, or Core-parent closure is claimed.",
    ]
    major = {
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_HIGH_FREQUENCY_TRANSFER_MATRIX_ENDPOINT",
        "topic": "core_curved_3p1",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": what_closed,
        "what_remains_open": what_open,
        "equation_or_mapping": {
            "lambda1_ratio_limit": "lambda1/zeta -> -1/(1-beta)",
            "lambda2_ratio": "lambda2/zeta = 1/beta",
            "normalized_mode_limits": [
                "v1=(zeta/|zeta|)*(1,1,0,0)/sqrt(2)",
                "v2=(zeta/|zeta|)*(0,0,1,0)",
                "v3=(0,0,0,1)",
            ],
            "endpoint_transfer": "T_infinity(beta)=W_infinity(beta)*C_infinity(beta)^-1",
            "endpoint_determinant": "|det C_infinity|=2^8/(|beta|^20*(1-beta)^6)",
            "operator_norm_candidate": "||T_infinity||_2=1-beta; exploratory numerical check only",
        },
        "units": "Dimensionless frozen-coefficient Fourier-Laplace variables; tangential frequency normalized to one.",
        "derivation_class": "analytic leading-mode and scaled-boundary-map limit; determinant inherited from source-matched Eq. (123); numerical matrix convergence cross-check",
        "observable": "30x30 high-frequency boundary matrix, 40x30 state-transfer endpoint, determinant log error, singular norm, and finite-frequency matrix convergence",
        "data_role": "internal standard-GR frozen-coefficient diagnostic; no empirical data, fitting, or holdout",
        "evidence_artifacts": [
            {"path": _relative(Path(__file__)), "sha256": source_hashes[_relative(Path(__file__))]},
            {"path": _relative(SCREEN_SCRIPT), "sha256": source_hashes[_relative(SCREEN_SCRIPT)]},
            {"path": _relative(NEGATIVE_ARTIFACT), "sha256": source_hashes[_relative(NEGATIVE_ARTIFACT)]},
        ],
        "verification_status": status,
        "open_blockers": [blocker, "analytic_high_frequency_operator_norm_identity_unproved", "full_variable_coefficient_GH_boundary_and_Core_parent_gates_remain_open"],
        "dependency_unlocked": "none; Core parent remains PARTIAL and Gravity remains blocked",
        "claim_boundary": claim_boundary,
    }
    return {
        "schema_version": "core-curved-3p1-gh-rinne-high-frequency-transfer-endpoint-v1",
        "artifact": "curved_3p1_gh_rinne_high_frequency_transfer_endpoint",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "major_result_id": major["major_result_id"],
        "major_result": major,
        "closure_level": "CLOSED_FOR_LANE",
        "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE",
        "WHAT_IS_ACTUALLY_CLOSED": what_closed,
        "WHAT_REMAINS_OPEN": what_open,
        "DEPENDENCY_UNLOCKED": major["dependency_unlocked"],
        "STATUS": status,
        "status": status,
        "EQUATION_OR_MAPPING": major["equation_or_mapping"],
        "VERIFICATION": {
            "checks": checks,
            "beta_values": list(BETA_VALUES),
            "endpoint_cases": endpoint_cases,
            "phase_independence_angles": [float(angle) for angle in ANGLES],
            "phase_independence_cases": phase_errors,
            "finite_frequency_radii": list(RADII),
            "finite_frequency_angles": [float(angle) for angle in ANGLES],
            "finite_frequency_matrix_convergence_cases": matrix_convergence_cases,
            "maximum_eq123_asymptotic_log_error": max_det_error,
            "maximum_norm_candidate_abs_error": max_norm_candidate_error,
            "maximum_phase_relative_error": max_phase_error,
            "maximum_last_radius_relative_matrix_error": max_last_radius_matrix_error,
            "exploratory_grid_design": {
                "status": "EXPLORATORY_NOT_PREREGISTERED",
                "grid_role": "finite matrix-convergence cross-check after preliminary diagnostic work",
                "tolerance_origin": "numerical thresholds declared after preliminary preview; not an independent acceptance threshold",
            },
            "source_hashes": source_hashes,
            "primary_source": {
                "locator": "https://arxiv.org/abs/gr-qc/0606053",
                "sections": ["3.1", "3.2"],
                "equations": ["(51)-(55)", "(69)-(74)", "(109)-(123)"],
                "note": "The published Jordan normalization discrepancy remains separately visible; the exact endpoint construction here concerns |zeta|->infinity, not the Jordan point.",
            },
        },
        "CONTROLLING_BLOCKER": blocker,
        "NEXT_ACTION": "Derive the zeta->0 transfer extension. Then reconcile the normalized source-matrix determinant condition with the Kreiss equivalence and prove or interval-certify the compactified finite-frequency bound for each fixed beta.",
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
                "closure_level": artifact["closure_level"],
                "checks": artifact["VERIFICATION"]["checks"],
                "beta_cases": len(artifact["VERIFICATION"]["endpoint_cases"]),
                "finite_frequency_cases": sum(
                    row["case_count"]
                    for row in artifact["VERIFICATION"]["finite_frequency_matrix_convergence_cases"]
                ),
                "max_det_log_error": artifact["VERIFICATION"]["maximum_eq123_asymptotic_log_error"],
                "max_norm_candidate_error": artifact["VERIFICATION"]["maximum_norm_candidate_abs_error"],
                "max_matrix_error_at_largest_radius": artifact["VERIFICATION"]["maximum_last_radius_relative_matrix_error"],
            },
            indent=2,
        )
    )
    return 0 if all(artifact["VERIFICATION"]["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
