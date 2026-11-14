"""Tree Noether density readout, not atomic density or thermal transport.

Chemical-potential source vertices and their seagull follow the same
declared action. Independent first-order and modal projections verify them.
The neutron route remains a protocol screen, not a numeric dataset.
"""

from datetime import datetime, timezone
import hashlib
import json
from math import isfinite, sqrt
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[5]
LOCAL = Path(__file__).resolve().parent
sys.path.insert(0, str(LOCAL))
import Research_T13_Gaussian_Work_Remainder as REM

WORK, VIRT, EFT, TH, MOD, PREFIX = REM.WORK, REM.VIRT, REM.EFT, REM.TH, REM.MOD, REM.PREFIX
PREDECESSOR = PREFIX+"Result/artifacts/t13_gaussian_work_remainder.json"
PREDECESSOR_SHA = "0bff6697f0c94f749cbaf2134c3e78ae36de40c66783a7303e8c5f5aadf307b1"
REGISTRY = PREFIX+"Data/03_Research/t13_noether_density_readout_registry.json"
PROTOCOL = PREFIX+"Data/03_Research/t13_density_spectroscopy_protocol_screen.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_noether_density_readout.json")
FIRST_FAILURE = OUTPUT.with_name("t13_noether_density_readout_first_failure.json")
# Density and unit-family subprotocols were fixed before their respective first audits.
MU_GRID, Q_GRID = (1.05, 1.2), (.002, .01, .04)
FREQUENCIES = (.02j, .05j, .03+.02j)
FD_STEPS, POLE_OFFSETS, COORDINATE_SCALES = (1e-4, 5e-5), (1e-4, 5e-5), (.5, 2.)
UNIT_FAMILY_SCALES = (1.01, 1.02)
GATES = {"identity_relative": 1e-8, "static_derivative_relative": 1e-6,
         "pole_projection_relative": 1e-5, "negative_control_minimum": .1,
         "gain_null_absolute": 1e-12, "original_causal_leakage": 1e-6}


def load_predecessor():
    raw = (ROOT/PREDECESSOR).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PREDECESSOR_SHA:
        raise ValueError("predecessor changed; revalidate its identity")
    record = json.loads(raw)
    if not all(record["checks"].values()) or record["old_source_work_audit_promoted"]:
        raise ValueError("the new scoped result must not overwrite the original FAIL")
    return record


def source_vertices(z, state):
    if not np.isfinite(z) or state["xi"] != 0:
        raise ValueError("finite rest-frame frequency required")
    v, mu = sqrt(state["s"]), state["mu"]
    return v*np.array([2*mu, 1j*z, 0]), v*np.array([2*mu, -1j*z, 0])


def density_response(q, z, state, action, first_order=False):
    if not isfinite(q) or q < 0 or not np.isfinite(z) or z.imag <= 0:
        raise ValueError("nonnegative q and upper-half-plane frequency required")
    source, detector = source_vertices(z, state)
    if first_order:
        kinetic, linear, potential = VIRT.matrices(q, state, action)
        gyro = (1j*linear).real
        generator = np.block([[np.zeros((3, 3)), np.eye(3)],
                              [-np.linalg.solve(kinetic, potential), -np.linalg.solve(kinetic, gyro)]])
        force = np.r_[np.zeros(3), np.linalg.solve(kinetic, source)]
        phase_space = np.linalg.solve(-1j*z*np.eye(6)-generator, force)
        x = phase_space[:3]
        matter_density = sqrt(state["s"])*(2*state["mu"]*x[0]+phase_space[4])
    else:
        x = np.linalg.solve(VIRT.kernel(q, z, state, action), source)
        matter_density = detector@x
    total = state["s"]+matter_density
    current = -1j*q*sqrt(state["s"])*x[1]
    terms = [-1j*z*state["s"], -1j*z*matter_density, 1j*q*current]
    ward = abs(sum(terms))/max(sum(abs(t) for t in terms), 1e-30)
    h_response = np.linalg.solve(VIRT.kernel(q, z, state, action), [0., 0., 1.])
    return {"susceptibility": complex(total), "matter_without_contact": complex(matter_density),
            "current_response": complex(current), "ward_error": float(ward),
            "density_to_h": complex(detector@h_response)}


