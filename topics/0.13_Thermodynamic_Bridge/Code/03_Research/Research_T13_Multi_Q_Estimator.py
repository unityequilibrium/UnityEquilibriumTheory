"""Three-node coefficient estimator, covariance and conditional tree budget.

Interpolation of derived controls is not acquired material calibration.
Exact bounded-error requirements exclude physical q/resolution/state errors.
"""

from datetime import datetime, timezone
from fractions import Fraction as F
from itertools import product
import hashlib
import json
from pathlib import Path
import sys

import mpmath as mp

LOCAL = Path(__file__).resolve().parent
sys.path.insert(0, str(LOCAL))
import Research_T13_Q5_Dispersion_Information as Q

ROOT, PREFIX, TH = Q.ROOT, Q.PREFIX, Q.TH
PREDECESSOR = PREFIX+"Result/artifacts/t13_q5_dispersion_information.json"
PREDECESSOR_SHA = "c4b23308c1ffdc45215cdba8d1fb0e3ba8b44c861d8c2c402bec22b3055a6485"
REGISTRY = PREFIX+"Data/03_Research/t13_multi_q_estimator_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_multi_q_estimator.json")
FIRST_FAILURE = OUTPUT.with_name("t13_multi_q_estimator_first_failure.json")
MU_GRID, Q_MAX_GRID, RATIOS = (1.05, 1.2), (.04, .02, .01, .005, .0025), (F(1), F(1, 2), F(1, 4))
ROOT_DIGITS, ESTIMATOR_DIGITS, FD_STEP, BUDGET_STEPS = 80, (70, 100), "1e-24", 96
AXIS_SCALES, TARGET = (F(1, 2), F(2)), F(1, 100)
GATES = {"estimator_relative": 1e-45, "jacobian_relative": 1e-8, "original_causal_leakage": 1e-6}
MAX_INTEGER_BITS, MAX_DECIMAL_DIGITS = 332000, 100000


def integer_decimal(value):
    if abs(value).bit_length() > MAX_INTEGER_BITS:
        raise ValueError("rational witness exceeds bounded serialization size")
    # Preserve the decimal wire format without changing Python's global limit.
    sign, chunks, value = "-" if value < 0 else "", [], abs(value)
    while value:
        value, chunk = divmod(value, 10**9)
        chunks.append(chunk)
    if not chunks:
        return "0"
    return sign+str(chunks[-1])+"".join(f"{c:09d}" for c in reversed(chunks[:-1]))


def decimal_integer(value):
    negative = value.startswith("-")
    digits = value[1:] if negative else value
    if not digits or len(digits) > MAX_DECIMAL_DIGITS or any(c not in "0123456789" for c in digits):
        raise ValueError("bounded ASCII decimal integer required")
    result = 0
    for start in range(0, len(digits), 9):
        chunk = digits[start:start+9]
        result = result*10**len(chunk)+int(chunk)
    if result.bit_length() > MAX_INTEGER_BITS:
        raise ValueError("rational witness exceeds bounded serialization size")
    return -result if negative else result


def fraction_record(value):
    return {"numerator": integer_decimal(value.numerator), "denominator": integer_decimal(value.denominator)}


def decode(value):
    return F(decimal_integer(value["numerator"]), decimal_integer(value["denominator"]))


def number(value):
    return mp.mpf(value.numerator)/value.denominator if isinstance(value, F) else mp.mpf(value)


def weights(qs):
    if len(qs) != 3 or len(set(qs)) != 3 or any(q <= 0 for q in qs):
        raise ValueError("three distinct positive momenta required")
    xs, out = [q*q for q in qs], [[], [], []]
    for i in range(3):
        j, k = [v for v in range(3) if v != i]
        denominator = (xs[i]-xs[j])*(xs[i]-xs[k])
        out[0].append(xs[j]*xs[k]/denominator)
        out[1].append(-(xs[j]+xs[k])/denominator)
        out[2].append(1/denominator)
    return out


def estimate(qs, energies):
    if len(energies) != 3 or any(e <= 0 for e in energies):
        raise ValueError("three positive energies required")
    ww = weights(qs)
    return [sum(w*e/q for w, e, q in zip(row, energies, qs)) for row in ww]


def newton_estimate(qs, energies):
    x, y = [q*q for q in qs], [e/q for e, q in zip(energies, qs)]
    d01, d12 = (y[1]-y[0])/(x[1]-x[0]), (y[2]-y[1])/(x[2]-x[1])
    zeta = (d12-d01)/(x[2]-x[0])
    eta = d01-zeta*(x[0]+x[1])
    return [y[0]-eta*x[0]-zeta*x[0]**2, eta, zeta]


