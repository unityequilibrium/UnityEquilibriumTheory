"""Even cyclic-work hierarchy and a conservative finite-pair remainder.

This is the predecessor's fixed two-block Gaussian Hamiltonian, not a
nonlinear completion of the UET parent action or a physical heat model.
Coefficients are evolved as derivatives at zero; no amplitude fit is used.
"""

from datetime import datetime, timezone
import hashlib
import json
from math import isfinite, sqrt
from pathlib import Path
import sys

import mpmath as mp
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import block_diag

ROOT = Path(__file__).resolve().parents[5]
LOCAL = Path(__file__).resolve().parent
if str(LOCAL) not in sys.path:
    sys.path.insert(0, str(LOCAL))
import Research_T13_Gaussian_Source_Work as WORK

FQ, VIRT, EFT, TH, MOD, PREFIX = WORK.FQ, WORK.VIRT, WORK.EFT, WORK.TH, WORK.MOD, WORK.PREFIX
PREDECESSOR = PREFIX+"Result/artifacts/t13_gaussian_source_work.json"
PREDECESSOR_SHA = "959441d2940f0aa209d72b8f8671d440807dd14ae9a80aff4357606f3bce4c62"
REGISTRY = PREFIX+"Data/03_Research/t13_gaussian_work_remainder_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_gaussian_work_remainder.json")
FIRST_FAILURE = ROOT/(PREFIX+"Result/artifacts/t13_gaussian_work_remainder_first_failure.json")
# Locked before the first audit; the old pulse/amplitudes/gates are untouched.
COEFFICIENT_ORDERS = (2, 4, 6)
SOLVERS = (dict(WORK.SOLVERS[1]), {"rtol": 2.5e-12, "atol": 2.5e-15, "max_step": .125})
GATES = {"coefficient_resolution_scaled": 1e-6, "coefficient_ledger_scaled": 1e-6,
         "finite_grid_prediction_relative": 1e-5, "algebraic_relative": 1e-10,
         "sampled_majorant_relative": 1e-10, "negative_control_minimum": .1,
         "linear_relative_tolerance": .01, "original_causal_leakage": 1e-6}


def load_predecessor():
    raw = (ROOT/PREDECESSOR).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PREDECESSOR_SHA:
        raise ValueError("predecessor identity changed; revalidate instead of reusing")
    result = json.loads(raw)
    if result["closure_level"] != "PARTIAL" or result["verification_status"] != "FAIL_SCOPED_GAUSSIAN_SOURCE_WORK":
        raise ValueError("the retained finite-amplitude failure must remain visible")
    if result["declared_protocol"]["amplitudes"] != list(WORK.AMPLITUDES):
        raise ValueError("no amplitude tuning allowed")
    return result


def ingredients(p, r, q, temperature, state, action):
    WORK.NOE.geometry(p, r, q)
    FQ.validate(p, r, temperature, state, action)
    ap, cp = FQ.evolution_and_covariance(p, temperature, state, action)
    ar, cr = FQ.evolution_and_covariance(r, temperature, state, action)
    kinetic, _, vp = VIRT.matrices(p, state, action)
    vr = VIRT.matrices(r, state, action)[2]
    hp, hr = block_diag(vp, kinetic), block_diag(vr, kinetic)
    return ap, ar, cp, cr, hp, hr, np.linalg.inv(kinetic), MOD.cubic_tensor(state, action)


def perturbation(t, q, state, action, inverse_kinetic, cubic):
    b, velocity, _, _ = WORK.source_path(t, q, state, action)
    vertex = np.einsum("ijk,k->ij", cubic, b)
    derivative = np.einsum("ijk,k->ij", cubic, velocity)
    delta_a = np.zeros((6, 6))
    delta_a[3:, :3] = -inverse_kinetic@vertex
    return delta_a, derivative


