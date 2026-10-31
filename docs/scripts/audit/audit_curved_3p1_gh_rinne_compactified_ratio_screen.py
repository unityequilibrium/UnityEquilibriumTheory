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
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_compactified_ratio_screen.json"
DELTAS = (1.0e-2, 1.0e-3, 1.0e-4, 1.0e-5)
RATIOS = tuple(
    sorted(
        {float(value) for value in np.logspace(-8.0, 8.0, 17)}
        | {0.99, 0.999999, 1.000001, 1.01}
    )
)
REMAINDER_SCREEN_LIMIT = 24.0


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load audit dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OPERATOR = _load("_uet_joint_real_state_transfer_operator", OPERATOR_SCRIPT)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _sample(delta: float, ratio: float) -> dict[str, Any]:
    # Parameterize the max-norm shell so both |beta| and zeta are <= delta.
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

    transfer = OPERATOR._state_operator(boundary, state)
    endpoint = np.zeros((40, 30), dtype=complex)
    endpoint[:, :10] = OPERATOR._zero_shift_operator(1.0e-10)
    distance = float(np.linalg.norm(transfer - endpoint, ord="fro"))
    return {
        "delta": delta,
        "ratio_abs_beta_over_zeta": ratio,
        "beta": beta,
        "zeta": zeta,
        "basis_chart": chart,
        "state_operator_shape": list(transfer.shape),
        "state_operator_norm_2": float(np.linalg.svd(transfer, compute_uv=False)[0]),
        "frobenius_distance_to_endpoint_reference": distance,
        "distance_over_delta": distance / delta,
        "principal_mode_residual": residual,
        "all_operator_entries_finite": bool(np.all(np.isfinite(transfer))),
    }


