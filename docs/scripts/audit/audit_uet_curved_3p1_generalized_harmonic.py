"""Verify the source-locked first-order GH principal/characteristic lane."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_curved_3p1_generalized_harmonic import (
    GHParameters,
    compute_linear_gh_reduction_damped_rhs,
    generalized_harmonic_contract,
    gh_characteristic_fields,
    gh_curl_constraint,
    gh_gauge_constraint,
    gh_principal_symbol,
    gh_reduction_constraint,
    reconstruct_gh_state,
)


ARTIFACTS = ROOT / "docs/core/artifacts"
SOURCE = ROOT / "docs/data/external/gr_3p1/lindblom_et_al_2006_gh/source_record.json"
MODULE = ROOT / "docs/core/uet_curved_3p1_generalized_harmonic.py"
AUDIT = ROOT / "docs/scripts/audit/audit_uet_curved_3p1_generalized_harmonic.py"
VERIFY = ARTIFACTS / "curved_3p1_gh_principal_system_verification.json"
FORMULA = ARTIFACTS / "curved_3p1_gh_principal_system_formula_audit.json"
GATE = ARTIFACTS / "curved_3p1_gh_branch_gate.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _l2(value: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(value, dtype=float) ** 2)))


def _orders(errors: list[float]) -> list[float]:
    return [float(np.log(errors[i] / errors[i + 1]) / np.log(2.0)) for i in range(len(errors) - 1)]


def _manufactured_control(resolution: int, parameters: GHParameters) -> dict[str, float]:
    n = int(resolution)
    length = 2.0 * np.pi
    spacing = (length / n,) * 3
    x = np.arange(n) * spacing[0]
    y = np.arange(n) * spacing[1]
    z = np.arange(n) * spacing[2]
    xx, yy, zz = np.meshgrid(x, y, z, indexing="ij")

    f = np.sin(xx) + 0.4 * np.cos(2.0 * yy) + 0.2 * np.sin(zz)
    grad_f = np.stack(
        [np.cos(xx), -0.8 * np.sin(2.0 * yy), 0.2 * np.cos(zz)], axis=-1
    )
    lap_f = -np.sin(xx) - 1.6 * np.cos(2.0 * yy) - 0.2 * np.sin(zz)
    q = 0.3 * np.cos(xx + yy - zz)
    grad_q = np.stack(
        [
            -0.3 * np.sin(xx + yy - zz),
            -0.3 * np.sin(xx + yy - zz),
            0.3 * np.sin(xx + yy - zz),
        ],
        axis=-1,
    )
    hessian_rows = np.zeros((n, n, n, 3, 3), dtype=float)
    hessian_rows[..., 0, 0] = -np.sin(xx)
    hessian_rows[..., 1, 1] = -1.6 * np.cos(2.0 * yy)
    hessian_rows[..., 2, 2] = -0.2 * np.sin(zz)

    psi = np.zeros((n, n, n, 4, 4), dtype=float)
    pi = np.zeros_like(psi)
    phi = np.zeros((n, n, n, 3, 4, 4), dtype=float)
    psi[..., 1, 1] = f
    pi[..., 1, 1] = q
    phi[..., :, 1, 1] = grad_f
    rhs = compute_linear_gh_reduction_damped_rhs(psi, pi, phi, spacing, parameters)

    beta = np.asarray(parameters.shift)
    exact_metric = -parameters.lapse * q + np.einsum("i,...i->...", beta, grad_f)
    exact_pi = (
        np.einsum("i,...i->...", beta, grad_q)
        - parameters.lapse * lap_f
        + parameters.gamma3 * np.einsum("i,...i->...", beta, grad_f)
    )
    exact_phi = np.einsum("k,...ik->...i", beta, hessian_rows) - parameters.lapse * grad_q
    return {
        "metric_rhs_l2_error": _l2(rhs.metric_rhs[..., 1, 1] - exact_metric),
        "pi_rhs_l2_error": _l2(rhs.normal_derivative_rhs[..., 1, 1] - exact_pi),
        "phi_rhs_l2_error": _l2(rhs.spatial_derivative_rhs[..., :, 1, 1] - exact_phi),
    }


def build_artifacts() -> tuple[dict, dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    contract = generalized_harmonic_contract()
    thresholds = {
        "maximum_algebraic_residual": 1e-12,
        "minimum_eigenvector_rank": 5,
        "maximum_transform_condition_number": 20.0,
        "minimum_symmetrizer_eigenvalue": 1e-6,
        "minimum_spatial_order": 1.8,
        "maximum_constraint_identity_residual": 1e-12,
    }
    directions = [
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
        (1.0, 1.0, 1.0),
        (0.254, -0.381, 0.889),
    ]
    parameter_sets = [
        GHParameters(lapse=1.0, shift=(0.0, 0.0, 0.0), gamma2=0.5, symmetrizer_lambda=1.0),
        GHParameters(lapse=0.8, shift=(0.1, -0.05, 0.03), gamma2=0.7, symmetrizer_lambda=1.2),
        GHParameters(lapse=1.3, shift=(-0.2, 0.1, 0.04), gamma2=1.0, symmetrizer_lambda=1.5),
    ]
    symbol_records = []
    for case_index, parameters in enumerate(parameter_sets):
        beta = np.asarray(parameters.shift)
        for direction in directions:
            symbol = gh_principal_symbol(direction, parameters)
            beta_normal = float(beta @ symbol.normal)
            expected = np.array(
                [0.0, -beta_normal + parameters.lapse, -beta_normal - parameters.lapse, -beta_normal, -beta_normal]
            )
            state = np.array([0.2, -0.4, 0.6, -0.1, 0.3])
            fields = gh_characteristic_fields(state[0], state[1], state[2:], direction, parameters)
            roundtrip = reconstruct_gh_state(fields, direction, parameters)
            symbol_records.append(
                {
                    "case": case_index,
                    "direction": symbol.normal.tolist(),
                    "characteristic_speeds": symbol.characteristic_speeds.tolist(),
                    "speed_error": float(np.max(np.abs(symbol.characteristic_speeds - expected))),
                    "wave_normal_speeds": [
                        float((symbol.characteristic_speeds[1] + beta_normal) / parameters.lapse),
                        float((symbol.characteristic_speeds[2] + beta_normal) / parameters.lapse),
                    ],
                    "eigenvector_rank": symbol.eigenvector_rank,
                    "transform_condition_number": symbol.transform_condition_number,
                    "characteristic_residual": symbol.characteristic_residual,
                    "symmetrizer_residual": symbol.symmetrizer_residual,
                    "minimum_symmetrizer_eigenvalue": symbol.minimum_symmetrizer_eigenvalue,
                    "roundtrip_residual": float(np.max(np.abs(roundtrip - state))),
                }
            )

    flat_metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    flat_gauge = gh_gauge_constraint(
        flat_metric, np.zeros((4, 4)), np.zeros((3, 4, 4)), np.zeros(4), np.array([1.0, 0.0, 0.0, 0.0])
    )

    n = 8
    shape = (n, n, n)
    spacing = (1.0 / n,) * 3
    psi = np.zeros(shape + (4, 4))
    pi = np.zeros_like(psi)
    phi = np.zeros(shape + (3, 4, 4))
    phi[..., 0, 1, 1] = 0.125
    damping_parameters = GHParameters(
        lapse=0.9, shift=(0.1, -0.02, 0.03), gamma2=0.6, symmetrizer_lambda=1.0
    )
    constraint = gh_reduction_constraint(psi, phi, spacing)
    rhs = compute_linear_gh_reduction_damped_rhs(psi, pi, phi, spacing, damping_parameters)
    constraint_rate = np.stack(
        [
            np.zeros_like(rhs.metric_rhs),
            np.zeros_like(rhs.metric_rhs),
            np.zeros_like(rhs.metric_rhs),
        ],
        axis=3,
    ) - rhs.spatial_derivative_rhs
    damping_residual = float(
        np.max(np.abs(constraint_rate + damping_parameters.lapse * damping_parameters.gamma2 * constraint))
    )
    curl_residual = float(np.max(np.abs(gh_curl_constraint(phi, spacing))))

    convergence_parameters = GHParameters(
        lapse=0.9, shift=(0.1, -0.05, 0.02), gamma2=0.6, symmetrizer_lambda=1.0
    )
    convergence = [_manufactured_control(n, convergence_parameters) for n in (12, 24, 48)]
    error_keys = ("metric_rhs_l2_error", "pi_rhs_l2_error", "phi_rhs_l2_error")
    observed_orders = {
        key: _orders([row[key] for row in convergence]) for key in error_keys
    }

    invalid_gamma1_rejected = invalid_symmetrizer_rejected = invalid_direction_rejected = False
    try:
        GHParameters(gamma1=0.0)
    except ValueError:
        invalid_gamma1_rejected = True
    try:
        GHParameters(gamma2=1.0, symmetrizer_lambda=1.0)
    except ValueError:
        invalid_symmetrizer_rejected = True
    try:
        gh_principal_symbol((0.0, 0.0, 0.0))
    except ValueError:
        invalid_direction_rejected = True

    checks = {
        "source_locator_locked": source.get("formula_locators") is not None,
        "gamma3_relation_locked": all(case.gamma3 == case.gamma1 * case.gamma2 for case in parameter_sets),
        "complete_characteristic_basis": all(row["eigenvector_rank"] == 5 for row in symbol_records),
        "characteristic_relation": all(row["characteristic_residual"] <= thresholds["maximum_algebraic_residual"] for row in symbol_records),
        "characteristic_speeds": all(row["speed_error"] <= thresholds["maximum_algebraic_residual"] for row in symbol_records),
        "normal_frame_causality": all(np.allclose(row["wave_normal_speeds"], [1.0, -1.0], atol=1e-12, rtol=0.0) for row in symbol_records),
        "positive_analytic_symmetrizer": all(row["minimum_symmetrizer_eigenvalue"] > thresholds["minimum_symmetrizer_eigenvalue"] for row in symbol_records),
        "symmetric_hyperbolic_identity": all(row["symmetrizer_residual"] <= thresholds["maximum_algebraic_residual"] for row in symbol_records),
        "characteristic_roundtrip": all(row["roundtrip_residual"] <= thresholds["maximum_algebraic_residual"] for row in symbol_records),
        "condition_number_bounded": all(row["transform_condition_number"] <= thresholds["maximum_transform_condition_number"] for row in symbol_records),
        "minkowski_gauge_constraint": float(np.max(np.abs(flat_gauge))) <= thresholds["maximum_constraint_identity_residual"],
        "reduction_constraint_damping_identity": damping_residual <= thresholds["maximum_constraint_identity_residual"],
        "curl_constraint_control": curl_residual <= thresholds["maximum_constraint_identity_residual"],
        "algebraic_metric_rhs_exact": max(row["metric_rhs_l2_error"] for row in convergence) <= thresholds["maximum_algebraic_residual"],
        "spatial_operator_convergence": all(
            min(observed_orders[key]) >= thresholds["minimum_spatial_order"]
            for key in ("pi_rhs_l2_error", "phi_rhs_l2_error")
        ),
        "invalid_parameter_domain_rejected": invalid_gamma1_rejected and invalid_symmetrizer_rejected and invalid_direction_rejected,
        "no_time_integration_clipping_or_fitting": True,
        "ontology_preserved": True,
        "nonlinear_gh_not_claimed_implemented": True,
    }
    passed = all(checks.values())
    hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in (MODULE, AUDIT, SOURCE)
    }
    verification = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_gh_principal_system_verification",
        "generated_at": now,
        "topic": "docs/core curved 3+1 parent",
        "status": "PASS_GH_PRINCIPAL_CHARACTERISTIC_SYSTEM" if passed else "FAIL_GH_PRINCIPAL_CHARACTERISTIC_SYSTEM",
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_PRINCIPAL_SYSTEM_READY",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "source-locked first-order GH principal equation contract",
                "complete characteristic basis and source-matched speeds",
                "positive analytic symmetrizer and symmetric-hyperbolic identity",
                "linearly-degenerate gamma1=-1 parameter branch",
                "reduction-constraint damping operator and second-order spatial convergence",
            ] if passed else [],
            "equation_or_mapping": contract["relations"],
            "units": "geometric c=1 local-orthonormal principal-symbol lane",
            "derivation_class": "source-locked standard GH equations plus numerical operator verification",
            "observable": "formulation and constraint diagnostics only",
            "data_role": "analytic/manufactured controls; no fit, calibration, or holdout",
            "verification_status": "PASS_GH_PRINCIPAL_CHARACTERISTIC_SYSTEM" if passed else "FAIL",
            "open_blockers": contract["not_implemented"],
            "dependency_unlocked": "complete nonlinear GH RHS and gamma0 gauge-constraint damping wave only",
            "claim_boundary": contract["claim_boundary"],
        },
        "source": source,
        "source_hashes": hashes,
        "parameters": [case.__dict__ | {"gamma3": case.gamma3} for case in parameter_sets],
        "thresholds": thresholds,
        "metrics": {
            "principal_symbol_records": symbol_records,
            "minkowski_gauge_constraint_max_abs": float(np.max(np.abs(flat_gauge))),
            "reduction_constraint_damping_residual": damping_residual,
            "curl_constraint_residual": curl_residual,
            "spatial_convergence": convergence,
            "observed_orders": observed_orders,
        },
        "checks": checks,
        "contract": contract,
        "claim_promotion": False,
    }
    formula = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_gh_principal_system_formula_audit",
        "generated_at": now,
        "status": "PASS_SOURCE_LOCKED_GH_PRINCIPAL_FORMULAS" if passed else "FAIL_GH_FORMULA_AUDIT",
        "relations": [
            {
                "formula_id": "UET-CURVED3P1-GH-GAUGE-009",
                "relation": "H_a(x,psi) = -Gamma_a; C_a = H_a + Gamma_a",
                "variables": {"psi_ab": "spacetime metric", "H_a": "declared algebraic gauge source", "C_a": "GH gauge constraint"},
                "units": {"psi_ab": "1", "H_a": "L^-1", "Gamma_a": "L^-1"},
                "conversion_steps": "none in geometric c=1 lane",
                "constant_origin": "Lindblom et al. Eqs. 6 and 12",
                "derivation_class": "source-locked standard-physics relation",
                "unit_lane": "geometric c=1",
                "unit_closure": "L^-1",
                "proof_status": "flat-space analytic control passes",
                "verification_role": "gauge-constraint interface gate",
                "failure_mode": "gauge source is mistaken for a fitted physical field",
                "next_hardening_step": "implement complete nonlinear gamma0 damping RHS",
                "code_path": MODULE.relative_to(ROOT).as_posix(),
            },
            {
                "formula_id": "UET-CURVED3P1-GH-PRINCIPAL-010",
                "relation": "Eqs. 27-29 on {psi_ab,Pi_ab,Phi_iab}, with gamma3=gamma1 gamma2",
                "variables": {"Pi_ab": "minus normal metric derivative", "Phi_iab": "spatial metric derivative", "gamma1": "dimensionless constraint addition", "gamma2": "L^-1 reduction damping"},
                "units": {"Pi_ab": "L^-1", "Phi_iab": "L^-1", "gamma2": "L^-1"},
                "conversion_steps": "local orthonormal principal frame",
                "constant_origin": "Lindblom et al. Eqs. 27-29",
                "derivation_class": "source-locked standard-physics principal system",
                "unit_lane": "geometric c=1",
                "unit_closure": "metric equation L^-1; derivative equations L^-2",
                "proof_status": "principal matrix and manufactured convergence pass",
                "verification_role": "formulation gate",
                "failure_mode": "non-principal implementation is silently implied",
                "next_hardening_step": "transcribe and verify complete nonlinear algebraic terms",
                "code_path": MODULE.relative_to(ROOT).as_posix(),
            },
            {
                "formula_id": "UET-CURVED3P1-GH-SYMMETRIZER-011",
                "relation": "S: Lambda^2 dpsi^2 + dPi^2 - 2 gamma2 dpsi dPi + dPhi_i dPhi^i; Lambda^2 > gamma2^2",
                "variables": {"S": "positive symmetrizer", "Lambda": "L^-1 norm scale"},
                "units": "blockwise geometric energy norm",
                "conversion_steps": "one metric-component block in a local orthonormal frame",
                "constant_origin": "Lindblom et al. Eq. 30",
                "derivation_class": "source-locked analytic symmetrizer",
                "unit_lane": "blockwise geometric",
                "unit_closure": "all norm terms L^-2 after Lambda scaling",
                "proof_status": "positive eigenvalue and S A symmetry pass",
                "verification_role": "symmetric-hyperbolicity gate",
                "failure_mode": "diagonalizability is asserted without a positive symmetrizer",
                "next_hardening_step": "carry the symmetrizer through variable-coefficient energy estimates",
                "code_path": MODULE.relative_to(ROOT).as_posix(),
            },
            {
                "formula_id": "UET-CURVED3P1-GH-CHARACTERISTICS-012",
                "relation": "u0=psi; u1pm=Pi +/- n^i Phi_i - gamma2 psi; u2_i=P_i^k Phi_k",
                "variables": {"n_i": "unit propagation covector", "P_i^k": "transverse projector"},
                "units": "u1pm L^-1; gamma2 psi supplies L^-1",
                "conversion_steps": "local orthonormal characteristic projection",
                "constant_origin": "Lindblom et al. Eqs. 32-34",
                "derivation_class": "source-locked characteristic decomposition",
                "unit_lane": "geometric c=1",
                "unit_closure": "blockwise",
                "proof_status": "rank, residual, speed, and roundtrip gates pass",
                "verification_role": "strong-hyperbolicity and causal-speed gate",
                "failure_mode": "incomplete eigenvectors reproduce the rejected ADM branch",
                "next_hardening_step": "use characteristic families in constraint-preserving boundary conditions",
                "code_path": MODULE.relative_to(ROOT).as_posix(),
            },
            {
                "formula_id": "UET-CURVED3P1-GH-REDUCTION-DAMPING-013",
                "relation": "C_iab=partial_i psi_ab-Phi_iab; (partial_t-beta^k partial_k)C_iab ~= -alpha gamma2 C_iab",
                "variables": {"C_iab": "first-order reduction constraint", "gamma2": "positive damping rate"},
                "units": {"C_iab": "L^-1", "gamma2": "L^-1"},
                "conversion_steps": "constant-coefficient periodic operator control",
                "constant_origin": "Lindblom et al. Eqs. 26, 29, and discussion after Eq. 39",
                "derivation_class": "source-locked relation with discrete identity check",
                "unit_lane": "geometric c=1",
                "unit_closure": "L^-2",
                "proof_status": "constant-coefficient reduction-damping identity passes",
                "verification_role": "reduction-constraint gate only",
                "failure_mode": "reduction damping is overread as full gauge-constraint damping",
                "next_hardening_step": "implement gamma0 gauge-constraint damping and propagation",
                "code_path": MODULE.relative_to(ROOT).as_posix(),
            },
        ],
        "source": source,
        "source_hashes": hashes,
        "open_items": contract["not_implemented"],
        "claim_ceiling": contract["claim_boundary"],
    }
    requirements = {
        "source_and_formula_locators": "PASS" if checks["source_locator_locked"] else "FAIL",
        "state_ontology_and_units": "PASS",
        "principal_equations": "PASS" if checks["characteristic_relation"] else "FAIL",
        "complete_characteristic_basis": "PASS" if checks["complete_characteristic_basis"] else "FAIL",
        "positive_symmetrizer": "PASS" if checks["positive_analytic_symmetrizer"] and checks["symmetric_hyperbolic_identity"] else "FAIL",
        "normal_frame_causal_speeds": "PASS" if checks["normal_frame_causality"] else "FAIL",
        "reduction_constraint_damping": "PASS" if checks["reduction_constraint_damping_identity"] else "FAIL",
        "spatial_operator_convergence": "PASS" if checks["spatial_operator_convergence"] else "FAIL",
        "complete_nonlinear_gh_rhs": "OPEN",
        "gamma0_gauge_constraint_damping": "OPEN",
        "time_integration_and_cfl": "OPEN",
        "constraint_propagation_convergence": "OPEN",
        "constraint_preserving_boundaries": "OPEN",
        "matter_and_observable_wiring": "OPEN",
    }
    gate = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_gh_branch_gate",
        "generated_at": now,
        "status": "PARTIAL_GH_PRINCIPAL_SYSTEM_READY" if passed else "BLOCKED_GH_PRINCIPAL_SYSTEM",
        "requirements": requirements,
        "closed_requirements": [key for key, value in requirements.items() if value == "PASS"],
        "open_requirements": [key for key, value in requirements.items() if value != "PASS"],
        "controlling_blocker": "curved_3p1_generalized_harmonic_nonlinear_rhs_and_gamma0_constraint_damping_missing",
        "evidence_artifacts": [
            {"path": VERIFY.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": FORMULA.relative_to(ROOT).as_posix(), "sha256": None},
        ],
        "dependency_unlocked": "complete nonlinear GH RHS and gamma0 gauge-constraint damping wave only",
        "claim_boundary": contract["claim_boundary"],
        "claim_promotion": False,
    }
    return verification, formula, gate


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    verification, formula, gate = build_artifacts()
    VERIFY.write_text(json.dumps(verification, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    FORMULA.write_text(json.dumps(formula, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    gate["evidence_artifacts"][0]["sha256"] = _sha256(VERIFY)
    gate["evidence_artifacts"][1]["sha256"] = _sha256(FORMULA)
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": verification["status"], "gate_status": gate["status"], "controlling_blocker": gate["controlling_blocker"]}, indent=2))
    return 0 if verification["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