def projected_modes(q, state, action):
    if not isfinite(q) or q <= 0:
        raise ValueError("positive q for three separated tree modes required")
    result = []
    for energy, unit in VIRT.tree_modes(q, state, action):
        _, detector = source_vertices(energy, state)
        amplitude = detector@unit
        ward_amplitude = -1j*sqrt(state["s"])*q*q*unit[1]/energy
        result.append({"energy": energy, "density_strength": float(abs(amplitude)**2),
                       "mixed_density_Phi_strength": float((amplitude*unit[2].conjugate()).real),
                       "on_shell_ward_error": float(abs(amplitude-ward_amplitude)/max(abs(amplitude), abs(ward_amplitude), 1e-30))})
    return result


def modal_response(q, z, state, action, modes=None):
    modes = projected_modes(q, state, action) if modes is None else modes
    return complex(sum(x["density_strength"]/(x["energy"]**2-z*z) for x in modes)), complex(sum(x["mixed_density_Phi_strength"]/(x["energy"]**2-z*z) for x in modes))


def static_density_susceptibility(state, action):
    active = (0, 2)
    hessian = VIRT.matrices(0., state, action)[2][np.ix_(active, active)]
    radial = np.linalg.solve(hessian, [2*state["mu"]*sqrt(state["s"]), 0.])
    return float(state["s"]+2*state["mu"]*sqrt(state["s"])*radial[0])


def intensity_product(gain, density_map):
    if not all(isfinite(x) and x > 0 for x in (gain, density_map)):
        raise ValueError("positive finite gain and density map required")
    return gain*density_map*density_map


def gain_information():
    jacobian = np.array([[1., 2.]])
    augmented = np.array([[1., 2.], [1., 0.]])
    rows = []
    for scale in (.5, 2.):
        rows.append({"coordinate_scale": scale, "gain": 1/scale**2, "density_map": scale,
                     "same_intensity_product": intensity_product(1/scale**2, scale), "data_role": "CONSTRUCTIVE_IDENTIFIABILITY_WITNESS_NOT_DATA"})
    return {"log_parameter_order": ["instrument_gain", "Noether_to_atomic_density_map"],
            "log_intensity_jacobian": jacobian.tolist(), "null_direction": [-2., 1.],
            "null_residual": float(np.linalg.norm(jacobian@np.array([-2., 1.]))),
            "amplitude_only_rank": int(np.linalg.matrix_rank(jacobian)),
            "plus_independent_gain_rank": int(np.linalg.matrix_rank(augmented)),
            "positive_class_inverse": "Z_N=sqrt(I/(G_inst*S_N)); conditional on known nonzero S_N and all other input/units",
            "conditional_not_full_UET_minimum_measurements": True, "witnesses": rows}


def kinetic_inverse(linear, cubic, volumetric_scale, sound, eta_base, density):
    values = (linear, cubic, volumetric_scale, sound, eta_base, density)
    if not all(isfinite(x) and x > 0 for x in values):
        raise ValueError("positive conditional dispersion, scale and state inputs required")
    q_unit = (sound*volumetric_scale/linear)**.25
    energy_unit = linear*q_unit/sound
    eta = cubic*q_unit**3/energy_unit
    invariant = (eta/eta_base-1)/density
    return {"q_unit": q_unit, "energy_unit": energy_unit, "eta": eta, "I_kinetic": invariant}


def kinetic_log_gradient(linear, cubic, volumetric_scale, sound, eta_base, density):
    result = kinetic_inverse(linear, cubic, volumetric_scale, sound, eta_base, density)
    ratio = result["eta"]/eta_base/density
    return np.array([-1.5*ratio, ratio, .5*ratio, 1.5*ratio, -ratio, -result["I_kinetic"]])


