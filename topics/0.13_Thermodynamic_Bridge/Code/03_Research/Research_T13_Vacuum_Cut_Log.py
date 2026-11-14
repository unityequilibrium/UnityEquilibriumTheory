"""Formal LO linear-phase vacuum cut and real logarithm modulo local terms.

Dispersion integration to infinity defines a subtracted mathematical loop,
not a physical assertion of EFT validity in the UV. Internal curvature and
state-dependent microscopic Wilson matching remain separate obligations.
"""

from __future__ import annotations

import cmath
from datetime import datetime, timezone
import hashlib
import json
from math import isfinite, pi, sqrt
from pathlib import Path
import sys

import numpy as np
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[5]
LOCAL = Path(__file__).resolve().parent
if str(LOCAL) not in sys.path:
    sys.path.insert(0, str(LOCAL))
import Research_T13_Low_T_Interactions as INT
EFT = INT.EFT
PREFIX = EFT.PREFIX
REGISTRY = PREFIX+"Data/03_Research/t13_vacuum_cut_log_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_vacuum_cut_log.json")
MU_GRID = (1.05, 1.2)
Q_GRID = (.02, .01, .005)
FREQUENCY_RATIOS = (1.05, 1.2, 1.5)
THRESHOLD_OFFSETS = (.01, .001, .0001)
ORDERS = (24, 48, 96)
QUAD_TOLERANCES = (1e-9, 1e-11)
REN_SCALES = (.5, 1., 2.)
LOCAL_ELL6 = (-.5, 0., .5)
MATCHING_RATIOS = (-1., 0., .5, 2.)
GATES = {"cut_relative": 1e-10, "Cauchy_relative": 1e-8,
         "scale_relative": 1e-10, "threshold_decay_relative": .002,
         "local_low_q_margin": .01, "original_causal_leakage": 1e-6}


def validate(q, c):
    if not isfinite(q) or q < 0 or not isfinite(c) or c <= 0:
        raise ValueError("finite nonnegative momentum and positive sound speed required")


def validate_cubic(cf, vv):
    validate(0., cf["c"])
    if not all(isfinite(vv[name]) for name in ("g_t", "g_s")):
        raise ValueError("finite declared cubic coefficients required")


def cut_polynomial(k2, cf, vv):
    """F(z,K2)=z[a(z)^2-2a(z)b/3+b^2/5], no numerical fit."""
    validate_cubic(cf, vv)
    if not isfinite(k2) or k2 < 0:
        raise ValueError("finite nonnegative acoustic momentum squared required")
    poly = np.polynomial.Polynomial
    barred = vv["g_s"]/cf["c"]**2
    total = vv["g_t"]+barred
    z = poly([0., 1.])
    aa = (1.5*total-2*barred)*z+2*barred*k2
    bb = 1.5*total*k2
    return z*(aa*aa-2*aa*bb/3+bb*bb/5)


def cut_imaginary(omega, q, cf, vv):
    validate(q, cf["c"])
    if not isfinite(omega):
        raise ValueError("finite real frequency required")
    k2 = (cf["c"]*q)**2
    if omega*omega == k2 and q != 0:
        raise ValueError("threshold value requires a curvature prescription, not padding")
    if omega == 0 or omega*omega < k2:
        return 0.
    return -np.sign(omega)*float(cut_polynomial(k2, cf, vv)(omega*omega))/(32*pi*cf["c"]**3)


def direct_cut_phase_space(omega, q, cf, vv, order=48):
    validate(q, cf["c"])
    validate_cubic(cf, vv)
    c = cf["c"]
    if not isfinite(omega) or omega <= c*q or q <= 0 or not isinstance(order, int) or order < 2:
        raise ValueError("positive timelike frequency, q>0 and integer quadrature required")
    low, high = (omega/c-q)/2, (omega/c+q)/2
    nodes, weights = np.polynomial.legendre.leggauss(order)
    total, margins, energies = 0., [], []
    for node, weight in zip(nodes, weights):
        p = low+(high-low)*(node+1)/2
        r = omega/c-p
        cosine = (q*q+p*p-r*r)/(2*q*p)
        if not -1 < cosine < 1:
            raise ValueError("outside physical cut support; no angular clipping")
        qp = q*p*cosine
        ep, er = c*p, c*r
        amplitude = 6*vv["g_t"]*omega*ep*er+2*vv["g_s"]*(omega*(qp-p*p)+ep*(q*q-qp)+er*qp)
        total += weight*(high-low)/2*amplitude**2
        margins.append(1-abs(cosine))
        energies.append(abs(omega-ep-er)/omega)
    return {"Im_Sigma": -total/(32*pi*q*c**3),
            "order": order, "angular_support_margin_min": min(margins),
            "energy_residual_max": max(energies)}