def native_information(p):
    if p["g"] == 0:
        raise ValueError("decoupled Phi has no kinetic inference")
    z = Q.series(p)
    zero = Q.series(p | {"p": F(0), "A": F(1), "B": F(0)})
    return {"I": p["g"]**2*p["k"]/p["W"]**2, "s": p["s"],
            "r0": zero["j"]/zero["h"]**2,
            "D": (1-z["a"])**3*p["s"]*p["W"]/(2*z["a"]*p["N"]*p["g"]**2*zero["h"]**2)}


def ratio(beta):
    if beta[1] == 0:
        raise ValueError("nonzero cubic coefficient required")
    return beta[0]*beta[2]/beta[1]**2


def native_ratio(inv, native):
    return native["r0"]-native["D"]*(inv/(1+native["s"]*inv))**2


def inverse_ratio(value, native):
    n = {key: number(v) for key, v in native.items()}
    value = number(value)
    if not n["r0"]-n["D"]/n["s"]**2 < value < n["r0"]:
        return None
    tau = mp.sqrt((n["r0"]-value)/n["D"])
    return tau/(1-n["s"]*tau)


def log_data_jacobian(qs, energies, beta):
    ww = weights(qs)
    out = []
    for row in ww:
        energy = [w*e/q for w, e, q in zip(row, energies, qs)]
        momentum = [w*(-e/q-2*q*q*(beta[1]+2*beta[2]*q*q)) for w, e, q in zip(row, energies, qs)]
        out.append(energy+momentum)
    return out


def ratio_gradient(beta, jacobian):
    aa, bb, cc = beta
    grad = [cc/bb**2, -2*aa*cc/bb**3, aa/bb**2]
    return [sum(grad[k]*jacobian[k][i] for k in range(3)) for i in range(6)]


def profile(qs, p):
    z, ww = Q.series(p), weights(qs)
    errors = [decode(Q.tree_envelope(float(q), p)["normalized_energy_error_bound_exact"]) for q in qs]
    polynomial = [1+z["h"]*q*q+z["j"]*q**4 for q in qs]
    return {"u": [F(1), z["h"], z["j"]],
            "T": [sum(abs(w)*b for w, b in zip(row, errors)) for row in ww],
            "N": [sum(abs(w)*(poly+b) for w, poly, b in zip(row, polynomial, errors)) for row in ww]}


def target_box(prof, native, epsilon):
    if epsilon < 0:
        raise ValueError("nonnegative relative energy-error bound required")
    radii = [t+epsilon*n for t, n in zip(prof["T"], prof["N"])]
    lo, hi = [u-r for u, r in zip(prof["u"], radii)], [u+r for u, r in zip(prof["u"], radii)]
    if lo[0] <= 0 or lo[1] <= 0 or hi[2] >= 0:
        return {"certified": False, "classification": "SIGN_NOT_CERTIFIED"}
    rlo, rhi = hi[0]*lo[2]/lo[1]**2, lo[0]*hi[2]/hi[1]**2
    target_lo, target_hi = native_ratio(native["I"]*(1+TARGET), native), native_ratio(native["I"]*(1-TARGET), native)
    return {"certified": target_lo <= rlo and rhi <= target_hi,
            "classification": "TARGET_CERTIFIED" if target_lo <= rlo and rhi <= target_hi else "TARGET_NOT_CERTIFIED",
            "ratio_lower": rlo, "ratio_upper": rhi, "target_ratio_lower": target_lo, "target_ratio_upper": target_hi}


def budget(prof, native):
    zero = target_box(prof, native, F(0))
    if not zero["certified"]:
        return {"classification": "NO_POSITIVE_BUDGET_CERTIFIED_TREE_BIAS", "lower": F(0), "upper": F(0), "zero": zero}
    lo, hi = F(0), F(1)
    if target_box(prof, native, hi)["certified"]:
        raise ValueError("budget search upper endpoint must not be certified")
    for _ in range(BUDGET_STEPS):
        mid = (lo+hi)/2
        if target_box(prof, native, mid)["certified"]:
            lo = mid
        else:
            hi = mid
    return {"classification": "SUFFICIENT_ENERGY_ONLY_BUDGET_NOT_LAB_PRECISION", "lower": lo, "upper": hi, "zero": zero}


