"""Off-shell acoustic Landau/source kernel and conditional energy-flux bound.

Finite thermal quadratures remain diagnostics, not full real/contact matching.
The unit-front-speed bound requires positive K and semidefinite V0 of this
declared quadratic parent; it is not a repair of the old conserved-C branch.
"""

from datetime import datetime, timezone
import json
from math import isfinite, pi, sqrt
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[5]
LOCAL = Path(__file__).resolve().parent
if str(LOCAL) not in sys.path:
    sys.path.insert(0, str(LOCAL))
import Research_T13_Acoustic_Source_Pair as PAIR

MOD, TH, EFT, INT, PREFIX = PAIR.MOD, PAIR.TH, PAIR.EFT, PAIR.INT, PAIR.PREFIX
REGISTRY = PREFIX+"Data/03_Research/t13_acoustic_source_Landau_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_acoustic_source_Landau.json")
MU_GRID, Q_GRID, FREQUENCY_RATIOS = (1.05, 1.2), (.04, .02), (.5, .9, 1.001)
TEMPERATURE_DIVISORS, ORDERS, TAILS = (256, 512), (24, 48, 96), (32., 40.)
GATES = {"identity_relative": 1e-9, "velocity_FD_relative": 1e-6,
         "modal_projection_relative": 1e-6, "quadrature_relative": 1e-6,
         "tail_relative": 1e-8, "original_causal_leakage": 1e-6}


def parent_mass_matrix(state, action):
    s, g = state["s"], action["gamma"]
    return np.array([[2*action["u"]*s, 0., -g*sqrt(s)],
                     [0., 0., 0.], [-g*sqrt(s), 0., state["V_curvature"]]])


def flux_bound(p, state, action):
    mode = MOD.mode(p, state, action)
    u, energy = mode["polarization"], mode["omega"]
    k = np.diag([1., 1., action["epsilon"]*action["response_kinetic"]])
    v0 = parent_mass_matrix(state, action)
    if min(np.diag(k)) <= 0 or state["V_curvature"] <= 0 or 2*action["u"]*state["V_curvature"]-action["gamma"]**2 <= 0:
        raise ValueError("positive kinetic and semidefinite V0 contract required")
    kinetic = float(np.vdot(u, k@u).real)
    mass = float(np.vdot(u, v0@u).real)
    h = (energy*energy+p*p)*kinetic+mass
    flux = 2*energy*p*kinetic
    velocity = flux/h
    step = p*1e-4
    finite_difference = (TH.energy_value(p+step, state, action)-TH.energy_value(p-step, state, action))/(2*step)
    return {"p": p, "v_flux": velocity, "v_implicit": INT.group_velocity(p, state, action),
            "velocity_identity_error": INT.relative(velocity, INT.group_velocity(p, state, action)),
            "velocity_FD_error": INT.relative(velocity, finite_difference),
            "mass_form": mass, "energy_minus_flux_identity_error": abs((h-flux)-((energy-p)**2*kinetic+mass))/h,
            "positive_energy": h, "front_speed_margin": 1-velocity,
            "energy_over_sound_bound": energy/(INT.dispersion_coefficients(state, action)["c"]*p)}


def support_start(q, omega, state, action, on_shell=False):
    TH.validate(q, 0., state, action, 2)
    if not isfinite(omega) or omega <= 0:
        raise ValueError("positive finite frequency required")
    flux_bound(q, state, action)
    if omega >= q:
        return {"status": "NO_LANDAU_SUPPORT_CONDITIONAL_UNIT_FRONT_SPEED_BOUND", "p_min": None}
    energy = TH.energy_value(q, state, action)
    c = INT.dispersion_coefficients(state, action)["c"]
    if on_shell:
        if INT.relative(omega, energy) > GATES["identity_relative"]:
            raise ValueError("on-shell flag disagrees with original tree root")
        return {"status": "SUPPORTED", "p_min": 0.}
    if omega == energy:
        raise ValueError("use explicit on-shell control, not source dressing at its pole")
    if omega < energy:
        pmin = brentq(lambda p: TH.energy_value(q-p, state, action)-TH.energy_value(p, state, action)-omega,
                      0., q/2, xtol=1e-14, rtol=1e-13)
        branch = "LOWER_ANGULAR_ENDPOINT"
    else:
        offset = omega-c*q
        def boundary(p):
            return TH.energy_split(p+q, state, action)[1]-TH.energy_split(p, state, action)[1]-offset
        maximum = INT.dispersion_coefficients(state, action)["dispersion_scale"]/2
        if boundary(maximum) <= 0:
            return {"status": "SUPPORT_NOT_RESOLVED_WITHIN_DECLARED_MOMENTUM_DOMAIN", "p_min": None}
        pmin = brentq(boundary, 0., maximum, xtol=1e-14, rtol=1e-13)
        branch = "UPPER_ANGULAR_ENDPOINT"
    return {"status": "SUPPORTED", "p_min": pmin, "endpoint": branch}


