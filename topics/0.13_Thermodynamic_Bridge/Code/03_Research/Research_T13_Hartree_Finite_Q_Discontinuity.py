"""Finite-q local spectral continuation of the unchanged Hartree candidate.

This computes the discontinuity needed by a later finite-q pole calculation,
not that pole or a physical collision rate. No empirical rows are consumed.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from math import pi, sqrt
from pathlib import Path
import runpy

import numpy as np
from scipy.optimize import brentq, root

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
PREVIOUS_CODE = PREFIX+"Code/03_Research/Research_T13_Hartree_Soft_Poles.py"
PREVIOUS_ARTIFACT = PREFIX+"Result/artifacts/t13_hartree_soft_poles.json"
P = runpy.run_path(str(ROOT/PREVIOUS_CODE))
R, G, F = P["R"], P["G"], P["F"]
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_hartree_finite_q_discontinuity.json")
Q_GRID = (.04, .02, .01)
REAL_RAYS = (.2, .3, .4)
ORDERS = (64, 96, 128)
ORIGINAL_ORDERS = (48, 80)
CUT_TOLERANCE = 1e-8
TAIL_TOLERANCE = 1e-9
LOCAL_DOMAIN = {"Re_v": [.19, .45], "Im_v": [-.015, 0.]}


def validate(q, v, example, order):
    P["validate_example"](example, order)
    v = complex(v)
    if (not np.isfinite(q) or isinstance(q, bool) or not 0 < q <= .04
            or not np.isfinite(v) or not .19 <= v.real <= .45 or not -.015 <= v.imag <= 0):
        raise ValueError("positive q<=.04 and the declared local positive-cut v domain required")
    gap = float(P["complex_poles"](0., example["mu"], example["a"], example["b"])[0][0, 2].real)
    if q*v.real >= 2*gap:
        raise ValueError("pair threshold overlaps this local continuation; no omitted-cut repair")


def complex_inverse_shell(ell, mode, example):
    """Analytic inverse of the original dispersion; never abs(complex energy)."""
    if mode not in (0, 1, 2, 3):
        raise ValueError("one of the four original signed modes required")
    ell = np.asarray(ell, complex)
    mu, a, b = (example[key] for key in ("mu", "a", "b"))
    branch = 1 if mode in (1, 2) else -1
    d = np.sqrt((a-b)**2/4+4*mu*mu*ell*ell)
    r_sq = ell*ell-(a+b)/2+branch*d
    derivative = 2*ell*(1+branch*2*mu*mu/d)
    determinant_derivative = 4*ell*(-branch*d-2*mu*mu)
    residue = np.zeros(ell.shape+(2, 2), complex)
    residue[..., 0, 0] = ((b-a)/2+branch*d)/determinant_derivative
    residue[..., 1, 1] = ((a-b)/2+branch*d)/determinant_derivative
    residue[..., 0, 1] = -2j*mu*ell/determinant_derivative
    residue[..., 1, 0] = 2j*mu*ell/determinant_derivative
    return r_sq, derivative, residue


def signed_occupation(ell, mode, t):
    sign = 1 if mode >= 2 else -1
    energy = sign*np.asarray(ell, complex)
    return sign*(np.exp(-energy/t)/(-np.expm1(-energy/t))+.5)


def threshold_root(q, v, example, mode):
    """Continue each signed mode's exact finite-q collinear shell endpoint."""
    validate(q, v, example, 32)
    if mode not in (0, 1, 2, 3):
        raise ValueError("one of four original signed modes required")
    sign = 1 if mode >= 2 else -1
    branch = mode if sign > 0 else 3-mode
    z = q*complex(v)
    def energy(k):
        return P["complex_poles"](k, example["mu"], example["a"], example["b"])[0][0, branch]
    def equation(k):
        return sign*(energy(k+sign*q)-energy(k))-z
    left, right = q/2, max(example["mu"], sqrt(example["a"]), sqrt(example["b"]), 1.)
    while equation(right).real < 0 and right < 1e4:
        right *= 2
    if equation(left).real >= 0 or equation(right).real <= 0:
        raise ValueError("endpoint is not uniquely bracketed above q/2 in the declared tail domain")
    seed = brentq(lambda k: equation(k).real, left, right, xtol=1e-13)
    def equations(values):
        value = equation(complex(*values))
        return [value.real, value.imag]
    result = root(equations, [seed, 0.], tol=1e-10)
    k = complex(*result.x)
    residual = abs(equation(k))
    if residual > 1e-11 or k.real <= q/2 or not np.isfinite(k):
        raise ValueError("complex finite-q endpoint continuation failed")
    return k, float(residual)