def differential_check(qs, energies, beta, native):
    jac = log_data_jacobian(qs, energies, beta)
    grad = ratio_gradient(beta, jac)
    with mp.workdps(100):
        analytic = [number(v) for v in grad]
        step, differences = mp.mpf(FD_STEP), []
        data = [number(v) for v in energies+qs]
        for index in range(6):
            plus, minus = list(data), list(data)
            plus[index] *= mp.exp(step)
            minus[index] *= mp.exp(-step)
            differences.append((ratio(newton_estimate(plus[3:], plus[:3]))-ratio(newton_estimate(minus[3:], minus[:3])))/(2*step))
        error = max(abs(a-b)/max(abs(a), mp.mpf("1e-50")) for a, b in zip(analytic, differences))
        inferred = inverse_ratio(ratio(beta), native)
        result = {"ratio_gradient_relative_error": float(error),
                  "energy_common_mode_null_exact": sum(grad[:3]) == 0,
                  "q_common_mode_null_exact": sum(grad[3:]) == 0,
                  "coefficient_energy_covariance_control_exact": all(sum(row[:3]) == b for row, b in zip(jac, beta)),
                  "coefficient_q_covariance_control_exact": all(sum(row[3:]) == -(1+2*k)*beta[k] for k, row in enumerate(jac)),
                  "ratio_log_data_gradient": [float(v) for v in grad],
                  "covariance_formula": "Sigma_beta=J_beta Sigma_log(E,q) J_beta^T; Var(I)=g_full^T Sigma_full g_full; no diagonal or measured Sigma assumed"}
        if inferred is None:
            return result | {"inference_classification": "OUTSIDE_POSITIVE_KINETIC_CLASS", "I_estimate": None, "I_relative_bias": None, "I_full_log_gradient": None}
        s, dd, r0 = [number(native[k]) for k in ("s", "D", "r0")]
        f = 1+s*inferred
        derivative = -f**3/(2*dd*inferred)
        data_grad = [derivative*v for v in analytic]
        native_grad = [-derivative*r0, -inferred*f/2, s*inferred*inferred]
        native_differences = []
        for key in ("r0", "D", "s"):
            plus, minus = dict(native), dict(native)
            plus[key] = number(native[key])*mp.exp(step)
            minus[key] = number(native[key])*mp.exp(-step)
            native_differences.append((inverse_ratio(ratio(beta), plus)-inverse_ratio(ratio(beta), minus))/(2*step))
        native_error = max(abs(a-b)/max(abs(a), mp.mpf("1e-50")) for a, b in zip(native_grad, native_differences))
        return result | {"inference_classification": "CONDITIONAL_POSITIVE_KINETIC_INVERSE",
                         "native_gradient_relative_error": float(native_error),
                         "I_estimate": float(inferred), "I_relative_bias": float(abs(inferred-number(native["I"]))/number(native["I"])),
                         "I_full_log_gradient": [float(v) for v in data_grad+native_grad],
                         "relative_I_independent_energy_noise_l2_gain": float(mp.sqrt(sum(v*v for v in data_grad[:3]))/inferred),
                         "gain_is_response_to_unit_covariance_control_not_instrument_noise": True}


def encoded_box(box):
    return {k: fraction_record(v) if isinstance(v, F) else v for k, v in box.items()}


def load_predecessor():
    raw = (ROOT/PREDECESSOR).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PREDECESSOR_SHA:
        raise ValueError("q5 predecessor identity changed")
    previous = json.loads(raw)
    if not all(previous["checks"].values()) or previous["physical_q5_measured"]:
        raise ValueError("scoped derived predecessor required")