def nonlocal_z(z, q, cf, vv, ren_scale=1.):
    validate(q, cf["c"])
    if not isfinite(ren_scale) or ren_scale <= 0:
        raise ValueError("positive finite renormalization scale required")
    z = complex(z)
    if not isfinite(z.real) or not isfinite(z.imag):
        raise ValueError("finite complex frequency squared required")
    k2 = (cf["c"]*q)**2
    if z == k2:
        if q == 0:
            return 0j  # The explicit z^3 log(z) zero-momentum limit, not a mass repair.
        raise ValueError("linear threshold logarithm undefined; internal curvature not resummed")
    return cut_polynomial(k2, cf, vv)(z)*cmath.log((k2-z)/ren_scale**2)/(32*pi*pi*cf["c"]**3)


def retarded_real_frequency(omega, q, cf, vv, ren_scale=1.):
    validate(q, cf["c"])
    if not isfinite(omega) or not isfinite(ren_scale) or ren_scale <= 0:
        raise ValueError("finite frequency and positive scale required")
    k2, z = (cf["c"]*q)**2, omega*omega
    if z == k2:
        if q == 0:
            return 0j
        raise ValueError("threshold requires resummation, not assigned width")
    logarithm = complex(np.log(abs(k2-z)/ren_scale**2), -pi*np.sign(omega) if z > k2 else 0.)
    return cut_polynomial(k2, cf, vv)(z)*logarithm/(32*pi*pi*cf["c"]**3)


def four_subtracted_analytic(z, q, cf, vv, ren_scale=1.):
    validate(q, cf["c"])
    if not isfinite(ren_scale) or ren_scale <= 0:
        raise ValueError("positive finite renormalization scale required")
    k2 = (cf["c"]*q)**2
    if k2 <= 0:
        raise ValueError("this subtraction reference requires q>0")
    reference = -k2
    # Compose polynomial and analytic Taylor log; no finite-difference subtraction.
    shift = np.polynomial.Polynomial([reference, 1.])
    f_taylor = cut_polynomial(k2, cf, vv)(shift)
    gap = k2-reference
    log_taylor = np.polynomial.Polynomial([np.log(gap/ren_scale**2), -1/gap,
                                         -1/(2*gap**2), -1/(3*gap**3)])
    coefficients = (f_taylor*log_taylor).coef[:4]
    subtraction = np.polynomial.polynomial.polyval(complex(z)-reference, coefficients)/(32*pi*pi*cf["c"]**3)
    return nonlocal_z(z, q, cf, vv, ren_scale)-subtraction


def four_subtracted_dispersion(z, q, cf, vv, tolerance=1e-11):
    validate(q, cf["c"])
    scale = (cf["c"]*q)**2
    if scale <= 0 or not isfinite(tolerance) or tolerance <= 0:
        raise ValueError("positive q and quadrature tolerance required")
    normalized = complex(z)/scale
    if not isfinite(normalized.real) or not isfinite(normalized.imag):
        raise ValueError("finite complex frequency squared required")
    if normalized.imag == 0 and normalized.real >= 1:
        raise ValueError("this independent integral is off-cut; no ad-hoc principal-value padding")
    polynomial = cut_polynomial(1., cf, vv)
    def integrand(t):
        return polynomial(t)/((t+1)**4*(t-normalized))
    real, error_real = quad(lambda t: integrand(t).real, 1., np.inf,
                            epsabs=tolerance, epsrel=tolerance, limit=150)
    imag, error_imag = quad(lambda t: integrand(t).imag, 1., np.inf,
                            epsabs=tolerance, epsrel=tolerance, limit=150)
    multiplier = -scale**3*(normalized+1)**4/(32*pi*pi*cf["c"]**3)
    return {"Sigma_subtracted": multiplier*complex(real, imag),
            "quadrature_error_estimate": abs(multiplier)*(error_real+error_imag)}


def local_degree_six(z, k2, coefficients):
    """Fixed-canonical/source convention; not four independent physical parameters."""
    z = complex(z)
    values = np.asarray(coefficients, dtype=float)
    if values.shape != (4,) or not np.isfinite(values).all():
        raise ValueError("four finite local coefficients required")
    if not isfinite(k2) or k2 < 0 or not isfinite(z.real) or not isfinite(z.imag):
        raise ValueError("finite z and nonnegative acoustic K2 required")
    return sum(a*monomial for a, monomial in zip(values, (z**3, z*z*k2, z*k2*k2, k2**3)))


