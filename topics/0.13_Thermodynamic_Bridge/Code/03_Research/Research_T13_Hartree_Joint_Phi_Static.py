"""Homogeneous classical-Phi extension of the declared Hartree candidate.

Keep the mass-dependent normalization when varying the UET response.
Phi fluctuations, finite-q joint dynamics and material matching are excluded.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from math import isfinite, sqrt
from pathlib import Path
import runpy
import sys

import numpy as np
from scipy.optimize import root

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
FIELD_CODE = PREFIX+"Code/03_Research/Research_T13_Hartree_External_Response.py"
F = runpy.run_path(str(ROOT/FIELD_CODE))
H, CT = F["H"], F["CT"]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config

BACKGROUND = F["BACKGROUND_ARTIFACT"]
COUNTERTERM = F["MATCH_ARTIFACT"]
POLES = PREFIX+"Result/artifacts/t13_hartree_finite_q_poles.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_hartree_joint_phi_static.json")
ACTION_PATHS = (
    "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
    "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py",
    "docs/core/02_equations/o2/uet_o2_finite_density_eos.py",
    "docs/core/02_equations/covariant/uet_covariant_matter.py",
    "docs/core/02_equations/covariant/uet_covariant_response.py",
)
ORDERS = ((128, 20.), (192, 40.), (256, 64.))
PHI_STEPS = (.002, .001, .0005)
LOOP_ORDERS = (96, 144, 192)
MS_SCALE = 1.0
IDENTITY_TOLERANCE = 1e-10
ROOT_TOLERANCE = 1e-8
REFINEMENT_TOLERANCE = 1e-5
HESSIAN_TOLERANCE = 2e-5


def action_controls():
    eos = natural_bridge_config().eos
    matter, response = eos.matter, eos.response
    return {"Z": matter.matter_kinetic, "m0_sq": matter.matter_mass_sq/matter.matter_kinetic,
            "u": matter.matter_quartic/matter.matter_kinetic**2,
            "gamma": response.epsilon_nc*matter.response_coupling/matter.matter_kinetic,
            "epsilon": response.epsilon_nc, "Phi_reference": response.phi_equilibrium,
            "response_mass_sq": response.response_mass_sq, "response_quartic": response.response_quartic}


def validate_controls(controls):
    if not all(isfinite(value) for value in controls.values()):
        raise ValueError("finite action inputs required")
    if min(controls[name] for name in ("Z", "u", "epsilon", "response_quartic")) <= 0:
        raise ValueError("positive kinetic, quartic and response prefactor required")
    if min(controls["gamma"], controls["response_mass_sq"]) < 0:
        raise ValueError("declared nonnegative reciprocal coupling and response mass required")


def mass_sq(phi, controls):
    validate_controls(controls)
    if not isfinite(phi):
        raise ValueError("finite UET response Phi required")
    return controls["m0_sq"]-controls["gamma"]*(phi-controls["Phi_reference"])


def response_potential(phi, controls):
    mass_sq(phi, controls)
    x = phi-controls["Phi_reference"]
    return controls["epsilon"]*(controls["response_mass_sq"]*x*x/2+controls["response_quartic"]*x**4/4)


def response_force(phi, controls):
    mass_sq(phi, controls)
    x = phi-controls["Phi_reference"]
    return controls["epsilon"]*(controls["response_mass_sq"]*x+controls["response_quartic"]*x**3)


def response_curvature(phi, controls):
    mass_sq(phi, controls)
    x = phi-controls["Phi_reference"]
    return controls["epsilon"]*(controls["response_mass_sq"]+3*controls["response_quartic"]*x*x)


def normalization_jet(phi, controls, D, D2, reference_sq=1., reference_logdet=0.):
    m = mass_sq(phi, controls)
    ct = CT["counterterms"](controls["u"], D, D2, m, reference_sq)
    singlet = 1+4*controls["u"]*D
    delta = D2+(m-reference_sq)*D
    gamma = controls["gamma"]
    return {"normalization": CT["normalization_constant"](ct, D, D2, m, reference_sq, reference_logdet),
            "normalization_force": -gamma*delta/singlet,
            "normalization_curvature": gamma*gamma*D/singlet,
            "bare_mass_slope": -gamma/singlet,
            "bare_response_force": response_force(phi, controls)+gamma*delta/singlet,
            "bare_response_curvature": response_curvature(phi, controls)-gamma*gamma*D/singlet}


def force_match(phi, s, finite_tadpoles, mu, controls, D, D2):
    m, gamma = mass_sq(phi, controls), controls["gamma"]
    row = CT["state_match"](s, finite_tadpoles, m, controls["u"], mu, D, D2, 1.)
    jet = normalization_jet(phi, controls, D, D2)
    finite_force = response_force(phi, controls)-gamma*(s+sum(finite_tadpoles))/2
    bare_matter_force = jet["bare_mass_slope"]*(s+sum(row["unsubtracted_tadpoles"]))/2
    matched_force = jet["bare_response_force"]+bare_matter_force
    uncorrected_force = response_force(phi, controls)+bare_matter_force
    return {"finite_force": float(finite_force), "matched_bare_force": float(matched_force),
            "force_match_residual": float(matched_force-finite_force),
            "uncorrected_force_difference": float(uncorrected_force-finite_force),
            "normalization_force": jet["normalization_force"], "normalization_curvature": jet["normalization_curvature"],
            "potential_match_residual": row["potential_match_residual"]}


def joint_residual(s, a, b, phi, t, mu, controls, order=256, split=64.):
    r = mu*mu-mass_sq(phi, controls)
    if r <= 0:
        raise ValueError("this declared condensed chart requires r>0; no branch repair")
    loops = H["loop_integrals"](t, mu, a, b, order=order, split=split)
    Is, Ip, u = loops["sigma"], loops["phase"], controls["u"]
    return np.array([-r+u*s+u*(3*Is+Ip), a+r-3*u*s-u*(3*Is+Ip),
                     b+r-u*s-u*(Is+3*Ip),
                     response_force(phi, controls)-controls["gamma"]*(s+Is+Ip)/2])


def joint_background(t, mu, anchor, controls=None, order=256, split=64., seed_factor=1.):
    controls = action_controls() if controls is None else controls
    validate_controls(controls)
    if not isfinite(seed_factor) or seed_factor <= 0:
        raise ValueError("positive numerical seed factor required")
    initial = np.r_[np.log([anchor[name]*seed_factor for name in ("s", "a", "b")]), anchor["Phi"]]
    matter_scale = mu*mu-mass_sq(anchor["Phi"], controls)
    # The first three residuals carry E^2; the Phi force carries E^3.
    force_scale = controls["epsilon"]*MS_SCALE**3
    scales = np.array([matter_scale]*3+[force_scale])
    if matter_scale <= 0:
        raise ValueError("initial state outside condensed chart")
    def equations(values):
        s, a, b = np.exp(values[:3])
        return joint_residual(s, a, b, values[3], t, mu, controls, order, split)/scales
    result = root(equations, initial, options={"xtol": 1e-10, "maxfev": 200})
    s, a, b = np.exp(result.x[:3])
    phi = result.x[3]
    residual = joint_residual(s, a, b, phi, t, mu, controls, order, split)
    if not result.success or np.max(abs(residual/scales)) > ROOT_TOLERANCE:
        raise RuntimeError("joint stationary candidate not closed; no fallback/mass repair")
    loops = H["loop_integrals"](t, mu, a, b, order=order, split=split)
    potential = joint_potential(s, a, b, phi, t, mu, controls, order, split)
    return {"s": float(s), "a": float(a), "b": float(b), "Phi": float(phi),
            "residual": residual.tolist(), "residual_scales": scales.tolist(),
            "residual_scale_units": ["E^2", "E^2", "E^2", "E^3"],
            "scaled_residual_max": float(np.max(abs(residual/scales))),
            "potential": float(potential), "mass_sq": mass_sq(phi, controls), "loops": loops}


def joint_potential(s, a, b, phi, t, mu, controls, order=256, split=64.):
    r = mu*mu-mass_sq(phi, controls)
    return response_potential(phi, controls)+H["variational_potential"](s, a, b, t, mu, r, controls["u"], order=order, split=split)


def covariance_hessian(state, t, mu, controls, order=256, split=64.):
    s, a, b, phi = (state[name] for name in ("s", "a", "b", "Phi"))
    step = 1e-4*min(a, b)
    def tadpoles(am, bm):
        loops = H["loop_integrals"](t, mu, am, bm, order=order, split=split)
        return np.array([loops["sigma"], loops["phase"]])
    J = np.column_stack(((tadpoles(a+step, b)-tadpoles(a-step, b))/(2*step),
                         (tadpoles(a, b+step)-tadpoles(a, b-step))/(2*step)))
    u, gamma = controls["u"], controls["gamma"]
    kernel = np.eye(2)-u*CT["HARTREE_MATRIX"]@J
    ms = np.linalg.solve(kernel, u*np.array([3., 1.]))
    mm = np.linalg.solve(kernel, np.ones(2))
    vv = 2*s*(u+u*np.array([3., 1.])@J@ms)+state["residual"][0]
    vphi = -gamma*sqrt(s)*(1+u*np.array([3., 1.])@J@mm)
    phiv = -gamma*sqrt(s)*(1+np.ones(2)@J@ms)
    phiphi = response_curvature(phi, controls)+gamma**2/2*np.ones(2)@J@mm
    matrix = np.array([[vv, vphi], [phiv, phiphi]])
    reduced_phi = phiphi-phiv*vphi/vv
    return {"matrix": matrix.tolist(), "reciprocity_residual": float(abs(vphi-phiv)),
            "covariance_min_singular_value": float(np.linalg.svd(kernel, compute_uv=False)[-1]),
            "eigenvalues": np.linalg.eigvalsh(matrix).tolist(),
            "radial_relaxed_Phi_curvature": float(reduced_phi)}


def source_loop_hessian(state, t, mu, controls, order=192):
    s, a, b, phi = (state[name] for name in ("s", "a", "b", "Phi"))
    bubble = F["direct_subtracted_bubble"](0., 0j, t, mu, a, b, radial_order=order, angular_order=16)
    _, kernel, field_vertices = F["source_vertices"](s, controls["u"])
    phi_vertex = np.array([-sqrt(2)*controls["gamma"], 0., 0.])
    vertices = np.column_stack((field_vertices[:, 0], phi_vertex))
    # The only new insertion is the derivative of the declared mass term.
    tree = np.array([[a, -controls["gamma"]*sqrt(s)],
                     [-controls["gamma"]*sqrt(s), response_curvature(phi, controls)]])
    matrix = tree+.5*vertices.T@bubble@np.linalg.solve(np.eye(3)-kernel@bubble, vertices)
    return {"matrix": F["complex_matrix"](matrix), "bubble": F["complex_matrix"](bubble),
            "covariance_min_singular_value": float(np.linalg.svd(np.eye(3)-kernel@bubble, compute_uv=False)[-1]),
            "phase_Ward_inverse": float((b+.5*field_vertices[:, 1]@bubble@np.linalg.solve(np.eye(3)-kernel@bubble, field_vertices[:, 1])).real),
            "imaginary_residual": float(np.max(abs(matrix.imag)))}


def potential_hessian_check(state, t, mu, controls):
    v, phi = sqrt(state["s"]), state["Phi"]
    def optimized(field, response):
        r = mu*mu-mass_sq(response, controls)
        a, b = H["solve_gap_at_s"](field*field, t, mu, r, controls["u"], state)
        return joint_potential(field*field, a, b, response, t, mu, controls)
    expected = np.asarray(covariance_hessian(state, t, mu, controls)["matrix"])
    rows = []
    center = optimized(v, phi)
    for relative_step in PHI_STEPS:
        hv, hp = relative_step*v, relative_step*MS_SCALE
        vv = (optimized(v+hv, phi)+optimized(v-hv, phi)-2*center)/hv**2
        pp = (optimized(v, phi+hp)+optimized(v, phi-hp)-2*center)/hp**2
        vp = (optimized(v+hv, phi+hp)-optimized(v+hv, phi-hp)-optimized(v-hv, phi+hp)+optimized(v-hv, phi-hp))/(4*hv*hp)
        actual = np.array([[vv, vp], [vp, pp]])
        rows.append({"relative_field_step": relative_step, "Phi_step": hp, "matrix": actual.tolist(),
                     "maximum_absolute_disagreement": float(np.max(abs(actual-expected)))})
    return rows


def relaxed_phi_derivative_check(state, t, mu, controls):
    expected = covariance_hessian(state, t, mu, controls)["radial_relaxed_Phi_curvature"]
    rows = []
    for relative_step in PHI_STEPS:
        h = relative_step*MS_SCALE
        states = []
        for sign in (-1, 1):
            phi = state["Phi"]+sign*h
            r = mu*mu-mass_sq(phi, controls)
            matter = H["stationary_background"](t, mu, r, controls["u"])
            states.append(matter | {"Phi": phi})
        values = [response_force(e["Phi"], controls)-controls["gamma"]*(e["s"]+e["loops"]["sigma"]+e["loops"]["phase"])/2 for e in states]
        derivative = (values[1]-values[0])/(2*h)
        rows.append({"Phi_step": h, "force_derivative": float(derivative), "expected_curvature": expected,
                     "absolute_disagreement": float(abs(derivative-expected))})
    return rows


def audit(progress=None):
    previous = {path: json.loads((ROOT/path).read_text(encoding="utf-8")) for path in (BACKGROUND, COUNTERTERM, POLES)}
    controls = action_controls()
    formal = [force_match(phi, s, tadpoles, .85, controls, D, D2)
              | {"Phi": phi, "s": s, "finite_tadpoles": list(tadpoles), "D": D, "D2": D2}
              for phi in (-.1, .15, .3) for s, f1, f2 in CT["STATE_PROBES"]
              for tadpoles in ((f1, f2),) for D in CT["D_PROBES"] for D2 in CT["D2_PROBES"]]
    examples = []
    for e in previous[BACKGROUND]["examples"]:
        anchor = e["background"] | {"Phi": e["Phi_fixed"]}
        runs = [joint_background(e["T"], e["mu"], anchor, controls, order=n, split=split) for n, split in ORDERS]
        state = runs[-1]
        seeds = [joint_background(e["T"], e["mu"], anchor, controls, seed_factor=f) for f in (.8, 1.2)]
        curvature = covariance_hessian(state, e["T"], e["mu"], controls)
        loops = [source_loop_hessian(state, e["T"], e["mu"], controls, order=n) | {"radial_order": n} for n in LOOP_ORDERS]
        expected = np.asarray(curvature["matrix"])
        for loop in loops:
            actual = np.asarray(loop["matrix"]["real"])+1j*np.asarray(loop["matrix"]["imaginary"])
            loop["maximum_hessian_disagreement"] = float(np.max(abs(actual-expected)))
        matching = [force_match(state["Phi"], state["s"], (state["loops"]["sigma"], state["loops"]["phase"]), e["mu"], controls, D, D2)
                    for D in CT["D_PROBES"] for D2 in CT["D2_PROBES"]]
        potential_rows = potential_hessian_check(state, e["T"], e["mu"], controls)
        relaxed_rows = relaxed_phi_derivative_check(state, e["T"], e["mu"], controls)
        frozen_force = joint_residual(anchor["s"], anchor["a"], anchor["b"], anchor["Phi"], e["T"], e["mu"], controls)[-1]
        maximum_refinement = max(abs(runs[-1][key]-runs[-2][key]) for key in ("s", "a", "b", "Phi"))
        examples.append({"T": e["T"], "mu": e["mu"], "prior_fixed_Phi": e["Phi_fixed"],
                         "prior_fixed_Phi_joint_force": float(frozen_force), "joint_state": state,
                         "quadrature_runs": runs, "maximum_last_state_refinement": float(maximum_refinement),
                         "maximum_seed_disagreement": max(abs(seed[key]-state[key]) for seed in seeds for key in ("s", "a", "b", "Phi")),
                         "static_covariance_hessian": curvature, "independent_source_loop_hessian": loops,
                         "reoptimized_potential_Hessian": potential_rows, "radial_relaxed_Phi_force_derivative": relaxed_rows,
                         "formal_counterterm_replay_at_joint_state": matching})
        if progress:
            progress(f"mu={e['mu']}: joint Phi={state['Phi']}, min static eigenvalue={min(curvature['eigenvalues'])}")
    checks = {
        "accepted_predecessors_preserved": all(record["closure_level"] == "CLOSED_FOR_LANE" and all(record["checks"].values()) for record in previous.values()),
        "same_declared_action_trial_inputs": all(e["u_canonical"] == controls["u"] and abs(e["mu"]**2-e["r"]-mass_sq(e["Phi_fixed"], controls)) < 1e-12 for e in previous[BACKGROUND]["examples"]),
        "arbitrary_state_counterterm_force_and_potential_match": max(abs(row[key]) for row in formal for key in ("force_match_residual", "potential_match_residual")) < IDENTITY_TOLERANCE,
        "dropping_mass_normalization_is_detected": max(abs(row["uncorrected_force_difference"]) for row in formal) > 1e-3,
        "actual_joint_stationarity_without_mass_or_Phi_fit": all(e["joint_state"]["scaled_residual_max"] < ROOT_TOLERANCE for e in examples),
        "fixed_Phi_is_not_joint_stationarity": all(abs(e["prior_fixed_Phi_joint_force"]) > 1e-4 for e in examples),
        "joint_state_refinement_and_seed_agreement": all(e["maximum_last_state_refinement"] < REFINEMENT_TOLERANCE and e["maximum_seed_disagreement"] < REFINEMENT_TOLERANCE for e in examples),
        "mixed_static_reciprocity_and_covariance_nonsingularity": all(e["static_covariance_hessian"]["reciprocity_residual"] < IDENTITY_TOLERANCE and e["static_covariance_hessian"]["covariance_min_singular_value"] > .01 for e in examples),
        "independent_actual_source_loop_Hessian_and_static_Ward": all(e["independent_source_loop_hessian"][-1]["maximum_hessian_disagreement"] < HESSIAN_TOLERANCE and abs(e["independent_source_loop_hessian"][-1]["phase_Ward_inverse"]) < HESSIAN_TOLERANCE for e in examples),
        "reoptimized_potential_Hessian_agreement": all(e["reoptimized_potential_Hessian"][-1]["maximum_absolute_disagreement"] < HESSIAN_TOLERANCE for e in examples),
        "radial_relaxed_Phi_force_curvature_agreement": all(e["radial_relaxed_Phi_force_derivative"][-1]["absolute_disagreement"] < HESSIAN_TOLERANCE for e in examples),
        "local_static_positive_amplitude_Phi_block": all(min(e["static_covariance_hessian"]["eigenvalues"]) > 0 and e["static_covariance_hessian"]["radial_relaxed_Phi_curvature"] > 0 for e in examples),
        "joint_state_counterterm_replay": all(abs(row["force_match_residual"]) < IDENTITY_TOLERANCE for e in examples for row in e["formal_counterterm_replay_at_joint_state"]),
        "protected_Core_and_failed_baseline_hashes_unchanged": all(hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"] for item in previous[POLES]["protected_evidence_hashes"]),
    }
    passed = all(checks.values())
    paths = (BACKGROUND, COUNTERTERM, POLES, FIELD_CODE, *ACTION_PATHS, Path(__file__).relative_to(ROOT).as_posix())
    record = {"schema_version": "t13-hartree-joint-phi-static-v1", "generated_at": datetime.now(timezone.utc).isoformat(),
              "major_result_id": "T13_HOMOGENEOUS_CLASSICAL_PHI_HARTREE_STATIONARITY", "topic": "0.13",
              "branch_id": "t13.candidate.classical_phi_hartree_ms_homogeneous_v1", "parent_branch_id": previous[POLES]["branch_id"],
              "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL", "verification_status": "PASS_SCOPED_JOINT_PHI_STATIC" if passed else "FAIL_JOINT_PHI_STATIC",
              "what_is_closed": ["mass_dependent_normalization_force_and_curvature_counterterm", "homogeneous_classical_Phi_and_matter_stationary_candidate_at_two_states", "mixed_source_Hessian_reciprocity_and_local_static_stability"],
              "equation_or_mapping": "m2(Phi)=m0^2/Z-gamma*(Phi-Phi_*); U_b=U_R-N(m2); Gamma_Phi=epsilon*U'(Phi)-gamma*(s+I_s+I_p)/2; Gamma_Phi=0 jointly with matter gaps/field; Gamma_joint=Gamma_tree+L_joint^T*J*(I-KJ)^-1*L_joint/2",
              "units": {"Phi_T_mu_gamma": "E", "m2_s_a_b_D2_response_mass_sq": "E^2", "epsilon_u_Z_D_response_quartic": "dimensionless", "potential_N": "E^4", "Phi_force": "E^3", "static_joint_curvature": "E^2"},
              "derivation_class": "HOMOGENEOUS_CLASSICAL_RESPONSE_BACKGROUND_AND_HARTREE_SOURCE_DERIVATION_NOT_FULL_QUANTUM_JOINT_ACTION",
              "observable": "joint_stationary_state_and_conditional_static_response_not_material_temperature_or_dynamic_sound", "data_role": "DERIVED_FORMAL_PROBES_NO_EMPIRICAL_ROWS",
              "equation_registry_ids": ["t13.diagnostic.hartree_Phi_normalization_jet", "t13.diagnostic.classical_Phi_hartree_joint_static"],
              "action_controls": controls, "examples": examples, "formal_counterterm_probes": formal, "checks": checks,
              "config": {"orders_and_vacuum_splits": ORDERS, "potential_difference_steps_in_MS_units": PHI_STEPS, "source_loop_orders": LOOP_ORDERS, "MS_scale": MS_SCALE, "MS_scale_units": "E", "force_residual_scale": "epsilon*MS_scale^3 (E^3)", "numerical_seed_factors": [.8, 1.2]},
              "thresholds": {"algebraic_identity": IDENTITY_TOLERANCE, "scaled_root": ROOT_TOLERANCE, "state_refinement": REFINEMENT_TOLERANCE, "static_Hessian_absolute": HESSIAN_TOLERANCE, "causal_leakage_unchanged": 1e-6},
              "evidence_artifacts": [{"path": path, "sha256": hashlib.sha256((ROOT/path).read_bytes()).hexdigest()} for path in paths],
              "protected_evidence_hashes": previous[POLES]["protected_evidence_hashes"],
              "open_blockers": ["joint_finite_q_retarded_response_and_validity_domain", "regulator_RG_and_controlled_Hartree_action_remainder", "response_field_quantum_fluctuation_and_kinetic_counterterm_if_required", "independent_material_state_source_detector_thermal_input_and_physical_transport"],
              "controlling_blocker": "joint_dynamic_validity_regulator_remainder_material_transport_not_closed",
              "dependency_unlocked": ["named_homogeneous_classical_Phi_candidate_joint_dynamic_research_only"],
              "homogeneous_classical_Phi_stationarity_derived": bool(passed), "full_quantum_joint_Phi_stationarity_derived": False,
              "joint_finite_q_complex_pole_computed": False, "prior_fixed_Phi_poles_reused_as_joint": False,
              "physical_Kubo_emitted": False, "independent_alpha_Phi_K_admitted": False, "controlled_truncation_error_established": False,
              "global_phase_minimum_proved": False, "full_covariant_counterterm_match": False, "RG_invariance_established": False,
              "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False, "core_composition_gate_overwritten": False,
              "claim_promotion": False, "parameter_fitting": False, "target_source_accessed": False, "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
              "clipping": False, "IR_filter": False, "mass_repair": False, "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False,
              "state_variables": ["same_O2_amplitude_and_covariance", "existing_classical_UET_Phi_response_background"], "excluded_variables": ["R_gen", "R_obs", "nondynamical_A"],
              "claim_boundary": "Homogeneous classical-Phi extension of one named trial-input Hartree prescription. Local static stationarity and mixed susceptibility only, not quantum Phi loops, finite-q joint dynamics, global stability, controlled Hartree remainder, material calibration/prediction, physical heat/Kubo/SK-KMS/entropy or Full Topic13/UET."}
    names = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    values = (record["major_result_id"]+": "+record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"],
              "Derived mass-source/response counterterms, actual homogeneous joint states and independently checked mixed static response without retuning.", record["equation_or_mapping"], checks, record["controlling_blocker"],
              "Construct same-action joint finite-q response and validity/approximation contract before independent material/thermal and physical transport admission; do not reuse old fixed-Phi poles.", record["claim_boundary"])
    record["report"] = dict(zip(names, values))
    return record


if __name__ == "__main__":
    result = audit(progress=lambda message: print(message, flush=True))
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"]}, indent=2), flush=True)