def on_shell_density(k, q, v, example, mode):
    k = np.atleast_1d(np.asarray(k, complex))
    z = q*complex(v)
    p, residues, _ = P["complex_poles"](k, example["mu"], example["a"], example["b"])
    p, rp = p[:, mode], residues[:, mode]
    ell = p+z
    r_sq, derivative, re = complex_inverse_shell(ell, mode, example)
    sign = 1 if mode >= 2 else -1
    jacobian = sign*derivative/(2*k*q)
    kz = (r_sq-k*k)/(2*q)
    transverse_sq = ((k+q)**2-r_sq)*(r_sq-(k-q)**2)/(4*q*q)
    operators = np.zeros((len(k), 5, 2, 2), complex)
    operators[:, :3] = G["BASIS"]
    operators[:, 3] = -(2*p+z)[:, None, None]*G["ROTATION"]+2j*example["mu"]*np.eye(2)
    operators[:, 4] = -2j*kz[:, None, None]*G["ROTATION"]
    # The equal vacuum halves cancel exactly; retain exponentially small tails.
    t = example["T"]
    energy, outgoing_energy = sign*p, sign*ell
    occupation = (sign*np.exp(-energy/t)*(-np.expm1(-sign*z/t))
                  /((-np.expm1(-energy/t))*(-np.expm1(-outgoing_energy/t))))
    trace = np.einsum("...aij,...jk,...bkl,...li->...ab", operators, re, operators, rp)
    joint = .5*(occupation*jacobian)[:, None, None]*trace
    transverse = -transverse_sq*np.einsum("ij,...jk,kl,...li->...", G["ROTATION"], re, G["ROTATION"], rp)*occupation*jacobian
    return joint, transverse, ell, r_sq


def spectral_tail(q, v, example, order=96, contour="horizontal"):
    validate(q, v, example, order)
    if contour not in ("horizontal", "return_to_real"):
        raise ValueError("declared local tail path required")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    x, weights = (nodes+1)/2, weights/2
    scale = max(example["mu"], sqrt(example["a"]), sqrt(example["b"]), 1.)
    joint, transverse = np.zeros((5, 5), complex), 0j
    checks = []
    for mode in range(4):
        threshold, error = threshold_root(q, v, example, mode)
        k = threshold+scale*x/(1-x)
        dk = scale/(1-x)**2+np.zeros_like(x, complex)
        if contour == "return_to_real":
            k -= 1j*threshold.imag*x
            dk -= 1j*threshold.imag
        numerator, tn, ell, r_sq = on_shell_density(k, q, v, example, mode)
        measure = weights*dk*k*k/(4*pi*pi)
        joint += np.sum(measure[:, None, None]*numerator, axis=0)
        transverse += np.sum(measure*tn)
        sign = 1 if mode >= 2 else -1
        energy = sign*ell
        checks.append({"signed_mode": mode, "threshold_k": [threshold.real, threshold.imag],
                       "shell_root_residual": error, "minimum_outgoing_energy_real": float(np.min(energy.real)),
                       "minimum_Bose_denominator": float(np.min(abs(-np.expm1(-energy/example["T"])))),
                       "minimum_shell_momentum_real": float(np.min(r_sq.real)),
                       "threshold_above_q_half": bool(threshold.real > q/2)})
    bubble, mixed, reverse, current = R["unpack_joint"](joint, transverse)
    return {"bubble": bubble, "mixed": mixed, "reverse": reverse, "loop_current": current}, checks


