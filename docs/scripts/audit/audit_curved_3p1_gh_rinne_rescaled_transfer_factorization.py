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
OPERATOR_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_joint_real_kreiss_operator.py"
OPERATOR_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_joint_real_kreiss_operator.json"
RATIO_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_compactified_ratio_screen.json"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_rescaled_transfer_factorization.json"
DELTAS = (1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5)
RATIOS = tuple(
    sorted(
        {float(value) for value in np.logspace(-8.0, 8.0, 17)}
        | {0.99, 0.999999, 1.000001, 1.01}
    )
)
FACTOR_IDENTITY_TOLERANCE = 1.0e-10
ROW_PROJECTOR_IDENTITY_TOLERANCE = 1.0e-12


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OPERATOR = _load("_uet_rescaled_transfer_operator", OPERATOR_SCRIPT)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _matrices(delta: float, ratio: float):
    if ratio <= 1.0:
        zeta = delta
        beta = -ratio * delta
    else:
        zeta = delta / ratio
        beta = -delta

    if ratio == 1.0:
        boundary, state, residual = OPERATOR._jordan_matrices(zeta)
        chart = "source_ode_consistent_jordan"
    elif abs(ratio - 1.0) < 0.05:
        boundary, state, residual = OPERATOR._confluent_matrices(zeta, beta)
        chart = "normalized_confluent_divided_difference"
    else:
        boundary, state, residual = OPERATOR._generic_matrices(zeta, beta)
        chart = "unit_generic_eigenmodes"
    return beta, zeta, chart, boundary, state, residual


