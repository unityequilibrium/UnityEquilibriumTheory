"""Tree acoustic pole residues, cubic projection and modal phase-space cuts.

Only the tree-reduced acoustic branch is quantized as in the predecessor.
Heavy-field components are slaved polarizations, not new quantum Phi loops.
"""

from datetime import datetime, timezone
import hashlib
import itertools
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
import Research_T13_Thermal_Cut_Stiffness as TH

EFT, INT, PREFIX = TH.EFT, TH.INT, TH.PREFIX
REGISTRY = PREFIX+"Data/03_Research/t13_acoustic_modal_cut_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_acoustic_modal_cuts.json")
Q_GRID = (.04, .02, .01, .005)
MU_GRID = (1.05, 1.2)
FD_STEPS = (.01, .005, .0025)
RESIDUE_OFFSETS = (.01, .001, .0001)
GATES = {"identity_relative": 1e-9, "tensor_relative": 1e-7,
         "potential_derivative_relative": 1e-5, "residue_relative": 1e-6,
         "low_q_relative": .005, "quadrature_relative": 1e-6,
         "tail_relative": 1e-8, "original_causal_leakage": 1e-6}


def kernel(q, omega, state, action):
    if not all(isfinite(x) for x in (q, omega)) or q <= 0:
        raise ValueError("positive finite momentum and finite frequency required")
    ell, r = q*q-omega*omega, sqrt(state["s"])
    kp = action["epsilon"]*action["response_kinetic"]
    return np.array([[ell+2*action["u"]*state["s"], 2j*state["mu"]*omega, -action["gamma"]*r],
                     [-2j*state["mu"]*omega, ell, 0.],
                     [-action["gamma"]*r, 0., state["V_curvature"]+kp*ell]], dtype=complex)


def mode(q, state, action, sign=1):
    TH.validate(q, 0., state, action, 2)
    if sign not in (-1, 1):
        raise ValueError("signed acoustic frequency required")
    energy = TH.energy_value(q, state, action)
    ell = q*q-energy*energy
    a0, v = INT.dispersion_coefficients(state, action)["A0"], state["V_curvature"]
    kp, g, r = action["epsilon"]*action["response_kinetic"], action["gamma"], sqrt(state["s"])
    w = v+kp*ell
    hh = 1+g*g*state["s"]*kp/(v*w)
    den = a0+ell*hh
    aa = 2*state["mu"]*sign*energy/den
    bb = g*r*aa/w
    n = 1+4*state["mu"]**2/den+aa*aa+kp*bb*bb
    if min(w, den, n) <= 0:
        raise ValueError("positive acoustic pole norm and heavy denominators required")
    z = 1/n
    return {"q": q, "omega": sign*energy, "Z_pi": z, "N_pi": n, "A": aa, "B": bb,
            "ell": ell, "den": den, "W": w, "H": hh,
            "delta_inverse_den": -ell*hh/(a0*den),
            "delta_inverse_den_W": -ell*(a0*kp+hh*v+ell*hh*kp)/(a0*v*den*w),
            "polarization": sqrt(z)*np.array([-1j*aa, 1., -1j*bb])}


def cubic_tensor(state, action):
    r, g = sqrt(state["s"]), action["gamma"]
    tensor = np.zeros((3, 3, 3))
    tensor[0, 0, 0] = 6*action["u"]*r
    tensor[2, 2, 2] = 6*action["epsilon"]*action["response_quartic"]*(state["Phi"]-action["Phi_reference"])
    for indices, value in (((0, 1, 1), 2*action["u"]*r), ((2, 0, 0), -g), ((2, 1, 1), -g)):
        for permutation in set(itertools.permutations(indices)):
            tensor[permutation] = value
    return tensor


def potential(fields, state, action):
    sigma, phase, phi = fields
    radial = (sqrt(state["s"])+sigma)**2+phase**2
    displacement = state["Phi"]-action["Phi_reference"]+phi
    return -(state["mu"]**2-action["m0_sq"]+action["gamma"]*displacement)*radial/2+action["u"]*radial**2/4+action["epsilon"]*(action["response_mass_sq"]*displacement**2/2+action["response_quartic"]*displacement**4/4)-state["h"]*(state["Phi"]+phi)