def errors(first, second):
    return {key: float(np.max(abs(first[key]-second[key]))) for key in first}


def original_cut_check(q, v, example):
    density, _ = spectral_tail(q, v, example, ORDERS[-1])
    runs = []
    for order in ORIGINAL_ORDERS:
        loops = R["retarded_loops"](q, q*v, example["T"], example["mu"], example["a"], example["b"], order, 32)
        original = dict(zip(density, loops["cuts"]["scattering"]))
        residuals = errors({key: -pi*value for key, value in density.items()}, original)
        pair_size = max(float(np.max(abs(value))) for value in loops["cuts"]["pair"])
        runs.append({"original_full_radial_order": order, "finite_q_cut_errors": residuals,
                     "original_all_pair_cut_max": pair_size})
    return {"q": q, "velocity_ray": v, "runs": runs}


def independent_forward_shell_check(q, v, example):
    """Forward dispersion/angular roots check all channels, not inverse-shell algebra."""
    rows = []
    for k in (.035, .09, .2, .6, 1.5):
        cuts, checks = R["direct_on_shell_cut"](k, q, q*v, example["T"], example["mu"], example["a"], example["b"])
        actual_joint, actual_tr = np.zeros((5, 5), complex), 0j
        active = 0
        for mode in range(4):
            p = P["complex_poles"](k, example["mu"], example["a"], example["b"])[0][0, mode].real
            limits = P["complex_poles"]([abs(k-q), k+q], example["mu"], example["a"], example["b"])[0][:, mode].real
            if min(limits) < p+q*v < max(limits):
                n, tn, _, _ = on_shell_density(k, q, v, example, mode)
                actual_joint -= pi*n[0]
                actual_tr -= pi*tn[0]
                active += 1
        rows.append({"k": k, "forward_shell_checks": checks,
                     "same_signed_active_shell_count": active,
                     "joint_cut_error": float(np.max(abs(actual_joint-cuts["scattering"][0]))),
                     "transverse_cut_error": float(abs(actual_tr-cuts["scattering"][1])),
                     "pair_cut_max": float(max(np.max(abs(cuts["pair"][0])), abs(cuts["pair"][1])))})
    return rows