def build_artifact() -> dict[str, Any]:
    endpoint = OPERATOR._zero_shift_operator(1.0e-10)[:, 6:10]
    gauge_projector = np.diag([0.0] * 6 + [1.0] * 4 + [0.0] * 20)
    cases: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []

    for delta in DELTAS:
        group: list[dict[str, Any]] = []
        for ratio in RATIOS:
            beta, zeta, chart, boundary, state, mode_residual = _matrices(delta, ratio)
            scales = np.asarray(
                [zeta] * 6 + [1.0] * 4 + [min(abs(beta), zeta)] * 10 + [abs(beta)] * 10,
                dtype=float,
            )
            row_scaling = np.diag(scales)
            rescaled_boundary = row_scaling @ boundary
            transfer_factor = np.linalg.solve(rescaled_boundary.T, state.T).T
            factored_transfer = transfer_factor @ row_scaling
            direct_transfer = OPERATOR._state_operator(boundary, state)
            singular_values = np.linalg.svd(rescaled_boundary, compute_uv=False)
            gauge_distance = float(
                np.linalg.norm(transfer_factor[:, 6:10] - endpoint, ord="fro")
            )
            projector_distance = float(
                np.linalg.norm(row_scaling - gauge_projector, ord=2)
            )
            record = {
                "delta": delta,
                "ratio_abs_beta_over_zeta": ratio,
                "beta": beta,
                "zeta": zeta,
                "basis_chart": chart,
                "rescaled_boundary_sigma_min": float(singular_values[-1]),
                "rescaled_boundary_sigma_max": float(singular_values[0]),
                "transfer_factor_norm_2": float(
                    np.linalg.svd(transfer_factor, compute_uv=False)[0]
                ),
                "state_map_norm_2": float(np.linalg.svd(state, compute_uv=False)[0]),
                "gauge_block_distance_to_endpoint": gauge_distance,
                "gauge_block_distance_over_delta": gauge_distance / delta,
                "row_scaling_projector_distance_2": projector_distance,
                "expected_delta": delta,
                "factorization_max_abs_error": float(
                    np.max(np.abs(direct_transfer - factored_transfer))
                ),
                "principal_mode_residual": mode_residual,
                "finite": bool(
                    np.all(np.isfinite(rescaled_boundary))
                    and np.all(np.isfinite(transfer_factor))
                    and np.all(np.isfinite(direct_transfer))
                ),
            }
            group.append(record)
            cases.append(record)

        summaries.append(
            {
                "delta": delta,
                "case_count": len(group),
                "minimum_rescaled_boundary_sigma_min": min(
                    row["rescaled_boundary_sigma_min"] for row in group
                ),
                "maximum_transfer_factor_norm_2": max(
                    row["transfer_factor_norm_2"] for row in group
                ),
                "maximum_state_map_norm_2": max(row["state_map_norm_2"] for row in group),
                "maximum_gauge_block_distance": max(
                    row["gauge_block_distance_to_endpoint"] for row in group
                ),
                "maximum_gauge_block_distance_over_delta": max(
                    row["gauge_block_distance_over_delta"] for row in group
                ),
            }
        )

    max_factor_error = max(row["factorization_max_abs_error"] for row in cases)
    max_projector_error = max(
        abs(row["row_scaling_projector_distance_2"] - row["expected_delta"])
        for row in cases
    )
    max_mode_residual = max(row["principal_mode_residual"] for row in cases)
    checks = {
        "exact_transfer_factorization_matches_direct_solve": max_factor_error
        < FACTOR_IDENTITY_TOLERANCE,
        "row_scaling_distance_equals_delta": max_projector_error
        < ROW_PROJECTOR_IDENTITY_TOLERANCE,
        "rescaled_boundary_maps_are_nonsingular_on_sampled_charts": all(
            row["rescaled_boundary_sigma_min"] > 1.0e-10 for row in cases
        ),
        "all_sampled_state_and_transfer_factors_are_finite": all(
            row["finite"] for row in cases
        ),
        "principal_modes_satisfy_registered_system": max_mode_residual < 1.0e-8,
        "gauge_block_distance_envelopes_contract_with_delta": all(
            right["maximum_gauge_block_distance"]
            < left["maximum_gauge_block_distance"]
            for left, right in zip(summaries, summaries[1:])
        ),
        "ratio_and_jordan_charts_are_all_covered": (
            len(cases) == 84
            and min(RATIOS) <= 1.0e-8
            and max(RATIOS) >= 1.0e8
            and all(
                chart in {row["basis_chart"] for row in cases}
                for chart in (
                    "unit_generic_eigenmodes",
                    "normalized_confluent_divided_difference",
                    "source_ode_consistent_jordan",
                )
            )
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}

    source_hashes = dict(
        json.loads(OPERATOR_ARTIFACT.read_text(encoding="utf-8"))["VERIFICATION"]["source_hashes"]
    )
    source_hashes[_relative(Path(__file__))] = _hash(Path(__file__))
    source_hashes[_relative(OPERATOR_SCRIPT)] = _hash(OPERATOR_SCRIPT)
    source_hashes[_relative(OPERATOR_ARTIFACT)] = _hash(OPERATOR_ARTIFACT)
    source_hashes[_relative(RATIO_ARTIFACT)] = _hash(RATIO_ARTIFACT)

    status = "PASS_RESCALED_TRANSFER_FACTORIZATION_SCREEN" if all(checks.values()) else "FAIL_OR_UNRESOLVED_RESCALED_TRANSFER_SCREEN"
    controlling_blocker = "uniform_inverse_bound_for_rescaled_boundary_map_and_uniform_gauge_block_lipschitz_bound_not_proved"
    claim_boundary = (
        "exact row-scaling/factorization identities plus finite positive-real compactified-ratio screening; "
        "uniform invertibility and Lipschitz constants are not proved"
    )
    what_closed = [
        "With S=D*C and U=W*S^-1, the registered transfer obeys the exact identity T=W*C^-1=U*D.",
        "For P_G=diag(0_6,I_4,0_20), the row scaling has the exact max-norm identity ||D-P_G||_2=delta=max(|beta|,zeta).",
        "Across 84 sampled ratio/delta points, D*S^-1 factorization residuals are below tolerance, rescaled boundary maps remain full-rank on the sampled charts, and the surviving gauge block approaches the endpoint as delta shrinks.",
    ]
    what_open = [
        "A continuous lower singular-value bound for S on all compactified ratios and a uniform bound for ||U|| remain unproved.",
        "A uniform Lipschitz estimate for U*P_G in delta, including chart transitions, remains unproved; without it the conditional O(delta) remainder is not a theorem.",
        "Imaginary-frequency/high-frequency uniformity, norm-interface reconciliation, and full variable-coefficient CPBC evolution remain open.",
    ]
    evidence_artifacts = [
        {"path": _relative(Path(__file__)), "sha256": source_hashes[_relative(Path(__file__))]},
        {"path": _relative(OPERATOR_SCRIPT), "sha256": source_hashes[_relative(OPERATOR_SCRIPT)]},
        {"path": _relative(OPERATOR_ARTIFACT), "sha256": source_hashes[_relative(OPERATOR_ARTIFACT)]},
        {"path": _relative(RATIO_ARTIFACT), "sha256": source_hashes[_relative(RATIO_ARTIFACT)]},
    ]
    equation = {
        "source_row_scaling": "S=D*C; D=diag(zeta*I6,I4,min(abs(beta),zeta)*I10,abs(beta)*I10)",
        "transfer_factor": "U=W*S^-1",
        "exact_transfer_factorization": "T=W*C^-1=U*D",
        "surviving_source_projector": "P_G=diag(0_6,I4,0_20)",
        "exact_row_remainder": "||D-P_G||_2=delta=max(abs(beta),zeta)",
        "conditional_remainder_decomposition": "T-T0=U*(D-P_G)+(U*P_G-T0)",
        "conditional_bound": "if ||U||_2<=K and ||U*P_G-T0||_2<=L*delta uniformly, then ||T-T0||_2<=(K+L)*delta",
        "claim_boundary": claim_boundary,
    }
    major = {
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_RESCALED_TRANSFER_FACTORIZATION",
        "topic": "core_curved_3p1",
        "closure_level": "PARTIAL",
        "what_is_closed": what_closed,
        "what_remains_open": what_open,
        "dependency_unlocked": "none; Core curved 3+1 remains PARTIAL and Gravity remains blocked",
        "evidence_artifacts": evidence_artifacts,
        "open_blockers": what_open,
        "controlling_blocker": controlling_blocker,
        "equation_or_mapping": equation,
        "units": "Dimensionless frozen-coefficient Fourier-Laplace variables with tangential omega=1.",
        "derivation_class": "exact row-scaling, projector-distance, and transfer-factorization identities with finite compactified-ratio verification",
        "observable": "rescaled boundary-map singular values and state-transfer response blocks",
        "data_role": "internal analytic/numerical diagnostic; no empirical data, fitting, or holdout",
        "verification_status": status,
        "claim_boundary": claim_boundary,
    }
    return {
        "schema_version": "core-curved-3p1-gh-rinne-rescaled-transfer-factorization-v1",
        "artifact": "curved_3p1_gh_rinne_rescaled_transfer_factorization",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "major_result_id": major["major_result_id"],
        "major_result": major,
        "closure_level": "PARTIAL",
        "MAJOR_RESULT_CLOSURE": "PARTIAL",
        "WHAT_IS_ACTUALLY_CLOSED": what_closed,
        "WHAT_REMAINS_OPEN": what_open,
        "DEPENDENCY_UNLOCKED": major["dependency_unlocked"],
        "STATUS": status,
        "EQUATION_OR_MAPPING": equation,
        "VERIFICATION": {
            "checks": checks,
            "deltas": list(DELTAS),
            "ratio_grid": list(RATIOS),
            "cases": cases,
            "summaries": summaries,
            "maximum_factorization_error": max_factor_error,
            "maximum_projector_identity_error": max_projector_error,
            "maximum_principal_mode_residual": max_mode_residual,
            "source_hashes": source_hashes,
        },
        "CONTROLLING_BLOCKER": controlling_blocker,
        "NEXT_ACTION": "Prove a continuous positive lower bound for sigma_min(S) in overlapping generic/confluent/Jordan charts, then prove a uniform delta-Lipschitz bound for U*P_G; extend after that to the imaginary-frequency boundary.",
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
                "summaries": artifact["VERIFICATION"]["summaries"],
            },
            indent=2,
            ensure_ascii=True,
        )
    )
    return 0 if all(artifact["VERIFICATION"]["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