def landau_root(q, p, omega, state, action):
    c = INT.dispersion_coefficients(state, action)["c"]
    dp = TH.energy_split(p, state, action)[1]
    offset = omega-c*q
    lower = (abs(p-q)-p)/q
    z = brentq(lambda z: c*(z-1)+(TH.energy_split(p+q*z, state, action)[1]-dp-offset)/q,
               lower, 1., xtol=1e-13, rtol=1e-13)
    r = p+q*z
    cosine = (r*r-p*p-q*q)/(2*p*q)
    if not -1 < cosine < 1:
        raise ValueError("strict Landau angular support required; no clipping")
    return r, cosine


def angular_root(q, p, omega, state, action):
    ep = TH.energy_value(p, state, action)
    cosine = brentq(lambda x: TH.energy_value(sqrt((p-q)**2+2*p*q*(x+1)), state, action)-ep-omega,
                    -1., 1., xtol=1e-13, rtol=1e-13)
    return sqrt((p-q)**2+2*p*q*(cosine+1)), cosine


def landau_vector(p, r, state, action):
    up = MOD.mode(p, state, action, -1)["polarization"]
    ur = MOD.mode(r, state, action)["polarization"]
    return np.einsum("ijk,j,k->i", MOD.cubic_tensor(state, action), up, ur)


def landau_matrix(q, omega, temperature, state, action, order=48, tail=40., on_shell=False, angular=False):
    TH.validate(q, temperature, state, action, order)
    if not isfinite(tail) or tail <= 16:
        raise ValueError("declared thermal tail >16 required")
    support = support_start(q, omega, state, action, on_shell)
    if support["status"] != "SUPPORTED":
        return {"support": support, "matrix": None, "source_spectral_response": None}
    if temperature == 0:
        return {"support": support, "matrix": np.zeros((3, 3), complex), "source_spectral_response": 0., "zero_T_limit": True}
    c = INT.dispersion_coefficients(state, action)["c"]
    matrix, projected, source = np.zeros((3, 3), complex), 0., 0.
    unit = MOD.mode(q, state, action)["polarization"]
    dressed = None if on_shell else np.linalg.solve(MOD.kernel(q, omega, state, action), np.array([0., 0., 1.]))
    samples, margins, balances, bose_errors = [], [], [], []
    pmin = support["p_min"]
    for x, weight in TH.radial_nodes(order, tail):
        p = pmin+temperature*x/c
        root = angular_root if angular else landau_root
        r, cosine = root(q, p, omega, state, action)
        ep, er = TH.energy_value(p, state, action), TH.energy_value(r, state, action)
        thermal = TH.thermal_weights(ep, er, omega, temperature, "Landau")
        if thermal["difference"] <= 0:
            raise ValueError("underflow/nonpositive thermal weight is unresolved, not absent support")
        vector = landau_vector(p, r, state, action)
        measure = weight*temperature/c*p*r*thermal["difference"]/(ep*er*INT.group_velocity(r, state, action))/(16*pi*q)
        matrix += measure*np.outer(vector, vector.conjugate())
        projected += measure*abs(np.vdot(unit, vector))**2
        if dressed is not None:
            source += measure*abs(np.vdot(dressed, vector))**2
        samples.append((measure, vector))
        margins.append(1-abs(cosine))
        balances.append(abs(er-ep-omega)/omega)
        bose_errors.append(max(thermal["KMS_ratio_error"], thermal["FDT_error"]))
    return {"support": support, "matrix": matrix, "modal_projection": float(projected),
            "source_spectral_response": None if on_shell else float(source),
            "decimal_gram_source": None if on_shell else PAIR.decimal_gram_source(samples, dressed),
            "support_margin": min(margins), "energy_residual": max(balances),
            "Bose_identity_error": max(bose_errors), "thermal_tail": tail,
            "p_max": pmin+temperature*tail/c, "finite_tail_is_total_error_bound": False}


