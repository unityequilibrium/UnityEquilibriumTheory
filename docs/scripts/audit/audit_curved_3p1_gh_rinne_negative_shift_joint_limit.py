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
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_negative_shift_joint_limit.json"
AUDIT_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_negative_shift_kreiss_symbol.py"
AUDIT_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_negative_shift_kreiss_symbol.json"
JOINT_EPSILON_VALUES = (1.0e-2, 1.0e-4, 1.0e-6, 1.0e-8)
MATRIX_EPSILON_VALUES = (1.0e-2, 5.0e-3, 2.0e-3, 1.0e-3)
RANK_RELATIVE_TOLERANCE = 1.0e-10
RINNE_URL = "https://arxiv.org/abs/gr-qc/0606053"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = _load_module("_uet_rinne_negative_joint_limit_parent", AUDIT_SCRIPT)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _eq123_log_abs(beta: float, zeta: float) -> float:
    _, lambda1, _ = AUDIT._root_and_lambdas(complex(zeta, 0.0), beta)
    k1 = float(
        np.linalg.norm(
            [zeta - beta * lambda1, -lambda1, -1.0j, 0.0j]
        )
    )
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


def build_artifact() -> dict[str, Any]:
    root3 = float(np.sqrt(3.0))
    asymptotic_coefficient = float(4.0 / (root3 - 1.0) ** 26)
    asymptotic_log_coefficient = float(np.log(asymptotic_coefficient))
    determinant_path = []
    for epsilon in JOINT_EPSILON_VALUES:
        beta = -1.0 + epsilon
        zeta = float(np.sqrt(epsilon))
        log_abs = _eq123_log_abs(beta, zeta)
        asymptotic_log_abs = asymptotic_log_coefficient + 5.0 * np.log(epsilon)
        determinant_path.append(
            {
                "epsilon": epsilon,
                "rinne_beta": beta,
                "zeta_real": zeta,
                "eq123_log_abs_determinant": log_abs,
                "asymptotic_log_abs_determinant": float(asymptotic_log_abs),
                "ratio_to_C_epsilon5": float(np.exp(log_abs - asymptotic_log_abs)),
            }
        )

    row_transform, column_transform, _ = AUDIT._source_transforms()
    matrix_path = []
    for epsilon in MATRIX_EPSILON_VALUES:
        beta = -1.0 + epsilon
        zeta = float(np.sqrt(epsilon))
        row = AUDIT._generic_case(
            beta, complex(zeta, 0.0), row_transform, column_transform
        )
        matrix_path.append(
            {
                "epsilon": epsilon,
                "rinne_beta": beta,
                "zeta_real": zeta,
                "boundary_matrix_rank": row["boundary_matrix_rank"],
                "row_equilibrated_sigma_min_over_sigma_max": row[
                    "boundary_relative_smallest_singular_value"
                ],
                "sigma_ratio_over_epsilon_cubed": float(
                    row["boundary_relative_smallest_singular_value"] / epsilon**3
                ),
                "eq123_numeric_log_offset": row["source_eq_123_log_offset"],
            }
        )

    determinant_checks = {
        "epsilon_values_are_in_sub_luminal_negative_shift_domain": all(
            -1.0 < row["rinne_beta"] < 0.0 for row in determinant_path
        ),
        "joint_path_avoids_exact_degenerate_root": all(
            not np.isclose(row["zeta_real"], -row["rinne_beta"], rtol=0.0, atol=1.0e-12)
            for row in determinant_path
        ),
        "source_eq123_determinant_converges_to_C_epsilon5": abs(
            determinant_path[-1]["ratio_to_C_epsilon5"] - 1.0
        ) < 1.0e-5,
        "determinant_tends_to_zero_on_joint_path": determinant_path[-1][
            "eq123_log_abs_determinant"
        ] < determinant_path[0]["eq123_log_abs_determinant"],
    }
    matrix_checks = {
        "moderate_epsilon_matrices_retain_rank_30": all(
            row["boundary_matrix_rank"] == 30 for row in matrix_path
        ),
        "row_equilibrated_singular_ratio_decreases_along_sampled_path": all(
            right["row_equilibrated_sigma_min_over_sigma_max"]
            < left["row_equilibrated_sigma_min_over_sigma_max"]
            for left, right in zip(matrix_path, matrix_path[1:])
        ),
        "matrix_diagnostic_remains_above_double_precision_rank_floor": all(
            row["row_equilibrated_sigma_min_over_sigma_max"]
            > RANK_RELATIVE_TOLERANCE
            for row in matrix_path
        ),
    }
    status = (
        "PASS_NO_UNIFORM_DETERMINANT_FLOOR_JOINT_LIMIT_IDENTIFIED"
        if all(determinant_checks.values()) and all(matrix_checks.values())
        else "MARGINAL_OR_UNRESOLVED_JOINT_LIMIT_DIAGNOSTIC"
    )
    major_result = {
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_NEGATIVE_SHIFT_JOINT_LUMINAL_LOW_FREQUENCY_LIMIT",
        "topic": "core_curved_3p1",
        "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS_") else "PARTIAL",
        "what_is_closed": [
            "Along beta=-1+epsilon and zeta=sqrt(epsilon), source Eq. (123) gives |det C|~C*epsilon^5 with C=4/(sqrt(3)-1)^26. Thus the source-normalized boundary determinant has no positive parameter-uniform lower bound over the entire open subluminal negative-shift domain as beta approaches -1 and zeta approaches 0.",
            "The registered row-equilibrated boundary-symbol sample has rank 30 at four moderate epsilon values while sigma_min/sigma_max decreases monotonically from about 1.48e-6 to 1.53e-9. This is a finite conditioning diagnostic consistent with loss of uniform conditioning, not a proof of the exact singular-value exponent.",
        ],
        "what_remains_open": [
            "A direct asymptotic derivation of the minimum singular value or inverse boundary-map norm along the joint path is still needed before claiming a uniform Kreiss estimate fails in the full operator norm.",
            "Per-fixed-beta Kreiss stability, compact beta intervals bounded away from -1 and 0, the beta=0 lane transition, variable-coefficient/nonlinear GH, corners, matter boundaries, and the Core curved-parent gate remain separate questions.",
        ],
        "dependency_unlocked": "none; this closes only the full-domain uniform determinant-floor question and unlocks no Core-parent or Gravity dependency",
        "equation_or_mapping": {
            "joint_limit_path": "epsilon=1+beta -> 0+, beta=-1+epsilon, zeta=sqrt(epsilon)>0",
            "asymptotic_modes": "lambda1^-~(1-sqrt(3))/(2*sqrt(epsilon)); lambda2=zeta/beta~ -sqrt(epsilon)",
            "asymptotic_normalizations": "K1~(sqrt(6)-sqrt(2))/(2*sqrt(epsilon)); K2->1",
            "source_eq123_result": "|det C|~[(1+sqrt(3))/2]^16/[8*((sqrt(6)-sqrt(2))/2)^10]*epsilon^5 = [4/(sqrt(3)-1)^26]*epsilon^5",
            "interpretation": "No parameter-uniform positive determinant floor exists over all -1<beta<0 and Re(zeta)>0 in this source-normalized boundary-data basis; this does not contradict a Kreiss bound for each fixed beta.",
        },
        "units": "Frozen local orthonormal geometric units; zeta=s/omega and epsilon are dimensionless.",
        "derivation_class": "analytic asymptotic of source Eq. (123), with finite registered boundary-symbol singular-value cross-check",
        "observable": "source-normalized boundary determinant and row-equilibrated sigma_min/sigma_max diagnostic",
        "data_role": "primary-literature formula cross-check; no empirical data, fitting, or calibration",
        "verification_status": status,
        "claim_boundary": "The asymptotic determinant-floor result is analytic for the declared joint path. The observed singular-value trend is finite-precision numerical evidence only; it is not a complete inverse-map/Kreiss failure proof, does not negate per-background stability for fixed beta, and does not close the Core curved parent or Gravity.",
    }
    source_hashes = {
        _rel(path): _sha256(path)
        for path in (Path(__file__), AUDIT_SCRIPT, AUDIT_ARTIFACT)
    }
    return {
        "schema_version": "core-curved-3p1-gh-rinne-joint-limit-v1",
        "artifact": "curved_3p1_gh_rinne_negative_shift_joint_limit",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "major_result_id": major_result["major_result_id"],
        "major_result": major_result,
        "closure_level": major_result["closure_level"],
        "STATUS": status,
        "MAJOR_RESULT_CLOSURE": major_result["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": major_result["what_is_closed"],
        "WHAT_REMAINS_OPEN": major_result["what_remains_open"],
        "DEPENDENCY_UNLOCKED": major_result["dependency_unlocked"],
        "EQUATION_OR_MAPPING": major_result["equation_or_mapping"],
        "VERIFICATION": {
            "determinant_checks": determinant_checks,
            "matrix_checks": matrix_checks,
            "joint_path_determinant": determinant_path,
            "registered_matrix_path": matrix_path,
            "asymptotic_coefficient": asymptotic_coefficient,
            "double_precision_rank_relative_tolerance": RANK_RELATIVE_TOLERANCE,
            "source_hashes": source_hashes,
        },
        "CONTROLLING_BLOCKER": "uniform_inverse_boundary_map_asymptotic_not_yet_derived_even_though_uniform_determinant_floor_is_absent",
        "NEXT_ACTION": "Derive the normalized smallest-singular-value asymptotic along beta=-1+epsilon,zeta=sqrt(epsilon), then analyze compact shift intervals and the separate beta=0 transition; do not conflate this joint limit with fixed-beta Kreiss stability.",
        "CLAIM_BOUNDARY": major_result["claim_boundary"],
        "full_core_unlock": False,
        "gravity_unlock": False,
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
                "determinant_checks": artifact["VERIFICATION"]["determinant_checks"],
                "matrix_checks": artifact["VERIFICATION"]["matrix_checks"],
            },
            indent=2,
        )
    )
    return 0 if artifact["STATUS"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
