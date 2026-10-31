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
NEGATIVE_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_negative_shift_kreiss_symbol.json"
ZERO_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_zero_shift_kreiss_symbol.py"
ZERO_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_zero_shift_kreiss_symbol.json"
BOUNDARY_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py"
PROJECTOR_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_negative_shift_zero_transition.json"
ZETA_VALUES = (0.25, 0.5, 1.0, 2.0, 4.0)
BETA_MAGNITUDES = (1.0e-1, 1.0e-2, 1.0e-3)
BLOCK_TOLERANCE = 1.0e-10


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


NEGATIVE = _load_module("_uet_rinne_zero_transition_negative", NEGATIVE_SCRIPT)
ZERO = NEGATIVE.BASELINE


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _source_matrices(zeta: float, beta: float, negative_maps, zero_maps):
    negative_row, negative_column = negative_maps
    zero_row, zero_column = zero_maps
    columns: list[np.ndarray] = []
    for family in range(3):
        value, derivative = NEGATIVE._generic_mode(complex(zeta, 0.0), beta, family)
        for component in range(10):
            column, _, _ = NEGATIVE._boundary_column(
                beta, complex(zeta, 0.0), value, derivative, component
            )
            columns.append(column)
    negative_matrix = negative_row @ np.column_stack(columns) @ negative_column

    zero_columns = [ZERO._mode_column(complex(zeta, 0.0), component)[0] for component in range(10)]
    zero_residuals = np.column_stack(zero_columns)
    zero_residuals[:6, :] /= zeta
    zero_matrix = zero_row @ zero_residuals @ zero_column
    return negative_matrix, zero_matrix


def _case(zeta: float, beta: float, negative_maps, zero_maps) -> dict[str, Any]:
    negative_matrix, zero_matrix = _source_matrices(
        zeta, beta, negative_maps, zero_maps
    )
    block_a = negative_matrix[:10, :10]
    block_b = negative_matrix[:10, 10:]
    block_d = negative_matrix[10:, :10]
    block_e = negative_matrix[10:, 10:]
    k2 = float(np.sqrt(beta * beta + zeta * zeta))
    xy_leading = (zeta * zeta - beta * beta) / (k2 * zeta)
    expected_beta_e = np.zeros((20, 20), dtype=complex)
    expected_beta_e[:10, :10] = xy_leading * np.eye(10)
    expected_beta_e[10:, 10:] = 1.0j * np.eye(10)

    negative_sv = np.linalg.svd(negative_matrix, compute_uv=False)[::-1]
    zero_sv = np.linalg.svd(zero_matrix, compute_uv=False)[::-1]
    sign_negative, logdet_negative = np.linalg.slogdet(negative_matrix)
    sign_zero, logdet_zero = np.linalg.slogdet(zero_matrix)
    return {
        "zeta_real": zeta,
        "beta": beta,
        "block_shapes": {
            "A_u1_to_top_data": list(block_a.shape),
            "B_u2_to_top_data": list(block_b.shape),
            "D_u1_to_u2_curl_data": list(block_d.shape),
            "E_u2_to_u2_curl_data": list(block_e.shape),
        },
        "A_to_zero_shift_max_abs": float(np.max(np.abs(block_a - zero_matrix))),
        "B_frobenius_norm": float(np.linalg.norm(block_b)),
        "D_max_abs": float(np.max(np.abs(block_d))),
        "beta_E_to_analytic_limit_max_abs": float(
            np.max(np.abs(beta * block_e - expected_beta_e))
        ),
        "xy_curl_beta_E_diagonal": float(np.real(np.diag(beta * block_e[:10, :10])[0])),
        "xz_curl_beta_E_diagonal": {
            "real": float(np.real(np.diag(beta * block_e[10:, 10:])[0])),
            "imag": float(np.imag(np.diag(beta * block_e[10:, 10:])[0])),
        },
        "full_inverse_norm": float(1.0 / negative_sv[0]),
        "zero_shift_inverse_norm": float(1.0 / zero_sv[0]),
        "inverse_norm_difference": float(abs(1.0 / negative_sv[0] - 1.0 / zero_sv[0])),
        "ten_smallest_singular_values_max_difference": float(
            np.max(np.abs(negative_sv[:10] - zero_sv))
        ),
        "determinant_beta20_residual": float(
            logdet_negative - logdet_zero + 20.0 * np.log(abs(beta))
        ),
        "determinant_orientation_ratio": {
            "real": float(np.real(sign_negative / sign_zero)),
            "imag": float(np.imag(sign_negative / sign_zero)),
        },
    }


