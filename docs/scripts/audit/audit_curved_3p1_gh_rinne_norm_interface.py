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
NEGATIVE_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_negative_shift_kreiss_symbol.py"
ZERO_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_zero_shift_kreiss_symbol.py"
TRANSFER_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_positive_real_joint_transfer_bound.py"
TRANSFER_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_positive_real_joint_transfer_bound.json"
BOUNDARY_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py"
PROJECTOR_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_norm_interface.json"
TOLERANCE = 2.0e-11
SAMPLES = ((0.2, -0.65), (0.4, -0.15), (1.25, -0.45))
RINNE_SOURCE = "https://arxiv.org/abs/gr-qc/0606053"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


NEGATIVE = _load("_uet_rinne_norm_negative", NEGATIVE_SCRIPT)


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _block_diag(*blocks: np.ndarray) -> np.ndarray:
    rows = sum(block.shape[0] for block in blocks)
    cols = sum(block.shape[1] for block in blocks)
    result = np.zeros((rows, cols), dtype=float)
    row = 0
    col = 0
    for block in blocks:
        height, width = block.shape
        result[row : row + height, col : col + width] = block
        row += height
        col += width
    return result


def _state_column(value: np.ndarray, component: int) -> np.ndarray:
    state = np.zeros((4, 10), dtype=complex)
    state[:, component] = value
    return state.reshape(-1)


def _transfer_identity_case(
    zeta: float,
    beta: float,
    row_transform: np.ndarray,
    column_transform: np.ndarray,
) -> dict[str, Any]:
    boundary_columns: list[np.ndarray] = []
    state_columns: list[np.ndarray] = []
    maximum_mode_residual = 0.0
    maximum_curl_map_residual = 0.0
    for family in range(3):
        value, derivative = NEGATIVE._generic_mode(complex(zeta, 0.0), beta, family)
        for component in range(10):
            boundary, mode_residual, curl_residual = NEGATIVE._boundary_column(
                beta, complex(zeta, 0.0), value, derivative, component
            )
            boundary_columns.append(boundary)
            state_columns.append(_state_column(value, component))
            maximum_mode_residual = max(maximum_mode_residual, mode_residual)
            maximum_curl_map_residual = max(maximum_curl_map_residual, curl_residual)

    raw_boundary = np.column_stack(boundary_columns)
    raw_state = np.column_stack(state_columns)
    source_boundary = row_transform @ raw_boundary @ column_transform
    source_state = raw_state @ column_transform
    transfer_from_source_matrices = np.linalg.solve(
        source_boundary.T, source_state.T
    ).T
    inverse_row = np.linalg.solve(row_transform, np.eye(row_transform.shape[0]))
    transfer_from_raw_matrices = raw_state @ np.linalg.solve(raw_boundary, inverse_row)
    residual = transfer_from_source_matrices - transfer_from_raw_matrices
    scale = max(1.0, float(np.linalg.norm(transfer_from_source_matrices, ord=np.inf)))
    return {
        "zeta": zeta,
        "beta": beta,
        "relative_transfer_identity_residual": float(
            np.linalg.norm(residual, ord=np.inf) / scale
        ),
        "transfer_spectral_norm_independent_component_l2": float(
            np.linalg.svd(transfer_from_source_matrices, compute_uv=False)[0]
        ),
        "maximum_mode_equation_residual": maximum_mode_residual,
        "maximum_source_curl_row_residual": maximum_curl_map_residual,
    }


