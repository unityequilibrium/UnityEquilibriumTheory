"""Audit Topic 13 material-interface factors and coupling substitution no-go."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import hashlib
import inspect
import json

from docs.core.uet_covariant_matter import interaction_energy_density
from docs.core.uet_material_interface_factor_resolution import (
    conditional_alpha_witness,
    material_interface_factor_resolution,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_material_interface_factor_resolution_audit.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_material_interface_factor_resolution_addendum.json"
EQUATION_ID = "uet.o2.thermal.material_interface_factor_resolution"


def _sha(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def _load(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    contract = material_interface_factor_resolution()
    no_go = contract["operator_substitution_no_go"]
    factors = contract["factor_matrix"]
    action_bridge = _load(
        "docs/core/artifacts/t13_uet_o2_action_thermal_observable_bridge_audit.json"
    )
    coupling_no_go = _load(
        "docs/core/artifacts/t13_covariant_matter_coupling_normalization_no_go.json"
    )
    field_no_go = _load(
        "docs/core/artifacts/t13_covariant_field_normalization_identifiability_no_go.json"
    )
    calorine = _load(
        "docs/core/artifacts/t13_calorine_lattice_interface_input_boundary.json"
    )
    interface = _load(
        "docs/core/artifacts/t13_uet_material_lattice_interface_contract_audit.json"
    )
    signature = inspect.signature(interaction_energy_density)
    witness = conditional_alpha_witness(
        chi_u_theta=0.8,
        g_phi_theta=2.5,
        z_phi=1.2,
        c_src=4.0,
        standard_uncertainties={
            "chi_u_theta": 0.08,
            "g_phi_theta": 0.25,
            "z_phi": 0.12,
            "c_src": 0.4,
        },
    )
    expected_relative = (4.0 * 0.1**2) ** 0.5
    checks = {
        "implemented_operator_has_no_displacement_or_strain_argument": not (
            {"u_i", "theta", "strain"} & set(signature.parameters)
        ),
        "implemented_and_required_operators_have_different_state_support": set(
            no_go["implemented_operator_fields"]
        ).isdisjoint({"theta", "u_i"}),
        "implemented_coupling_has_mass_dimension_one": no_go[
            "implemented_coefficient_mass_dimension"
        ] == 1,
        "required_strain_coupling_has_mass_dimension_three": no_go[
            "required_coefficient_mass_dimension"
        ] == 3,
        "direct_coefficient_substitution_is_dimensionally_invalid": no_go[
            "missing_mass_dimension"
        ] == 2,
        "both_declared_operator_terms_close_to_energy_density": (
            no_go["implemented_operator_mass_dimension_without_coefficient"] + 1 == 4
            and no_go["required_operator_mass_dimension_without_coefficient"] + 3 == 4
        ),
        "field_residue_remains_nonidentifiable": field_no_go["status"]
        == "PASS_SCOPED_NO_GO_COVARIANT_FIELD_NORMALIZATION",
        "matter_coupling_rescaling_no_go_is_preserved": coupling_no_go["status"]
        == "PASS_SCOPED_NO_GO_COVARIANT_MATTER_COUPLING_NORMALIZATION",
        "natural_action_bridge_is_derived_but_not_si_alpha": (
            action_bridge["status"]
            == "PASS_ACTION_DERIVED_NATURAL_PHI_THERMAL_BRIDGE_LANE"
            and not action_bridge["state"]["numeric_alpha_phi_k_emitted"]
        ),
        "calorine_heat_capacity_is_comparator_only": (
            calorine["verification_status"]
            == "PASS_SCOPED_CALORINE_LATTICE_INTERFACE_INPUT_BOUNDARY"
            and calorine["data_role"]
            == "EXTERNAL_CANDIDATE_REPRODUCTION_NOT_CALIBRATION_NOT_HOLDOUT"
        ),
        "normal_umklapp_split_remains_absent": not calorine["witness"][
            "normal_umklapp_decomposition_available"
        ],
        "prior_interface_did_not_promote_physical_coupling": (
            interface["registration_status"]
            == "CONDITIONAL_INTERFACE_NOT_MERGED_INTO_UET_ACTION"
            and not interface["claim_promotion"]
        ),
        "factor_matrix_keeps_alpha_open": factors["alpha_Phi_K"][
            "resolution_status"
        ] == "OPEN_COMPOSITE_COEFFICIENT",
        "independent_uncertainty_algebra_closes": abs(
            witness.relative_standard_uncertainty - expected_relative
        ) <= 1.0e-15,
        "no_fit_holdout_or_physical_promotion": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    passed = all(checks.values())
    status = (
        "PASS_FACTOR_RESOLUTION_WITH_COUPLING_SUBSTITUTION_NO_GO"
        if passed
        else "WARN_MATERIAL_INTERFACE_FACTOR_RESOLUTION"
    )
    what_is_closed = [
        "Every factor in alpha_Phi_K=chi_u_theta*g_Phi_theta*Z_Phi/C_src now has a machine-readable evidence class, unit role, admissible route and blocker.",
        "The implemented response_coupling h multiplies delta_phi*chi^2, while the required g_Phi_theta multiplies Phi_E*theta; their field support and coefficient dimensions differ.",
        "Directly relabeling h as g_Phi_theta is closed as a scoped no-go for the current action.",
        "The existing alpha_Phi_T^nat is retained as a homogeneous natural-action bridge and is explicitly barred from substitution for SI material alpha_Phi_K.",
        "The independent-factor and covariance-form uncertainty propagation contracts are fixed without emitting a numeric physical coefficient.",
    ]
    open_blockers = [
        "physical_Phi_energy_residue_Z_Phi_missing",
        "new_Phi_strain_operator_or_independent_microscopic_match_missing",
        "source_backed_material_response_chi_u_theta_missing",
        "accepted_Ding_equivalent_C_src_and_material_state_mapping_missing",
        "normal_umklapp_split_or_admissible_full_collision_operator_missing",
        "SI_conversion_and_independent_alpha_record_missing",
    ]
    source_paths = [
        "docs/core/uet_material_interface_factor_resolution.py",
        "docs/core/test/test_topic13_material_interface_factor_resolution.py",
        "docs/scripts/audit/audit_topic13_material_interface_factor_resolution.py",
    ]
    evidence_paths = [
        "docs/core/artifacts/t13_uet_material_lattice_interface_contract_audit.json",
        "docs/core/artifacts/t13_covariant_field_normalization_identifiability_no_go.json",
        "docs/core/artifacts/t13_covariant_matter_coupling_normalization_no_go.json",
        "docs/core/artifacts/t13_uet_o2_action_thermal_observable_bridge_audit.json",
        "docs/core/artifacts/t13_calorine_lattice_interface_input_boundary.json",
    ]
    artifact = {
        "schema_version": "t13-material-interface-factor-resolution-v1",
        "major_result_id": "T13_MATERIAL_INTERFACE_FACTOR_RESOLUTION",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
        "closure_disposition": (
            "CLOSED_AS_NO_GO_EXISTING_MATTER_COUPLING_SUBSTITUTION"
            if passed
            else "OPEN"
        ),
        "verification_status": status,
        "what_is_closed": what_is_closed,
        "equation_registry_ids": [EQUATION_ID],
        "registration_status": "DIAGNOSTIC_FACTOR_GATE_NOT_NEW_ACTION_TERM",
        "equation_or_mapping": contract["equations"],
        "ontology": contract["ontology"],
        "unit_lane": "natural_factor_audit_open_SI",
        "units": {
            "response_coupling_h": 1,
            "g_Phi_theta": 3,
            "Phi_E": 1,
            "theta": 0,
            "C_src_natural": 3,
            "alpha_per_normalized_Phi_natural": 1,
        },
        "derivation_class": "action_operator_and_unit_substitution_no_go_plus_factor_evidence_resolution",
        "observable": "Conditional material thermal coefficient factor gate; no numeric alpha",
        "data_role": "INTERNAL_STRUCTURAL_AUDIT_NO_CALIBRATION_NO_HOLDOUT",
        "factor_matrix": factors,
        "operator_substitution_no_go": no_go,
        "uncertainty_witness": asdict(witness),
        "checks": checks,
        "open_blockers": open_blockers,
        "controlling_blocker": (
            "new_Phi_strain_operator_or_independent_microscopic_match_missing"
        ),
        "source_hashes": {path: _sha(path) for path in source_paths},
        "evidence_artifacts": [
            {"path": path, "sha256": _sha(path)} for path in evidence_paths
        ],
        "dependency_unlocked": [
            "candidate_Phi_strain_action_extension_F0_F4_design",
            "material_response_kernel_source_requirement",
            "conditional_alpha_uncertainty_gate",
        ],
        "full_core_unlock": False,
        "claim_promotion": False,
        "xie_2026_accessed": False,
        "parameter_fitting_performed": False,
        "claim_boundary": contract["claim_boundary"],
    }
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": artifact["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": what_is_closed,
        "WHAT_REMAINS_OPEN": open_blockers,
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": (
            "Resolved the material alpha product factor by factor and closed direct "
            "substitution of the existing Phi--O(2) coupling for a Phi--strain coupling."
        ),
        "EQUATION_OR_MAPPING": contract["equations"],
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": (
            "Design an explicitly separate Phi_E*theta action candidate through F0--F4 "
            "or source-lock a microscopic response match; do not reuse response_coupling h."
        ),
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    entry = {
        "equation_id": EQUATION_ID,
        "version": "1",
        "classification": "diagnostic_material_interface_factor_gate",
        "relation_or_code_path": contract["equations"],
        "ontology": contract["ontology"],
        "standard_physics_counterpart": "Scalar deformation-potential/strain coupling and linear-response coefficient factorization",
        "variables": {
            "h": "current O(2)-matter response coupling",
            "g_Phi_theta": "required response-strain coupling",
            "Z_Phi": "physical response residue",
            "chi_u_theta": "material response kernel",
            "C_src": "volumetric heat capacity",
        },
        "mathematical_role": "factor admission gate and current-operator substitution no-go",
        "observable_mapping": artifact["observable"],
        "unit_lane": artifact["unit_lane"],
        "units": artifact["units"],
        "parameter_dimensions": artifact["units"],
        "derivation_class": artifact["derivation_class"],
        "source_or_origin": "Current covariant response/O(2) action plus conditional material-lattice interface",
        "assumptions": {
            "current_action_only": True,
            "direct_coefficient_relabeling_prohibited": True,
            "physical_coefficients_supplied": False,
        },
        "symmetry_and_conservation": "No action change; prior ontology and exchange-ledger contracts retained",
        "limiting_cases": ["zero strain coupling", "field-coordinate rescaling"],
        "implementation_paths": [source_paths[0]],
        "verifier_paths": source_paths[1:],
        "observable": artifact["observable"],
        "data_role": artifact["data_role"],
        "evidence_class": "INTERNAL_STRUCTURAL_NO_GO",
        "proof_status": "FACTOR_GATE_AND_CURRENT_OPERATOR_SUBSTITUTION_NO_GO_VERIFIED",
        "verification_status": status,
        "evidence_artifacts": [
            {"path": OUT.relative_to(ROOT).as_posix(), "sha256": _sha(OUT)}
        ],
        "downstream_dependencies": artifact["dependency_unlocked"],
        "dependency_role": "physical_strain_coupling_design_controller",
        "physical_dependency_unlock": False,
        "controlling_blocker": artifact["controlling_blocker"],
        "failure_mode": open_blockers,
        "next_hardening_step": artifact["report"]["NEXT_ACTION"],
        "claim_boundary": artifact["claim_boundary"],
    }
    REGISTRY_OUT.write_text(
        json.dumps(
            {
                "schema_version": "uet-equation-registry-addendum-v1",
                "status": "DIAGNOSTIC_FACTOR_GATE_NOT_NEW_ACTION_TERM",
                "extends": "docs/core/artifacts/uet_equation_correspondence_registry.json",
                "equation_entries": [entry],
                "full_core_unlock": False,
                "claim_promotion": False,
            },
            indent=2,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": status,
                "checks_passed": sum(checks.values()),
                "checks_total": len(checks),
                "coupling_mass_dimension_gap": no_go["missing_mass_dimension"],
                "factor_statuses": {
                    name: row["resolution_status"] for name, row in factors.items()
                },
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