def matching_information():
    ratios = np.array(MATCHING_RATIOS)
    matrix = np.column_stack((ratios**3, ratios**2, ratios, np.ones(4)))
    on_shell = np.ones((4, 4))
    witness = np.array([.2, -.1, .3, -.4])
    reconstructed = np.linalg.solve(matrix, matrix@witness)
    # The null directions of the on-shell row include equation-of-motion terms.
    null_direction = np.array([1., -1., 0., 0.])
    return {"basis": ["z^3", "z^2 K2", "z K2^2", "K2^3"],
            "coefficients_units": "E^-4", "ratios_z_over_K2": MATCHING_RATIOS,
            "matrix_rank": int(np.linalg.matrix_rank(matrix)),
            "matrix_determinant": float(np.linalg.det(matrix)),
            "matrix_condition_number": float(np.linalg.cond(matrix)),
            "synthetic_algebra_witness_reconstruction_error": float(np.max(abs(reconstructed-witness))),
            "leading_on_shell_rank": int(np.linalg.matrix_rank(on_shell)),
            "leading_on_shell_combination": "a6+b6+c6+d6",
            "on_shell_null_direction": null_direction.tolist(),
            "null_direction_off_shell_value_at_z_over_K2_half": float((matrix@null_direction)[2]),
            "role": "DERIVED_FIXED_CONVENTION_MATCHING_INTERFACE_NOT_MEASURED_CALIBRATION",
            "four_independent_physical_parameters_claimed": False,
            "four_lab_measurements_required_claimed": False,
            "field_redefinition_and_source_contact_matching_required": True}


def relative(x, y):
    return abs(x-y)/max(abs(y), 1e-30)


