"""Reproduce a source-separated material comparator without physical unlocks."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import unittest

import numpy as np

from docs.core.uet_dynamic_thermoelastic_response import material_mode
from docs.core.uet_thermoelastic_spatial_compatibility import isotropic_stiffness

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = "docs/core/07_artifacts/topic13/t13_dynamic_thermoelastic_response_audit.json"
REGISTRY = "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic13_dynamic_material_response_addendum.json"
ID = "uet.o2.thermal.dynamic_material_response"
EVIDENCE = ["docs/core/03_lanes/topic13_support/T13_DYNAMIC_THERMOELASTIC_RESPONSE.md",
            "docs/core/03_lanes/thermal/uet_dynamic_thermoelastic_response.py",
            "docs/core/test/test_topic13_dynamic_thermoelastic_response.py",
            "docs/scripts/audit/audit_topic13_dynamic_thermoelastic_response.py",
            "docs/core/07_artifacts/topic13/t13_thermoelastic_spatial_compatibility_audit.json",
            "docs/core/03_lanes/thermal/uet_thermoelastic_spatial_compatibility.py"]
PROTECTED = ["docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json",
             "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"]


def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def build():
    protected = {path: digest(path) for path in PROTECTED}
    p = dict(stiffness=isotropic_stiffness(5., 3.), expansion=np.array([.04, .04, .04, 0., 0., 0.]),
             coupling=np.array([.7, .7, .7, 0., 0., 0.]), direction=[1., 0., 0.],
             q=1., rho=1., temperature=.8, heat_capacity=2.4, conductivity=.3, relaxation=.2)
    times = np.linspace(0., 12., 61)
    curves, witnesses = {}, {}
    for name, tau in (("fourier", 0.), ("cattaneo", .2)):
        mode = material_mode(**dict(p, relaxation=tau))
        x0 = mode.initial_state(.03)
        curve = mode.evolve_constant(times, x0)
        availability = np.einsum("ti,ij,tj->t", curve, mode.metric, curve)/2
        balances = [mode.balance(row) for row in curve]
        transfer_errors = []
        for s in (.1+.01j, .1+.5j, .1+3j, .1+10j):
            direct = np.linalg.solve(s*np.eye(len(mode.matrix))-mode.matrix,
                                     np.column_stack([mode.phi_port, mode.heat_port]))[6]
            transfer_errors.append(float(np.linalg.norm(direct-mode.laplace_transfer(s))))
        curves[name] = curve[:, 6]/x0[6]
        witnesses[name] = {
            "relaxation": tau,
            "state_variables": ["v[3]", "w[3]", "theta"]+(["longitudinal_J"] if tau else []),
            "initial_entropy": .03, "initial_temperature": float(x0[6]),
            "initial_temperature_slope": float((mode.matrix@x0)[6]),
            "time_samples": times.tolist(), "normalized_temperature": curves[name].tolist(),
            "max_balance_residual": max(abs(row["balance_residual"]) for row in balances),
            "max_availability_increase": float(np.max(np.diff(availability))),
            "min_metric_eigenvalue": float(np.min(np.linalg.eigvalsh(mode.metric))),
            "max_generator_real_part": float(np.max(np.linalg.eigvals(mode.matrix).real)),
            "max_laplace_crosscheck_error": max(transfer_errors),
            "dc_phi_temperature_gain": float(mode.laplace_transfer(0.)[0]),
            "causal_status": "PARABOLIC_STANDARD_COMPARATOR" if not tau else "LINEAR_RELAXATION_CONTROL_NOT_UET_CONE_VERIFICATION",
        }
    no_heat = material_mode(**dict(p, conductivity=0., relaxation=0.))
    no_heat_gain = float(no_heat.laplace_transfer(1e-6)[0])
    homogeneous_initial_boundary = {
        "prescribed_phi": 0., "initial_entropy": .03,
        "temperature_at_initial_time": witnesses["cattaneo"]["initial_temperature"],
        "interpretation": "This material interface admits a heat-initialized temperature response without Phi drive; a universal proportional output map requires an additional coupled initialization constraint.",
    }
    run = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromName(
        "docs.core.test.test_topic13_dynamic_thermoelastic_response"))
    checks = {
        "focused_analytic_dynamic_balance_and_covariance_tests": run.wasSuccessful() and run.testsRun >= 12,
        "both_metrics_positive": all(w["min_metric_eigenvalue"] > 0 for w in witnesses.values()),
        "both_unforced_modes_non_growing": all(w["max_generator_real_part"] < 1e-10 for w in witnesses.values()),
        "availability_balances_close": all(w["max_balance_residual"] < 1e-12 for w in witnesses.values()),
        "sampled_availability_nonincreasing": all(w["max_availability_increase"] < 1e-12 for w in witnesses.values()),
        "independent_laplace_eliminations_match": all(w["max_laplace_crosscheck_error"] < 1e-11 for w in witnesses.values()),
        "heat_initialization_is_not_zero_Phi_initialization": homogeneous_initial_boundary["temperature_at_initial_time"] > 0,
        "fourier_and_relaxation_initial_slopes_differ": witnesses["fourier"]["initial_temperature_slope"] < 0 and witnesses["cattaneo"]["initial_temperature_slope"] == 0,
        "conducting_DC_and_isentropic_limits_differ": witnesses["fourier"]["dc_phi_temperature_gain"] == 0 and abs(no_heat_gain) > .01,
        "protected_full_closure_files_unchanged": protected == {path: digest(path) for path in PROTECTED},
    }
    checks = {key: bool(value) for key, value in checks.items()}
    ok = all(checks.values())
    equations = {
        "mechanical": "dot(v)=w; dot(w)=-(q^2/rho)*(A*v-b*theta+h*phi_r)",
        "heat_balance": "c*dot(theta)=-T*b^T*w-q*J+Q",
        "flux": "tau*dot(J)+J=k*q*theta for tau>0; J=k*q*theta for tau=0",
        "initial_entropy": "theta0=T*(ds0-b^T*v0)/c",
        "availability": "W=rho*w^2/(2*q^2)+v^T*A*v/2+c*theta^2/(2*T)+tau*J^2/(2*T*k)",
        "power_balance": "dot(W)=-phi_r*h^T*w+theta*Q/T-J^2/(T*k); Fourier dissipation=k*q^2*theta^2/T",
        "transfer": "H_Phi=T*s*b^T*D^-1*h/(c*s+k*q^2/(1+tau*s)+T*s*b^T*D^-1*b); D=A+rho*s^2*I/q^2",
    }
    result = {
        "schema_version": "t13-dynamic-material-response-v1",
        "major_result_id": "T13_DYNAMIC_MATERIAL_RESPONSE_AND_INITIAL_ENTROPY",
        "topic": "0.13_Thermodynamic_Bridge", "closure_level": "CLOSED_FOR_LANE" if ok else "OPEN",
        "verification_status": "PASS_CONDITIONAL_DYNAMIC_MATERIAL_RESPONSE" if ok else "FAIL_DYNAMIC_MATERIAL_RESPONSE",
        "what_is_closed": ["Bulk thermoelastic time response with separate initial entropy, heat source and prescribed Phi ports.",
                           "Positive modal availability and explicit external-source/dissipation balance.",
                           "Independent Laplace and time-domain verification, including Fourier/Cattaneo analytic limits.",
                           "Conducting DC response is distinct from the locally isentropic static gain."] if ok else [],
        "equation_registry_ids": [ID], "equation_or_mapping": equations,
        "ontology": {"rho_and_K_el": "material inertia and stiffness, not UET C", "phi_r": "prescribed response port, not temperature or an added state",
                     "state": "compatible material v,w,theta and optional longitudinal J", "R_gen_R_obs": "excluded"},
        "units": {"rho": "E^4", "K_el": "E^4", "v": "1", "w": "E", "theta": "E", "phi_r": "E", "q": "E",
                  "T": "E", "c": "E^3", "b": "E^3", "G": "E^3", "k": "E^2", "tau": "E^-1", "J": "E^4", "Q": "E^5", "ds": "E^3"},
        "unit_lane": "natural_conditional_material_comparator_not_SI",
        "derivation_class": "linear_standard_thermoelastic_response_with_conditional_external_Phi_port",
        "observable": "bulk temperature grating amplitude from independent initial and driven inputs",
        "data_role": "SYNTHETIC_COMPARATOR_NO_CALIBRATION",
        "synthetic_inputs": {key: value.tolist() if isinstance(value, np.ndarray) else value for key, value in p.items()},
        "witnesses": witnesses, "initialization_boundary": homogeneous_initial_boundary,
        "no_conduction_low_frequency_phi_gain": no_heat_gain,
        "max_normalized_fourier_cattaneo_difference": float(np.max(np.abs(curves["fourier"]-curves["cattaneo"]))),
        "checks": checks, "test_count": run.testsRun,
        "evidence_artifacts": [{"path": path, "sha256": digest(path)} for path in EVIDENCE],
        "protected_full_closure_hashes": protected,
        "input_policy": "No experimental numeric input or fitting. Only listed local evidence/gate files are hashed. This is not a repository-wide holdout-access audit.",
        "open_blockers": ["physical_pump_to_Phi_entropy_initialization_missing", "independent_G_Z_and_same_state_transport_inputs_missing",
                          "reciprocal_UET_material_dynamics_and_KMS_matching_missing", "finite_geometry_detector_map_and_uncertainty_missing"],
        "controlling_blocker": "physical_pump_to_Phi_entropy_initialization_and_material_coefficients_missing",
        "dependency_unlocked": "conditional pump/material initialization design only",
        "physical_dependency_unlock": False, "full_core_unlock": False, "claim_promotion": False,
        "claim_boundary": "Standard bulk material comparator with prescribed Phi, not full UET dynamics, physical alpha/Kubo/KMS, graphite validation or a replacement causal-cone gate.",
    }
    return result


def main():
    result = build()
    (ROOT/OUTPUT).write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    entry = {key: result[key] for key in ("ontology", "units", "unit_lane", "derivation_class", "observable", "data_role",
                                         "verification_status", "controlling_blocker", "claim_boundary", "physical_dependency_unlock")}
    entry.update(equation_id=ID, version="1", classification="conditional_material_comparator",
                 relation_or_code_path=result["equation_or_mapping"], standard_physics_counterpart="linear thermoelasticity with Fourier/Cattaneo conduction",
                 variables=result["ontology"], mathematical_role="source-separated dynamic response and availability balance",
                 observable_mapping=result["observable"], parameter_dimensions=result["units"],
                 source_or_origin="standard material conservation/constitutive equations plus an uncalibrated Phi-strain ansatz",
                 assumptions=["linear bulk grating", "constant reference coefficients", "prescribed Phi", "scalar flux relaxation"],
                 symmetry_and_conservation="reciprocal thermoelastic coupling; source-explicit availability balance; rotation covariance",
                 limiting_cases=["Fourier tau=0", "decoupled telegraph heat mode", "no-conduction isentropic response"],
                 implementation_paths=[EVIDENCE[1]], verifier_paths=[EVIDENCE[2], EVIDENCE[3]],
                 proof_status="conditional linear derivation and internal verification only", evidence_class="INTERNAL_STANDARD_COMPARATOR",
                 evidence_artifacts=[{"path": OUTPUT, "sha256": digest(OUTPUT)}],
                 downstream_dependencies=["physical_pump_and_material_interface"], dependency_role="diagnostic_material_mapping",
                 failure_mode=result["open_blockers"], next_hardening_step="derive physical pump/initialization and reciprocal material coupling before calibration")
    registry = {"schema_version": "uet-equation-registry-addendum-v1", "status": "CONDITIONAL_INTERFACE_NOT_ACCEPTED_UET_ACTION",
                "extends": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json", "equation_entries": [entry],
                "full_core_unlock": False, "claim_promotion": False}
    (ROOT/REGISTRY).write_text(json.dumps(registry, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(result["verification_status"])
    print("max_normalized_control_difference="+str(result["max_normalized_fourier_cattaneo_difference"]))
    print("no_conduction_gain="+str(result["no_conduction_low_frequency_phi_gain"])+"; conducting_DC_gain=0")
    return 0 if all(result["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
