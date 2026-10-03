"""Same-action q5 information and exact rational tree expansion envelope.

No experimental coefficients, fitted dispersion or physical thermal map.
The rounded stationary state supplies declared rational coefficient witnesses;
their exact polynomial bound does not certify the stationary EOS or interactions.
"""

from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from math import isfinite, sqrt
from pathlib import Path
import sys

import mpmath as mp
import numpy as np

LOCAL = Path(__file__).resolve().parent
sys.path.insert(0, str(LOCAL))
import Research_T13_Noether_Density_Readout as DENS

ROOT, PREFIX, EFT, VIRT, TH = DENS.ROOT, DENS.PREFIX, DENS.EFT, DENS.VIRT, DENS.TH
PREDECESSOR = PREFIX+"Result/artifacts/t13_noether_density_readout.json"
PREDECESSOR_SHA = "2b6688dab3cb55c623fa5c1a43320ef28d65fe82e95b27d6ea1731f9c632ac12"
REGISTRY = PREFIX+"Data/03_Research/t13_q5_dispersion_information_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_q5_dispersion_information.json")
FIRST_FAILURE = OUTPUT.with_name("t13_q5_dispersion_information_first_failure.json")
MU_GRID, Q_GRID, UNIT_SCALES, PHI_SCALES = (1.05, 1.2), (.02, .01, .005), (1.01, 1.02), (.5, 2.)
DIGITS, FD_STEP, BISECTION_STEPS = (50, 80), 1e-8, 300
GATES = {"identity_relative": 1e-9, "matrix_relative": 1e-8, "precision_relative": 1e-40,
         "q5_extraction_relative_finest": 1e-3, "refinement_ratio_min": 3., "refinement_ratio_max": 5.,
         "gradient_relative": 1e-5, "original_causal_leakage": 1e-6}


def rational(value):
    return F(str(float(value)))


def parameters(state, action):
    EFT.validate(action)
    if state["xi"] != 0 or state["h"] != 0 or state["mu"] <= 0:
        raise ValueError("declared rest h0=0 tree class required")
    mu, s, u, g, w, k = [rational(v) for v in (state["mu"], state["s"], action["u"], action["gamma"], state["V_curvature"], action["epsilon"]*action["response_kinetic"])]
    radial, gyro, mixing, p = 2*u*s, 4*mu*mu, g*g*s, k/w
    delta = radial-mixing/w
    if min(s, w, k, delta) <= 0:
        raise ValueError("positive condensed/heavy/kinetic curvature required")
    return {"s": s, "g": g, "W": w, "k": k, "R": radial, "H": gyro,
            "S": mixing, "delta": delta, "N": delta+gyro, "p": p,
            "A": 1+p*radial, "B": p*gyro}


def polynomial_value(t, y, p):
    x = t-y
    return p["delta"]*t-p["N"]*y+p["A"]*x*x-p["B"]*x*y+p["p"]*x*x*x


def series(p):
    a = p["delta"]/p["N"]
    ell = 1-a
    b = (p["A"]*ell**2-p["B"]*ell*a)/p["N"]
    d = (-2*p["A"]*ell*b-p["B"]*(ell-a)*b+p["p"]*ell**3)/p["N"]
    h, j = b/(2*a), d/(2*a)-b*b/(8*a*a)
    return {"a": a, "b": b, "d": d, "h": h, "j": j}


def coefficients(p):
    z = series(p)
    c = sqrt(float(z["a"]))
    eta, zeta = c*float(z["h"]), c*float(z["j"])
    eta0 = float((1-z["a"])**2/p["N"])/(2*c)
    zeta0 = -float((1-z["a"])**3/p["N"]**2)/c-float((1-z["a"])**4/p["N"]**2)/(8*c**3)
    result = {"c": c, "eta": eta, "zeta": zeta, "eta_base": eta0, "zeta_base": zeta0}
    if p["g"] == 0:
        return result | {"kinetic_information": "NOT_APPLICABLE_DECOUPLED_PHI"}
    invariant = float(p["g"]**2*p["k"]/p["W"]**2)
    coupling = float((1-z["a"])**3*p["s"]*p["W"]/(2*p["N"]*p["g"]**2))/c
    r0, dd = c*zeta0/eta0**2, c*coupling/eta0**2
    return result | {"I": invariant, "K": coupling, "r0": r0, "D": dd,
                     "r": c*zeta/eta**2, "s": float(p["s"])}


