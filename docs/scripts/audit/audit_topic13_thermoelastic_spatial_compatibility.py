"""Generate a conditional finite-q material result, never a full-topic unlock."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_thermoelastic_spatial_compatibility import (
    isotropic_stiffness, spatial_response,
)
ARTIFACT = "docs/core/artifacts/t13_thermoelastic_spatial_compatibility_audit.json"
REGISTRY = "docs/core/artifacts/uet_equation_correspondence_registry_topic13_spatial_compatibility_addendum.json"
EQUATION_ID = "uet.o2.thermal.thermoelastic_spatial_compatibility"
PROTECTED = [
    "docs/core/artifacts/t13_topic13_closure_matrix.json",
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json",
]
EVIDENCE = [
    "docs/core/T13_THERMOELASTIC_SPATIAL_COMPATIBILITY.md",
    "docs/core/uet_thermoelastic_spatial_compatibility.py",
    "docs/core/test/test_topic13_thermoelastic_spatial_compatibility.py",
    "docs/scripts/audit/audit_topic13_thermoelastic_spatial_compatibility.py",
    "docs/core/artifacts/t13_anisotropic_thermoelastic_response_bridge_audit.json",
]


def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def build():
    before = {path: digest(path) for path in PROTECTED}
    p = dict(stiffness=isotropic_stiffness(5., 3.), expansion=[.04, .04, .04, 0., 0., 0.],
             coupling=[.7, .7, .7, 0., 0., 0.], direction=[1., 0., 0.],
             temperature=.8, heat_capacity=2.4, phi_response=.026, response_curvature=.8)
    ref = spatial_response(**p)
    analytic = .8*5*.12*.7/((5+4*3/3)*2.4+.8*25*.12**2)
    khex = np.diag([8., 8., 4., 3., 3., 6.])
    khex[0, 1] = khex[1, 0] = 2.
    khex[0, 2] = khex[2, 0] = khex[1, 2] = khex[2, 1] = 1.
    hexp = dict(p, stiffness=khex, expansion=[-.03, -.03, .18, 0., 0., 0.],
                coupling=[.2, .2, .5, 0., 0., 0.])
    orientations = {label: spatial_response(**dict(hexp, direction=direction))
                    for label, direction in {"basal": [1., 0., 0.], "axial": [0., 0., 1.],
                                             "oblique": [1., 0., 1.]}.items()}
    suite = unittest.defaultTestLoader.loadTestsFromName(
        "docs.core.test.test_topic13_thermoelastic_spatial_compatibility")
    run = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
    checks = {
        "isotropic_longitudinal_analytic_match": abs(ref["gain_per_phi_response"]-analytic) < 1e-12,
        "grating_equilibrium_residual": ref["mechanical_residual"] < 1e-12,
        "fixed_entropy_residual": abs(ref["entropy_residual"]) < 1e-12,
        "block_and_compliance_elimination_match": abs(ref["delta_temperature"]-ref["closed_form_temperature"]) < 1e-12,
        "homogeneous_strain_is_incompatible_in_declared_witness": ref["homogeneous_incompatible_strain_norm"] > 1e-4,
        "nonzero_transverse_stress_does_not_violate_equilibrium": np.linalg.norm(ref["stress"]) > 1e-3,
        "anisotropic_orientation_dependence_is_resolved": abs(orientations["basal"]["delta_temperature"]-orientations["axial"]["delta_temperature"]) > 1e-4,
        "independent_test_suite_passes": run.wasSuccessful() and run.testsRun >= 8,
        "existing_topic_closure_inputs_unchanged": before == {path: digest(path) for path in PROTECTED},
    }
    checks = {key: bool(value) for key, value in checks.items()}
    ok = all(checks.values())
    result = {
        "schema_version": "t13-thermoelastic-spatial-compatibility-v1",
        "major_result_id": "T13_THERMOELASTIC_FINITE_Q_COMPATIBILITY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if ok else "OPEN",
        "verification_status": "PASS_CONDITIONAL_FINITE_Q_COMPATIBILITY" if ok else "FAIL_FINITE_Q_COMPATIBILITY",
        "what_is_closed": [
            "Compatible bulk nonzero-q strain response derived from mechanical equilibrium and fixed local entropy.",
            "Homogeneous zero-stress formula cannot be reused as the general bulk grating formula.",
            "Full six-component Mandel shear/rotation structure and isotropic longitudinal limit tested.",
        ] if ok else [],
        "equation_registry_ids": [EQUATION_ID],
        "equation_or_mapping": {
            "compatibility": "eps=B(n)*v; B*v=Mandel(sym(n tensor v))",
            "equilibrium": "B^T*sigma=0; sigma=K_el*eps-beta*dT+G*phi_r; beta=K_el*alpha",
            "entropy": "ds=beta^T*eps+c_eps*dT/T=0",
            "compliance": "R_n=B*(B^T*K_el*B)^-1*B^T",
            "temperature": "dT=T*(beta^T*R_n*G)*phi_r/(c_eps+T*beta^T*R_n*beta)",
            "fixed_T_stability": "a_phi-G^T*R_n*G>0",
        },
        "ontology": {
            "K_el": "material isothermal stiffness, not UET C",
            "phi_r": "candidate energy-dimension response, not temperature or a new UET state",
            "eps": "external material strain from sym grad u",
            "G": "conditional material coupling, not yet action-derived or independently calibrated",
            "R_gen_and_R_obs": "excluded from state and dynamics",
        },
        "units": {"T": "E", "phi_r": "E", "K_el": "E^4", "alpha": "E^-1",
                  "beta": "E^3", "G": "E^3", "c_eps": "E^3", "a_phi": "E^2",
                  "R_n": "E^-4", "eps": "1", "n": "1"},
        "unit_lane": "conditional_natural_material_response_SI_open",
        "derivation_class": "derived_relation_with_conditional_Phi_strain_constitutive_ansatz",
        "observable": "conditional bulk grating temperature amplitude, not a TTG time trace",
        "data_role": "SYNTHETIC_INTERNAL_VERIFICATION_NO_CALIBRATION",
        "assumptions": ["linear homogeneous bulk", "nonzero grating wavevector", "positive isothermal stiffness",
                        "mechanically quasistatic", "ds=0 locally", "constant coefficients at reference T"],
        "reference_inputs": {key: value.tolist() if isinstance(value, np.ndarray) else value for key, value in p.items()},
        "reference_witness": ref,
        "grating_to_uniform_temperature_ratio": ref["gain_per_phi_response"]/ref["homogeneous_gain_per_phi_response"],
        "hexagonal_inputs": {key: value.tolist() if isinstance(value, np.ndarray) else value for key, value in hexp.items()},
        "hexagonal_orientation_witnesses": orientations,
        "checks": checks,
        "test_count": run.testsRun,
        "evidence_artifacts": [{"path": path, "sha256": digest(path)} for path in EVIDENCE],
        "protected_closure_hashes": before,
        "input_policy": {"experimental_numeric_input_paths": [], "holdout_numeric_access": "NOT_REQUIRED_NO_DATA_INPUT",
                         "scope": "This runner reads only listed evidence and protected gate files; not a repository-wide access audit."},
        "open_blockers": ["initial_entropy_and_finite_frequency_acoustic_heat_response_missing",
                          "physical_G_and_Z_Phi_not_identified", "same_state_material_tensor_and_uncertainty_missing"],
        "controlling_blocker": "finite_frequency_initial_entropy_material_response_missing",
        "dependency_unlocked": "conditional finite-frequency material-interface design only",
        "physical_dependency_unlock": False, "full_core_unlock": False, "claim_promotion": False,
        "claim_boundary": "Quasistatic locally isentropic bulk candidate only. No TTG dynamics, causal-cone proof, physical alpha, accepted UET action, external validation or Full Topic 13 closure.",
    }
    entry = dict(
        equation_id=EQUATION_ID, version="1", classification="conditional_material_interface",
        relation_or_code_path=result["equation_or_mapping"], ontology=result["ontology"],
        standard_physics_counterpart="linear anisotropic thermoelastic compatibility and plane-wave equilibrium",
        variables=result["ontology"], mathematical_role="constrained thermoelastic response",
        observable_mapping=result["observable"], unit_lane=result["unit_lane"], units=result["units"],
        parameter_dimensions=result["units"], derivation_class=result["derivation_class"],
        source_or_origin="derivation note and conditional material interaction; no physical constants fitted",
        assumptions=result["assumptions"], symmetry_and_conservation="Mandel rotation covariance, mechanical equilibrium, fixed entropy",
        limiting_cases=["isotropic longitudinal elasticity", "homogeneous free strain is a distinct boundary problem", "small positive shear"],
        implementation_paths=[EVIDENCE[1]], verifier_paths=[EVIDENCE[2], EVIDENCE[3]],
        observable=result["observable"], data_role=result["data_role"], evidence_class="INTERNAL_CONDITIONAL_DERIVATION",
        proof_status="derived within declared quasistatic ansatz; physical interpretation open",
        verification_status=result["verification_status"], evidence_artifacts=[],
        downstream_dependencies=["finite_frequency_material_response"], dependency_role="diagnostic_material_mapping",
        physical_dependency_unlock=False, controlling_blocker=result["controlling_blocker"],
        failure_mode=result["open_blockers"], next_hardening_step="derive acoustic and initial-entropy response before TTG use",
        claim_boundary=result["claim_boundary"],
    )
    return result, entry


def main():
    result, entry = build()
    (ROOT/ARTIFACT).write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    entry["evidence_artifacts"] = [{"path": ARTIFACT, "sha256": digest(ARTIFACT)}]
    registry = {"schema_version": "uet-equation-registry-addendum-v1", "status": "CONDITIONAL_INTERFACE_NOT_ACCEPTED_UET_ACTION",
                "extends": "docs/core/artifacts/uet_equation_correspondence_registry.json",
                "equation_entries": [entry], "full_core_unlock": False, "claim_promotion": False}
    (ROOT/REGISTRY).write_text(json.dumps(registry, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(result["verification_status"])
    print("grating_to_uniform_temperature_ratio="+str(result["grating_to_uniform_temperature_ratio"]))
    print("tests="+str(result["test_count"])+"; full_core_unlock=false")
    return 0 if all(result["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