def audit():
    action, examples = EFT.controls(), []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        cf = INT.dispersion_coefficients(state, action)
        rows, controls, flux_rows = [], [], []
        for q in Q_GRID:
            energy = TH.energy_value(q, state, action)
            flux_rows.append(flux_bound(q, state, action))
            for divisor in TEMPERATURE_DIVISORS:
                temperature = cf["c"]*cf["dispersion_scale"]/divisor
                control = landau_matrix(q, energy, temperature, state, action, ORDERS[-1], on_shell=True)
                reference = 2*energy*MOD.cut_rate(q, temperature, state, action, "Landau", ORDERS[-1])["gamma_pole"]
                controls.append({"q": q, "T": temperature, "modal_projection_error": INT.relative(control["modal_projection"], reference)})
                for ratio in FREQUENCY_RATIOS:
                    omega = ratio*energy
                    runs = [landau_matrix(q, omega, temperature, state, action, order) for order in ORDERS]
                    if any(x["support"]["status"] != "SUPPORTED" for x in runs):
                        raise ValueError("declared diagnostic grid must resolve support, not silently return zero")
                    item = runs[-1]
                    independent = landau_matrix(q, omega, temperature, state, action, ORDERS[-1], angular=True)
                    short = landau_matrix(q, omega, temperature, state, action, ORDERS[-1], TAILS[0])
                    matrix, response = item["matrix"], item["source_spectral_response"]
                    eig = np.linalg.eigvalsh(matrix)
                    chi = PAIR.source_schur(q, omega, state, action)
                    if omega < cf["c"]*q:
                        pair_response = 0.
                        pair_status = "NO_PAIR_SUPPORT_CONDITIONAL_Ep_GE_cp_BOUND"
                    elif omega > energy:
                        pair_result = PAIR.pair_matrix(q, omega, temperature, state, action, ORDERS[-1])
                        pair_response = pair_result["source_spectral_response"]
                        pair_status = "PAIR_SUPPORT_EVALUATED_ABOVE_Eq"
                    else:
                        raise ValueError("gap between cq and Eq needs explicit pair-threshold analysis, not an assumed zero")
                    rows.append({"q": q, "omega": omega, "omega_over_Eq": ratio, "T": temperature,
                                 "support": item["support"], "p_max": item["p_max"],
                                 "source_spectral_response": response, "Landau_inverse_spectral_units": "E^2",
                                 "pair_source_response": pair_response, "pair_support_status": pair_status,
                                 "combined_pair_Landau_source_response": response+pair_response,
                                 "combined_window_is_full_retarded_response": False,
                                 "Landau_spectral_matrix": PAIR.matrix_record(matrix),
                                 "scaled_min_eigenvalue": float(eig[0]/max(eig[-1], 1e-30)),
                                 "hermitian_error": float(np.max(abs(matrix-matrix.conjugate().T))/np.max(abs(matrix))),
                                 "source_gram_error": INT.relative(item["decimal_gram_source"], response),
                                 "quadrature_error": INT.relative(runs[-2]["source_spectral_response"], response),
                                 "tail_error": INT.relative(short["source_spectral_response"], response),
                                 "angular_root_method_error": INT.relative(independent["source_spectral_response"], response),
                                 "support_margin": item["support_margin"], "energy_residual": item["energy_residual"],
                                 "Bose_identity_error": item["Bose_identity_error"],
                                 "imaginary_source_correction_over_tree": response/abs(chi),
                                 "correction_ratio_is_not_full_perturbative_control": True})
                    flux_rows.append(flux_bound(item["p_max"], state, action))
        examples.append({"mu": mu, "flux_checks": flux_rows, "modal_controls": controls, "off_shell_Landau_rows": rows,
                         "outside_front_support": [support_start(.02, omega, state, action) for omega in (.02, .04)]})
    checks = {
        "conditional_positive_energy_flux_identity": all(max(x["velocity_identity_error"], x["energy_minus_flux_identity_error"]) < GATES["identity_relative"] and x["positive_energy"] > 0 and x["mass_form"] >= 0 and x["front_speed_margin"] > 0 for e in examples for x in e["flux_checks"]),
        "group_velocity_independent_FD": all(x["velocity_FD_error"] < GATES["velocity_FD_relative"] for e in examples for x in e["flux_checks"]),
        "on_shell_Landau_projects_to_prior_modal_rate": all(x["modal_projection_error"] < GATES["modal_projection_relative"] for e in examples for x in e["modal_controls"]),
        "positive_hermitian_Landau_kernel_source": all(x["scaled_min_eigenvalue"] >= -GATES["identity_relative"] and x["hermitian_error"] < GATES["identity_relative"] and x["source_spectral_response"] > 0 for e in examples for x in e["off_shell_Landau_rows"]),
        "source_gram_energy_Bose_and_strict_support": all(max(x["source_gram_error"], x["energy_residual"], x["Bose_identity_error"]) < GATES["identity_relative"] and x["support_margin"] > 0 for e in examples for x in e["off_shell_Landau_rows"]),
        "quadrature_tail_and_independent_angular_root": all(x["quadrature_error"] < GATES["quadrature_relative"] and x["tail_error"] < GATES["tail_relative"] and x["angular_root_method_error"] < GATES["identity_relative"] for e in examples for x in e["off_shell_Landau_rows"]),
        "outside_front_support_has_structural_reason": all(x["status"] == "NO_LANDAU_SUPPORT_CONDITIONAL_UNIT_FRONT_SPEED_BOUND" for e in examples for x in e["outside_front_support"])}
    checks["conditional_sound_bound_and_combined_cut_window"] = all(x["energy_over_sound_bound"] >= 1 for e in examples for x in e["flux_checks"]) and all(x["pair_source_response"] >= 0 and x["combined_pair_Landau_source_response"] >= x["source_spectral_response"] and not x["combined_window_is_full_retarded_response"] for e in examples for x in e["off_shell_Landau_rows"])
    paths = [str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), REGISTRY, PREFIX+"Code/03_Research/test_t13_acoustic_source_Landau.py"]
    protected = [PREFIX+"Result/artifacts/t13_acoustic_source_pair.json", PREFIX+"Code/03_Research/Research_T13_Acoustic_Source_Pair.py",
                 PREFIX+"Result/artifacts/t13_acoustic_modal_cuts.json"]+list(EFT.ACTION_PATHS)
    record = {"major_result_id": "T13_ACOUSTIC_OFF_SHELL_LANDAU_SOURCE_AND_FLUX_BOUND", "topic": "0.13_Thermodynamic_Bridge",
              "branch_id": EFT.BRANCH, "created_at": datetime.now(timezone.utc).isoformat(),
              "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
              "verification_status": "PASS_SCOPED_LANDAU_SOURCE_INTERFACE" if all(checks.values()) else "FAIL_SCOPED_LANDAU_SOURCE_INTERFACE",
              "what_is_closed": "Conditional positive-energy tree group/sound support bounds and declared off-shell acoustic Landau/pair source spectral window with modal projection",
              "equation_or_mapping": "H-F=(E-p)^2 udagger K u+udagger V0 u>=0; R_L=integral V_L V_Ldagger (np-nr)/(16pi q); Im delta_chi_hh=d_hdagger R_L d_h",
              "units": {"q_omega_T_h": "E/E/E/E^3", "Phi": "E", "R_L": "E^2", "source_chi": "E^-2", "group_velocity_front_speed": "1"},
              "derivation_class": "TREE_ENERGY_FLUX_IDENTITY_AND_OFF_SHELL_ACOUSTIC_LANDAU_CUT",
              "observable": "Conditional source absorption, not physical heat/Kubo or Kelvin calibration", "data_role": "DERIVED_NOT_CALIBRATION",
              "equation_registry_ids": [x["id"] for x in json.loads((ROOT/REGISTRY).read_text())["entries"]],
              "action_controls": action, "checks": checks, "examples": examples, "thresholds": GATES,
              "declared_grids": {"mu": MU_GRID, "q": Q_GRID, "omega_over_Eq": FREQUENCY_RATIOS,
                                 "T_divisors": TEMPERATURE_DIVISORS, "orders": ORDERS, "thermal_tails": TAILS, "locked_before_first_audit": True},
              "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected),
              "controlling_blocker": "local_real_source_contact_and_complete_thermal_sunset_matching_open",
              "open_blockers": ["principal_value_finite_local_real_and_complete_source_contact_matching", "all_mode_quantum_heavy_and_complete_thermal_sunset_pressure", "physical_material_readout_scale_transport_and_total_uncertainty"],
              "dependency_unlocked": ["dispersive_and_source_matching_research_only"],
              "full_off_shell_source_matching_closed": False, "full_real_self_energy_matched": False,
              "full_two_loop_pressure_computed": False, "all_parent_modes_and_quantum_Phi_loops_included": False,
              "full_SK_KMS_matching_closed": False, "physical_Kubo_emitted": False, "independent_alpha_Phi_K_admitted": False,
              "finite_thermal_tail_is_total_error_bound": False, "controlled_full_action_truncation_error_established": False,
              "full_core_unlock": False, "core_composition_gate_overwritten": False, "claim_promotion": False,
              "parameter_fitting": False, "assigned_width": False, "clipping": False, "cone_padding": False,
              "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
              "primary_references": ["https://arxiv.org/abs/cond-mat/9708104"],
              "claim_boundary": "Declared acoustic Landau/source quadrature and conditional quadratic-parent energy-flux support only. Not full retarded/contact/local real response, all-mode loops, interacting EOS, physical transport/calibration/causal closure or global UET; original conserved-C and owner Core unchanged."}
    fields = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(fields, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Derived Landau/source support and quadratic energy-flux boundary", record["equation_or_mapping"], checks, record["controlling_blocker"], "Derive dispersive/local/source contact matching and complete thermal consistency", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    record = audit()
    OUTPUT.write_bytes((json.dumps(record, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": record["verification_status"], "checks": record["checks"]}, indent=2))
    raise SystemExit(0 if all(record["checks"].values()) else 1)