def inverse(linear, cubic, quintic, c, eta0, r0, dd, s):
    values = (linear, cubic, quintic, c, eta0, r0, dd, s)
    if not all(isfinite(x) for x in values) or min(linear, cubic, c, eta0, dd, s) <= 0 or max(quintic, r0) >= 0:
        raise ValueError("positive A/B/c/eta0/D/s and negative C/r0 required")
    ratio = linear*quintic/cubic**2
    gap = r0-ratio
    if not 0 < gap < dd/(s*s):
        raise ValueError("outside the strict positive kinetic class; no clipping")
    tau = sqrt(gap/dd)
    inv = tau/(1-s*tau)
    eta = eta0*(1+s*inv)
    q_unit = sqrt(linear*eta/(cubic*c))
    return {"I": inv, "q_unit": q_unit, "energy_unit": linear*q_unit/c, "unit_free_ratio": ratio}


def inverse_log_gradient(linear, cubic, quintic, c, eta0, r0, dd, s):
    row = inverse(linear, cubic, quintic, c, eta0, r0, dd, s)
    inv, ratio = row["I"], row["unit_free_ratio"]
    f = 1+s*inv
    derivative = -f**3/(2*dd*inv)
    return np.array([derivative*ratio, -2*derivative*ratio, derivative*ratio,
                     -derivative*r0, -inv*f/2, s*inv*inv])


def add(a, b, factor=F(1)):
    out = [F(0)]*max(len(a), len(b))
    for i, value in enumerate(a):
        out[i] += value
    for i, value in enumerate(b):
        out[i] += factor*value
    return out


def multiply(a, b):
    out = [F(0)]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return out


def fraction_record(value):
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def tree_envelope(q, p):
    if not isfinite(q) or q <= 0:
        raise ValueError("positive finite q required")
    t = rational(q)**2
    z = series(p)
    poly = [F(1), z["h"], z["j"]]
    pp = sum(v*t**i for i, v in enumerate(poly))
    yp = z["a"]*t*pp*pp
    slope = p["N"]-p["B"]*t
    if slope <= 0 or pp <= 0 or not 0 < yp < t:
        raise ValueError("outside the declared monotone root/envelope domain")
    y = [F(0)]+[z["a"]*v for v in multiply(poly, poly)]
    x = add([F(0), F(1)], y, -F(1))
    residual = add([F(0), p["delta"]], y, -p["N"])
    residual = add(residual, multiply(x, x), p["A"])
    residual = add(residual, multiply(x, y), -p["B"])
    residual = add(residual, multiply(multiply(x, x), x), p["p"])
    leading_zero = all(v == 0 for v in residual[:4])
    tail = sum(abs(v)*t**i for i, v in enumerate(residual[4:], 4))
    bound = tail/(slope*z["a"]*t*(1+pp))
    return {"first_four_residual_coefficients_exactly_zero": leading_zero,
            "normalized_energy_error_bound_exact": fraction_record(bound),
            "normalized_energy_error_bound": float(bound), "slope_lower_bound": float(slope),
            "E5_inside_root_interval": True, "residual_degree": len(residual)-1,
            "rational_coefficient_witness_not_certified_EOS_or_physical_state": True}


def high_precision_root_check(q, p, digits):
    with mp.workdps(digits):
        m = lambda v: mp.mpf(v.numerator)/v.denominator
        pp = {key: m(value) for key, value in p.items()}
        z = series(p)
        a, b, d = [m(z[key]) for key in ("a", "b", "d")]
        t = m(rational(q)**2)
        lo, hi = a*t, t
        for _ in range(BISECTION_STEPS):
            middle = (lo+hi)/2
            value = polynomial_value(t, middle, pp)
            if value > 0:
                lo = middle
            else:
                hi = middle
        energy, mom = mp.sqrt((lo+hi)/2), mp.sqrt(t)
        c, eta = mp.sqrt(a), b/(2*mp.sqrt(a))
        zeta = (d-eta*eta)/(2*c)
        e5 = c*mom+eta*mom**3+zeta*mom**5
        extraction = (energy-c*mom-eta*mom**3)/mom**5
        return {"digits": digits, "energy": mp.nstr(energy, digits),
                "q5_extracted_coefficient": float(extraction),
                "normalized_E5_error": float(abs(energy-e5)/(c*mom)),
                "q5_extraction_relative_error": float(abs(extraction-zeta)/abs(zeta))}