def hierarchy(p, r, q, temperature, state, action, solver=1, order=6):
    if order not in COEFFICIENT_ORDERS or solver not in (0, 1):
        raise ValueError("declared even orders and solver levels only")
    ap, ar, cp0, cr0, hp, hr, invk, cubic = ingredients(p, r, q, temperature, state, action)
    offsets, size = {}, 0
    for n in range(1, order+1):
        offsets[n] = size
        size += 36 if n % 2 else 72
    even = tuple(range(2, order+1, 2))

    def rhs(t, y):
        delta_a, vdot = perturbation(t, q, state, action, invk, cubic)
        result = np.zeros_like(y)
        for n in range(1, order+1):
            start = offsets[n]
            if n % 2:
                cross = y[start:start+36].reshape(6, 6)
                if n == 1:
                    cp, cr = cp0, cr0
                else:
                    last = offsets[n-1]
                    cp, cr = y[last:last+36].reshape(6, 6), y[last+36:last+72].reshape(6, 6)
                derivative = ar@cross+cross@ap.T+delta_a@cp+cr@delta_a.T
                result[start:start+36] = derivative.ravel()
            else:
                cp, cr = y[start:start+36].reshape(6, 6), y[start+36:start+72].reshape(6, 6)
                last = offsets[n-1]
                cross = y[last:last+36].reshape(6, 6)
                dp = ap@cp+cp@ap.T+delta_a@cross+cross.T@delta_a.T
                dr = ar@cr+cr@ar.T+delta_a@cross.T+cross@delta_a.T
                result[start:start+36], result[start+36:start+72] = dp.ravel(), dr.ravel()
                result[size+even.index(n)] = np.sum(vdot*cross[:3, :3])
        return result

    solution = solve_ivp(rhs, (0., WORK.DURATION), np.zeros(size+len(even)), method="DOP853", **SOLVERS[solver])
    if not solution.success or not np.all(np.isfinite(solution.y)):
        raise RuntimeError("coefficient hierarchy failed")
    rows = []
    for n in even:
        start = offsets[n]
        cp, cr = solution.y[start:start+36, -1].reshape(6, 6), solution.y[start+36:start+72, -1].reshape(6, 6)
        work = float(solution.y[size+even.index(n), -1])
        energy = float(.5*np.sum(hp*cp)+.5*np.sum(hr*cr))
        rows.append({"order": n, "work_coefficient": work, "energy_coefficient": energy,
                     "endpoint_symmetry_relative": max(VIRT.matrix_error(cp, cp.T), VIRT.matrix_error(cr, cr.T))})
    scale = max(abs(x["work_coefficient"]) for x in rows if x["order"] >= 4) if order >= 4 else 1.
    for row in rows:
        row["ledger_scaled_error"] = abs(row["work_coefficient"]-row["energy_coefficient"])/(scale or 1.)
    return {"coefficients": rows, "function_evaluations": solution.nfev, "finite_amplitude_fit_used": False,
            "order_two_cancellation_not_relabelled": True, "scale_for_order_four_and_six": scale}


def tone_vertex(coefficient, frequency, q, state, action):
    f, nu = coefficient, frequency
    mu, gv = state["mu"], action["gamma"]*sqrt(state["s"])
    u2 = 2*action["u"]*state["s"]
    sigma = (nu*nu-q*q)*f/(2*mu)
    b = np.array([sigma, -1j*nu*f, ((u2+q*q-nu*nu)*sigma+2*mu*nu*nu*f)/gv])
    return np.einsum("ijk,k->ij", MOD.cubic_tensor(state, action), b)


def norm_majorant(p, r, q, temperature, state, action):
    ap, ar, cp, cr, hp, hr, invk, cubic = ingredients(p, r, q, temperature, state, action)
    h0, c0, a0 = block_diag(hp, hr), block_diag(cp, cr), block_diag(ap, ar)
    energy_factor = np.linalg.cholesky(h0).T
    inverse_factor = np.linalg.inv(energy_factor)
    parity = block_diag(np.eye(6), -np.eye(6))
    samples, norms = [], []
    for coefficient, frequency in WORK.tones():
        for nu in (frequency, -frequency):
            vertex = tone_vertex(coefficient/2, nu, q, state, action)
            delta_a = np.zeros((6, 6), dtype=complex)
            delta_a[3:, :3] = -invk@vertex
            a1 = np.block([[np.zeros((6, 6)), delta_a], [delta_a, np.zeros((6, 6))]])
            norms.append(float(np.linalg.norm(energy_factor@a1@inverse_factor, 2)))
    summed = sum(norms)
    left, right = a0.T@h0, h0@a0
    algebra = float(np.linalg.norm(left+right)/max(np.linalg.norm(left), np.linalg.norm(right), 1e-30))
    # The all-time bound follows from the tone triangle inequality, not samples.
    for t in np.linspace(0., WORK.DURATION, 33):
        delta_a, _ = perturbation(float(t), q, state, action, invk, cubic)
        a1 = np.block([[np.zeros((6, 6)), delta_a], [delta_a, np.zeros((6, 6))]])
        samples.append({"t": float(t), "norm_to_majorant": float(np.linalg.norm(energy_factor@a1@inverse_factor, 2)/summed),
                        "odd_generator_parity_error": VIRT.matrix_error(parity@a1@parity, -a1)})
    energy = float(.5*np.sum(h0*c0))
    return {"eta_upper": WORK.DURATION*summed, "initial_pair_rotating_energy": energy,
            "tone_norm_sum": summed, "energy_metric_min_eigenvalue": float(np.linalg.eigvalsh(h0)[0]),
            "free_energy_skew_error": algebra,
            "initial_state_parity_error": VIRT.matrix_error(parity@c0@parity, c0),
            "energy_parity_error": VIRT.matrix_error(parity@h0@parity, h0),
            "free_generator_parity_error": VIRT.matrix_error(parity@a0@parity, a0),
            "samples": samples, "all_time_bound_is_derived_not_sample_certified": True,
            "reported_numeric_bound_is_interval_certified": False}


