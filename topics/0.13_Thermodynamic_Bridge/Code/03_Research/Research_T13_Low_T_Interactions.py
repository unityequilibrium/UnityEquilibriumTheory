"""Tree phase vertices, dispersion remainder and leading T=0 phonon decay.

The thermal-thermal quartic diagram is deliberately not called the full
two-loop pressure. No real self-energy, vacuum matching or Kubo input is
supplied by the finite on-shell cut.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from math import isfinite, pi, sqrt
from pathlib import Path
import sys

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[5]
LOCAL = Path(__file__).resolve().parent
if str(LOCAL) not in sys.path:
    sys.path.insert(0, str(LOCAL))
import Research_T13_Low_T_Phase_EFT as EFT

PREFIX = EFT.PREFIX
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_low_T_interactions.json")
REGISTRY = PREFIX+"Data/03_Research/t13_low_T_interaction_registry.json"
MU_GRID = (1.05, 1.2)
DISPERSION_Q_GRID = (.04, .02, .01)
DECAY_Q_GRID = (.02, .01, .005)
QUADRATURE_ORDERS = (24, 48, 96)
FD_STEPS = (.0004, .0002, .0001)
TEMPERATURE_DIVISORS = (32, 64, 128)
GATES = {"derivative_relative": 2e-5, "direct_vertex_relative": 1e-3, "zeta_relative": .005,
         "decay_relative": .002, "quadrature_relative": 1e-8,
         "group_velocity_relative": 1e-7, "pressure_T8_relative": 1e-6,
         "identity_relative": 1e-9, "original_causal_leakage": 1e-6}


def pressure_derivatives(state, action):
    if state["xi"] != 0:
        raise ValueError("rest-frame derivative contract required")
    v, u, g = state["V_curvature"], state["U"], action["gamma"]
    x = state["Phi"]-action["Phi_reference"]
    w = v-g*g/(2*action["u"])
    phi_x = g/(2*v*u)
    vx = 6*action["epsilon"]*action["response_quartic"]*x*phi_x
    phi_xx = -phi_x*vx/w
    vxx = 6*action["epsilon"]*action["response_quartic"]*(phi_x**2+x*phi_xx)
    ux = g*g*vx/(2*v*v)
    uxx = g*g/2*(vxx/(v*v)-2*vx*vx/v**3)
    return {"P1": state["s"]/2, "P2": 1/(2*u),
            "P3": -ux/(2*u*u), "P4": ux*ux/u**3-uxx/(2*u*u)}


def vertices(state, action):
    p = pressure_derivatives(state, action)
    mu, chi = state["mu"], state["A"]
    return p | {"g_t": -(2*mu*p["P2"]+4*mu**3*p["P3"]/3)/chi**1.5,
                "g_s": 2*mu*p["P2"]/chi**1.5,
                "h_t": (p["P2"]/2+2*mu*mu*p["P3"]+2*mu**4*p["P4"]/3)/chi**2,
                "h_m": -(p["P2"]+2*mu*mu*p["P3"])/chi**2,
                "h_s": p["P2"]/(2*chi**2)}


def dispersion_coefficients(state, action):
    cf = EFT.rest_coefficients(state, action)
    c, a0, eta = cf["c"], cf["A0"], cf["eta"]
    v, s = state["V_curvature"], state["s"]
    kp = action["epsilon"]*action["response_kinetic"]
    hh = 1+action["gamma"]**2*s*kp/v**2
    jj = -action["gamma"]**2*s*kp*kp/v**3
    d2 = 2*c*eta
    d3 = (jj*(1-c*c)**3-2*hh*(1-c*c)*d2)/(a0+4*state["mu"]**2)
    zeta = d3/(2*c)-d2*d2/(8*c**3)
    c8 = 4*pi**6*(4*eta*eta-c*zeta)/(15*c**9)
    return cf | {"zeta": zeta, "C8_disp": c8}


def group_velocity(q, state, action):
    if not isfinite(q) or q <= 0:
        raise ValueError("positive finite momentum required")
    omega = EFT.acoustic_energy(q, state, action)
    ell = q*q-omega*omega
    kp = action["epsilon"]*action["response_kinetic"]
    v = state["V_curvature"]+kp*ell
    den = ell+2*action["u"]*state["s"]-action["gamma"]**2*state["s"]/v
    derivative = 1+action["gamma"]**2*state["s"]*kp/v**2
    hh = den+ell*derivative
    return q/omega*hh/(hh+4*state["mu"]**2)


def decay_leading_coefficient(cf, vv):
    return 3*(vv["g_t"]+vv["g_s"]/cf["c"]**2)**2*cf["c"]**2/(80*pi)


def decay_phase_space(k, state, action, order=48):
    if not isfinite(k) or k <= 0 or not isinstance(order, int) or order < 2:
        raise ValueError("positive finite momentum and quadrature order >=2 required")
    cf, vv = dispersion_coefficients(state, action), vertices(state, action)
    if cf["eta"] <= 0:
        raise ValueError("this audit admits only convex low-q dispersion")
    ek = EFT.acoustic_energy(k, state, action)
    nodes, weights = np.polynomial.legendre.leggauss(order)
    integral, cosines, balances, detailed_balances = 0., [], [], []
    for node, weight in zip(nodes, weights):
        p = k*(node+1)/2
        ep = EFT.acoustic_energy(p, state, action)
        target = (ek-ep)/k
        r = k*brentq(lambda z: EFT.acoustic_energy(k*z, state, action)/k-target,
                    0., 1., xtol=1e-14, rtol=1e-14)
        er = EFT.acoustic_energy(r, state, action)
        cosine = (k*k+p*p-r*r)/(2*k*p)
        # An invalid root is a failed support check, not silently clipped or discarded.
        if not -1 < cosine < 1:
            raise ValueError("energy root outside angular support; no clipping")
        kp = k*p*cosine
        vertex = 6*vv["g_t"]*ek*ep*er+2*vv["g_s"]*(ek*(kp-p*p)+ep*(k*k-kp)+er*kp)
        integral += weight*k/2*p*r/(ep*er*group_velocity(r, state, action))*vertex**2
        cosines.append(float(cosine))
        balances.append(abs(ek-ep-er)/ek)
        # This on-shell Bose identity checks a future collision kernel, not SK/KMS closure.
        temperature = ek/2
        nk, np_, nr = (1/np.expm1(e/temperature) for e in (ek, ep, er))
        gain, loss = (1+nk)*np_*nr, nk*(1+np_)*(1+nr)
        detailed_balances.append(relative(gain, loss))
    occupation = integral/(32*pi*ek*k)
    return {"Gamma_occupation": occupation, "gamma_pole": occupation/2,
            "quadrature_order": order, "q": k,
            "minimum_angular_support_margin": min(1-abs(x) for x in cosines),
            "energy_balance_relative_max": max(balances),
            "Bose_gain_loss_relative_max": max(detailed_balances),
            "gamma_pole_over_omega": occupation/(2*ek),
            "coefficient_q5": occupation/k**5,
            "scope": "LO canonical cubic vertex with exact tree dispersion; not full finite-q rate"}


def bose_moment(power):
    return quad(lambda x: x**power*np.exp(-x)/(-np.expm1(-x)),
                0., np.inf, epsabs=1e-9, epsrel=1e-11)[0]


def dispersion_pressure_moment(cf):
    moment7 = bose_moment(7)
    moment_derivative = 8*moment7
    return (-cf["zeta"]*moment7/cf["c"]**8+
            cf["eta"]**2*moment_derivative/(2*cf["c"]**9))/(2*pi*pi)


def quartic_thermal_thermal(vv, c):
    if not isfinite(c) or c <= 0:
        raise ValueError("positive sound speed required")
    factor = (pi*pi/(30*c**3))**2
    return factor*(3*vv["h_t"]+vv["h_m"]/c**2+5*vv["h_s"]/(3*c**4))


def wick_quartic_independent(vv, c):
    # Subtracted Euclidean thermal covariance: <d_tau phi^2>_T=-J.
    cov = np.diag([-1., 1/(3*c*c), 1/(3*c*c), 1/(3*c*c)])
    def four(i, j, k, l):
        return cov[i, j]*cov[k, l]+cov[i, k]*cov[j, l]+cov[i, l]*cov[j, k]
    wick = vv["h_t"]*four(0, 0, 0, 0)
    wick -= vv["h_m"]*sum(four(0, 0, i, i) for i in range(1, 4))
    wick += vv["h_s"]*sum(four(i, i, j, j) for i in range(1, 4) for j in range(1, 4))
    moment3 = bose_moment(3)/(2*pi*pi*c**3)
    return wick*moment3**2


def relative(x, y):
    return abs(x-y)/max(abs(y), 1e-20)


def direct_pressure_vertex_check(state, action, cf, vv):
    checks = []
    step = .01
    for t, z in ((1., 0.), (0., 1.), (1., .7)):
        def pressure(e):
            return EFT.tree_state(state["mu"]-e*t/sqrt(state["A"]),
                                  xi=e*z/sqrt(state["A"]), action=action)["pressure_tree"]
        linear = -state["mu"]*state["s"]*t/sqrt(state["A"])
        quadratic = (t*t-cf["c"]**2*z*z)/2
        cubic = vv["g_t"]*t**3+vv["g_s"]*t*z*z
        quartic = vv["h_t"]*t**4+vv["h_m"]*t*t*z*z+vv["h_s"]*z**4
        direct3 = ((pressure(step)-pressure(-step))/2-linear*step)/step**3
        direct4 = ((pressure(step)+pressure(-step))/2-pressure(0)-quadratic*step*step)/step**4
        checks.append({"time_direction": t, "space_direction": z, "step": step,
                       "cubic_relative_error": relative(direct3, cubic) if cubic != 0 else abs(direct3),
                       "quartic_relative_error": relative(direct4, quartic)})
    return checks


def audit():
    action = EFT.controls()
    rows = []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        cf, vv = dispersion_coefficients(state, action), vertices(state, action)
        derivatives = []
        for step in FD_STEPS:
            def derivative_at_x(x, name):
                return pressure_derivatives(EFT.tree_state(sqrt(x), action=action), action)[name]
            derivatives.append({"X_step": step,
                                "P3_relative_error": relative(EFT.finite_difference(lambda x: derivative_at_x(x, "P2"), state["X"], step), vv["P3"]),
                                "P4_relative_error": relative(EFT.finite_difference(lambda x: derivative_at_x(x, "P3"), state["X"], step), vv["P4"])})
        dispersion = []
        for q in DISPERSION_Q_GRID:
            energy = EFT.acoustic_energy(q, state, action)
            estimate = (energy/q-cf["c"]-cf["eta"]*q*q)/q**4
            velocity_fd = EFT.finite_difference(lambda z: EFT.acoustic_energy(z, state, action), q, q*1e-4)
            dispersion.append({"q": q, "zeta_estimate": estimate,
                               "zeta_relative_error": relative(estimate, cf["zeta"]),
                               "group_velocity_relative_error": relative(velocity_fd, group_velocity(q, state, action)),
                               "parent_energy_check": EFT.parent_energy_check(q, state, action)})
        decay = []
        coefficient = decay_leading_coefficient(cf, vv)
        for q in DECAY_Q_GRID:
            runs = [decay_phase_space(q, state, action, order) for order in QUADRATURE_ORDERS]
            decay.append({"q": q, "runs": runs,
                          "coefficient_relative_error": relative(runs[-1]["coefficient_q5"], coefficient),
                          "quadrature_relative_error": relative(runs[-2]["Gamma_occupation"], runs[-1]["Gamma_occupation"])})
        quartic = quartic_thermal_thermal(vv, cf["c"])
        thermal = []
        for divisor in TEMPERATURE_DIVISORS:
            t = cf["c"]*cf["dispersion_scale"]/divisor
            pressure = EFT.parent_acoustic_pressure(t, state, action)["pressure"]
            p6 = cf["A4"]*t**4+cf["B6"]*t**6
            p8 = p6+cf["C8_disp"]*t**8
            entropy = EFT.parent_acoustic_entropy(t, state, action)["entropy"]
            s8 = 4*cf["A4"]*t**3+6*cf["B6"]*t**5+8*cf["C8_disp"]*t**7
            thermal.append({"T": t, "divisor": divisor,
                            "pressure_T6_relative_error": relative(p6, pressure),
                            "pressure_T8_relative_error": relative(p8, pressure),
                            "entropy_T8_relative_error": relative(s8, entropy),
                            "quartic_TT_over_T4": quartic*t**4/cf["A4"],
                            "quartic_TT_is_total_error_bound": False})
        coordinate = []
        for scale in (.5, 2.):
            other_action = EFT.rescale_Phi_coordinate(action, scale)
            other_state = EFT.tree_state(mu, action=other_action)
            other_cf, other_vv = dispersion_coefficients(other_state, other_action), vertices(other_state, other_action)
            coordinate.append({"scale": scale,
                               "vertex_relative_error": max(relative(other_vv[k], vv[k]) for k in vv),
                               "zeta_relative_error": relative(other_cf["zeta"], cf["zeta"]),
                               "decay_coefficient_relative_error": relative(decay_leading_coefficient(other_cf, other_vv), coefficient)})
        rows.append({"mu": mu, "state_tree": state, "coefficients": cf, "vertices": vv,
                     "direct_stationary_pressure_vertex_checks": direct_pressure_vertex_check(state, action, cf, vv),
                     "pressure_derivative_checks": derivatives, "dispersion_checks": dispersion,
                     "Gamma_occupation_q5_coefficient": coefficient, "gamma_pole_q5_coefficient": coefficient/2,
                     "decay_phase_space_checks": decay, "thermal_runs": thermal,
                     "quartic_TT_T8_coefficient": quartic,
                     "quartic_Wick_relative_error": relative(wick_quartic_independent(vv, cf["c"]), quartic),
                     "T8_Bose_moment_relative_error": relative(dispersion_pressure_moment(cf), cf["C8_disp"]),
                     "coordinate_controls": coordinate})
    checks = {
        "vertices_match_direct_reoptimized_pressure": all(max(x["cubic_relative_error"], x["quartic_relative_error"]) < GATES["direct_vertex_relative"] for r in rows for x in r["direct_stationary_pressure_vertex_checks"]),
        "tree_pressure_higher_derivatives": all(max(r["pressure_derivative_checks"][-1][k] for k in ("P3_relative_error", "P4_relative_error")) < GATES["derivative_relative"] for r in rows),
        "q5_dispersion_matches_parent_and_refines": all(r["dispersion_checks"][-1]["zeta_relative_error"] < GATES["zeta_relative"] and r["dispersion_checks"][-1]["zeta_relative_error"] < r["dispersion_checks"][0]["zeta_relative_error"] for r in rows),
        "group_velocity_independent_derivative": all(d["group_velocity_relative_error"] < GATES["group_velocity_relative"] for r in rows for d in r["dispersion_checks"]),
        "parent_quadratic_ledger_unchanged": all(d["parent_energy_check"]["energy_conservation_residual"] < GATES["identity_relative"] and d["parent_energy_check"]["potential_min_eigenvalue"] > 0 for r in rows for d in r["dispersion_checks"]),
        "decay_phase_space_matches_q5_and_refines": all(r["decay_phase_space_checks"][-1]["coefficient_relative_error"] < GATES["decay_relative"] and r["decay_phase_space_checks"][-1]["coefficient_relative_error"] < r["decay_phase_space_checks"][0]["coefficient_relative_error"] for r in rows),
        "decay_quadrature_convergence": all(d["quadrature_relative_error"] < GATES["quadrature_relative"] for r in rows for d in r["decay_phase_space_checks"]),
        "decay_no_angular_clipping_energy_balance": all(x["minimum_angular_support_margin"] > 0 and x["energy_balance_relative_max"] < GATES["identity_relative"] for r in rows for d in r["decay_phase_space_checks"] for x in d["runs"]),
        "on_shell_Bose_detailed_balance_identity_only": all(x["Bose_gain_loss_relative_max"] < GATES["identity_relative"] for r in rows for d in r["decay_phase_space_checks"] for x in d["runs"]),
        "T8_dispersion_pressure_refines_parent_integral": all(r["thermal_runs"][-1]["pressure_T8_relative_error"] < GATES["pressure_T8_relative"] and all(t["pressure_T8_relative_error"] < t["pressure_T6_relative_error"] for t in r["thermal_runs"]) for r in rows),
        "T8_entropy_independent_integral": all(r["thermal_runs"][-1]["entropy_T8_relative_error"] < 2*GATES["pressure_T8_relative"] for r in rows),
        "T8_independent_Bose_moment": all(r["T8_Bose_moment_relative_error"] < GATES["identity_relative"] for r in rows),
        "quartic_subtracted_Wick_and_moment": all(r["quartic_Wick_relative_error"] < GATES["identity_relative"] for r in rows),
        "Phi_coordinate_invariance": all(max(x[k] for k in ("vertex_relative_error", "zeta_relative_error", "decay_coefficient_relative_error")) < GATES["identity_relative"] for r in rows for x in r["coordinate_controls"])}
    evidence_paths = [str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
                      PREFIX+"Code/03_Research/test_t13_low_T_interactions.py",
                      PREFIX+"Code/03_Research/Research_T13_Low_T_Phase_EFT.py", REGISTRY]
    protected_paths = [PREFIX+"Result/artifacts/t13_low_T_phase_eft.json"]+list(EFT.ACTION_PATHS)
    def identities(paths):
        return [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths]
    record = {
        "major_result_id": "T13_LOW_T_PHASE_INTERACTION_AND_DECAY_KERNEL",
        "topic": "0.13_Thermodynamic_Bridge", "branch_id": EFT.BRANCH,
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
        "verification_status": "PASS_SCOPED_INTERACTION_KERNEL" if all(checks.values()) else "FAIL_SCOPED_INTERACTION_KERNEL",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "what_is_closed": "Tree P3/P4 canonical vertices, tree-dispersion one-phase-loop T8, one subtracted quartic thermal-thermal diagram and derived leading T=0 Beliaev cut with independent phase-space convergence",
        "equation_or_mapping": "Gamma_occupation=3(g_t+g_s/c^2)^2 c^2 q^5/(80pi); gamma_pole=Gamma_occupation/2; C8_disp=4pi^6(4eta^2-c*zeta)/(15c^9)",
        "equation_registry_ids": [e["id"] for e in json.loads((ROOT/REGISTRY).read_text())["entries"]],
        "units": {"canonical_phase": "E", "cubic_vertices": "E^-2", "quartic_vertices": "E^-4", "zeta_C8_and_quartic_coefficient": "E^-4", "rates": "E", "rate_q5_coefficient": "E^-4"},
        "derivation_class": "TREE_MATCHED_PHASE_LOOP_AND_LEADING_ON_SHELL_CUT",
        "observable": "Conditional acoustic thermal difference and T=0 attenuation, not TTG/He-II detector output",
        "data_role": "DERIVED", "action_controls": action, "checks": checks,
        "thresholds": GATES,
        "declared_grids": {"mu": MU_GRID, "dispersion_q": DISPERSION_Q_GRID, "decay_q": DECAY_Q_GRID, "quadrature_orders": QUADRATURE_ORDERS, "FD_X_steps": FD_STEPS, "temperature_divisors": TEMPERATURE_DIVISORS, "locked_before_first_audit": True, "external_data_preregistration": False},
        "examples": rows, "evidence_artifacts": identities(evidence_paths),
        "protected_evidence_hashes": identities(protected_paths),
        "controlling_blocker": "renormalized_cubic_sunset_and_vacuum_Wilson_matching_open",
        "open_blockers": ["full_T8_two_loop_pressure_not_computed", "real_self_energy_Wilson_subtractions_not_matched", "finite_T_collision_normal_component_Kubo_and_entropy_transport_open", "independent_material_source_readout_and_temperature_scale_open"],
        "dependency_unlocked": ["renormalized_two_loop_and_finite_T_collision_research_only"],
        "primary_references": ["https://arxiv.org/html/1004.2567v2", "https://www.fuw.edu.pl/~derezins/damping_publ.pdf"],
        "standard_correspondence": "Nonrelativistic EFT and Bose-gas results are method/limiting controls, not coefficient imports to relativistic X=mu^2-xi^2",
        "full_two_loop_pressure_computed": False, "quartic_TT_is_total_error_bound": False,
        "real_self_energy_computed": False, "finite_q_complete_decay_computed": False,
        "finite_T_collision_computed": False, "assigned_damping_width": False,
        "on_shell_Bose_detailed_balance_identity_checked": True,
        "full_SK_KMS_matching_closed": False,
        "controlled_full_action_truncation_error_established": False,
        "independent_alpha_Phi_K_admitted": False, "physical_Kubo_emitted": False,
        "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False,
        "core_composition_gate_overwritten": False, "claim_promotion": False,
        "old_Hartree_branch_repaired": False, "parameter_fitting": False,
        "clipping": False, "cone_padding": False, "target_source_accessed": False,
        "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
        "state_variables": ["canonical_phase"], "excluded_variables": ["C", "R_gen", "R_obs", "UET_Pi"],
        "claim_boundary": "Scoped candidate tree/phase kernels, not a full quantum EOS/remainder bound, thermal transport, material calibration, external validation or Full Topic13/Core. The original conserved-C causal failure remains blocked at 1e-6."}
    names = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    values = (record["major_result_id"]+": "+record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "New topic-local interaction/cut audit; predecessor untouched", record["equation_or_mapping"], checks, record["controlling_blocker"], "Compute matched cubic-sunset/vacuum subtractions and finite-T collision obligations before full thermal admission", record["claim_boundary"])
    record["report"] = dict(zip(names, values))
    return record


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"], "examples": [{"mu": e["mu"], "zeta": e["coefficients"]["zeta"], "C8_disp": e["coefficients"]["C8_disp"], "quartic_TT": e["quartic_TT_T8_coefficient"], "gamma_pole_q5": e["gamma_pole_q5_coefficient"], "decay_error": e["decay_phase_space_checks"][-1]["coefficient_relative_error"]} for e in result["examples"]]}, indent=2))
    raise SystemExit(0 if all(result["checks"].values()) else 1)
