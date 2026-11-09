"""Same-action classical-Phi response of the jointly stationary Hartree lane.

Matter covariance is reoptimized; Phi has its declared classical kinetic
term, not quantum loops or an imposed damping width. No old pole is reused.
"""

from __future__ import annotations

from datetime import datetime, timezone
import gc
import hashlib
import json
from math import pi, sqrt
from pathlib import Path
import runpy

import numpy as np
from scipy.optimize import root

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
STATIC_CODE = PREFIX+"Code/03_Research/Research_T13_Hartree_Joint_Phi_Static.py"
POLE_CODE = PREFIX+"Code/03_Research/Research_T13_Hartree_Finite_Q_Poles.py"
STATIC_ARTIFACT = PREFIX+"Result/artifacts/t13_hartree_joint_phi_static.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_hartree_joint_phi_response.json")
S, Q = runpy.run_path(str(ROOT/STATIC_CODE)), runpy.run_path(str(ROOT/POLE_CODE))
F, G, R, D = (Q[name] for name in ("F", "G", "R", "D"))
Q_GRID = (.04, .02, .01)
ORDERS = ((64, 24), (96, 32), (128, 40))
SEEDS = (.2-.01j, .4-.005j)
UPPER_V = .3+.02j
EVEN = (0, 2)
ROOT_TOLERANCE = 1e-8
REFINEMENT_TOLERANCE = 2e-5
WARD_TOLERANCE = 1e-3
IDENTITY_TOLERANCE = 1e-10


def controls():
    action = S["action_controls"]()
    kinetic = S["natural_bridge_config"]().eos.response.response_kinetic
    return action | {"response_kinetic": kinetic}


def example_from_static(row):
    state = row["joint_state"]
    return {key: row[key] for key in ("T", "mu")} | {
        key: state[key] for key in ("s", "a", "b", "Phi")
    } | {"u_canonical": S["action_controls"]()["u"]}


def joint_vertices(s, action):
    S["validate_controls"](action)
    if action["response_kinetic"] <= 0:
        raise ValueError("positive declared response kinetic required")
    w, kernel, matter = F["source_vertices"](s, action["u"])
    mass = np.array([-sqrt(2)*action["gamma"], 0., 0.])
    return w, kernel, np.column_stack((matter, mass))


def joint_tree(q, z, example, action):
    F["validate"](example["T"], example["mu"], example["a"], example["b"], q, 0j)
    if not np.isfinite(z):
        raise ValueError("finite tree-polynomial frequency required; loops enforce their own domain")
    joint_vertices(example["s"], action)
    mu, s, a, b, phi = (example[name] for name in ("mu", "s", "a", "b", "Phi"))
    kinetic = action["epsilon"]*action["response_kinetic"]*(q*q-complex(z)**2)
    return np.array([[q*q+a-z*z, 2j*mu*z, -action["gamma"]*sqrt(s)],
                     [-2j*mu*z, q*q+b-z*z, 0.],
                     [-action["gamma"]*sqrt(s), 0., kinetic+S["response_curvature"](phi, action)]], complex)