def even_remainder(energy, eta, amplitude, through_order):
    if not all(isfinite(x) for x in (energy, eta, amplitude)) or energy < 0 or eta < 0:
        raise ValueError("finite nonnegative energy/norm and finite amplitude required")
    if not isinstance(through_order, int) or through_order < 0 or through_order % 2:
        raise ValueError("nonnegative even truncation order required")
    ctx = mp.mp.clone()
    ctx.dps = 60
    x = 2*abs(ctx.mpf(str(amplitude)))*ctx.mpf(str(eta))
    # Positive tail evaluation avoids cancellation of cosh minus its polynomial.
    start = through_order+2
    term, tail, n = x**start/ctx.factorial(start), ctx.mpf(0), start
    for _ in range(10000):
        tail += term
        n += 2
        term *= x*x/(n*(n-1))
        if abs(term) <= abs(tail)*ctx.mpf("1e-55") or term == 0:
            break
    else:
        raise RuntimeError("even norm tail failed to converge")
    result = ctx.mpf(str(energy))*tail
    if result > ctx.mpf(str(np.finfo(float).max)):
        return {"value": None, "log10_value": float(ctx.log10(result)), "overflow_in_binary64": True}
    return {"value": float(result), "log10_value": float(ctx.log10(result)) if result else None, "overflow_in_binary64": False}


def sufficient_linear_amplitude(energy, eta, leading, tolerance=GATES["linear_relative_tolerance"]):
    if not all(isfinite(x) and x > 0 for x in (energy, eta, leading, tolerance)):
        raise ValueError("positive finite energy, norm, leading work and tolerance required")
    ctx = mp.mp.clone()
    ctx.dps = 60
    e, norm, w, tol = [ctx.mpf(str(x)) for x in (energy, eta, leading, tolerance)]
    limit = min(1/(2*norm), ctx.sqrt(24*tol*w/(e*ctx.cosh(1)*(2*norm)**4)))
    return {"amplitude_upper_evaluated": float(limit),
            "formula": "min(1/(2eta),sqrt(24*tol*W2/(E0*cosh(1)*(2eta)^4)))",
            "conditional_on_exact_positive_W2": True, "numeric_interval_certificate": False,
            "selected_from_target_work": False}


def prediction(leading, coefficients, amplitude):
    if not isfinite(amplitude):
        raise ValueError("finite amplitude required")
    by_order = {x["order"]: x["work_coefficient"] for x in coefficients}
    return float(amplitude**2*leading+sum(amplitude**n*value for n, value in by_order.items() if n >= 4))


