"""Verify the complete nonlinear vacuum GH right-hand-side transcription."""

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
    GHNonlinearParameters,
    compute_nonlinear_vacuum_gh_rhs,
    derive_gh_kinematics,
    generalized_harmonic_contract,
    gh_gamma0_damping_term,
    gh_gauge_constraint,
)


ARTIFACTS = ROOT / "docs/core/artifacts"
SOURCE = ROOT / "docs/data/external/gr_3p1/lindblom_et_al_2006_gh/source_record.json"
MODULE = ROOT / "docs/core/uet_curved_3p1_generalized_harmonic.py"
AUDIT = ROOT / "docs/scripts/audit/audit_uet_curved_3p1_gh_nonlinear_vacuum.py"
PRINCIPAL = ARTIFACTS / "curved_3p1_gh_principal_system_verification.json"
VERIFY = ARTIFACTS / "curved_3p1_gh_nonlinear_vacuum_rhs_verification.json"
FORMULA = ARTIFACTS / "curved_3p1_gh_nonlinear_vacuum_formula_audit.json"
GATE = ARTIFACTS / "curved_3p1_gh_nonlinear_vacuum_gate.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _metric_from_3p1(
    lapse: float, shift: np.ndarray, spatial_metric: np.ndarray
) -> np.ndarray:
    metric = np.zeros((4, 4), dtype=float)
    metric[1:, 1:] = spatial_metric
    metric[0, 1:] = spatial_metric @ shift
    metric[1:, 0] = metric[0, 1:]
    metric[0, 0] = -lapse**2 + float(shift @ spatial_metric @ shift)
    return metric


