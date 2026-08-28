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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifacts() -> tuple[dict, dict, dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    geometry_verification = json.loads(GEOMETRY_VERIFY.read_text(encoding="utf-8"))
    geometry_formula = json.loads(GEOMETRY_FORMULA.read_text(encoding="utf-8"))
    geometry_passed = (
        geometry_verification.get("status") == "PASS_CURVED_3P1_GEOMETRY_OPERATOR"
        and geometry_verification.get("major_result", {}).get("closure_level")
        == "CLOSED_FOR_LANE"
        and geometry_formula.get("status") == "PASS_NUMERICAL_GEOMETRY_FORMULAS"
        and all(geometry_verification.get("checks", {}).values())
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
        "lapse_shift_gauge": "OPEN",
        "metric_and_extrinsic_curvature_evolution": "OPEN",
        "strong_hyperbolicity": "OPEN",
        "constraint_propagation": "OPEN",
        "temporal_spatial_convergence": "OPEN",
        "topic13_stress_energy_projection": "OPEN",
        "dimensional_observable_mapping": "OPEN",
    }
    gate = {
        "schema_version": "1.0",
        "artifact": "core_curved_3p1_parent_gate",
        "generated_at": now,
        "status": "PARTIAL_CURVED_3P1_PARENT_GEOMETRY_OPERATOR_READY" if passed and geometry_passed else ("PARTIAL_CURVED_3P1_PARENT_CONSTRAINT_INTERFACE_READY" if passed else "BLOCKED"),
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_OBSERVABLE_PARENT_READY",
            "topic": "core",
            "closure_level": "PARTIAL",
            "what_is_closed": ([
                "ADM constraint evaluation interface",
                "periodic-grid metric-to-Ricci operator",
                "periodic-grid covariant momentum-tensor divergence",
                "second-order spatial geometry convergence",
            ] if passed and geometry_passed else (["ADM constraint evaluation interface"] if passed else [])),
            "equation_or_mapping": contract["equations"],
            "units": "geometric constraint lane; SI observable mapping open",
            "derivation_class": "incremental curved 3+1 parent construction",
            "observable": "constraint residual diagnostics only",
            "data_role": "internal analytic controls",
            "verification_status": "PARTIAL_CURVED_3P1_PARENT_GEOMETRY_OPERATOR_READY" if passed and geometry_passed else ("PARTIAL_CURVED_3P1_PARENT_CONSTRAINT_INTERFACE_READY" if passed else "BLOCKED"),
            "open_blockers": [key for key, value in parent_requirements.items() if value != "PASS"],
            "dependency_unlocked": "gauge-declared metric/K evolution research wave only; GR_CLASSICAL_COMPATIBILITY_LANE remains blocked",
            "claim_boundary": "partial parent construction; not CLOSED_FOR_CORE and not Gravity/GR compatibility",
        },
        "requirements": parent_requirements,
        "controlling_blocker": "curved_3p1_gauge_evolution_hyperbolicity_and_constraint_propagation_missing",
        "evidence_artifacts": [
            {"path": VERIFY.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": FORMULA.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GEOMETRY_VERIFY.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": GEOMETRY_FORMULA.relative_to(ROOT).as_posix(), "sha256": None},
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
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    ADDENDUM.write_text(json.dumps(addendum, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": verification["status"], "parent_status": gate["status"], "controlling_blocker": gate["controlling_blocker"]}, indent=2))
    return 0 if verification["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