def tensor_potential_check(state, action, step):
    expected, errors = cubic_tensor(state, action), []
    tensor_scale = max(float(np.max(abs(expected))), 1e-30)
    for indices in itertools.combinations_with_replacement(range(3), 3):
        value = 0.
        for signs in itertools.product((-1, 1), repeat=3):
            displacement = np.zeros(3)
            for index, sign in zip(indices, signs):
                displacement[index] += sign*step
            value += np.prod(signs)*potential(displacement, state, action)
        numeric = value/(8*step**3)
        errors.append(abs(numeric-expected[indices])/tensor_scale)
    return float(max(errors))


def amplitude(momentum, signs, state, action, stable=True):
    if len(momentum) != 3 or len(signs) != 3:
        raise ValueError("three signed acoustic legs required")
    modes = [mode(q, state, action, sign) for q, sign in zip(momentum, signs)]
    energies = [x["omega"] for x in modes]
    if abs(sum(energies))/max(abs(x) for x in energies) > GATES["identity_relative"]:
        raise ValueError("on-shell energy conservation required, not enforced by fitting")
    if min(sum(momentum)-2*q for q in momentum) <= 0:
        raise ValueError("strict momentum triangle required")
    if not stable:
        return np.einsum("ijk,i,j,k", cubic_tensor(state, action), *(x["polarization"] for x in modes))
    # On shell sum omega=0. Subtract its exact zero before small-q cancellation.
    sum_a = 2*state["mu"]*sum(x["omega"]*x["delta_inverse_den"] for x in modes)
    sum_b = 2*state["mu"]*action["gamma"]*sqrt(state["s"])*sum(x["omega"]*x["delta_inverse_den_W"] for x in modes)
    a, b = [x["A"] for x in modes], [x["B"] for x in modes]
    value = 6*action["u"]*sqrt(state["s"])*np.prod(a)-2*action["u"]*sqrt(state["s"])*sum_a
    value -= action["gamma"]*sum(b[i]*a[(i+1)%3]*a[(i+2)%3] for i in range(3))
    value += action["gamma"]*sum_b
    value += cubic_tensor(state, action)[2, 2, 2]*np.prod(b)
    return 1j*float(value)*sqrt(np.prod([x["Z_pi"] for x in modes]))


def pair_root(k, p, state, action):
    c = INT.dispersion_coefficients(state, action)["c"]
    dk, dp = TH.energy_split(k, state, action)[1], TH.energy_split(p, state, action)[1]
    scale = k*p*(k-p)
    def residual(a):
        r = k-p+scale*a
        return (dk-dp-TH.energy_split(r, state, action)[1])/scale-c*a
    a = brentq(residual, 0., 2*p/scale, xtol=1e-13, rtol=1e-13)
    r = k-p+scale*a
    cosine = 1-scale*a*(2*(k-p)+scale*a)/(2*k*p)
    if not -1 < cosine < 1:
        raise ValueError("pair root support failed")
    return r, cosine


def cut_rate(k, temperature, state, action, channel, order=48, tail=40.):
    TH.validate(k, temperature, state, action, order)
    if channel not in ("pair", "Landau"):
        raise ValueError("declared pair or Landau channel required")
    ek, c = TH.energy_value(k, state, action), INT.dispersion_coefficients(state, action)["c"]
    if channel == "Landau" and temperature == 0:
        return {"gamma_pole": 0., "Gamma_occupation": 0., "zero_T_limit": True}
    if channel == "pair":
        nodes, weights = np.polynomial.legendre.leggauss(order)
        radial = [(k*(z+1)/2, k*w/2) for z, w in zip(nodes, weights)]
    else:
        radial = [(temperature*x/c, temperature*w/c) for x, w in TH.radial_nodes(order, tail)]
    result, balance, supports, bose_checks = 0., [], [], []
    for p, weight in radial:
        if channel == "pair":
            r, cosine = pair_root(k, p, state, action)
            signs = (1, -1, -1)
        else:
            r, _, _, cosine, _ = TH.landau_root(k, p, state, action)
            signs = (1, 1, -1)
        ep, er = TH.energy_value(p, state, action), TH.energy_value(r, state, action)
        thermal = TH.thermal_weights(ep, er, ek, temperature, channel)
        projected = amplitude((k, p, r), signs, state, action)
        result += weight*p*r*abs(projected)**2*thermal["difference"]/(ep*er*INT.group_velocity(r, state, action))
        balance.append(abs(ek-ep-er)/ek if channel == "pair" else abs(ek+ep-er)/ek)
        supports.append(1-abs(cosine))
        bose_checks.append(max(thermal["KMS_ratio_error"], thermal["FDT_error"]))
    gamma = float(result/(pi*ek*k*(64 if channel == "pair" else 32)))
    return {"gamma_pole": gamma, "Gamma_occupation": 2*gamma,
            "support_margin_min": min(supports), "energy_residual_max": max(balance),
            "Bose_identity_error_max": max(bose_checks)}


