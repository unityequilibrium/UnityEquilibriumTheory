"""Check a thermal source-matching route without physical coefficient promotion."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import io
import json
from pathlib import Path
import unittest

import numpy as np

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_matter_strain_susceptibility import canonical_sources, thermal_matching, thermal_moments, isentropic_matched_response
from docs.core.uet_thermoelastic_spatial_compatibility import isotropic_stiffness

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = "docs/core/07_artifacts/topic13/t13_matter_strain_susceptibility_matching_audit.json"
REGISTRY = "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic13_matter_strain_matching_addendum.json"
ID = "uet.o2.thermal.matter_strain_susceptibility_matching"
PUMP = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_experimental_heating_input_source_package.json"
EVIDENCE = ["docs/core/03_lanes/topic13_support/T13_MATTER_STRAIN_SUSCEPTIBILITY_MATCH.md", "docs/core/03_lanes/thermal/uet_matter_strain_susceptibility.py",
            "docs/core/test/test_topic13_matter_strain_susceptibility.py", "docs/scripts/audit/audit_topic13_matter_strain_susceptibility.py",
            "docs/core/02_equations/covariant/uet_covariant_matter.py", "docs/core/02_equations/covariant/uet_covariant_response.py",
            "docs/core/03_lanes/thermal/uet_thermoelastic_spatial_compatibility.py", PUMP]
PROTECTED = ["docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json",
             "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"]


def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def serial(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {key: serial(item) for key, item in value.items()}
    return value


def build():
    protected = {path: digest(path) for path in PROTECTED}
    matter = CovariantMatterConfig(matter_kinetic=1.2, matter_mass_sq=2.7, matter_quartic=.2, response_coupling=.84)
    response = CovariantResponseConfig(epsilon_nc=.5, phi_equilibrium=.1)
    raw = np.array([.48, -.24, .36, 0., 0., 0.])
    sources = canonical_sources(matter, response, raw)
    match = thermal_matching(.8, sources)
    a, b = thermal_moments(.8, sources["mass_squared"], 128), thermal_moments(.8, sources["mass_squared"], 256)
    refinement = max(abs(a[key]-b[key])/abs(b[key]) for key in a)
    bare_k = isotropic_stiffness(5., 3.)
    total_k = bare_k+match["delta_stiffness"]
    total_beta = bare_k@np.array([.04, .04, .04, 0., 0., 0.])+match["delta_thermal_stress"]
    total_c = 2.4+match["delta_heat_capacity"]
    witness = isentropic_matched_response(stiffness=total_k, thermal_stress=total_beta, coupling=match["G"],
                                          entropy_phi_coefficient=match["entropy_phi_coefficient"], temperature=.8,
                                          heat_capacity=total_c, direction=[1., 0., 0.], delta_phi=.026)
    schur = .8+match["delta_phi_curvature"]-match["G"]@np.linalg.solve(total_k, match["G"])
    zero_d = thermal_matching(.8, dict(sources, deformation=np.zeros(6)))
    run = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromName(
        "docs.core.test.test_topic13_matter_strain_susceptibility"))
    pump = json.loads((ROOT/PUMP).read_text(encoding="utf-8-sig"))
    checks = {
        "action_and_independent_derivative_suite": run.wasSuccessful() and run.testsRun >= 12,
        "semi_infinite_quadrature_refinement": refinement < 1e-8,
        "thermal_mass_susceptibility_is_negative": match["moments"]["mass_second_derivative"] < 0,
        "mixed_phi_strain_hessian_is_reciprocal": np.array_equal(match["phi_strain_hessian"], match["phi_strain_hessian"].T),
        "loop_static_hessian_is_rank_one_softening": np.linalg.matrix_rank(match["phi_strain_hessian"], tol=1e-12) == 1 and np.max(np.linalg.eigvalsh(match["phi_strain_hessian"])) < 1e-12,
        "zero_D_removes_G_but_not_direct_entropy": np.linalg.norm(zero_d["G"]) == 0 and zero_d["entropy_phi_coefficient"] > 0,
        "declared_total_synthetic_schur_positive": schur > 0,
        "complete_isentropic_entropy_and_force_balance": abs(witness["entropy_residual"]) < 1e-12 and witness["mechanical_residual"] < 1e-12,
        "block_solution_matches_complete_gain": abs(witness["delta_temperature"]-witness["gain"]*.026) < 1e-12,
        "full_topic_closure_files_unchanged": protected == {path: digest(path) for path in PROTECTED},
    }
    checks = {key: bool(value) for key, value in checks.items()}
    passed = all(checks.values())
    result = {
        "schema_version": "t13-matter-strain-susceptibility-matching-v1", "major_result_id": "T13_THERMAL_MATTER_STRAIN_AND_ENTROPY_MATCHING",
        "topic": "0.13_Thermodynamic_Bridge", "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
        "verification_status": "PASS_CONDITIONAL_THERMAL_SOURCE_MATCHING" if passed else "FAIL_THERMAL_SOURCE_MATCHING",
        "what_is_closed": ["Canonical mass-source normalization matches the existing O(2) action plus a declared external strain deformation.",
                           "Finite thermal matter determinant derives G, direct entropy coefficient r and all companion Hessian increments.",
                           "Independent derivatives and reciprocity show that keeping G alone is not the complete matching of this route."] if passed else [],
        "equation_registry_ids": [ID],
        "equation_or_mapping": {"mass_source": "x=(m_raw^2-epsilon_nc*h*delta_phi+D_raw:eps)/A_chi=x0-eta*delta_phi+D:eps",
                                "thermal_free_energy": "F_th=2*T*integral dp*p^2/(2*pi^2)*log(1-exp(-sqrt(p^2+x)/T))",
                                "coupling": "G=-eta*D*F_xx; r=eta*F_xT",
                                "companion_terms": "delta_K=D*D^T*F_xx; delta_a=eta^2*F_xx; delta_beta=-D*F_xT; delta_c=-T*F_TT",
                                "entropy": "ds=beta:eps+c*dT/T+r*delta_phi",
                                "isentropic_map": "dT/delta_phi=T*(b^T*A^-1*h-r)/(c+T*b^T*A^-1*b)"},
        "ontology": {"Phi": "original response displacement; not temperature", "chi": "canonical O(2) matter doublet, not identified with graphite phonons",
                     "strain": "external material mass-source probe", "C": "unchanged collective coordinate", "R_gen_R_obs": "excluded from state"},
        "units": {"T_phi_eta": "E", "x_D": "E^2", "F": "E^4", "F_x": "E^2", "F_xx": "1", "F_xT": "E", "G": "E^3", "r": "E^2", "c": "E^3"},
        "unit_lane": "natural_thermal_increment_not_SI", "derivation_class": "Gaussian_thermal_source_matching_with_external_deformation_ansatz",
        "observable": "thermal increments to mixed response/strain/entropy coefficients", "data_role": "SYNTHETIC_INTERNAL_MATCHING_NO_CALIBRATION",
        "synthetic_inputs": {"matter": asdict(matter), "response": asdict(response), "D_raw": raw.tolist(), "canonical_sources": serial(sources),
                             "temperature": .8, "orders": [128, 160, 256], "bare_material_K": bare_k.tolist(), "bare_c": 2.4, "bare_phi_curvature": .8,
                             "bare_expansion": [.04, .04, .04, 0., 0., 0.], "direction": [1., 0., 0.], "delta_phi": .026},
        "thermal_matching": serial(match), "synthetic_complete_response": serial(witness),
        "total_fixed_T_schur_margin": float(schur), "max_relative_quadrature_change": refinement,
        "pump_source_context_not_computational_input": {"path": PUMP, "status": pump["status"],
                                                       "absorbed_energy_status": pump["energy_density_contract"]["absorbed_energy_density"]["status"],
                                                       "role": "incident setup does not identify material D, Z or pump-to-Phi initialization"},
        "checks": checks, "test_count": run.testsRun,
        "evidence_artifacts": [{"path": path, "sha256": digest(path)} for path in EVIDENCE], "protected_full_closure_hashes": protected,
        "input_policy": "No experimental curve or holdout is a computational input. Ding setup metadata is context only. No fit, Landauer substitution or threshold change.",
        "open_blockers": ["physical_UET_matter_to_material_excitation_identification_missing", "independent_deformation_potential_D_and_Phi_Z_missing",
                          "vacuum_subtraction_and_no_double_counting_material_match_missing", "complete_G_r_reciprocal_dynamic_and_pump_initialization_missing"],
        "controlling_blocker": "physical_material_mass_source_and_vacuum_matching_missing",
        "dependency_unlocked": "conditional joint G/r dynamic matching design only", "physical_dependency_unlock": False,
        "full_core_unlock": False, "claim_promotion": False,
        "claim_boundary": "Thermal Gaussian increment under an external mass-source ansatz only. Not physical graphite G or alpha, accepted UET action extension, pump calibration, vacuum/interaction closure, transport or Full Topic 13.",
    }
    return result


def main():
    result = build()
    (ROOT/OUTPUT).write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    entry = {key: result[key] for key in ("ontology", "units", "unit_lane", "derivation_class", "observable", "data_role",
                                         "verification_status", "controlling_blocker", "claim_boundary", "physical_dependency_unlock")}
    entry.update(equation_id=ID, version="1", classification="conditional_external_source_matching",
                 relation_or_code_path=result["equation_or_mapping"], standard_physics_counterpart="Gaussian thermal free-energy source derivatives",
                 variables=result["ontology"], mathematical_role="reciprocal mixed susceptibility and complete Hessian matching",
                 observable_mapping=result["observable"], parameter_dimensions=result["units"], source_or_origin="existing matter coupling plus declared external strain-mass deformation",
                 assumptions=["normal chi=0", "mu=0", "positive mass squared", "fixed integration measure", "thermal Gaussian increment only"],
                 symmetry_and_conservation="symmetric source Hessian; thermodynamic Maxwell reciprocity; state meanings unchanged",
                 limiting_cases=["eta=0", "D=0 retains r", "matter-field reparameterization", "natural-unit scaling"],
                 implementation_paths=[EVIDENCE[1]], verifier_paths=[EVIDENCE[2], EVIDENCE[3]],
                 evidence_class="INTERNAL_CONDITIONAL_THERMAL_DERIVATION", proof_status="analytic source differentiation with independent numerical checks; physical matching open",
                 evidence_artifacts=[{"path": OUTPUT, "sha256": digest(OUTPUT)}], downstream_dependencies=["joint_G_r_dynamic_interface"],
                 dependency_role="conditional_material_matching", failure_mode=result["open_blockers"],
                 next_hardening_step="identify physical mass-deformation source and carry G/r together without double counting")
    registry = {"schema_version": "uet-equation-registry-addendum-v1", "status": "CONDITIONAL_EXTERNAL_SOURCE_NOT_ACCEPTED_UET_ACTION",
                "extends": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json", "equation_entries": [entry], "full_core_unlock": False, "claim_promotion": False}
    (ROOT/REGISTRY).write_text(json.dumps(registry, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(result["verification_status"])
    print("G="+str(result["thermal_matching"]["G"])+"; r="+str(result["thermal_matching"]["entropy_phi_coefficient"]))
    print("complete_gain="+str(result["synthetic_complete_response"]["gain"])+"; strain_only_gain="+str(result["synthetic_complete_response"]["strain_only_gain"]))
    return 0 if all(result["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
