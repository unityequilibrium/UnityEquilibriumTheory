"""Audit the first curved 3+1 ADM constraint-interface hardening wave."""

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

from docs.core.uet_curved_3p1_constraints import (
    ADMMatterProjection,
    adm_constraint_contract,
    evaluate_adm_constraints,
    flat_flrw_adm_control,
    minkowski_adm_control,
)


ARTIFACTS = ROOT / "docs/core/artifacts"
SOURCE = ROOT / "docs/data/external/gr_3p1/gourgoulhon_2007/source_record.json"
VERIFY = ARTIFACTS / "curved_3p1_adm_constraint_interface_audit.json"
FORMULA = ARTIFACTS / "curved_3p1_adm_constraint_formula_audit.json"
GATE = ARTIFACTS / "core_curved_3p1_parent_gate.json"
ADDENDUM = ARTIFACTS / "uet_equation_correspondence_registry_curved_3p1_addendum.json"
GEOMETRY_VERIFY = ARTIFACTS / "curved_3p1_geometry_operator_verification.json"
GEOMETRY_FORMULA = ARTIFACTS / "curved_3p1_geometry_operator_formula_audit.json"
EVOLUTION_VERIFY = ARTIFACTS / "curved_3p1_adm_evolution_operator_verification.json"
HYPERBOLICITY_NO_GO = ARTIFACTS / "curved_3p1_fixed_gauge_adm_hyperbolicity_no_go.json"
EVOLUTION_FORMULA = ARTIFACTS / "curved_3p1_adm_evolution_formula_audit.json"
FORMULATION_SELECTION = ARTIFACTS / "curved_3p1_formulation_selection_gate.json"
GH_VERIFY = ARTIFACTS / "curved_3p1_gh_principal_system_verification.json"
GH_FORMULA = ARTIFACTS / "curved_3p1_gh_principal_system_formula_audit.json"
GH_GATE = ARTIFACTS / "curved_3p1_gh_branch_gate.json"
GH_NONLINEAR_VERIFY = ARTIFACTS / "curved_3p1_gh_nonlinear_vacuum_rhs_verification.json"
GH_NONLINEAR_FORMULA = ARTIFACTS / "curved_3p1_gh_nonlinear_vacuum_formula_audit.json"
GH_NONLINEAR_GATE = ARTIFACTS / "curved_3p1_gh_nonlinear_vacuum_gate.json"
GH_TIME_VERIFY = ARTIFACTS / "curved_3p1_gh_time_evolution_verification.json"
GH_TIME_FORMULA = ARTIFACTS / "curved_3p1_gh_time_evolution_formula_audit.json"
GH_TIME_GATE = ARTIFACTS / "curved_3p1_gh_time_evolution_gate.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifacts() -> tuple[dict, dict, dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    geometry_verification = json.loads(GEOMETRY_VERIFY.read_text(encoding="utf-8"))
    geometry_formula = json.loads(GEOMETRY_FORMULA.read_text(encoding="utf-8"))
    evolution_verification = json.loads(EVOLUTION_VERIFY.read_text(encoding="utf-8"))
    hyperbolicity_no_go = json.loads(HYPERBOLICITY_NO_GO.read_text(encoding="utf-8"))
    evolution_formula = json.loads(EVOLUTION_FORMULA.read_text(encoding="utf-8"))
    formulation_selection = json.loads(FORMULATION_SELECTION.read_text(encoding="utf-8"))
    gh_verification = json.loads(GH_VERIFY.read_text(encoding="utf-8"))
    gh_formula = json.loads(GH_FORMULA.read_text(encoding="utf-8"))
    gh_gate = json.loads(GH_GATE.read_text(encoding="utf-8"))
    gh_nonlinear_verification = json.loads(
        GH_NONLINEAR_VERIFY.read_text(encoding="utf-8")
    )
    gh_nonlinear_formula = json.loads(
        GH_NONLINEAR_FORMULA.read_text(encoding="utf-8")
    )
    gh_nonlinear_gate = json.loads(GH_NONLINEAR_GATE.read_text(encoding="utf-8"))
    gh_time_verification = json.loads(GH_TIME_VERIFY.read_text(encoding="utf-8"))
    gh_time_formula = json.loads(GH_TIME_FORMULA.read_text(encoding="utf-8"))
    gh_time_gate = json.loads(GH_TIME_GATE.read_text(encoding="utf-8"))
    geometry_passed = (
        geometry_verification.get("status") == "PASS_CURVED_3P1_GEOMETRY_OPERATOR"
        and geometry_verification.get("major_result", {}).get("closure_level")
        == "CLOSED_FOR_LANE"
        and geometry_formula.get("status") == "PASS_NUMERICAL_GEOMETRY_FORMULAS"
        and all(geometry_verification.get("checks", {}).values())
    )
    evolution_passed = (
        evolution_verification.get("status") == "PASS_ADM_EVOLUTION_RHS_OPERATOR_ONLY"
        and evolution_verification.get("major_result", {}).get("closure_level")
        == "CLOSED_FOR_LANE"
        and hyperbolicity_no_go.get("status", "").startswith("CLOSED_AS_NO_GO")
        and evolution_formula.get("status")
        == "PASS_RHS_FORMULAS_WITH_HYPERBOLICITY_NO_GO"
        and formulation_selection.get("status")
        == "PASS_SELECT_GENERALIZED_HARMONIC_NEXT_BRANCH"
    )
    gh_principal_passed = (
        gh_verification.get("status") == "PASS_GH_PRINCIPAL_CHARACTERISTIC_SYSTEM"
        and gh_verification.get("major_result", {}).get("closure_level") == "CLOSED_FOR_LANE"
        and gh_formula.get("status") == "PASS_SOURCE_LOCKED_GH_PRINCIPAL_FORMULAS"
        and gh_gate.get("status") == "PARTIAL_GH_PRINCIPAL_SYSTEM_READY"
        and all(gh_verification.get("checks", {}).values())
    )
    gh_nonlinear_passed = (
        gh_nonlinear_verification.get("status")
        == "PASS_GH_NONLINEAR_VACUUM_RHS"
        and gh_nonlinear_verification.get("major_result", {}).get("closure_level")
        == "CLOSED_FOR_LANE"
        and gh_nonlinear_formula.get("status")
        == "PASS_SOURCE_LOCKED_GH_NONLINEAR_VACUUM_FORMULAS"
        and gh_nonlinear_gate.get("status")
        == "PARTIAL_GH_NONLINEAR_VACUUM_RHS_READY"
        and all(gh_nonlinear_verification.get("checks", {}).values())
    )
    gh_time_passed = (
        gh_time_verification.get("status")
        == "PASS_GH_PERIODIC_VACUUM_TIME_EVOLUTION"
        and gh_time_verification.get("major_result", {}).get("closure_level")
        == "CLOSED_FOR_LANE"
        and gh_time_formula.get("status")
        == "PASS_GH_TIME_EVOLUTION_NUMERICAL_CONTRACT"
        and gh_time_gate.get("status")
        == "PARTIAL_GH_PERIODIC_VACUUM_EVOLUTION_READY"
        and all(gh_time_verification.get("checks", {}).values())
    )
    threshold = 1e-12

    minkowski_geometry, minkowski_matter = minkowski_adm_control((2, 2, 2))
    minkowski = evaluate_adm_constraints(minkowski_geometry, minkowski_matter)

    flrw_geometry, flrw_matter = flat_flrw_adm_control(
        1.7, 0.12, shape=(2, 2, 2)
    )
    flrw = evaluate_adm_constraints(flrw_geometry, flrw_matter)
    violated = evaluate_adm_constraints(
        flrw_geometry,
        ADMMatterProjection(
            1.1 * np.asarray(flrw_matter.energy_density),
            flrw_matter.momentum_density,
        ),
    )

    invalid_metric_rejected = False
    try:
        bad_geometry, bad_matter = minkowski_adm_control()
        metric = np.asarray(bad_geometry.spatial_metric).copy()
        metric[0, 0] = -1.0
        evaluate_adm_constraints(
            type(bad_geometry)(
                bad_geometry.lapse,
                bad_geometry.shift,
                metric,
                bad_geometry.extrinsic_curvature,
                bad_geometry.spatial_ricci_scalar,
                bad_geometry.momentum_tensor_divergence,
            ),
            bad_matter,
        )
    except ValueError:
        invalid_metric_rejected = True

    contract = adm_constraint_contract()
    metrics = {
        "minkowski_max_abs_hamiltonian_residual": minkowski.max_abs_hamiltonian_residual,
        "minkowski_max_abs_momentum_residual": minkowski.max_abs_momentum_residual,
        "flat_flrw_max_abs_hamiltonian_residual": flrw.max_abs_hamiltonian_residual,
        "flat_flrw_max_abs_momentum_residual": flrw.max_abs_momentum_residual,
        "flat_flrw_trace_K": float(np.max(np.abs(flrw.trace_extrinsic_curvature))),
        "negative_control_max_abs_hamiltonian_residual": violated.max_abs_hamiltonian_residual,
    }
    checks = {
        "source_identity_locked": source.get("arxiv_id") == "gr-qc/0703035",
        "minkowski_hamiltonian_constraint": metrics["minkowski_max_abs_hamiltonian_residual"] <= threshold,
        "minkowski_momentum_constraint": metrics["minkowski_max_abs_momentum_residual"] <= threshold,
        "flat_flrw_hamiltonian_constraint": metrics["flat_flrw_max_abs_hamiltonian_residual"] <= threshold,
        "flat_flrw_momentum_constraint": metrics["flat_flrw_max_abs_momentum_residual"] <= threshold,
        "density_negative_control_detected": metrics["negative_control_max_abs_hamiltonian_residual"] > 1e-4,
        "invalid_spatial_metric_rejected": invalid_metric_rejected,
        "no_clipping_or_fitting": not minkowski.diagnostics["field_clipping"] and not minkowski.diagnostics["parameter_fitting"],
        "metric_is_not_phi": contract["ontology"]["spatial_metric"] == "standard 3-metric; not Phi",
        "generated_trace_excluded": contract["ontology"]["R_gen"] == "excluded derived history trace",
        "metric_evolution_not_claimed": "spatial-metric and extrinsic-curvature evolution" in contract["not_implemented"],
    }
    passed = all(checks.values())

    verification = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_adm_constraint_interface_audit",
        "generated_at": now,
        "topic": "docs/core curved 3+1 parent",
        "version": "adm-constraint-interface-v1",
        "benchmark_role": "internal analytic constraint gate",
        "method_label": "standard ADM constraints from declared geometric inputs",
        "status": "PASS_CURVED_3P1_ADM_CONSTRAINT_INTERFACE" if passed else "FAIL",
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_ADM_CONSTRAINT_INTERFACE_READY",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "standard ADM Hamiltonian residual from declared 3+1 inputs",
                "standard ADM momentum residual from declared covariant divergence",
                "Minkowski and flat-FLRW analytic controls",
                "invalid-metric and matter-density negative controls",
                "geometric-unit and ontology boundary",
            ] if passed else [],
            "equation_or_mapping": contract["equations"],
            "units": {
                "K_ij": "L^-1",
                "R3": "L^-2",
                "G_rho": "L^-2",
                "G_S_i": "L^-2",
                "constraint_residuals": "L^-2",
            },
            "derivation_class": "standard-physics ADM constraint transcription and internal algebraic verification",
            "observable": "Hamiltonian and momentum constraint residuals; no detector observable",
            "data_role": "analytic controls and metadata-only primary-source record",
            "verification_status": "PASS_CURVED_3P1_ADM_CONSTRAINT_INTERFACE" if passed else "FAIL",
            "open_blockers": contract["not_implemented"],
            "dependency_unlocked": "curved 3+1 differential-geometry and evolution wave only; Gravity remains blocked",
            "claim_boundary": contract["claim_boundary"],
        },
        "source": {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "sha256": _sha256(SOURCE),
            "identity": source,
        },
        "input_identity": {
            "module": "docs/core/uet_curved_3p1_constraints.py",
            "source_record": SOURCE.relative_to(ROOT).as_posix(),
            "analytic_controls": ["Minkowski vacuum", "spatially flat FLRW"],
            "negative_controls": ["10 percent FLRW density perturbation", "non-positive spatial metric"],
        },
        "config": {
            "signature": "(-,+,+,+)",
            "unit_lane": "geometric",
            "gravitational_constant": 1.0,
            "flrw_scale_factor": 1.7,
            "flrw_hubble_rate": 0.12,
            "control_shape": [2, 2, 2],
            "parameter_fitting": False,
        },
        "thresholds": {"analytic_constraint_max_abs": threshold, "negative_control_min_abs": 1e-4},
        "metrics": metrics,
        "checks": checks,
        "contract": contract,
        "notes": [
            "R3 and the covariant momentum-tensor divergence are declared inputs in v1.",
            "Constraint residuals are diagnostics and are not physical detector observables.",
            "No C-to-mass, Phi-to-metric, R_gen-to-state, fitting, clipping, or Gravity unlock is introduced.",
        ],
        "claim_promotion": False,
    }

    formula = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_adm_constraint_formula_audit",
        "generated_at": now,
        "status": "PASS_FORMULA_INTERFACE_ONLY" if passed else "FAIL",
        "relations": [
            {
                "formula_id": "UET-CURVED3P1-HAMILTONIAN-001",
                "relation": contract["equations"]["hamiltonian"],
                "variables": {
                    "R3": "spatial Ricci scalar",
                    "K": "trace gamma^ij K_ij",
                    "K_ij": "extrinsic curvature",
                    "rho": "Eulerian energy density",
                    "G": "declared positive gravitational constant",
                },
                "units": {"R3": "L^-2", "K": "L^-1", "G_rho": "L^-2"},
                "conversion_steps": "none in geometric lane; SI conversion remains open",
                "constant_origin": {"16*pi": "standard ADM convention", "G": "declared input"},
                "derivation_class": "imported standard ADM identity",
                "unit_lane": "geometric",
                "unit_closure": "L^-2 on every term",
                "proof_status": "Minkowski and flat-FLRW algebraic controls pass",
                "verification_role": "analytic gate and violation diagnostic",
                "failure_mode": "vacuum/FLRW control does not cancel or a density violation is missed",
                "next_hardening_step": "compute R3 from the grid metric and test spatial convergence",
                "code_path": "docs/core/uet_curved_3p1_constraints.py",
            },
            {
                "formula_id": "UET-CURVED3P1-MOMENTUM-002",
                "relation": contract["equations"]["momentum"],
                "variables": {
                    "D_j": "spatial covariant derivative",
                    "K^j_i": "mixed extrinsic curvature",
                    "K": "trace gamma^ij K_ij",
                    "S_i": "Eulerian covariant momentum density",
                    "G": "declared positive gravitational constant",
                },
                "units": {"D_K": "L^-2", "G_S_i": "L^-2"},
                "conversion_steps": "none in geometric lane; SI conversion remains open",
                "constant_origin": {"8*pi": "standard ADM convention", "G": "declared input"},
                "derivation_class": "imported standard ADM identity",
                "unit_lane": "geometric",
                "unit_closure": "L^-2 on every term",
                "proof_status": "declared-divergence interface and analytic controls pass",
                "verification_role": "analytic gate and momentum-source negative control",
                "failure_mode": "momentum source is ignored or covariant-divergence sign/index placement drifts",
                "next_hardening_step": "compute the covariant divergence from grid gamma_ij and K_ij",
                "code_path": "docs/core/uet_curved_3p1_constraints.py",
            },
        ],
        "source": verification["source"],
        "open_items": contract["not_implemented"],
        "claim_ceiling": "curved 3+1 ADM constraint interface; no dynamical solver",
    }

    parent_requirements = {
        "adm_constraint_interface": "PASS" if passed else "FAIL",
        "metric_to_ricci_operator": "PASS" if geometry_passed else "OPEN",
        "spatial_geometry_convergence": "PASS" if geometry_passed else "OPEN",
        "adm_metric_k_evolution_rhs_operator": "PASS" if evolution_passed else "OPEN",
        "fixed_gauge_adm_hyperbolicity": "CLOSED_AS_NO_GO" if evolution_passed else "OPEN",
        "formulation_selection": "PASS" if evolution_passed else "OPEN",
        "first_order_gh_principal_system": "PASS" if gh_principal_passed else "OPEN",
        "gh_characteristic_basis": "PASS" if gh_principal_passed else "OPEN",
        "gh_symmetric_hyperbolicity": "PASS" if gh_principal_passed else "OPEN",
        "gh_reduction_constraint_damping": "PASS" if gh_principal_passed else "OPEN",
        "lapse_shift_gauge": "PASS_GH_METRIC_DERIVED_PERIODIC_HARMONIC_GAUGE" if gh_time_passed else ("PARTIAL_GH_DECLARED_SOURCE_AND_METRIC_RECONSTRUCTION" if gh_nonlinear_passed else ("PARTIAL_GH_ALGEBRAIC_SOURCE_CONTRACT" if gh_principal_passed else "OPEN_GENERALIZED_HARMONIC")),
        "metric_and_extrinsic_curvature_evolution": "PASS_PERIODIC_GH_VACUUM_TIME_INTEGRATION" if gh_time_passed else ("PARTIAL_GH_NONLINEAR_VACUUM_RHS_OPERATOR_ONLY" if gh_nonlinear_passed else ("PARTIAL_GH_PRINCIPAL_RHS_ONLY" if gh_principal_passed else ("PARTIAL_RHS_OPERATOR_ONLY" if evolution_passed else "OPEN"))),
        "strong_hyperbolicity": "PASS" if gh_principal_passed else "OPEN_GENERALIZED_HARMONIC",
        "complete_nonlinear_gh_rhs": "PASS" if gh_nonlinear_passed else "OPEN",
        "gamma0_gauge_constraint_damping": "PASS" if gh_nonlinear_passed else "OPEN",
        "periodic_gh_time_integration": "PASS" if gh_time_passed else "OPEN",
        "characteristic_cfl_policy": "PASS" if gh_time_passed else "OPEN",
        "constraint_propagation": "PASS_PERIODIC_GAUGE_REDUCTION_CURL_CONVERGENCE" if gh_time_passed else ("PARTIAL_REDUCTION_AND_ALGEBRAIC_GAUGE_DAMPING_ONLY" if gh_nonlinear_passed else ("PARTIAL_REDUCTION_CONSTRAINT_DAMPING_ONLY" if gh_principal_passed else "OPEN")),
        "temporal_spatial_convergence": "PASS_RK4_TEMPORAL_AND_SECOND_ORDER_SPATIAL" if gh_time_passed else ("PARTIAL_SPATIAL_OPERATOR_CONVERGENCE_ONLY" if gh_principal_passed else "OPEN"),
        "constraint_preserving_boundaries": "OPEN",
        "topic13_stress_energy_projection": "OPEN",
        "dimensional_observable_mapping": "OPEN",
    }
    parent_status = (
        "PARTIAL_CURVED_3P1_GH_PERIODIC_VACUUM_EVOLUTION_READY"
        if passed
        and geometry_passed
        and evolution_passed
        and gh_principal_passed
        and gh_nonlinear_passed
        and gh_time_passed
        else (
            "PARTIAL_CURVED_3P1_GH_NONLINEAR_VACUUM_RHS_READY"
            if passed and geometry_passed and evolution_passed and gh_principal_passed and gh_nonlinear_passed
            else (
                "PARTIAL_CURVED_3P1_GH_PRINCIPAL_SYSTEM_READY"
                if passed and geometry_passed and evolution_passed and gh_principal_passed
                else (
                    "PARTIAL_CURVED_3P1_ADM_EVOLUTION_NOGO_READY"
                    if passed and geometry_passed and evolution_passed
                    else (
                        "PARTIAL_CURVED_3P1_PARENT_GEOMETRY_OPERATOR_READY"
                        if passed and geometry_passed
                        else (
                            "PARTIAL_CURVED_3P1_PARENT_CONSTRAINT_INTERFACE_READY"
                            if passed
                            else "BLOCKED"
                        )
                    )
                )
            )
        )
    )
    closed_components = []
    if passed:
        closed_components.append("ADM constraint evaluation interface")
    if geometry_passed:
        closed_components.extend(
            [
                "periodic-grid metric-to-Ricci operator",
                "periodic-grid covariant momentum-tensor divergence",
                "second-order spatial geometry convergence",
            ]
        )
    if evolution_passed:
        closed_components.extend(
            [
                "nonlinear periodic ADM metric/K right-hand-side operator",
                "second-order lapse-Hessian and shift-Lie convergence controls",
                "fixed-gauge ADM strong-hyperbolicity branch closed as no-go",
                "first-order generalized-harmonic next branch selected",
            ]
        )
    if gh_principal_passed:
        closed_components.extend(
            [
                "first-order GH principal equation and algebraic gauge-source contract",
                "complete GH characteristic basis with source-matched speeds",
                "positive GH symmetrizer and principal-system symmetric hyperbolicity",
                "reduction-constraint damping identity and spatial convergence",
            ]
        )
    if gh_nonlinear_passed:
        closed_components.extend(
            [
                "complete nonlinear vacuum GH Eqs. 35-40 right-hand-side operator",
                "metric-derived lapse, shift, normal, Christoffel, and gauge constraint",
                "gamma0 algebraic gauge-constraint damping term",
                "independent constant-grid and variable-grid explicit-index controls",
            ]
        )
    if gh_time_passed:
        closed_components.extend(
            [
                "classical RK4 integration of the nonlinear vacuum GH system",
                "fixed characteristic CFL policy on the periodic branch",
                "exact Minkowski and harmonic gauge-wave evolution controls",
                "second-order spatial and fourth-order temporal convergence",
                "periodic gauge, reduction, and curl constraint propagation",
                "gamma2 reduction-constraint damping over time",
            ]
        )
    gate = {
        "schema_version": "1.0",
        "artifact": "core_curved_3p1_parent_gate",
        "generated_at": now,
        "status": parent_status,
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_OBSERVABLE_PARENT_READY",
            "topic": "core",
            "closure_level": "PARTIAL",
            "what_is_closed": closed_components,
            "equation_or_mapping": contract["equations"],
            "units": "geometric constraint lane; SI observable mapping open",
            "derivation_class": "incremental curved 3+1 parent construction",
            "observable": "constraint residual diagnostics only",
            "data_role": "internal analytic controls",
            "verification_status": parent_status,
            "open_blockers": [key for key, value in parent_requirements.items() if value not in {"PASS", "CLOSED_AS_NO_GO"}],
            "dependency_unlocked": "constraint-preserving boundary and Topic 13 stress-energy wiring waves only; GR_CLASSICAL_COMPATIBILITY_LANE remains blocked",
            "claim_boundary": "partial parent construction; not CLOSED_FOR_CORE and not Gravity/GR compatibility",
        },
        "requirements": parent_requirements,
        "controlling_blocker": "curved_3p1_constraint_preserving_boundaries_and_topic13_stress_energy_wiring_missing",
        "evidence_artifacts": [
            {"path": VERIFY.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": FORMULA.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GEOMETRY_VERIFY.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GEOMETRY_FORMULA.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": EVOLUTION_VERIFY.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": HYPERBOLICITY_NO_GO.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": EVOLUTION_FORMULA.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": FORMULATION_SELECTION.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_VERIFY.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_FORMULA.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_GATE.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_NONLINEAR_VERIFY.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_NONLINEAR_FORMULA.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_NONLINEAR_GATE.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_TIME_VERIFY.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_TIME_FORMULA.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_TIME_GATE.relative_to(ROOT).as_posix(), "sha256": None},
        ],
        "claim_promotion": False,
    }

    addendum = {
        "schema_version": "1.0",
        "artifact": "uet_equation_correspondence_registry_curved_3p1_addendum",
        "generated_at": now,
        "extends": "docs/core/artifacts/uet_equation_correspondence_registry.json",
        "status": "CANDIDATE_ENTRY_PENDING_MERGE",
        "equation_entries": [
            {
                "equation_id": "uet.main_theory.curved_3p1.adm_constraints",
                "version": "adm-constraint-interface-v1",
                "classification": "standard_physics_constraint_interface",
                "relation_or_code_path": "docs/core/uet_curved_3p1_constraints.py",
                "variables": {
                    "gamma_ij": "positive-definite spatial metric",
                    "K_ij": "extrinsic curvature",
                    "rho": "Eulerian energy density",
                    "S_i": "Eulerian covariant momentum density",
                },
                "mathematical_role": "evaluate ADM Hamiltonian and momentum constraints",
                "standard_physics_counterpart": "ADM 3+1 initial-value constraints",
                "observable_mapping": {"status": "OPEN", "reason": "constraint residuals are diagnostics, not detector observables"},
                "unit_lane": "geometric",
                "parameter_dimensions": verification["major_result"]["units"],
                "source_or_origin": verification["source"],
                "assumptions": ["(-,+,+,+) signature", "positive lapse", "positive-definite spatial metric", "declared Ricci scalar and momentum divergence"],
                "symmetry_and_conservation": "symmetric gamma_ij and K_ij; ADM constraints evaluated but not propagated",
                "limiting_cases": ["Minkowski vacuum", "spatially flat FLRW Friedmann control"],
                "implementation_paths": ["docs/core/uet_curved_3p1_constraints.py"],
                "verifier_paths": ["docs/scripts/audit/audit_uet_curved_3p1_constraints.py", VERIFY.relative_to(ROOT).as_posix(), "docs/core/test/test_uet_curved_3p1_constraints.py"],
                "evidence_class": "INTERNAL_FORMAL_AND_ANALYTIC_CONTROL",
                "proof_status": "constraint algebra and analytic controls pass; differential geometry and evolution open",
                "downstream_dependencies": ["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"],
                "claim_boundary": contract["claim_boundary"],
                "failure_mode": "invalid metric, nonzero analytic residual, hidden geometry operator, or constraint violation not detected",
                "next_hardening_step": "implement metric-to-Ricci and covariant-divergence operators, then a gauge-declared evolution/constraint-propagation system",
            },
            {
                "equation_id": "uet.main_theory.curved_3p1.periodic_spatial_geometry",
                "version": "periodic-geometry-operator-v1",
                "classification": "numerical_implementation",
                "relation_or_code_path": "docs/core/uet_curved_3p1_geometry.py",
                "variables": {
                    "gamma_ij": "positive-definite spatial metric on a uniform periodic Cartesian chart",
                    "Gamma^k_ij": "Levi-Civita connection",
                    "R_ij": "spatial Ricci tensor",
                    "R3": "spatial Ricci scalar",
                    "K_ij": "extrinsic curvature",
                },
                "mathematical_role": "compute Ricci curvature and ADM momentum-tensor divergence from grid fields",
                "standard_physics_counterpart": "ADM spatial differential geometry",
                "observable_mapping": {"status": "OPEN", "reason": "curvature and constraint inputs are diagnostics; no detector map is declared"},
                "unit_lane": "geometric periodic Cartesian chart",
                "parameter_dimensions": geometry_verification["major_result"]["units"],
                "source_or_origin": geometry_verification["source"],
                "assumptions": ["uniform three-dimensional grid", "periodic boundaries", "positive-definite gamma_ij", "second-order centered derivatives"],
                "symmetry_and_conservation": "Levi-Civita metric compatibility and Ricci symmetry checked; evolution conservation/constraint propagation open",
                "limiting_cases": ["Cartesian flat metric", "conformally flat analytic Ricci control", "manufactured off-diagonal K divergence control"],
                "implementation_paths": ["docs/core/uet_curved_3p1_geometry.py"],
                "verifier_paths": ["docs/scripts/audit/audit_uet_curved_3p1_geometry.py", GEOMETRY_VERIFY.relative_to(ROOT).as_posix(), "docs/core/test/test_uet_curved_3p1_geometry.py"],
                "evidence_class": "INTERNAL_FORMAL_NUMERICAL_AND_CONVERGENCE_CONTROL",
                "proof_status": "standard identities implemented with verified second-order periodic-grid convergence; no continuum or evolution proof",
                "downstream_dependencies": ["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"],
                "claim_boundary": geometry_verification["major_result"]["claim_boundary"],
                "failure_mode": "connection/index/stencil error yields wrong Ricci or momentum-constraint input",
                "next_hardening_step": "implement a gauge-declared strongly-hyperbolic metric/K evolution branch and test constraint propagation",
            },
            {
                "equation_id": "uet.main_theory.curved_3p1.adm_evolution_rhs",
                "version": "adm-evolution-rhs-v1",
                "classification": "standard_physics_evolution_operator",
                "relation_or_code_path": "docs/core/uet_curved_3p1_adm_evolution.py",
                "variables": {"gamma_ij": "spatial metric; not Phi", "K_ij": "extrinsic curvature; not Pi", "alpha": "positive lapse", "beta_i": "shift", "rho_Sij": "Eulerian stress-energy projection; not universal C"},
                "mathematical_role": "evaluate nonlinear ADM metric and extrinsic-curvature right-hand sides",
                "standard_physics_counterpart": "ADM 3+1 evolution equations",
                "observable_mapping": {"status": "OPEN", "reason": "RHS fields are evolution diagnostics, not detector observables"},
                "unit_lane": "geometric periodic Cartesian chart",
                "parameter_dimensions": evolution_verification["major_result"]["units"],
                "source_or_origin": evolution_verification["sources"],
                "assumptions": ["(-,+,+,+) signature", "positive lapse", "periodic grid", "declared Eulerian stress projection"],
                "symmetry_and_conservation": "symmetric gamma_ij/K_ij; constraint propagation remains open",
                "limiting_cases": ["Minkowski vacuum", "spatially flat dust FLRW instantaneous control"],
                "implementation_paths": ["docs/core/uet_curved_3p1_adm_evolution.py"],
                "verifier_paths": ["docs/scripts/audit/audit_uet_curved_3p1_adm_evolution.py", EVOLUTION_VERIFY.relative_to(ROOT).as_posix(), "docs/core/test/test_uet_curved_3p1_adm_evolution.py"],
                "evidence_class": "INTERNAL_FORMAL_NUMERICAL_AND_CONVERGENCE_CONTROL",
                "proof_status": "RHS operator controls pass; well-posed time evolution remains open",
                "downstream_dependencies": ["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"],
                "claim_boundary": evolution_verification["major_result"]["claim_boundary"],
                "failure_mode": "RHS execution is mistaken for a strongly-hyperbolic time evolution",
                "next_hardening_step": "implement first-order generalized-harmonic evolution and constraint damping"
            },
            {
                "equation_id": "uet.main_theory.curved_3p1.fixed_gauge_adm_hyperbolicity_no_go",
                "version": "fixed-geodesic-adm-symbol-v1",
                "classification": "formulation_no_go",
                "relation_or_code_path": "docs/core/uet_curved_3p1_adm_evolution.py",
                "variables": {"P_n": "dimensionless principal symbol", "h_ij": "linear metric perturbation", "K_ij": "linear extrinsic-curvature perturbation"},
                "mathematical_role": "reject the fixed-geodesic ADM branch from the strong-hyperbolicity parent gate",
                "standard_physics_counterpart": "principal-symbol strong-hyperbolicity test",
                "observable_mapping": {"status": "NOT_APPLICABLE", "reason": "formulation diagnostic"},
                "unit_lane": "dimensionless principal-symbol lane",
                "parameter_dimensions": "dimensionless after |k| scaling",
                "source_or_origin": hyperbolicity_no_go["sources"],
                "assumptions": ["linearization about flat space", "fixed geodesic gauge", "preregistered propagation directions"],
                "symmetry_and_conservation": "not a conservation relation; tests completeness of characteristic fields",
                "limiting_cases": ["axis directions", "diagonal direction", "fixed oblique direction"],
                "implementation_paths": ["docs/core/uet_curved_3p1_adm_evolution.py"],
                "verifier_paths": ["docs/scripts/audit/audit_uet_curved_3p1_adm_evolution.py", HYPERBOLICITY_NO_GO.relative_to(ROOT).as_posix()],
                "evidence_class": "INTERNAL_FORMAL_PRINCIPAL_SYMBOL_NO_GO",
                "proof_status": "CLOSED_AS_NO_GO for the declared fixed-gauge branch",
                "downstream_dependencies": ["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"],
                "claim_boundary": hyperbolicity_no_go["major_result"]["claim_boundary"],
                "failure_mode": "branch-local no-go is overgeneralized to every ADM/BSSN/NOR gauge",
                "next_hardening_step": "verify first-order generalized-harmonic characteristic fields"
            },
            {
                "equation_id": "uet.main_theory.curved_3p1.generalized_harmonic_principal_system",
                "version": "gh-principal-system-v1",
                "classification": "standard_physics_hyperbolic_formulation",
                "relation_or_code_path": "docs/core/uet_curved_3p1_generalized_harmonic.py",
                "variables": {"psi_ab": "spacetime metric; not UET Phi", "Pi_ab": "minus normal metric derivative; not UET Pi", "Phi_iab": "spatial metric derivative", "H_a": "declared algebraic gauge source", "C_iab": "first-order reduction constraint"},
                "mathematical_role": "provide a complete symmetric-hyperbolic first-order principal system for the curved parent",
                "standard_physics_counterpart": "Lindblom et al. first-order generalized harmonic Einstein formulation",
                "observable_mapping": {"status": "OPEN", "reason": "characteristic and constraint fields are formulation diagnostics"},
                "unit_lane": "geometric c=1 local-orthonormal principal frame",
                "parameter_dimensions": gh_verification["major_result"]["units"],
                "source_or_origin": gh_verification["source"],
                "assumptions": ["gamma1=-1", "gamma3=gamma1*gamma2", "gamma0>0", "gamma2>0", "Lambda^2>gamma2^2", "algebraic H_a(x,psi)"],
                "symmetry_and_conservation": "positive analytic symmetrizer and complete characteristic basis pass; full Einstein/constraint propagation remains open",
                "limiting_cases": ["Minkowski harmonic gauge", "constant-coefficient local orthonormal frame", "zero shift", "sub/super-coordinate shift cases with normal-frame causal waves"],
                "implementation_paths": ["docs/core/uet_curved_3p1_generalized_harmonic.py"],
                "verifier_paths": ["docs/scripts/audit/audit_uet_curved_3p1_generalized_harmonic.py", GH_VERIFY.relative_to(ROOT).as_posix(), "docs/core/test/test_uet_curved_3p1_generalized_harmonic.py"],
                "evidence_class": "INTERNAL_FORMAL_ANALYTIC_AND_MANUFACTURED_CONVERGENCE_CONTROL",
                "proof_status": "principal/characteristic and reduction-damping lane passes; nonlinear vacuum RHS is tracked separately",
                "downstream_dependencies": ["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"],
                "claim_boundary": gh_verification["major_result"]["claim_boundary"],
                "failure_mode": "principal-system closure is overread as a complete numerical-relativity solver",
                "next_hardening_step": "integrate the separately verified nonlinear vacuum RHS, then add time evolution"
            },
            {
                "equation_id": "uet.main_theory.curved_3p1.generalized_harmonic_nonlinear_vacuum_rhs",
                "version": "gh-nonlinear-vacuum-rhs-v1",
                "classification": "standard_physics_vacuum_evolution_operator",
                "relation_or_code_path": "docs/core/uet_curved_3p1_generalized_harmonic.py",
                "formula_ids": [
                    "UET-CURVED3P1-GH-PSI-RHS-014",
                    "UET-CURVED3P1-GH-PI-RHS-015",
                    "UET-CURVED3P1-GH-PHI-RHS-016",
                    "UET-CURVED3P1-GH-STATE-RECONSTRUCTION-017"
                ],
                "variables": {
                    "psi_ab": "spacetime metric; not UET Phi",
                    "Pi_ab": "minus normal metric derivative; not UET Pi",
                    "Phi_iab": "spatial metric derivative",
                    "H_a": "declared gauge source",
                    "nabla_a_H_b": "declared covariant gauge-source derivative",
                    "C_a": "GH gauge constraint"
                },
                "mathematical_role": "evaluate complete nonlinear vacuum GH Eqs. 35-40 right-hand sides",
                "standard_physics_counterpart": "Lindblom et al. first-order generalized harmonic vacuum Einstein system",
                "observable_mapping": {
                    "status": "OPEN",
                    "reason": "metric-state RHS and constraints are formulation diagnostics, not detector observables"
                },
                "unit_lane": "geometric c=1 vacuum",
                "parameter_dimensions": gh_nonlinear_verification["major_result"]["units"],
                "source_or_origin": gh_nonlinear_verification["source"],
                "assumptions": [
                    "vacuum matter source",
                    "gamma1=-1",
                    "gamma0>0 and gamma2>0",
                    "uniform periodic Cartesian grid",
                    "declared H_a and nabla_a H_b"
                ],
                "symmetry_and_conservation": "symmetric metric derivative fields and algebraic gamma0 damping pass; propagated constraints remain open",
                "limiting_cases": [
                    "Minkowski harmonic gauge",
                    "constant nontrivial state",
                    "manufactured periodic variable state"
                ],
                "implementation_paths": ["docs/core/uet_curved_3p1_generalized_harmonic.py"],
                "verifier_paths": [
                    "docs/scripts/audit/audit_uet_curved_3p1_gh_nonlinear_vacuum.py",
                    GH_NONLINEAR_VERIFY.relative_to(ROOT).as_posix(),
                    "docs/core/test/test_uet_curved_3p1_gh_nonlinear_vacuum.py"
                ],
                "evidence_class": "INTERNAL_FORMAL_NUMERICAL_OPERATOR_CONTROL",
                "proof_status": "complete vacuum RHS transcription passes independent constant-grid and variable-grid controls; no time evolution",
                "downstream_dependencies": ["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"],
                "claim_boundary": gh_nonlinear_verification["major_result"]["claim_boundary"],
                "failure_mode": "operator-only closure is overread as time-evolved constraint propagation or a matter-coupled solver",
                "next_hardening_step": "add a fixed CFL time integrator and verify gauge/reduction constraint propagation"
            },
            {
                "equation_id": "uet.main_theory.curved_3p1.generalized_harmonic_periodic_vacuum_evolution",
                "version": "gh-periodic-vacuum-evolution-v1",
                "classification": "standard_physics_numerical_evolution_control",
                "relation_or_code_path": "docs/core/uet_curved_3p1_gh_evolution.py",
                "formula_ids": [
                    "UET-CURVED3P1-GH-RK4-018",
                    "UET-CURVED3P1-GH-CFL-019",
                    "UET-CURVED3P1-GH-GAUGE-WAVE-020"
                ],
                "variables": {
                    "psi_ab": "spacetime metric; not UET Phi",
                    "Pi_ab": "normal metric derivative; not UET Pi",
                    "Phi_iab": "spatial metric derivative",
                    "dt": "coordinate-time step",
                    "cfl": "fixed numerical Courant coefficient"
                },
                "mathematical_role": "advance the verified nonlinear vacuum GH system and monitor propagated constraints",
                "standard_physics_counterpart": "classical RK4 method-of-lines evolution of the first-order GH system",
                "observable_mapping": {"status": "OPEN", "reason": "gauge-wave error and constraint norms are numerical diagnostics"},
                "unit_lane": "geometric c=1 periodic coordinates",
                "parameter_dimensions": gh_time_verification["major_result"]["units"],
                "source_or_origin": gh_time_verification["source_hashes"],
                "assumptions": ["vacuum", "periodic grid", "prescribed time-independent H_a and nabla_a H_b", "fixed CFL coefficient", "no filtering or projection"],
                "symmetry_and_conservation": "metric symmetry and gauge/reduction/curl constraint convergence pass on the declared periodic controls",
                "limiting_cases": ["Minkowski fixed point", "exact harmonic gauge wave", "constant off-diagonal reduction violation"],
                "implementation_paths": ["docs/core/uet_curved_3p1_gh_evolution.py"],
                "verifier_paths": ["docs/scripts/audit/audit_uet_curved_3p1_gh_time_evolution.py", GH_TIME_VERIFY.relative_to(ROOT).as_posix(), "docs/core/test/test_uet_curved_3p1_gh_time_evolution.py"],
                "evidence_class": "INTERNAL_ANALYTIC_AND_NUMERICAL_CONVERGENCE_CONTROL",
                "proof_status": "periodic vacuum evolution and propagated-constraint controls pass; non-periodic boundaries and matter remain open",
                "downstream_dependencies": ["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"],
                "claim_boundary": gh_time_verification["major_result"]["claim_boundary"],
                "failure_mode": "periodic gauge-wave convergence is overread as a production numerical-relativity or matter-coupled solver",
                "next_hardening_step": "add constraint-preserving non-periodic boundaries and Topic 13 stress-energy wiring"
            }
        ],
    }
    return verification, formula, gate, addendum


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    verification, formula, gate, addendum = build_artifacts()
    VERIFY.write_text(json.dumps(verification, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    FORMULA.write_text(json.dumps(formula, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    gate["evidence_artifacts"][0]["sha256"] = _sha256(VERIFY)
    gate["evidence_artifacts"][1]["sha256"] = _sha256(FORMULA)
    gate["evidence_artifacts"][2]["sha256"] = _sha256(GEOMETRY_VERIFY)
    gate["evidence_artifacts"][3]["sha256"] = _sha256(GEOMETRY_FORMULA)
    gate["evidence_artifacts"][4]["sha256"] = _sha256(EVOLUTION_VERIFY)
    gate["evidence_artifacts"][5]["sha256"] = _sha256(HYPERBOLICITY_NO_GO)
    gate["evidence_artifacts"][6]["sha256"] = _sha256(EVOLUTION_FORMULA)
    gate["evidence_artifacts"][7]["sha256"] = _sha256(FORMULATION_SELECTION)
    gate["evidence_artifacts"][8]["sha256"] = _sha256(GH_VERIFY)
    gate["evidence_artifacts"][9]["sha256"] = _sha256(GH_FORMULA)
    gate["evidence_artifacts"][10]["sha256"] = _sha256(GH_GATE)
    gate["evidence_artifacts"][11]["sha256"] = _sha256(GH_NONLINEAR_VERIFY)
    gate["evidence_artifacts"][12]["sha256"] = _sha256(GH_NONLINEAR_FORMULA)
    gate["evidence_artifacts"][13]["sha256"] = _sha256(GH_NONLINEAR_GATE)
    gate["evidence_artifacts"][14]["sha256"] = _sha256(GH_TIME_VERIFY)
    gate["evidence_artifacts"][15]["sha256"] = _sha256(GH_TIME_FORMULA)
    gate["evidence_artifacts"][16]["sha256"] = _sha256(GH_TIME_GATE)
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    ADDENDUM.write_text(json.dumps(addendum, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": verification["status"], "parent_status": gate["status"], "controlling_blocker": gate["controlling_blocker"]}, indent=2))
    return 0 if verification["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
