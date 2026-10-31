"""Audit the first curved 3+1 ADM constraint-interface hardening wave."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_local_module(module_name: str, path: Path):
    """Load a leaf module without triggering the dependency-heavy core package init."""

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_constraint_module = _load_local_module(
    "_uet_curved_3p1_constraints_audit",
    ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_constraints.py",
)
_core_paths_module = _load_local_module(
    "_uet_core_paths_audit", ROOT / "docs/core/core_paths.py"
)
ADMMatterProjection = _constraint_module.ADMMatterProjection
adm_constraint_contract = _constraint_module.adm_constraint_contract
evaluate_adm_constraints = _constraint_module.evaluate_adm_constraints
flat_flrw_adm_control = _constraint_module.flat_flrw_adm_control
minkowski_adm_control = _constraint_module.minkowski_adm_control
canonical_artifact_path = _core_paths_module.canonical_artifact_path


ARTIFACTS = ROOT / "docs/core/07_artifacts"
SOURCE = ROOT / "docs/data/external/gr_3p1/gourgoulhon_2007/source_record.json"
VERIFY = canonical_artifact_path("curved_3p1_adm_constraint_interface_audit.json", "verification")
FORMULA = canonical_artifact_path("curved_3p1_adm_constraint_formula_audit.json", "correspondence")
GATE = canonical_artifact_path("core_curved_3p1_parent_gate.json", "gates")
ADDENDUM = canonical_artifact_path("uet_equation_correspondence_registry_curved_3p1_addendum.json", "correspondence")
GEOMETRY_VERIFY = canonical_artifact_path("curved_3p1_geometry_operator_verification.json", "verification")
GEOMETRY_FORMULA = canonical_artifact_path("curved_3p1_geometry_operator_formula_audit.json", "correspondence")
EVOLUTION_VERIFY = canonical_artifact_path("curved_3p1_adm_evolution_operator_verification.json", "verification")
HYPERBOLICITY_NO_GO = canonical_artifact_path("curved_3p1_fixed_gauge_adm_hyperbolicity_no_go.json")
EVOLUTION_FORMULA = canonical_artifact_path("curved_3p1_adm_evolution_formula_audit.json", "correspondence")
FORMULATION_SELECTION = canonical_artifact_path("curved_3p1_formulation_selection_gate.json", "gates")
GH_VERIFY = canonical_artifact_path("curved_3p1_gh_principal_system_verification.json", "verification")
GH_FORMULA = canonical_artifact_path("curved_3p1_gh_principal_system_formula_audit.json", "correspondence")
GH_GATE = canonical_artifact_path("curved_3p1_gh_branch_gate.json", "gates")
GH_NONLINEAR_VERIFY = canonical_artifact_path("curved_3p1_gh_nonlinear_vacuum_rhs_verification.json", "verification")
GH_NONLINEAR_FORMULA = canonical_artifact_path("curved_3p1_gh_nonlinear_vacuum_formula_audit.json", "correspondence")
GH_NONLINEAR_GATE = canonical_artifact_path("curved_3p1_gh_nonlinear_vacuum_gate.json", "gates")
GH_TIME_VERIFY = canonical_artifact_path("curved_3p1_gh_time_evolution_verification.json", "verification")
GH_TIME_FORMULA = canonical_artifact_path("curved_3p1_gh_time_evolution_formula_audit.json", "correspondence")
GH_TIME_GATE = canonical_artifact_path("curved_3p1_gh_time_evolution_gate.json", "gates")
MATTER_VERIFY = canonical_artifact_path("curved_3p1_topic13_matter_wiring_verification.json", "verification")
MATTER_FORMULA = canonical_artifact_path("curved_3p1_topic13_matter_wiring_formula_audit.json", "correspondence")
MATTER_GATE = canonical_artifact_path("curved_3p1_topic13_matter_wiring_gate.json", "gates")
GH_LINEAR_BOUNDARY_AUDIT = canonical_artifact_path(
    "curved_3p1_gh_linear_boundary_residual_audit.json", "verification"
)
GH_GW_DETECTOR_RESPONSE_AUDIT = canonical_artifact_path(
    "curved_3p1_gh_gw_detector_response_audit.json", "verification"
)
GH_GAUGE_WAVE_TT_NULL_AUDIT = canonical_artifact_path(
    "curved_3p1_gh_gauge_wave_tt_null_audit.json", "verification"
)
GH_TT_SBP_SAT_BOUNDARY_AUDIT = canonical_artifact_path(
    "curved_3p1_gh_tt_sbp_sat_boundary_pilot.json", "verification"
)
GH_FULL_U1_CPBC_SLAB_AUDIT = canonical_artifact_path(
    "curved_3p1_gh_full_u1_cpbc_slab_pilot.json", "verification"
)
GH_REDUCED_WAVE_COMPARATOR_AUDIT = canonical_artifact_path(
    "curved_3p1_gh_reduced_wave_boundary_comparator.json", "verification"
)
GH_REDUCED_WAVE_SBP_SAT_COMPARATOR_AUDIT = canonical_artifact_path(
    "curved_3p1_gh_reduced_wave_sbp_sat_comparator.json", "verification"
)


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
    matter_verification = json.loads(MATTER_VERIFY.read_text(encoding="utf-8"))
    matter_formula = json.loads(MATTER_FORMULA.read_text(encoding="utf-8"))
    matter_gate = json.loads(MATTER_GATE.read_text(encoding="utf-8"))
    gh_linear_boundary_audit = json.loads(
        GH_LINEAR_BOUNDARY_AUDIT.read_text(encoding="utf-8")
    )
    gh_gw_detector_response_audit = json.loads(
        GH_GW_DETECTOR_RESPONSE_AUDIT.read_text(encoding="utf-8")
    )
    gh_gauge_wave_tt_null_audit = json.loads(
        GH_GAUGE_WAVE_TT_NULL_AUDIT.read_text(encoding="utf-8")
    )
    gh_tt_sbp_sat_boundary_audit = json.loads(
        GH_TT_SBP_SAT_BOUNDARY_AUDIT.read_text(encoding="utf-8")
    )
    gh_full_u1_cpbc_slab_audit = json.loads(
        GH_FULL_U1_CPBC_SLAB_AUDIT.read_text(encoding="utf-8")
    )
    gh_reduced_wave_comparator_audit = json.loads(
        GH_REDUCED_WAVE_COMPARATOR_AUDIT.read_text(encoding="utf-8")
    )
    gh_reduced_wave_sbp_sat_comparator_audit = json.loads(
        GH_REDUCED_WAVE_SBP_SAT_COMPARATOR_AUDIT.read_text(encoding="utf-8")
    )
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
    matter_passed = (
        matter_verification.get("status")
        == "PASS_CURVED_3P1_TOPIC13_PRESCRIBED_MATTER_WIRING"
        and matter_verification.get("major_result", {}).get("closure_level")
        == "CLOSED_FOR_LANE"
        and matter_formula.get("status")
        == "PASS_SOURCE_LOCKED_TOPIC13_MATTER_FORMULAS"
        and matter_gate.get("status")
        == "PARTIAL_CURVED_3P1_PRESCRIBED_MATTER_SOURCE_READY"
        and all(matter_verification.get("checks", {}).values())
    )
    gh_linear_boundary_passed = (
        gh_linear_boundary_audit.get("status")
        == "PASS_GH_LINEAR_BOUNDARY_RESIDUAL_OPERATOR_AUDIT"
        and gh_linear_boundary_audit.get("major_result", {}).get("closure_level")
        == "CLOSED_FOR_LANE"
        and all(gh_linear_boundary_audit.get("checks", {}).values())
        and gh_linear_boundary_audit.get("scope", {}).get(
            "boundary_operator_applied_to_evolution"
        )
        is False
    )
    gw_response_hashes = gh_gw_detector_response_audit.get("source_hashes", {})
    gw_response_hashes_valid = bool(gw_response_hashes) and all(
        (ROOT / source_path).is_file()
        and _sha256(ROOT / source_path) == source_hash
        for source_path, source_hash in gw_response_hashes.items()
    )
    gh_gw_detector_response_passed = (
        gh_gw_detector_response_audit.get("status")
        == "PASS_GH_LINEAR_GW_INTERFEROMETER_RESPONSE"
        and gh_gw_detector_response_audit.get("major_result", {}).get(
            "major_result_id"
        )
        == "CORE_CURVED_3P1_GW_DETECTOR_RESPONSE_LANE"
        and gh_gw_detector_response_audit.get("major_result", {}).get(
            "closure_level"
        )
        == "CLOSED_FOR_LANE"
        and all(gh_gw_detector_response_audit.get("checks", {}).values())
        and gh_gw_detector_response_audit.get("claim_promotion") is False
        and gh_gw_detector_response_audit.get("input_identity", {}).get(
            "detector_data_consumed"
        )
        is False
        and gh_gw_detector_response_audit.get("input_identity", {}).get(
            "holdout_consumed"
        )
        is False
        and gh_gw_detector_response_audit.get("input_identity", {}).get(
            "data_rows_consumed"
        )
        == 0
        and gw_response_hashes_valid
    )
    gauge_wave_hashes = gh_gauge_wave_tt_null_audit.get("source_hashes", {})
    gauge_wave_hashes_valid = bool(gauge_wave_hashes) and all(
        (ROOT / source_path).is_file()
        and _sha256(ROOT / source_path) == source_hash
        for source_path, source_hash in gauge_wave_hashes.items()
    )
    gh_gauge_wave_tt_null_passed = (
        gh_gauge_wave_tt_null_audit.get("status")
        == "PASS_GH_HARMONIC_GAUGE_WAVE_TT_NULL_CONTROL"
        and gh_gauge_wave_tt_null_audit.get("major_result", {}).get(
            "major_result_id"
        )
        == "CORE_CURVED_3P1_GH_GAUGE_WAVE_TT_NULL_CONTROL"
        and gh_gauge_wave_tt_null_audit.get("major_result", {}).get(
            "closure_level"
        )
        == "CLOSED_FOR_LANE"
        and all(gh_gauge_wave_tt_null_audit.get("checks", {}).values())
        and gh_gauge_wave_tt_null_audit.get("claim_promotion") is False
        and gh_gauge_wave_tt_null_audit.get("input_identity", {}).get(
            "detector_data_consumed"
        )
        is False
        and gh_gauge_wave_tt_null_audit.get("input_identity", {}).get(
            "holdout_consumed"
        )
        is False
        and gauge_wave_hashes_valid
    )
    gh_tt_boundary_hashes = gh_tt_sbp_sat_boundary_audit.get("source_hashes", {})
    gh_tt_boundary_hashes_valid = bool(gh_tt_boundary_hashes) and all(
        (ROOT / source_path).is_file()
        and _sha256(ROOT / source_path) == source_hash
        for source_path, source_hash in gh_tt_boundary_hashes.items()
    )
    gh_tt_sbp_sat_boundary_passed = (
        gh_tt_sbp_sat_boundary_audit.get("status")
        == "PASS_GH_LINEAR_TT_SBP_SAT_BOUNDARY_PILOT"
        and gh_tt_sbp_sat_boundary_audit.get("major_result", {}).get(
            "major_result_id"
        )
        == "CORE_CURVED_3P1_GH_LINEAR_TT_SBP_SAT_BOUNDARY_PILOT"
        and gh_tt_sbp_sat_boundary_audit.get("major_result", {}).get(
            "closure_level"
        )
        == "CLOSED_FOR_LANE"
        and all(gh_tt_sbp_sat_boundary_audit.get("checks", {}).values())
        and gh_tt_sbp_sat_boundary_audit.get("claim_promotion") is False
        and gh_tt_sbp_sat_boundary_audit.get("scope", {}).get(
            "full_rinne_cpbc_implemented"
        )
        is False
        and gh_tt_sbp_sat_boundary_audit.get("scope", {}).get(
            "periodic_gh_solver_modified"
        )
        is False
        and gh_tt_sbp_sat_boundary_audit.get("scope", {}).get("filtering")
        is False
        and gh_tt_sbp_sat_boundary_audit.get("scope", {}).get("clipping") is False
        and gh_tt_sbp_sat_boundary_audit.get("scope", {}).get(
            "parameter_fitting"
        )
        is False
        and gh_tt_sbp_sat_boundary_audit.get("major_result", {}).get("units", {}).get(
            "UET_symbols_used"
        )
        == []
        and gh_tt_boundary_hashes_valid
    )
    gh_full_u1_hashes = gh_full_u1_cpbc_slab_audit.get("source_hashes", {})
    gh_full_u1_hashes_valid = bool(gh_full_u1_hashes) and all(
        (ROOT / source_path).is_file()
        and _sha256(ROOT / source_path) == source_hash
        for source_path, source_hash in gh_full_u1_hashes.items()
    )
    gh_full_u1_mapping_partial = (
        gh_full_u1_cpbc_slab_audit.get("status")
        == "FAIL_GH_FULL_U1_CHEBYSHEV_SLAB_PILOT"
        and gh_full_u1_cpbc_slab_audit.get("major_result", {}).get(
            "major_result_id"
        )
        == "CORE_CURVED_3P1_GH_FULL_U1_CHEBYSHEV_SLAB_PILOT"
        and gh_full_u1_cpbc_slab_audit.get("major_result", {}).get(
            "closure_level"
        )
        == "PARTIAL"
        and all(
            gh_full_u1_cpbc_slab_audit.get("checks", {}).get(name) is True
            for name in (
                "projector_ranks_are_4_2_4",
                "projector_algebra_is_orthogonal_and_complete",
                "incoming_rhs_matches_all_three_projected_targets",
                "rhs_targets_match_rinne_normal_incidence_residuals",
                "constraint_compatible_lift_preserves_reduction_and_incoming_targets",
            )
        )
        and gh_full_u1_cpbc_slab_audit.get("major_result", {}).get(
            "dependency_unlocked"
        )
        == "none; the Core curved-3+1 CPBC parent and Gravity remain blocked"
        and gh_full_u1_cpbc_slab_audit.get("claim_promotion") is False
        and gh_full_u1_hashes_valid
    )
    gh_reduced_wave_hashes = gh_reduced_wave_comparator_audit.get(
        "source_hashes", {}
    )
    gh_reduced_wave_hashes_valid = bool(gh_reduced_wave_hashes) and all(
        (ROOT / source_path).is_file()
        and _sha256(ROOT / source_path) == source_hash
        for source_path, source_hash in gh_reduced_wave_hashes.items()
    )
    gh_reduced_wave_partial = (
        gh_reduced_wave_comparator_audit.get("status")
        == "PARTIAL_REDUCED_WAVE_BOUNDARY_COMPARATOR"
        and gh_reduced_wave_comparator_audit.get("major_result", {}).get(
            "major_result_id"
        )
        == "CORE_CURVED_3P1_GH_REDUCED_WAVE_BOUNDARY_COMPARATOR"
        and gh_reduced_wave_comparator_audit.get("major_result", {}).get(
            "closure_level"
        )
        == "PARTIAL"
        and all(
            gh_reduced_wave_comparator_audit.get("checks", {}).get(name) is True
            for name in (
                "no_resolved_growing_semidiscrete_mode",
                "random_perturbation_stays_bounded",
                "reduction_constraint_is_algebraic",
            )
        )
        and gh_reduced_wave_comparator_audit.get("checks", {}).get(
            "tt_packet_is_absorbed"
        ) is False
        and gh_reduced_wave_comparator_audit.get("claim_promotion") is False
        and gh_reduced_wave_comparator_audit.get("major_result", {}).get(
            "dependency_unlocked"
        )
        == "none; Core curved-3+1 parent and Gravity remain blocked"
        and gh_reduced_wave_hashes_valid
    )
    gh_reduced_wave_sbp_sat_hashes = gh_reduced_wave_sbp_sat_comparator_audit.get(
        "source_hashes", {}
    )
    gh_reduced_wave_sbp_sat_hashes_valid = bool(gh_reduced_wave_sbp_sat_hashes) and all(
        (ROOT / source_path).is_file()
        and _sha256(ROOT / source_path) == source_hash
        for source_path, source_hash in gh_reduced_wave_sbp_sat_hashes.items()
    )
    gh_reduced_wave_sbp_sat_passed = (
        gh_reduced_wave_sbp_sat_comparator_audit.get("status")
        == "PASS_REDUCED_TT_SBP_SAT_COMPARATOR"
        and gh_reduced_wave_sbp_sat_comparator_audit.get("major_result", {}).get(
            "major_result_id"
        )
        == "CORE_CURVED_3P1_GH_REDUCED_TT_SBP_SAT_COMPARATOR"
        and gh_reduced_wave_sbp_sat_comparator_audit.get("major_result", {}).get(
            "closure_level"
        )
        == "CLOSED_FOR_LANE"
        and all(gh_reduced_wave_sbp_sat_comparator_audit.get("checks", {}).values())
        and gh_reduced_wave_sbp_sat_comparator_audit.get("claim_promotion") is False
        and gh_reduced_wave_sbp_sat_comparator_audit.get("scope", {}).get(
            "full_first_order_gh_cpbc"
        )
        is False
        and gh_reduced_wave_sbp_sat_comparator_audit.get("major_result", {}).get(
            "dependency_unlocked", ""
        ).startswith("none;")
        and gh_reduced_wave_sbp_sat_hashes_valid
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
            "module": "docs/core/02_equations/covariant/uet_curved_3p1_constraints.py",
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
                "code_path": "docs/core/02_equations/covariant/uet_curved_3p1_constraints.py",
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
                "code_path": "docs/core/02_equations/covariant/uet_curved_3p1_constraints.py",
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
        "gh_linear_boundary_residuals": "PASS_DIAGNOSTIC_ONLY" if gh_linear_boundary_passed else "OPEN",
        "linearized_gw_detector_response": "PASS_DIAGNOSTIC_ONLY"
        if gh_gw_detector_response_passed
        else "OPEN",
        "gh_gauge_wave_tt_null_control": "PASS_DIAGNOSTIC_ONLY"
        if gh_gauge_wave_tt_null_passed
        else "OPEN",
        "gh_tt_sbp_sat_boundary_pilot": "PASS_DIAGNOSTIC_ONLY"
        if gh_tt_sbp_sat_boundary_passed
        else "OPEN",
        "gh_full_u1_cpbc_slab": "PARTIAL_MAPPING_ONLY_DISCRETIZATION_OPEN"
        if gh_full_u1_mapping_partial
        else "OPEN",
        "gh_full_u1_slab_evolution": "OPEN_POINTWISE_REDUCTION_AND_LIFT_STABILITY_TRADEOFF",
        "gh_reduced_wave_boundary_comparator": "PARTIAL_ALGEBRAIC_REDUCTION_AND_LOW_RESOLUTION_BOUNDEDNESS"
        if gh_reduced_wave_partial
        else "OPEN",
        "gh_reduced_wave_sbp_sat_comparator": "PASS_DIAGNOSTIC_ONLY"
        if gh_reduced_wave_sbp_sat_passed
        else "OPEN",
        "constraint_preserving_boundaries": "OPEN",
        "topic13_stress_energy_projection": "PASS_PRESCRIBED_TOPIC13_HE4_SOURCE"
        if matter_passed
        else "OPEN",
        "dimensional_observable_mapping": "OPEN",
    }
    parent_status = (
        "PARTIAL_CURVED_3P1_GH_PERIODIC_PRESCRIBED_MATTER_READY"
        if passed
        and geometry_passed
        and evolution_passed
        and gh_principal_passed
        and gh_nonlinear_passed
        and gh_time_passed
        and matter_passed
        else (
            "PARTIAL_CURVED_3P1_GH_PERIODIC_VACUUM_EVOLUTION_READY"
            if passed and geometry_passed and evolution_passed and gh_principal_passed and gh_nonlinear_passed and gh_time_passed
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
    if matter_passed:
        closed_components.extend(
            [
                "Topic 13 He-4/O(2) prescribed relativistic stress-energy tensor",
                "Eulerian energy, momentum, and spatial-stress projections",
                "trace-reversed GH prescribed matter source",
                "natural-to-SI multiplicative stress-energy scaling control",
            ]
        )
    if gh_linear_boundary_passed:
        closed_components.append(
            "source-matched linearized GH differential boundary residual evaluators (not applied to evolution)"
        )
    if gh_gw_detector_response_passed:
        closed_components.append(
            "source-matched finite-frequency linear TT-mode interferometer response diagnostic (not a UET prediction)"
        )
    if gh_gauge_wave_tt_null_passed:
        closed_components.append(
            "evolved periodic GH harmonic gauge-wave negative control rejected as TT detector strain"
        )
    if gh_tt_sbp_sat_boundary_passed:
        closed_components.append(
            "linearized standard-GR TT-sector non-periodic SBP-SAT boundary pilot only"
        )
    if gh_full_u1_mapping_partial:
        closed_components.append(
            "full ten-component normal-incidence u1-minus 4+2+4 target algebra and residual cross-check only; evolution discretization remains open"
        )
    if gh_reduced_wave_sbp_sat_passed:
        closed_components.append(
            "second-order reduced-TT SBP-SAT energy estimate and bidirectional outgoing-packet control only"
        )
    open_parent_requirements = [
        key
        for key, value in parent_requirements.items()
        if not (value == "CLOSED_AS_NO_GO" or value.startswith("PASS"))
    ]
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
            "equation_or_mapping": {
                **contract["equations"],
                **matter_verification["major_result"]["equation_or_mapping"],
                "linearized_gw_detector_response": gh_gw_detector_response_audit[
                    "major_result"
                ]["equation_or_mapping"],
                "gh_gauge_wave_tt_null_control": gh_gauge_wave_tt_null_audit[
                    "major_result"
                ]["equation_or_mapping"],
                "gh_linear_boundary_residuals": gh_linear_boundary_audit[
                    "major_result"
                ]["equation_or_mapping"],
                "gh_tt_sbp_sat_boundary_pilot": gh_tt_sbp_sat_boundary_audit[
                    "major_result"
                ]["equation_or_mapping"],
                "gh_full_u1_cpbc_slab_pilot": gh_full_u1_cpbc_slab_audit[
                    "major_result"
                ]["equation_or_mapping"],
                "gh_reduced_wave_boundary_comparator": gh_reduced_wave_comparator_audit[
                    "major_result"
                ]["equation_or_mapping"],
                "gh_reduced_wave_sbp_sat_comparator": gh_reduced_wave_sbp_sat_comparator_audit[
                    "major_result"
                ]["equation_or_mapping"],
            },
            "units": "geometric constraints plus one bounded SI linear detector-response lane; general observable mapping open",
            "derivation_class": "incremental curved 3+1 parent construction",
            "observable": "constraint residuals, ideal interferometer strain for one linearized TT plane-wave mode, and a GH pure-gauge null control; general mapping open",
            "data_role": "internal analytic controls",
            "verification_status": parent_status,
            "open_blockers": open_parent_requirements,
            "dependency_unlocked": "bounded linear TT detector-response, GH gauge-false-positive, TT-sector SBP-SAT boundary, full-u1 boundary-mapping, and reduced-TT SBP-SAT energy diagnostic lanes only; full GH CPBC evolution and general observable mapping remain open, and GR_CLASSICAL_COMPATIBILITY_LANE remains blocked",
            "claim_boundary": "partial parent construction; not CLOSED_FOR_CORE and not Gravity/GR compatibility",
        },
        "requirements": parent_requirements,
        "controlling_blocker": "curved_3p1_constraint_preserving_boundaries_and_dimensional_observable_mapping_missing"
        if matter_passed
        else "curved_3p1_constraint_preserving_boundaries_and_topic13_stress_energy_wiring_missing",
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
            {"path": MATTER_VERIFY.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": MATTER_FORMULA.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": MATTER_GATE.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_LINEAR_BOUNDARY_AUDIT.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_GW_DETECTOR_RESPONSE_AUDIT.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_GAUGE_WAVE_TT_NULL_AUDIT.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_TT_SBP_SAT_BOUNDARY_AUDIT.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_FULL_U1_CPBC_SLAB_AUDIT.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_REDUCED_WAVE_COMPARATOR_AUDIT.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GH_REDUCED_WAVE_SBP_SAT_COMPARATOR_AUDIT.relative_to(ROOT).as_posix(), "sha256": None},
        ],
        "claim_promotion": False,
    }

    addendum = {
        "schema_version": "1.0",
        "artifact": "uet_equation_correspondence_registry_curved_3p1_addendum",
        "generated_at": now,
        "extends": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json",
        "status": "CANDIDATE_ENTRY_PENDING_MERGE",
        "equation_entries": [
            {
                "equation_id": "uet.main_theory.curved_3p1.adm_constraints",
                "version": "adm-constraint-interface-v1",
                "classification": "standard_physics_constraint_interface",
                "relation_or_code_path": "docs/core/02_equations/covariant/uet_curved_3p1_constraints.py",
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
                "implementation_paths": ["docs/core/02_equations/covariant/uet_curved_3p1_constraints.py"],
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
                "relation_or_code_path": "docs/core/02_equations/covariant/uet_curved_3p1_geometry.py",
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
                "implementation_paths": ["docs/core/02_equations/covariant/uet_curved_3p1_geometry.py"],
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
                "relation_or_code_path": "docs/core/02_equations/covariant/uet_curved_3p1_adm_evolution.py",
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
                "implementation_paths": ["docs/core/02_equations/covariant/uet_curved_3p1_adm_evolution.py"],
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
                "relation_or_code_path": "docs/core/02_equations/covariant/uet_curved_3p1_adm_evolution.py",
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
                "implementation_paths": ["docs/core/02_equations/covariant/uet_curved_3p1_adm_evolution.py"],
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
                "relation_or_code_path": "docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py",
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
                "implementation_paths": ["docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py"],
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
                "relation_or_code_path": "docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py",
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
                "implementation_paths": ["docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py"],
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
                "relation_or_code_path": "docs/core/02_equations/covariant/uet_curved_3p1_gh_evolution.py",
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
                "implementation_paths": ["docs/core/02_equations/covariant/uet_curved_3p1_gh_evolution.py"],
                "verifier_paths": ["docs/scripts/audit/audit_uet_curved_3p1_gh_time_evolution.py", GH_TIME_VERIFY.relative_to(ROOT).as_posix(), "docs/core/test/test_uet_curved_3p1_gh_time_evolution.py"],
                "evidence_class": "INTERNAL_ANALYTIC_AND_NUMERICAL_CONVERGENCE_CONTROL",
                "proof_status": "periodic vacuum evolution and propagated-constraint controls pass; non-periodic boundaries and matter remain open",
                "downstream_dependencies": ["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"],
                "claim_boundary": gh_time_verification["major_result"]["claim_boundary"],
                "failure_mode": "periodic gauge-wave convergence is overread as a production numerical-relativity or matter-coupled solver",
                "next_hardening_step": "add constraint-preserving non-periodic boundaries and Topic 13 stress-energy wiring"
            },
            {
                "equation_id": "uet.main_theory.curved_3p1.topic13_prescribed_matter_source",
                "version": "topic13-prescribed-matter-wiring-v1",
                "classification": "standard_physics_matter_source_interface",
                "relation_or_code_path": "docs/core/02_equations/covariant/uet_curved_3p1_matter_wiring.py",
                "formula_ids": [
                    "UET-CURVED3P1-MATTER-TAB-021",
                    "UET-CURVED3P1-MATTER-ADM-022",
                    "UET-CURVED3P1-MATTER-GH-023"
                ],
                "variables": {
                    "T_ab": "declared lane-specific stress-energy tensor",
                    "rho": "Eulerian energy density",
                    "S_i": "Eulerian momentum density",
                    "S_ij": "Eulerian spatial stress",
                    "psi_ab": "spacetime metric; not UET Phi",
                    "kappa_E": "declared Einstein coupling; numeric SI provenance open"
                },
                "mathematical_role": "construct and project a prescribed Topic 13 stress-energy source into the GH metric RHS",
                "standard_physics_counterpart": "relativistic-fluid stress tensor, 3+1 matter projections, and trace-reversed Einstein source",
                "observable_mapping": {
                    "status": "PARTIAL",
                    "reason": "He-4/O(2) natural and SI stress scales are connected; detector and gravitational observables remain open"
                },
                "unit_lane": matter_verification["major_result"]["units"],
                "parameter_dimensions": matter_verification["major_result"]["units"],
                "source_or_origin": matter_verification["major_result"]["evidence_artifacts"],
                "assumptions": [
                    "(-,+,+,+) signature",
                    "prescribed matter state",
                    "future-normalized four velocity",
                    "heat flux orthogonal to four velocity",
                    "anisotropic stress symmetric, orthogonal, and trace free"
                ],
                "symmetry_and_conservation": "stress symmetry and projection reconstruction pass; stress-energy conservation evolution remains open",
                "limiting_cases": ["rest perfect fluid", "boosted perfect fluid", "vacuum null source"],
                "implementation_paths": ["docs/core/02_equations/covariant/uet_curved_3p1_matter_wiring.py"],
                "verifier_paths": [
                    "docs/scripts/audit/audit_uet_curved_3p1_matter_wiring.py",
                    MATTER_VERIFY.relative_to(ROOT).as_posix(),
                    "docs/core/test/test_uet_curved_3p1_matter_wiring.py"
                ],
                "evidence_class": "INTERNAL_FORMAL_ALGEBRAIC_AND_SOURCE_COMPOSITION_CONTROL",
                "proof_status": "prescribed stress-energy construction/projection and GH source pass; self-consistent matter evolution remains open",
                "downstream_dependencies": ["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"],
                "claim_boundary": matter_verification["major_result"]["claim_boundary"],
                "failure_mode": "prescribed source wiring is overread as a self-consistent matter-coupled spacetime solution",
                "next_hardening_step": "add constraint-preserving boundaries and a conservation-compatible matter evolution contract"
            },
            {
                "equation_id": "uet.main_theory.curved_3p1.gh_linear_differential_boundary_residuals",
                "version": "gh-linear-differential-boundary-residuals-v1",
                "classification": "standard_physics_boundary_condition_diagnostic",
                "relation_or_code_path": "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py",
                "formula_ids": [
                    "GH-BC-CONSTRAINT-C0MINUS-027",
                    "GH-BC-INCOMING-WEYL-030-033",
                    "GH-BC-U2-CURL-029",
                    "GH-BC-GAUGE-PROJECTION-035-036"
                ],
                "variables": {
                    "delta_psi_ab": "linear spacetime-metric perturbation; not UET Phi",
                    "delta_Pi_ab": "linear normal metric-derivative perturbation; not UET Pi",
                    "delta_Phi_iab": "linear spatial metric-derivative perturbation; not UET Phi",
                    "beta_n": "outward normal shift component",
                    "gamma2": "first-order reduction-constraint damping parameter"
                },
                "mathematical_role": "evaluate incoming subsidiary-constraint, Weyl/Psi_0, gauge-data, and positive-shift u2_A definition-curl boundary residuals",
                "standard_physics_counterpart": "linearized/frozen-background first-order generalized-harmonic boundary conditions of Rinne (2006), Eqs. 27-36",
                "observable_mapping": {"status": "OPEN", "reason": "boundary residuals are numerical/formulation diagnostics, not gravitational detector observables"},
                "unit_lane": "geometric c=1 local orthonormal frame",
                "parameter_dimensions": {
                    "delta_psi": "1",
                    "delta_Pi_and_delta_Phi": "L^-1",
                    "gamma2": "L^-1",
                    "constraint_and_weyl_residuals": "L^-2",
                    "gauge_residual": "L^-1"
                },
                "source_or_origin": {
                    "formula_source": "https://arxiv.org/abs/gr-qc/0606053",
                    "formula_locators": "Eqs. 27-33 and 35-36",
                    "well_posedness_caution": "https://arxiv.org/abs/gr-qc/0303040"
                },
                "assumptions": ["linear perturbations about Minkowski", "local orthonormal frame", "fixed smooth face", "strictly subluminal normal shift", "source GH first-order variables and sign convention"],
                "symmetry_and_conservation": "projected Weyl tensor is transverse and trace-free; subsidiary-constraint propagation under a discrete boundary scheme remains unverified",
                "limiting_cases": ["nonpositive normal shift: u1_minus incoming", "positive subluminal normal shift: u1_minus and u2_A incoming", "zero perturbation with homogeneous data"],
                "implementation_paths": ["docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py"],
                "verifier_paths": ["docs/scripts/audit/audit_uet_curved_3p1_gh_linear_boundary.py", GH_LINEAR_BOUNDARY_AUDIT.relative_to(ROOT).as_posix(), "docs/core/05_tests/regression/root/test_uet_curved_3p1_gh_linear_boundary.py"],
                "evidence_class": "INTERNAL_SOURCE_MATCHED_FORMULA_AND_ANALYTIC_CONTROL",
                "proof_status": "linear boundary residual formulas and projector kernels pass deterministic controls; no evolution enforcement or IBVP stability result",
                "downstream_dependencies": ["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"],
                "claim_boundary": "frozen-background linear residual evaluator only; not implemented nonlinear CPBC or a well-posed repository IBVP",
                "failure_mode": "correct residual evaluation is overread as a stable discrete boundary treatment",
                "next_hardening_step": "apply to a non-periodic SBP/SAT GH boundary evolution and verify constraint energy, stability, convergence, and corners"
            },
            {
                "equation_id": "uet.main_theory.curved_3p1.gh_full_u1_boundary_slab_pilot",
                "version": "gh-full-u1-chebyshev-slab-pilot-v1",
                "classification": "standard_physics_boundary_evolution_diagnostic",
                "relation_or_code_path": "docs/core/02_equations/covariant/uet_curved_3p1_gh_full_u1_slab.py",
                "formula_ids": [
                    "GH-BC-U1-MINUS-4-2-4-PROJECTION-001",
                    "GH-BC-U1-INCOMING-RHS-NORMAL-INCIDENCE-002",
                    "GH-BC-U1-CONSTRAINT-COMPATIBLE-LIFT-EXPERIMENT-003"
                ],
                "variables": {
                    "psi_ab": "linearized spacetime metric perturbation; not UET Phi",
                    "Pi_ab": "normal time derivative variable; not UET Pi",
                    "Phi_xab": "normal spatial derivative variable; not UET Phi",
                    "q_ab": "incoming u1-minus characteristic field",
                    "P_C_P_P_P_G": "source-defined constraint, physical, and gauge projectors"
                },
                "mathematical_role": "match the 4+2+4 incoming-u1 boundary RHS targets to the normal-incidence constraint, Weyl, and gauge residuals, then compare endpoint and reduction-compatible discretizations",
                "standard_physics_counterpart": "frozen-background first-order GH differential boundary conditions of Rinne (2006), Eqs. 27-36 and Sec. 5.1",
                "observable_mapping": {"status": "OPEN", "reason": "boundary residual, reduction constraint, and pulse energy are numerical diagnostics rather than gravitational observables"},
                "unit_lane": "geometric c=1 with slab length scale L0=1",
                "parameter_dimensions": gh_full_u1_cpbc_slab_audit["major_result"]["units"],
                "source_or_origin": {
                    "formula_source": "https://arxiv.org/abs/gr-qc/0606053",
                    "formula_locators": "Eqs. 27-36 and Sec. 5.1",
                    "local_evidence": GH_FULL_U1_CPBC_SLAB_AUDIT.relative_to(ROOT).as_posix(),
                    "source_hashes": gh_full_u1_cpbc_slab_audit["source_hashes"]
                },
                "assumptions": ["linear perturbations about Minkowski", "zero shift", "one spatial normal with no tangential derivatives", "homogeneous constraint and Weyl data", "prescribed gauge-data rate", "gamma0 gauge-constraint damping excluded"],
                "symmetry_and_conservation": "the 4+2+4 target algebra matches residual evaluation; pointwise replacement leaves a nonzero discrete reduction residual, while the cubic compatible lift is unstable",
                "limiting_cases": ["homogeneous zero state", "normal-incidence incoming u1-minus only", "no positive-shift u2_A modes"],
                "implementation_paths": ["docs/core/02_equations/covariant/uet_curved_3p1_gh_full_u1_slab.py"],
                "verifier_paths": ["docs/scripts/audit/audit_curved_3p1_gh_full_u1_cpbc_slab.py", GH_FULL_U1_CPBC_SLAB_AUDIT.relative_to(ROOT).as_posix(), "docs/core/05_tests/regression/root/test_uet_curved_3p1_gh_full_u1_slab.py"],
                "evidence_class": "INTERNAL_SOURCE_MATCHED_FORMULA_AND_PARTIAL_NUMERICAL_DIAGNOSTIC",
                "proof_status": "4+2+4 projector and residual identities pass; pointwise Chebyshev spectrum/noise screens pass but pulse/reduction limits fail; the reduction-compatible lift preserves the identity but is spectrally unstable; no CPBC evolution closure",
                "downstream_dependencies": [],
                "claim_boundary": "partial full-u1 boundary-mapping diagnostic only; not stable full GH CPBC, nonlinear well-posedness, Gravity compatibility, or UET closure",
                "failure_mode": "the pointwise incoming RHS and a reduction-compatible lift each solve only one side of the discrete trade-off; either is overread as a complete stable constraint-preserving evolution",
                "next_hardening_step": "derive a boundary/SBP discretization that preserves the reduction constraint without the lift's growing modes, then rerun pulse reflection and convergence gates"
            },
            {
                "equation_id": "uet.main_theory.curved_3p1.gh_reduced_wave_boundary_comparator",
                "version": "gh-reduced-wave-algebraic-phi-boundary-comparator-v1",
                "classification": "standard_physics_second_order_boundary_comparator",
                "relation_or_code_path": "docs/core/02_equations/covariant/uet_curved_3p1_gh_full_u1_slab.py",
                "formula_ids": ["GH-BC-U1-REDUCED-WAVE-ALGEBRAIC-PHI-COMPARATOR-001"],
                "variables": {
                    "psi_ab": "linearized spacetime metric perturbation; not UET Phi",
                    "Pi_ab": "normal time derivative variable; not UET Pi",
                    "Phi_xab": "spatial derivative variable constrained algebraically to D_x(psi_ab); not UET Phi",
                    "q_ab": "incoming u1-minus characteristic field",
                },
                "mathematical_role": "compare a second-order algebraic-reduction wave formulation against the full-u1 boundary target without treating it as the independent-variable first-order GH CPBC system",
                "standard_physics_counterpart": "frozen-background linear GH wave system with algebraic reduction Phi_xab=D_x(psi_ab)",
                "observable_mapping": {"status": "OPEN", "reason": "spectrum and pulse energy are numerical diagnostics rather than gravitational observables"},
                "unit_lane": "geometric c=1 with slab length scale L0=1",
                "parameter_dimensions": gh_reduced_wave_comparator_audit["major_result"]["units"],
                "source_or_origin": {
                    "formula_source": "https://arxiv.org/abs/gr-qc/0606053",
                    "formula_locators": "Eqs. 27-36 and Sec. 5.1",
                    "local_evidence": GH_REDUCED_WAVE_COMPARATOR_AUDIT.relative_to(ROOT).as_posix(),
                    "source_hashes": gh_reduced_wave_comparator_audit["source_hashes"],
                },
                "assumptions": ["linear perturbations about Minkowski", "zero shift", "one spatial normal with no tangential derivatives", "homogeneous constraint and Weyl data", "prescribed gauge-data rate", "Phi_xab=D_x(psi_ab) imposed algebraically"],
                "symmetry_and_conservation": "algebraic reduction remains at roundoff in the declared pulse test; a semidiscrete energy estimate and spatial convergence are open",
                "limiting_cases": ["homogeneous zero state", "normal-incidence incoming u1-minus only", "no positive-shift u2_A modes"],
                "implementation_paths": ["docs/core/02_equations/covariant/uet_curved_3p1_gh_full_u1_slab.py"],
                "verifier_paths": ["docs/scripts/audit/audit_curved_3p1_gh_full_u1_cpbc_slab.py", GH_REDUCED_WAVE_COMPARATOR_AUDIT.relative_to(ROOT).as_posix(), "docs/core/05_tests/regression/root/test_uet_curved_3p1_gh_full_u1_slab.py"],
                "evidence_class": "INTERNAL_SYNTHETIC_SECOND_ORDER_COMPARATOR_PARTIAL",
                "proof_status": "degree-8 algebraic reduction, spectrum, and noise screens pass; degree-12 integrated packet remainder exceeds the unchanged 0.05 limit, higher-resolution energy is non-monotone, and degree 20 has one eigenvalue above the unchanged 1e-6 tolerance",
                "downstream_dependencies": [],
                "claim_boundary": "partial second-order comparator only; not full first-order GH CPBC, continuum well-posedness, Gravity compatibility, or UET closure",
                "failure_mode": "a discrete algebraic reduction or one passing low-resolution screen is overread as a converged stable full-GH boundary evolution",
                "next_hardening_step": "derive a discrete energy estimate and establish spatial convergence and high-order spectral behavior without changing the declared thresholds",
            },
            {
                "equation_id": "uet.main_theory.curved_3p1.gh_reduced_tt_sbp_sat_energy_comparator",
                "version": "gh-reduced-tt-sbp-sat-energy-v1",
                "classification": "standard_physics_reduced_tt_boundary_evolution_diagnostic",
                "relation_or_code_path": "docs/scripts/audit/audit_curved_3p1_gh_reduced_wave_sbp_sat.py",
                "formula_ids": [
                    "GH-TT-REDUCED-ALGEBRAIC-GRADIENT-001",
                    "GH-TT-REDUCED-SBP-SAT-RHS-002",
                    "GH-TT-REDUCED-SEMIDISCRETE-ENERGY-003",
                ],
                "variables": {
                    "h_A": "dimensionless standard-GR TT metric polarization, A in {+,x}",
                    "Pi_A": "standard-GR normal time derivative variable; not UET Pi",
                    "G_A": "spatial derivative D(h_A), reconstructed algebraically; not UET Phi",
                    "H": "LGL diagonal SBP norm matrix",
                    "e_L_e_R": "left/right endpoint basis vectors",
                },
                "mathematical_role": "test an energy-stable second-order TT outgoing-wave SAT comparator with no independent gradient state",
                "standard_physics_counterpart": "one-dimensional standard linearized-GR TT wave equation with homogeneous outgoing characteristic penalties",
                "observable_mapping": {
                    "status": "OPEN",
                    "reason": "discrete energy, characteristic, and packet diagnostics are not gravitational observables",
                },
                "unit_lane": "geometric c=1 with slab length scale L0=1",
                "parameter_dimensions": gh_reduced_wave_sbp_sat_comparator_audit[
                    "major_result"
                ]["units"],
                "source_or_origin": {
                    "formula_source": "https://arxiv.org/abs/gr-qc/0606053",
                    "formula_locator": "Rinne (2006), frozen-background linear GH boundary target; the reduced TT SAT energy identity is derived and tested in the local audit",
                    "local_evidence": GH_REDUCED_WAVE_SBP_SAT_COMPARATOR_AUDIT.relative_to(
                        ROOT
                    ).as_posix(),
                    "source_hashes": gh_reduced_wave_sbp_sat_comparator_audit[
                        "source_hashes"
                    ],
                },
                "assumptions": [
                    "linear perturbations about Minkowski",
                    "zero shift and one spatial normal",
                    "two standard TT polarizations only",
                    "LGL diagonal-norm SBP operator on a finite slab",
                    "homogeneous no-incoming characteristic data",
                    "G_A=D(h_A) reconstructed algebraically",
                ],
                "symmetry_and_conservation": "the exact SBP identity gives dE/dt=-sum_A(Pi_A,L^2+Pi_A,R^2)<=0; floating-point SBP defect is recorded separately",
                "limiting_cases": [
                    "zero state remains zero",
                    "left- and right-going outgoing Gaussian packets",
                    "first-order TT RHS agreement on G_A=D(h_A)",
                ],
                "implementation_paths": [
                    "docs/scripts/audit/audit_curved_3p1_gh_reduced_wave_sbp_sat.py"
                ],
                "verifier_paths": [
                    "docs/scripts/audit/audit_curved_3p1_gh_reduced_wave_sbp_sat.py",
                    GH_REDUCED_WAVE_SBP_SAT_COMPARATOR_AUDIT.relative_to(ROOT).as_posix(),
                    "docs/core/05_tests/regression/root/test_uet_curved_3p1_gh_reduced_wave_sbp_sat.py",
                ],
                "evidence_class": "INTERNAL_ANALYTIC_AND_SYNTHETIC_STANDARD_GR_CONTROL",
                "proof_status": "declared semidiscrete energy identity, first/second-order reduction-subspace RHS equivalence, bounded spectrum, bidirectional packet absorption, and fourth-order temporal refinement pass; no spatial continuum or full GH CPBC closure",
                "downstream_dependencies": [],
                "claim_boundary": "second-order standard-GR TT comparator only; not full first-order GH CPBC, curved 3+1 parent closure, Gravity compatibility, or UET closure",
                "failure_mode": "a TT-sector energy estimate is overread as stability or well-posedness of the coupled constraint/physical/gauge boundary system",
                "next_hardening_step": "derive and verify a projector-aware SBP-SAT energy estimate for the full incoming GH constraint, physical, and gauge sectors without changing locked thresholds",
            },
            {
                "equation_id": "uet.main_theory.curved_3p1.linear_gw_detector_response",
                "version": "linear-gw-detector-response-v1",
                "classification": "standard_physics_detector_response_mapping",
                "relation_or_code_path": "docs/core/02_equations/covariant/uet_curved_3p1_gw_detector_response.py",
                "variables": {
                    "h_ij": "dimensionless spatial metric perturbation in the declared asymptotically flat wave zone",
                    "h_TT_ij": "transverse-traceless plane-wave Fourier mode",
                    "n_i": "dimensionless unit propagation direction",
                    "u_i_v_i": "dimensionless equal-arm unit vectors",
                    "f": "frequency in s^-1",
                    "L": "arm length in m",
                    "h_D": "dimensionless ideal detector strain response",
                    "DeltaL_equiv": "equivalent differential length in m"
                },
                "mathematical_role": "map one linearized GH spatial-metric Fourier mode through TT projection and finite-frequency equal-arm interferometer response to strain and equivalent length",
                "standard_physics_counterpart": "linearized-GR equal-arm Michelson single-round-trip response without optical cavities",
                "observable_mapping": {
                    "status": "CLOSED_FOR_LANE",
                    "observable": "ideal equal-arm interferometer strain response to one TT plane-wave mode",
                    "general_curved_space_mapping": "OPEN"
                },
                "unit_lane": "SI detector response; metric and strain dimensionless, frequency s^-1, arm length m",
                "parameter_dimensions": gh_gw_detector_response_audit["units"],
                "source_or_origin": gh_gw_detector_response_audit["literature_basis"],
                "assumptions": gh_gw_detector_response_audit["assumptions"],
                "symmetry_and_conservation": "TT projection is transverse and trace-free; this is a measurement operator, not an added dynamical source or conserved UET state",
                "limiting_cases": ["zero-frequency arm transfer tends to one", "plus and cross polarization analytic controls", "negative-frequency transfer is the complex conjugate"],
                "implementation_paths": ["docs/core/02_equations/covariant/uet_curved_3p1_gw_detector_response.py"],
                "verifier_paths": ["docs/scripts/audit/audit_uet_curved_3p1_gh_gw_detector_response.py", GH_GW_DETECTOR_RESPONSE_AUDIT.relative_to(ROOT).as_posix(), "docs/core/05_tests/regression/root/test_uet_curved_3p1_gw_detector_response.py"],
                "evidence_class": "SOURCE_MATCHED_STANDARD_FORMULA_WITH_ANALYTIC_INTERNAL_CONTROLS",
                "proof_status": "bounded ideal detector response matches the declared finite-frequency source formula and analytic controls; no detector data or UET evolution prediction",
                "downstream_dependencies": ["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"],
                "claim_boundary": gh_gw_detector_response_audit["major_result"]["claim_boundary"],
                "failure_mode": "ideal single-mode transfer is overread as detector calibration, strong-field radiation extraction, or a UET prediction",
                "next_hardening_step": "connect a verified GH wave-zone extraction and temporal Fourier map, then add detector calibration, noise, and uncertainty only when source-backed inputs exist"
            }
        ],
    }
    return verification, formula, gate, addendum


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    verification, formula, gate, addendum = build_artifacts()
    VERIFY.write_text(json.dumps(verification, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    FORMULA.write_text(json.dumps(formula, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
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
    gate["evidence_artifacts"][17]["sha256"] = _sha256(MATTER_VERIFY)
    gate["evidence_artifacts"][18]["sha256"] = _sha256(MATTER_FORMULA)
    gate["evidence_artifacts"][19]["sha256"] = _sha256(MATTER_GATE)
    gate["evidence_artifacts"][20]["sha256"] = _sha256(GH_LINEAR_BOUNDARY_AUDIT)
    gate["evidence_artifacts"][21]["sha256"] = _sha256(GH_GW_DETECTOR_RESPONSE_AUDIT)
    gate["evidence_artifacts"][22]["sha256"] = _sha256(GH_GAUGE_WAVE_TT_NULL_AUDIT)
    gate["evidence_artifacts"][23]["sha256"] = _sha256(GH_TT_SBP_SAT_BOUNDARY_AUDIT)
    gate["evidence_artifacts"][24]["sha256"] = _sha256(GH_FULL_U1_CPBC_SLAB_AUDIT)
    gate["evidence_artifacts"][25]["sha256"] = _sha256(GH_REDUCED_WAVE_COMPARATOR_AUDIT)
    gate["evidence_artifacts"][26]["sha256"] = _sha256(
        GH_REDUCED_WAVE_SBP_SAT_COMPARATOR_AUDIT
    )
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    ADDENDUM.write_text(json.dumps(addendum, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": verification["status"], "parent_status": gate["status"], "controlling_blocker": gate["controlling_blocker"]}, indent=2))
    return 0 if verification["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