def audit():
    load_predecessor()
    registry = json.loads((ROOT/REGISTRY).read_text())
    action, examples = Q.EFT.controls(), []
    for mu in MU_GRID:
        state = Q.EFT.tree_state(mu, action=action)
        p, rows, roots = Q.parameters(state, action), [], {}
        native, z = native_information(p), Q.series(p)
        for maximum in Q_MAX_GRID:
            qs = [Q.rational(maximum)*r for r in RATIOS]
            for q in qs:
                if q not in roots:
                    roots[q] = F(Q.high_precision_root_check(float(q), p, ROOT_DIGITS)["energy"])
            energies = [roots[q] for q in qs]
            beta, ww, prof = estimate(qs, energies), weights(qs), profile(qs, p)
            exact_monomials = all(sum(ww[k][i]*qs[i]**(2*j) for i in range(3)) == int(k == j) for k in range(3) for j in range(3))
            with mp.workdps(100):
                c = mp.sqrt(number(z["a"]))
                coefficient_errors = [abs(number(b)/c-number(u)) for b, u in zip(beta, prof["u"])]
                contained = all(error <= number(bound) for error, bound in zip(coefficient_errors, prof["T"]))
            precision_errors = []
            for digits in ESTIMATOR_DIGITS:
                with mp.workdps(digits):
                    other = newton_estimate([number(q) for q in qs], [number(e) for e in energies])
                    precision_errors.append(float(max(abs(a-number(b))/max(abs(number(b)), mp.mpf("1e-50")) for a, b in zip(other, beta))))
            differential, bd = differential_check(qs, energies, beta, native), budget(prof, native)
            axes = all(ratio(estimate([q*scale for q in qs], energies)) == ratio(beta) and ratio(estimate(qs, [e*scale for e in energies])) == ratio(beta) for scale in AXIS_SCALES)
            corners = True
            if bd["lower"] > 0:
                target_lo, target_hi = native_ratio(native["I"]*(1+TARGET), native), native_ratio(native["I"]*(1-TARGET), native)
                for signs in product((-1, 1), repeat=3):
                    perturbed = [e*(1+sign*bd["lower"]) for e, sign in zip(energies, signs)]
                    rr = ratio(estimate(qs, perturbed))
                    corners = corners and target_lo <= rr <= target_hi
            rows.append({"q_max": maximum, "q_grid": [float(q) for q in qs],
                         "derived_root_energies_rationalized_80_digit": [str(e) for e in energies],
                         "weights_exact": [[fraction_record(v) for v in row] for row in ww],
                         "estimated_coefficients": [float(b) for b in beta],
                         "monomial_identity_exact": exact_monomials, "independent_newton_relative_errors": precision_errors,
                         "coefficient_tree_bias_contained": contained, "coefficient_error_over_c": [float(e) for e in coefficient_errors],
                         "profile_exact": {k: [fraction_record(v) for v in values] for k, values in prof.items()},
                         "profile_bias_over_c": [float(v) for v in prof["T"]], "differential": differential,
                         "common_axis_ratio_invariant_exact": axes, "energy_noise_budget_classification": bd["classification"],
                         "sufficient_relative_energy_error_budget": float(bd["lower"]),
                         "budget_lower_exact": fraction_record(bd["lower"]), "budget_upper_exact": fraction_record(bd["upper"]),
                         "zero_noise_box": encoded_box(bd["zero"]), "budget_corner_controls_pass": corners,
                         "budget_lower_certified": target_box(prof, native, bd["lower"])["certified"],
                         "budget_upper_not_certified": not target_box(prof, native, bd["upper"])["certified"],
                         "physical_noise_or_precision_assigned": False})
        examples.append({"mu": mu, "native_information_exact": {k: fraction_record(v) for k, v in native.items()}, "rows": rows})
    rows = [r for e in examples for r in e["rows"]]
    checks = {"exact_interpolation_and_axis_invariance": all(r["monomial_identity_exact"] and r["common_axis_ratio_invariant_exact"] for r in rows),
              "independent_newton_estimator": all(max(r["independent_newton_relative_errors"]) < GATES["estimator_relative"] for r in rows),
              "tree_bias_box_contains_derived_controls": all(r["coefficient_tree_bias_contained"] for r in rows),
              "data_jacobian_and_exact_correlated_nulls": all(r["differential"]["ratio_gradient_relative_error"] < GATES["jacobian_relative"] and (r["differential"].get("native_gradient_relative_error", 0) < GATES["jacobian_relative"]) and all(r["differential"][k] for k in ("energy_common_mode_null_exact", "q_common_mode_null_exact", "coefficient_energy_covariance_control_exact", "coefficient_q_covariance_control_exact")) for r in rows),
              "rational_sufficient_budget_and_corners": all(r["budget_upper_not_certified"] and r["budget_corner_controls_pass"] and (r["budget_lower_certified"] if r["sufficient_relative_energy_error_budget"] > 0 else not r["zero_noise_box"]["certified"]) for r in rows),
              "all_preregistered_ranges_retained": len(rows) == len(MU_GRID)*len(Q_MAX_GRID),
              "no_physical_noise_assigned": all(not r["physical_noise_or_precision_assigned"] for r in rows)}
    passed = all(checks.values())
    paths = [Path(__file__).relative_to(ROOT).as_posix(), REGISTRY, PREFIX+"Code/03_Research/test_t13_multi_q_estimator.py"]
    protected = [PREDECESSOR, Q.REGISTRY, Q.PREDECESSOR, Q.DENS.PREDECESSOR,
                 Q.DENS.REM.PREDECESSOR, PREFIX+"Result/artifacts/t13_gaussian_source_work_first_failure.json"]+list(Q.EFT.ACTION_PATHS)
    record = {"major_result_id": "T13_MULTI_Q_ESTIMATOR_COVARIANCE_AND_TREE_BIAS_BUDGET", "topic": "0.13_Thermodynamic_Bridge", "branch_id": Q.VIRT.BRANCH,
              "generated_at": datetime.now(timezone.utc).isoformat(), "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL", "verification_status": "PASS_SCOPED_MULTI_Q_ESTIMATOR" if passed else "FAIL_SCOPED_MULTI_Q_ESTIMATOR",
              "what_is_closed": "Exact three-node coefficient estimator, full energy/q differential and correlated-null covariance controls, sufficient rational tree-bias/relative-energy-error budget at fixed native inputs",
              "equation_or_mapping": "beta_hat=W*(E_i/q_i); Sigma_beta=J Sigma_log(E,q) J^T; r=beta0*beta2/beta1^2; rational tree/noise component box maps to target I interval",
              "units": {"beta": "c:1,eta:E^-2,zeta:E^-4 in natural witness lane", "log_inputs": "reference ratios", "energy_error_budget": "dimensionless sufficient bound, not measured noise"},
              "derivation_class": "DERIVED_INTERPOLATION_JACOBIAN_EXACT_RATIONAL_TREE_ERROR_REQUIREMENT", "observable": "conditional density-dispersion information", "data_role": "DERIVED_CONTROL_NO_EMPIRICAL_CALIBRATION",
              "declared_protocol": registry["protocol"], "thresholds": GATES, "checks": checks, "examples": examples,
              "rational_encoding": {"format": "decimal_numerator_denominator", "max_integer_bits": MAX_INTEGER_BITS, "max_decimal_digits": MAX_DECIMAL_DIGITS, "global_python_integer_limit_changed": False},
              "covariance_input_order": ["log_E1", "log_E2", "log_E3", "log_q1", "log_q2", "log_q3", "log_minus_r0", "log_D", "log_s"],
              "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected), "equation_registry_ids": [e["id"] for e in registry["entries"]],
              "controlling_blocker": "physical_peak_resolution_joint_covariance_native_state_and_interaction_error_not_admitted",
              "open_blockers": ["source_detector_to_peak_resolution_and_correlated_bias", "permitted_same_state_low_q_rows_and_native_current_map", "physical_q_native_state_interaction_error_outside_energy_only_budget", "thermal_gain_alpha_heat_entropy_KMS_parent_closure"],
              "dependency_unlocked": ["instrument_input_and_resolution_feasibility_research_only"] if passed else [],
              "multi_q_estimator_verified": passed, "joint_data_differential_verified": passed, "rational_energy_only_budget_verified": passed,
              "physical_noise_acquired": False, "physical_resolution_admitted": False, "physical_q5_measured": False, "physical_measurement_design_completed": False,
              "physical_material_map_admitted": False, "independent_alpha_Phi_K_admitted": False, "physical_Kubo_emitted": False, "full_SK_KMS_matching_closed": False,
              "nonlinear_parent_action_completed": False, "controlled_full_action_truncation_error_established": False,
              "full_core_unlock": False, "core_composition_gate_overwritten": False, "old_source_work_audit_promoted": False,
              "external_parameter_fitting": False, "estimator_is_linear_interpolation_not_physical_calibration": True,
              "clipping": False, "cone_padding": False, "assigned_width": False, "claim_promotion": False,
              "external_numeric_rows_admitted": 0, "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
              "state_variables": ["existing_sigma_pi_phase_Phi_tree_fluctuations"], "excluded_variables": ["C", "UET_Pi", "R_gen", "R_obs", "external_detector_noise"],
              "claim_boundary": "Conditional estimator/error requirement for fixed rational tree witnesses. Failed/noncertified windows are retained; a sufficient box is not the optimal measurement budget or a physical no-go. Exact budget excludes q/native-state/resolution/interaction uncertainty; covariance is a prospective formula, not acquired noise or full design/thermal/Core/Goal closure."}
    names = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(names, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Derived multi-q interpolation, covariance and sufficient bias/noise requirements", record["equation_or_mapping"], checks, record["controlling_blocker"], "Match instrument resolution and native physical state/covariance or establish a scoped feasibility limit; do not rerun unchanged grids", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    result = audit()
    raw = (json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8")
    OUTPUT.write_bytes(raw)
    if not all(result["checks"].values()) and not FIRST_FAILURE.exists():
        FIRST_FAILURE.write_bytes(raw)
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"]}, indent=2))
    raise SystemExit(0 if all(result["checks"].values()) else 1)