def residue_matrix_check(q, state, action, offset):
    item = mode(q, state, action)
    e2 = item["omega"]**2
    measured = []
    for sign in (-1, 1):
        z = e2*(1+sign*offset)
        measured.append(float((-(z-e2)*np.linalg.inv(kernel(q, sqrt(z), state, action))[1, 1]).real))
    return INT.relative(sum(measured)/2, item["Z_pi"])


def audit():
    action, rows = EFT.controls(), []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        cf, vv = INT.dispersion_coefficients(state, action), INT.vertices(state, action)
        modes, vertices, vacua, thermal = [], [], [], []
        kp = action["epsilon"]*action["response_kinetic"]
        kinetic = np.diag([1., 1., kp])
        gyroscopic = np.array([[0., -2*mu, 0.], [2*mu, 0., 0.], [0., 0., 0.]])
        for q in Q_GRID:
            item = mode(q, state, action)
            u, e = item["polarization"], item["omega"]
            norm = np.vdot(u, (2*e*kinetic+1j*gyroscopic)@u)/(2*e)
            modes.append({"q": q, "Z_pi": item["Z_pi"], "positive_norm": item["N_pi"],
                          "parent_ledger": EFT.parent_energy_check(q, state, action),
                          "kernel_residual_over_q2": float(np.max(abs(kernel(q, e, state, action)@u))/q**2),
                          "symplectic_norm_error": float(abs(norm-1)),
                          "residue_errors": [residue_matrix_check(q, state, action, offset) for offset in RESIDUE_OFFSETS],
                          "low_q_residue_relative_error": INT.relative(item["Z_pi"], cf["c"]**2)})
            p = .37*q
            r, cosine = pair_root(q, p, state, action)
            projected, raw = amplitude((q, p, r), (1, -1, -1), state, action), amplitude((q, p, r), (1, -1, -1), state, action, False)
            lo = TH.vertex(e, TH.energy_value(p, state, action), TH.energy_value(r, state, action), q, p, cosine, vv)
            vertices.append({"q": q, "projected_absolute": float(abs(projected)),
                             "tensor_relative_error": INT.relative(raw, projected),
                             "LO_vertex_relative_error": INT.relative(abs(projected), abs(lo))})
            rates = [cut_rate(q, 0., state, action, "pair", order) for order in TH.ORDERS]
            vacua.append({"q": q, "runs": rates,
                          "quadrature_error": INT.relative(rates[-2]["gamma_pole"], rates[-1]["gamma_pole"]),
                          "q5_coefficient_error": INT.relative(rates[-1]["gamma_pole"]/q**5, INT.decay_leading_coefficient(cf, vv)/2)})
        for divisor in TH.TEMPERATURE_DIVISORS:
            t = cf["c"]*cf["dispersion_scale"]/divisor
            for ratio in TH.SOFT_RATIOS:
                q = ratio*t/cf["c"]
                pair = [cut_rate(q, t, state, action, "pair", order) for order in TH.ORDERS]
                landau = [cut_rate(q, t, state, action, "Landau", order) for order in TH.ORDERS]
                tails = [cut_rate(q, t, state, action, "Landau", TH.ORDERS[-1], tail) for tail in (32., 40.)]
                previous = TH.landau_rate(q, t, state, action)
                thermal.append({"T": t, "q": q, "temperature_divisor": divisor, "cq_over_T": ratio,
                                "pair_runs": pair, "Landau_runs": landau,
                                "pair_quadrature_error": INT.relative(pair[-2]["gamma_pole"], pair[-1]["gamma_pole"]),
                                "Landau_quadrature_error": INT.relative(landau[-2]["gamma_pole"], landau[-1]["gamma_pole"]),
                                "tail_error": INT.relative(tails[0]["gamma_pole"], tails[1]["gamma_pole"]),
                                "modal_to_LO_Landau_ratio": landau[-1]["gamma_pole"]/previous["gamma_pole"],
                                "soft_coefficient_error": INT.relative(landau[-1]["gamma_pole"]/(q*t**4), TH.soft_landau_coefficient(cf["c"], vv))})
        rows.append({"mu": mu, "tree_state": state, "mode_checks": modes, "vertex_checks": vertices,
                     "vacuum_cuts": vacua, "thermal_cuts": thermal,
                     "potential_tensor_errors": [tensor_potential_check(state, action, step) for step in FD_STEPS]})
    checks = {
        "positive_symplectic_norm_and_kernel": all(x["positive_norm"] > 0 and max(x["symplectic_norm_error"], x["kernel_residual_over_q2"]) < GATES["identity_relative"] for r in rows for x in r["mode_checks"]),
        "residue_independent_matrix_pole": all(x["residue_errors"][-1] < GATES["residue_relative"] for r in rows for x in r["mode_checks"]),
        "cubic_tensor_from_full_shifted_potential": all(max(r["potential_tensor_errors"]) < GATES["potential_derivative_relative"] for r in rows),
        "cancellation_free_vertex_matches_tensor": all(x["tensor_relative_error"] < GATES["tensor_relative"] for r in rows for x in r["vertex_checks"]),
        "low_q_vertex_residue_and_vacuum_rate_match_EFT": all(max(r["vertex_checks"][-1]["LO_vertex_relative_error"], r["mode_checks"][-1]["low_q_residue_relative_error"], r["vacuum_cuts"][-1]["q5_coefficient_error"]) < GATES["low_q_relative"] and r["vertex_checks"][-1]["LO_vertex_relative_error"] < r["vertex_checks"][0]["LO_vertex_relative_error"] for r in rows),
        "modal_cut_quadrature_and_tail": all(max(x["pair_quadrature_error"], x["Landau_quadrature_error"]) < GATES["quadrature_relative"] and x["tail_error"] < GATES["tail_relative"] for r in rows for x in r["thermal_cuts"]),
        "strict_support_energy_and_positive_modal_rates": all(x["support_margin_min"] > 0 and max(x["energy_residual_max"], x["Bose_identity_error_max"]) < GATES["identity_relative"] and x["gamma_pole"] > 0 for r in rows for t in r["thermal_cuts"] for x in t["pair_runs"]+t["Landau_runs"]),
        "unchanged_positive_parent_energy_ledger": all(x["parent_ledger"]["energy_conservation_residual"] < GATES["identity_relative"] and x["parent_ledger"]["potential_min_eigenvalue"] > 0 for r in rows for x in r["mode_checks"]),
        "modal_soft_Landau_recovers_independent_Bose_limit": all(r["thermal_cuts"][-1]["soft_coefficient_error"] < GATES["low_q_relative"] and r["thermal_cuts"][-1]["soft_coefficient_error"] < r["thermal_cuts"][2]["soft_coefficient_error"] for r in rows)}
    paths = [str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), REGISTRY,
             PREFIX+"Code/03_Research/test_t13_acoustic_modal_cuts.py",
             PREFIX+"Code/03_Research/Research_T13_Thermal_Cut_Stiffness.py"]
    protected = [PREFIX+"Result/artifacts/t13_thermal_cut_stiffness.json", PREFIX+"Result/artifacts/t13_vacuum_cut_log.json",
                 PREFIX+"Result/artifacts/t13_low_T_interactions.json", PREFIX+"Result/artifacts/t13_low_T_phase_eft.json"]+list(EFT.ACTION_PATHS)
    record = {"major_result_id": "T13_ACOUSTIC_TREE_MODAL_CUT_MATCHING", "topic": "0.13_Thermodynamic_Bridge", "branch_id": EFT.BRANCH,
              "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
              "verification_status": "PASS_SCOPED_ACOUSTIC_MODAL_CUT" if all(checks.values()) else "FAIL_SCOPED_ACOUSTIC_MODAL_CUT",
              "created_at": datetime.now(timezone.utc).isoformat(), "action_controls": action,
              "what_is_closed": "Acoustic tree pole residue, full shifted-parent cubic projection and pair/Landau cuts restricted to three acoustic legs",
              "equation_or_mapping": "Z_pi=[1+4mu2/den+A2+epsilon ZPhi B2]^-1; M_aaa=T_ijk u_i u_j u_k; modal cuts use |M_aaa|2",
              "units": {"q_omega_T": "E", "kernel": "E^2", "Z_pi_polarization": "1", "cubic_tensor_amplitude": "E", "gamma_pole": "E"},
              "derivation_class": "TREE_PARENT_SPECTRAL_RESIDUE_AND_ACOUSTIC_CUBIC_MATCHING",
              "observable": "Conditional acoustic three-wave attenuation, not material/source response", "data_role": "DERIVED_NOT_CALIBRATION",
              "equation_registry_ids": [x["id"] for x in json.loads((ROOT/REGISTRY).read_text())["entries"]],
              "checks": checks, "thresholds": GATES, "examples": rows,
              "declared_grids": {"mu": MU_GRID, "q": Q_GRID, "FD_steps": FD_STEPS, "residue_offsets": RESIDUE_OFFSETS,
                                 "temperature_divisors": TH.TEMPERATURE_DIVISORS, "cq_over_T": TH.SOFT_RATIOS,
                                 "orders": TH.ORDERS, "thermal_tails": [32., 40.], "locked_before_first_audit": True},
              "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected),
              "ontology": {"parent_radial_and_phase_are_collective_C": False, "phase_is_UET_Pi": False, "heavy_polarization_adds_independent_R_gen": False, "excluded_variables": ["C", "R_gen", "R_obs"]},
              "controlling_blocker": "off_shell_source_real_matching_and_complete_thermal_sunset_open",
              "open_blockers": ["full_off_shell_source_contact_and_local_real_matching", "complete_quantum_heavy_and_thermal_sunset_pressure_source_entropy", "finite_T_normal_heat_Kubo_KMS_transport", "independent_material_readout_scale_and_uncertainty"],
              "dependency_unlocked": ["off_shell_matching_and_thermal_sunset_research_only"],
              "acoustic_tree_residues_and_cubic_vertex_matched": True,
              "all_parent_modes_and_quantum_Phi_loops_included": False, "full_off_shell_source_matching_closed": False,
              "full_real_self_energy_matched": False, "full_two_loop_pressure_computed": False,
              "full_finite_T_collision_operator_computed": False, "full_SK_KMS_matching_closed": False,
              "controlled_full_action_truncation_error_established": False, "independent_alpha_Phi_K_admitted": False,
              "physical_Kubo_emitted": False, "g1_physical_unlock": False, "g2_science_unlock": False,
              "full_core_unlock": False, "core_composition_gate_overwritten": False, "claim_promotion": False,
              "parameter_fitting": False, "assigned_damping_width": False, "clipping": False, "cone_padding": False,
              "target_source_accessed": False, "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
              "primary_references": ["https://www.fuw.edu.pl/~derezins/damping_publ.pdf"],
              "claim_boundary": "Tree-reduced acoustic residue/cubic/cut matching only, not all-mode loops, full quantum Phi, off-shell source/contact/local real matching, complete thermal pressure/transport/uncertainty, material prediction or Full Topic13/Core. Heavy components remain tree-slaved; old conserved-C blocked at1e-6 and owner Core unchanged."}
    names = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(names, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Matched tree acoustic residue and parent cubic, predecessor preserved", record["equation_or_mapping"], checks, record["controlling_blocker"], "Derive off-shell source/local real matching and complete thermal sunset/source/entropy with independent input design", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    record = audit()
    OUTPUT.write_bytes((json.dumps(record, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": record["verification_status"], "checks": record["checks"],
                      "examples": [{"mu": r["mu"], "LO_vertex_error": r["vertex_checks"][-1]["LO_vertex_relative_error"], "soft_error": r["thermal_cuts"][-1]["soft_coefficient_error"], "modal_to_LO_Landau_ratio": r["thermal_cuts"][-1]["modal_to_LO_Landau_ratio"]} for r in record["examples"]]}, indent=2))
    raise SystemExit(0 if all(record["checks"].values()) else 1)