def audit():
    action = EFT.controls()
    rows = []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        cf, vv = INT.dispersion_coefficients(state, action), INT.vertices(state, action)
        cuts, dispersions, thresholds, local_family, scale_checks = [], [], [], [], []
        for q in Q_GRID:
            k2 = (cf["c"]*q)**2
            for ratio in FREQUENCY_RATIOS:
                omega = cf["c"]*q*ratio
                direct = [direct_cut_phase_space(omega, q, cf, vv, order) for order in ORDERS]
                analytic = cut_imaginary(omega, q, cf, vv)
                sigma = retarded_real_frequency(omega, q, cf, vv)
                cuts.append({"q": q, "omega_over_cq": ratio, "analytic_Im_Sigma": analytic,
                             "direct_phase_space": direct,
                             "relative_error": relative(direct[-1]["Im_Sigma"], analytic),
                             "retarded_log_cut_error": relative(sigma.imag, analytic),
                             "reality_error": abs(retarded_real_frequency(-omega, q, cf, vv)-sigma.conjugate())})
            for normalized in (-.5, 0., .5, .5+.25j):
                z = normalized*k2
                analytic = four_subtracted_analytic(z, q, cf, vv)
                numeric = [four_subtracted_dispersion(z, q, cf, vv, tol) for tol in QUAD_TOLERANCES]
                dispersions.append({"q": q, "z_over_K2": [complex(normalized).real, complex(normalized).imag],
                                    "analytic_subtracted": [analytic.real, analytic.imag],
                                    "integral_subtracted": [[x["Sigma_subtracted"].real, x["Sigma_subtracted"].imag] for x in numeric],
                                    "relative_error": relative(numeric[-1]["Sigma_subtracted"], analytic),
                                    "refinement_relative_error": relative(numeric[0]["Sigma_subtracted"], numeric[-1]["Sigma_subtracted"])})
            coefficient = INT.decay_leading_coefficient(cf, vv)/2
            for offset in THRESHOLD_OFFSETS:
                omega = cf["c"]*q*sqrt(1+offset)
                gamma = -cut_imaginary(omega, q, cf, vv)/(2*omega)
                thresholds.append({"q": q, "threshold_offset": offset,
                                   "gamma_pole_q5_coefficient": gamma/q**5,
                                   "predecessor_coefficient_relative_error": relative(gamma/q**5, coefficient)})
            z = .5*k2
            for scale in REN_SCALES:
                shift = nonlocal_z(z, q, cf, vv, scale)-nonlocal_z(z, q, cf, vv, 1.)
                counterterm = 2*np.log(scale)*cut_polynomial(k2, cf, vv)(z)/(32*pi*pi*cf["c"]**3)
                scale_checks.append({"q": q, "ren_scale": scale,
                                     "relative_compensation_error": abs(shift+counterterm)/max(abs(nonlocal_z(z, q, cf, vv, 1.)), 1e-30),
                                     "four_subtracted_scale_error": relative(four_subtracted_analytic(z, q, cf, vv, scale), four_subtracted_analytic(z, q, cf, vv, 1.))})
            for ell6 in LOCAL_ELL6:
                local = ell6*q**6
                local_family.append({"q": q, "ell6": ell6, "local_Sigma_real": local,
                                     "conditional_local_pole_shift": local/(2*cf["c"]*q),
                                     "unchanged_Im_Sigma": cut_imaginary(cf["c"]*q*1.2, q, cf, vv),
                                     "low_q_correction_fraction": abs(local)/k2,
                                     "order_reduced_frequency_squared": k2+local,
                                     "microscopic_completion_or_global_stability": False})
        rows.append({"mu": mu, "state_tree": state, "c": cf["c"], "vertices": vv,
                     "cut_checks": cuts, "Cauchy_checks": dispersions,
                     "threshold_optical_theorem_checks": thresholds,
                     "scale_checks": scale_checks, "local_matching_ambiguity": local_family,
                     "threshold_gamma_pole_q5_coefficient": INT.decay_leading_coefficient(cf, vv)/2,
                     "threshold_real_log_q5_coefficient_linear_loop": INT.decay_leading_coefficient(cf, vv)/(2*pi)})
    matching = matching_information()
    checks = {
        "off_shell_cut_matches_direct_original_vertex_phase_space": all(x["relative_error"] < GATES["cut_relative"] for r in rows for x in r["cut_checks"]),
        "retarded_log_has_exact_cut_and_reality": all(x["retarded_log_cut_error"] < GATES["cut_relative"] and x["reality_error"] < 1e-20 for r in rows for x in r["cut_checks"]),
        "direct_cut_support_and_energy": all(y["angular_support_margin_min"] > 0 and y["energy_residual_max"] < 1e-12 for r in rows for x in r["cut_checks"] for y in x["direct_phase_space"]),
        "independent_four_subtracted_Cauchy_integral": all(x["relative_error"] < GATES["Cauchy_relative"] for r in rows for x in r["Cauchy_checks"]),
        "Cauchy_quadrature_refinement": all(x["refinement_relative_error"] < GATES["Cauchy_relative"] for r in rows for x in r["Cauchy_checks"]),
        "optical_theorem_limit_matches_predecessor_Beliaev": all(x["predecessor_coefficient_relative_error"] < GATES["threshold_decay_relative"] for r in rows for x in r["threshold_optical_theorem_checks"] if x["threshold_offset"] == THRESHOLD_OFFSETS[-1]),
        "local_scale_compensation_and_subtracted_invariance": all(max(x["relative_compensation_error"], x["four_subtracted_scale_error"]) < GATES["scale_relative"] for r in rows for x in r["scale_checks"]),
        "local_ambiguity_inside_declared_low_q_margin": all(x["low_q_correction_fraction"] < GATES["local_low_q_margin"] and x["order_reduced_frequency_squared"] > 0 for r in rows for x in r["local_matching_ambiguity"]),
        "fixed_convention_matching_rank_and_on_shell_null_boundary": matching["matrix_rank"] == 4 and matching["leading_on_shell_rank"] == 1 and matching["synthetic_algebra_witness_reconstruction_error"] < GATES["scale_relative"] and matching["null_direction_off_shell_value_at_z_over_K2_half"] != 0}
    def identities(paths):
        return [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths]
    record = {"major_result_id": "T13_VACUUM_PHASE_CUT_LOG_AND_LOCAL_MATCHING_BOUNDARY",
              "topic": "0.13_Thermodynamic_Bridge", "branch_id": EFT.BRANCH,
              "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
              "verification_status": "PASS_SCOPED_VACUUM_CUT_LOG" if all(checks.values()) else "FAIL_SCOPED_VACUUM_CUT_LOG",
              "created_at": datetime.now(timezone.utc).isoformat(), "action_controls": action,
              "what_is_closed": "LO linear-phase vacuum spectral continuum and real logarithmic equivalence class, independent four-subtracted dispersion reconstruction, optical-theorem connection and constructive local matching ambiguity",
              "equation_or_mapping": "Sigma_nonlocal=F(z,K2) log((K2-z)/mu_R2)/(32pi2 c3); local ell6 q6 leaves Im unchanged",
              "equation_registry_ids": [x["id"] for x in json.loads((ROOT/REGISTRY).read_text())["entries"]],
              "units": {"Sigma": "E^2", "z_K2": "E^2", "mu_R_omega_q": "E", "g_t_g_s": "E^-2", "ell6_real_log_q5_coefficient": "E^-4"},
              "derivation_class": "LO_LINEAR_PHASE_CUT_AND_SUBTRACTED_DISPERSION_MODULO_LOCAL_MATCHING",
              "observable": "Formal phase vacuum self-energy, not a detector/material prediction",
              "data_role": "DERIVED_DIAGNOSTIC_NOT_CALIBRATION", "checks": checks, "thresholds": GATES,
              "ontology": {"phase_self_energy_is_Phi": False, "canonical_phase_is_UET_Pi": False,
                           "radial_amplitude_is_collective_C": False, "excluded_state_variables": ["C", "R_gen", "R_obs"]},
              "local_matching_information": matching,
              "declared_grids": {"mu": MU_GRID, "q": Q_GRID, "frequency_ratios": FREQUENCY_RATIOS,
                                "threshold_offsets": THRESHOLD_OFFSETS, "orders": ORDERS,
                                "quad_tolerances": QUAD_TOLERANCES, "ren_scales": REN_SCALES, "ell6_family": LOCAL_ELL6,
                                "matching_ratios": MATCHING_RATIOS,
                                "locked_before_first_audit": True, "external_data_preregistration": False},
              "examples": rows,
              "evidence_artifacts": identities([str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), REGISTRY,
                                               PREFIX+"Code/03_Research/Research_T13_Low_T_Interactions.py",
                                               PREFIX+"Code/03_Research/test_t13_vacuum_cut_log.py"]),
              "protected_evidence_hashes": identities([PREFIX+"Result/artifacts/t13_low_T_interactions.json",
                                                       PREFIX+"Result/artifacts/t13_low_T_phase_eft.json"]+list(EFT.ACTION_PATHS)),
              "controlling_blocker": "state_dependent_local_Wilson_and_thermal_sunset_matching_open",
              "open_blockers": ["microscopic_state_dependent_local_Wilson_not_matched", "internal_curvature_on_shell_real_constant_not_computed",
                                "finite_T_two_loop_pressure_and_source_entropy_derivatives_open", "independent_material_source_readout_scale_and_transport_open"],
              "dependency_unlocked": ["microscopic_Wilson_and_thermal_sunset_research_only"],
              "primary_references": ["https://arxiv.org/html/1004.2567v2", "https://www.fuw.edu.pl/~derezins/damping_publ.pdf"],
              "real_nonlocal_linear_loop_computed": True, "four_subtracted_reconstruction_checked": True,
              "formal_UV_integral_is_physical_EFT_validity": False, "local_Wilson_matching_completed": False,
              "internal_curvature_real_self_energy_computed": False, "full_real_self_energy_matched": False,
              "full_two_loop_pressure_computed": False, "finite_T_collision_computed": False,
              "full_SK_KMS_matching_closed": False, "controlled_full_action_truncation_error_established": False,
              "independent_alpha_Phi_K_admitted": False, "physical_Kubo_emitted": False,
              "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False,
              "core_composition_gate_overwritten": False, "claim_promotion": False,
              "parameter_fitting": False, "assigned_damping_width": False, "clipping": False, "cone_padding": False,
              "old_Hartree_branch_repaired": False, "target_source_accessed": False, "xie_2026_accessed": False,
              "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
              "claim_boundary": "Formal LO linear-phase nonlocal loop modulo local matching, not full curved-parent/on-shell quantum EOS, total error bound, physical thermal transport/calibration, external validation or Full Topic13/Core. Original conserved-C remains blocked at 1e-6."}
    names = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    values = (record["major_result_id"]+": "+record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "New cut/log/matching audit; predecessor and Core-owner untouched", record["equation_or_mapping"], checks, record["controlling_blocker"], "Match local Wilson inputs and internal curvature before full real response; derive finite-T sunset pressure/source/entropy consistently", record["claim_boundary"])
    record["report"] = dict(zip(names, values))
    return record


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"],
                      "examples": [{"mu": x["mu"], "gamma_q5": x["threshold_gamma_pole_q5_coefficient"], "real_log_q5": x["threshold_real_log_q5_coefficient_linear_loop"], "Cauchy_error_max": max(y["relative_error"] for y in x["Cauchy_checks"])} for x in result["examples"]]}, indent=2))
    raise SystemExit(0 if all(result["checks"].values()) else 1)
