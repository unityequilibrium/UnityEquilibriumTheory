"""Audit the ADM evolution RHS and fixed-gauge hyperbolicity no-go."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from math import log2, pi
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_curved_3p1_adm_evolution import (
    ADMStressProjection,
    adm_evolution_contract,
    compute_adm_evolution_rhs,
    fixed_gauge_adm_principal_symbol,
)


ARTIFACTS = ROOT / "docs/core/artifacts"
MODULE = ROOT / "docs/core/uet_curved_3p1_adm_evolution.py"
AUDIT_SCRIPT = Path(__file__).resolve()
GOURGOULHON = ROOT / "docs/data/external/gr_3p1/gourgoulhon_2007/source_record.json"
GUNDLACH = ROOT / "docs/data/external/gr_3p1/gundlach_martin_garcia_2006/source_record.json"
LINDBLOM = ROOT / "docs/data/external/gr_3p1/lindblom_et_al_2006_gh/source_record.json"
VERIFY = ARTIFACTS / "curved_3p1_adm_evolution_operator_verification.json"
NO_GO = ARTIFACTS / "curved_3p1_fixed_gauge_adm_hyperbolicity_no_go.json"
FORMULA = ARTIFACTS / "curved_3p1_adm_evolution_formula_audit.json"
SELECTION = ARTIFACTS / "curved_3p1_formulation_selection_gate.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _flat_metric(resolution: int, scale_factor: float = 1.0) -> np.ndarray:
    return np.broadcast_to(
        scale_factor**2 * np.eye(3),
        (resolution, resolution, resolution, 3, 3),
    ).copy()


def _zero_sources(resolution: int) -> tuple[np.ndarray, ADMStressProjection]:
    vector = np.zeros((resolution, resolution, resolution, 3))
    tensor = np.zeros((resolution, resolution, resolution, 3, 3))
    return vector, ADMStressProjection(0.0, vector, tensor)


def _l2(error: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(error))))


def _orders(errors: list[float]) -> list[float]:
    return [log2(errors[index] / errors[index + 1]) for index in range(len(errors) - 1)]


def build_artifacts() -> tuple[dict, dict, dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    sources = {
        "adm_equations": json.loads(GOURGOULHON.read_text(encoding="utf-8")),
        "hyperbolicity_boundary": json.loads(GUNDLACH.read_text(encoding="utf-8")),
        "next_generalized_harmonic_branch": json.loads(LINDBLOM.read_text(encoding="utf-8")),
    }
    contract = adm_evolution_contract()
    resolution = 6
    spacing = (1.0, 1.0, 1.0)
    flat = _flat_metric(resolution)
    zero_curvature = np.zeros_like(flat)
    zero_shift, vacuum = _zero_sources(resolution)

    minkowski = compute_adm_evolution_rhs(
        spatial_metric=flat,
        extrinsic_curvature=zero_curvature,
        lapse=1.0,
        shift=zero_shift,
        matter=vacuum,
        spacing=spacing,
    )

    scale_factor = 1.7
    hubble = 0.12
    flrw_metric = _flat_metric(resolution, scale_factor)
    flrw_curvature = -hubble * flrw_metric
    density = 3.0 * hubble**2 / (8.0 * pi)
    flrw = compute_adm_evolution_rhs(
        spatial_metric=flrw_metric,
        extrinsic_curvature=flrw_curvature,
        lapse=1.0,
        shift=zero_shift,
        matter=ADMStressProjection(density, zero_shift, np.zeros_like(flrw_metric)),
        spacing=spacing,
    )
    expected_metric_rhs = 2.0 * hubble * flrw_metric
    expected_curvature_rhs = -0.5 * hubble**2 * flrw_metric

    resolutions = [12, 24, 48]
    lapse_errors: list[float] = []
    shift_errors: list[float] = []
    gauge_amplitude = 0.05
    for grid_size in resolutions:
        length = 2.0 * pi
        step = length / grid_size
        x_grid = (np.arange(grid_size) * step)[:, None, None]
        metric = _flat_metric(grid_size)
        curvature = np.zeros_like(metric)
        shift, matter = _zero_sources(grid_size)

        lapse = np.broadcast_to(
            1.0 + gauge_amplitude * np.cos(x_grid),
            metric.shape[:3],
        )
        lapse_result = compute_adm_evolution_rhs(
            spatial_metric=metric,
            extrinsic_curvature=curvature,
            lapse=lapse,
            shift=shift,
            matter=matter,
            spacing=(step,) * 3,
        )
        expected_lapse_rhs = np.zeros_like(metric)
        expected_lapse_rhs[..., 0, 0] = gauge_amplitude * np.cos(x_grid)
        lapse_errors.append(
            _l2(lapse_result.extrinsic_curvature_rhs - expected_lapse_rhs)
        )

        shift[..., 0] = gauge_amplitude * np.sin(x_grid)
        shift_result = compute_adm_evolution_rhs(
            spatial_metric=metric,
            extrinsic_curvature=curvature,
            lapse=1.0,
            shift=shift,
            matter=matter,
            spacing=(step,) * 3,
        )
        expected_shift_rhs = np.zeros_like(metric)
        expected_shift_rhs[..., 0, 0] = 2.0 * gauge_amplitude * np.cos(x_grid)
        shift_errors.append(
            _l2(shift_result.spatial_metric_rhs - expected_shift_rhs)
        )

    lapse_orders = _orders(lapse_errors)
    shift_orders = _orders(shift_errors)
    directions = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 1.0, 1.0],
        [0.2, -0.3, 0.7],
    ]
    symbols = [fixed_gauge_adm_principal_symbol(direction) for direction in directions]
    symbol_records = [
        {
            "direction": result.direction.tolist(),
            "eigenvalues_real_sorted": sorted(
                float(value) for value in np.real_if_close(result.eigenvalues).real
            ),
            "maximum_eigenvalue_imaginary_part": float(
                np.max(np.abs(result.eigenvalues.imag))
            ),
            "characteristic_polynomial_residual": float(
                np.max(
                    np.abs(
                        (result.symbol @ result.symbol)
                        @ (
                            (result.symbol @ result.symbol)
                            - np.eye(result.symbol.shape[0])
                        )
                    )
                )
            ),
            "zero_algebraic_multiplicity": result.zero_algebraic_multiplicity,
            "zero_geometric_multiplicity": result.zero_geometric_multiplicity,
            "eigenvector_rank": result.eigenvector_rank,
            "complete_eigenbasis": result.complete_eigenbasis,
            "classification": result.classification,
        }
        for result in symbols
    ]

    invalid_lapse_rejected = False
    invalid_stress_rejected = False
    try:
        compute_adm_evolution_rhs(
            spatial_metric=flat,
            extrinsic_curvature=zero_curvature,
            lapse=0.0,
            shift=zero_shift,
            matter=vacuum,
            spacing=spacing,
        )
    except ValueError:
        invalid_lapse_rejected = True
    try:
        compute_adm_evolution_rhs(
            spatial_metric=flat,
            extrinsic_curvature=zero_curvature,
            lapse=1.0,
            shift=zero_shift,
            matter=ADMStressProjection(0.0, zero_shift, np.zeros(flat.shape[:3] + (3, 2))),
            spacing=spacing,
        )
    except ValueError:
        invalid_stress_rejected = True

    thresholds = {
        "analytic_rhs_max_abs": 1e-12,
        "minimum_gauge_spatial_order": 1.8,
        "maximum_characteristic_polynomial_residual": 1e-12,
        "expected_zero_algebraic_multiplicity": 6,
        "expected_zero_geometric_multiplicity": 3,
        "expected_eigenvector_rank": 9,
    }
    metrics = {
        "minkowski_metric_rhs_max_abs": float(np.max(np.abs(minkowski.spatial_metric_rhs))),
        "minkowski_curvature_rhs_max_abs": float(np.max(np.abs(minkowski.extrinsic_curvature_rhs))),
        "flrw_metric_rhs_max_abs_error": float(np.max(np.abs(flrw.spatial_metric_rhs - expected_metric_rhs))),
        "flrw_curvature_rhs_max_abs_error": float(np.max(np.abs(flrw.extrinsic_curvature_rhs - expected_curvature_rhs))),
        "lapse_hessian_l2_errors": lapse_errors,
        "lapse_hessian_observed_orders": lapse_orders,
        "shift_lie_l2_errors": shift_errors,
        "shift_lie_observed_orders": shift_orders,
        "principal_symbols": symbol_records,
    }
    checks = {
        "source_identities_locked": sources["adm_equations"].get("arxiv_id") == "gr-qc/0703035" and sources["hyperbolicity_boundary"].get("arxiv_id") == "gr-qc/0604035" and sources["next_generalized_harmonic_branch"].get("arxiv_id") == "gr-qc/0512093",
        "minkowski_fixed_point": max(metrics["minkowski_metric_rhs_max_abs"], metrics["minkowski_curvature_rhs_max_abs"]) <= thresholds["analytic_rhs_max_abs"],
        "dust_flrw_rhs": max(metrics["flrw_metric_rhs_max_abs_error"], metrics["flrw_curvature_rhs_max_abs_error"]) <= thresholds["analytic_rhs_max_abs"],
        "lapse_hessian_spatial_convergence": min(lapse_orders) >= thresholds["minimum_gauge_spatial_order"],
        "shift_lie_spatial_convergence": min(shift_orders) >= thresholds["minimum_gauge_spatial_order"],
        "fixed_gauge_characteristic_polynomial": all(record["characteristic_polynomial_residual"] <= thresholds["maximum_characteristic_polynomial_residual"] for record in symbol_records),
        "fixed_gauge_zero_jordan_defect": all(record["zero_algebraic_multiplicity"] == thresholds["expected_zero_algebraic_multiplicity"] and record["zero_geometric_multiplicity"] == thresholds["expected_zero_geometric_multiplicity"] and record["eigenvector_rank"] == thresholds["expected_eigenvector_rank"] and not record["complete_eigenbasis"] for record in symbol_records),
        "invalid_lapse_rejected": invalid_lapse_rejected,
        "invalid_stress_rejected": invalid_stress_rejected,
        "no_time_integration_clipping_or_fitting": minkowski.diagnostics["time_integrator"] == "NOT_IMPLEMENTED" and not minkowski.diagnostics["field_clipping"] and not minkowski.diagnostics["parameter_fitting"],
        "ontology_preserved": contract["ontology"]["gamma_ij"] == "standard spatial metric; not Phi" and contract["ontology"]["K_ij"] == "standard extrinsic curvature; not Pi" and contract["ontology"]["R_gen"] == "excluded derived history trace",
        "generalized_harmonic_not_claimed_implemented": contract["branch_decision"]["next_branch_status"] == "PREREGISTERED_NOT_IMPLEMENTED",
    }
    passed = all(checks.values())
    source_hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in (MODULE, AUDIT_SCRIPT, GOURGOULHON, GUNDLACH, LINDBLOM)
    }

    verification = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_adm_evolution_operator_verification",
        "generated_at": now,
        "topic": "docs/core curved 3+1 parent",
        "version": "adm-evolution-rhs-v1",
        "benchmark_role": "internal analytic operator and gauge-derivative gate",
        "method_label": "nonlinear periodic ADM RHS with declared lapse and shift",
        "status": "PASS_ADM_EVOLUTION_RHS_OPERATOR_ONLY" if passed else "FAIL",
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_ADM_EVOLUTION_RHS_READY",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "nonlinear periodic ADM metric right-hand side",
                "nonlinear periodic ADM extrinsic-curvature right-hand side",
                "declared lapse-Hessian and shift-Lie derivative terms",
                "Minkowski and dust-FLRW analytic controls",
                "second-order lapse/shift derivative convergence controls",
            ] if passed else [],
            "equation_or_mapping": contract["relations"],
            "units": {"gamma_ij": "dimensionless chart component", "K_ij": "L^-1", "R_ij": "L^-2", "rho_and_S_ij_with_G": "L^-2", "d_t_gamma_ij": "L^-1", "d_t_K_ij": "L^-2"},
            "derivation_class": "standard ADM evolution transcription plus second-order numerical derivatives",
            "observable": "metric/K right-hand-side diagnostics; no detector observable",
            "data_role": "analytic controls only; no fit, calibration, or holdout",
            "verification_status": "PASS_ADM_EVOLUTION_RHS_OPERATOR_ONLY" if passed else "FAIL",
            "open_blockers": contract["not_implemented"],
            "dependency_unlocked": "formulation-selection and generalized-harmonic implementation wave only",
            "claim_boundary": contract["claim_boundary"],
        },
        "sources": sources,
        "source_hashes": source_hashes,
        "input_identity": {"module": MODULE.relative_to(ROOT).as_posix(), "analytic_controls": ["Minkowski vacuum", "spatially-flat dust FLRW", "sinusoidal lapse Hessian", "sinusoidal shift Lie derivative"], "negative_controls": ["non-positive lapse", "invalid stress shape"]},
        "config": {"signature": "(-,+,+,+)", "extrinsic_curvature_convention": "K_ij=-(1/2)L_n gamma_ij", "boundary_condition": "periodic_all_axes", "resolutions": resolutions, "gauge_amplitude": gauge_amplitude, "time_integrator": None, "parameter_fitting": False, "field_clipping": False},
        "thresholds": thresholds,
        "metrics": metrics,
        "checks": checks,
        "contract": contract,
        "notes": ["RHS verification is not a well-posed time-evolution proof.", "FLRW is an instantaneous equation control with externally declared dust stress, not a cosmology validation.", "The fixed-gauge ADM hyperbolicity failure is preserved and selects a separate generalized-harmonic branch."],
        "claim_promotion": False,
    }

    no_go = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_fixed_gauge_adm_hyperbolicity_no_go",
        "generated_at": now,
        "topic": "docs/core curved 3+1 parent",
        "version": "fixed-geodesic-adm-symbol-v1",
        "status": "CLOSED_AS_NO_GO_FIXED_GAUGE_ADM_NOT_STRONGLY_HYPERBOLIC" if passed else "UNRESOLVED",
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_FIXED_GAUGE_ADM_HYPERBOLICITY_NO_GO",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": ["fixed-geodesic-gauge linearized ADM principal symbol is defective in every preregistered direction", "zero-speed algebraic multiplicity 6 exceeds geometric multiplicity 3", "this branch cannot satisfy the parent strong-hyperbolicity gate"] if passed else [],
            "equation_or_mapping": "P(n) on (i|k| h_ij, K_ij) has speeds {-1 x3, 0 x6, +1 x3} and zero eigenspace dimension 3",
            "units": "dimensionless principal symbol after division by |k|",
            "derivation_class": "linearized pseudo-differential principal-symbol analysis",
            "observable": "formulation diagnostic only",
            "data_role": "analytic matrix controls; no empirical data",
            "verification_status": "CLOSED_AS_NO_GO" if passed else "UNRESOLVED",
            "open_blockers": ["generalized-harmonic nonlinear implementation", "generalized-harmonic characteristic fields", "constraint damping and propagation", "time integration and convergence"],
            "dependency_unlocked": "FIRST_ORDER_GENERALIZED_HARMONIC branch implementation",
            "claim_boundary": "no-go for the declared fixed-geodesic ADM principal symbol only; not every gauge-modified ADM/BSSN/NOR formulation",
        },
        "sources": {"hyperbolicity_boundary": sources["hyperbolicity_boundary"], "next_branch": sources["next_generalized_harmonic_branch"]},
        "source_hashes": source_hashes,
        "principal_symbol_records": symbol_records,
        "acceptance": {"required_defect": "zero algebraic multiplicity > zero geometric multiplicity", "all_preregistered_directions_agree": all(record["classification"] == "DEFECTIVE_ZERO_SPEED_JORDAN_BLOCK" for record in symbol_records)},
        "claim_promotion": False,
    }

    formula = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_adm_evolution_formula_audit",
        "generated_at": now,
        "topic": "docs/core curved 3+1 parent",
        "version": "adm-evolution-rhs-v1",
        "benchmark_role": "formula/unit/formulation audit",
        "method_label": verification["method_label"],
        "status": "PASS_RHS_FORMULAS_WITH_HYPERBOLICITY_NO_GO" if passed else "FAIL",
        "relations": [
            {"formula_id": "UET-CURVED3P1-ADM-GAMMA-EVOL-006", "relation": contract["relations"]["metric_evolution"], "variables": {"gamma_ij": "spatial metric", "alpha": "positive lapse", "beta^i": "shift", "K_ij": "extrinsic curvature"}, "units": {"d_t_gamma_ij": "L^-1", "K_ij": "L^-1", "d_i_beta^j": "L^-1"}, "conversion_steps": "none in geometric chart lane", "constant_origin": "standard ADM identity", "derivation_class": "imported standard ADM relation", "unit_lane": "geometric", "unit_closure": "L^-1", "proof_status": "Minkowski/FLRW and shift-Lie controls pass", "verification_role": "RHS operator gate", "failure_mode": "sign/gauge drift changes slice evolution", "next_hardening_step": "replace rejected fixed-gauge ADM parent with a strongly-hyperbolic formulation", "code_path": MODULE.relative_to(ROOT).as_posix()},
            {"formula_id": "UET-CURVED3P1-ADM-K-EVOL-007", "relation": contract["relations"]["curvature_evolution"], "variables": {"K_ij": "extrinsic curvature", "R_ij": "spatial Ricci tensor", "rho": "Eulerian energy density", "S_ij": "Eulerian spatial stress", "Lambda": "cosmological constant"}, "units": {"d_t_K_ij": "L^-2", "R_ij": "L^-2", "K_squared": "L^-2", "G_rho": "L^-2", "Lambda": "L^-2"}, "conversion_steps": "none in geometric chart lane", "constant_origin": {"8*pi": "standard ADM convention", "G": "declared positive input"}, "derivation_class": "imported standard ADM relation", "unit_lane": "geometric", "unit_closure": "L^-2", "proof_status": "Minkowski/FLRW and lapse-Hessian controls pass", "verification_role": "RHS operator gate", "failure_mode": "Ricci, stress, Hessian, or sign error violates analytic controls", "next_hardening_step": "implement generalized-harmonic metric evolution and constraint damping", "code_path": MODULE.relative_to(ROOT).as_posix()},
            {"formula_id": "UET-CURVED3P1-ADM-PRINCIPAL-NOGO-008", "relation": "P(n) on (i|k|h_ij,K_ij): zero algebraic multiplicity 6, geometric multiplicity 3", "variables": {"n_i": "unit spatial covector", "h_ij": "linear metric perturbation", "K_ij": "linear extrinsic curvature", "P(n)": "dimensionless principal symbol"}, "units": "dimensionless after |k| scaling", "conversion_steps": "pseudo-differential reduction q_ij=i|k|h_ij", "constant_origin": "linearized fixed-gauge ADM principal part", "derivation_class": "derived relation", "unit_lane": "dimensionless principal-symbol lane", "unit_closure": "dimensionless", "proof_status": "CLOSED_AS_NO_GO for declared branch", "verification_role": "strong-hyperbolicity rejection gate", "failure_mode": "an incomplete eigenbasis is mistaken for a well-posed evolution system", "next_hardening_step": "implement and independently verify first-order generalized harmonic characteristic fields", "code_path": MODULE.relative_to(ROOT).as_posix()},
        ],
        "sources": sources,
        "source_hashes": source_hashes,
        "thresholds": thresholds,
        "metrics": metrics,
        "open_items": contract["not_implemented"],
        "claim_ceiling": contract["claim_boundary"],
    }

    selection = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_formulation_selection_gate",
        "generated_at": now,
        "status": "PASS_SELECT_GENERALIZED_HARMONIC_NEXT_BRANCH" if passed else "BLOCKED",
        "evaluated_branch": "fixed_geodesic_gauge_adm",
        "evaluated_branch_result": "REJECTED_STRONG_HYPERBOLICITY",
        "selected_next_branch": "first_order_generalized_harmonic",
        "selected_next_branch_status": "PREREGISTERED_NOT_IMPLEMENTED",
        "selection_basis": ["fixed-gauge ADM principal symbol is defective", "generalized harmonic has a source-backed symmetric-hyperbolic target formulation", "constraint damping and characteristic boundary structure are explicit next acceptance requirements"],
        "required_next_artifacts": ["generalized_harmonic_equation_and_gauge_contract", "generalized_harmonic_principal_symbol_verification", "generalized_harmonic_constraint_damping_verification", "temporal_spatial_convergence_artifact", "constraint_propagation_artifact"],
        "forbidden_shortcuts": ["calling ADM RHS execution strong hyperbolicity", "adding numerical dissipation to hide a Jordan defect", "using clipping or fitted damping", "promoting periodic controls to black-hole or external GR validation"],
        "evidence": [VERIFY.relative_to(ROOT).as_posix(), NO_GO.relative_to(ROOT).as_posix(), FORMULA.relative_to(ROOT).as_posix()],
        "claim_promotion": False,
    }
    return verification, no_go, formula, selection


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    payloads = build_artifacts()
    for path, payload in zip((VERIFY, NO_GO, FORMULA, SELECTION), payloads):
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    verification, no_go, _, selection = payloads
    print(json.dumps({"rhs_status": verification["status"], "no_go_status": no_go["status"], "selection_status": selection["status"], "claim_promotion": False}, indent=2))
    return 0 if verification["status"].startswith("PASS") and no_go["status"].startswith("CLOSED_AS_NO_GO") else 1


if __name__ == "__main__":
    raise SystemExit(main())
