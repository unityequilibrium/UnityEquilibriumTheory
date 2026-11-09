from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
NEGATIVE_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_negative_shift_kreiss_symbol.py"
NEGATIVE_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_negative_shift_kreiss_symbol.json"
JOINT_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_negative_shift_joint_limit.py"
JOINT_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_negative_shift_joint_limit.json"
BOUNDARY_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py"
PROJECTOR_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_negative_shift_no_uniform_beta_kreiss.json"
WITNESS_EPSILON_VALUES = (1.0e-2, 1.0e-3, 1.0e-4)
SVD_EPSILON_VALUES = (1.0e-2, 5.0e-3, 2.0e-3, 1.0e-3, 5.0e-4, 2.0e-4, 1.0e-4)
ROW_MATCH_RELATIVE_TOLERANCE = 1.0e-8


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


NEGATIVE = _load_module("_uet_rinne_no_uniform_beta_parent", NEGATIVE_SCRIPT)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _symbolic_witness() -> dict[str, Any]:
    t = sp.symbols("t", positive=True)
    epsilon = t**2
    beta = -1 + epsilon
    zeta = t
    lambda1 = (1 - epsilon - sp.sqrt(3 - epsilon)) / (t * (2 - epsilon))
    k1 = sp.sqrt((zeta - beta * lambda1) ** 2 + lambda1**2 + 1)
    determinant_factor = zeta - (1 + beta) * lambda1
    h_component = -(
        1 + 2 * lambda1 * determinant_factor
    ) / (sp.sqrt(3) * k1 * zeta)
    leading_h = sp.simplify(sp.limit(h_component / epsilon, t, 0, dir="+"))
    expected_leading_h = (9 * sp.sqrt(2) + 5 * sp.sqrt(6)) / 12
    k_lower_bound = sp.simplify(1 / (sp.sqrt(2) * leading_h))
    expected_k_lower_bound = 9 - 5 * sp.sqrt(3)
    residual_series = sp.series(h_component, t, 0, 6)
    return {
        "epsilon_definition": "epsilon=t^2=1+beta, t>0",
        "beta_path": "beta=-1+epsilon",
        "zeta_path": "zeta=t=sqrt(epsilon)>0",
        "lambda1_expression": sp.sstr(lambda1),
        "lambda1_asymptotic": sp.sstr(sp.series(lambda1, t, 0, 3).removeO()),
        "k1_asymptotic_leading": "(sqrt(6)-sqrt(2))/(2*t)",
        "amplitude_witness": "sigma_1,ab has independent components (tt,tx,xx)=(1,1,1)/sqrt(3); sigma_2=sigma_3=0",
        "source_boundary_data_witness": "C(beta,zeta)*sigma=(r,r,0,...,0), with only the first two constraint-data rows nonzero",
        "r_expression": "-[1+2*lambda1*(zeta-(1+beta)*lambda1)]/(sqrt(3)*K1*zeta)",
        "r_series_in_t": sp.sstr(residual_series),
        "r_over_epsilon_limit": sp.sstr(leading_h),
        "leading_coefficient_matches_exact_form": bool(sp.simplify(leading_h - expected_leading_h) == 0),
        "leading_boundary_data_norm": "sqrt(2)*(9*sqrt(2)+5*sqrt(6))/12 * epsilon + O(epsilon^2) = (9+5*sqrt(3))/6 * epsilon + O(epsilon^2)",
        "source_amplitude_and_normalized_mode_norm": "||sigma||_2=1 and ||(zeta-beta*lambda1,-lambda1,-i,0)/K1||_2=1; hence ||v||_2=1 in the declared source component norm",
        "kreiss_constant_lower_bound": "K_beta >= ||v||_2/||h||_2 = (9-5*sqrt(3))/epsilon + O(1)",
        "kreiss_prefactor_matches_exact_form": bool(sp.simplify(k_lower_bound - expected_k_lower_bound) == 0),
        "numeric_values": {
            "r_over_epsilon_limit": float(sp.N(leading_h, 16)),
            "epsilon_times_k_lower_bound_limit": float(sp.N(k_lower_bound, 16)),
        },
    }


def _source_matrix(beta: float, zeta: complex, row_transform: np.ndarray, column_transform: np.ndarray) -> np.ndarray:
    columns: list[np.ndarray] = []
    for family in range(3):
        value, derivative = NEGATIVE._generic_mode(zeta, beta, family)
        for component in range(10):
            column, _, _ = NEGATIVE._boundary_column(
                beta, zeta, value, derivative, component
            )
            columns.append(column)
    return row_transform @ np.column_stack(columns) @ column_transform