def unit_information(state, action):
    cf = EFT.rest_coefficients(state, action)
    s = state["s"]
    invariant = action["gamma"]**2*action["epsilon"]*action["response_kinetic"]/state["V_curvature"]**2
    eta_base = cf["eta"]/(1+s*invariant)
    slope = s/(1+s*invariant)
    jacobian = np.array([[1., -1., 0.], [1., -3., slope]])
    augmented = np.vstack([jacobian, [1., 3., 0.]])
    rows = []
    # Unit values here are ratios to a constructive reference, not SI inputs.
    for scale in UNIT_FAMILY_SCALES:
        target_invariant = (scale**2*(1+s*invariant)-1)/s
        kinetic = target_invariant*state["V_curvature"]**2/(action["gamma"]**2*action["epsilon"])
        other_action = action | {"response_kinetic": kinetic}
        other_state = EFT.tree_state(state["mu"], action=other_action)
        other_cf = EFT.rest_coefficients(other_state, other_action)
        recovered = kinetic_inverse(cf["c"], cf["eta"], scale**4, cf["c"], eta_base, s)
        rows.append({"unit_ratio": scale, "energy_unit_ratio": scale, "q_unit_ratio": scale,
                     "I_kinetic": target_invariant, "response_kinetic": kinetic,
                     "same_linear_coefficient_error": WORK.relative(scale*other_cf["c"]/scale, cf["c"]),
                     "same_cubic_coefficient_error": WORK.relative(scale*other_cf["eta"]/scale**3, cf["eta"]),
                     "static_native_pressure_error": WORK.relative(other_state["pressure_tree"], state["pressure_tree"]),
                     "volumetric_scale_ratio": scale**4,
                     "independent_scale_inverse_error": WORK.relative(recovered["I_kinetic"], target_invariant),
                     "data_role": "CONSTRUCTIVE_UNIT_KINETIC_AMBIGUITY_NOT_SI_CALIBRATION"})
    inverted = kinetic_inverse(cf["c"], cf["eta"], 1., cf["c"], eta_base, s)
    return {"scope": "q_cubed_dispersion_with_native_static_inputs_fixed_but_action_SI_scales_open",
            "parameter_order": ["log_E_unit", "log_Q_unit", "I_kinetic"],
            "observable_order": ["log_linear_energy_Q_coefficient", "log_cubic_energy_Q_coefficient"],
            "jacobian": jacobian.tolist(), "null_direction": [1., 1., 2/slope],
            "null_residual": float(np.linalg.norm(jacobian@np.array([1., 1., 2/slope]))),
            "dispersion_only_rank": int(np.linalg.matrix_rank(jacobian)),
            "plus_independent_volumetric_scale_rank": int(np.linalg.matrix_rank(augmented)),
            "augmented_determinant": float(np.linalg.det(augmented)),
            "analytic_determinant": -4*slope, "eta_base": eta_base, "I_kinetic_reference": invariant,
            "inverse_reference_error": WORK.relative(inverted["I_kinetic"], invariant),
            "positive_reference_inverse": inverted, "witnesses": rows,
            "log_input_order_for_uncertainty": ["linear", "cubic", "volumetric_scale", "c", "eta_base", "s"],
            "log_gradient_I": kinetic_log_gradient(cf["c"], cf["eta"], 1., cf["c"], eta_base, s).tolist(),
            "uncertainty_contract": "Var(I)=g^T Sigma_log g plus a separately controlled theory remainder; no independent errors or instrument precision assumed",
            "native_static_inputs_do_not_include_admitted_physical_volumetric_scale": True,
            "volumetric_relation_requires_declared_action_normalization": True,
            "independent_physical_scale_already_locked_would_remove_this_family": True,
            "absolute_pressure_at_SVP_or_vacuum_offset_is_not_automatically_a_scale_anchor": True,
            "only_retained_q_and_q_cubed_coefficients_preserved_not_full_curve": True}


def encoded(value):
    return {"real": float(value.real), "imag": float(value.imag)}


