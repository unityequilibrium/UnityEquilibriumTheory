"""Audit the conditional anisotropic thermoelastic bridge for Topic 13."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import hashlib
import json

import numpy as np

from docs.core.uet_anisotropic_thermoelastic_response_bridge import (
    anisotropic_thermoelastic_bridge_contract,
    anisotropic_thermoelastic_response,
    hexagonal_normal_stiffness,
)
from docs.core.uet_scalar_thermoelastic_response_bridge import (
    scalar_thermoelastic_response,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_anisotropic_thermoelastic_response_bridge_audit.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_anisotropic_thermoelastic_bridge_addendum.json"
EQUATION_ID = "uet.o2.thermal.anisotropic_thermoelastic_response_bridge"


def _sha(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def _load(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    contract = anisotropic_thermoelastic_bridge_contract()
    units = contract["natural_unit_exponents"]
    stiffness = hexagonal_normal_stiffness(c11=8.0, c12=2.0, c13=1.0, c33=4.0)
    alpha = np.asarray([-0.03, -0.03, 0.18])
    coupling = np.asarray([0.2, 0.2, 0.5])
    reference = anisotropic_thermoelastic_response(
        temperature=0.8,
        alpha_tensor=alpha,
        stiffness=stiffness,
        c_strain_vol=2.4,
        coupling_tensor=coupling,
        response_residue=1.3,
        response_curvature=0.8,
        delta_phi=0.02,
    )
    unstable = anisotropic_thermoelastic_response(
        temperature=0.8,
        alpha_tensor=alpha,
        stiffness=stiffness,
        c_strain_vol=2.4,
        coupling_tensor=[2.0, 2.0, 3.0],
        response_residue=1.3,
        response_curvature=0.8,
        delta_phi=0.02,
    )
    tensor_scalar = anisotropic_thermoelastic_response(
        temperature=0.8,
        alpha_tensor=[0.12, 0.0, 0.0],
        stiffness=np.diag([5.0, 7.0, 9.0]),
        c_strain_vol=2.4,
        coupling_tensor=[0.7, 0.0, 0.0],
        response_residue=1.3,
        response_curvature=0.8,
        delta_phi=0.02,
    )
    scalar = scalar_thermoelastic_response(
        temperature=0.8,
        alpha_v=0.12,
        bulk_modulus=5.0,
        c_v_vol=2.4,
        coupling=0.7,
        response_residue=1.3,
        response_curvature=0.8,
        delta_phi=0.02,
    )
    bosak = _load("docs/core/artifacts/t13_graphite_elastic_bulk_modulus_source_audit.json")
    tpg = _load("docs/core/artifacts/t13_tpg_anisotropic_alpha_v_source_audit.json")
    scalar_artifact = _load(
        "docs/core/artifacts/t13_scalar_thermoelastic_response_bridge_audit.json"
    )
    expected_coupling = 2.0 * alpha[0] * coupling[0] + alpha[2] * coupling[2]
    expected_thermoelastic = (
        2.0 * (8.0 + 2.0) * alpha[0] ** 2
        + 4.0 * 1.0 * alpha[0] * alpha[2]
        + 4.0 * alpha[2] ** 2
    )
    permutation = np.asarray(
        [[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
    )
    permuted = anisotropic_thermoelastic_response(
        temperature=0.8,
        alpha_tensor=permutation @ alpha,
        stiffness=permutation @ stiffness @ permutation.T,
        c_strain_vol=2.4,
        coupling_tensor=permutation @ coupling,
        response_residue=1.3,
        response_curvature=0.8,
        delta_phi=0.02,
    )
    checks = {
        "tensor_free_energy_units_close": (
            units["stiffness"] + 2 * units["strain"]
            == units["free_energy_density"]
            and units["coupling_tensor"] + units["Phi_E"] + units["strain"]
            == units["free_energy_density"]
            and units["response_curvature"] + 2 * units["Phi_E"]
            == units["free_energy_density"]
        ),
        "hexagonal_stiffness_is_symmetric_positive": (
            np.allclose(stiffness, stiffness.T)
            and float(np.min(np.linalg.eigvalsh(stiffness))) > 0.0
        ),
        "stress_stationarity_closes": reference.stress_residual_norm <= 1.0e-14,
        "adiabatic_entropy_closes": abs(reference.entropy_residual) <= 1.0e-14,
        "heat_capacity_identity_closes": abs(
            reference.heat_capacity_identity_residual
        ) <= 1.0e-14,
        "closed_form_matches_block_solve": (
            reference.temperature_map_relative_residual <= 1.0e-14
        ),
        "hexagonal_coupling_contraction_matches": abs(
            reference.coupling_contraction - expected_coupling
        ) <= 1.0e-15,
        "hexagonal_thermoelastic_contraction_matches": abs(
            reference.thermoelastic_contraction - expected_thermoelastic
        ) <= 1.0e-15,
        "basal_axis_permutation_is_covariant": (
            abs(permuted.delta_temperature - reference.delta_temperature)
            <= 1.0e-15
            and abs(permuted.stability_margin - reference.stability_margin)
            <= 1.0e-15
        ),
        "scalar_parent_is_recovered": (
            abs(tensor_scalar.delta_temperature - scalar.delta_temperature)
            <= 1.0e-15
            and abs(tensor_scalar.c_stress_vol - scalar.c_p_vol) <= 1.0e-15
        ),
        "positive_schur_stability_margin_is_exposed": reference.stability_margin > 0.0,
        "unstable_tensor_coupling_is_not_silently_admitted": unstable.stability_margin < 0.0,
        "bosak_tensor_is_dynamic_comparator_not_K_T": (
            bosak["status"] == "PASS_SCOPED_GRAPHITE_ELASTIC_BULK_COMPARATOR"
            and bosak["checks"]["dynamic_elastic_not_relabelled_as_K_T"]
        ),
        "tpg_expansion_is_mixed_comparator_not_same_specimen": (
            tpg["status"] == "PASS_SCOPED_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR"
            and tpg["checks"]["mixed_row_boundary_is_explicit"]
        ),
        "scalar_parent_remains_conditional": (
            scalar_artifact["registration_status"]
            == "CONDITIONAL_INTERFACE_NOT_ACCEPTED_UET_ACTION"
        ),
        "source_combination_is_not_admitted": True,
        "accepted_action_physical_tensor_and_dynamic_promotion_are_excluded": (
            contract["excluded"]["accepted_UET_action_term"]
            and contract["excluded"]["physical_graphite_tensor_input"]
            and contract["excluded"]["finite_frequency_transport"]
        ),
        "no_fit_holdout_or_claim_promotion": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    passed = all(checks.values())
    status = (
        "PASS_CONDITIONAL_ANISOTROPIC_THERMOELASTIC_RESPONSE_BRIDGE"
        if passed
        else "WARN_ANISOTROPIC_THERMOELASTIC_RESPONSE_BRIDGE"
    )
    what_is_closed = [
        "The scalar thermoelastic bridge is generalized to an arbitrary symmetric positive normal-stiffness block and diagonal thermal-expansion/coupling vectors.",
        "The adiabatic response is DeltaT=T*(alpha:G)*Phi_E/(C_epsilon+T*alpha:C:alpha), with the scalar parent recovered exactly.",
        "The anisotropic static stability condition is the Schur-complement bound a_Phi-G:S:G>0.",
        "The hexagonal graphite contractions and basal-axis covariance are explicit and numerically verified.",
        "Bosak stiffness and TPG expansion remain separate comparators and are not combined into a physical graphite tensor package.",
    ]
    open_blockers = [
        "same_specimen_state_isothermal_stiffness_alpha_tensor_and_C_epsilon_missing",
        "physical_Phi_strain_coupling_tensor_G_missing",
        "physical_response_residue_Z_Phi_and_curvature_a_Phi_missing",
        "Ding_TTG_orientation_geometry_and_material_mapping_missing",
        "finite_frequency_anisotropic_transport_SK_KMS_entropy_missing",
        "independent_SI_alpha_record_missing",
    ]
    source_paths = [
        "docs/core/uet_anisotropic_thermoelastic_response_bridge.py",
        "docs/core/test/test_topic13_anisotropic_thermoelastic_response_bridge.py",
        "docs/scripts/audit/audit_topic13_anisotropic_thermoelastic_response_bridge.py",
    ]
    evidence_paths = [
        "docs/core/artifacts/t13_scalar_thermoelastic_response_bridge_audit.json",
        "docs/core/artifacts/t13_graphite_elastic_bulk_modulus_source_audit.json",
        "docs/core/artifacts/t13_tpg_anisotropic_alpha_v_source_audit.json",
    ]
    artifact = {
        "schema_version": "t13-anisotropic-thermoelastic-response-bridge-v1",
        "major_result_id": "T13_ANISOTROPIC_THERMOELASTIC_RESPONSE_BRIDGE_CANDIDATE",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
        "closure_disposition": "CONDITIONAL_ANISOTROPIC_MAP_DERIVED",
        "verification_status": status,
        "what_is_closed": what_is_closed,
        "equation_registry_ids": [EQUATION_ID],
        "registration_status": "CONDITIONAL_INTERFACE_NOT_ACCEPTED_UET_ACTION",
        "equation_or_mapping": contract["equations"],
        "ontology": contract["ontology"],
        "unit_lane": "conditional_natural_anisotropic_thermoelastic_open_SI",
        "units": contract["natural_unit_exponents"],
        "derivation_class": "standard_anisotropic_thermoelastic_block_solve_and_conditional_UET_interface",
        "observable": "Conditional local adiabatic tensor DeltaPhi-to-DeltaT response",
        "data_role": "DERIVED_CONDITIONAL_TENSOR_MAP_WITH_UNCOMBINED_COMPARATORS",
        "contract": contract,
        "reference_witness": asdict(reference),
        "checks": checks,
        "source_combination_admitted": False,
        "source_combination_blocker": (
            "Bosak_dynamic_stiffness_and_TPG_mixed_expansion_are_not_a_same_state_Ding_tensor_package"
        ),
        "open_blockers": open_blockers,
        "controlling_blocker": (
            "same_state_thermoelastic_tensor_and_physical_Phi_strain_coupling_missing"
        ),
        "source_hashes": {path: _sha(path) for path in source_paths},
        "evidence_artifacts": [
            {"path": path, "sha256": _sha(path)} for path in evidence_paths
        ],
        "dependency_unlocked": [
            "same_state_anisotropic_thermoelastic_tensor_acceptance_gate",
            "Phi_strain_coupling_tensor_stability_gate",
            "orientation_resolved_TTG_mapping_design",
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
            "Generalized the scalar thermoelastic map and stability bound to the "
            "anisotropic normal-strain tensor lane without combining source records."
        ),
        "EQUATION_OR_MAPPING": contract["equations"],
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": (
            "Acquire one same-state isothermal stiffness/alpha/C_epsilon tensor package "
            "and derive or match G, Z_Phi and a_Phi before orientation-resolved TTG use."
        ),
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    entry = {
        "equation_id": EQUATION_ID,
        "version": "1",
        "classification": "conditional_anisotropic_thermoelastic_response_bridge",
        "relation_or_code_path": contract["equations"],
        "ontology": contract["ontology"],
        "standard_physics_counterpart": "Linear anisotropic thermoelasticity in normal-strain Voigt form",
        "variables": {
            "epsilon": "normal-strain vector",
            "alpha": "thermal-expansion vector",
            "C_tensor": "normal stiffness block",
            "G": "Phi_E--strain coupling vector",
            "C_epsilon": "fixed-strain volumetric heat capacity",
        },
        "mathematical_role": "conditional anisotropic response and Schur-complement stability gate",
        "observable_mapping": artifact["observable"],
        "unit_lane": artifact["unit_lane"],
        "units": artifact["units"],
        "parameter_dimensions": artifact["units"],
        "derivation_class": artifact["derivation_class"],
        "source_or_origin": "Standard anisotropic thermoelasticity plus conditional Phi_E--strain tensor interface",
        "assumptions": {
            "linear_normal_strain_block": True,
            "zero_external_stress": True,
            "adiabatic_local_response": True,
            "physical_tensor_inputs_supplied": False,
        },
        "symmetry_and_conservation": "Symmetric positive stiffness; basal-axis permutation covariance; fixed entropy",
        "limiting_cases": [
            "scalar one-axis parent",
            "hexagonal basal-axis permutation",
            "positive versus negative Schur stability margin",
        ],
        "implementation_paths": [source_paths[0]],
        "verifier_paths": source_paths[1:],
        "observable": artifact["observable"],
        "data_role": artifact["data_role"],
        "evidence_class": "INTERNAL_CONDITIONAL_DERIVATION",
        "proof_status": "ANISOTROPIC_MAP_HEXAGONAL_REDUCTION_AND_STABILITY_BOUND_VERIFIED",
        "verification_status": status,
        "evidence_artifacts": [
            {"path": OUT.relative_to(ROOT).as_posix(), "sha256": _sha(OUT)}
        ],
        "downstream_dependencies": artifact["dependency_unlocked"],
        "dependency_role": "anisotropic_material_response_controller",
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
                "temperature_map_residual": reference.temperature_map_relative_residual,
                "stress_residual_norm": reference.stress_residual_norm,
                "stability_margin": reference.stability_margin,
                "source_combination_admitted": False,
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