def _numeric_witness(symbolic: dict[str, Any]) -> dict[str, Any]:
    row_transform, column_transform, _ = NEGATIVE._source_transforms()
    sigma = np.zeros(30, dtype=complex)
    sigma[[0, 1, 4]] = 1.0 / np.sqrt(3.0)
    amplitude_norm = float(np.linalg.norm(sigma))
    lambda_t = sp.symbols("t", positive=True)
    epsilon_t = lambda_t**2
    beta_t = -1 + epsilon_t
    zeta_t = lambda_t
    lambda1_t = (1 - epsilon_t - sp.sqrt(3 - epsilon_t)) / (
        lambda_t * (2 - epsilon_t)
    )
    k1_t = sp.sqrt((zeta_t - beta_t * lambda1_t) ** 2 + lambda1_t**2 + 1)
    r_t = -(1 + 2 * lambda1_t * (zeta_t - (1 + beta_t) * lambda1_t)) / (
        sp.sqrt(3) * k1_t * zeta_t
    )
    r_numeric = sp.lambdify(lambda_t, r_t, modules="numpy")
    rows = []
    for epsilon in WITNESS_EPSILON_VALUES:
        beta = -1.0 + epsilon
        zeta_value = float(np.sqrt(epsilon))
        matrix = _source_matrix(
            beta, complex(zeta_value, 0.0), row_transform, column_transform
        )
        boundary_data = matrix @ sigma
        expected_component = float(r_numeric(zeta_value))
        expected = np.zeros(30, dtype=complex)
        expected[:2] = expected_component
        maximum_row_error = float(np.max(np.abs(boundary_data - expected)))
        _, lambda1, _ = NEGATIVE._root_and_lambdas(complex(zeta_value, 0.0), beta)
        mode, _ = NEGATIVE._generic_mode(complex(zeta_value, 0.0), beta, 0)
        state_norm = float(np.linalg.norm(mode) * amplitude_norm)
        data_norm = float(np.linalg.norm(boundary_data))
        rows.append(
            {
                "epsilon": epsilon,
                "beta": beta,
                "zeta_real": zeta_value,
                "lambda1_real": float(lambda1.real),
                "amplitude_norm": amplitude_norm,
                "normalized_mode_norm": float(np.linalg.norm(mode)),
                "state_norm": state_norm,
                "source_data_component_1": float(boundary_data[0].real),
                "source_data_component_2": float(boundary_data[1].real),
                "other_source_data_max_abs": float(np.max(np.abs(boundary_data[2:]))),
                "symbolic_component_prediction": expected_component,
                "maximum_source_matrix_row_error": maximum_row_error,
                "boundary_data_norm": data_norm,
                "kreiss_constant_lower_bound_sample": float(state_norm / data_norm),
                "epsilon_times_lower_bound": float(epsilon * state_norm / data_norm),
            }
        )

    svd_rows = []
    for epsilon in SVD_EPSILON_VALUES:
        beta = -1.0 + epsilon
        matrix = _source_matrix(
            beta,
            complex(float(np.sqrt(epsilon)), 0.0),
            row_transform,
            column_transform,
        )
        singular_values = np.linalg.svd(matrix, compute_uv=False)
        svd_rows.append(
            {
                "epsilon": epsilon,
                "sigma_min": float(singular_values[-1]),
                "sigma_max": float(singular_values[0]),
                "inverse_norm_diagnostic": float(1.0 / singular_values[-1]),
                "condition_number_diagnostic": float(singular_values[0] / singular_values[-1]),
                "role": "finite-precision source-matrix diagnostic only; not the analytic no-uniform-K proof",
            }
        )

    checks = {
        "witness_stays_in_negative_subluminal_domain": all(
            -1.0 < row["beta"] < 0.0 for row in rows
        ),
        "joint_frequency_path_avoids_exact_degeneracy": all(
            not np.isclose(row["zeta_real"], -row["beta"], rtol=0.0, atol=1.0e-12)
            for row in rows
        ),
        "source_amplitude_is_unit_norm": abs(amplitude_norm - 1.0) < 1.0e-14,
        "principal_mode_is_unit_norm": all(
            abs(row["normalized_mode_norm"] - 1.0) < 1.0e-14 for row in rows
        ),
        "registered_source_matrix_matches_symbolic_boundary_witness": all(
            row["maximum_source_matrix_row_error"]
            <= max(1.0e-13, ROW_MATCH_RELATIVE_TOLERANCE * abs(row["symbolic_component_prediction"]))
            for row in rows
        ),
        "boundary_data_only_has_two_declared_constraint_rows": all(
            row["other_source_data_max_abs"] < 1.0e-12 for row in rows
        ),
        "sampled_kreiss_lower_bound_grows_toward_luminal_edge": all(
            right["kreiss_constant_lower_bound_sample"]
            > left["kreiss_constant_lower_bound_sample"]
            for left, right in zip(rows, rows[1:])
        ),
        "symbolic_leading_coefficients_are_exact": (
            symbolic["leading_coefficient_matches_exact_form"]
            and symbolic["kreiss_prefactor_matches_exact_form"]
        ),
    }
    return {
        "checks": checks,
        "witness_path": rows,
        "source_matrix_singular_values": svd_rows,
        "declared_norms": {
            "amplitude": "Euclidean norm over the 30 independent source sigma_ab coefficients",
            "boundary_data": "Euclidean norm over the 30 source boundary-data coefficients in C*sigma=h",
            "stable_mode": "Euclidean norm of the four normalized principal variables times the independent tensor-amplitude norm",
        },
    }