def audit():
    previous, action, rows = load_predecessor(), EFT.controls(), []
    for baseline in previous["examples"]:
        mu, p, r, q, temperature = [baseline[k] for k in ("mu", "p", "r", "q", "T")]
        state = EFT.tree_state(mu, action=action)
        coarse = hierarchy(p, r, q, temperature, state, action, 0)
        fine = hierarchy(p, r, q, temperature, state, action, 1)
        majorant = norm_majorant(p, r, q, temperature, state, action)
        leading = baseline["extended_leading"]["modal_work"]
        limit = sufficient_linear_amplitude(majorant["initial_pair_rotating_energy"], majorant["eta_upper"], leading)
        scale = max(coarse["scale_for_order_four_and_six"], fine["scale_for_order_four_and_six"])
        resolutions = [abs(a["work_coefficient"]-b["work_coefficient"])/scale for a, b in zip(coarse["coefficients"][1:], fine["coefficients"][1:])]
        comparisons = []
        for cycle in baseline["cycles"]:
            epsilon = cycle["amplitude"]
            predicted = prediction(leading, fine["coefficients"], epsilon)
            bound = even_remainder(majorant["initial_pair_rotating_energy"], majorant["eta_upper"], epsilon, 6)
            comparisons.append({"amplitude": epsilon, "predicted_work_through_six": predicted,
                                "predecessor_exact_flow_work": cycle["work"],
                                "prediction_relative_error": WORK.relative(predicted, cycle["work"]),
                                "formal_even_remainder_bound": bound,
                                "inside_sufficient_linear_domain": epsilon <= limit["amplitude_upper_evaluated"]})
        rows.append({"mu": mu, "p": p, "r": r, "q": q, "T": temperature,
                     "hierarchy": fine, "coefficient_resolution_scaled": resolutions,
                     "leading_coefficient_from_predecessor": leading,
                     "order_two_hierarchy_relative_error_reported": WORK.relative(fine["coefficients"][0]["work_coefficient"], leading),
                     "norm_majorant": majorant, "sufficient_linear_domain": limit, "comparisons": comparisons})
    state = EFT.tree_state(WORK.MU_GRID[0], action=action)
    negative = WORK.exact_cycle(*WORK.MOMENTUM_TRIPLES[0], WORK.TEMPERATURE, state, action, -WORK.AMPLITUDES[0])
    positive = previous["examples"][0]["cycles"][0]
    sign_error = WORK.relative(positive["work"], negative["work"])
    toy_energy, toy_eta, toy_amplitude = 1., 1., .1
    toy_tail = even_remainder(toy_energy, toy_eta, toy_amplitude, 2)["value"]
    ctx = mp.mp.clone()
    ctx.dps = 60
    toy_actual_tail = float(ctx.cosh(ctx.mpf(".2"))-1-ctx.mpf(".2")**2/2)
    checks = {
        "parity_and_positive_energy_metric": all(x["norm_majorant"]["energy_metric_min_eigenvalue"] > 0 and max(x["norm_majorant"][name] for name in ("free_energy_skew_error", "initial_state_parity_error", "energy_parity_error", "free_generator_parity_error")) < GATES["algebraic_relative"] and all(s["odd_generator_parity_error"] < GATES["algebraic_relative"] for s in x["norm_majorant"]["samples"]) for x in rows),
        "coefficient_refinement_orders_four_six": all(max(x["coefficient_resolution_scaled"]) < GATES["coefficient_resolution_scaled"] for x in rows),
        "order_four_six_energy_work_ledger": all(max(c["ledger_scaled_error"] for c in x["hierarchy"]["coefficients"][1:]) < GATES["coefficient_ledger_scaled"] for x in rows),
        "independent_exact_flow_grid_comparison": all(c["prediction_relative_error"] < GATES["finite_grid_prediction_relative"] for x in rows for c in x["comparisons"]),
        "sign_reversal_control": sign_error < GATES["algebraic_relative"],
        "tone_majorant_implementation": all(max(s["norm_to_majorant"] for s in x["norm_majorant"]["samples"]) <= 1+GATES["sampled_majorant_relative"] for x in rows),
        "even_tail_known_saturating_control": WORK.relative(toy_tail, toy_actual_tail) < GATES["algebraic_relative"],
        "old_failure_and_protocol_retained": previous["closure_level"] == "PARTIAL" and not all(previous["checks"].values()) and previous["declared_protocol"]["amplitudes"] == list(WORK.AMPLITUDES)}
    passed = all(checks.values())
    paths = [str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), REGISTRY, PREFIX+"Code/03_Research/test_t13_gaussian_work_remainder.py"]
    protected = [PREDECESSOR, PREFIX+"Result/artifacts/t13_gaussian_source_work_first_failure.json", PREFIX+"Code/03_Research/Research_T13_Gaussian_Source_Work.py", PREFIX+"Result/artifacts/t13_collisionless_soft_source.json"]+list(EFT.ACTION_PATHS)
    record = {"major_result_id": "T13_FINITE_PAIR_CYCLIC_WORK_PARITY_AND_REMAINDER", "topic": "0.13_Thermodynamic_Bridge", "branch_id": VIRT.BRANCH,
              "created_at": datetime.now(timezone.utc).isoformat(), "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
              "verification_status": "PASS_SCOPED_GAUSSIAN_WORK_REMAINDER" if passed else "FAIL_SCOPED_GAUSSIAN_WORK_REMAINDER",
              "what_is_closed": "Finite two-block even-work coefficient hierarchy, observed quartic domination and conditional Peano-Baker remainder formula when recorded checks pass; no useful original-grid certificate inferred",
              "equation_or_mapping": "C_n'=A0 C_n+C_n A0^T+A1 C_(n-1)+C_(n-1) A1^T; W(epsilon)=sum W_(2k) epsilon^(2k); |R_2N|<=E0 sum_(k>N)(2|epsilon|eta)^(2k)/(2k)!",
              "units": {"amplitude": "dimensionless", "W_coefficients": "E per internal pair", "energy_frame": "rotating_Gaussian_Hamiltonian", "eta": "dimensionless integral of energy-metric generator norm", "physical_SI_measure_or_temperature": "not admitted"},
              "derivation_class": "DERIVED_COVARIANCE_TAYLOR_HIERARCHY_PARITY_AND_ENERGY_METRIC_PEANO_BAKER_MAJORANT", "observable": "conditional finite-pair cyclic work and approximation bound", "data_role": "DERIVED_AND_DIAGNOSTIC_ONLY_KNOWN_CONTROL",
              "declared_protocol": {"inherited_source_artifact_sha256": PREDECESSOR_SHA, "pulse_and_amplitudes_unchanged": True, "orders": COEFFICIENT_ORDERS, "solvers": SOLVERS, "locked_before_first_audit": True, "negative_amplitude_control": -WORK.AMPLITUDES[0]},
              "action_controls": action, "thresholds": GATES, "checks": checks, "examples": rows, "sign_reversal_error": sign_error,
              "known_control": {"role": "DIAGNOSTIC_ONLY_NOT_DATA_OR_CALIBRATION", "system": "A0=0,A1=sigma_x,C0=I; W=cosh(2epsilon*eta)-1", "remainder": toy_tail, "exact_remainder": toy_actual_tail},
              "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected),
              "equation_registry_ids": [x["id"] for x in json.loads((ROOT/REGISTRY).read_text())["entries"]],
              "controlling_blocker": "physical_source_readout_scale_and_parent_interaction_remainder_open" if passed else "finite_pair_work_hierarchy_verification_open",
              "open_blockers": ["conservative_bound_not_a_useful_original_grid_certificate", "numeric_bound_not_interval_certified", "nonlinear_parent_action_not_completed_by_quadratic_control", "actual_material_heat_readout_independent_scale_and_transport"],
              "dependency_unlocked": ["source_readout_identifiability_and_controlled_parent_remainder_research_only"] if passed else [],
              "finite_pair_even_work_hierarchy_verified": passed, "formal_finite_pair_remainder_formula_derived": True,
              "useful_linear_certificate_on_original_grid": False, "numeric_bound_interval_certified": False,
              "old_source_work_audit_promoted": False, "finite_amplitude_fit_used": False,
              "full_energy_exchange_ledger_closed": False, "nonlinear_parent_action_completed": False,
              "full_collision_operator_computed": False, "physical_Kubo_emitted": False, "full_SK_KMS_matching_closed": False,
              "independent_alpha_Phi_K_admitted": False, "controlled_full_action_truncation_error_established": False,
              "full_core_unlock": False, "core_composition_gate_overwritten": False,
              "state_variables": ["radial_phase_Phi_fluctuations_velocities_covariance_coefficients"], "excluded_variables": ["C", "UET_Pi", "R_gen", "R_obs"],
              "primary_covariance_entropy_defined": False, "quantum_vacuum_population_added": False,
              "parameter_fitting": False, "assigned_width": False, "assigned_relaxation_time": False,
              "clipping": False, "cone_padding": False, "claim_promotion": False, "xie_2026_accessed": False,
              "prior_Xie_context_exposure_review": "REVIEW_REQUIRED", "primary_references": ["https://www.math.uni-bielefeld.de/baake/ps/peano-baker.pdf", "https://arxiv.org/abs/1011.1775"],
              "claim_boundary": "Fixed finite two-block Gaussian rotating-energy Taylor coefficients and formal conservative remainder only. Numeric norm/coefficients are not interval certified and a loose bound is not original-grid or material error control. Old FAIL remains; no nonlinear UET parent, complete quantum/physical heat/collision/KMS/entropy/SI mapping or Full Topic13/Core/global closure."}
    fields = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(fields, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Derived even-work hierarchy and conservative remainder without fitting", record["equation_or_mapping"], checks, record["controlling_blocker"], "Independent source/readout scale and controlled nonlinear parent remainder, not tuning the failed pulse grid", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    result = audit()
    raw = (json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8")
    OUTPUT.write_bytes(raw)
    if not all(result["checks"].values()) and not FIRST_FAILURE.exists():
        FIRST_FAILURE.write_bytes(raw)
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"]}, indent=2))
    raise SystemExit(0 if all(result["checks"].values()) else 1)