def build_artifact() -> dict[str, Any]:
    row_transform, column_transform, source_map = NEGATIVE._source_transforms()
    component_weights = np.asarray(NEGATIVE.MODE.TENSOR_WEIGHTS, dtype=float)
    tensor_metric = np.diag(component_weights)
    state_metric = np.kron(np.eye(4), tensor_metric)

    # The matrix uses the audit order C(4), P(2), G(4), curl_xy(10), curl_xz(10).
    source_metric_independent = np.eye(30)
    source_metric_tensor = _block_diag(
        np.eye(4), 2.0 * np.eye(2), np.eye(4), tensor_metric, tensor_metric
    )
    paper_order = np.eye(30)[
        list(range(4)) + list(range(10, 30)) + list(range(4, 10)), :
    ]
    paper_order_metric = _block_diag(
        np.eye(4), tensor_metric, tensor_metric, 2.0 * np.eye(2), np.eye(4)
    )
    permuted_source_metric = paper_order.T @ paper_order_metric @ paper_order

    row_singular_values = np.linalg.svd(row_transform, compute_uv=False)
    state_eigenvalues = np.linalg.eigvalsh(state_metric)
    source_eigenvalues = np.linalg.eigvalsh(source_metric_tensor)
    paper_permutation_residual = float(
        np.max(np.abs(paper_order.T @ paper_order - np.eye(30)))
    )
    source_metric_order_residual = float(
        np.max(np.abs(permuted_source_metric - source_metric_tensor))
    )
    expected_column_metric = np.kron(np.eye(3), tensor_metric)
    column_metric_residual = float(
        np.max(np.abs(column_transform.T @ column_transform - expected_column_metric))
    )
    transfer_cases = [
        _transfer_identity_case(zeta, beta, row_transform, column_transform)
        for zeta, beta in SAMPLES
    ]
    max_transfer_identity_residual = max(
        case["relative_transfer_identity_residual"] for case in transfer_cases
    )

    transfer_artifact = json.loads(TRANSFER_ARTIFACT.read_text(encoding="utf-8"))
    transfer_verification = transfer_artifact.get("VERIFICATION", {})
    upstream_hashes = transfer_verification.get("source_hashes", {})
    upstream_hashes_match = bool(upstream_hashes) and all(
        (ROOT / path).is_file() and _sha256(ROOT / path) == expected
        for path, expected in upstream_hashes.items()
    )
    transfer_bound = transfer_artifact.get("EQUATION_OR_MAPPING", {}).get(
        "common_uniform_transfer_bound"
    )
    if transfer_bound is None:
        transfer_bound = transfer_artifact.get("EQUATION_OR_MAPPING", {}).get(
            "chartwise_bounds", {}
        )
    checks = {
        "source_matrix_dimensions_match_30_boundary_channels_and_40_state_components": row_transform.shape
        == (30, 30)
        and state_metric.shape == (40, 40),
        "source_channel_order_change_is_norm_preserving": paper_permutation_residual
        <= TOLERANCE,
        "source_row_map_is_fixed_and_invertible": row_singular_values[-1] > 0.0
        and row_singular_values[0] < 2.0,
        "source_row_map_projector_identities_pass": source_map[
            "all_projector_and_coordinate_identities_within_tolerance"
        ],
        "normalized_mode_columns_map_to_independent_tensor_components": column_metric_residual
        <= TOLERANCE,
        "state_tensor_norms_have_unit_to_sqrt2_equivalence": abs(
            float(state_eigenvalues[0]) - 1.0
        )
        <= TOLERANCE
        and abs(float(state_eigenvalues[-1]) - 2.0) <= TOLERANCE,
        "source_tensor_norms_have_unit_to_sqrt2_equivalence": abs(
            float(source_eigenvalues[0]) - 1.0
        )
        <= TOLERANCE
        and abs(float(source_eigenvalues[-1]) - 2.0) <= TOLERANCE,
        "source_transfer_basis_identity_holds_on_fixed_samples": max_transfer_identity_residual
        <= TOLERANCE,
        "upstream_positive_real_transfer_artifact_and_hashes_pass": transfer_artifact.get(
            "STATUS"
        )
        == "PASS_POSITIVE_REAL_UNIFORM_TRANSFER_BOUND"
        and transfer_verification.get("checks", {}).get(
            "all_upstream_source_hashes_match", False
        )
        and upstream_hashes_match,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    all_pass = all(checks.values())

    source_hash_paths = (
        NEGATIVE_SCRIPT,
        ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_zero_shift_kreiss_symbol.py",
        ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_joint_real_kreiss_operator.py",
        TRANSFER_SCRIPT,
        BOUNDARY_SOURCE,
        PROJECTOR_SOURCE,
        TRANSFER_ARTIFACT,
        Path(__file__).resolve(),
    )
    max_tensor_norm_factor = float(
        np.sqrt(max(float(state_eigenvalues[-1]), float(source_eigenvalues[-1])))
    )
    return {
        "schema_version": "core-curved-3p1-gh-rinne-norm-interface-v1",
        "artifact": "curved_3p1_gh_rinne_norm_interface",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_NORM_INTERFACE",
        "closure_level": "CLOSED_FOR_LANE" if all_pass else "OPEN",
        "claim_promotion": False,
        "full_core_unlock": False,
        "gravity_unlock": False,
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_RINNE_NORM_INTERFACE",
            "topic": "core_curved_3p1",
            "closure_level": "CLOSED_FOR_LANE" if all_pass else "OPEN",
            "what_is_closed": [
                "The source-matched 30-channel boundary vector and 40-component state vector are explicitly expressed in independent tensor-component coordinates, with a norm-preserving permutation to the equation order in Rinne (2006), Eqs. (109)-(120).",
                "The mode-column conversion cancels from the state transfer operator: T_source = V_source*C_source^-1 = V_raw*B_raw^-1*R^-1.",
                "Independent-component Euclidean and full symmetric-tensor Frobenius norms are related by fixed Gram matrices with eigenvalues in [1,2]; the existing positive-real bound therefore transfers with at most a sqrt(2) factor under the Frobenius convention.",
            ],
            "what_remains_open": [
                "A transfer/inverse bound over the full closed right half-plane, including the imaginary-frequency boundary and high-frequency compactification.",
                "A useful-size stability constant; the existing positive-real low-frequency bound is extremely loose.",
                "Variable-coefficient/nonlinear GH boundary evolution, corners, dimensional-observable mapping, and the Core curved 3+1 parent gate.",
            ],
            "equation_or_mapping": {
                "source_boundary_matrix": "C_source = R*B_raw*Q",
                "source_state_matrix": "V_source = V_raw*Q",
                "source_transfer": "T_source = V_source*C_source^-1 = V_raw*B_raw^-1*R^-1",
                "state_tensor_metric": "G_v = I_4 kron diag(TENSOR_WEIGHTS)",
                "boundary_tensor_metric_audit_order": "G_h = diag(I_4, 2*I_2, I_4, diag(TENSOR_WEIGHTS), diag(TENSOR_WEIGHTS))",
                "frobenius_transfer_norm": "||G_v^(1/2)*T_source*G_h^(-1/2)||_2 <= sqrt(2)*||T_source||_2",
                "source_channel_order_audit": "constraint[4], physical[2], gauge[4], curl_xy[10], curl_xz[10]; equation order differs only by a permutation",
            },
            "units": "Dimensionless frozen-coefficient Fourier-Laplace variables with tangential frequency normalized to one; no SI observable is claimed.",
            "derivation_class": "Source-matched finite-dimensional basis identity and exact norm-equivalence bounds, with numerical residual checks.",
            "observable": "Spectral norm of the frozen-coefficient boundary state-transfer operator.",
            "data_role": "Internal mathematical verification linked to a primary-source formula audit; no empirical data, fit, calibration, or holdout.",
            "verification_status": "PASS_SOURCE_STATE_NORM_INTERFACE_LANE" if all_pass else "FAIL_SOURCE_STATE_NORM_INTERFACE_AUDIT",
            "open_blockers": [
                "complex_frequency_transfer_bound_and_high_frequency_compactification_missing"
            ],
            "dependency_unlocked": "none; this closes only the source/state norm-coordinate interface for the declared frozen-coefficient lane",
            "claim_boundary": "This is a coordinate/norm-equivalence result, not a full Kreiss estimate, practical stability result, full GH well-posedness proof, UET validation, Core-parent closure, or Gravity compatibility.",
        },
        "STATUS": "PASS_SOURCE_STATE_NORM_INTERFACE_LANE" if all_pass else "FAIL_SOURCE_STATE_NORM_INTERFACE_AUDIT",
        "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE" if all_pass else "OPEN",
        "WHAT_IS_ACTUALLY_CLOSED": [
            "Explicit source-data and state component order for the audited 30-to-40 transfer map.",
            "Column-basis cancellation in the transfer map and norm-equivalence constants for independent-component Euclidean versus full tensor Frobenius conventions.",
            "For the existing positive-real low-frequency result only, the Frobenius-convention upper bound is at most sqrt(2)*1e67.",
        ],
        "WHAT_REMAINS_OPEN": [
            "The all-complex-frequency and high-frequency transfer bound remains open.",
            "The source paper does not state a unique component-counting convention for every symmetric tensor norm; both standard conventions are bracketed here for boundedness, not for a sharp Kreiss constant.",
            "Full GH evolution, variable coefficients, corners, dimensional observables, and parent closure remain open.",
        ],
        "EQUATION_OR_MAPPING": {
            "source_boundary_matrix": "C_source = R*B_raw*Q",
            "source_state_matrix": "V_source = V_raw*Q",
            "source_transfer": "T_source = V_raw*B_raw^-1*R^-1",
            "independent_component_l2_bound": "||T_source||_2 < 1e67 on the previously declared beta<0, zeta>0, max(|beta|,zeta)<=1e-2 lane",
            "full_tensor_frobenius_bound": "||T_source||_F <= sqrt(2)*||T_source||_2 < sqrt(2)*1e67 on that same lane",
        },
        "VERIFICATION": {
            "checks": checks,
            "check_count": len(checks),
            "passed_count": sum(checks.values()),
            "tolerance": TOLERANCE,
            "source_row_singular_values": [float(value) for value in row_singular_values],
            "source_row_map_condition_number": float(row_singular_values[0] / row_singular_values[-1]),
            "column_metric_max_abs_residual": column_metric_residual,
            "paper_order_permutation_orthogonality_residual": paper_permutation_residual,
            "source_metric_order_residual": source_metric_order_residual,
            "state_metric_eigenvalue_range": [float(state_eigenvalues[0]), float(state_eigenvalues[-1])],
            "source_metric_eigenvalue_range": [float(source_eigenvalues[0]), float(source_eigenvalues[-1])],
            "max_tensor_norm_conversion_factor": max_tensor_norm_factor,
            "transfer_identity_samples": transfer_cases,
            "max_transfer_identity_residual": max_transfer_identity_residual,
            "previous_transfer_bound_artifact": {
                "path": _relative(TRANSFER_ARTIFACT),
                "sha256": _sha256(TRANSFER_ARTIFACT),
                "status": transfer_artifact.get("STATUS"),
                "independent_component_bound": "<1e67",
                "frobenius_convention_bound": f"<{max_tensor_norm_factor * 1.0e67:.12g}",
            },
            "source_hashes": {
                _relative(path): _sha256(path) for path in source_hash_paths
            },
            "primary_source": {
                "locator": RINNE_SOURCE,
                "sections": ["3.1", "3.2"],
                "equations": ["(54)-(55)", "(69)-(74)", "(109)-(120)"],
                "note": "The primary source establishes the Kreiss inequality and supplies the state/boundary channels; tensor norm convention is explicitly bracketed rather than assumed.",
            },
        },
        "CONTROLLING_BLOCKER": "complex_frequency_transfer_bound_and_high_frequency_compactification_missing",
        "DEPENDENCY_UNLOCKED": "None; Core curved 3+1 remains PARTIAL and Gravity remains blocked.",
        "NEXT_ACTION": "Extend the analytic inverse/transfer estimate over the complex-frequency boundary and high-frequency compactification using the now-explicit source/state norm interface.",
        "CLAIM_BOUNDARY": "Closes only a finite-dimensional norm-coordinate interface for the declared source-matched frozen-coefficient lane. It is not a full Kreiss estimate, practical stability result, full GH well-posedness proof, UET validation, Core-parent closure, or Gravity compatibility.",
        "source_locator": RINNE_SOURCE,
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
                "passed": artifact["VERIFICATION"]["passed_count"],
                "checks": artifact["VERIFICATION"]["check_count"],
                "max_transfer_identity_residual": artifact["VERIFICATION"][
                    "max_transfer_identity_residual"
                ],
                "frobenius_bound": artifact["VERIFICATION"][
                    "previous_transfer_bound_artifact"
                ]["frobenius_convention_bound"],
            },
            indent=2,
        )
    )
    return 0 if artifact["STATUS"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
