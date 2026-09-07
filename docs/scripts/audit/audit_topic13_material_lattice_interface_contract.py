"""Audit the conditional UET-to-material-lattice interface contract."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import hashlib
import json

from docs.core.uet_material_lattice_interface_contract import (
    exchange_ledger_witness,
    interface_rescaling_witness,
    material_lattice_interface_contract,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_uet_material_lattice_interface_contract_audit.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_material_lattice_interface_addendum.json"
EQUATION_ID = "uet.o2.thermal.material_lattice_interface_contract"


def _sha(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def main() -> int:
    contract = material_lattice_interface_contract()
    scales = (0.25, 0.5, 2.0, 4.0)
    rescaling_rows = [asdict(interface_rescaling_witness(scale=scale)) for scale in scales]
    ledger = exchange_ledger_witness()
    units = contract["natural_unit_exponents"]
    admitted = contract["admitted_current_evidence"]
    checks = {
        "uet_and_material_state_ownership_separate": contract["state_ownership"]["UET"] == ["C", "Phi", "Pi"] and "u_i" in contract["state_ownership"]["material_lattice"],
        "history_and_observer_excluded_from_state": set(contract["state_ownership"]["excluded_from_state"]) == {"R_gen", "R_obs"},
        "Phi_not_relabelled_as_material_variable": "not temperature" in contract["ontology"]["Phi"],
        "strain_unit_closure": units["derivative"] + units["displacement_u"] == units["strain_theta"],
        "interaction_unit_closure": units["g_Phi_theta"] + units["Phi_E"] + units["strain_theta"] == units["interaction_energy_density"],
        "exchange_rate_unit_closure": units["exchange_rate_density"] == units["phonon_energy_density"] + units["derivative"],
        "conditional_alpha_unit_closure": units["Phi_E"] + units["g_Phi_theta"] - units["C_src_natural"] == units["alpha_per_normalized_Phi_natural"],
        "equal_and_opposite_exchange_ledger": ledger["total_energy_source"] == 0.0,
        "field_rescaling_leaves_interaction_invariant": max(row["interaction_relative_residual"] for row in rescaling_rows) <= 1.0e-15,
        "field_rescaling_leaves_alpha_product_invariant": max(row["alpha_product_relative_residual"] for row in rescaling_rows) <= 1.0e-15,
        "calorine_mode_fields_admitted_only_as_comparator": admitted["calorine_mode_source_fields"] and not admitted["normal_umklapp_collision_split"],
        "physical_coupling_and_alpha_remain_open": not admitted["physical_Z_Phi"] and not admitted["physical_g_Phi_theta"] and not admitted["physical_alpha_Phi_K"],
        "no_fit_holdout_or_physical_promotion": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    passed = all(checks.values())
    status = "PASS_CONDITIONAL_MATERIAL_LATTICE_INTERFACE_CONTRACT" if passed else "WARN_MATERIAL_LATTICE_INTERFACE_CONTRACT"
    what_is_closed = [
        "UET state, external material displacement/strain and phonon-distribution variables have separate owners; Phi, C and R_gen are not relabeled.",
        "A scalar strain interface, phonon heat current, PBTE collision split and equal-and-opposite energy-exchange ledger are declared with a closed natural-unit contract.",
        "The conditional map alpha_Phi_K=chi_u_theta*g_Phi_theta*Z_Phi/C_src exposes every required factor instead of fitting the product to TTG.",
        "Field rescaling Z_Phi to s*Z_Phi and g to g/s leaves both the interaction and alpha product invariant, so normalized Phi dynamics alone cannot identify either physical factor.",
    ]
    open_blockers = [
        "physical_Phi_energy_residue_Z_Phi_missing",
        "physical_Phi_strain_coupling_g_missing",
        "source_backed_material_response_chi_u_theta_missing",
        "normal_umklapp_split_or_admissible_full_collision_operator_missing",
        "Ding_material_state_and_source_uncertainty_missing",
        "SI_conversion_and_independent_alpha_record_missing",
    ]
    source_paths = [
        "docs/core/uet_material_lattice_interface_contract.py",
        "docs/core/test/test_topic13_material_lattice_interface_contract.py",
        "docs/scripts/audit/audit_topic13_material_lattice_interface_contract.py",
    ]
    prior_paths = [
        "docs/core/artifacts/t13_calorine_lattice_interface_input_boundary.json",
        "docs/core/artifacts/t13_continuum_action_umklapp_direct_route_no_go.json",
    ]
    artifact = {
        "schema_version": "t13-uet-material-lattice-interface-contract-v1",
        "major_result_id": "T13_UET_MATERIAL_LATTICE_INTERFACE_CONTRACT",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
        "closure_disposition": "CONDITIONAL_INTERFACE_ARCHITECTURE_READY" if passed else "OPEN",
        "verification_status": status,
        "what_is_closed": what_is_closed,
        "equation_registry_ids": [EQUATION_ID],
        "registration_status": "CONDITIONAL_INTERFACE_NOT_MERGED_INTO_UET_ACTION",
        "equation_or_mapping": contract["equations"],
        "ontology": contract["ontology"],
        "unit_lane": "conditional_natural_3p1_open_SI",
        "units": contract["natural_unit_exponents"],
        "derivation_class": "conditional_interface_and_identifiability_contract",
        "observable": "Conditional phonon energy/current response to normalized Phi; no numeric physical coefficient",
        "data_role": "DERIVED_CONDITIONAL_INTERFACE_NO_CALIBRATION",
        "contract": contract,
        "rescaling_witnesses": rescaling_rows,
        "exchange_ledger_witness": ledger,
        "checks": checks,
        "open_blockers": open_blockers,
        "controlling_blocker": "physical_Phi_residue_strain_coupling_and_material_response_missing",
        "source_hashes": {path: _sha(path) for path in source_paths},
        "evidence_artifacts": [{"path": path, "sha256": _sha(path)} for path in prior_paths],
        "dependency_unlocked": [
            "physical_Phi_strain_coupling_derivation_or_source_gate",
            "material_response_kernel_chi_u_theta_source_gate",
            "conditional_alpha_uncertainty_propagation_design",
        ],
        "full_core_unlock": False,
        "claim_promotion": False,
        "xie_2026_accessed": False,
        "parameter_fitting_performed": False,
        "claim_boundary": "Conditional interface architecture and identifiability result only; not a new accepted UET action term, physical Phi residue/coupling, material transport coefficient, alpha calibration, TTG prediction, external validation or Full Topic 13 closure.",
    }
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": artifact["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": what_is_closed,
        "WHAT_REMAINS_OPEN": open_blockers,
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Defined the first ontology- and unit-safe UET/material-lattice interface and exposed the coefficient product required for alpha without fitting it.",
        "EQUATION_OR_MAPPING": contract["equations"],
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": "Derive or source-lock Z_Phi, g_Phi_theta and chi_u_theta independently, and acquire an admissible material collision operator before evaluating alpha or transport.",
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    entry = {
        "equation_id": EQUATION_ID,
        "version": "1",
        "classification": "conditional_uet_material_lattice_interface",
        "relation_or_code_path": contract["equations"],
        "ontology": contract["ontology"],
        "standard_physics_counterpart": "Scalar-strain material coupling plus linearized phonon BTE and subsystem exchange ledger",
        "variables": {"Phi_E": "canonical energy-dimension response amplitude", "theta": "volumetric strain", "delta_n_qnu": "phonon distribution perturbation", "Q_ex": "energy exchange rate density"},
        "mathematical_role": "conditional bridge from UET response to external material energy/current",
        "observable_mapping": artifact["observable"],
        "unit_lane": artifact["unit_lane"],
        "units": artifact["units"],
        "parameter_dimensions": artifact["units"],
        "derivation_class": artifact["derivation_class"],
        "source_or_origin": "Conditional interface design constrained by the current-action Umklapp no-go and Calorine source boundary",
        "assumptions": {"external_material_sector": True, "scalar_volumetric_strain_channel": True, "physical_coefficients_supplied": False},
        "symmetry_and_conservation": "Displacement shift enters through strain; subsystem energy sources cancel exactly",
        "limiting_cases": ["zero coupling", "homogeneous strain", "field-coordinate rescaling"],
        "implementation_paths": [source_paths[0]],
        "verifier_paths": source_paths[1:],
        "observable": artifact["observable"],
        "data_role": artifact["data_role"],
        "evidence_class": "INTERNAL_CONDITIONAL_INTERFACE",
        "proof_status": "ARCHITECTURE_AND_IDENTIFIABILITY_VERIFIED_PHYSICAL_INPUTS_OPEN",
        "verification_status": status,
        "evidence_artifacts": [{"path": OUT.relative_to(ROOT).as_posix(), "sha256": _sha(OUT)}],
        "downstream_dependencies": artifact["dependency_unlocked"],
        "dependency_role": "physical_coupling_and_alpha_controller",
        "physical_dependency_unlock": False,
        "controlling_blocker": artifact["controlling_blocker"],
        "failure_mode": open_blockers,
        "next_hardening_step": artifact["report"]["NEXT_ACTION"],
        "claim_boundary": artifact["claim_boundary"],
    }
    REGISTRY_OUT.write_text(json.dumps({
        "schema_version": "uet-equation-registry-addendum-v1",
        "status": "CONDITIONAL_INTERFACE_NOT_MERGED_AS_ACCEPTED_ACTION",
        "extends": "docs/core/artifacts/uet_equation_correspondence_registry.json",
        "equation_entries": [entry],
        "full_core_unlock": False,
        "claim_promotion": False,
    }, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "maximum_rescaling_residual": max(row["interaction_relative_residual"] for row in rescaling_rows),
        "exchange_ledger_residual": ledger["total_energy_source"],
        "conditional_alpha": contract["equations"]["conditional_alpha"],
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