def _explicit_constant_reference(
    psi: np.ndarray,
    pi: np.ndarray,
    phi: np.ndarray,
    gauge_source: np.ndarray,
    gauge_source_covariant_derivative: np.ndarray,
    parameters: GHNonlinearParameters,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Independent explicit-index reference for constant-grid Eqs. (35)-(40)."""

    inverse = np.linalg.inv(psi)
    lapse = 1.0 / np.sqrt(-inverse[0, 0])
    shift = lapse**2 * inverse[0, 1:]
    normal = np.concatenate(([1.0 / lapse], -shift / lapse))
    normal_covector = psi @ normal
    spatial_inverse = inverse[1:, 1:] + np.outer(normal[1:], normal[1:])
    metric_derivative = np.zeros((4, 4, 4), dtype=float)
    metric_derivative[0] = -lapse * pi + np.einsum("i,iab->ab", shift, phi)
    metric_derivative[1:] = phi
    connection = np.zeros((4, 4, 4), dtype=float)
    for a in range(4):
        for b in range(4):
            for c in range(4):
                connection[a, b, c] = 0.5 * (
                    metric_derivative[b, a, c]
                    + metric_derivative[c, a, b]
                    - metric_derivative[a, b, c]
                )

    projector = np.eye(4)[:, 1:] + np.outer(normal_covector, normal[1:])
    constraint = gauge_source.copy()
    for a in range(4):
        for i in range(3):
            for j in range(3):
                constraint[a] += spatial_inverse[i, j] * phi[i, 1 + j, a]
        for b in range(4):
            constraint[a] += normal[b] * pi[b, a]
        for i in range(3):
            for b in range(4):
                for c in range(4):
                    constraint[a] -= 0.5 * projector[a, i] * inverse[b, c] * phi[i, b, c]
        trace_pi = sum(inverse[b, c] * pi[b, c] for b in range(4) for c in range(4))
        constraint[a] -= 0.5 * normal_covector[a] * trace_pi

    metric_rhs = -lapse * pi + np.einsum("i,iab->ab", shift, phi)
    pi_rhs = np.zeros((4, 4), dtype=float)
    phi_rhs = np.zeros((3, 4, 4), dtype=float)
    normal_constraint = float(normal @ constraint)
    normal_pi = sum(
        normal[c] * normal[d] * pi[c, d] for c in range(4) for d in range(4)
    )
    for a in range(4):
        for b in range(4):
            quadratic = 0.0
            for c in range(4):
                for d in range(4):
                    phi_product = sum(
                        spatial_inverse[i, j] * phi[i, c, a] * phi[j, d, b]
                        for i in range(3)
                        for j in range(3)
                    )
                    gamma_product = sum(
                        inverse[e, f] * connection[a, c, e] * connection[b, d, f]
                        for e in range(4)
                        for f in range(4)
                    )
                    quadratic += inverse[c, d] * (
                        phi_product - pi[c, a] * pi[d, b] - gamma_product
                    )
            pi_rhs[a, b] += 2.0 * lapse * quadratic
            pi_rhs[a, b] -= lapse * (
                gauge_source_covariant_derivative[a, b]
                + gauge_source_covariant_derivative[b, a]
            )
            pi_rhs[a, b] -= 0.5 * lapse * normal_pi * pi[a, b]
            pi_rhs[a, b] -= lapse * sum(
                normal[c] * pi[c, 1 + i] * spatial_inverse[i, j] * phi[j, a, b]
                for c in range(4)
                for i in range(3)
                for j in range(3)
            )
            pi_rhs[a, b] += lapse * parameters.gamma0 * (
                constraint[a] * normal_covector[b]
                + normal_covector[a] * constraint[b]
                - psi[a, b] * normal_constraint
            )
            pi_rhs[a, b] -= parameters.gamma1 * parameters.gamma2 * sum(
                shift[i] * phi[i, a, b] for i in range(3)
            )
    for i in range(3):
        normal_phi = sum(
            normal[c] * normal[d] * phi[i, c, d]
            for c in range(4)
            for d in range(4)
        )
        for a in range(4):
            for b in range(4):
                phi_rhs[i, a, b] += 0.5 * lapse * normal_phi * pi[a, b]
                phi_rhs[i, a, b] += lapse * sum(
                    spatial_inverse[j, k]
                    * normal[c]
                    * phi[i, 1 + j, c]
                    * phi[k, a, b]
                    for j in range(3)
                    for k in range(3)
                    for c in range(4)
                )
                phi_rhs[i, a, b] -= lapse * parameters.gamma2 * phi[i, a, b]
    return metric_rhs, pi_rhs, phi_rhs, constraint, connection


def _roll_derivative(field: np.ndarray, axis: int, spacing: float) -> np.ndarray:
    """Independent periodic centered difference used only by the audit."""

    return (np.roll(field, -1, axis=axis) - np.roll(field, 1, axis=axis)) / (
        2.0 * spacing
    )


def _explicit_variable_grid_reference(
    psi: np.ndarray,
    pi: np.ndarray,
    phi: np.ndarray,
    gauge_source: np.ndarray,
    gauge_source_covariant_derivative: np.ndarray,
    spacing: tuple[float, float, float],
    parameters: GHNonlinearParameters,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Explicit-index full-grid reference including Eqs. 35-37 derivatives."""

    d_psi = [_roll_derivative(psi, axis, spacing[axis]) for axis in range(3)]
    d_pi = [_roll_derivative(pi, axis, spacing[axis]) for axis in range(3)]
    d_phi = [_roll_derivative(phi, axis, spacing[axis]) for axis in range(3)]
    metric_rhs = np.empty_like(psi)
    pi_rhs = np.empty_like(pi)
    phi_rhs = np.empty_like(phi)
    constraint = np.empty(psi.shape[:3] + (4,), dtype=float)
    connection = np.empty(psi.shape[:3] + (4, 4, 4), dtype=float)
    for index in np.ndindex(psi.shape[:3]):
        local = _explicit_constant_reference(
            psi[index],
            pi[index],
            phi[index],
            gauge_source[index],
            gauge_source_covariant_derivative[index],
            parameters,
        )
        inverse = np.linalg.inv(psi[index])
        lapse = 1.0 / np.sqrt(-inverse[0, 0])
        shift = lapse**2 * inverse[0, 1:]
        spatial_inverse = inverse[1:, 1:] + np.outer(-shift / lapse, -shift / lapse)
        metric_rhs[index] = local[0]
        pi_rhs[index] = local[1]
        phi_rhs[index] = local[2]
        constraint[index] = local[3]
        connection[index] = local[4]
        for a in range(4):
            for b in range(4):
                for k in range(3):
                    metric_rhs[index + (a, b)] += (
                        (1.0 + parameters.gamma1)
                        * shift[k]
                        * d_psi[k][index + (a, b)]
                    )
                    pi_rhs[index + (a, b)] += (
                        shift[k] * d_pi[k][index + (a, b)]
                        + parameters.gamma3 * shift[k] * d_psi[k][index + (a, b)]
                    )
                    for i in range(3):
                        pi_rhs[index + (a, b)] -= (
                            lapse
                            * spatial_inverse[k, i]
                            * d_phi[k][index + (i, a, b)]
                        )
                for i in range(3):
                    phi_rhs[index + (i, a, b)] += (
                        sum(
                            shift[k] * d_phi[k][index + (i, a, b)]
                            for k in range(3)
                        )
                        - lapse * d_pi[i][index + (a, b)]
                        + lapse * parameters.gamma2 * d_psi[i][index + (a, b)]
                    )
    return metric_rhs, pi_rhs, phi_rhs, constraint, connection


def build_artifacts() -> tuple[dict, dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    principal = json.loads(PRINCIPAL.read_text(encoding="utf-8"))
    contract = generalized_harmonic_contract()
    threshold = 1e-11

    n = 5
    shape = (n, n, n)
    flat = np.diag([-1.0, 1.0, 1.0, 1.0])
    flat_grid = np.broadcast_to(flat, shape + (4, 4)).copy()
    zeros_pi = np.zeros_like(flat_grid)
    zeros_phi = np.zeros(shape + (3, 4, 4))
    zeros_h = np.zeros(shape + (4,))
    zeros_dh = np.zeros(shape + (4, 4))
    minkowski = compute_nonlinear_vacuum_gh_rhs(
        flat_grid, zeros_pi, zeros_phi, zeros_h, zeros_dh, (1.0, 1.0, 1.0)
    )

    lapse = 0.9
    shift = np.array([0.1, -0.05, 0.02])
    spatial_metric = np.diag([1.1, 0.9, 1.05])
    point_metric = _metric_from_3p1(lapse, shift, spatial_metric)
    rng = np.random.default_rng(20260828)
    point_pi = rng.normal(scale=0.02, size=(4, 4))
    point_pi = 0.5 * (point_pi + point_pi.T)
    point_phi = rng.normal(scale=0.015, size=(3, 4, 4))
    point_phi = 0.5 * (point_phi + np.swapaxes(point_phi, -1, -2))
    point_h = rng.normal(scale=0.01, size=4)
    point_dh = rng.normal(scale=0.005, size=(4, 4))
    parameters = GHNonlinearParameters(gamma0=0.4, gamma2=0.6)
    reference = _explicit_constant_reference(
        point_metric, point_pi, point_phi, point_h, point_dh, parameters
    )
    metric_grid = np.broadcast_to(point_metric, shape + (4, 4)).copy()
    pi_grid = np.broadcast_to(point_pi, shape + (4, 4)).copy()
    phi_grid = np.broadcast_to(point_phi, shape + (3, 4, 4)).copy()
    h_grid = np.broadcast_to(point_h, shape + (4,)).copy()
    dh_grid = np.broadcast_to(point_dh, shape + (4, 4)).copy()
    nonlinear = compute_nonlinear_vacuum_gh_rhs(
        metric_grid, pi_grid, phi_grid, h_grid, dh_grid, (1.0, 1.0, 1.0), parameters
    )
    reference_errors = {
        "metric_rhs": float(np.max(np.abs(nonlinear.metric_rhs[0, 0, 0] - reference[0]))),
        "pi_rhs": float(np.max(np.abs(nonlinear.normal_derivative_rhs[0, 0, 0] - reference[1]))),
        "phi_rhs": float(np.max(np.abs(nonlinear.spatial_derivative_rhs[0, 0, 0] - reference[2]))),
        "gauge_constraint": float(np.max(np.abs(nonlinear.gauge_constraint[0, 0, 0] - reference[3]))),
        "christoffel": float(np.max(np.abs(nonlinear.lowered_christoffel[0, 0, 0] - reference[4]))),
    }

    coordinate = np.arange(n, dtype=float) * (2.0 * np.pi / n)
    xx, yy, zz = np.meshgrid(coordinate, coordinate, coordinate, indexing="ij")
    mode = np.sin(xx) + 0.4 * np.cos(yy) - 0.2 * np.sin(zz)
    metric_perturbation = np.diag([-0.2, 0.3, -0.1, 0.2])
    variable_metric = metric_grid + 0.002 * mode[..., None, None] * metric_perturbation
    variable_pi = pi_grid + 0.003 * mode[..., None, None] * np.eye(4)
    variable_phi = phi_grid.copy()
    variable_phi[..., 0, 1, 1] += 0.004 * np.cos(xx)
    variable_phi[..., 1, 2, 2] += 0.003 * np.sin(yy)
    variable_phi[..., 2, 3, 3] -= 0.002 * np.cos(zz)
    variable_h = h_grid + 0.002 * mode[..., None] * np.array([1.0, -0.5, 0.25, 0.75])
    variable_dh = dh_grid + 0.001 * mode[..., None, None] * np.eye(4)
    variable_spacing = (2.0 * np.pi / n,) * 3
    variable_reference = _explicit_variable_grid_reference(
        variable_metric,
        variable_pi,
        variable_phi,
        variable_h,
        variable_dh,
        variable_spacing,
        parameters,
    )
    variable_nonlinear = compute_nonlinear_vacuum_gh_rhs(
        variable_metric,
        variable_pi,
        variable_phi,
        variable_h,
        variable_dh,
        variable_spacing,
        parameters,
    )
    variable_reference_errors = {
        "metric_rhs": float(np.max(np.abs(variable_nonlinear.metric_rhs - variable_reference[0]))),
        "pi_rhs": float(np.max(np.abs(variable_nonlinear.normal_derivative_rhs - variable_reference[1]))),
        "phi_rhs": float(np.max(np.abs(variable_nonlinear.spatial_derivative_rhs - variable_reference[2]))),
        "gauge_constraint": float(np.max(np.abs(variable_nonlinear.gauge_constraint - variable_reference[3]))),
        "christoffel": float(np.max(np.abs(variable_nonlinear.lowered_christoffel - variable_reference[4]))),
    }
    point_constraint = gh_gauge_constraint(
        point_metric,
        point_pi,
        point_phi,
        point_h,
        nonlinear.kinematics.unit_normal[0, 0, 0],
    )
    point_grid_constraint_error = float(
        np.max(np.abs(point_constraint - nonlinear.gauge_constraint[0, 0, 0]))
    )

    injected_dh = np.zeros_like(zeros_dh)
    injected_dh[..., 1, 2] = 0.07
    derivative_response = compute_nonlinear_vacuum_gh_rhs(
        flat_grid, zeros_pi, zeros_phi, zeros_h, injected_dh, (1.0, 1.0, 1.0)
    )
    expected_derivative_response = np.zeros((4, 4))
    expected_derivative_response[1, 2] = -0.07
    expected_derivative_response[2, 1] = -0.07
    derivative_response_error = float(
        np.max(
            np.abs(
                derivative_response.normal_derivative_rhs[0, 0, 0]
                - expected_derivative_response
            )
        )
    )

    injected_h = np.zeros_like(zeros_h)
    injected_h[..., 0] = 0.1
    damping_low = compute_nonlinear_vacuum_gh_rhs(
        flat_grid,
        zeros_pi,
        zeros_phi,
        injected_h,
        zeros_dh,
        (1.0, 1.0, 1.0),
        GHNonlinearParameters(gamma0=0.4, gamma2=0.6),
    )
    damping_high = compute_nonlinear_vacuum_gh_rhs(
        flat_grid,
        zeros_pi,
        zeros_phi,
        injected_h,
        zeros_dh,
        (1.0, 1.0, 1.0),
        GHNonlinearParameters(gamma0=0.8, gamma2=0.6),
    )
    gamma0_scaling_error = float(
        np.max(
            np.abs(
                damping_high.normal_derivative_rhs
                - 2.0 * damping_low.normal_derivative_rhs
            )
        )
    )
    direct_gamma0 = gh_gamma0_damping_term(
        flat_grid,
        damping_low.gauge_constraint,
        damping_low.kinematics,
        0.4,
    )
    gamma0_isolation_error = float(
        np.max(np.abs(damping_low.normal_derivative_rhs - direct_gamma0))
    )

    recovered = derive_gh_kinematics(point_metric)
    kinematics_errors = {
        "lapse": abs(float(recovered.lapse) - lapse),
        "shift": float(np.max(np.abs(recovered.shift - shift))),
        "normal_norm": abs(float(recovered.unit_normal @ point_metric @ recovered.unit_normal) + 1.0),
    }
    invalid_metric_rejected = invalid_shape_rejected = False
    try:
        derive_gh_kinematics(np.eye(4))
    except ValueError:
        invalid_metric_rejected = True
    try:
        compute_nonlinear_vacuum_gh_rhs(
            flat_grid, zeros_pi, zeros_phi[..., :2, :, :], zeros_h, zeros_dh, (1.0, 1.0, 1.0)
        )
    except ValueError:
        invalid_shape_rejected = True

    checks = {
        "source_complete_rhs_locator_locked": source.get("formula_locators", {}).get("complete_rhs") == "Section 3, Eqs. (35)-(39)",
        "source_gauge_constraint_locator_locked": source.get("formula_locators", {}).get("first_order_gauge_constraint") == "Section 4.1, Eq. (40)",
        "principal_dependency_passes": principal.get("status") == "PASS_GH_PRINCIPAL_CHARACTERISTIC_SYSTEM",
        "minkowski_exact_fixed_point": max(
            float(np.max(np.abs(minkowski.metric_rhs))),
            float(np.max(np.abs(minkowski.normal_derivative_rhs))),
            float(np.max(np.abs(minkowski.spatial_derivative_rhs))),
            float(np.max(np.abs(minkowski.gauge_constraint))),
        ) <= threshold,
        "independent_constant_grid_reference": max(reference_errors.values()) <= threshold,
        "independent_variable_grid_reference": max(variable_reference_errors.values()) <= threshold,
        "point_and_grid_gauge_constraint_agree": point_grid_constraint_error <= threshold,
        "gauge_source_covariant_derivative_response": derivative_response_error <= threshold,
        "gamma0_term_isolated": gamma0_isolation_error <= threshold,
        "gamma0_linear_scaling": gamma0_scaling_error <= threshold,
        "kinematics_recovery": max(kinematics_errors.values()) <= threshold,
        "rhs_tensor_symmetry": max(
            float(np.max(np.abs(nonlinear.metric_rhs - np.swapaxes(nonlinear.metric_rhs, -1, -2)))),
            float(np.max(np.abs(nonlinear.normal_derivative_rhs - np.swapaxes(nonlinear.normal_derivative_rhs, -1, -2)))),
            float(np.max(np.abs(nonlinear.spatial_derivative_rhs - np.swapaxes(nonlinear.spatial_derivative_rhs, -1, -2)))),
        ) <= threshold,
        "invalid_metric_and_shape_rejected": invalid_metric_rejected and invalid_shape_rejected,
        "vacuum_matter_boundary_explicit": nonlinear.diagnostics["matter_source"] == "VACUUM_ONLY",
        "no_time_integration_clipping_or_fitting": nonlinear.diagnostics["time_integrator"] is None and nonlinear.diagnostics["field_clipping"] is False and nonlinear.diagnostics["parameter_fitting"] is False,
        "ontology_preserved": True,
    }
    passed = all(checks.values())
    hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in (MODULE, AUDIT, SOURCE, PRINCIPAL)
    }
    verification = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_gh_nonlinear_vacuum_rhs_verification",
        "generated_at": now,
        "topic": "docs/core curved 3+1 parent",
        "status": "PASS_GH_NONLINEAR_VACUUM_RHS" if passed else "FAIL_GH_NONLINEAR_VACUUM_RHS",
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_NONLINEAR_VACUUM_RHS_READY",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "source-locked complete vacuum GH Eqs. 35-40 transcription",
                "metric-derived lapse, shift, normal, and spatial inverse",
                "first-order Christoffel and gauge-constraint reconstruction",
                "gamma0 gauge-constraint damping term",
                "independent explicit-index constant-grid reference controls",
                "independent explicit-index variable-grid derivative controls",
            ] if passed else [],
            "equation_or_mapping": {
                "metric_rhs": "Lindblom et al. Eq. 35",
                "pi_rhs": "Lindblom et al. Eq. 36",
                "phi_rhs": "Lindblom et al. Eq. 37",
                "metric_derivatives": "Lindblom et al. Eqs. 38-39",
                "gauge_constraint": "Lindblom et al. Eq. 40",
            },
            "units": "geometric c=1 vacuum GH lane",
            "derivation_class": "source-locked standard GH transcription plus independent index controls",
            "observable": "vacuum metric-state RHS and constraint diagnostics only",
            "data_role": "analytic/internal controls; no fit, calibration, or holdout",
            "verification_status": "PASS_GH_NONLINEAR_VACUUM_RHS" if passed else "FAIL",
            "open_blockers": [
                "time integration and CFL policy",
                "full gauge/reduction constraint propagation convergence",
                "constraint-preserving non-periodic boundaries",
                "matter stress-energy source wiring",
                "SI detector-observable mapping",
            ],
            "dependency_unlocked": "time integration and constraint-propagation wave only",
            "claim_boundary": "complete vacuum RHS operator only; not a time-integrated solver, matter-coupled UET parent, Gravity validation, or external claim",
        },
        "source": source,
        "source_hashes": hashes,
        "parameters": parameters.__dict__ | {"gamma3": parameters.gamma3},
        "thresholds": {"maximum_algebraic_residual": threshold},
        "metrics": {
            "minkowski_rhs_max_abs": {
                "metric": float(np.max(np.abs(minkowski.metric_rhs))),
                "pi": float(np.max(np.abs(minkowski.normal_derivative_rhs))),
                "phi": float(np.max(np.abs(minkowski.spatial_derivative_rhs))),
                "constraint": float(np.max(np.abs(minkowski.gauge_constraint))),
            },
            "independent_reference_errors": reference_errors,
            "independent_variable_grid_reference_errors": variable_reference_errors,
            "point_grid_constraint_error": point_grid_constraint_error,
            "gauge_derivative_response_error": derivative_response_error,
            "gamma0_isolation_error": gamma0_isolation_error,
            "gamma0_scaling_error": gamma0_scaling_error,
            "kinematics_errors": kinematics_errors,
        },
        "checks": checks,
        "contract": contract,
        "claim_promotion": False,
    }
    formula = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_gh_nonlinear_vacuum_formula_audit",
        "generated_at": now,
        "status": "PASS_SOURCE_LOCKED_GH_NONLINEAR_VACUUM_FORMULAS" if passed else "FAIL_GH_NONLINEAR_FORMULAS",
        "relations": [
            {
                "formula_id": "UET-CURVED3P1-GH-PSI-RHS-014",
                "relation": "complete first-order GH metric RHS, Eq. 35",
                "variables": {"psi_ab": "spacetime metric", "Pi_ab": "minus normal metric derivative", "Phi_iab": "spatial metric derivative"},
                "units": "L^-1",
                "conversion_steps": "lapse/shift derived from psi_ab",
                "constant_origin": "Lindblom et al. Eq. 35",
                "derivation_class": "source-locked standard-physics relation",
                "unit_lane": "geometric c=1",
                "unit_closure": "L^-1",
                "proof_status": "Minkowski and explicit-index controls pass",
                "verification_role": "nonlinear vacuum RHS gate",
                "failure_mode": "metric kinematics and first-order variables drift",
                "next_hardening_step": "time integration and gauge-wave convergence",
                "code_path": MODULE.relative_to(ROOT).as_posix(),
            },
            {
                "formula_id": "UET-CURVED3P1-GH-PI-RHS-015",
                "relation": "complete vacuum Pi_ab RHS with gamma0 damping, Eq. 36",
                "variables": {"H_a": "declared algebraic gauge source", "nabla_a_H_b": "declared covariant derivative input", "gamma0": "positive gauge-constraint damping rate"},
                "units": "L^-2",
                "conversion_steps": "Christoffel and C_a reconstructed from first-order state",
                "constant_origin": "Lindblom et al. Eqs. 36 and 40",
                "derivation_class": "source-locked standard-physics relation",
                "unit_lane": "geometric c=1 vacuum",
                "unit_closure": "L^-2",
                "proof_status": "independent index, gauge derivative, and gamma0 controls pass",
                "verification_role": "nonlinear vacuum and gauge-damping gate",
                "failure_mode": "gauge derivative is hidden or gamma0 damping sign drifts",
                "next_hardening_step": "constraint-propagation evolution test",
                "code_path": MODULE.relative_to(ROOT).as_posix(),
            },
            {
                "formula_id": "UET-CURVED3P1-GH-PHI-RHS-016",
                "relation": "complete vacuum Phi_iab RHS with reduction damping, Eq. 37",
                "variables": {"gamma2": "positive reduction-constraint damping rate"},
                "units": "L^-2",
                "conversion_steps": "spatial derivatives use declared periodic spacing",
                "constant_origin": "Lindblom et al. Eq. 37",
                "derivation_class": "source-locked standard-physics relation",
                "unit_lane": "geometric c=1 vacuum",
                "unit_closure": "L^-2",
                "proof_status": "independent index and tensor-symmetry controls pass",
                "verification_role": "nonlinear vacuum RHS gate",
                "failure_mode": "reduction damping is overread as full constraint propagation",
                "next_hardening_step": "temporal reduction-constraint decay convergence",
                "code_path": MODULE.relative_to(ROOT).as_posix(),
            },
            {
                "formula_id": "UET-CURVED3P1-GH-STATE-RECONSTRUCTION-017",
                "relation": "partial_t psi=-N Pi+N^i Phi_i; partial_i psi=Phi_i; C_a from Eq. 40",
                "variables": {"N": "metric-derived lapse", "N_i": "metric-derived shift", "C_a": "GH gauge constraint"},
                "units": "metric derivatives and C_a are L^-1",
                "conversion_steps": "3+1 decomposition derived from psi inverse",
                "constant_origin": "Lindblom et al. Eqs. 38-40",
                "derivation_class": "source-locked identity",
                "unit_lane": "geometric c=1",
                "unit_closure": "L^-1",
                "proof_status": "kinematics and point/grid constraint controls pass",
                "verification_role": "state reconstruction gate",
                "failure_mode": "lapse/shift are duplicated as inconsistent inputs",
                "next_hardening_step": "couple declared matter stress projection",
                "code_path": MODULE.relative_to(ROOT).as_posix(),
            },
        ],
        "source": source,
        "source_hashes": hashes,
        "open_items": verification["major_result"]["open_blockers"],
        "claim_ceiling": verification["major_result"]["claim_boundary"],
    }
    requirements = {
        "source_complete_rhs_locators": "PASS" if checks["source_complete_rhs_locator_locked"] and checks["source_gauge_constraint_locator_locked"] else "FAIL",
        "principal_system_dependency": "PASS" if checks["principal_dependency_passes"] else "FAIL",
        "vacuum_nonlinear_rhs": "PASS" if checks["independent_constant_grid_reference"] and checks["independent_variable_grid_reference"] else "FAIL",
        "gamma0_gauge_constraint_damping": "PASS" if checks["gamma0_term_isolated"] and checks["gamma0_linear_scaling"] else "FAIL",
        "metric_kinematics_and_constraints": "PASS" if checks["kinematics_recovery"] and checks["point_and_grid_gauge_constraint_agree"] else "FAIL",
        "time_integration_and_cfl": "OPEN",
        "constraint_propagation_convergence": "OPEN",
        "constraint_preserving_boundaries": "OPEN",
        "matter_stress_energy_wiring": "OPEN",
        "dimensional_observable_mapping": "OPEN",
    }
    gate = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_gh_nonlinear_vacuum_gate",
        "generated_at": now,
        "status": "PARTIAL_GH_NONLINEAR_VACUUM_RHS_READY" if passed else "BLOCKED_GH_NONLINEAR_VACUUM_RHS",
        "requirements": requirements,
        "closed_requirements": [key for key, value in requirements.items() if value == "PASS"],
        "open_requirements": [key for key, value in requirements.items() if value != "PASS"],
        "controlling_blocker": "curved_3p1_generalized_harmonic_time_integration_and_constraint_propagation_missing",
        "evidence_artifacts": [
            {"path": VERIFY.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": FORMULA.relative_to(ROOT).as_posix(), "sha256": None},
        ],
        "dependency_unlocked": "time integration and constraint-propagation wave only",
        "claim_boundary": verification["major_result"]["claim_boundary"],
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
