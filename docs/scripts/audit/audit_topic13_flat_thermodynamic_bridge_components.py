"""Audit the Topic 13 flat thermodynamic component closure.

This verifier separates the formal EOS/SK/KMS/entropy interfaces from the
physical UET calibration and Kubo requirements.  It accepts the Kim et al.
Green-Kubo record only as a source-locked standard-physics comparator and
never relabels it as a Phi response or a Topic 13 physical coefficient.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_flat_thermodynamic_bridge_components_gate.json"


INPUTS = {
    "normal_component": "docs/core/artifacts/t13_uet_o2_thermodynamic_normal_component_audit.json",
    "formal_bridge": "docs/core/artifacts/t13_formal_thermodynamic_bridge_integration_audit.json",
    "sk_kms_entropy": "docs/core/artifacts/t13_sk_kms_entropy_contract_audit.json",
    "entropy_heat_flux": "docs/core/artifacts/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json",
    "kim_audit": "docs/core/artifacts/t13_kim_2018_graphite_green_kubo_external_input_audit.json",
    "kim_package": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/kim_2018_graphite_green_kubo_source_package.json",
    "holdout": "docs/core/artifacts/t13_xie_2026_holdout_access_audit.json",
}


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def lane_closed(value: dict[str, Any]) -> bool:
    major = value.get("major_result", {})
    return (
        str(value.get("status", "")).startswith("PASS")
        and isinstance(major, dict)
        and major.get("closure_level") == "CLOSED_FOR_LANE"
    )


def evidence(relative: str, value: dict[str, Any], role: str) -> dict[str, Any]:
    major = value.get("major_result", {})
    return {
        "path": relative,
        "sha256": digest(relative),
        "summary": {
            "role": role,
            "status": value.get("status"),
            "major_result_id": major.get("major_result_id") if isinstance(major, dict) else None,
            "closure_level": major.get("closure_level") if isinstance(major, dict) else None,
        },
    }


def all_true(mapping: dict[str, Any], names: tuple[str, ...]) -> bool:
    return all(mapping.get(name) is True for name in names)


def main() -> int:
    artifacts = {name: load(relative) for name, relative in INPUTS.items()}
    normal = artifacts["normal_component"]
    formal = artifacts["formal_bridge"]
    sk = artifacts["sk_kms_entropy"]
    heat = artifacts["entropy_heat_flux"]
    kim = artifacts["kim_audit"]
    kim_package = artifacts["kim_package"]
    holdout = artifacts["holdout"]

    normal_checks = normal.get("checks", {})
    formal_checks = formal.get("checks", {})
    sk_checks = sk.get("checks", {})
    heat_checks = heat.get("checks", {})
    kim_checks = kim.get("checks", {})
    kim_source = kim.get("source", {})
    kim_package_source = kim_package.get("source", {})
    kim_acceptance = kim.get("acceptance", {})
    holdout_audit = holdout.get("audit", {})

    checks = {
        "normal_component_lane_closed": lane_closed(normal)
        and all_true(
            normal_checks,
            (
                "normal_component_is_explicit_on_both_branches",
                "thermodynamic_fields_are_finite",
                "normal_entropy_is_nonnegative",
                "normal_static_response_is_nonnegative",
                "total_state_stability_is_nonnegative",
                "normal_component_is_suppressed_at_lower_temperature",
                "signed_residual_sector_is_not_clipped",
                "normal_equations_are_declared",
                "physical_flow_boundary_is_explicit",
                "natural_unit_boundary_is_explicit",
                "no_fit_target_or_holdout",
            ),
        ),
        "formal_bridge_lane_closed": lane_closed(formal)
        and all_true(
            formal_checks,
            (
                "eos_local_stability",
                "eos_mixed_reciprocity",
                "beta_symbols_remain_separate",
                "kms_noise_witness_nonnegative",
                "onsager_entropy_witness_nonnegative",
                "heat_flux_entropy_production_nonnegative",
                "formal_balance_equation_present",
                "covariant_balance_equation_present",
                "phi_remains_effective_response",
                "c_remains_collective",
                "r_gen_remains_derived",
                "no_physical_kubo_coefficient",
                "no_si_heat_flux",
                "no_alpha_calibration",
                "no_holdout",
            ),
        ),
        "sk_kms_entropy_interface_closed": lane_closed(sk)
        and all_true(
            sk_checks,
            (
                "sk_action_declared",
                "kms_relation_declared",
                "entropy_current_declared",
                "dissipative_balance_declared",
                "beta_symbols_separated",
                "entropy_witness_nonnegative",
                "kms_noise_witness_nonnegative",
                "phi_remains_effective_response",
                "c_remains_collective",
                "trace_is_derived_no_backreaction",
                "physical_coefficient_boundary_explicit",
                "finite_temperature_boundary_explicit",
                "no_target_or_holdout",
            ),
        ),
        "entropy_heat_flux_balance_lane_closed": lane_closed(heat)
        and all_true(
            heat_checks,
            (
                "finite_cutoff_operator_is_symmetric",
                "finite_cutoff_operator_is_positive",
                "heat_response_matrix_is_symmetric",
                "heat_response_matrix_is_positive_semidefinite",
                "landau_heat_flux_is_projected",
                "thermal_force_is_projected",
                "entropy_production_is_nonnegative",
                "kinetic_entropy_matches_covariant_entropy",
                "kinetic_response_equation_is_resolved",
                "charge_balance_is_closed",
                "energy_balance_is_closed",
                "momentum_balance_is_closed",
                "heat_flux_response_is_resolved",
                "local_lorentz_covariance_is_resolved",
                "physical_kubo_is_not_emitted",
                "numeric_alpha_is_not_emitted",
                "no_parameter_fitting",
                "no_target_data",
                "xie_holdout_is_unread",
                "finite_cutoff_boundary_is_declared",
                "Phi_ontology_is_preserved",
                "C_ontology_is_preserved",
                "R_gen_ontology_is_preserved",
                "R_obs_remains_separate",
                "physical_shortcuts_are_excluded",
            ),
        ),
        "curved_3p1_is_explicitly_deferred": (
            "flat/local tensor notation only" in sk.get("major_result", {}).get("equation_or_mapping", {}).get("curved_scope", "")
            and "curved 3+1 solver remains open" in sk.get("major_result", {}).get("equation_or_mapping", {}).get("curved_scope", "")
            and "curved 3+1 result" in heat.get("major_result", {}).get("claim_boundary", "")
        ),
        "external_transport_input_is_provenance_complete": (
            kim.get("status", "").startswith("PASS")
            and kim_acceptance.get("accepted_for_external_transport_input") is True
            and kim_acceptance.get("accepted_for_uet_physical_kubo_coefficient") is False
            and kim_acceptance.get("accepted_for_full_topic13") is False
            and kim_checks.get("coefficient_rows_have_identity_units_uncertainty") is True
            and kim_checks.get("source_hash_matches_payload") is True
            and kim_checks.get("holdout_untouched") is True
            and kim_source.get("source_payload_sha256") == kim_package_source.get("source_payload_sha256")
            and kim_source.get("payload_hash_matches_declared") is True
        ),
        "external_transport_is_not_relabelled_as_uet": (
            kim_checks.get("external_input_not_uet_relabelled") is True
            and kim_checks.get("no_ding_or_alpha_promotion") is True
            and kim_acceptance.get("uet_space_response_state_present") is False
            and kim_acceptance.get("base_Phi_amplitude_present") is False
        ),
        "holdout_remains_unconsumed": (
            holdout.get("status") == "PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY"
            and holdout_audit.get("metadata_only_observed") is True
            and holdout_audit.get("source_data_payload_observed") is False
            and holdout_audit.get("numeric_payload_consumed") is False
            and holdout_audit.get("used_for_fit") is False
            and holdout_audit.get("used_for_tuning") is False
            and holdout_audit.get("used_for_calibration") is False
            and holdout_audit.get("used_for_threshold_adjustment") is False
            and holdout_audit.get("locked_holdout_remains_unconsumed") is True
        ),
        "claim_promotion_remains_disabled": (
            normal.get("claim_promotion", False) is False
            and formal.get("claim_promotion", False) is False
            and sk.get("claim_promotion", False) is False
            and heat.get("claim_promotion", False) is False
            and kim.get("claim_promotion", False) is False
            and holdout_audit.get("claim_promotion") is False
        ),
    }

    status = (
        "PASS_SCOPED_T13_FLAT_COMPONENTS_WITH_EXTERNAL_INPUT"
        if all(checks.values())
        else "FAIL_T13_FLAT_COMPONENT_GATE"
    )
    evidence_artifacts = [
        evidence(INPUTS["normal_component"], normal, "action-derived finite-temperature normal component"),
        evidence(INPUTS["formal_bridge"], formal, "formal cross-module thermodynamic bridge"),
        evidence(INPUTS["sk_kms_entropy"], sk, "formal SK/KMS and entropy interface"),
        evidence(INPUTS["entropy_heat_flux"], heat, "action-derived entropy and heat-flux balance"),
        evidence(INPUTS["kim_audit"], kim, "source-locked external Green-Kubo comparator"),
        evidence(INPUTS["kim_package"], kim_package, "external transport source package"),
        evidence(INPUTS["holdout"], holdout, "locked holdout access audit"),
    ]

    artifact = {
        "schema_version": "t13-flat-thermodynamic-bridge-components-v1",
        "artifact": "t13_flat_thermodynamic_bridge_components_gate",
        "generated_at": date.today().isoformat(),
        "status": status,
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "T13_FLAT_THERMODYNAMIC_BRIDGE_COMPONENTS",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "action-derived finite-temperature normal-sector EOS definitions and stability witnesses on the declared natural-unit O(2) lane",
                "formal cross-module SK/KMS, Onsager, entropy-current, and dissipative-balance interfaces",
                "finite-cutoff covariant heat-flux response and nonnegative entropy-production witness on the declared normal quasiparticle lane",
                "source-locked Kim et al. Green-Kubo directional transport input as a standard-physics external comparator with units, uncertainty, locator, and hash",
                "explicit boundary that curved 3+1 is a later Core result rather than a hidden Topic 13 prerequisite",
            ],
            "what_remains_open": [
                "physical_Kubo_coefficient_record_missing",
                "dimensional_phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "normalized_beta_and_SI_scale_correspondence_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "material_regime_mapping_to_TTG_not_closed",
            ],
            "equation_or_mapping": {
                "normal_eos": "p_n(T,mu,Phi)=p_qp(T,mu,Phi); n_n=partial_mu p_n; s_n=partial_T p_n; epsilon_n=-p_n+T*s_n+mu*n_n",
                "formal_eos": "f_hat=a_C C^2/2+b_C C^4/4+a_Phi(T) Phi^2/2+b_Phi Phi^4/4-g C^2 Phi/2",
                "sk_kms": "S_SK=integral[Phi_a D_R Phi_r+i Phi_a N Phi_a/2]; N(omega)=coth(beta_th*omega/2)*2 Im D_R(omega)",
                "heat_flux": "q^mu=kappa_natural*X_T^mu; J_S^mu=s*u^mu+q^mu/T; sigma=X_T_mu*q^mu>=0",
                "dissipative_balance": "nabla_mu T_matter^(mu nu)=Q^nu; nabla_mu T_UET^(mu nu)=-Q^nu",
                "external_comparator": "KuboCoefficientRecord_external -> directional lattice transport comparator only",
                "physical_bridge_still_open": "Delta_Tq=alpha_Phi_K*Delta_Phi requires an independent Phi/SI anchor",
            },
            "units": {
                "normal_eos": "natural energy/density lane; no SI energy anchor",
                "Phi": "effective response variable; normalized/natural scale only",
                "q_formal": "formal natural-unit moment current; not W m^-2",
                "kappa_formal": "finite-cutoff natural response; not W m^-1 K^-1",
                "kim_external_kappa": "W m^-1 K^-1 with source-reported uncertainty",
                "curved_scope": "flat/local tensor notation; curved 3+1 deferred to Core",
            },
            "derivation_class": "action-derived formal component composition plus source-locked external comparator; no microscopic UET Kubo match",
            "observable": "finite-temperature formal normal response, entropy production, heat-flux interface, and standard directional transport comparator",
            "data_role": "INTERNAL_FORMAL_COMPONENTS_PLUS_EXTERNAL_INPUT_COMPARATOR_NOT_CALIBRATION",
            "evidence_artifacts": evidence_artifacts,
            "verification_status": checks,
            "open_blockers": [
                "physical_Kubo_coefficient_record_missing",
                "dimensional_phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "normalized_beta_and_SI_scale_correspondence_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "material_regime_mapping_to_TTG_not_closed",
            ],
            "dependency_unlocked": "Topic 13 flat formal-component integration and comparator provenance only; no Full Topic 13 Core, curved 3+1, Gravity, or external validation unlock",
            "claim_boundary": "This closes a scoped flat/natural-unit component result. It does not provide a physical UET Kubo coefficient, SI Phi-to-temperature map, alpha_Phi_K, Ding TTG C_src validation, curved 3+1 transport, or Full Topic 13 closure.",
        },
        "equation_or_mapping": {
            "standard": "external Green-Kubo record remains a comparator, not a UET constitutive identity",
            "uet_normalized": "y_TTG^UET=Delta_Phi(t)/Delta_Phi(0)",
            "dimensional": "Delta_Tq=alpha_Phi_K*Delta_Phi remains open",
        },
        "units": {
            "formal_lane": "natural units and normalized response coordinates",
            "external_transport": "W m^-1 K^-1",
            "alpha_Phi_K": "K per normalized Phi; not emitted",
        },
        "verification_status": checks,
        "external_transport_input": {
            "source_id": kim_source.get("source_id"),
            "doi": kim_source.get("doi"),
            "source_payload_sha256": kim_source.get("source_payload_sha256"),
            "payload_hash_matches_declared": kim_source.get("payload_hash_matches_declared"),
            "material_regime_status": kim_source.get("material_regime_status"),
            "accepted_for_external_transport_input": kim_acceptance.get("accepted_for_external_transport_input"),
            "accepted_for_uet_physical_kubo_coefficient": kim_acceptance.get("accepted_for_uet_physical_kubo_coefficient"),
            "accepted_for_full_topic13": kim_acceptance.get("accepted_for_full_topic13"),
            "data_role": "EXTERNAL_INPUT_STANDARD_COMPARATOR_NOT_CALIBRATION",
        },
        "formal_component_status": {
            "eos": "CLOSED_FOR_LANE" if checks["normal_component_lane_closed"] else "OPEN",
            "sk_kms": "CLOSED_FOR_LANE" if checks["sk_kms_entropy_interface_closed"] else "OPEN",
            "entropy_heat_flux": "CLOSED_FOR_LANE" if checks["entropy_heat_flux_balance_lane_closed"] else "OPEN",
            "cross_module_bridge": "CLOSED_FOR_LANE" if checks["formal_bridge_lane_closed"] else "OPEN",
        },
        "physical_coefficient_evidence": "EXTERNAL_INPUT_STANDARD_COMPARATOR_NOT_UET_MAPPING",
        "uet_physical_kubo_record_present": False,
        "external_numeric_transport_input_present": True,
        "uet_numeric_transport_coefficients_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "source_rows_consumed": True,
        "calibration_data_used": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "full_core_unlock": False,
        "controlling_blocker": "physical_Kubo_coefficient_record_missing",
        "next_controller": "Acquire a state-matched UET response-space/Kubo record or a microscopic UET match, then close the independent Phi/SI anchor and alpha_Phi_K without reading Xie 2026.",
        "claim_boundary": "Component closure only. The Kim record is not a UET Phi coefficient, no numeric alpha_Phi_K is emitted, and the locked holdout remains metadata-only.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "closure_level": artifact["major_result"]["closure_level"], "failed_checks": [name for name, value in checks.items() if not value], "artifact": OUT.relative_to(ROOT).as_posix()}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
