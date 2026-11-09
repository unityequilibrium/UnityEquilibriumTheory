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
SCALE_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_joint_real_glancing_scale.py"
SCALE_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_joint_real_glancing_scale.json"
TRANSITION_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_negative_shift_zero_transition.py"
NEGATIVE_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_negative_shift_kreiss_symbol.py"
NEGATIVE_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_negative_shift_kreiss_symbol.json"
ZERO_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_zero_shift_kreiss_symbol.py"
ZERO_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_zero_shift_kreiss_symbol.json"
BOUNDARY_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py"
PROJECTOR_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_joint_real_kreiss_operator.json"
SCALES = (1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5)
GRID_POINTS_PER_AXIS = 5
REFERENCE_ZETA = 1.0e-8


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCALE_AUDIT = _load("_uet_joint_kreiss_scale_audit", SCALE_SCRIPT)
TRANSITION = SCALE_AUDIT.TRANSITION
NEGATIVE = SCALE_AUDIT.NEGATIVE
ROW, COLUMN, _ = NEGATIVE._source_transforms()
ZERO_ROW, ZERO_COLUMN, _ = NEGATIVE.BASELINE._source_component_basis_map()


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _state_column(value: np.ndarray, component: int) -> np.ndarray:
    state = np.zeros((4, 10), dtype=complex)
    state[:, component] = value
    return state.reshape(-1)


def _generic_matrices(zeta: float, beta: float) -> tuple[np.ndarray, np.ndarray, float]:
    boundary, _ = TRANSITION._source_matrices(
        zeta, beta, (ROW, COLUMN), (ZERO_ROW, ZERO_COLUMN)
    )
    state_columns: list[np.ndarray] = []
    maximum_mode_residual = 0.0
    for family in range(3):
        value, derivative = NEGATIVE._generic_mode(complex(zeta, 0.0), beta, family)
        for component in range(10):
            _, residual, _ = NEGATIVE._boundary_column(
                beta, complex(zeta, 0.0), value, derivative, component
            )
            maximum_mode_residual = max(maximum_mode_residual, residual)
            state_columns.append(_state_column(value, component))
    state = np.column_stack(state_columns) @ COLUMN
    return boundary, state, maximum_mode_residual


def _jordan_matrices(zeta: float) -> tuple[np.ndarray, np.ndarray, float]:
    beta = -zeta
    boundary_columns: list[np.ndarray] = []
    state_columns: list[np.ndarray] = []
    maximum_mode_residual = 0.0
    for family in range(3):
        value, derivative = NEGATIVE._degenerate_mode(
            beta, family, "source_ode_consistent"
        )
        for component in range(10):
            boundary, residual, _ = NEGATIVE._boundary_column(
                beta, zeta, value, derivative, component
            )
            boundary_columns.append(boundary)
            state_columns.append(_state_column(value, component))
            maximum_mode_residual = max(maximum_mode_residual, residual)
    boundary = ROW @ np.column_stack(boundary_columns) @ COLUMN
    state = np.column_stack(state_columns) @ COLUMN
    return boundary, state, maximum_mode_residual


def _confluent_matrices(zeta: float, beta: float) -> tuple[np.ndarray, np.ndarray, float]:
    spectral = complex(zeta, 0.0)
    _, lambda1, lambda2 = NEGATIVE._root_and_lambdas(spectral, beta)
    gap = lambda2 - lambda1
    boundary_groups: list[list[np.ndarray]] = [[], [], []]
    state_groups: list[list[np.ndarray]] = [[], [], []]
    maximum_mode_residual = 0.0
    for component in range(10):
        mode_boundary: list[np.ndarray] = []
        mode_state: list[np.ndarray] = []
        for family in range(3):
            value, derivative = NEGATIVE._generic_mode(spectral, beta, family)
            boundary, residual, _ = NEGATIVE._boundary_column(
                beta, spectral, value, derivative, component
            )
            mode_boundary.append(boundary)
            mode_state.append(_state_column(value, component))
            maximum_mode_residual = max(maximum_mode_residual, residual)
        boundary_groups[0].append((-1.0j * mode_boundary[1] - mode_boundary[0]) / gap)
        boundary_groups[1].append(mode_boundary[0])
        boundary_groups[2].append(mode_boundary[2])
        state_groups[0].append((-1.0j * mode_state[1] - mode_state[0]) / gap)
        state_groups[1].append(mode_state[0])
        state_groups[2].append(mode_state[2])
    boundary = ROW @ np.column_stack(sum(boundary_groups, [])) @ COLUMN
    state = np.column_stack(sum(state_groups, [])) @ COLUMN
    return boundary, state, maximum_mode_residual