def build_artifact() -> dict[str, Any]:
    cases = [_sample(delta, ratio) for delta in DELTAS for ratio in RATIOS]
    summaries = []
    for delta in DELTAS:
        group = [row for row in cases if row["delta"] == delta]
        summaries.append(
            {
                "delta": delta,
                "case_count": len(group),
                "ratio_min": min(row["ratio_abs_beta_over_zeta"] for row in group),
                "ratio_max": max(row["ratio_abs_beta_over_zeta"] for row in group),
                "operator_norm_min": min(row["state_operator_norm_2"] for row in group),
                "operator_norm_max": max(row["state_operator_norm_2"] for row in group),
                "max_endpoint_distance": max(
                    row["frobenius_distance_to_endpoint_reference"] for row in group
                ),
                "max_distance_over_delta": max(row["distance_over_delta"] for row in group),
            }
        )

    max_remainder_ratio = max(row["distance_over_delta"] for row in cases)
    max_operator_norm = max(row["state_operator_norm_2"] for row in cases)
    max_residual = max(row["principal_mode_residual"] for row in cases)
    max_distances = [row["max_endpoint_distance"] for row in summaries]
    checks = {
        "all_compactified_ratio_samples_are_finite": all(
            row["all_operator_entries_finite"] for row in cases
        ),
        "all_cases_use_registered_40_by_30_transfer": all(
            row["state_operator_shape"] == [40, 30] for row in cases
        ),
        "principal_modes_satisfy_registered_system": max_residual < 1.0e-8,
        "sampled_remainder_over_delta_below_screen_limit": max_remainder_ratio
        < REMAINDER_SCREEN_LIMIT,
        "sampled_transfer_norms_remain_below_five": max_operator_norm < 5.0,
        "endpoint_distance_envelopes_contract_with_delta": all(
            right < left for left, right in zip(max_distances, max_distances[1:])
        ),
        "ratio_grid_covers_both_compactified_endpoints_and_jordan_chart": (
            min(RATIOS) <= 1.0e-8
            and max(RATIOS) >= 1.0e8
            and 0.999999 in RATIOS
            and 1.0 in RATIOS
            and 1.000001 in RATIOS
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    source_hashes = dict(
        json.loads(OPERATOR_ARTIFACT.read_text(encoding="utf-8"))["VERIFICATION"]["source_hashes"]
    )
    source_hashes[_relative(Path(__file__))] = _hash(Path(__file__))
    source_hashes[_relative(OPERATOR_SCRIPT)] = _hash(OPERATOR_SCRIPT)
    source_hashes[_relative(OPERATOR_ARTIFACT)] = _hash(OPERATOR_ARTIFACT)
    status = "PASS_COMPACTIFIED_POSITIVE_REAL_RATIO_SCREEN" if all(checks.values()) else "FAIL_OR_UNRESOLVED_COMPACTIFIED_RATIO_SCREEN"
    controlling_blocker = "continuous_analytic_or_rigorously_interval_certified_remainder_bound_over_all_positive_real_ratios_missing"
    claim_boundary = (
        "finite positive-real max-norm-shell samples over ratios 1e-8 to 1e8, including corrected Jordan/confluent charts; "
        "not a continuous all-ratio remainder proof, complex-frequency Kreiss estimate, or Core-parent closure"
    )
    major = {
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_COMPACTIFIED_POSITIVE_REAL_RATIO_SCREEN",
        "topic": "core_curved_3p1",
        "closure_level": "PARTIAL",
        "what_is_closed": [
            "A max-norm-shell parameterization samples both |beta| and zeta <= delta while spanning 16 decades in |beta|/zeta, including both ratio endpoints and the corrected Jordan chart.",
            f"Across {len(cases)} cases, ||T-T0||_F/delta stays below {REMAINDER_SCREEN_LIMIT:g} and the sampled state-transfer norm stays below 5; these are finite numerical screens, not proved constants.",
        ],
        "what_remains_open": [
            "A continuous analytic or rigorously interval-certified remainder bound over every ratio and delta remains unproved.",
            "The imaginary-frequency boundary, high-frequency compactification, fixed-background norm interface, and full variable-coefficient CPBC evolution remain open.",
        ],
        "dependency_unlocked": "none; Core curved 3+1 remains PARTIAL and Gravity remains blocked",
        "evidence_artifacts": [
            {"path": _relative(Path(__file__)), "sha256": source_hashes[_relative(Path(__file__))]},
            {"path": _relative(OPERATOR_SCRIPT), "sha256": source_hashes[_relative(OPERATOR_SCRIPT)]},
            {"path": _relative(OPERATOR_ARTIFACT), "sha256": source_hashes[_relative(OPERATOR_ARTIFACT)]},
        ],
        "open_blockers": [
            "continuous remainder bound over every positive-real ratio and delta",
            "imaginary-frequency boundary and high-frequency compactification",
            "fixed-background norm interface and full variable-coefficient CPBC evolution",
        ],
        "controlling_blocker": controlling_blocker,
        "equation_or_mapping": {
            "state_transfer": "T(beta,zeta)=W(beta,zeta)*C(beta,zeta)^-1",
            "compactified_direction": "delta=max(abs(beta),zeta); r=abs(beta)/zeta; if r<=1 then zeta=delta,beta=-r*delta; if r>=1 then abs(beta)=delta,zeta=delta/r",
            "sampled_remainder": "rho(delta,r)=||T(beta,zeta)-T0||_F/delta",
            "screen_limit": REMAINDER_SCREEN_LIMIT,
            "claim_boundary": claim_boundary,
        },
        "units": "Dimensionless frozen-coefficient Fourier-Laplace variables with tangential omega=1.",
        "derivation_class": "compactified directional parameterization with generic, confluent, and ODE-consistent Jordan state-transfer evaluation",
        "observable": "spectral norm of the 40x30 state response operator and Frobenius distance to the zero-shift endpoint reference",
        "data_role": "internal numerical diagnostic; no empirical data, fitting, or holdout",
        "verification_status": status,
        "claim_boundary": claim_boundary,
    }
    return {
        "schema_version": "core-curved-3p1-gh-rinne-compactified-ratio-screen-v1",
        "artifact": "curved_3p1_gh_rinne_compactified_ratio_screen",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "major_result_id": major["major_result_id"],
        "major_result": major,
        "closure_level": "PARTIAL",
        "MAJOR_RESULT_CLOSURE": "PARTIAL",
        "WHAT_IS_ACTUALLY_CLOSED": major["what_is_closed"],
        "WHAT_REMAINS_OPEN": major["what_remains_open"],
        "DEPENDENCY_UNLOCKED": major["dependency_unlocked"],
        "STATUS": status,
        "EQUATION_OR_MAPPING": major["equation_or_mapping"],
        "VERIFICATION": {
            "checks": checks,
            "deltas": list(DELTAS),
            "ratio_grid": list(RATIOS),
            "cases": cases,
            "summaries": summaries,
            "maximum_distance_over_delta": max_remainder_ratio,
            "maximum_transfer_norm": max_operator_norm,
            "maximum_principal_mode_residual": max_residual,
            "source_hashes": source_hashes,
        },
        "CONTROLLING_BLOCKER": major["controlling_blocker"],
        "NEXT_ACTION": "Derive explicit compactified-ratio formulas for the physical state-transfer blocks and bound their delta derivative uniformly, including the confluent Jordan chart; then extend to the imaginary-frequency boundary.",
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