def information(p):
    cf = coefficients(p)
    if p["g"] == 0:
        return {"classification": "NOT_APPLICABLE_DECOUPLED_PHI"}
    f, inv, s = 1+cf["s"]*cf["I"], cf["I"], cf["s"]
    eta_slope = s/f
    zeta_slope = (2*cf["zeta_base"]*s*f-2*cf["K"]*inv)/cf["zeta"]
    jacobian = np.array([[1., -1., 0.], [1., -3., eta_slope], [1., -5., zeta_slope]])
    recovered = inverse(cf["c"], cf["eta"], cf["zeta"], cf["c"], cf["eta_base"], cf["r0"], cf["D"], s)
    values = np.array([cf["c"], cf["eta"], cf["zeta"], cf["r0"], cf["D"], s])
    analytic = inverse_log_gradient(*values[:3], cf["c"], cf["eta_base"], *values[3:])
    differences = []
    for index in range(6):
        plus, minus = values.copy(), values.copy()
        plus[index] *= np.exp(FD_STEP)
        minus[index] *= np.exp(-FD_STEP)
        fn = lambda v: inverse(*v[:3], cf["c"], cf["eta_base"], *v[3:])["I"]
        differences.append((fn(plus)-fn(minus))/(2*FD_STEP))
    derivative = -2*cf["D"]*inv/f**3
    return {"classification": "IDENTIFIABLE_WITH_Q5_IN_RESTRICTED_POSITIVE_CLASS",
            "parameter_order": ["log_E_unit", "log_Q_unit", "I"],
            "log_observable_order": ["A_Q", "B_Q", "minus_C_Q"],
            "jacobian": jacobian.tolist(), "rank": int(np.linalg.matrix_rank(jacobian)),
            "determinant": float(np.linalg.det(jacobian)), "analytic_determinant": 2*(2*eta_slope-zeta_slope),
            "ratio_derivative_dI": derivative, "inverse_reference_error": DENS.WORK.relative(recovered["I"], inv),
            "ratio_gap": cf["r0"]-cf["r"], "relative_I_per_relative_ratio_condition": abs(cf["r"]/derivative/inv),
            "log_covariance_input_order": ["A_Q", "B_Q", "minus_C_Q", "minus_r0", "D", "s"],
            "log_gradient_I": analytic.tolist(), "central_log_gradient": differences,
            "gradient_relative_error": float(np.max(abs(analytic-differences)/np.maximum(abs(analytic), 1e-12))),
            "uncertainty_contract": "Var(I)=g^T Sigma_log g plus separately controlled theory/material/resolution errors; full correlations required",
            "instrument_precision_or_native_inputs_independence_assumed": False}


def load_predecessor():
    raw = (ROOT/PREDECESSOR).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PREDECESSOR_SHA:
        raise ValueError("density predecessor identity changed")
    previous = json.loads(raw)
    if not all(previous["checks"].values()) or previous["full_core_unlock"]:
        raise ValueError("scoped predecessor required")