def build_artifact() -> dict[str, Any]:
    negative_row, negative_column, _ = NEGATIVE._source_transforms()
    zero_row, zero_column, _ = ZERO._source_component_basis_map()
    negative_maps = (negative_row, negative_column)
    zero_maps = (zero_row, zero_column)
    cases = [
        _case(zeta, -beta_magnitude, negative_maps, zero_maps)
        for zeta in ZETA_VALUES
        for beta_magnitude in BETA_MAGNITUDES
    ]
    grouped: dict[float, list[dict[str, Any]]] = {
        zeta: [row for row in cases if row["zeta_real"] == zeta]
        for zeta in ZETA_VALUES
    }
    checks = {
        "five_positive_real_frequencies_are_preregistered": len(ZETA_VALUES) == 5,
        "all_sub_luminal_negative_shifts_are_nonzero": all(
            -1.0 < row["beta"] < 0.0 for row in cases
        ),
        "u1_modes_do_not_enter_additional_u2_curl_rows": all(
            row["D_max_abs"] < BLOCK_TOLERANCE for row in cases
        ),
        "incoming_u2_curl_block_matches_analytic_beta_scaling": all(
            row["beta_E_to_analytic_limit_max_abs"] < BLOCK_TOLERANCE
            for row in cases
        ),
        "top_left_block_converges_to_zero_shift_operator": all(
            values[-1]["A_to_zero_shift_max_abs"]
            < values[-2]["A_to_zero_shift_max_abs"]
            < values[-3]["A_to_zero_shift_max_abs"]
            for values in grouped.values()
        ),
        "u2_to_top_data_block_stays_bounded_on_declared_compact_frequency_grid": max(
            row["B_frobenius_norm"] for row in cases
        ) < 100.0,
        "boundary_inverse_norm_converges_to_zero_shift_lane": all(
            values[-1]["inverse_norm_difference"]
            < values[-2]["inverse_norm_difference"]
            < values[-3]["inverse_norm_difference"]
            for values in grouped.values()
        ),
        "ten_small_singular_values_approach_zero_shift_spectrum": all(
            values[-1]["ten_smallest_singular_values_max_difference"]
            < values[-2]["ten_smallest_singular_values_max_difference"]
            < values[-3]["ten_smallest_singular_values_max_difference"]
            for values in grouped.values()
        ),
        "determinant_magnitude_ratio_converges_to_beta_minus20": all(
            abs(values[-1]["determinant_beta20_residual"]) < 0.02
            and abs(values[-1]["determinant_beta20_residual"])
            < abs(values[-2]["determinant_beta20_residual"])
            < abs(values[-3]["determinant_beta20_residual"])
            for values in grouped.values()
        ),
    }
    status = (
        "PASS_FIXED_FREQUENCY_GLANCING_BLOCK_LIMIT"
        if all(checks.values())
        else "FAIL_OR_UNRESOLVED_FIXED_FREQUENCY_GLANCING_LIMIT"
    )
    source_hashes = {
        _rel(path): _sha256(path)
        for path in (
            Path(__file__),
            NEGATIVE_SCRIPT,
            NEGATIVE_ARTIFACT,
            ZERO_SCRIPT,
            ZERO_ARTIFACT,
            BOUNDARY_SOURCE,
            PROJECTOR_SOURCE,
        )
    }
    analytic_mapping = {
        "parameter_domain": "real zeta>0 fixed; beta->0- from the negative-shift side",
        "incoming_mode_count": "30 for beta<0 (u1_minus plus two u2_A families); 10 at beta=0 (u1_minus only, u2_A glancing)",
        "source_matrix_block_form": "C_minus=[[A(beta,zeta),B(beta,zeta)],[0,E(beta,zeta)]] with 10+20 source rows and 10+20 mode amplitudes",
        "top_left_limit": "A(beta,zeta)->C_zero(zeta), the registered 10x10 zero-shift source boundary matrix",
        "top_right_bound": "B(beta,zeta)=O(1) for each fixed real zeta>0",
        "lower_left_identity": "D=0 because each u1_minus mode satisfies the two definition-curl rows",
        "lower_right_u2_curl_block": "beta*E=diag(((zeta^2-beta^2)/(zeta*sqrt(zeta^2+beta^2)))*I10, i*I10)->diag(I10,i*I10)",
        "inverse_limit": "C_minus^-1 -> diag(C_zero^-1,0_20); the 20 glancing amplitudes are suppressed as O(beta) for bounded incoming curl data",
        "determinant_interpretation": "|det C_minus|~|beta|^-20*|det C_zero| at fixed zeta; the divergence is the product of 20 stiff curl directions, not an inverse-map blow-up",
        "claim_boundary": "analytic block limit at fixed real zeta>0; compact positive-real frequency intervals follow by continuity where C_zero is nonsingular; no conclusion for zeta->0, the imaginary axis, or |zeta|->infinity",
    }
    major_result = {
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_ZERO_SHIFT_GLANCING_BLOCK_LIMIT",
        "topic": "core_curved_3p1",
        "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS_") else "PARTIAL",
        "what_is_closed": [
            "For fixed real zeta>0, the negative-shift 30x30 source symbol splits into the zero-shift 10x10 u1 boundary map and a 20x20 u2 curl block whose leading scale is 1/beta. The inverse solution map converges to the zero-shift lane while the 20 glancing-mode amplitudes vanish for bounded curl data.",
            "The source determinant's |beta|^-20 growth at fixed zeta is accounted for by the 20 stiff u2 curl directions; it is not evidence that the boundary-to-mode inverse norm diverges at beta=0.",
        ],
        "what_remains_open": [
            "The result is for fixed real positive zeta and its declared compact frequency sample. Joint zeta->0, the imaginary frequency boundary, |zeta|->infinity, complex right-half-plane uniformity, and the full parent CPBC evolution remain open.",
            "The endpoint beta->-1 has the distinct family-uniform Kreiss no-go recorded in the adjacent lane and is not repaired by this beta->0 result.",
        ],
        "dependency_unlocked": "none; no Core-parent or Gravity dependency is unlocked",
        "equation_or_mapping": analytic_mapping,
        "units": "Dimensionless frozen-coefficient Fourier-Laplace variables with omega=1.",
        "derivation_class": "analytic block asymptotic from the registered u1/u2 modes and definition-curl rows, with source-matrix and zero-shift-lane cross-checks",
        "observable": "source boundary-to-decaying-mode operator norm and singular spectrum across the glancing-mode transition",
        "data_role": "primary-literature formula reproduction and internal analytic/numerical verification; no empirical data or fitting",
        "verification_status": status,
        "claim_boundary": analytic_mapping["claim_boundary"],
    }
    return {
        "schema_version": "core-curved-3p1-gh-rinne-zero-transition-v1",
        "artifact": "curved_3p1_gh_rinne_negative_shift_zero_transition",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "major_result_id": major_result["major_result_id"],
        "major_result": major_result,
        "closure_level": major_result["closure_level"],
        "MAJOR_RESULT_CLOSURE": major_result["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": major_result["what_is_closed"],
        "WHAT_REMAINS_OPEN": major_result["what_remains_open"],
        "DEPENDENCY_UNLOCKED": major_result["dependency_unlocked"],
        "STATUS": status,
        "EQUATION_OR_MAPPING": analytic_mapping,
        "VERIFICATION": {
            "checks": checks,
            "frequency_values": list(ZETA_VALUES),
            "negative_shift_magnitudes": list(BETA_MAGNITUDES),
            "cases": cases,
            "source_hashes": source_hashes,
            "source_reference": "https://arxiv.org/abs/gr-qc/0606053",
        },
        "CONTROLLING_BLOCKER": "joint_zero_frequency_glancing_and_closed_frequency_uniformity_remain_open",
        "NEXT_ACTION": "Analyze beta->0 jointly with zeta->0 and along the imaginary axis, then extend the block estimate to compact complex frequency sets; keep the beta->-1 loss of family-uniformity separate.",
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
                "checks": artifact["VERIFICATION"]["checks"],
                "last_case_per_frequency": {
                    str(zeta): next(
                        row for row in artifact["VERIFICATION"]["cases"]
                        if row["zeta_real"] == zeta and row["beta"] == -BETA_MAGNITUDES[-1]
                    )
                    for zeta in ZETA_VALUES
                },
            },
            indent=2,
        )
    )
    return 0 if artifact["STATUS"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
