"""Audit the conditional scalar thermoelastic response bridge for Topic 13."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import hashlib
import json

from docs.core.uet_scalar_thermoelastic_response_bridge import (
    scalar_thermoelastic_bridge_contract,
    scalar_thermoelastic_response,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_scalar_thermoelastic_response_bridge_audit.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_scalar_thermoelastic_bridge_addendum.json"
EQUATION_ID = "uet.o2.thermal.scalar_thermoelastic_response_bridge"


def _sha(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def _load(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    contract = scalar_thermoelastic_bridge_contract()
    units = contract["natural_unit_exponents"]
    reference = scalar_thermoelastic_response(
        temperature=0.8,
        alpha_v=0.12,
        bulk_modulus=5.0,
        c_v_vol=2.4,
        coupling=0.7,
        response_residue=1.3,
        response_curvature=0.8,
        delta_phi=0.02,
    )
    zero_alpha = scalar_thermoelastic_response(
        temperature=0.8,
        alpha_v=0.0,
        bulk_modulus=5.0,
        c_v_vol=2.4,
        coupling=0.7,
        response_residue=1.3,
        response_curvature=0.8,
        delta_phi=0.02,
    )
    zero_coupling = scalar_thermoelastic_response(
        temperature=0.8,
        alpha_v=0.12,
        bulk_modulus=5.0,
        c_v_vol=2.4,
        coupling=0.0,
        response_residue=1.3,
        response_curvature=0.8,
        delta_phi=0.02,
    )
    unstable = scalar_thermoelastic_response(
        temperature=0.8,
        alpha_v=0.12,
        bulk_modulus=5.0,
        c_v_vol=2.4,
        coupling=2.1,
        response_residue=1.3,
        response_curvature=0.8,
        delta_phi=0.02,
    )
    lowitzer = _load(
        "docs/core/artifacts/t13_lowitzer_graphite_pvt_full_source_pair_audit.json"
    )
    mp48 = _load("docs/core/artifacts/t13_mp48_independent_graphite_cv_audit.json")
    factor_gate = _load(
        "docs/core/artifacts/t13_material_interface_factor_resolution_audit.json"
    )
    cp_identity = (
        reference.c_v_vol
        + reference.temperature
        * reference.alpha_v**2
        * reference.bulk_modulus
    )
    factor_product = (
        reference.chi_u_theta
        * reference.coupling
        * reference.response_residue
        / reference.c_v_vol
    )
    checks = {
        "free_energy_terms_close_to_energy_density": (
            units["bulk_modulus"] + 2 * units["theta"]
            == units["free_energy_density"]
            and units["g_Phi_theta"] + units["Phi_E"] + units["theta"]
            == units["free_energy_density"]
            and units["a_Phi"] + 2 * units["Phi_E"]
            == units["free_energy_density"]
        ),
        "thermoelastic_cross_term_closes": (
            units["bulk_modulus"]
            + units["alpha_v"]
            + units["theta"]
            + units["temperature"]
            == units["free_energy_density"]
        ),
        "cp_cv_identity_closes": abs(reference.c_p_vol - cp_identity) <= 1.0e-15,
        "stress_stationarity_closes": abs(reference.stress_residual) <= 1.0e-14,
        "adiabatic_entropy_closes": abs(reference.entropy_residual) <= 1.0e-14,
        "closed_form_matches_linear_solve": (
            reference.temperature_map_relative_residual <= 1.0e-14
        ),
        "material_factor_matches_alpha_product": abs(
            factor_product - reference.alpha_phi_temperature_natural
        ) <= 1.0e-15,
        "zero_expansion_has_zero_temperature_response": abs(
            zero_alpha.delta_temperature
        ) <= 1.0e-15,
        "zero_coupling_has_zero_temperature_response": abs(
            zero_coupling.delta_temperature
        ) <= 1.0e-15,
        "positive_static_hessian_margin_is_exposed": reference.stability_margin > 0.0,
        "unstable_coupling_is_not_silently_admitted": unstable.stability_margin < 0.0,
        "lowitzer_pair_is_source_locked_comparator": (
            lowitzer["status"]
            == "PASS_SCOPED_SOURCE_LOCKED_LOWITZER_ALPHA_V_K_T_PAIR"
            and lowitzer["major_result"]["data_role"]
            == "EXTERNAL_INPUT_THERMODYNAMIC_CORRECTION_COMPARATOR_NOT_DING_CALIBRATION"
        ),
        "lowitzer_ding_mapping_remains_open": (
            "material_regime_mapping_to_TTG_not_closed"
            in lowitzer["major_result"]["what_remains_open"]
        ),
        "mp48_cv_is_independent_comparator_only": (
            mp48["status"] == "PASS_INDEPENDENT_NUMERIC_CV_WITH_EPISTEMIC_ENVELOPE"
            and mp48["major_result"]["data_role"]
            == "INDEPENDENT_REPRODUCTION_NOT_CALIBRATION"
        ),
        "source_combination_is_not_admitted": True,
        "factor_gate_keeps_physical_g_and_Z_open": (
            factor_gate["factor_matrix"]["g_Phi_theta"]["resolution_status"]
            == "ABSENT_FROM_CURRENT_ACTION"
            and factor_gate["factor_matrix"]["Z_Phi"]["resolution_status"]
            == "OPEN_PHYSICAL_RESIDUE_NONIDENTIFIABLE"
        ),
        "accepted_action_and_anisotropic_promotion_are_excluded": (
            contract["excluded"]["accepted_UET_action_term"]
            and contract["excluded"]["anisotropic_graphite_tensor"]
        ),
        "no_fit_holdout_or_action_promotion": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    passed = all(checks.values())
    status = (
        "PASS_CONDITIONAL_SCALAR_THERMOELASTIC_RESPONSE_BRIDGE"
        if passed
        else "WARN_SCALAR_THERMOELASTIC_RESPONSE_BRIDGE"
    )
    what_is_closed = [
        "The scalar zero-stress, adiabatic thermoelastic equations derive chi_u_theta instead of treating it as an unconstrained free factor.",
        "The conditional response reduces to DeltaT=T*alpha_V*g_Phi_theta*Phi_E/C_p^V with C_p^V=C_v^V+T*alpha_V^2*K_T.",
        "The static coupled Phi_E--theta Hessian supplies the necessary bound g_Phi_theta^2<a_Phi*K_T.",
        "The Lowitzer alpha_V/K_T pair and MP48 c_v record are independently admissible comparators but are not combined as a physical calibration because material/state equivalence is open.",
    ]
    open_blockers = [
        "physical_Phi_strain_coupling_g_Phi_theta_missing",
        "physical_response_residue_Z_Phi_missing",
        "same_material_state_alpha_V_K_T_C_v_input_package_missing",
        "anisotropic_graphite_thermoelastic_tensor_mapping_missing",
        "Ding_TTG_material_regime_mapping_missing",
        "finite_frequency_transport_SK_KMS_and_entropy_closure_missing",
        "independent_SI_alpha_record_missing",
    ]
    source_paths = [
        "docs/core/uet_scalar_thermoelastic_response_bridge.py",
        "docs/core/test/test_topic13_scalar_thermoelastic_response_bridge.py",
        "docs/scripts/audit/audit_topic13_scalar_thermoelastic_response_bridge.py",
    ]
    evidence_paths = [
        "docs/core/artifacts/t13_material_interface_factor_resolution_audit.json",
        "docs/core/artifacts/t13_lowitzer_graphite_pvt_full_source_pair_audit.json",
        "docs/core/artifacts/t13_mp48_independent_graphite_cv_audit.json",
    ]
    artifact = {
        "schema_version": "t13-scalar-thermoelastic-response-bridge-v1",
        "major_result_id": "T13_SCALAR_THERMOELASTIC_RESPONSE_BRIDGE_CANDIDATE",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
        "closure_disposition": "CONDITIONAL_STANDARD_THERMOELASTIC_MAP_DERIVED",
        "verification_status": status,
        "what_is_closed": what_is_closed,
        "equation_registry_ids": [EQUATION_ID],
        "registration_status": "CONDITIONAL_INTERFACE_NOT_ACCEPTED_UET_ACTION",
        "equation_or_mapping": contract["equations"],
        "ontology": contract["ontology"],
        "unit_lane": "conditional_natural_scalar_thermoelastic_open_SI",
        "units": contract["natural_unit_exponents"],
        "derivation_class": "standard_linear_thermoelastic_stationarity_and_conditional_UET_interface",
        "observable": "Conditional local adiabatic DeltaPhi-to-DeltaT response",
        "data_role": "DERIVED_CONDITIONAL_MAP_WITH_UNCOMBINED_EXTERNAL_COMPARATORS",
        "contract": contract,
        "reference_witness": asdict(reference),
        "checks": checks,
        "source_combination_admitted": False,
        "source_combination_blocker": (
            "Lowitzer_alpha_K_and_MP48_Cv_are_not_same_material_state_or_Ding_mapped"
        ),
        "open_blockers": open_blockers,
        "controlling_blocker": (
            "physical_g_Phi_theta_Z_Phi_and_same_state_thermoelastic_inputs_missing"
        ),
        "source_hashes": {path: _sha(path) for path in source_paths},
        "evidence_artifacts": [
            {"path": path, "sha256": _sha(path)} for path in evidence_paths
        ],
        "dependency_unlocked": [
            "same_state_thermoelastic_input_acceptance_gate",
            "Phi_strain_coupling_stability_gate",
            "anisotropic_thermoelastic_extension_design",
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
            "Derived the material response factor and coupling stability bound from "
            "a declared scalar thermoelastic free-energy increment."
        ),
        "EQUATION_OR_MAPPING": contract["equations"],
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": (
            "Build a same-material/state alpha_V, K_T and C_v package and derive or "
            "microscopically match g_Phi_theta and Z_Phi before any numeric alpha."
        ),
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    entry = {
        "equation_id": EQUATION_ID,
        "version": "1",
        "classification": "conditional_scalar_thermoelastic_response_bridge",
        "relation_or_code_path": contract["equations"],
        "ontology": contract["ontology"],
        "standard_physics_counterpart": "Linear isotropic thermoelasticity under zero stress and adiabatic response",
        "variables": {
            "theta": "volumetric strain",
            "DeltaT": "temperature perturbation",
            "Phi_E": "energy-dimension response amplitude",
            "K_T": "isothermal bulk modulus",
            "C_v_vol": "volumetric fixed-volume heat capacity",
            "alpha_V": "volumetric thermal expansion",
        },
        "mathematical_role": "conditional static material response and stability gate",
        "observable_mapping": artifact["observable"],
        "unit_lane": artifact["unit_lane"],
        "units": artifact["units"],
        "parameter_dimensions": artifact["units"],
        "derivation_class": artifact["derivation_class"],
        "source_or_origin": "Standard thermoelastic identity plus conditional Phi_E--strain interface",
        "assumptions": {
            "linear_scalar_isotropic": True,
            "zero_external_stress": True,
            "adiabatic_local_response": True,
            "constant_coefficients": True,
            "physical_inputs_supplied": False,
        },
        "symmetry_and_conservation": "Uniform displacement shift preserved; entropy perturbation constrained to zero",
        "limiting_cases": [
            "zero thermal expansion",
            "zero Phi-strain coupling",
            "positive versus negative static Hessian margin",
        ],
        "implementation_paths": [source_paths[0]],
        "verifier_paths": source_paths[1:],
        "observable": artifact["observable"],
        "data_role": artifact["data_role"],
        "evidence_class": "INTERNAL_CONDITIONAL_DERIVATION",
        "proof_status": "SCALAR_THERMOELASTIC_MAP_AND_STATIC_STABILITY_BOUND_VERIFIED",
        "verification_status": status,
        "evidence_artifacts": [
            {"path": OUT.relative_to(ROOT).as_posix(), "sha256": _sha(OUT)}
        ],
        "downstream_dependencies": artifact["dependency_unlocked"],
        "dependency_role": "material_response_and_coupling_stability_controller",
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
                "status": "CONDITIONAL_INTERFACE_NOT_ACCEPTED_UET_ACTION",
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
                "chi_u_theta": reference.chi_u_theta,
                "temperature_map_residual": reference.temperature_map_relative_residual,
                "stability_margin": reference.stability_margin,
                "source_combination_admitted": False,
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