def audit():
    load_predecessor()
    registry = json.loads((ROOT/REGISTRY).read_text())
    action, examples = EFT.controls(), []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        p, qrows, families, coordinates = parameters(state, action), [], [], []
        cf = coefficients(p)
        for q in Q_GRID:
            envelope = tree_envelope(q, p)
            roots = [high_precision_root_check(q, p, digits) for digits in DIGITS]
            with mp.workdps(80):
                precision_error = float(abs(mp.mpf(roots[0]["energy"])/mp.mpf(roots[1]["energy"])-1))
            matrix_energy = EFT.parent_energy_check(q, state, action)["positive_mode_frequencies"][0]
            finite_inferred = inverse(cf["c"], cf["eta"], roots[-1]["q5_extracted_coefficient"], cf["c"], cf["eta_base"], cf["r0"], cf["D"], cf["s"])
            qrows.append({"q": q, "envelope": envelope, "roots": roots,
                          "finite_q_proxy_I": finite_inferred["I"],
                          "finite_q_proxy_I_relative_bias": DENS.WORK.relative(finite_inferred["I"], cf["I"]),
                          "finite_q_proxy_is_calibration_or_prediction": False,
                          "precision_relative_error": precision_error,
                          "matrix_relative_error": DENS.WORK.relative(matrix_energy, float(roots[-1]["energy"]))})
        for scale in UNIT_SCALES:
            target_i = (scale**2*(1+cf["s"]*cf["I"])-1)/cf["s"]
            other_action = action | {"response_kinetic": target_i*state["V_curvature"]**2/(action["gamma"]**2*action["epsilon"])}
            other_state = EFT.tree_state(mu, action=other_action)
            other = coefficients(parameters(other_state, other_action))
            a, b, cc = scale*other["c"]/scale, scale*other["eta"]/scale**3, scale*other["zeta"]/scale**5
            recovered = inverse(a, b, cc, cf["c"], cf["eta_base"], cf["r0"], cf["D"], cf["s"])
            families.append({"scale": scale, "A_Q": a, "B_Q": b, "C_Q": cc,
                             "q3_preserved_relative_error": max(DENS.WORK.relative(a, cf["c"]), DENS.WORK.relative(b, cf["eta"])),
                             "q5_ratio_difference": a*cc/b**2-cf["r"],
                             "inverse_I_error": DENS.WORK.relative(recovered["I"], target_i),
                             "inverse_units_error": max(DENS.WORK.relative(recovered["q_unit"], scale), DENS.WORK.relative(recovered["energy_unit"], scale)),
                             "data_role": "CONSTRUCTIVE_REFERENCE_RATIOS_NOT_PHYSICAL_UNITS"})
        for scale in PHI_SCALES:
            other_action = EFT.rescale_Phi_coordinate(action, scale)
            other = coefficients(parameters(EFT.tree_state(mu, action=other_action), other_action))
            coordinates.append({"scale": scale, "coefficient_invariance_error": max(DENS.WORK.relative(other[key], cf[key]) for key in ("c", "eta", "zeta", "r", "I"))})
        info = information(p)
        eta_previous = EFT.rest_coefficients(state, action)["eta"]
        simplified_zeta = cf["zeta_base"]*(1+cf["s"]*cf["I"])**2-cf["K"]*cf["I"]**2
        det_errors = []
        for q in Q_GRID:
            for z in (.02j, .03+.02j):
                native = {key: float(value) for key, value in p.items()}
                polynomial = polynomial_value(q*q, z*z, native)
                matrix = np.linalg.det(VIRT.kernel(q, z, state, action))/float(p["W"])
                det_errors.append(DENS.WORK.relative(polynomial, matrix))
        extraction_errors = [row["roots"][-1]["q5_extraction_relative_error"] for row in qrows]
        examples.append({"mu": mu, "declared_rational_parameters": {key: fraction_record(value) for key, value in p.items()},
                         "declared_rational_series": {key: fraction_record(value) for key, value in series(p).items()},
                         "coefficients": cf, "information": info, "q_rows": qrows,
                         "unit_families": families, "coordinate_controls": coordinates,
                         "eta_predecessor_relative_error": DENS.WORK.relative(cf["eta"], eta_previous),
                         "simplified_zeta_relative_error": DENS.WORK.relative(cf["zeta"], simplified_zeta),
                         "matrix_determinant_relative_error": max(det_errors),
                         "q5_extraction_refinement_ratios": [x/y for x, y in zip(extraction_errors, extraction_errors[1:])]})
    qrows = [q for e in examples for q in e["q_rows"]]
    checks = {
        "same_action_determinant_and_prior_q3": all(max(e["matrix_determinant_relative_error"], e["eta_predecessor_relative_error"], e["simplified_zeta_relative_error"]) < GATES["identity_relative"] for e in examples),
        "independent_matrix_and_dual_precision_roots": all(q["matrix_relative_error"] < GATES["matrix_relative"] and q["precision_relative_error"] < GATES["precision_relative"] for q in qrows),
        "q5_extraction_refines_to_derived_coefficient": all(e["q_rows"][-1]["roots"][-1]["q5_extraction_relative_error"] < GATES["q5_extraction_relative_finest"] and all(GATES["refinement_ratio_min"] < r < GATES["refinement_ratio_max"] for r in e["q5_extraction_refinement_ratios"]) for e in examples),
        "exact_rational_tree_envelope": all(q["envelope"]["first_four_residual_coefficients_exactly_zero"] and q["roots"][-1]["normalized_E5_error"] <= q["envelope"]["normalized_energy_error_bound"] for q in qrows),
        "positive_class_q5_rank_and_inverse": all(e["information"]["rank"] == 3 and e["information"]["ratio_derivative_dI"] < 0 and e["information"]["inverse_reference_error"] < GATES["identity_relative"] and DENS.WORK.relative(e["information"]["determinant"], e["information"]["analytic_determinant"]) < GATES["identity_relative"] for e in examples),
        "old_q3_unit_family_separated_without_fitting": all(r["q3_preserved_relative_error"] < GATES["identity_relative"] and r["q5_ratio_difference"] < 0 and max(r["inverse_I_error"], r["inverse_units_error"]) < GATES["identity_relative"] for e in examples for r in e["unit_families"]),
        "Phi_coordinate_invariance": all(r["coefficient_invariance_error"] < GATES["identity_relative"] for e in examples for r in e["coordinate_controls"]),
        "full_covariance_inverse_gradient": all(e["information"]["gradient_relative_error"] < GATES["gradient_relative"] for e in examples)}
    passed = all(checks.values())
    paths = [Path(__file__).relative_to(ROOT).as_posix(), REGISTRY, PREFIX+"Code/03_Research/test_t13_q5_dispersion_information.py"]
    protected = [PREDECESSOR, DENS.PREDECESSOR, DENS.REM.PREDECESSOR,
                 PREFIX+"Result/artifacts/t13_gaussian_source_work_first_failure.json", DENS.REGISTRY, DENS.PROTOCOL]+list(EFT.ACTION_PATHS)
    record = {"major_result_id": "T13_Q5_UNIT_FREE_KINETIC_IDENTIFIABILITY_AND_TREE_REMAINDER", "topic": "0.13_Thermodynamic_Bridge", "branch_id": VIRT.BRANCH,
              "generated_at": datetime.now(timezone.utc).isoformat(), "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
              "verification_status": "PASS_SCOPED_Q5_INFORMATION" if passed else "FAIL_SCOPED_Q5_INFORMATION",
              "what_is_closed": "Derived tree q5, strict positive-class unit-free kinetic inverse/rank and exact rational expansion envelope for declared coefficient witnesses",
              "equation_or_mapping": "r=A_Q*C_Q/B_Q^2=r0-D*(I/(1+sI))^2; I=tau/(1-s*tau); E5=cq+eta*q^3+zeta*q^5",
              "units": {"c": "1", "eta": "E^-2", "zeta": "E^-4", "I": "E^-2", "r": "1", "D": "E^4", "A_Q": "J*m", "B_Q": "J*m^3", "C_Q": "J*m^5", "physical_coefficients": "not acquired/admitted"},
              "derivation_class": "DERIVED_SAME_ACTION_TREE_SERIES_CONSTRUCTIVE_INVERSE_EXACT_RATIONAL_ROOT_BOUND", "observable": "conditional density-visible q5 acoustic dispersion, not temperature", "data_role": "DERIVED_RATIONAL_AND_CONSTRUCTIVE_CONTROLS_NO_EXPERIMENTAL_ROWS",
              "declared_protocol": registry["protocol"], "finite_q_inference_diagnostic": registry["finite_q_inference_diagnostic"], "thresholds": GATES, "checks": checks, "examples": examples,
              "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected), "equation_registry_ids": [e["id"] for e in registry["entries"]],
              "controlling_blocker": "physical_q5_resolution_native_input_covariance_material_map_and_interaction_error_open",
              "open_blockers": ["Noether_atomic_current_and_same_state_native_input_map", "independent_q5_resolution_covariance_and_source_rows", "weak_coupling_conditioning_and_physical_inference_window", "interacting_finite_T_heat_entropy_KMS_and_parent_error"],
              "dependency_unlocked": ["conditional_q5_measurement_information_route_not_requiring_U_in_restricted_class"] if passed else [],
              "q5_tree_coefficient_verified": passed, "restricted_unit_free_inverse_verified": passed, "exact_rational_tree_witness_envelope_verified": passed,
              "physical_q5_measured": False, "physical_measurement_design_completed": False, "physical_material_map_admitted": False,
              "independent_alpha_Phi_K_admitted": False, "full_SK_KMS_matching_closed": False, "physical_Kubo_emitted": False,
              "nonlinear_parent_action_completed": False, "controlled_full_action_truncation_error_established": False,
              "full_core_unlock": False, "core_composition_gate_overwritten": False, "old_source_work_audit_promoted": False,
              "parameter_fitting": False, "assigned_width": False, "clipping": False, "cone_padding": False, "claim_promotion": False,
              "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED", "external_numeric_rows_admitted": 0,
              "state_variables": ["existing_sigma_pi_phase_Phi_tree_fluctuations"], "excluded_variables": ["C", "UET_Pi", "R_gen", "R_obs", "external_detector_gain"],
              "claim_boundary": "Restricted same-action positive kinetic class with other native inputs known. q5 removes the retained-q3 unit family, not full UET ambiguity, independent temperature scale, detector gain or physical calibration. Exact rational tree bound is conditional on declared rounded-state coefficient witnesses, not EOS/state uncertainty or interaction/finite-T validity. No physical/Core/Goal or owner promotion."}
    names = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(names, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Derived q5 and alternative independent-information route without importing U", record["equation_or_mapping"], checks, record["controlling_blocker"], "Determine q5 resolution/conditioning and same-state physical input/error map before comparison; preserve independent thermal and gain requirements", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    result = audit()
    raw = (json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8")
    OUTPUT.write_bytes(raw)
    if not all(result["checks"].values()) and not FIRST_FAILURE.exists():
        FIRST_FAILURE.write_bytes(raw)
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"]}, indent=2))
    raise SystemExit(0 if all(result["checks"].values()) else 1)
