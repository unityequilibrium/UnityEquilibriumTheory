"""Audit the standard lattice/momentum-relaxing heat parent for Topic 13."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import hashlib
import json
import math

from docs.core.uet_lattice_momentum_relaxing_heat_parent import (
    lattice_momentum_relaxing_heat_parent_state,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_lattice_momentum_relaxing_heat_parent_audit.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_lattice_heat_parent_addendum.json"
EQUATION_ID = "standard.lattice.thermal.momentum_relaxing_heat_parent"


def _sha(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def _relative(first: float, second: float) -> float:
    return abs(first - second) / max(abs(first), abs(second), 1.0e-300)


def main() -> int:
    reference = lattice_momentum_relaxing_heat_parent_state()
    no_resistive = lattice_momentum_relaxing_heat_parent_state(resistive_rate=0.0)
    rate_rows = [
        lattice_momentum_relaxing_heat_parent_state(resistive_rate=rate)
        for rate in (0.0125, 0.025, 0.05)
    ]
    resolution_rows = [
        lattice_momentum_relaxing_heat_parent_state(radial_order=order)
        for order in (16, 24, 48, 80)
    ]
    scale_rows = [
        lattice_momentum_relaxing_heat_parent_state(
            temperature=0.25 * scale,
            normal_rate=0.20 * scale,
            resistive_rate=0.025 * scale,
        )
        for scale in (0.5, 1.0, 2.0)
    ]
    rate_products = [
        row.resistive_rate * float(row.conductivity_natural)
        for row in rate_rows
    ]
    rate_scaling_residual = max(
        _relative(value, rate_products[1]) for value in rate_products
    )
    final_resolution_change = _relative(
        float(resolution_rows[-1].conductivity_natural),
        float(resolution_rows[-2].conductivity_natural),
    )
    scale_exponent = math.log(
        float(scale_rows[-1].conductivity_natural)
        / float(scale_rows[1].conductivity_natural)
    ) / math.log(2.0)

    checks = {
        "normal_collision_symmetric": reference.normal_symmetry_residual <= 1.0e-14,
        "normal_collision_psd": reference.normal_minimum_eigenvalue >= -1.0e-12,
        "normal_collision_preserves_crystal_momentum": reference.normal_momentum_null_residual <= 1.0e-12,
        "linear_debye_heat_source_overlaps_momentum": reference.source_momentum_overlap >= 1.0 - 1.0e-12,
        "zero_resistive_rate_has_no_finite_steady_response": not no_resistive.finite_steady_conductivity and no_resistive.conductivity_natural is None,
        "zero_resistive_rate_operator_is_singular": no_resistive.total_minimum_eigenvalue <= 1.0e-12,
        "positive_resistive_rate_relaxes_momentum": _relative(reference.resistive_momentum_relaxation_rate, reference.resistive_rate) <= 1.0e-12,
        "positive_resistive_rate_makes_operator_spd": reference.total_minimum_eigenvalue > 0.0,
        "onsager_symmetry": reference.total_symmetry_residual <= 1.0e-14,
        "entropy_production_nonnegative": reference.minimum_entropy_quadratic_eigenvalue > 0.0,
        "finite_response_matches_analytic_null_mode_limit": float(reference.conductivity_relative_residual) <= 1.0e-11,
        "inverse_resistive_rate_scaling": rate_scaling_residual <= 1.0e-11,
        "quadrature_convergence": final_resolution_change <= 1.0e-8,
        "natural_unit_conductivity_scales_as_E2": abs(scale_exponent - 2.0) <= 1.0e-10,
        "no_fit_holdout_or_physical_kubo": not reference.parameter_fitting_performed and not reference.xie_2026_accessed and not reference.physical_kubo_coefficient_emitted,
        "no_uet_ontology_relabeling": not reference.uet_mapping_claimed,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    passed = all(checks.values())
    status = "PASS_SCOPED_LATTICE_HEAT_PARENT" if passed else "WARN_LATTICE_HEAT_PARENT"
    equations = {
        "normal_collision": "C_N=gamma_N*(I-|P><P|)",
        "resistive_collision": "C_R=gamma_R*I",
        "linearized_pbte": "(C_N+C_R) chi=S_T",
        "heat_source": "S_T(p)=sqrt[dPi_3*n_B*(1+n_B)/3]*beta*E(p)*v(p)",
        "conductivity": "kappa_natural=S_T^T*(C_N+C_R)^(-1)*S_T",
        "entropy_production": "sigma[chi]=chi^T*(C_N+C_R)*chi>=0",
        "singular_limit": "gamma_R=0 and <P|S_T>!=0 implies no finite steady conductivity",
    }
    what_is_closed = [
        "A lattice rest frame and an explicit positive momentum-relaxing operator evade the current relativistic Landau-frame heat-rank obstruction at standard-comparator level.",
        "Normal collisions preserve crystal momentum, while the declared resistive control removes that null mode and yields a finite positive heat response.",
        "The gamma_R to zero limit is singular when the Debye heat source overlaps momentum, so a finite conductivity cannot be manufactured from normal collisions alone.",
        "The finite response satisfies Onsager symmetry, nonnegative entropy production, inverse resistive-rate scaling, quadrature convergence, and E^2 natural-unit scaling.",
    ]
    open_blockers = [
        "physical_lattice_collision_kernel_and_rate_provenance_missing",
        "uet_action_to_lattice_quasiparticle_and_current_mapping_missing",
        "material_specific_dispersion_boundary_and_Umklapp_channels_missing",
        "physical_Kubo_and_SI_frame_normalization_missing",
        "independent_alpha_Phi_K_and_TTG_source_closure_missing",
    ]
    source_paths = [
        "docs/core/uet_lattice_momentum_relaxing_heat_parent.py",
        "docs/core/test/test_topic13_lattice_momentum_relaxing_heat_parent.py",
        "docs/scripts/audit/audit_topic13_lattice_momentum_relaxing_heat_parent.py",
    ]
    prior_path = "docs/core/artifacts/t13_coupled_response_heat_carrier_no_go_audit.json"
    artifact = {
        "schema_version": "t13-lattice-momentum-relaxing-heat-parent-v1",
        "major_result_id": "T13_LATTICE_MOMENTUM_RELAXING_HEAT_PARENT",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
        "closure_disposition": "STANDARD_COMPARATOR_PARENT_READY" if passed else "OPEN",
        "verification_status": status,
        "what_is_closed": what_is_closed,
        "equation_registry_ids": [EQUATION_ID],
        "registration_status": "STANDARD_COMPARATOR_NOT_UET_EQUATION",
        "equation_or_mapping": equations,
        "ontology": {
            "state": "linearized acoustic quasiparticle distribution in a declared lattice rest frame",
            "C": "unchanged and absent from the comparator state",
            "Phi": "unchanged and absent from the comparator state",
            "R_gen": "excluded",
            "R_obs": "excluded",
        },
        "unit_lane": reference.unit_lane,
        "units": {
            "T_E_gamma_p": "E",
            "sound_speed": "1",
            "heat_source": "E^(3/2)",
            "collision_operator": "E",
            "kappa_natural": "E^2",
        },
        "derivation_class": "standard_physics_synthetic_pbte_parent",
        "observable": "Natural-unit heat-response form in a synthetic lattice rest frame, not material conductivity",
        "data_role": "SYNTHETIC_STANDARD_COMPARATOR",
        "reference_witness": asdict(reference),
        "zero_resistive_witness": asdict(no_resistive),
        "resistive_rate_sweep": [asdict(row) for row in rate_rows],
        "resolution_sweep": [asdict(row) for row in resolution_rows],
        "energy_scale_sweep": [asdict(row) for row in scale_rows],
        "derived_metrics": {
            "inverse_rate_scaling_residual": rate_scaling_residual,
            "final_quadrature_relative_change": final_resolution_change,
            "natural_unit_energy_scaling_exponent": scale_exponent,
        },
        "thresholds": {
            "matrix_relative": 1.0e-12,
            "analytic_response_relative": 1.0e-11,
            "quadrature_relative": 1.0e-8,
            "energy_scaling_exponent_absolute": 1.0e-10,
        },
        "checks": checks,
        "open_blockers": open_blockers,
        "controlling_blocker": "physical_lattice_collision_kernel_and_uet_to_lattice_mapping_missing",
        "source_hashes": {path: _sha(path) for path in source_paths},
        "evidence_artifacts": [{"path": prior_path, "sha256": _sha(prior_path)}],
        "dependency_unlocked": [
            "physical_lattice_pbte_collision_source_provenance_audit",
            "uet_to_lattice_quasiparticle_observable_mapping_design",
        ],
        "full_core_unlock": False,
        "claim_promotion": False,
        "xie_2026_accessed": False,
        "parameter_fitting_performed": False,
        "claim_boundary": "Standard-physics synthetic lattice parent only; not a UET transport derivation, physical Umklapp rate, material Kubo/SI coefficient, TTG prediction, external validation, or Full Topic 13 closure.",
    }
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": artifact["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": what_is_closed,
        "WHAT_REMAINS_OPEN": open_blockers,
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Constructed the first explicit preferred-frame momentum-relaxing heat parent allowed by the preceding no-go result.",
        "EQUATION_OR_MAPPING": equations,
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": "Replace synthetic rates with a source-backed lattice collision kernel and derive, rather than assume, the UET-to-lattice quasiparticle/current mapping.",
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    entry = {
        "equation_id": EQUATION_ID,
        "version": "1",
        "classification": "standard_physics_lattice_heat_parent",
        "relation_or_code_path": equations,
        "ontology": artifact["ontology"],
        "standard_physics_counterpart": "Linearized phonon Boltzmann equation with normal and resistive collisions",
        "variables": {
            "C_N": "normal collision operator preserving crystal momentum",
            "C_R": "resistive Umklapp/boundary/open-bath control operator",
            "S_T": "temperature-gradient heat source",
            "chi": "linearized distribution response",
            "kappa_natural": "natural-unit heat-response form",
        },
        "mathematical_role": "preferred-frame escape parent for the relativistic heat-rank no-go",
        "observable_mapping": artifact["observable"],
        "unit_lane": artifact["unit_lane"],
        "units": artifact["units"],
        "parameter_dimensions": artifact["units"],
        "derivation_class": artifact["derivation_class"],
        "source_or_origin": "Synthetic Debye PBTE comparator; rates are declared controls",
        "assumptions": {
            "linear_isotropic_dispersion": "E=c_s*p",
            "lattice_rest_frame": True,
            "normal_operator_preserves_momentum": True,
            "resistive_rate_external_control": True,
        },
        "symmetry_and_conservation": "C_N and C_R symmetric positive semidefinite; C_N preserves crystal momentum; C_R relaxes it",
        "limiting_cases": ["gamma_R=0", "gamma_R>0", "uniform energy rescaling", "radial quadrature refinement"],
        "implementation_paths": [source_paths[0]],
        "verifier_paths": [source_paths[1], source_paths[2]],
        "observable": artifact["observable"],
        "data_role": artifact["data_role"],
        "evidence_class": "INTERNAL_SYNTHETIC_STANDARD_COMPARATOR",
        "proof_status": "STANDARD_PARENT_STRUCTURAL_LIMIT_VERIFIED",
        "verification_status": status,
        "evidence_artifacts": [{"path": OUT.relative_to(ROOT).as_posix(), "sha256": _sha(OUT)}],
        "downstream_dependencies": artifact["dependency_unlocked"],
        "dependency_role": "nonphysical_design_parent",
        "physical_dependency_unlock": False,
        "controlling_blocker": artifact["controlling_blocker"],
        "failure_mode": open_blockers,
        "next_hardening_step": artifact["report"]["NEXT_ACTION"],
        "claim_boundary": artifact["claim_boundary"],
    }
    REGISTRY_OUT.write_text(
        json.dumps({
            "schema_version": "uet-equation-registry-addendum-v1",
            "status": "STANDARD_COMPARATOR_NOT_MERGED_AS_UET_EQUATION",
            "extends": "docs/core/artifacts/uet_equation_correspondence_registry.json",
            "equation_entries": [entry],
            "full_core_unlock": False,
            "claim_promotion": False,
        }, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": status,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "conductivity_natural": reference.conductivity_natural,
        "zero_resistive_finite_response": no_resistive.finite_steady_conductivity,
        "inverse_rate_scaling_residual": rate_scaling_residual,
        "quadrature_relative_change": final_resolution_change,
        "energy_scaling_exponent": scale_exponent,
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
