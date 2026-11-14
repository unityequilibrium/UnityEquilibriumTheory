"""Low-T compatibility boundary of the unmodified joint Hartree candidate.

The external phase mode is not inserted into the internal trace-log. A
conditional phonon comparator tests admission, not a repaired free energy.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from math import exp, isfinite, log, pi, sqrt
from pathlib import Path
import runpy

import numpy as np
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
JOINT_CODE = PREFIX+"Code/03_Research/Research_T13_Hartree_Joint_Phi_Response.py"
JOINT_ARTIFACT = PREFIX+"Result/artifacts/t13_hartree_joint_phi_response.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_hartree_low_T_validity.json")
M = runpy.run_path(str(ROOT/JOINT_CODE))
S, H, F, G = M["S"], M["S"]["H"], M["F"], M["G"]
STATE_ORDERS = ((128, 20.), (192, 40.), (256, 64.))
SOURCE_ORDERS = (96, 144, 192)
TEMPERATURE_DIVISORS = (2., 4., 8., 16., 32., 64.)
ENVELOPE_T = (.02, .01)
ENVELOPE_STEPS = (.02, .01, .005)
Q_GRID = (.008, .004, .002)
IMAGINARY_VELOCITIES = (.2, .4)
ROOT_TOLERANCE = 1e-8
REFINEMENT_TOLERANCE = 2e-5
ENVELOPE_TOLERANCE = 1e-3
WARD_TOLERANCE = 1e-3
EXPANSION_TOLERANCE = 5e-4
ASYMPTOTIC_DIAGNOSTIC_TOLERANCE = .1


def gap_jet(mu, a, b):
    F["validate"](0., mu, a, b)
    d = sqrt((a-b)**2+8*mu*mu*(a+b)+16*mu**4)
    A = a+b+4*mu*mu
    gap = sqrt(2*a*b/(A+sqrt(A*A-4*a*b)))
    # Exact unmixed equal masses have E=sqrt(k^2+a); no near-degeneracy cutoff.
    coefficient = 1. if d == 0 else 1-4*mu*mu/d
    return {"gap": gap, "low_energy_k_squared_coefficient": coefficient/(2*gap),
            "effective_quadratic_mass": gap/coefficient,
            "energy_squared_k_squared_coefficient": coefficient}


def entropy_weight(x):
    if not isfinite(x) or x <= 0:
        raise ValueError("positive finite energy/temperature required")
    occupation = exp(-x)/(-np.expm1(-x))
    return float(x*occupation-np.log1p(-exp(-x)))


def independent_entropy(t, mu, a, b, relative_tolerance=1e-9):
    F["validate"](t, mu, a, b)
    if t <= 0 or not 0 < relative_tolerance < 1:
        raise ValueError("positive T and relative quadrature tolerance required")
    jet = gap_jet(mu, a, b)
    momentum_scale = sqrt(2*jet["effective_quadratic_mass"]*t)
    # Factor the small Boltzmann scale out before adaptive error control.
    entropy_scale = momentum_scale**3*exp(-jet["gap"]/t)/(2*pi*pi)
    if entropy_scale == 0:
        raise ValueError("entropy scale underflow: outside this numerical diagnostic")
    def integrand(y):
        low, high = H["modes"](momentum_scale*y, mu, a, b)
        return y*y*(entropy_weight(float(low/t))+entropy_weight(float(high/t)))*exp(jet["gap"]/t)
    integral, error = quad(integrand, 0., np.inf, epsabs=1e-10, epsrel=relative_tolerance, limit=180)
    return {"entropy": float(entropy_scale*integral), "adaptive_absolute_error_estimate": float(entropy_scale*error),
            "momentum_scale": momentum_scale, "Boltzmann_entropy_scale": entropy_scale,
            "quadrature_relative_tolerance": relative_tolerance}


def boltzmann_entropy(t, mu, a, b):
    if not isfinite(t) or t <= 0:
        raise ValueError("positive finite temperature required")
    jet = gap_jet(mu, a, b)
    return (jet["effective_quadratic_mass"]*t/(2*pi))**1.5*exp(-jet["gap"]/t)*(jet["gap"]/t+2.5)


def residual_jacobian(state, mu, action):
    keys = ("s", "a", "b", "Phi")
    values = np.array([state[key] for key in keys])
    scales = np.array(state["residual_scales"])
    columns = []
    for j, value in enumerate(values):
        step = 1e-4*(abs(value) if j < 3 else 1.)
        high, low = values.copy(), values.copy()
        high[j] += step
        low[j] -= step
        columns.append((S["joint_residual"](*high, 0., mu, action)-S["joint_residual"](*low, 0., mu, action))/(2*step*scales))
    matrix = np.column_stack(columns)
    return {"matrix_in_MS_unit_coordinates": matrix.tolist(),
            "minimum_singular_value": float(np.linalg.svd(matrix, compute_uv=False)[-1]),
            "coordinate_contract": "s,a,b measured in MS^2 and Phi in MS; MS=1 E; residual E^2/E^3 scales retained, not an SI norm"}


def source_response(state, mu, action, q=0., z=0j, order=192):
    e = {"T": 0., "mu": mu, "u_canonical": action["u"]} | {key: state[key] for key in ("s", "a", "b", "Phi")}
    mixed, reverse, aa = G["gauge_loops"](q, z, 0., mu, e["a"], e["b"], radial_order=order, angular_order=32)
    bubble = F["direct_subtracted_bubble"](q, z, 0., mu, e["a"], e["b"], radial_order=order, angular_order=32)
    return M["assemble"](q, z, e, action, {"bubble": bubble, "mixed": mixed, "reverse": reverse, "loop_current": aa})


def zero_temperature_response(state, mu, action):
    runs = []
    for n in SOURCE_ORDERS:
        out = source_response(state, mu, action, order=n)
        chi, rho = (float(out["relaxed_current"][i, i].real) for i in (0, 1))
        runs.append({"order": n, "charge_susceptibility": chi, "spatial_stiffness": rho,
                     "external_phase_zero_inverse": float(abs(out["field"][1, 1])),
                     "even_min_singular_value": out["even_min_singular_value"],
                     "covariance_min_singular_value": out["covariance_min_singular_value"],
                     "current_imaginary_residual": float(np.max(abs(out["relaxed_current"].imag)))})
    chi, rho = runs[-1]["charge_susceptibility"], runs[-1]["spatial_stiffness"]
    if min(chi, rho) <= 0:
        raise RuntimeError("positive source coefficients not established; no sound repair")
    c = sqrt(rho/chi)
    finite_q = []
    for v in IMAGINARY_VELOCITIES:
        expected = (rho+v*v*chi)/state["s"]
        for q in Q_GRID:
            out = source_response(state, mu, action, q, 1j*v*q)
            finite_q.append({"q": q, "imaginary_velocity": v,
                             "phase_coefficient_real": float(out["phase_coefficient"].real),
                             "phase_coefficient_imaginary": float(out["phase_coefficient"].imag),
                             "expected_quadratic_coefficient": expected,
                             "relative_expansion_disagreement": float(abs(out["phase_coefficient"]/expected-1)),
                             "phase_current_Ward_disagreement": out["phase_current_Ward_disagreement"]})
    return {"source_runs": runs, "finite_q_upper_plane_checks": finite_q,
            "external_derivative_expansion_speed": c,
            "conditional_one_gapless_mode_entropy_T_cubed_coefficient": 2*pi*pi/(45*c**3),
            "coefficient_protocol": "joint source-relaxed T=0 derivative expansion; conditional bosonic mode counting, not inserted in Omega and not measured sound"}


def entropy_envelope(state, t, mu, action):
    expected = independent_entropy(t, mu, state["a"], state["b"])["entropy"]
    rows = []
    for factor in ENVELOPE_STEPS:
        h = factor*t
        states = [S["joint_background"](t+sign*h, mu, state, action) for sign in (-1, 1)]
        entropy = -(states[1]["potential"]-states[0]["potential"])/(2*h)
        frozen = -(S["joint_potential"](state["s"], state["a"], state["b"], state["Phi"], t+h, mu, action)
                   -S["joint_potential"](state["s"], state["a"], state["b"], state["Phi"], t-h, mu, action))/(2*h)
        rows.append({"relative_T_step": factor, "joint_pressure_entropy": float(entropy),
                     "fixed_variational_entropy": float(frozen),
                     "joint_relative_disagreement": float(abs(entropy/expected-1)),
                     "fixed_relative_disagreement": float(abs(frozen/expected-1))})
    return {"T": t, "expected_quasiparticle_entropy": expected, "runs": rows,
            "protocol": "mu and original action fixed; matter and Phi reoptimized; no additional phonon free energy"}


def audit(progress=None):
    previous = json.loads((ROOT/JOINT_ARTIFACT).read_text(encoding="utf-8"))
    action = M["controls"]()
    examples = []
    for row in previous["examples"]:
        anchor = {key: row[key] for key in ("s", "a", "b", "Phi")}
        mu = row["mu"]
        states = [S["joint_background"](0., mu, anchor, action, order=n, split=split) for n, split in STATE_ORDERS]
        zero = states[-1]
        seeds = [S["joint_background"](0., mu, anchor, action, seed_factor=factor) for factor in (.8, 1.2)]
        jet = gap_jet(mu, zero["a"], zero["b"])
        response = zero_temperature_response(zero, mu, action)
        curvature = S["covariance_hessian"](zero, 0., mu, action)
        jacobian = residual_jacobian(zero, mu, action)
        thermal = []
        for divisor in TEMPERATURE_DIVISORS:
            t = jet["gap"]/divisor
            state = S["joint_background"](t, mu, zero, action)
            independent = independent_entropy(t, mu, state["a"], state["b"])
            refined = independent_entropy(t, mu, state["a"], state["b"], 1e-11)
            zero_state = independent_entropy(t, mu, zero["a"], zero["b"])
            approximate = boltzmann_entropy(t, mu, zero["a"], zero["b"])
            entropy = independent["entropy"]
            legacy = state["loops"]["quasiparticle_entropy"]
            thermal.append({"T": t, "gap_over_T": divisor, "joint_state": state,
                            "independent_entropy": independent, "refined_independent_entropy": refined,
                            "entropy_over_T_cubed": entropy/t**3,
                            "conditional_gapless_entropy_ratio": entropy/(response["conditional_one_gapless_mode_entropy_T_cubed_coefficient"]*t**3),
                            "legacy_trace_log_entropy": legacy, "legacy_relative_difference": float(abs(legacy/entropy-1)),
                            "zero_state_entropy": zero_state["entropy"], "zero_state_Boltzmann_asymptotic_entropy": approximate,
                            "Boltzmann_asymptotic_relative_difference": float(abs(zero_state["entropy"]/approximate-1)),
                            "state_movement_from_zero": float(max(abs(state[key]-zero[key]) for key in ("s", "a", "b", "Phi")))})
        envelopes = [entropy_envelope(S["joint_background"](t, mu, zero, action), t, mu, action) for t in ENVELOPE_T]
        examples.append({"mu": mu, "zero_T_state": zero, "zero_T_gap_jet": jet, "zero_T_state_refinements": states,
                         "last_state_refinement": float(max(abs(states[-1][k]-states[-2][k]) for k in ("s", "a", "b", "Phi"))),
                         "seed_disagreement": float(max(abs(state[k]-zero[k]) for state in seeds for k in ("s", "a", "b", "Phi"))),
                         "local_static_Hessian": curvature, "zero_T_residual_Jacobian": jacobian,
                         "zero_T_external_response": response, "low_T_runs": thermal, "entropy_envelope_checks": envelopes,
                         "asymptotic_compatibility_disposition": "UNAMENDED_HARTREE_EOS_NOT_ADMITTED_AS_ASYMPTOTIC_THERMODYNAMICS_OF_ITS_EXTERNAL_GAPLESS_MODE"})
        if progress:
            progress(f"mu={mu}: internal gap={jet['gap']}, external derivative speed={response['external_derivative_expansion_speed']}, final entropy/T^3={thermal[-1]['entropy_over_T_cubed']}")
    checks = {
        "joint_response_predecessor_preserved": previous["closure_level"] == "CLOSED_FOR_LANE" and all(previous["checks"].values()),
        "unmodified_joint_zero_T_stationary_states": all(e["zero_T_state"]["scaled_residual_max"] < ROOT_TOLERANCE for e in examples),
        "zero_T_refinement_and_seed_agreement": all(e["last_state_refinement"] < REFINEMENT_TOLERANCE and e["seed_disagreement"] < REFINEMENT_TOLERANCE for e in examples),
        "positive_internal_gap_and_quadratic_minimum": all(min(e["zero_T_gap_jet"].values()) > 0 for e in examples),
        "local_static_positive_and_implicit_nondegeneracy": all(min(e["local_static_Hessian"]["eigenvalues"]) > 0 and e["zero_T_residual_Jacobian"]["minimum_singular_value"] > .01 for e in examples),
        "external_static_phase_zero_and_positive_source_coefficients": all(run["external_phase_zero_inverse"] < REFINEMENT_TOLERANCE and min(run["charge_susceptibility"],run["spatial_stiffness"],run["even_min_singular_value"],run["covariance_min_singular_value"]) > .01 and run["current_imaginary_residual"] < 1e-10 for e in examples for run in e["zero_T_external_response"]["source_runs"]),
        "zero_T_source_coefficient_refinement": all(abs(e["zero_T_external_response"]["source_runs"][-1][key]/e["zero_T_external_response"]["source_runs"][-2][key]-1) < REFINEMENT_TOLERANCE for e in examples for key in ("charge_susceptibility", "spatial_stiffness")),
        "upper_plane_quadratic_phase_and_source_Ward": all(run["relative_expansion_disagreement"] < EXPANSION_TOLERANCE and run["phase_current_Ward_disagreement"] < WARD_TOLERANCE for e in examples for run in e["zero_T_external_response"]["finite_q_upper_plane_checks"] if run["q"] == Q_GRID[-1]),
        "independent_entropy_quadrature_refinement": all(abs(r["independent_entropy"]["entropy"]/r["refined_independent_entropy"]["entropy"]-1) < 1e-7 for e in examples for r in e["low_T_runs"]),
        "legacy_entropy_matches_resolved_temperature_window": all(r["legacy_relative_difference"] < REFINEMENT_TOLERANCE for e in examples for r in e["low_T_runs"] if r["gap_over_T"] <= 16),
        "joint_and_frozen_entropy_envelope": all(r["runs"][-1]["joint_relative_disagreement"] < ENVELOPE_TOLERANCE and r["runs"][-1]["fixed_relative_disagreement"] < ENVELOPE_TOLERANCE for e in examples for r in e["entropy_envelope_checks"]),
        "Boltzmann_asymptotic_approach": all(e["low_T_runs"][-1]["Boltzmann_asymptotic_relative_difference"] < ASYMPTOTIC_DIAGNOSTIC_TOLERANCE and e["low_T_runs"][-1]["Boltzmann_asymptotic_relative_difference"] < e["low_T_runs"][-2]["Boltzmann_asymptotic_relative_difference"] for e in examples),
        "entropy_over_T_cubed_decreases_in_deep_gapped_window": all(e["low_T_runs"][-1]["entropy_over_T_cubed"] < e["low_T_runs"][-2]["entropy_over_T_cubed"] < e["low_T_runs"][-3]["entropy_over_T_cubed"] for e in examples),
        "protected_Core_and_baseline_hashes_unchanged": all(hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"] for item in previous["protected_evidence_hashes"]),
    }
    passed = all(checks.values())
    paths = (JOINT_ARTIFACT, JOINT_CODE, M["STATIC_CODE"], F["BACKGROUND_CODE"], G["FIELD_CODE"], PREFIX+"Code/03_Research/Research_T13_Hartree_Gauge_Current.py", *S["ACTION_PATHS"], Path(__file__).relative_to(ROOT).as_posix())
    record = {"schema_version": "t13-joint-hartree-low-T-validity-v1", "generated_at": datetime.now(timezone.utc).isoformat(),
              "major_result_id": "T13_JOINT_HARTREE_LOW_T_THERMODYNAMIC_COMPATIBILITY_BOUNDARY", "topic": "0.13", "branch_id": previous["branch_id"],
              "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL", "verification_status": "PASS_SCOPED_LOW_T_EXCLUSION" if passed else "FAIL_LOW_T_BOUNDARY_CHECK",
              "what_is_closed": ["zero_T_joint_stationarity_and_positive_internal_gap_at_two_witnesses", "entropy_envelope_without_added_external_mode", "conditional_low_T_EOS_external_gapless_mode_compatibility_exclusion"],
              "equation_or_mapping": "Delta^2=2ab/(a+b+4mu^2+sqrt((a+b+4mu^2)^2-4ab)); s_H=-partial_T Omega_joint=s_internal; s_H/T^3->0 for nondegenerate positive-gap zero-T branch; conditional one physical linear bosonic mode gives s_ph/T^3=2pi^2/(45c^3)>0, c^2=rho/chi",
              "units": {"T_mu_Phi_gap_effective_mass": "E", "s_a_b_Hessian_chi_rho": "E^2", "entropy": "E^3", "potential": "E^4", "speed_entropy_over_T_cubed": "dimensionless"},
              "derivation_class": "CONDITIONAL_ASYMPTOTIC_COMPATIBILITY_BOUNDARY_PLUS_INTERNAL_NUMERICAL_WITNESSES_NOT_GLOBAL_UET_NO_GO",
              "observable": "candidate_equilibrium_entropy_and_external_phase_derivative_coefficients_not_material_heat_or_temperature", "data_role": "DERIVED_NO_EMPIRICAL_ROWS",
              "equation_registry_ids": ["t13.diagnostic.joint_hartree_entropy_envelope", "t13.diagnostic.joint_hartree_low_T_compatibility_boundary"],
              "action_controls": action, "examples": examples, "checks": checks,
              "config": {"zero_T_state_orders": STATE_ORDERS, "source_orders": SOURCE_ORDERS, "T_equals_zero_T_gap_divided_by": TEMPERATURE_DIVISORS, "envelope_T": ENVELOPE_T, "envelope_steps": ENVELOPE_STEPS, "upper_q_grid": Q_GRID, "upper_imaginary_velocities": IMAGINARY_VELOCITIES, "design_note": "Grid and gates locked in verifier after exploratory zero-T/entropy trend; not preregistered against external data"},
              "thresholds": {"scaled_root": ROOT_TOLERANCE, "state_refinement_and_resolved_entropy": REFINEMENT_TOLERANCE, "entropy_envelope": ENVELOPE_TOLERANCE, "phase_Ward": WARD_TOLERANCE, "upper_quadratic_expansion": EXPANSION_TOLERANCE, "Boltzmann_finite_T_diagnostic": ASYMPTOTIC_DIAGNOSTIC_TOLERANCE, "causal_leakage_unchanged": 1e-6},
              "evidence_artifacts": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in dict.fromkeys(paths)],
              "protected_evidence_hashes": previous["protected_evidence_hashes"],
              "compatibility_assumptions": ["smooth_noncritical_joint_zero_T_stationary_branch_with_positive_internal_gaps", "nonsingular_local_stationary_Jacobian", "external_derivative_expansion_admitted_as_one_physical_equilibrium_bosonic_mode", "unamended_internal_Hartree_trace_log_is_claimed_as_asymptotically_complete_thermal_EOS"],
              "physical_low_T_EOS_admission": "BLOCKED_ASYMPTOTIC_SPECTRUM_THERMODYNAMICS_MISMATCH" if passed else "UNRESOLVED",
              "open_blockers": ["consistent_gapless_thermal_approximation_or_explicit_restricted_validity_not_yet_derived", "global_regulator_RG_controlled_Hartree_remainder", "independent_material_source_readout_temperature_mapping", "physical_heat_collision_Kubo_SK_KMS_entropy_transport"],
              "controlling_blocker": "gapless_equilibrium_thermal_prescription_not_derived",
              "dependency_unlocked": ["research_on_consistent_thermal_approximation_and_independent_input_only"] if passed else [],
              "conditional_asymptotic_exclusion_established": bool(passed), "global_UET_no_go": False,
              "source_response_predecessor_invalidated": False, "phonon_free_energy_added": False, "mass_repair": False,
              "physical_Kubo_emitted": False, "independent_alpha_Phi_K_admitted": False, "controlled_truncation_error_established": False,
              "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False, "core_composition_gate_overwritten": False,
              "claim_promotion": False, "parameter_fitting": False, "clipping": False, "IR_filter": False,
              "target_source_accessed": False, "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
              "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False,
              "state_variables": ["same_O2_mean_field_and_covariance", "existing_classical_UET_Phi"], "excluded_variables": ["R_gen", "R_obs", "nondynamical_A"],
              "claim_boundary": "Conditional local low-T admission exclusion of one unmodified Hartree prescription at two trial-input witnesses; not global UET no-go, new approximation, physical material transport, SI calibration, external validation or Full Topic13/Core closure."}
    names = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    values = (record["major_result_id"]+": "+record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Checked unmodified joint zero-T state, entropy envelope and conditional external-mode thermodynamic boundary, without a mass/phonon repair.", record["equation_or_mapping"], checks, record["controlling_blocker"], "Derive a consistent gapless thermal prescription or a justified restricted validity lane; do not rematch masses or append phonon free energy by hand. Retain independent-input and full Goal obligations.", record["claim_boundary"])
    record["report"] = dict(zip(names, values))
    return record


if __name__ == "__main__":
    result = audit(progress=lambda message: print(message, flush=True))
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"]}, indent=2), flush=True)