def assemble(q, z, example, action, loops):
    _, kernel, vertices = joint_vertices(example["s"], action)
    bubble = np.asarray(loops["bubble"], complex)
    if bubble.shape != (3, 3) or np.any(~np.isfinite(bubble)):
        raise ValueError("finite three-channel covariance bubble required")
    covariance = np.eye(3)-kernel@bubble
    field = joint_tree(q, z, example, action)+.5*vertices.T@bubble@np.linalg.solve(covariance, vertices)
    mf, mr, aa = G["classical_vertices"](q, z, example["mu"], example["s"])
    forward, reverse = np.vstack((mf, np.zeros(4))), np.column_stack((mr, np.zeros(4)))
    forward += .5*vertices.T@np.linalg.solve(np.eye(3)-bubble@kernel, loops["mixed"])
    reverse += .5*loops["reverse"]@np.linalg.solve(covariance, vertices)
    aa += loops["loop_current"]+.5*loops["reverse"]@kernel@np.linalg.solve(np.eye(3)-bubble@kernel, loops["mixed"])
    even = field[np.ix_(EVEN, EVEN)]
    radial_current = aa-reverse[:, EVEN]@np.linalg.solve(even, forward[list(EVEN), :])
    phase = field[1, 1]-field[1, EVEN]@np.linalg.solve(even, field[list(EVEN), 1])
    qe = np.array([-1j*z, q, 0., 0.])
    return {"field": field, "forward": forward, "reverse": reverse, "aa": aa,
            "relaxed_current": radial_current, "phase_inverse": complex(phase),
            "phase_coefficient": complex(phase/q**2) if q else None,
            "phase_current_Ward_disagreement": float(abs(phase-qe@radial_current@qe/example["s"])/(q*q)) if q else None,
            "even_determinant": complex(np.linalg.det(even)),
            "even_min_singular_value": float(np.linalg.svd(even, compute_uv=False)[-1]),
            "covariance_determinant": complex(np.linalg.det(covariance)),
            "covariance_min_singular_value": float(np.linalg.svd(covariance, compute_uv=False)[-1]),
            "uneliminated_scaled_determinant": complex(np.linalg.det(covariance)*np.linalg.det(field)/(q*q)) if q else None}


def counterterm_response(q, z, example, action, loops, divergence, freeze_Phi=False):
    w, kernel, vertices = joint_vertices(example["s"], action)
    _, bare_kernel = S["CT"]["symmetric_tensor_projection"](action["u"], divergence)
    singlet = 1+4*action["u"]*divergence
    bare_gamma = action["gamma"] if freeze_Phi else action["gamma"]/singlet
    bare_vertices = np.column_stack((bare_kernel@w, [-sqrt(2)*bare_gamma, 0., 0.]))
    tree = joint_tree(q, z, example, action)
    tree[:2, :2] -= .5*w.T@(kernel-bare_kernel)@w
    tree[0, 2] = tree[2, 0] = -bare_gamma*sqrt(example["s"])
    if not freeze_Phi:
        tree[2, 2] -= S["normalization_jet"](example["Phi"], action, divergence, .11)["normalization_curvature"]
    bubble = loops["bubble"]+divergence*np.eye(3)
    covariance = np.eye(3)-bare_kernel@bubble
    field = tree+.5*bare_vertices.T@bubble@np.linalg.solve(covariance, bare_vertices)
    mf, mr, aa = G["classical_vertices"](q, z, example["mu"], example["s"])
    forward, reverse = np.vstack((mf, np.zeros(4))), np.column_stack((mr, np.zeros(4)))
    forward += .5*bare_vertices.T@np.linalg.solve(np.eye(3)-bubble@bare_kernel, loops["mixed"])
    reverse += .5*loops["reverse"]@np.linalg.solve(covariance, bare_vertices)
    aa += loops["loop_current"]+.5*loops["reverse"]@bare_kernel@np.linalg.solve(np.eye(3)-bubble@bare_kernel, loops["mixed"])
    finite = assemble(q, z, example, action, loops)
    return {"field": float(np.max(abs(field-finite["field"]))),
            "forward": float(np.max(abs(forward-finite["forward"]))),
            "reverse": float(np.max(abs(reverse-finite["reverse"]))),
            "aa": float(np.max(abs(aa-finite["aa"])))}