def _state_operator(boundary: np.ndarray, state: np.ndarray) -> np.ndarray:
    return np.linalg.solve(boundary.T, state.T).T


def _zero_shift_operator(zeta: float) -> np.ndarray:
    _, boundary = TRANSITION._source_matrices(
        zeta, -zeta, (ROW, COLUMN), (ZERO_ROW, ZERO_COLUMN)
    )
    root = np.sqrt(1.0 + zeta * zeta)
    value = np.asarray([zeta, root, -1.0j, 0.0j], dtype=complex)
    value /= np.linalg.norm(value)
    state_columns = [_state_column(value, component) for component in range(10)]
    state = np.column_stack(state_columns) @ ZERO_COLUMN
    return _state_operator(boundary, state)


def _complex_pairs(matrix: np.ndarray) -> list[list[list[float]]]:
    return [
        [[float(np.real(value)), float(np.imag(value))] for value in row]
        for row in matrix
    ]


def _matrix_metrics(boundary: np.ndarray, state: np.ndarray) -> tuple[np.ndarray, float]:
    operator = _state_operator(boundary, state)
    return operator, float(np.linalg.svd(operator, compute_uv=False)[0])


def build_artifact() -> dict[str, Any]:
    endpoint_gram = np.asarray(
        [
            [16.0, 0.0, 8.0j, 0.0],
            [0.0, 4.0, -4.0j, 0.0],
            [-8.0j, 4.0j, 12.0, 0.0],
            [0.0, 0.0, 0.0, 8.0],
        ],
        dtype=complex,
    )
    eigenvalues = np.asarray([12.0 - 4.0 * np.sqrt(7.0), 8.0, 8.0, 12.0 + 4.0 * np.sqrt(7.0)])
    endpoint_norm = float(2.0 * np.sqrt(3.0 + np.sqrt(7.0)))

    zero_operator = _zero_shift_operator(REFERENCE_ZETA)
    zero_gram = zero_operator[:, 6:10].conj().T @ zero_operator[:, 6:10]
    jordan_boundary, jordan_state, _ = _jordan_matrices(REFERENCE_ZETA)
    jordan_operator = _state_operator(jordan_boundary, jordan_state)
    jordan_gram = jordan_operator[:, 6:10].conj().T @ jordan_operator[:, 6:10]
    reference = np.zeros((40, 30), dtype=complex)
    reference[:, :10] = zero_operator

    grid_cases: list[dict[str, Any]] = []
    grid_summaries: list[dict[str, Any]] = []
    for scale in SCALES:
        parameter_grid = np.logspace(np.log10(scale) - 4.0, np.log10(scale), GRID_POINTS_PER_AXIS)
        records: list[dict[str, Any]] = []
        for zeta in parameter_grid:
            for beta_magnitude in parameter_grid:
                beta = -float(beta_magnitude)
                zeta_value = float(zeta)
                relative_gap = abs(zeta_value - beta_magnitude) / max(zeta_value, beta_magnitude)
                if zeta_value == beta_magnitude:
                    chart = "source_ode_consistent_jordan"
                    boundary, state, residual = _jordan_matrices(zeta_value)
                elif relative_gap < 0.1:
                    chart = "normalized_confluent_divided_difference"
                    boundary, state, residual = _confluent_matrices(zeta_value, beta)
                else:
                    chart = "unit_generic_eigenmodes"
                    boundary, state, residual = _generic_matrices(zeta_value, beta)
                operator, kreiss_norm = _matrix_metrics(boundary, state)
                record = {
                    "scale": scale,
                    "zeta": zeta_value,
                    "beta": beta,
                    "basis_chart": chart,
                    "state_operator_shape": list(operator.shape),
                    "kreiss_state_to_data_norm": kreiss_norm,
                    "frobenius_distance_to_embedded_zero_shift_reference": float(
                        np.linalg.norm(operator - reference, ord="fro")
                    ),
                    "principal_mode_residual": residual,
                }
                records.append(record)
                grid_cases.append(record)
        norms = [row["kreiss_state_to_data_norm"] for row in records]
        distances = [row["frobenius_distance_to_embedded_zero_shift_reference"] for row in records]
        grid_summaries.append(
            {
                "scale": scale,
                "sample_count": len(records),
                "kreiss_norm_min": min(norms),
                "kreiss_norm_max": max(norms),
                "max_frobenius_distance_to_zero_shift_reference": max(distances),
                "min_frobenius_distance_to_zero_shift_reference": min(distances),
                "basis_chart_counts": {
                    chart: sum(row["basis_chart"] == chart for row in records)
                    for chart in (
                        "unit_generic_eigenmodes",
                        "source_ode_consistent_jordan",
                        "normalized_confluent_divided_difference",
                    )
                },
            }
        )

    basis_invariance: list[dict[str, Any]] = []
    for scale in (1.0e-2, 1.0e-3, 1.0e-4):
        for relative_offset in (1.0e-1, 1.0e-2, 1.0e-3):
            beta = -scale
            zeta = scale * (1.0 + relative_offset)
            generic_boundary, generic_state, _ = _generic_matrices(zeta, beta)
            confluent_boundary, confluent_state, _ = _confluent_matrices(zeta, beta)
            generic_operator = _state_operator(generic_boundary, generic_state)
            confluent_operator = _state_operator(confluent_boundary, confluent_state)
            basis_invariance.append(
                {
                    "scale": scale,
                    "relative_offset": relative_offset,
                    "max_abs_operator_difference": float(
                        np.max(np.abs(generic_operator - confluent_operator))
                    ),
                }
            )

    gram_error_zero = float(np.max(np.abs(zero_gram - endpoint_gram)))
    gram_error_jordan = float(np.max(np.abs(jordan_gram - endpoint_gram)))
    zero_non_gauge_max_column_norm = float(
        np.max(np.linalg.norm(zero_operator[:, :6], axis=0))
    )
    jordan_non_gauge_max_column_norm = float(
        np.max(np.linalg.norm(jordan_operator[:, :6], axis=0))
    )
    zero_full_operator_norm = float(np.linalg.svd(zero_operator, compute_uv=False)[0])
    max_basis_difference = max(row["max_abs_operator_difference"] for row in basis_invariance)
    kreiss_upper = [row["kreiss_norm_max"] for row in grid_summaries]
    kreiss_lower = [row["kreiss_norm_min"] for row in grid_summaries]
    distance_upper = [row["max_frobenius_distance_to_zero_shift_reference"] for row in grid_summaries]
    checks = {
        "zero_shift_endpoint_gram_matches_exact_matrix": gram_error_zero < 2.0e-6,
        "corrected_jordan_endpoint_gram_matches_exact_matrix": gram_error_jordan < 2.0e-6,
        "constraint_and_physical_source_columns_vanish_at_endpoint": max(
            zero_non_gauge_max_column_norm, jordan_non_gauge_max_column_norm
        ) < 1.0e-6,
        "full_endpoint_norm_matches_gauge_gram_norm": abs(
            zero_full_operator_norm - endpoint_norm
        ) < 2.0e-6,
        "endpoint_norm_matches_exact_largest_eigenvalue": abs(
            endpoint_norm - np.sqrt(eigenvalues[-1])
        ) < 1.0e-14,
        "generic_and_confluent_charts_give_same_state_operator": max_basis_difference < 1.0e-10,
        "joint_neighborhood_kreiss_norm_envelopes_contract": all(
            right < left for left, right in zip(kreiss_upper, kreiss_upper[1:])
        )
        and all(right > left for left, right in zip(kreiss_lower, kreiss_lower[1:])),
        "full_state_operator_converges_to_zero_shift_reference_on_grids": all(
            right < left for left, right in zip(distance_upper, distance_upper[1:])
        ),
        "all_grid_operators_are_finite_and_modes_satisfy_the_principal_system": all(
            np.isfinite(row["kreiss_state_to_data_norm"])
            and row["state_operator_shape"] == [40, 30]
            and row["principal_mode_residual"] < 1.0e-8
            for row in grid_cases
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    status = "PASS_JOINT_REAL_KREISS_OPERATOR_SCREEN" if all(checks.values()) else "FAIL_OR_UNRESOLVED_JOINT_REAL_KREISS_OPERATOR"
    endpoint = {
        "definition": "T0=lim_(zeta->0+) W0(zeta)*C0(zeta)^-1, embedded in the 30-source negative-shift coordinates with the 20 extra curl-source columns zero",
        "input_columns": "the four gauge-source coordinates survive; the six constraint and two physical source coordinates vanish in the state-map limit",
        "gram_matrix_real_imag_pairs": _complex_pairs(endpoint_gram),
        "gram_eigenvalues": [float(value) for value in eigenvalues],
        "largest_eigenvalue": float(eigenvalues[-1]),
        "kreiss_operator_norm": endpoint_norm,
        "closed_form_norm": "2*sqrt(3+sqrt(7))",
        "zero_shift_reference_zeta": REFERENCE_ZETA,
        "zero_shift_full_operator_norm_at_reference": zero_full_operator_norm,
        "zero_shift_non_gauge_max_column_norm_at_reference": zero_non_gauge_max_column_norm,
        "corrected_jordan_non_gauge_max_column_norm_at_reference": jordan_non_gauge_max_column_norm,
        "zero_shift_gram_max_abs_error": gram_error_zero,
        "corrected_jordan_gram_max_abs_error": gram_error_jordan,
    }
    equation = {
        "kreiss_operator": "T(beta,zeta)=W(beta,zeta)*C(beta,zeta)^-1",
        "W": "40x30 boundary-state matrix for (Pi,Phi_x,Phi_y,Phi_z) in a Frobenius-orthonormal symmetric-tensor component basis",
        "C": "registered 30x30 source boundary matrix in the transformed constraint/physical/gauge/curl data basis",
        "state_norm": "Euclidean norm on the 40 orthonormal field/tensor coordinates",
        "source_norm": "Euclidean norm on the 30 registered transformed boundary-data coordinates",
        "endpoint": endpoint,
        "claim_boundary": "exact zero-shift endpoint Gram result plus a finite positive-real joint-neighborhood screen; no continuous all-ratio or complex-frequency uniform Kreiss proof",
    }
    source_hashes = {
        _relative(path): _hash(path)
        for path in (
            Path(__file__), SCALE_SCRIPT, SCALE_ARTIFACT, TRANSITION_SCRIPT,
            NEGATIVE_SCRIPT, NEGATIVE_ARTIFACT, ZERO_SCRIPT, ZERO_ARTIFACT,
            BOUNDARY_SOURCE, PROJECTOR_SOURCE,
        )
    }
    controlling_blocker = "analytic_uniform_remainder_bound_for_full_state_transfer_operator_over_joint_beta_zeta_domain_missing"
    major = {
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_JOINT_REAL_STATE_TRANSFER_LIMIT",
        "topic": "core_curved_3p1",
        "closure_level": "PARTIAL",
        "what_is_closed": [
            "The quantity required by the Kreiss inequality is now evaluated as the 40x30 boundary-state transfer T=W*C^-1, rather than inferring it from det(C) or coefficient norms alone.",
            "The zero-shift endpoint transfer has four surviving gauge-source directions; its six constraint and two physical source columns vanish. The gauge-sector Gram eigenvalues are {12-4*sqrt(7),8,8,12+4*sqrt(7)}, and this is also the full endpoint operator norm 2*sqrt(3+sqrt(7)). The corrected negative-shift Jordan chart converges to the same endpoint Gram matrix.",
            "Across 100 positive-real beta/zeta grid points, the Kreiss-norm interval contracts toward this endpoint value, while T converges to the embedded zero-shift reference; generic and confluent charts give the same operator in nine cross-checks.",
        ],
        "what_remains_open": [
            "The 2D log grids do not prove a uniform remainder bound over every positive-real ratio; an analytic chart-compatible bound for T-T0 is still needed.",
            "The imaginary-frequency boundary, high-frequency compactification, uniformity over a full shift interval, beta->-1 loss, and full variable-coefficient CPBC evolution remain open.",
            "The state/source norms are explicitly declared internal orthonormal coordinates; comparison with every convention in the imported Kreiss theorem remains an interface check, not a physical UET claim.",
        ],
        "dependency_unlocked": "none; Core curved 3+1 remains PARTIAL and Gravity remains blocked",
        "evidence_artifacts": [
            {"path": _relative(Path(__file__)), "sha256": source_hashes[_relative(Path(__file__))]},
            {"path": _relative(SCALE_ARTIFACT), "sha256": source_hashes[_relative(SCALE_ARTIFACT)]},
            {"path": _relative(NEGATIVE_ARTIFACT), "sha256": source_hashes[_relative(NEGATIVE_ARTIFACT)]},
            {"path": _relative(ZERO_ARTIFACT), "sha256": source_hashes[_relative(ZERO_ARTIFACT)]},
        ],
        "open_blockers": [
            "uniform remainder bound over all positive-real beta/zeta ratios",
            "imaginary-frequency boundary and high-frequency compactification",
            "fixed-background norm-interface comparison and full variable-coefficient CPBC evolution",
        ],
        "controlling_blocker": controlling_blocker,
        "equation_or_mapping": equation,
        "units": "Dimensionless frozen-coefficient Fourier-Laplace variables, tangential omega=1, local orthonormal GH state coordinates.",
        "derivation_class": "exact zero-shift endpoint Gram reduction with negative-shift generic/Jordan/confluent source-map reconstruction and finite 2D path verification",
        "observable": "operator norm of the boundary-state response per unit transformed boundary data",
        "data_role": "primary-literature formula reproduction and internal numerical verification; no empirical data, fitting, or holdout",
        "verification_status": status,
        "claim_boundary": equation["claim_boundary"],
    }
    return {
        "schema_version": "core-curved-3p1-gh-rinne-joint-real-kreiss-operator-v1",
        "artifact": "curved_3p1_gh_rinne_joint_real_kreiss_operator",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "major_result_id": major["major_result_id"],
        "major_result": major,
        "closure_level": "PARTIAL",
        "MAJOR_RESULT_CLOSURE": "PARTIAL",
        "WHAT_IS_ACTUALLY_CLOSED": major["what_is_closed"],
        "WHAT_REMAINS_OPEN": major["what_remains_open"],
        "DEPENDENCY_UNLOCKED": major["dependency_unlocked"],
        "STATUS": status,
        "EQUATION_OR_MAPPING": equation,
        "VERIFICATION": {
            "checks": checks,
            "scales": list(SCALES),
            "grid_points_per_axis": GRID_POINTS_PER_AXIS,
            "grid_summaries": grid_summaries,
            "grid_cases": grid_cases,
            "basis_invariance_cases": basis_invariance,
            "source_hashes": source_hashes,
            "source_reference": "https://arxiv.org/abs/gr-qc/0606053",
        },
        "CONTROLLING_BLOCKER": major["controlling_blocker"],
        "NEXT_ACTION": "Derive a continuous estimate for ||T(beta,zeta)-T0|| across the compactified positive-real ratio using the generic/Jordan chart transition; then extend the state-transfer bound to the imaginary-frequency boundary and high frequencies.",
        "CLAIM_BOUNDARY": equation["claim_boundary"],
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
                "grid_summaries": artifact["VERIFICATION"]["grid_summaries"],
                "endpoint": artifact["EQUATION_OR_MAPPING"]["endpoint"],
            },
            indent=2,
        )
    )
    return 0 if artifact["STATUS"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