def audit():
    load_predecessor()
    action, examples = EFT.controls(), []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        static = static_density_susceptibility(state, action)
        derivatives = []
        for step in FD_STEPS:
            plus, minus = [EFT.tree_state(m, action=action) for m in (mu+step, mu-step)]
            difference = ((mu+step)*plus["s"]-(mu-step)*minus["s"])/(2*step)
            derivatives.append({"step": step, "pressure_charge_derivative": difference,
                                "relative_error": WORK.relative(difference, static)})
        q_rows = []
        for q in Q_GRID:
            modes = projected_modes(q, state, action)
            responses, residues, coordinates = [], [], []
            for z in FREQUENCIES:
                direct = density_response(q, z, state, action)
                first = density_response(q, z, state, action, True)
                modal, mixed = modal_response(q, z, state, action, modes)
                responses.append({"z": encoded(z), "density": encoded(direct["susceptibility"]),
                                  "density_h": encoded(direct["density_to_h"]),
                                  "six_state_relative_error": WORK.relative(direct["susceptibility"], first["susceptibility"]),
                                  "modal_relative_error": WORK.relative(direct["susceptibility"], modal),
                                  "mixed_modal_relative_error": WORK.relative(direct["density_to_h"], mixed),
                                  "ward_error": direct["ward_error"]})
                for scale in COORDINATE_SCALES:
                    other_action = EFT.rescale_Phi_coordinate(action, scale)
                    other = EFT.tree_state(mu, action=other_action)
                    mapped = density_response(q, z, other, other_action)
                    coordinates.append({"scale": scale, "z": encoded(z),
                                        "density_invariant_error": WORK.relative(mapped["susceptibility"], direct["susceptibility"]),
                                        "h_column_covariance_error": WORK.relative(mapped["density_to_h"], scale*direct["density_to_h"])})
            energy, strength = modes[0]["energy"], modes[0]["density_strength"]
            for offset in POLE_OFFSETS:
                estimates = []
                for sign in (-1, 1):
                    z = energy*sqrt(1+sign*offset)
                    source, detector = source_vertices(z, state)
                    chi = state["s"]+detector@np.linalg.solve(VIRT.kernel(q, z, state, action), source)
                    estimates.append(float(((energy*energy-z*z)*chi).real))
                residues.append({"offset": offset, "density_strength_estimate": sum(estimates)/2,
                                 "relative_error": WORK.relative(sum(estimates)/2, strength)})
            q_rows.append({"q": q, "modes": modes, "responses": responses, "pole_residue_checks": residues,
                           "sum_rule_relative_error": WORK.relative(sum(x["density_strength"] for x in modes), state["s"]*q*q),
                           "coordinate_controls": coordinates})
        zero = []
        for z in FREQUENCIES:
            row = density_response(0., z, state, action)
            zero.append({"z": encoded(z), "total_density_scaled_error": abs(row["susceptibility"])/state["s"],
                         "missing_contact_scaled_error": abs(row["matter_without_contact"])/state["s"],
                         "neutral_h_density_scaled_error": abs(row["density_to_h"])/max(state["s"], 1e-30)})
        examples.append({"mu": mu, "unit_information": unit_information(state, action), "static_density_susceptibility": static,
                         "tree_pressure_chi": state["A"], "static_pressure_error": WORK.relative(static, state["A"]),
                         "static_derivative_checks": derivatives, "q_rows": q_rows, "q0_dynamic_controls": zero})
    decoupled = action | {"gamma": 0.}
    decoupled_state = EFT.tree_state(MU_GRID[0], action=decoupled)
    dark = max(abs(density_response(q, z, decoupled_state, decoupled)["density_to_h"]) for q in Q_GRID for z in FREQUENCIES)
    information = gain_information()
    qrows = [r for e in examples for r in e["q_rows"]]
    checks = {
        "independent_six_state_density_response": all(r["six_state_relative_error"] < GATES["identity_relative"] for q in qrows for r in q["responses"]),
        "all_tree_modal_density_and_mixed_projection": all(max(r["modal_relative_error"], r["mixed_modal_relative_error"]) < GATES["identity_relative"] for q in qrows for r in q["responses"]),
        "source_charge_ward": all(r["ward_error"] < GATES["identity_relative"] for q in qrows for r in q["responses"]),
        "static_pressure_charge_curvature": all(e["static_pressure_error"] < GATES["identity_relative"] and max(r["relative_error"] for r in e["static_derivative_checks"]) < GATES["static_derivative_relative"] for e in examples),
        "density_pole_and_sum_rule": all(max(r["relative_error"] for r in q["pole_residue_checks"]) < GATES["pole_projection_relative"] and q["sum_rule_relative_error"] < GATES["identity_relative"] and all(r["density_strength"] >= 0 for r in q["modes"]) for q in qrows),
        "q0_closed_charge_and_contact_negative": all(r["total_density_scaled_error"] < GATES["identity_relative"] and r["neutral_h_density_scaled_error"] < GATES["identity_relative"] and r["missing_contact_scaled_error"] > GATES["negative_control_minimum"] for e in examples for r in e["q0_dynamic_controls"]),
        "Phi_coordinate_invariance_not_absolute_thermal_scale": all(max(r["density_invariant_error"], r["h_column_covariance_error"]) < GATES["identity_relative"] for q in qrows for r in q["coordinate_controls"]),
        "decoupled_Phi_is_not_seen_as_density": dark < GATES["identity_relative"],
        "gain_map_constructive_nonidentifiability": information["null_residual"] < GATES["gain_null_absolute"] and information["amplitude_only_rank"] == 1 and information["plus_independent_gain_rank"] == 2 and all(x["same_intensity_product"] == 1 for x in information["witnesses"]),
        "conditional_unit_kinetic_information_and_inverse": all(u["dispersion_only_rank"] == 2 and u["plus_independent_volumetric_scale_rank"] == 3 and u["null_residual"] < GATES["gain_null_absolute"] and WORK.relative(u["augmented_determinant"], u["analytic_determinant"]) < GATES["identity_relative"] and u["inverse_reference_error"] < GATES["identity_relative"] and all(max(r["same_linear_coefficient_error"], r["same_cubic_coefficient_error"], r["static_native_pressure_error"], r["independent_scale_inverse_error"]) < GATES["identity_relative"] for r in u["witnesses"]) for u in (e["unit_information"] for e in examples))}
    passed = all(checks.values())
    source_record = json.loads((ROOT/PROTOCOL).read_text())
    paths = [Path(__file__).relative_to(ROOT).as_posix(), REGISTRY, PROTOCOL, PREFIX+"Code/03_Research/test_t13_noether_density_readout.py"]
    protected = [PREDECESSOR, REM.PREDECESSOR, PREFIX+"Result/artifacts/t13_gaussian_source_work_first_failure.json", PREFIX+"Result/artifacts/t13_thermal_noether_response.json", PREFIX+"Result/artifacts/t13_low_T_phase_eft.json"]+list(EFT.ACTION_PATHS)
    record = {"major_result_id": "T13_NOETHER_DENSITY_READOUT_AND_CALIBRATION_BOUNDARY", "topic": "0.13_Thermodynamic_Bridge", "branch_id": VIRT.BRANCH,
              "generated_at": datetime.now(timezone.utc).isoformat(), "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
              "verification_status": "PASS_SCOPED_NOETHER_DENSITY_READOUT" if passed else "FAIL_SCOPED_NOETHER_DENSITY_READOUT",
              "what_is_closed": "Tree Noether density/source/contact, independent spectral and first-order projection, coordinate covariance, restricted gain/density-map and q-cubed action-unit/kinetic identifiability with conditional inverse when checks pass",
              "equation_or_mapping": "delta_n=s*a0+sqrt(s)*(2mu*sigma+dot_pi_phase); chi_nn=s+j_minus D^-1 j_plus=sum Rnn/(E_j^2-z^2); I=G_inst*Z_N^2*(R_instrument convolve S_Noether) conditional",
              "units": {"a0": "E", "Noether_density_current": "E^3", "chi_nn": "E^2", "density_pole_strength": "E^4", "chi_nh": "E^0", "h": "E^3", "Phi": "E", "atomic_density_temperature_and_count_map": "not admitted; SI scales and source/detector conversions remain independent inputs"},
              "derivation_class": "DERIVED_SAME_ACTION_TREE_NOETHER_SOURCE_HESSIAN_AND_MODAL_READOUT_WITH_CONSTRUCTIVE_GAIN_BOUNDARY", "observable": "conditional density-susceptibility poles/strength, not temperature or second sound", "data_role": "DERIVED_AND_CONSTRUCTIVE_CONTROL_NO_EXPERIMENTAL_ROWS",
              "declared_protocol": {"density_protocol_locked_before_first_density_audit": True, "unit_family_locked_before_first_unit_information_audit": True, "unit_family_scales": UNIT_FAMILY_SCALES, "mu_grid": MU_GRID, "q_grid": Q_GRID, "upper_half_plane_frequencies": [encoded(z) for z in FREQUENCIES], "finite_difference_steps": FD_STEPS, "pole_offsets": POLE_OFFSETS, "coordinate_scales": COORDINATE_SCALES, "trial_inputs_not_lab_settings": True},
              "action_controls": action, "thresholds": GATES, "checks": checks, "examples": examples,
              "instrument_gain_boundary": information, "decoupled_h_to_density_max": dark,
              "protocol_screen_status": source_record["status"], "external_numeric_rows_admitted": 0,
              "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected),
              "equation_registry_ids": [e["id"] for e in json.loads((ROOT/REGISTRY).read_text())["entries"]],
              "controlling_blocker": "Noether_to_atomic_density_SI_state_resolution_and_independent_gain_not_admitted" if passed else "tree_density_source_readout_verification_open",
              "open_blockers": ["Noether_charge_to_He4_number_density_and_action_unit_state_match", "independent_Q_energy_temperature_gain_and_joint_resolution_covariance", "permitted_primary_low_q_numeric_rows_uncertainty_and_source_ancestry", "nonlinear_parent_interaction_and_physical_heat_entropy_KMS"],
              "dependency_unlocked": ["same_state_density_protocol_information_gap_research_only"] if passed else [],
              "tree_Noether_density_readout_verified": passed, "restricted_gain_density_map_ambiguity_verified": passed,
              "conditional_dispersion_unit_scale_information_verified": passed,
              "physical_Noether_to_atomic_density_map_admitted": False, "physical_measurement_protocol_admitted": False,
              "physical_resolution_or_intrinsic_damping_admitted": False, "full_measurement_design_completed": False,
              "independent_alpha_Phi_K_admitted": False, "physical_Kubo_emitted": False, "full_SK_KMS_matching_closed": False,
              "nonlinear_parent_action_completed": False, "controlled_full_action_truncation_error_established": False,
              "old_source_work_audit_promoted": False, "full_core_unlock": False, "core_composition_gate_overwritten": False,
              "C_relabelled_as_charge_or_mass": False, "state_variables": ["existing_radial_phase_Phi_tree_fluctuations"],
              "excluded_variables": ["C", "UET_Pi", "R_gen", "R_obs", "external_a0", "instrument_gain"],
              "parameter_fitting": False, "assigned_width": False, "assigned_relaxation_time": False,
              "quantum_Phi_loops_added": False, "predecessor_covariance_vacuum_populations_changed": False,
              "clipping": False, "cone_padding": False, "claim_promotion": False, "xie_2026_accessed": False,
              "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
              "claim_boundary": "Same-action tree Noether charge readout only, not automatic He4 atomic density, S(Q,E) admission, SI temperature, heat, full finite-T/KMS transport or physical UET validation. Instrument-gain ambiguity is a restricted class result, not a global minimum-measurement theorem; Phi coordinate invariance is not a physical no-go. Original failures, owner gates and exposure review remain unchanged."}
    names = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(names, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Derived Noether density readout and selected conditional spectroscopy input packet", record["equation_or_mapping"], checks, record["controlling_blocker"], "Verify particle-current/state/units and obtain independent resolution/gain with primary low-q source rows; never identify resolution width with intrinsic damping", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    result = audit()
    raw = (json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8")
    OUTPUT.write_bytes(raw)
    if not all(result["checks"].values()) and not FIRST_FAILURE.exists():
        FIRST_FAILURE.write_bytes(raw)
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"]}, indent=2))
    raise SystemExit(0 if all(result["checks"].values()) else 1)
