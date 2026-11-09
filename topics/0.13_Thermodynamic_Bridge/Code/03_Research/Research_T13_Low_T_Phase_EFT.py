"""Tree-matched, phase-only one-loop thermal EFT, not a Hartree repair.

The existing response Phi is classical at matching. Its conjugate h is an
external source, not a new state. Vacuum Wilson matching and interaction
remainders are not supplied by this calculation.
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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config

PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
PREDECESSOR = PREFIX+"Result/artifacts/t13_hartree_low_T_validity.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_low_T_phase_eft.json")
BRANCH = "t13.candidate.tree_matched_classical_phi_low_T_phase_EFT_v1"
MU_GRID = (1.05, 1.2)
Q_GRID = (.008, .004, .002)
TEMPERATURE_DIVISORS = (32, 64, 128)
FD_STEPS = (.0004, .0002, .0001)
FLOW_GRID = (0., .02, .04)
QUADRATURE_TOLERANCES = (1e-8, 1e-10)
IDENTITY_TOLERANCE = 1e-9
DERIVATIVE_TOLERANCE = 2e-5
DISPERSION_TOLERANCE = 5e-4
THERMAL_T6_TOLERANCE = 5e-5
ACTION_PATHS = (
    "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
    "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py",
    "docs/core/02_equations/covariant/uet_covariant_matter.py",
    "docs/core/02_equations/covariant/uet_covariant_response.py",
)


def controls():
    eos = natural_bridge_config().eos
    m, p = eos.matter, eos.response
    return {"Z": m.matter_kinetic, "m0_sq": m.matter_mass_sq/m.matter_kinetic,
            "u": m.matter_quartic/m.matter_kinetic**2,
            "gamma": p.epsilon_nc*m.response_coupling/m.matter_kinetic,
            "epsilon": p.epsilon_nc, "Phi_reference": p.phi_equilibrium,
            "response_mass_sq": p.response_mass_sq,
            "response_quartic": p.response_quartic,
            "response_kinetic": p.response_kinetic}


def validate(action):
    if not all(isfinite(x) for x in action.values()):
        raise ValueError("finite action inputs required")
    if min(action[k] for k in ("Z", "u", "epsilon", "response_mass_sq",
                               "response_quartic", "response_kinetic")) <= 0:
        raise ValueError("positive stable action inputs required")
    if action["epsilon"]*action["response_mass_sq"] <= action["gamma"]**2/(2*action["u"]):
        raise ValueError("this branch requires a globally monotone heavy source equation")


def tree_state(mu, xi=0., h=0., action=None):
    action = controls() if action is None else action
    validate(action)
    if not all(isfinite(v) for v in (mu, xi, h)) or mu <= abs(xi):
        raise ValueError("finite timelike chemical/phase/source inputs required")
    u, g, eps = (action[k] for k in ("u", "gamma", "epsilon"))
    xinv = mu*mu-xi*xi
    r0 = xinv-action["m0_sq"]
    w = eps*action["response_mass_sq"]-g*g/(2*u)
    constant = g*r0/(2*u)+h
    def force(x):
        return eps*action["response_quartic"]*x**3+w*x-constant
    bracket = max(1., abs(constant)/w+1.)
    x = brentq(force, -bracket, bracket, xtol=1e-14, rtol=1e-14)
    phi = x+action["Phi_reference"]
    s = (r0+g*x)/u
    if s <= 0:
        raise ValueError("condensed tree domain required; no state repair")
    vcurv = eps*(action["response_mass_sq"]+3*action["response_quartic"]*x*x)
    effective_u = u-g*g/(2*vcurv)
    pressure = u*s*s/4-eps*(action["response_mass_sq"]*x*x/2+
                            action["response_quartic"]*x**4/4)+h*phi
    aa = s+2*mu*mu/effective_u
    bb = 2*mu*xi/effective_u
    dd = s-2*xi*xi/effective_u
    if dd <= 0:
        raise ValueError("positive laboratory phonon energy required; no flow padding")
    mixed = aa*dd+bb*bb
    a4 = pi*pi/90*mixed**1.5/(s*dd*dd)
    c2 = s/(s+2*xinv/effective_u)
    return {"mu": mu, "xi": xi, "h": h, "X": xinv, "s": s, "Phi": phi,
            "V_curvature": vcurv, "U": effective_u, "pressure_tree": pressure,
            "A": aa, "B": bb, "D": dd, "rho": s,
            "c2_rest_at_X": c2, "A4_flow": a4,
            "stationary_residual": max(abs(force(x)), abs(-r0-g*x+u*s)),
            "heavy_hessian": [[2*u*s, -g*sqrt(s)], [-g*sqrt(s), vcurv]]}


def phase_inverse(q, omega, state, action):
    ell = q*q-omega*omega
    denominator = ell+2*action["u"]*state["s"]-action["gamma"]**2*state["s"]/(state["V_curvature"]+action["epsilon"]*action["response_kinetic"]*ell)
    return ell-4*state["mu"]**2*omega*omega/denominator


def acoustic_energy(q, state, action):
    if not isfinite(q) or q < 0 or state["xi"] != 0:
        raise ValueError("nonnegative rest-frame momentum required")
    if q == 0:
        return 0.
    # Solve for omega^2/q^2 so the small-q root is not lost to cancellation.
    def scaled_phase(t):
        ell = q*q*(1-t)
        denominator = ell+2*action["u"]*state["s"]-action["gamma"]**2*state["s"]/(state["V_curvature"]+action["epsilon"]*action["response_kinetic"]*ell)
        return 1-t-4*state["mu"]**2*t/denominator
    return q*sqrt(brentq(scaled_phase, 0., 1., xtol=1e-14, rtol=1e-14))


def parent_energy_check(q, state, action):
    kinetic = np.diag([1., 1., action["epsilon"]*action["response_kinetic"]])
    potential = np.array([[q*q+2*action["u"]*state["s"], 0., -action["gamma"]*sqrt(state["s"])],
                          [0., q*q, 0.],
                          [-action["gamma"]*sqrt(state["s"]), 0., state["V_curvature"]+kinetic[2, 2]*q*q]])
    gyroscopic = np.array([[0., -2*state["mu"], 0.], [2*state["mu"], 0., 0.], [0., 0., 0.]])
    operator = np.block([[np.zeros((3, 3)), np.eye(3)],
                         [-np.linalg.solve(kinetic, potential), -np.linalg.solve(kinetic, gyroscopic)]])
    energy_metric = np.block([[potential, np.zeros((3, 3))], [np.zeros((3, 3)), kinetic]])
    eigenvalues = np.linalg.eigvals(operator)
    positive_frequencies = sorted(float(z.imag) for z in eigenvalues if z.imag > 0)
    return {"energy_conservation_residual": float(np.max(abs(operator.T@energy_metric+energy_metric@operator))),
            "potential_min_eigenvalue": float(np.linalg.eigvalsh(potential)[0]),
            "kinetic_min_eigenvalue": float(np.linalg.eigvalsh(kinetic)[0]),
            "mode_real_growth_max": float(np.max(abs(eigenvalues.real))),
            "positive_mode_frequencies": positive_frequencies}


def rest_coefficients(state, action):
    if state["xi"] != 0:
        raise ValueError("T^6 matching is declared only at relative rest")
    s, u, v = state["s"], state["U"], state["V_curvature"]
    a0 = 2*s*u
    c = sqrt(state["rho"]/state["A"])
    heavy_derivative = 1+action["gamma"]**2*s*action["epsilon"]*action["response_kinetic"]/v**2
    d2 = heavy_derivative*(1-c*c)**2/(a0+4*state["mu"]**2)
    eta = d2/(2*c)
    a4 = pi*pi/(90*c**3)
    b6 = -4*pi**4*eta/(63*c**6)
    phi_h = 1/(v-action["gamma"]**2/(2*action["u"]))
    phi_mu = action["gamma"]*state["mu"]/(v*u)
    def a4_derivative(phi_derivative, explicit_mu):
        ds = (2*state["mu"]*explicit_mu+action["gamma"]*phi_derivative)/action["u"]
        dv = 6*action["epsilon"]*action["response_quartic"]*(state["Phi"]-action["Phi_reference"])*phi_derivative
        du = action["gamma"]**2*dv/(2*v*v)
        da = ds+4*state["mu"]*explicit_mu/u-2*state["mu"]**2*du/(u*u)
        return -1.5*a4*(ds/s-da/state["A"])
    return {"c": c, "A0": a0, "eta": eta, "A4": a4, "B6": b6,
            "A4_h": a4_derivative(phi_h, 0.), "A4_mu": a4_derivative(phi_mu, 1.),
            "Phi_h_tree": phi_h, "Phi_mu_tree": phi_mu,
            "dispersion_scale": sqrt(a0/heavy_derivative)}


def log_bose(x):
    if x <= 0:
        raise ValueError("positive Bose argument required")
    return float(-np.log(-np.expm1(-x))) if x < 1 else float(-np.log1p(-np.exp(-x)))


def parent_acoustic_pressure(t, state, action, tolerance=1e-10):
    if not isfinite(t) or t <= 0:
        raise ValueError("positive natural temperature required")
    c = rest_coefficients(state, action)["c"]
    def integrand(x):
        return x*x*log_bose(acoustic_energy(t*x/c, state, action)/t)
    value, error = quad(integrand, 0., np.inf, epsabs=tolerance, epsrel=tolerance, limit=180)
    return {"pressure": t**4*value/(2*pi*pi*c**3),
            "quadrature_error_estimate": t**4*error/(2*pi*pi*c**3)}


def parent_acoustic_entropy(t, state, action):
    if not isfinite(t) or t <= 0:
        raise ValueError("positive natural temperature required")
    c = rest_coefficients(state, action)["c"]
    def integrand(x):
        y = acoustic_energy(t*x/c, state, action)/t
        occupation = float(np.exp(-y)) if y > 50 else 1/float(np.expm1(y))
        return x*x*(y*occupation+log_bose(y))
    value, error = quad(integrand, 0., np.inf, epsabs=1e-10, epsrel=1e-10, limit=180)
    return {"entropy": t**3*value/(2*pi*pi*c**3),
            "quadrature_error_estimate": t**3*error/(2*pi*pi*c**3)}


def angular_a4(state):
    aa, bb, dd, rho = (state[k] for k in ("A", "B", "D", "rho"))
    def inverse_cube(z):
        velocity = bb*z/aa+sqrt((bb*bb/aa**2+dd/aa)*z*z+rho/aa*(1-z*z))
        if velocity <= 0:
            raise ValueError("positive laboratory mode velocity required")
        return velocity**-3
    value, error = quad(inverse_cube, -1., 1., epsabs=1e-10, epsrel=1e-10)
    return pi*pi/180*value, pi*pi/180*error


def finite_difference(fn, x, step, degree=1):
    if degree == 1:
        return (fn(x+step)-fn(x-step))/(2*step)
    return (fn(x+step)-2*fn(x)+fn(x-step))/(step*step)


def rescale_Phi_coordinate(action, scale):
    if not isfinite(scale) or scale <= 0:
        raise ValueError("positive coordinate normalization required")
    return action | {"gamma": action["gamma"]/scale,
                     "Phi_reference": scale*action["Phi_reference"],
                     "response_mass_sq": action["response_mass_sq"]/scale**2,
                     "response_quartic": action["response_quartic"]/scale**4,
                     "response_kinetic": action["response_kinetic"]/scale**2}


def audit():
    action = controls()
    previous = json.loads((ROOT/PREDECESSOR).read_text(encoding="utf-8"))
    examples = []
    for mu in MU_GRID:
        state = tree_state(mu, action=action)
        cf = rest_coefficients(state, action)
        source_rows = []
        for step in FD_STEPS:
            dmu = finite_difference(lambda m: tree_state(m, action=action)["pressure_tree"], mu, step)
            dmu2 = finite_difference(lambda m: tree_state(m, action=action)["pressure_tree"], mu, step, 2)
            dh = finite_difference(lambda h: tree_state(mu, h=h, action=action)["pressure_tree"], 0., step)
            a4h = finite_difference(lambda h: tree_state(mu, h=h, action=action)["A4_flow"], 0., step/10)
            a4mu = finite_difference(lambda m: tree_state(m, action=action)["A4_flow"], mu, step)
            source_rows.append({"step": step, "charge_relative_error": abs(dmu/(mu*state["s"])-1),
                                "chi_relative_error": abs(dmu2/state["A"]-1),
                                "Phi_source_relative_error": abs(dh/state["Phi"]-1),
                                "A4_h_relative_error": abs(a4h/cf["A4_h"]-1),
                                "A4_mu_relative_error": abs(a4mu/cf["A4_mu"]-1)})
        dispersion = []
        for q in Q_GRID:
            energy = acoustic_energy(q, state, action)
            ledger = parent_energy_check(q, state, action)
            estimated_eta = (energy/q-cf["c"])/(q*q)
            ell = q*q-energy*energy
            matrix = np.array([[ell+2*action["u"]*state["s"], 2j*mu*energy, -action["gamma"]*sqrt(state["s"])],
                               [-2j*mu*energy, ell, 0.],
                               [-action["gamma"]*sqrt(state["s"]), 0., state["V_curvature"]+action["epsilon"]*action["response_kinetic"]*ell]])
            dispersion.append({"q": q, "energy": energy, "eta_estimate": estimated_eta,
                               "eta_relative_error": abs(estimated_eta/cf["eta"]-1),
                               "uneliminated_scaled_determinant": float(abs(np.linalg.det(matrix))/(q*q)),
                               "phase_inverse_scaled": abs(phase_inverse(q, energy, state, action))/(q*q),
                               "independent_first_order_parent": ledger,
                               "first_order_frequency_relative_error": abs(ledger["positive_mode_frequencies"][0]/energy-1)})
        thermal = []
        for divisor in TEMPERATURE_DIVISORS:
            t = cf["c"]*cf["dispersion_scale"]/divisor
            integral = [parent_acoustic_pressure(t, state, action, tol) for tol in QUADRATURE_TOLERANCES]
            p4, p6 = cf["A4"]*t**4, cf["B6"]*t**6
            p = integral[-1]["pressure"]
            entropy = parent_acoustic_entropy(t, state, action)
            entropy_expansion = 4*cf["A4"]*t**3+6*cf["B6"]*t**5
            thermal.append({"T": t, "temperature_divisor": divisor, "integral_runs": integral,
                            "P_T4": p4, "P_T6_correction": p6,
                            "T4_relative_error": abs(p4/p-1), "T4_T6_relative_error": abs((p4+p6)/p-1),
                            "dispersion_correction_fraction": abs(p6/p4),
                            "Phi_thermal_shift_order_one_loop_T4": cf["A4_h"]*t**4,
                            "charge_thermal_shift_order_one_loop_T4": cf["A4_mu"]*t**4,
                            "entropy_T4": 4*cf["A4"]*t**3,
                            "entropy_T4_T6": entropy_expansion,
                            "independent_entropy_integral": entropy,
                            "entropy_T4_T6_relative_error": abs(entropy_expansion/entropy["entropy"]-1),
                            "fixed_charge_heat_capacity_leading": 12*cf["A4"]*t**3})
        flows = []
        for xi in FLOW_GRID:
            moving = tree_state(mu, xi=xi, action=action)
            angular, error = angular_a4(moving)
            flows.append({"xi": xi, "A4_closed": moving["A4_flow"], "A4_angular": angular,
                          "relative_disagreement": abs(angular/moving["A4_flow"]-1),
                          "quadrature_error_estimate": error,
                          "positive_energy_margin_D": moving["D"]})
        kinetic_probes = []
        for zphi in (.5, 1., 2.):
            probe_action = action | {"response_kinetic": zphi}
            probe_state = tree_state(mu, action=probe_action)
            probe_coefficients = rest_coefficients(probe_state, probe_action)
            kinetic_probes.append({"response_kinetic": zphi,
                                   "pressure_tree": probe_state["pressure_tree"],
                                   "c": probe_coefficients["c"], "A4": probe_coefficients["A4"],
                                   "eta": probe_coefficients["eta"], "B6": probe_coefficients["B6"],
                                   "parent_energy_checks": [parent_energy_check(q, probe_state, probe_action) for q in Q_GRID]})
        eta_slope = action["gamma"]**2*state["s"]*action["epsilon"]/state["V_curvature"]**2*(1-cf["c"]**2)**2/(2*cf["c"]*(cf["A0"]+4*mu*mu))
        coordinate_probes = []
        for scale in (.5, 2.):
            transformed = rescale_Phi_coordinate(action, scale)
            transformed_state = tree_state(mu, action=transformed)
            transformed_cf = rest_coefficients(transformed_state, transformed)
            coordinate_probes.append({"Phi_coordinate_scale": scale,
                                      "Phi_scaling_error": abs(transformed_state["Phi"]/(scale*state["Phi"])-1),
                                      "pressure_relative_error": abs(transformed_state["pressure_tree"]/state["pressure_tree"]-1),
                                      "eta_relative_error": abs(transformed_cf["eta"]/cf["eta"]-1),
                                      "A4_relative_error": abs(transformed_cf["A4"]/cf["A4"]-1)})
        examples.append({"state_tree_not_Hartree": state, "rest_coefficients": cf,
                         "source_derivative_checks": source_rows, "parent_dispersion_checks": dispersion,
                         "thermal_runs": thermal, "relative_flow_checks": flows,
                         "kinetic_nonidentifiability_witnesses": kinetic_probes,
                         "eta_response_kinetic_slope": eta_slope,
                         "Phi_coordinate_redundancy_controls": coordinate_probes,
                         "measurement_scope": "Tree rest EOS and leading T4 coefficient do not identify q-cubed dispersion; natural-unit conditional design, not physical TTG/He-II admission"})
    checks = {
        "same_action_trial_inputs_not_reoptimized_or_fitted": action == previous["action_controls"],
        "joint_tree_stationarity_and_heavy_positivity": all(e["state_tree_not_Hartree"]["stationary_residual"] < IDENTITY_TOLERANCE and np.linalg.eigvalsh(e["state_tree_not_Hartree"]["heavy_hessian"])[0] > 0 for e in examples),
        "pressure_source_charge_chi_and_Phi": all(e["source_derivative_checks"][-1][k] < DERIVATIVE_TOLERANCE for e in examples for k in ("charge_relative_error", "chi_relative_error", "Phi_source_relative_error")),
        "thermal_source_current_derivatives": all(e["source_derivative_checks"][-1][k] < DERIVATIVE_TOLERANCE for e in examples for k in ("A4_h_relative_error", "A4_mu_relative_error")),
        "parent_gapless_root_and_T6_dispersion": all(e["parent_dispersion_checks"][-1]["eta_relative_error"] < DISPERSION_TOLERANCE and all(r["uneliminated_scaled_determinant"] < IDENTITY_TOLERANCE and r["phase_inverse_scaled"] < IDENTITY_TOLERANCE for r in e["parent_dispersion_checks"]) for e in examples),
        "T6_pressure_matches_independent_parent_mode_integral": all(e["thermal_runs"][-1]["T4_T6_relative_error"] < THERMAL_T6_TOLERANCE and all(r["T4_T6_relative_error"] < r["T4_relative_error"] for r in e["thermal_runs"]) for e in examples),
        "low_T_dispersion_remainder_decreases": all(e["thermal_runs"][-1]["T4_T6_relative_error"] < e["thermal_runs"][-2]["T4_T6_relative_error"] < e["thermal_runs"][0]["T4_T6_relative_error"] for e in examples),
        "independent_quadrature_refinement": all(abs(r["integral_runs"][-1]["pressure"]/r["integral_runs"][0]["pressure"]-1) < 1e-7 for e in examples for r in e["thermal_runs"]),
        "relative_flow_angular_determinant_agreement": all(r["relative_disagreement"] < IDENTITY_TOLERANCE and r["positive_energy_margin_D"] > 0 for e in examples for r in e["relative_flow_checks"]),
        "positive_thermal_entropy_and_leading_fixed_charge_heat_capacity": all(r["entropy_T4_T6"] > 0 and r["fixed_charge_heat_capacity_leading"] > 0 for e in examples for r in e["thermal_runs"]),
        "independent_entropy_matches_same_T6_pressure_prescription": all(e["thermal_runs"][-1]["entropy_T4_T6_relative_error"] < 2*THERMAL_T6_TOLERANCE for e in examples),
        "tree_static_and_T4_inputs_do_not_identify_kinetic_dispersion": all(all(r[k] == e["kinetic_nonidentifiability_witnesses"][0][k] for r in e["kinetic_nonidentifiability_witnesses"] for k in ("pressure_tree", "c", "A4")) and e["eta_response_kinetic_slope"] > 0 and abs((e["kinetic_nonidentifiability_witnesses"][-1]["eta"]-e["kinetic_nonidentifiability_witnesses"][0]["eta"])/1.5/e["eta_response_kinetic_slope"]-1) < IDENTITY_TOLERANCE for e in examples),
        "independent_parent_energy_and_all_six_modes": all(all(r["first_order_frequency_relative_error"] < DERIVATIVE_TOLERANCE for r in e["parent_dispersion_checks"]) and all(c["energy_conservation_residual"] < IDENTITY_TOLERANCE and c["potential_min_eigenvalue"] > 0 and c["kinetic_min_eigenvalue"] > 0 and c["mode_real_growth_max"] < IDENTITY_TOLERANCE and len(c["positive_mode_frequencies"]) == 3 for r in e["kinetic_nonidentifiability_witnesses"] for c in r["parent_energy_checks"]) for e in examples),
        "physical_kinetic_ambiguity_not_Phi_coordinate_redundancy": all(all(r[k] < IDENTITY_TOLERANCE for r in e["Phi_coordinate_redundancy_controls"] for k in ("Phi_scaling_error", "pressure_relative_error", "eta_relative_error", "A4_relative_error")) for e in examples),
        "protected_Core_and_old_failed_branches_unchanged": all(hashlib.sha256((ROOT/r["path"]).read_bytes()).hexdigest() == r["sha256"] for r in previous["protected_evidence_hashes"]),
    }
    passed = all(checks.values())
    paths = (*ACTION_PATHS, PREDECESSOR, Path(__file__).relative_to(ROOT).as_posix())
    record = {"schema_version": "t13-low-T-phase-EFT-v1", "generated_at": datetime.now(timezone.utc).isoformat(),
              "major_result_id": "T13_TREE_MATCHED_LOW_T_PHASE_THERMODYNAMIC_PRESCRIPTION", "topic": "0.13", "branch_id": BRANCH,
              "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
              "verification_status": "PASS_SCOPED_TREE_MATCHED_LOW_T_EFT" if passed else "FAIL_LOW_T_EFT_CHECK",
              "what_is_closed": ["joint_tree_P_X_h_matching", "gapless_parent_and_tree_T6_dispersion", "phase_only_one_loop_T4_T6_thermal_pressure", "leading_relative_flow_and_source_Phi_thermal_response", "conditional_kinetic_input_nonidentifiability_and_dispersion_measurement"] if passed else [],
              "equation_or_mapping": "P0=r^2/(4u)-V(Phi)+h*Phi; Delta_T P=A4*T^4+B6*T^6 at phase one-loop and relative rest; Delta_T<Phi>=partial_h A4*T^4+...; s_th=partial_T Delta_T P",
              "units": {"mu_xi_T_Phi_gamma": "E", "X_s_Hessian_chi_rho_A_B_D_pressure_X": "E^2", "source_h_entropy_charge": "E^3", "pressure": "E^4", "eta_B6": "E^-2", "A4_U_u_pressure_XX": "dimensionless", "A4_h": "E^-3", "A4_mu": "E^-1"},
              "derivation_class": "TREE_MATCHED_LOW_ENERGY_EFT_PLUS_PHASE_ONE_LOOP_THERMAL_DETERMINANT_NOT_FULL_QUANTUM_COMPLETION",
              "observable": "natural_equilibrium_pressure_entropy_charge_and_Phi_source_response_not_TTG_or_material_transport",
              "data_role": "DERIVED_TRIAL_INPUT_NO_EMPIRICAL_ROWS",
              "ontology": {"C": "Collective lane coordinate, not this O2 amplitude or charge", "Phi": "Existing effective response, classical at tree matching, not a metric or 2PI functional", "s": "Canonical O2 radial amplitude squared, not collective C", "R_gen": "Derived history trace, no state or feedback", "R_obs": "Observer information, excluded from dynamics", "h": "External nondynamical source conjugate to existing Phi, E^3"},
              "standard_physics_correspondence": "Classical O2-plus-response action -> tree P(X,h) -> phase-only Bose thermal determinant; not full two-fluid or dissipative constitutive transport",
              "equation_registry_ids": ["t13.diagnostic.joint_tree_P_X_h", "t13.diagnostic.tree_matched_acoustic_T6", "t13.diagnostic.phase_EFT_thermal_source_response", "t13.diagnostic.phase_EFT_kinetic_identifiability"],
              "action_controls": action, "examples": examples, "checks": checks,
              "loop_ordering": {"zero_T_coefficients": "TREE_MATCHED_WILSON_INPUTS_NOT_VACUUM_LOOP_MATCHED", "thermal_difference": "PHASE_ONE_LOOP_T4_AND_TREE_DISPERSION_T6", "classical_heavy_shift_changes_stationary_pressure": "Second loop order after consistent tree elimination; source derivatives include tree elimination chain", "full_one_loop_quantum_pressure_computed": False, "normal_component_finite_T_dynamic_response_computed": False},
              "config": {"mu_grid": MU_GRID, "q_grid": Q_GRID, "T_equals_c_dispersion_scale_divided_by": TEMPERATURE_DIVISORS, "finite_difference_steps": FD_STEPS, "flow_grid": FLOW_GRID, "quadrature_tolerances": QUADRATURE_TOLERANCES, "design_note": "Declared before first audit; trial inputs and gates are internal, not an external preregistration"},
              "thresholds": {"identity": IDENTITY_TOLERANCE, "derivative": DERIVATIVE_TOLERANCE, "finest_eta_expansion": DISPERSION_TOLERANCE, "finest_T6_pressure": THERMAL_T6_TOLERANCE, "original_causal_leakage": 1e-6},
              "evidence_artifacts": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths],
              "protected_evidence_hashes": previous["protected_evidence_hashes"],
              "open_blockers": ["vacuum_Wilson_matching_and_phonon_interaction_remainder", "finite_T_normal_component_dynamic_and_heat_collision_Kubo_SK_KMS_entropy_transport", "independent_material_source_readout_and_temperature_scale", "full_original_causal_branch_and_Core_admission"],
              "controlling_blocker": "low_T_EFT_vacuum_Wilson_and_interaction_remainder_not_matched",
              "dependency_unlocked": ["research_on_new_EFT_remainder_and_independent_measurement_only"] if passed else [],
              "measurement_design": {"scope": "CONDITIONAL_NATURAL_UNIT_SINGLE_UNKNOWN_INVARIANT_KINETIC_COMBINATION", "unidentified_input": "I_kinetic=gamma^2*epsilon*Z_Phi/V_curvature^2; Z_Phi alone only after independent field normalization", "static_and_leading_T4_derivative_wrt_input": 0, "additional_observable": "eta=lim_q_to_0(omega(q)/q-c)/q^2=eta_base*(1+s*I_kinetic)", "local_information_rank_before": 0, "local_information_rank_after": 1, "requires": ["independently fixed other action parameters and field normalization", "admitted physical source/detector/state mapping", "controlled q^5 and Wilson/interaction remainder", "measured frequency and wavevector covariance"], "precision_relation": "sigma_eta <= abs(partial_Z_Phi eta)*requested_sigma_Z_Phi only in the independently normalized single-unknown lane, with full covariance/remainder budget", "physical_precision_or_lab_feasibility_established": False, "minimal_for_full_UET": False},
              "thermal_prescription_declared_in_new_lane": bool(passed), "old_Hartree_branch_repaired": False,
              "Hartree_internal_mass_reused": False, "phonon_pressure_appended_to_old_Hartree": False,
              "Phi_quantum_loops_included": False, "phase_boson_quantization_is_declared_prescription": True,
              "external_h_is_state": False, "controlled_full_action_truncation_error_established": False,
              "independent_alpha_Phi_K_admitted": False, "physical_Kubo_emitted": False,
              "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False,
              "core_composition_gate_overwritten": False, "claim_promotion": False, "parameter_fitting": False,
              "clipping": False, "IR_filter": False, "cone_padding": False, "target_source_accessed": False,
              "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
              "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False,
              "state_variables": ["existing_O2_phase_low_energy_degree", "classical_Phi_and_radial_amplitude_eliminated_at_tree_matching"],
              "excluded_variables": ["collective_C_not_O2_amplitude", "R_gen", "R_obs", "external_h", "external_A"],
              "claim_boundary": "New tree-matched phase-only low-T EFT prescription and internal checks at two trial inputs, not a repair of Hartree, full quantum/finite-T transport, controlled physical EOS, material/SI calibration, external validation or Full Topic13/Core."}
    names = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    values = (record["major_result_id"]+": "+record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Derived new joint tree matching, phase thermal determinant and source response without changing old Hartree.", record["equation_or_mapping"], checks, record["controlling_blocker"], "Control vacuum Wilson/interaction remainder and develop independent input measurement card; full thermal/physical acceptance remains open.", record["claim_boundary"])
    record["report"] = dict(zip(names, values))
    return record


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"]}, indent=2))
    raise SystemExit(0 if all(result["checks"].values()) else 1)