def audit(progress=None):
    predecessor = json.loads((ROOT/PREVIOUS_ARTIFACT).read_text(encoding="utf-8"))
    examples = []
    for e in predecessor["examples"]:
        example = {key: e[key] for key in ("T", "mu", "Phi_fixed", "a", "b", "s", "u_canonical")}
        pole = G["unpack"](e["pole_runs"][-1]["velocity_pole"])
        soft, _ = P["spectral_tail"](pole, example, ORDERS[-1])
        complex_rows = []
        for q in Q_GRID:
            densities = [spectral_tail(q, pole, example, n) for n in ORDERS]
            final, domain = densities[-1]
            alternate, _ = spectral_tail(q, pole, example, ORDERS[-1], "return_to_real")
            complex_rows.append({"q": q, "velocity_reference_is_prior_soft_pole_not_finite_q_pole": F["complex_matrix"](np.asarray(pole)),
                                 "order_refinements": [errors(densities[i][0], densities[i-1][0]) for i in (1, 2)],
                                 "tail_path_disagreement": errors(final, alternate),
                                 "difference_from_soft_density": errors(final, soft), "local_domain_checks": domain})
        cut_rows = [original_cut_check(q, v, example) for q in Q_GRID for v in REAL_RAYS]
        forward = independent_forward_shell_check(Q_GRID[0], .3, example)
        examples.append(example | {"complex_density_runs": complex_rows, "original_finite_q_cut_checks": cut_rows,
                                   "independent_forward_shell_checks": forward})
        if progress:
            progress(f"mu={e['mu']}: finite-q real cuts, exact complex thresholds and soft-limit density checked")
    checks = {
        "accepted_predecessor_hash_lineage": predecessor["closure_level"] == "CLOSED_FOR_LANE" and all(predecessor["checks"].values()) and R["predecessor_hashes_match"](predecessor),
        "original_all_channel_radial_cut_agreement": all(max(row["runs"][-1]["finite_q_cut_errors"].values()) < CUT_TOLERANCE for e in examples for row in e["original_finite_q_cut_checks"]),
        "no_pair_cut_in_declared_grid": all(row["runs"][-1]["original_all_pair_cut_max"] < CUT_TOLERANCE for e in examples for row in e["original_finite_q_cut_checks"]),
        "independent_forward_angular_shell_and_active_counts": all(max(row["joint_cut_error"], row["transverse_cut_error"], row["pair_cut_max"]) < CUT_TOLERANCE and row["same_signed_active_shell_count"] == row["forward_shell_checks"]["active_shell_count"] for e in examples for row in e["independent_forward_shell_checks"]),
        "complex_threshold_residual_and_sampled_Bose_domain": all(c["shell_root_residual"] < 1e-11 and c["minimum_outgoing_energy_real"] > 0 and c["minimum_Bose_denominator"] > .01 and c["threshold_above_q_half"] for e in examples for row in e["complex_density_runs"] for c in row["local_domain_checks"]),
        "complex_density_quadrature_converges": all(max(row["order_refinements"][-1].values()) < TAIL_TOLERANCE for e in examples for row in e["complex_density_runs"]),
        "two_local_tail_paths_agree": all(max(row["tail_path_disagreement"].values()) < TAIL_TOLERANCE for e in examples for row in e["complex_density_runs"]),
        "finite_q_density_approaches_original_soft_density": all(all(e["complex_density_runs"][i]["difference_from_soft_density"][key] < e["complex_density_runs"][i-1]["difference_from_soft_density"][key] for i in (1, 2)) for e in examples for key in ("bubble", "mixed", "reverse", "loop_current")),
        "finite_q_density_is_not_soft_substitution": all(max(e["complex_density_runs"][0]["difference_from_soft_density"].values()) > 1e-5 for e in examples),
        "protected_evidence_hashes_unchanged": all(hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"] for item in predecessor["protected_evidence_hashes"])}
    passed = all(checks.values())
    record = {"schema_version": "t13-hartree-finite-q-discontinuity-v1", "generated_at": datetime.now(timezone.utc).isoformat(),
              "major_result_id": "T13_FIXED_PHI_HARTREE_FINITE_Q_LANDAU_DISCONTINUITY", "topic": "0.13", "branch_id": predecessor["branch_id"],
              "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL", "verification_status": "PASS_SCOPED_FINITE_Q_DISCONTINUITY" if passed else "FAIL_FINITE_Q_DISCONTINUITY",
              "what_is_closed": ["finite_q_signed_mode_thresholds_and_analytic_shell_numerator", "local_complex_thermal_discontinuity_agrees_with_original_real_cuts", "two_tail_paths_and_soft_limit_density_diagnostic"],
              "equation_or_mapping": "ell=p_j(k)+q*v; sign_j*(E_j(k+sign_j*q)-E_j(k))=q*v; D(q,v)=sum_j integral_{k_j(q,v)}^infinity k^2/(4*pi^2)*N_joint*sign_j*d(r^2)/dell/(2*k*q) dk; B_L=B_principal_lower-2*pi*i*D(q,v)",
              "units": {"q_k_ell_T_mu": "E", "v": "dimensionless", "bubble_density": "dimensionless", "mixed_density": "E", "current_density": "E^2"},
              "derivation_class": "LOCAL_FINITE_Q_ON_SHELL_DISCONTINUITY_WITH_COMPLEX_THRESHOLD_QUADRATURE",
              "observable": "conditional_source_response_discontinuity_not_a_finite_q_pole_or_heat_transport", "data_role": "DERIVED_NO_EMPIRICAL_ROWS",
              "equation_registry_ids": ["t13.diagnostic.hartree_finite_q_local_discontinuity"], "examples": examples, "checks": checks,
              "config": {"q_grid": Q_GRID, "real_velocity_rays": REAL_RAYS, "complex_reference": "prior soft poles; not solved finite-q poles", "orders": ORDERS,
                         "original_full_radial_orders": ORIGINAL_ORDERS, "local_domain": LOCAL_DOMAIN, "tail_paths": ["horizontal", "return_to_real"],
                         "radial_domain": "0<=k<infinity", "assigned_output_width": None},
              "thresholds": {"original_cut_absolute": CUT_TOLERANCE, "tail_refinement_absolute": TAIL_TOLERANCE, "causal_leakage_unchanged": 1e-6},
              "evidence_artifacts": [{"path": path, "sha256": hashlib.sha256((ROOT/path).read_bytes()).hexdigest()} for path in (PREVIOUS_ARTIFACT, PREVIOUS_CODE, Path(__file__).relative_to(ROOT).as_posix())],
              "protected_evidence_hashes": predecessor["protected_evidence_hashes"],
              "open_blockers": ["actual_finite_q_principal_kernel_and_pole_root_not_computed", "certified_global_complex_domain", "Hartree_truncation_and_regulator_RG_full_action", "joint_Phi_material_source_detector_and_heat_transport"],
              "controlling_blocker": "finite_q_principal_kernel_and_actual_pole_not_computed",
              "dependency_unlocked": ["same_candidate_finite_q_principal_kernel_and_pole_research_only"],
              "finite_q_discontinuity_computed": bool(passed), "finite_q_complex_pole_computed": False,
              "certified_global_cut_support": False, "certified_global_contour_homotopy": False,
              "physical_mode_speed_emitted": False, "collision_rate_emitted": False, "controlled_truncation_error_established": False,
              "joint_Phi_stationarity_derived": False, "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False, "claim_promotion": False,
              "parameter_fitting": False, "artificial_width": False, "clipping": False, "IR_filter": False, "imposed_Ward_projection": False,
              "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED", "core_composition_gate_overwritten": False,
              "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False, "excluded_variables": ["R_gen", "R_obs", "nondynamical_A"],
              "claim_boundary": "Local finite-q discontinuity at unchanged fixed-Phi Hartree witnesses and declared q/v grid, independently checked against all-channel real cuts and forward angular shells. Sampled tail/domain agreement is not a global analytic proof. No finite-q pole, physical collision/Kubo/SK-KMS/heat/entropy, controlled Hartree remainder, empirical prediction or Full Topic13."}
    record["report"] = {"MAJOR_RESULT_CLOSURE": record["major_result_id"]+": "+record["closure_level"], "WHAT_IS_ACTUALLY_CLOSED": record["what_is_closed"],
                        "WHAT_REMAINS_OPEN": record["open_blockers"], "DEPENDENCY_UNLOCKED": record["dependency_unlocked"], "STATUS": record["verification_status"],
                        "WHAT_CHANGED": "Derived exact finite-q collinear thresholds and analytic joint on-shell density; checked independent original cuts and two complex tail paths.",
                        "EQUATION_OR_MAPPING": record["equation_or_mapping"], "VERIFICATION": checks, "CONTROLLING_BLOCKER": record["controlling_blocker"],
                        "NEXT_ACTION": "Compute the fixed-grid finite-q principal kernel, independently verify lower-sheet reciprocity, then solve actual poles with all elimination-denominator and convergence controls.", "CLAIM_BOUNDARY": record["claim_boundary"]}
    return record


if __name__ == "__main__":
    result = audit(progress=lambda message: print(message, flush=True))
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"]}, indent=2), flush=True)