def build_artifact() -> dict[str, Any]:
    symbolic = _symbolic_witness()
    numeric = _numeric_witness(symbolic)
    status = (
        "PASS_CONSTRUCTIVE_NO_UNIFORM_BETA_KREISS_BOUND"
        if all(numeric["checks"].values())
        else "FAIL_OR_UNRESOLVED_NO_UNIFORM_BETA_KREISS_DIAGNOSTIC"
    )
    major_result = {
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_NEGATIVE_SHIFT_NO_BETA_UNIFORM_KREISS_CONSTANT",
        "topic": "core_curved_3p1",
        "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS_") else "PARTIAL",
        "what_is_closed": [
            "A constructive source-normalized decaying-mode witness along beta=-1+epsilon and zeta=sqrt(epsilon) has unit amplitude and unit principal-mode norm, while its 30-component boundary-data vector has only two nonzero entries r with r=[(9*sqrt(2)+5*sqrt(6))/12]*epsilon+O(epsilon^2). Therefore the Kreiss constant cannot be bounded uniformly over the entire negative subluminal shift family as beta approaches -1; under the declared Euclidean source norms K_beta >= (9-5*sqrt(3))/epsilon+O(1).",
            "The witness is non-degenerate for every epsilon>0 and is cross-checked against the registered source-basis boundary matrix. This is a family-uniformity no-go, not a failure of the fixed-beta Kreiss condition.",
        ],
        "what_remains_open": [
            "Rinne's per-fixed-shift, frequency-uniform Kreiss result is not refuted; the bound may depend on the fixed background shift. Uniform estimates on compact shift ranges and the beta-to-zero transition remain to be checked separately.",
            "Closed frequency-boundary behavior, variable-coefficient/nonlinear GH, non-periodic full CPBC evolution, dimensional gravitational observables, and the curved 3+1 parent gate remain open.",
        ],
        "dependency_unlocked": "none; no Core-parent or Gravity dependency is unlocked",
        "equation_or_mapping": symbolic,
        "units": "Dimensionless frozen-coefficient Fourier-Laplace variables with omega=1; epsilon and zeta are dimensionless.",
        "derivation_class": "constructive analytic asymptotic from Rinne Eqs. (69)-(71), (109)-(120), independently cross-checked against the registered Core boundary matrix",
        "observable": "operator norm lower bound for the source boundary-to-decaying-mode solution map",
        "data_role": "primary-literature formula reproduction and internal analytic/numerical verification; no empirical data, fit, or calibration",
        "verification_status": status,
        "claim_boundary": "No finite Kreiss constant can be uniform over beta in (-1,0) on the declared joint path under the stated fixed Euclidean norms. This does not negate any finite K_beta at a fixed beta, contradict Rinne's per-background claim, prove a physical instability, or close the Core curved parent/Gravity.",
    }
    source_hashes = {
        _rel(path): _sha256(path)
        for path in (
            Path(__file__),
            NEGATIVE_SCRIPT,
            NEGATIVE_ARTIFACT,
            JOINT_SCRIPT,
            JOINT_ARTIFACT,
            BOUNDARY_SOURCE,
            PROJECTOR_SOURCE,
        )
    }
    return {
        "schema_version": "core-curved-3p1-gh-rinne-no-uniform-beta-kreiss-v1",
        "artifact": "curved_3p1_gh_rinne_negative_shift_no_uniform_beta_kreiss",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "major_result_id": major_result["major_result_id"],
        "major_result": major_result,
        "closure_level": major_result["closure_level"],
        "MAJOR_RESULT_CLOSURE": major_result["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": major_result["what_is_closed"],
        "WHAT_REMAINS_OPEN": major_result["what_remains_open"],
        "DEPENDENCY_UNLOCKED": major_result["dependency_unlocked"],
        "STATUS": status,
        "EQUATION_OR_MAPPING": symbolic,
        "VERIFICATION": {
            **numeric,
            "symbolic_checks": {
                "leading_h_coefficient": symbolic["leading_coefficient_matches_exact_form"],
                "kreiss_lower_bound_prefactor": symbolic["kreiss_prefactor_matches_exact_form"],
            },
            "source_hashes": source_hashes,
            "source_reference": "https://arxiv.org/abs/gr-qc/0606053",
        },
        "CONTROLLING_BLOCKER": "per_fixed_beta_closed_frequency_kreiss_bound_and_parent_cpbc_evolution_remain_separate_open_items",
        "NEXT_ACTION": "Analyze beta-to-zero and closed-frequency limits under the correct per-background quantifiers; for Core parent integration, declare a compact subluminal shift envelope or derive a shift-weighted estimate rather than requiring one constant up to the luminal edge.",
        "CLAIM_BOUNDARY": major_result["claim_boundary"],
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
                "artifact": _rel(OUTPUT),
                "status": artifact["STATUS"],
                "symbolic_checks": artifact["VERIFICATION"]["symbolic_checks"],
                "numeric_checks": artifact["VERIFICATION"]["checks"],
                "final_epsilon_sample": artifact["VERIFICATION"]["witness_path"][-1],
            },
            indent=2,
        )
    )
    return 0 if artifact["STATUS"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