class JointKernel:
    def __init__(self, example, q, action=None, radial_order=64, angular_order=24, rays=Q["SPLIT_RAYS"]):
        self.example, self.q = example, q
        self.action = controls() if action is None else action
        self.kernel = Q["FiniteQKernel"](example, q, radial_order, angular_order, rays)

    def loops(self, v, sheet="retarded_local", contour="horizontal"):
        if sheet not in ("retarded_local", "principal_lower"):
            raise ValueError("declared retarded or principal sheet required")
        v = complex(v)
        loops = self.kernel.principal_loops(v)
        if v.imag < 0 and sheet == "retarded_local":
            density, _ = D["spectral_tail"](self.q, v, self.example, self.kernel.radial_order, contour)
            loops = {name: loops[name]-2j*pi*density[name] for name in loops}
        return loops

    def response(self, v, sheet="retarded_local", contour="horizontal"):
        return assemble(self.q, self.q*complex(v), self.example, self.action, self.loops(v, sheet, contour))

    def pole(self, seed):
        def equations(values):
            value = self.response(complex(*values))["phase_coefficient"]
            return [value.real, value.imag]
        answer = root(equations, [complex(seed).real, complex(seed).imag], tol=1e-9)
        pole = complex(*answer.x)
        residual = abs(self.response(pole)["phase_coefficient"])
        if not answer.success or residual > ROOT_TOLERANCE or pole.imag >= 0:
            raise RuntimeError("joint pole not established; no old-pole/width substitution")
        return pole, float(residual)


def static_response(row, action):
    e = example_from_static(row)
    mixed, reverse, aa = G["gauge_loops"](0., 0j, e["T"], e["mu"], e["a"], e["b"])
    bubble = F["direct_subtracted_bubble"](0., 0j, e["T"], e["mu"], e["a"], e["b"], radial_order=192)
    assembled = assemble(0., 0j, e, action, {"bubble": bubble, "mixed": mixed, "reverse": reverse, "loop_current": aa})
    expected = np.asarray(row["static_covariance_hessian"]["matrix"])
    difference = float(np.max(abs(assembled["field"][np.ix_(EVEN, EVEN)]-expected)))
    susceptibility = assembled["relaxed_current"][0, 0]
    clamped = assembled["aa"][0, 0]-assembled["reverse"][0, 0]*assembled["forward"][0, 0]/assembled["field"][0, 0]
    envelope = []
    for step in (2e-4, 1e-4, 5e-5):
        states = [S["joint_background"](e["T"], e["mu"]+sign*step, row["joint_state"], action) for sign in (-1, 0, 1)]
        actual = -(states[2]["potential"]+states[0]["potential"]-2*states[1]["potential"])/step**2
        envelope.append({"mu_step": step, "potential_envelope_susceptibility": actual,
                         "relative_disagreement": float(abs(actual/susceptibility-1))})
    return {"static_Hessian_disagreement": difference, "phase_Ward_inverse": float(abs(assembled["field"][1, 1])),
            "joint_charge_susceptibility": float(susceptibility.real), "charge_imaginary_residual": float(abs(susceptibility.imag)),
            "clamped_Phi_charge_susceptibility": float(clamped.real), "envelope_checks": envelope,
            "protocol": "T and action inputs fixed; matter and classical Phi reoptimized; not physical material susceptibility"}


