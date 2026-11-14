"""Finite-T phase cuts with tree internal curvature and static LO coherence.

This is a leading-vertex cut diagnostic, not the complete curved parent
self-energy. Static LO diagrams use the linear propagator consistently;
the near-shell cut uses tree curvature to resolve otherwise singular support.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from math import isfinite, pi
from pathlib import Path
import sys

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[5]
LOCAL = Path(__file__).resolve().parent
if str(LOCAL) not in sys.path:
    sys.path.insert(0, str(LOCAL))
import Research_T13_Low_T_Interactions as INT

EFT, PREFIX = INT.EFT, INT.PREFIX
REGISTRY = PREFIX+"Data/03_Research/t13_thermal_cut_stiffness_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_thermal_cut_stiffness.json")
MU_GRID = (1.05, 1.2)
TEMPERATURE_DIVISORS = (128, 256, 512)
SOFT_RATIOS = (.1, .05, .025)
ORDERS = (24, 48, 96)
TAILS = (24., 32., 40.)
FD_STEPS = (.0004, .0002, .0001)
GATES = {"identity_relative": 1e-9, "quadrature_relative": 1e-6,
         "tail_relative": 1e-8, "soft_limit_relative": .005,
         "static_derivative_relative": 2e-5, "original_causal_leakage": 1e-6}


def validate(k, temperature, state, action, order):
    EFT.validate(action)
    if not all(isfinite(x) for x in (k, temperature)) or k <= 0 or temperature < 0:
        raise ValueError("positive momentum and nonnegative natural temperature required")
    if not isinstance(order, int) or isinstance(order, bool) or order < 2:
        raise ValueError("integer quadrature order >=2 required")
    if state["xi"] != 0 or INT.dispersion_coefficients(state, action)["eta"] <= 0:
        raise ValueError("convex rest-frame tree branch required")


def bose(y):
    if not isfinite(y) or y <= 0:
        raise ValueError("positive finite Bose argument required")
    return float(np.exp(-y)/(-np.expm1(-y)))


def thermal_weights(ep, er, ek, temperature, channel):
    if channel not in ("pair", "Landau") or min(ep, er, ek) <= 0:
        raise ValueError("positive energies and declared cut channel required")
    if not all(isfinite(x) for x in (ep, er, ek, temperature)) or temperature < 0:
        raise ValueError("finite nonnegative temperature required")
    if temperature == 0:
        return {"difference": float(channel == "pair"), "KMS_ratio_error": 0.,
                "FDT_error": 0., "zero_T_limit": True}
    np_, nr = bose(ep/temperature), bose(er/temperature)
    if channel == "pair":
        greater, lesser = (1+np_)*(1+nr), np_*nr
        difference = 1+np_+nr
    else:
        greater, lesser = np_*(1+nr), (1+np_)*nr
        difference = np_-nr
    # exp(-Ek/T), rather than exp(+Ek/T), is safe also for the T->0 test.
    ratio_error = abs(lesser-greater*np.exp(-ek/temperature))/max(greater, 1e-300)
    expected_fdt = 1/np.tanh(ek/(2*temperature))
    fdt_error = INT.relative((greater+lesser)/difference, expected_fdt) if difference > 0 else 0.
    return {"difference": difference, "KMS_ratio_error": ratio_error,
            "FDT_error": fdt_error, "zero_T_limit": False}


def vertex(ek, ep_signed, er, k, p, cosine, vv):
    kp = k*p*cosine
    return 6*vv["g_t"]*ek*ep_signed*er+2*vv["g_s"]*(
        ek*(kp-p*p)+ep_signed*(k*k-kp)+er*kp)


def energy_split(q, state, action):
    """Same tree root as c*q + curvature, without subtracting two sound speeds."""
    if not isfinite(q) or q < 0 or state["xi"] != 0:
        raise ValueError("nonnegative rest-frame momentum required")
    cf = INT.dispersion_coefficients(state, action)
    c, a0, mu2 = cf["c"], cf["A0"], state["mu"]**2
    kp, v = action["epsilon"]*action["response_kinetic"], state["V_curvature"]
    d = 2*c*cf["eta"]
    for _ in range(64):
        t = c*c+q*q*d
        ell = q*q*(1-t)
        h = 1+action["gamma"]**2*state["s"]*kp/(v*(v+kp*ell))
        updated = 4*mu2*(1-t)*h/((a0+ell*h+4*mu2)*(a0+4*mu2))
        if abs(updated-d) <= 2e-15*max(abs(updated), 1e-30):
            d = updated
            break
        d = updated
    else:
        raise ValueError("tree curvature fixed point did not converge")
    t = c*c+q*q*d
    if not c*c <= t < 1:
        raise ValueError("tree root outside convex acoustic branch")
    return c*q, q**3*d/(np.sqrt(t)+c)


def energy_value(q, state, action):
    return sum(energy_split(q, state, action))


def pair_rate(k, temperature, state, action, order=48, vv=None):
    validate(k, temperature, state, action, order)
    vv = INT.vertices(state, action) if vv is None else vv
    ek = energy_value(k, state, action)
    c, curvature_k = INT.dispersion_coefficients(state, action)["c"], energy_split(k, state, action)[1]
    nodes, weights = np.polynomial.legendre.leggauss(order)
    integral, margins, energy, balance = 0., [], [], []
    for node, weight in zip(nodes, weights):
        p = k*(node+1)/2
        ep = energy_value(p, state, action)
        curvature_p = energy_split(p, state, action)[1]
        displacement_scale = k*p*(k-p)
        def residual(a):
            displacement = displacement_scale*a
            r = k-p+displacement
            return (curvature_k-curvature_p-energy_split(r, state, action)[1])/displacement_scale-c*a
        a = brentq(residual, 0., 2*p/displacement_scale, xtol=1e-13, rtol=1e-13)
        displacement = displacement_scale*a
        r = k-p+displacement
        er = energy_value(r, state, action)
        cosine = 1-displacement*(2*(k-p)+displacement)/(2*k*p)
        if not -1 < cosine < 1:
            raise ValueError("pair energy root outside support; no clipping")
        thermal = thermal_weights(ep, er, ek, temperature, "pair")
        vv2 = vertex(ek, ep, er, k, p, cosine, vv)**2
        integral += weight*k/2*p*r/(ep*er*INT.group_velocity(r, state, action))*vv2*thermal["difference"]
        margins.append(1-abs(cosine))
        energy.append(abs(ek-ep-er)/ek)
        balance.append(max(thermal["KMS_ratio_error"], thermal["FDT_error"]))
    gamma = integral/(64*pi*ek*k)
    return {"gamma_pole": gamma, "Gamma_occupation": 2*gamma,
            "angular_support_margin_min": min(margins),
            "energy_balance_relative_max": max(energy), "Bose_identity_error_max": max(balance)}


def landau_root(k, p, state, action):
    if not all(isfinite(x) and x > 0 for x in (k, p)):
        raise ValueError("positive finite momenta required")
    ek, ep = (energy_value(x, state, action) for x in (k, p))
    c = INT.dispersion_coefficients(state, action)["c"]
    curvature_k, curvature_p = (energy_split(x, state, action)[1] for x in (k, p))
    # Solve for the bounded displacement; do not lose the small k to an r tolerance.
    x = brentq(lambda z: c*(z-1)+(energy_split(p+k*z, state, action)[1]-curvature_p-curvature_k)/k,
               0., 1., xtol=1e-13, rtol=1e-13)
    r = p+k*x
    er = energy_value(r, state, action)
    cosine = k*(1-x*x)/(2*p)-x
    if not -1 < cosine < 1:
        raise ValueError("Landau energy root outside support; no clipping")
    return r, ep, er, cosine, abs(ek+ep-er)/ek


def radial_nodes(order, tail):
    if not isfinite(tail) or tail <= 16:
        raise ValueError("finite scaled thermal tail >16 required")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    edges = (0., 1., 4., 8., 16., tail)
    for left, right in zip(edges[:-1], edges[1:]):
        for node, weight in zip(nodes, weights):
            yield (left+right+(right-left)*node)/2, weight*(right-left)/2


def landau_rate(k, temperature, state, action, order=48, tail=40., vv=None):
    validate(k, temperature, state, action, order)
    if not isfinite(tail) or tail <= 16:
        raise ValueError("finite scaled thermal tail >16 required")
    if temperature == 0:
        return {"gamma_pole": 0., "Gamma_occupation": 0., "zero_T_limit": True}
    cf = INT.dispersion_coefficients(state, action)
    vv = INT.vertices(state, action) if vv is None else vv
    c, ek = cf["c"], EFT.acoustic_energy(k, state, action)
    integral, margins, energy, balance, velocities = 0., [], [], [], []
    for x, weight in radial_nodes(order, tail):
        p = temperature*x/c
        r, ep, er, cosine, residual = landau_root(k, p, state, action)
        thermal = thermal_weights(ep, er, ek, temperature, "Landau")
        if thermal["difference"] <= 0:
            raise ValueError("positive-frequency Landau thermal weight must be positive")
        vr = INT.group_velocity(r, state, action)
        vv2 = vertex(ek, -ep, er, k, p, cosine, vv)**2
        integral += weight*temperature/c*p*r/(ep*er*vr)*vv2*thermal["difference"]
        margins.append(1-abs(cosine))
        velocities.append(vr)
        energy.append(residual)
        balance.append(max(thermal["KMS_ratio_error"], thermal["FDT_error"]))
    gamma = integral/(32*pi*ek*k)
    return {"gamma_pole": gamma, "Gamma_occupation": 2*gamma,
            "angular_support_margin_min": min(margins), "group_velocity_min": min(velocities),
            "energy_balance_relative_max": max(energy), "Bose_identity_error_max": max(balance),
            "scaled_radial_tail": tail, "radial_p_max_over_dispersion_scale": temperature*tail/(c*cf["dispersion_scale"]),
            "thermal_tail_is_total_EFT_error": False}


def soft_landau_coefficient(c, vv):
    return 3*pi**3*(vv["g_t"]+vv["g_s"]/c**2)**2/(10*c**2)


def soft_landau_moment(c, vv):
    moment = quad(lambda x: x**4*np.exp(-x)/(-np.expm1(-x))**2,
                  0., np.inf, epsabs=1e-10, epsrel=1e-11)[0]
    return 9*(vv["g_t"]+vv["g_s"]/c**2)**2*moment/(8*pi*c**2)


def static_coefficients(c, vv):
    j4 = pi*pi/(30*c**3)
    bubble = -4*vv["g_s"]**2*j4/c**2
    tadpole = -2*vv["h_m"]*j4-20*vv["h_s"]*j4/(3*c**2)
    return {"bubble": bubble, "tadpole": tadpole, "total": bubble+tadpole}


def static_integrated(c, vv):
    # The static bubble vertex squared cancels its removable angular denominator.
    # This is the zero-frequency limit, not an on-shell or hydrodynamic limit.
    q = .2
    nodes, weights = np.polynomial.legendre.leggauss(8)
    def radial(x):
        ep, p = x, x/c
        bubble, tadpole = 0., 0.
        for z, weight in zip(nodes, weights):
            cancellation = 2*q*p*z-q*q
            bubble += weight*8*vv["g_s"]**2*p*p*cancellation
            tadpole += weight*(-4)*(vv["h_m"]*ep**2+2*vv["h_s"]*(p*p+2*p*p*z*z))*q*q
        return p*p*bose(x)/(2*ep)*(bubble+tadpole)/(4*pi*pi*c*q*q)
    return quad(radial, 0., np.inf, epsabs=1e-9, epsrel=1e-11)[0]


def static_pressure_check(state, action, step, angular=False):
    def flow(xi):
        other = EFT.tree_state(state["mu"], xi=xi, h=state["h"], action=action)
        return EFT.angular_a4(other)[0] if angular else other["A4_flow"]
    return -EFT.finite_difference(flow, 0., step, degree=2)/state["A"]


def static_pressure_analytic(state, vv):
    p1, p2, p3 = vv["P1"], vv["P2"], vv["P3"]
    q = p1+2*state["mu"]**2*p2
    return -state["A4_flow"]/state["A"]*(11*p2/p1-(9*p2+6*state["mu"]**2*p3)/q)


def identities(paths):
    return [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths]


def audit():
    action = EFT.controls()
    rows = []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        cf, vv = INT.dispersion_coefficients(state, action), INT.vertices(state, action)
        runs = []
        for divisor in TEMPERATURE_DIVISORS:
            t = cf["c"]*cf["dispersion_scale"]/divisor
            for ratio in SOFT_RATIOS:
                k = ratio*t/cf["c"]
                pairs = [pair_rate(k, t, state, action, order) for order in ORDERS]
                landau = [landau_rate(k, t, state, action, order) for order in ORDERS]
                tails = [landau_rate(k, t, state, action, ORDERS[-1], tail) for tail in TAILS]
                coefficient = landau[-1]["gamma_pole"]/(k*t**4)
                runs.append({"temperature_divisor": divisor, "T": t, "q": k, "cq_over_T": ratio,
                             "pair_runs": pairs, "Landau_runs": landau, "tail_runs": tails,
                             "pair_quadrature_error": INT.relative(pairs[-2]["gamma_pole"], pairs[-1]["gamma_pole"]),
                             "Landau_quadrature_error": INT.relative(landau[-2]["gamma_pole"], landau[-1]["gamma_pole"]),
                             "thermal_tail_error": INT.relative(tails[-2]["gamma_pole"], tails[-1]["gamma_pole"]),
                             "Landau_over_qT4": coefficient,
                             "soft_coefficient_relative_error": INT.relative(coefficient, soft_landau_coefficient(cf["c"], vv)),
                             "pair_over_Landau": pairs[-1]["gamma_pole"]/landau[-1]["gamma_pole"],
                             "gamma_total_over_omega": (pairs[-1]["gamma_pole"]+landau[-1]["gamma_pole"])/EFT.acoustic_energy(k, state, action)})
        static = static_coefficients(cf["c"], vv)
        static_runs = [{"step": step, "pressure_coefficient": static_pressure_check(state, action, step),
                        "angular_pressure_coefficient": static_pressure_check(state, action, step, True),
                        "diagram_relative_error": INT.relative(static_pressure_check(state, action, step), static["total"])} for step in FD_STEPS]
        k0 = .005
        pair_zero = pair_rate(k0, 0., state, action)
        vacuum = INT.decay_phase_space(k0, state, action)
        root_checks = []
        for q in (.00001, k0, cf["dispersion_scale"]*.31):
            value = energy_value(q, state, action)
            root_checks.append({"q": q, "independent_parent_relative_error": INT.relative(value, EFT.acoustic_energy(q, state, action)),
                                "scaled_parent_inverse_residual": abs(EFT.phase_inverse(q, value, state, action))/q**2})
        rows.append({"mu": mu, "state_tree": state, "coefficients": cf, "vertices": vv,
                     "thermal_cut_runs": runs, "soft_Landau_coefficient": soft_landau_coefficient(cf["c"], vv),
                     "Bose_moment_relative_error": INT.relative(soft_landau_moment(cf["c"], vv), soft_landau_coefficient(cf["c"], vv)),
                     "zero_T_pair_predecessor_error": INT.relative(pair_zero["gamma_pole"], vacuum["gamma_pole"]),
                     "static_diagrams_over_q2T4": static, "static_pressure_checks": static_runs,
                     "static_general_PX_identity_error": INT.relative(static_pressure_analytic(state, vv), static["total"]),
                     "static_integrated_relative_error": INT.relative(static_integrated(cf["c"], vv), static["total"]),
                     "tadpole_without_bubble_relative_mismatch": INT.relative(static["tadpole"], static["total"]),
                     "stable_tree_root_checks": root_checks,
                     "parent_ledger": EFT.parent_energy_check(k0, state, action)})
    checks = {
        "pair_and_Landau_quadrature_refine": all(max(x["pair_quadrature_error"], x["Landau_quadrature_error"]) < GATES["quadrature_relative"] for r in rows for x in r["thermal_cut_runs"]),
        "thermal_radial_tail_refines_not_physical_remainder": all(x["thermal_tail_error"] < GATES["tail_relative"] for r in rows for x in r["thermal_cut_runs"]),
        "strict_energy_support_and_positive_rates": all(y["angular_support_margin_min"] > 0 and y["gamma_pole"] > 0 and y["energy_balance_relative_max"] < GATES["identity_relative"] for r in rows for x in r["thermal_cut_runs"] for y in x["pair_runs"]+x["Landau_runs"]),
        "cut_Bose_detailed_balance_and_two_point_FDT_only": all(y["Bose_identity_error_max"] < GATES["identity_relative"] for r in rows for x in r["thermal_cut_runs"] for y in x["pair_runs"]+x["Landau_runs"]),
        "soft_Landau_limit_and_temperature_refinement": all(r["thermal_cut_runs"][-1]["soft_coefficient_relative_error"] < GATES["soft_limit_relative"] and r["thermal_cut_runs"][-1]["soft_coefficient_relative_error"] < r["thermal_cut_runs"][2]["soft_coefficient_relative_error"] for r in rows),
        "independent_Bose_moment_and_vacuum_limit": all(max(r["Bose_moment_relative_error"], r["zero_T_pair_predecessor_error"]) < GATES["identity_relative"] for r in rows),
        "static_diagrams_match_reoptimized_flow_pressure": all(r["static_pressure_checks"][-1]["diagram_relative_error"] < GATES["static_derivative_relative"] and INT.relative(r["static_pressure_checks"][-1]["angular_pressure_coefficient"], r["static_pressure_checks"][-1]["pressure_coefficient"]) < GATES["static_derivative_relative"] for r in rows),
        "independent_static_loop_integration_and_missing_bubble_negative": all(max(r["static_integrated_relative_error"], r["static_general_PX_identity_error"]) < GATES["identity_relative"] and r["tadpole_without_bubble_relative_mismatch"] > .1 for r in rows),
        "parent_quadratic_ledger_preserved": all(r["parent_ledger"]["energy_conservation_residual"] < GATES["identity_relative"] and r["parent_ledger"]["potential_min_eigenvalue"] > 0 for r in rows),
        "cancellation_free_root_matches_original_parent": all(max(x["independent_parent_relative_error"], x["scaled_parent_inverse_residual"]) < GATES["identity_relative"] for r in rows for x in r["stable_tree_root_checks"])}
    record = {"major_result_id": "T13_FINITE_T_PHASE_CUT_AND_STATIC_THERMAL_COHERENCE",
              "topic": "0.13_Thermodynamic_Bridge", "branch_id": EFT.BRANCH,
              "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
              "verification_status": "PASS_SCOPED_THERMAL_CUT_STIFFNESS" if all(checks.values()) else "FAIL_SCOPED_THERMAL_CUT_STIFFNESS",
              "created_at": datetime.now(timezone.utc).isoformat(), "action_controls": action,
              "numerical_repair_history": "First audit rejected a naive r/k pair root outside support. Same tree root rewritten as cq plus curvature and positive displacement, with unchanged grids/gates; no clipping or dispersion replacement.",
              "what_is_closed": "Leading-vertex finite-T pair/Landau cuts with internal tree curvature and LO static thermal bubble/tadpole-pressure coherence",
              "equation_or_mapping": "gamma_L/(q T4)->3pi3(gt+gs/c2)^2/(10c2); Sigma_static/(q2 T4)=-d_xi2 A4_flow/chi",
              "units": {"gamma_omega_q_T": "E", "Sigma": "E^2", "g_t_g_s": "E^-2", "h_t_h_m_h_s": "E^-4", "static_and_soft_coefficients": "E^-4", "chi": "E^2"},
              "derivation_class": "DERIVED_LO_VERTICES_TREE_CURVATURE_CUT_AND_STATIC_ONE_PHASE_LOOP",
              "observable": "Conditional phase attenuation and static inverse response, not a detector/material prediction",
              "data_role": "DERIVED_NOT_CALIBRATION", "checks": checks, "thresholds": GATES,
              "equation_registry_ids": [x["id"] for x in json.loads((ROOT/REGISTRY).read_text())["entries"]],
              "ontology": {"Sigma_is_Phi": False, "phase_is_UET_Pi": False, "C_is_charge_or_radial_amplitude": False, "excluded_state_variables": ["C", "R_gen", "R_obs"]},
              "declared_grids": {"mu": MU_GRID, "temperature_divisors": TEMPERATURE_DIVISORS,
                                 "cq_over_T": SOFT_RATIOS, "orders": ORDERS, "thermal_tails": TAILS,
                                 "FD_steps": FD_STEPS, "locked_before_first_audit": True, "external_data_preregistration": False},
              "examples": rows,
              "evidence_artifacts": identities([str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), REGISTRY,
                                               PREFIX+"Code/03_Research/test_t13_thermal_cut_stiffness.py",
                                               PREFIX+"Code/03_Research/Research_T13_Low_T_Interactions.py",
                                               PREFIX+"Code/03_Research/Research_T13_Low_T_Phase_EFT.py"]),
              "protected_evidence_hashes": identities([PREFIX+"Result/artifacts/t13_vacuum_cut_log.json",
                                                       PREFIX+"Result/artifacts/t13_low_T_interactions.json",
                                                       PREFIX+"Result/artifacts/t13_low_T_phase_eft.json"]+list(EFT.ACTION_PATHS)),
              "controlling_blocker": "matched_curvature_real_response_and_full_thermal_sunset_open",
              "open_blockers": ["finite_local_Wilson_source_matching", "full_curved_vertices_residues_and_real_response", "complete_thermal_sunset_pressure_source_entropy", "independent_material_readout_scale_and_physical_transport"],
              "dependency_unlocked": ["matched_real_response_and_thermal_sunset_research_only"],
              "finite_T_pair_and_Landau_cuts_computed": True, "static_LO_thermal_coherence_checked": True,
              "full_finite_T_collision_operator_computed": False, "higher_derivative_vertices_and_residues_matched": False,
              "full_real_self_energy_matched": False, "full_two_loop_pressure_computed": False,
              "full_SK_KMS_matching_closed": False, "controlled_full_action_truncation_error_established": False,
              "independent_alpha_Phi_K_admitted": False, "physical_Kubo_emitted": False,
              "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False,
              "core_composition_gate_overwritten": False, "claim_promotion": False,
              "parameter_fitting": False, "assigned_damping_width": False, "clipping": False,
              "cone_padding": False, "old_Hartree_branch_repaired": False,
              "target_source_accessed": False, "xie_2026_accessed": False,
              "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
              "primary_references": ["https://arxiv.org/html/1004.2567v2"],
              "claim_boundary": "LO cut diagnostic with tree internal curvature and static linear-loop consistency only; not full curved one-loop matching, thermal quantum EOS, kinetic/normal/heat/Kubo/SK-KMS/entropy closure, SI calibration, material prediction, global no-go or Full Topic13. Old conserved-C remains blocked at 1e-6; Core-owner unchanged."}
    names = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(names, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "New thermal cut/static coherence wave, predecessors protected", record["equation_or_mapping"], checks, record["controlling_blocker"], "Match full curved real operator and thermal sunset/source/entropy; assess independent material/readout input", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"],
                      "examples": [{"mu": x["mu"], "soft_error": x["thermal_cut_runs"][-1]["soft_coefficient_relative_error"], "static_error": x["static_pressure_checks"][-1]["diagram_relative_error"]} for x in result["examples"]]}, indent=2))
    raise SystemExit(0 if all(result["checks"].values()) else 1)