def audit(progress=None):
    previous = json.loads((ROOT/STATIC_ARTIFACT).read_text(encoding="utf-8"))
    action = controls()
    examples = []
    for row in previous["examples"]:
        e = example_from_static(row)
        q_rows = []
        for q in Q_GRID:
            runs = []
            for nr, na in ORDERS:
                kernel = JointKernel(e, q, action, nr, na)
                pole, residual = kernel.pole(SEEDS[0])
                result = kernel.response(pole)
                runs.append({"radial_order": nr, "angular_order": na, "velocity_pole": F["complex_matrix"](np.asarray(pole)),
                             "frequency_pole": F["complex_matrix"](np.asarray(q*pole)), "inverse_residual": residual,
                             "phase_current_Ward_disagreement": result["phase_current_Ward_disagreement"],
                             "even_min_singular_value": result["even_min_singular_value"],
                             "even_determinant": F["complex_matrix"](np.asarray(result["even_determinant"])),
                             "covariance_min_singular_value": result["covariance_min_singular_value"],
                             "uneliminated_scaled_determinant_residual": float(abs(result["uneliminated_scaled_determinant"]))})
                if progress:
                    progress(f"mu={e['mu']}, q={q}, order={nr}/{na}: joint pole={pole}, residual={residual}")
                if (nr, na) != ORDERS[-1]:
                    del kernel
                    gc.collect()
            second = kernel.pole(SEEDS[1])[0]
            alternate = JointKernel(e, q, action, *ORDERS[-1], rays=Q["ALTERNATE_RAYS"])
            alternate_pole = alternate.pole(SEEDS[0])[0]
            del alternate
            gc.collect()
            loops = kernel.loops(pole)
            clamped = Q["response"](q, q*pole, e, loops)["phase_coefficient"]
            ct = [counterterm_response(q, q*pole, e, action, loops, probe) | {"D": probe} for probe in S["CT"]["D_PROBES"]]
            wrong = counterterm_response(q, q*pole, e, action, loops, .03, freeze_Phi=True)
            derivatives = Q["derivative_check"](kernel, pole)
            _, tail_checks = D["spectral_tail"](q, pole, e, ORDERS[-1][0])
            upper = kernel.loops(UPPER_V)
            independent = F["direct_subtracted_bubble"](q, q*UPPER_V, e["T"], e["mu"], e["a"], e["b"], radial_order=192, angular_order=96)
            absolute_field = assemble(q, q*UPPER_V, e, action, upper | {"bubble": independent})["field"]
            q_rows.append({"q": q, "pole_runs": runs,
                           "pole_refinements": [float(abs(G["unpack"](runs[i]["velocity_pole"])-G["unpack"](runs[i-1]["velocity_pole"]))) for i in (1, 2)],
                           "second_seed_disagreement": float(abs(second-pole)), "alternate_grid_disagreement": float(abs(alternate_pole-pole)),
                           "alternate_tail_inverse_residual": float(abs(kernel.response(pole, contour="return_to_real")["phase_coefficient"])),
                           "wrong_principal_sheet_residual": float(abs(kernel.response(pole, sheet="principal_lower")["phase_coefficient"])),
                           "clamped_Phi_inverse_at_joint_pole": F["complex_matrix"](np.asarray(clamped)),
                           "counterterm_checks": ct, "frozen_Phi_counterterm_negative_control": wrong,
                           "independent_upper_bubble_disagreement": float(np.max(abs(independent-upper["bubble"]))),
                           "independent_upper_joint_field_disagreement": float(np.max(abs(absolute_field-kernel.response(UPPER_V)["field"]))),
                           "local_derivative_check": derivatives, "local_tail_checks": tail_checks,
                           "joint_field_at_pole": F["complex_matrix"](result["field"])})
            del kernel
            gc.collect()
        examples.append(e | {"finite_q_runs": q_rows, "static_response": static_response(row, action)})
    rows = [q for e in examples for q in e["finite_q_runs"]]
    checks = {
        "joint_stationary_predecessor_is_preserved": previous["verification_status"] == "PASS_SCOPED_JOINT_PHI_STATIC" and all(previous["checks"].values()),
        "kinetic_from_same_declared_action": action["response_kinetic"] == S["natural_bridge_config"]().eos.response.response_kinetic,
        "static_joint_Hessian_and_Ward_recovered": all(e["static_response"]["static_Hessian_disagreement"] < REFINEMENT_TOLERANCE and e["static_response"]["phase_Ward_inverse"] < REFINEMENT_TOLERANCE for e in examples),
        "joint_charge_response_matches_reoptimized_potential": all(e["static_response"]["envelope_checks"][-1]["relative_disagreement"] < REFINEMENT_TOLERANCE and e["static_response"]["charge_imaginary_residual"] < IDENTITY_TOLERANCE for e in examples),
        "actual_joint_poles_without_old_answers": all(run["inverse_residual"] < ROOT_TOLERANCE and G["unpack"](run["velocity_pole"]).imag < 0 for q in rows for run in q["pole_runs"]),
        "orders_seeds_and_fixed_grids_agree": all(q["pole_refinements"][-1] < REFINEMENT_TOLERANCE and q["second_seed_disagreement"] < REFINEMENT_TOLERANCE and q["alternate_grid_disagreement"] < REFINEMENT_TOLERANCE for q in rows),
        "same_candidate_independent_absolute_upper_bubble": all(q["independent_upper_bubble_disagreement"] < REFINEMENT_TOLERANCE and q["independent_upper_joint_field_disagreement"] < REFINEMENT_TOLERANCE for q in rows),
        "neutral_Phi_phase_current_Ward": all(run["phase_current_Ward_disagreement"] < WARD_TOLERANCE for q in rows for run in q["pole_runs"]),
        "elimination_denominators_and_full_determinant": all(run["even_min_singular_value"] > .01 and run["covariance_min_singular_value"] > .01 and run["uneliminated_scaled_determinant_residual"] < ROOT_TOLERANCE for q in rows for run in q["pole_runs"]),
        "joint_dynamic_counterterm_cancellation": all(abs(ct[name]) < IDENTITY_TOLERANCE for q in rows for ct in q["counterterm_checks"] for name in ("field", "forward", "reverse", "aa")),
        "frozen_Phi_counterterm_and_clamped_answer_rejected": all(max(q["frozen_Phi_counterterm_negative_control"].values()) > 1e-5 and abs(G["unpack"](q["clamped_Phi_inverse_at_joint_pole"])) > 1e-5 for q in rows),
        "correct_local_sheet_and_tail": all(q["wrong_principal_sheet_residual"] > 1e-4 and q["alternate_tail_inverse_residual"] < ROOT_TOLERANCE for q in rows),
        "simple_local_analytic_poles": all(q["local_derivative_check"]["derivative_modulus"] > .01 and q["local_derivative_check"]["runs"][-1]["Cauchy_Riemann_disagreement"] < 2e-5 for q in rows),
        "protected_Core_and_baseline_hashes_unchanged": all(hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"] for item in previous["protected_evidence_hashes"]),
    }
    passed = all(checks.values())
    paths = list(dict.fromkeys([STATIC_ARTIFACT, STATIC_CODE, POLE_CODE, Q["PREVIOUS_CODE"], G["FIELD_CODE"], PREFIX+"Code/03_Research/Research_T13_Hartree_Gauge_Current.py", *S["ACTION_PATHS"], Path(__file__).relative_to(ROOT).as_posix()]))
    record = {"schema_version": "t13-joint-classical-phi-response-v1", "generated_at": datetime.now(timezone.utc).isoformat(),
              "major_result_id": "T13_CLASSICAL_PHI_HARTREE_JOINT_RETARDED_RESPONSE", "topic": "0.13",
              "branch_id": previous["branch_id"], "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
              "verification_status": "PASS_SCOPED_JOINT_PHI_RESPONSE" if passed else "FAIL_JOINT_PHI_RESPONSE",
              "what_is_closed": ["same_action_classical_Phi_kinetic_and_mass_source_retarded_response", "joint_source_quadratic_counterterm_identity", "six_computed_local_joint_phase_poles", "joint_charge_static_envelope_check"],
              "equation_or_mapping": "Gamma_joint=Gamma_tree+L^T*J*(I-KJ)^-1*L/2; Gamma_PhiPhi_tree=epsilon*Z_Phi*(q^2-z^2)+V_R''; L_Phi=(-sqrt(2)*gamma,0,0); Gamma_phase=Gamma_pp-Gamma_pE*Gamma_EE^-1*Gamma_Ep, E=(radial,Phi)",
              "units": {"Phi_v_A_T_mu_q_z_gamma": "E", "s_a_b_Gamma_current_charge_susceptibility": "E^2", "K_J_D_epsilon_Z_Phi_u": "dimensionless", "phase_coefficient_velocity": "dimensionless", "uneliminated_scaled_determinant": "E^4"},
              "derivation_class": "CLASSICAL_RESPONSE_FIELD_WITH_HARTREE_MATTER_EXTERNAL_SOURCE_DERIVATION_NOT_FULL_QUANTUM_JOINT_ACTION",
              "observable": "conditional_joint_source_response_and_phase_poles_not_material_temperature_heat_or_collision_transport", "data_role": "DERIVED_NO_EMPIRICAL_ROWS",
              "equation_registry_ids": ["t13.diagnostic.classical_Phi_hartree_joint_retarded", "t13.diagnostic.joint_Phi_quadratic_counterterm", "t13.diagnostic.joint_Phi_charge_envelope"],
              "action_controls": action, "examples": examples, "checks": checks,
              "config": {"q_grid": Q_GRID, "orders": ORDERS, "seeds": [[z.real, z.imag] for z in SEEDS], "upper_reference_velocity": [UPPER_V.real, UPPER_V.imag], "local_continuation_domain": D["LOCAL_DOMAIN"], "MS_scale": 1., "gauge_contact_convention": "inherited_frequency_first_MS_contact_not_material_input"},
              "thresholds": {"scaled_root": ROOT_TOLERANCE, "refinement_and_independent_check": REFINEMENT_TOLERANCE, "phase_current_Ward": WARD_TOLERANCE, "algebra_identity": IDENTITY_TOLERANCE, "causal_leakage_unchanged": 1e-6},
              "evidence_artifacts": [{"path": path, "sha256": hashlib.sha256((ROOT/path).read_bytes()).hexdigest()} for path in paths],
              "protected_evidence_hashes": previous["protected_evidence_hashes"],
              "open_blockers": ["global_validity_domain_and_regulator_RG_Hartree_remainder", "quantum_Phi_and_kinetic_counterterms_if_required", "independent_material_state_source_detector_thermal_mapping", "physical_heat_collision_Kubo_SK_KMS_entropy_transport"],
              "controlling_blocker": "joint_global_validity_Hartree_remainder_material_thermal_transport_not_closed",
              "dependency_unlocked": ["named_classical_Phi_candidate_validity_and_material_input_research_only"] if passed else [],
              "joint_finite_q_complex_pole_computed": bool(passed), "joint_classical_Phi_retarded_response_computed": bool(passed),
              "prior_fixed_Phi_poles_reused_as_joint": False, "homogeneous_classical_Phi_stationarity_derived": True,
              "full_quantum_joint_Phi_stationarity_derived": False, "full_frequency_joint_spectrum_classified": False,
              "global_phase_minimum_proved": False, "controlled_truncation_error_established": False,
              "full_covariant_counterterm_match": False, "RG_invariance_established": False,
              "physical_Kubo_emitted": False, "collision_rate_emitted": False, "independent_alpha_Phi_K_admitted": False,
              "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False, "core_composition_gate_overwritten": False,
              "claim_promotion": False, "parameter_fitting": False, "assigned_width": False, "mass_repair": False, "clipping": False, "IR_filter": False,
              "target_source_accessed": False, "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
              "state_variables": ["same_O2_mean_field_and_covariance", "existing_classical_UET_Phi"], "excluded_variables": ["R_gen", "R_obs", "nondynamical_A"],
              "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False,
              "claim_boundary": "Same-action classical-Phi response in one Hartree prescription at two stationary states and six local q points. Not quantum Phi loops, full-frequency/global spectrum or causal domain proof, controlled Hartree remainder/RG, physical material/temperature/heat/collision/Kubo/KMS/entropy, external validation or Full Topic13/UET."}
    names = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    values = (record["major_result_id"]+": "+record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"],
              "Computed the same-action joint response, new poles and relaxed static charge susceptibility; formal quadratic counterterms checked without retuning.", record["equation_or_mapping"], checks, record["controlling_blocker"],
              "Control the joint candidate validity/regulator/approximation and independently identify material/thermal/source/readout inputs; do not repeat unchanged local roots.", record["claim_boundary"])
    record["report"] = dict(zip(names, values))
    return record


if __name__ == "__main__":
    result = audit(progress=lambda message: print(message, flush=True))
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"]}, indent=2), flush=True)
