"""Condensed fixed-Phi thermal one-loop kernel, without infrared filtering.

The thermal difference is continued only into the upper frequency half-plane.
Exact static zero-Matsubara extraction resolves, rather than removes, the
massless radial bubble. No real-axis damping or resummed state is inferred.
"""

from __future__ import annotations

import hashlib
import json
from math import pi, sqrt
from pathlib import Path
import runpy

import numpy as np
from scipy.integrate import quad
from scipy.special import zeta

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
WARD_PATH = PREFIX + "Code/03_Research/Research_T13_Thermal_OneLoop_Ward_Current.py"
WARD_ARTIFACT = PREFIX + "Result/artifacts/t13_thermal_oneloop_ward_current.json"
CURVATURE_ARTIFACT = PREFIX + "Result/artifacts/t13_moving_background_thermal_stiffness.json"
WARD = runpy.run_path(str(ROOT / WARD_PATH))
OUTPUT = ROOT / (PREFIX + "Result/artifacts/t13_finite_momentum_thermal_1pi.json")

# Fixed before integration; these are natural-unit diagnostics, not TTG fits.
Q_GRID = (.02, .04, .08, .16)
RADIAL_ORDERS = (96, 144, 216)
ANGULAR_ORDERS = (48, 72, 108)
MATSUBARA_TERMS = (128, 256, 512)
POINT_TOLERANCE = 1e-6
QUADRATURE_TOLERANCE = 1e-3
CURRENT_TOLERANCE = 1e-2
IR_Q_REFINEMENT = (.005, .0025)


def poles_and_residues(k, mu: float, r: float):
    k = np.asarray(k, dtype=float)
    if np.any(~np.isfinite(k)) or np.any(k <= 0):
        raise ValueError("positive finite internal momentum required, without clipping")
    WARD["validate"](0., mu, r, 1., 1.)
    high_sq = k*k+r+2*mu*mu+np.sqrt((r+2*mu*mu)**2+4*mu*mu*k*k)
    low_sq = k*k*(k*k+2*r)/high_sq
    low, high = np.sqrt(low_sq), np.sqrt(high_sq)
    p = np.stack((-high, -low, low, high), axis=-1)
    numerator = np.zeros(p.shape+(2, 2), dtype=complex)
    numerator[..., 0, 0] = k[..., None]**2-p*p
    numerator[..., 1, 1] = k[..., None]**2+2*r-p*p
    numerator[..., 0, 1] = -2j*mu*p
    numerator[..., 1, 0] = 2j*mu*p
    derivative = 4*p*(p*p-k[..., None]**2-r-2*mu*mu)
    return p, numerator/derivative[..., None, None]


def vertices(mu: float, r: float, Z: float, lam: float):
    WARD["validate"](0., mu, r, Z, lam)
    g, amplitude = lam/Z, sqrt(Z*r/lam)
    return 2*g*amplitude*np.array([[[3., 0.], [0., 1.]], [[0., 1.], [1., 0.]]])


def bose(energy, t: float):
    energy = np.asarray(energy, dtype=float)
    if not np.isfinite(t) or t < 0 or np.any(energy <= 0):
        raise ValueError("T>=0 and positive energies required")
    if t == 0:
        return np.zeros_like(energy)
    y = np.exp(-energy/t)
    return y/(-np.expm1(-energy/t))


def convolution_weight(p, u, t: float, frequency: complex):
    """Thermal sum of two simple poles, including the coincident static limit."""
    frequency = complex(frequency)
    if not np.isfinite(frequency) or frequency.imag < 0 or (frequency.imag == 0 and frequency != 0):
        raise ValueError("static zero or upper-half-plane frequency required")
    p, u = np.broadcast_arrays(p, u)
    if t == 0:
        return np.zeros_like(p, dtype=complex)
    ep, eu = np.abs(p), np.abs(u)
    np_, nu_ = bose(ep, t), bose(eu, t)
    if frequency != 0:
        return -(np.sign(p)*np_-np.sign(u)*nu_)/(frequency+p-u)
    same = np.sign(p) == np.sign(u)
    gap = np.abs(ep-eu)
    factor = np.divide(-np.expm1(-gap/t), gap,
                       out=np.full_like(gap, 1/t), where=gap != 0)
    # Stable Bose divided difference; its continuous limit is n(1+n)/T.
    same_value = np.exp(-np.minimum(ep, eu)/t)*factor/(
        (-np.expm1(-ep/t))*(-np.expm1(-eu/t)))
    opposite = np.divide(-(np.sign(p)*np_-np.sign(u)*nu_), p-u,
                         out=np.zeros_like(p), where=~same)
    return np.where(same, same_value, opposite).astype(complex)


def point_bubble(k, ell, t: float, mu: float, r: float, Z: float, lam: float,
                 frequency: complex = 0j):
    k, ell = np.broadcast_arrays(np.asarray(k, dtype=float), np.asarray(ell, dtype=float))
    pk, rk = poles_and_residues(k, mu, r)
    pl, rl = poles_and_residues(ell, mu, r)
    v = vertices(mu, r, Z, lam)
    contraction = np.einsum("...sij,ajk,...tkl,bli->...abst", rk, v, rl, v, optimize=True)
    weight = convolution_weight(pk[..., :, None], pl[..., None, :], t, frequency)
    return -np.sum(contraction*weight[..., None, None, :, :], axis=(-2, -1))/(2*Z)


def euclidean_point_bubble(nu: float, external_nu: float, k: float, ell: float,
                          mu: float, r: float, Z: float, lam: float):
    amplitude = sqrt(Z*r/lam)
    v = vertices(mu, r, Z, lam)
    g1 = np.linalg.inv(WARD["euclidean_kernel"](nu, k, mu, r, Z, lam, amplitude))
    g2 = np.linalg.inv(WARD["euclidean_kernel"](nu+external_nu, ell, mu, r, Z, lam, amplitude))
    return np.array([[-np.trace(g1@a@g2@b)/(2*Z) for b in v] for a in v])


def matrix_frequency_check(k: float, ell: float, t: float, mu: float, r: float,
                           Z: float, lam: float, harmonic: int, terms: int):
    if t <= 0 or isinstance(terms, bool) or terms < 32 or harmonic not in (0, 1):
        raise ValueError("positive T, >=32 frequency terms and harmonic 0/1 required")
    omega = 2*pi*t*harmonic
    finite = t*sum((euclidean_point_bubble(2*pi*t*n, omega, k, ell, mu, r, Z, lam)
                    for n in range(-terms, terms+1)), start=np.zeros((2, 2)))
    # The even nu^-4 ultraviolet tail follows from Tr(V_a V_b), not residues.
    g, x0 = lam/Z, Z*r/lam
    c4 = -np.diag([20*g*g*x0/Z, 4*g*g*x0/Z])
    tail = 2*t*c4*zeta(4., terms+1)/(2*pi*t)**4
    vacuum = np.array([[quad(lambda nu: euclidean_point_bubble(
        nu, omega, k, ell, mu, r, Z, lam)[a, b], -np.inf, np.inf,
        epsabs=2e-11, epsrel=2e-11)[0]/(2*pi) for b in range(2)] for a in range(2)])
    direct = finite+tail-vacuum
    spectral = point_bubble(k, ell, t, mu, r, Z, lam, 1j*omega)
    scale = max(float(np.max(np.abs(spectral))), 1e-12)
    return {"k": k, "ell": ell, "harmonic": harmonic, "terms": terms,
            "direct": direct.tolist(), "spectral_real": spectral.real.tolist(),
            "spectral_imaginary_max": float(np.max(np.abs(spectral.imag))),
            "relative_disagreement": float(np.max(np.abs(direct-spectral))/scale)}


def convolution_3d(q: float, a: float, b: float):
    """Integral of [(k^2+a^2)((k+q)^2+b^2)]^-1 over all 3D momentum."""
    if not all(np.isfinite(v) for v in (q, a, b)) or q <= 0 or min(a, b) < 0:
        raise ValueError("q>0 and nonnegative masses required")
    return (pi/2 if a+b == 0 else np.arctan(q/(a+b)))/(4*pi*q)


def zero_matsubara_integral(q: float, t: float, mu: float, r: float, Z: float, lam: float):
    WARD["validate"](t, mu, r, Z, lam)
    g, x0, mass = lam/Z, Z*r/lam, sqrt(2*r)
    return np.diag([-2*g*g*x0*t/Z*(9*convolution_3d(q, mass, mass)+convolution_3d(q, 0., 0.)),
                    -4*g*g*x0*t/Z*convolution_3d(q, mass, 0.)])


def integrated_bubble(q: float, t: float, mu: float, r: float, Z: float, lam: float,
                      frequency: complex = 0j, radial_order: int = 216,
                      angular_order: int = 108, map_scale: float | None = None):
    WARD["validate"](t, mu, r, Z, lam)
    if not np.isfinite(q) or q <= 0:
        raise ValueError("positive finite external momentum required")
    for order in (radial_order, angular_order):
        if isinstance(order, bool) or not isinstance(order, int) or order < 16:
            raise ValueError("integer quadrature orders >=16 required")
    scale = max(t, mu, sqrt(r)) if map_scale is None else map_scale
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("positive finite quadrature mapping scale required")
    # Split at k=q and compactify q..infinity; no UV/IR cutoff is introduced.
    nodes, weights = np.polynomial.legendre.leggauss(radial_order)
    u, w = .5*(nodes+1), .5*weights
    grid = np.concatenate((q*u, q+scale*u/(1-u)))
    radial_weights = np.concatenate((q*w, scale*w/(1-u)**2))
    angle_nodes, angle_weights = np.polynomial.legendre.leggauss(angular_order)
    k = grid[:, None]
    if frequency == 0:
        ell = np.sqrt((k-q)**2+2*k*q*(1+angle_nodes[None, :]))
        angular_measure = np.broadcast_to(angle_weights, ell.shape)
    else:
        # d(cos theta)=ell*dell/(k*q). Log coordinates resolve 1/ell^2
        # soft occupation factors without dropping or regularizing any term.
        lower = np.abs(k-q)
        log_span = np.log1p(2*np.minimum(k, q)/lower)
        ell = lower*np.exp(.5*(angle_nodes[None, :]+1)*log_span)
        angular_measure = .5*angle_weights[None, :]*ell*ell*log_span/(k*q)
    values = point_bubble(k, ell, t, mu, r, Z, lam, frequency)
    if frequency == 0:
        g, x0 = lam/Z, Z*r/lam
        ks, kp, ls, lp = 1/(k*k+2*r), 1/(k*k), 1/(ell*ell+2*r), 1/(ell*ell)
        zero = np.zeros_like(values)
        zero[..., 0, 0] = -2*g*g*x0*t/Z*(9*ks*ls+kp*lp)
        zero[..., 1, 1] = -2*g*g*x0*t/Z*(ks*lp+kp*ls)
        values -= zero
    measure = radial_weights[:, None]*grid[:, None]**2*angular_measure/(4*pi*pi)
    answer = np.sum(measure[..., None, None]*values, axis=(0, 1))
    if frequency == 0:
        answer += zero_matsubara_integral(q, t, mu, r, Z, lam)
    return answer


def complex_matrix(value):
    return {"real": value.real.tolist(), "imaginary": value.imag.tolist()}


def formal_inverse_from_bubble(q, frequency, mu, r, Z, thermal_zero, bubble):
    """Order-matched inverse, not a Dyson resummation or a stable-state assertion."""
    w = complex(frequency)
    WARD["validate"](0., mu, r, Z, 1.)
    if not np.isfinite(q) or q < 0 or not np.isfinite(w):
        raise ValueError("finite q>=0 and frequency required")
    constant = np.array([[q*q+2*r-w*w-4*thermal_zero["Omega_G_x"]/Z, 2j*mu*w],
                         [-2j*mu*w, q*q-w*w-thermal_zero["transverse_bubble"]]])
    return constant+bubble


def audit():
    old = json.loads((ROOT/WARD_ARTIFACT).read_text(encoding="utf-8"))
    curvature = json.loads((ROOT/CURVATURE_ARTIFACT).read_text(encoding="utf-8"))
    examples, frequency_checks = [], []
    for anchor, held in zip(old["examples"], curvature["examples"]):
        t, mu, r, Z, lam = (anchor[key] for key in ("T", "mu", "r", "Z", "lambda"))
        zero = anchor["reference"]
        coefficient = -lam*r*t/(4*Z*Z)
        expected_gradient = (held["reference"]["f_s_held_amplitude_thermal"]-Z*zero["x_tree"])/(Z*zero["x_tree"])
        static = []
        for q in Q_GRID:
            runs = [integrated_bubble(q, t, mu, r, Z, lam, radial_order=n, angular_order=m)
                    for n, m in zip(RADIAL_ORDERS, ANGULAR_ORDERS)]
            reference = runs[-1]
            gradient = (reference[1, 1].real-zero["transverse_bubble"])/(q*q)
            static.append({"q": q, "bubble": complex_matrix(reference),
                           "formal_inverse": complex_matrix(formal_inverse_from_bubble(q, 0j, mu, r, Z, zero, reference)),
                           "refinement": [complex_matrix(v) for v in runs],
                           "refinement_max_absolute": float(np.max(np.abs(runs[-1]-runs[-2]))),
                           "phase_gradient_refinement_absolute": float(abs(runs[-1][1, 1]-runs[-2][1, 1])/(q*q)),
                           "phase_gradient_correction": float(gradient),
                           "q_times_radial_bubble": float(q*reference[0, 0].real),
                           "unresummed_radial_inverse": float(q*q+2*r-4*zero["Omega_G_x"]/Z+reference[0, 0].real)})
        q = Q_GRID[1]
        z = .15+.1j
        dynamic = [integrated_bubble(q, t, mu, r, Z, lam, z, n, m)
                   for n, m in zip(RADIAL_ORDERS, ANGULAR_ORDERS)]
        opposite = integrated_bubble(q, t, mu, r, Z, lam, -z.conjugate())
        scales = [integrated_bubble(q, t, mu, r, Z, lam, map_scale=f*max(t, mu, sqrt(r)))
                  for f in (.7, 1.4)]
        dynamic_scales = [integrated_bubble(q, t, mu, r, Z, lam, z, map_scale=f*max(t, mu, sqrt(r)))
                          for f in (.7, 1.4)]
        ir = [{"q": qi, "q_times_full_radial_bubble": float(qi*integrated_bubble(
            qi, t, mu, r, Z, lam)[0, 0].real)} for qi in IR_Q_REFINEMENT]
        for harmonic in (0, 1):
            frequency_checks.append({"mu": mu, "runs": [matrix_frequency_check(
                .4, .55, t, mu, r, Z, lam, harmonic, n) for n in MATSUBARA_TERMS]})
        phase0 = static[0]["phase_gradient_correction"]
        examples.append({"T": t, "mu": mu, "r": r, "Z": Z, "lambda": lam,
                         "Phi_fixed": anchor["Phi_fixed"], "static": static,
                         "expected_phase_gradient_from_held_current": expected_gradient,
                         "current_from_finite_q": Z*(zero["x_tree"]+zero["delta_x_order_one_loop"])+Z*zero["x_tree"]*phase0,
                         "previous_static_current": anchor["current_stiffness_order_one_loop"],
                         "radial_IR_coefficient": coefficient,
                         "full_radial_IR_refinement": ir,
                         "formal_IR_breakdown_momentum": lam*t/(8*Z*Z),
                         "IR_ratio_to_tree_radial_mass": [{"q": q, "ratio": lam*t/(8*Z*Z*q)} for q in Q_GRID],
                         "upper_half_plane_frequency": [z.real, z.imag],
                         "upper_half_plane_bubble": complex_matrix(dynamic[-1]),
                         "upper_half_plane_formal_inverse": complex_matrix(formal_inverse_from_bubble(q, z, mu, r, Z, zero, dynamic[-1])),
                         "dynamic_refinement_max_absolute": float(np.max(np.abs(dynamic[-1]-dynamic[-2]))),
                         "retarded_reality_absolute": float(np.max(np.abs(opposite-dynamic[-1].conjugate()))),
                         "dynamic_map_scale_variation_absolute": float(np.max(np.abs(dynamic_scales[0]-dynamic_scales[1]))),
                         "map_scale_variation_absolute": float(np.max(np.abs(scales[0]-scales[1])))})
    checks = {
        "independent_finite_external_frequency_matrix_sum": all(c["runs"][-1]["relative_disagreement"] < POINT_TOLERANCE for c in frequency_checks),
        "matrix_frequency_refinement": all(c["runs"][-1]["relative_disagreement"] <= c["runs"][0]["relative_disagreement"]+1e-10 for c in frequency_checks),
        "static_quadrature_refinement": all(row["refinement_max_absolute"] < QUADRATURE_TOLERANCE*max(abs(row["bubble"]["real"][0][0]), 1e-6) for e in examples for row in e["static"]),
        "current_gradient_matches_held_curvature": all(abs(e["static"][0]["phase_gradient_correction"]-e["expected_phase_gradient_from_held_current"]) < CURRENT_TOLERANCE*abs(e["expected_phase_gradient_from_held_current"]) for e in examples),
        "phase_gradient_quadrature_refinement": all(row["phase_gradient_refinement_absolute"] < QUADRATURE_TOLERANCE*abs(e["expected_phase_gradient_from_held_current"]) for e in examples for row in e["static"]),
        "full_radial_IR_limit": all(abs(e["full_radial_IR_refinement"][-1]["q_times_full_radial_bubble"]/e["radial_IR_coefficient"]-1) < CURRENT_TOLERANCE for e in examples),
        "full_radial_IR_refinement": all(abs(e["full_radial_IR_refinement"][-1]["q_times_full_radial_bubble"]/e["radial_IR_coefficient"]-1) < abs(e["full_radial_IR_refinement"][0]["q_times_full_radial_bubble"]/e["radial_IR_coefficient"]-1) for e in examples),
        "static_map_scale_refinement": all(e["map_scale_variation_absolute"] < 1e-6 for e in examples),
        "upper_half_plane_quadrature_refinement": all(e["dynamic_refinement_max_absolute"] < 1e-6 for e in examples),
        "upper_half_plane_map_scale_refinement": all(e["dynamic_map_scale_variation_absolute"] < 1e-6 for e in examples),
        "retarded_reality": all(e["retarded_reality_absolute"] < 1e-10 for e in examples),
    }
    paths = (WARD_ARTIFACT, WARD_PATH, CURVATURE_ARTIFACT, Path(__file__).relative_to(ROOT).as_posix())
    protected = (PREFIX+"Result/artifacts/t13_conditional_twofluid_operator.json",
                 "docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json",
                 "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json")
    record = {
        "major_result_id": "T13_FINITE_MOMENTUM_THERMAL_1PI_AND_INFRARED_BOUNDARY",
        "topic": "0.13", "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
        "verification_status": "PASS_SCOPED_FINITE_MOMENTUM_THERMAL_1PI" if all(checks.values()) else "FAIL_FINITE_MOMENTUM_THERMAL_1PI_CHECK",
        "what_is_closed": ["thermal_finite_q_2x2_bubble_and_upper_half_plane_continuation", "static_zero_Matsubara_radial_1_over_q_boundary", "finite_q_phase_gradient_matches_formal_static_current"],
        "equation_or_mapping": "B_ab=-Delta_T int Tr[G V_a G_shifted V_b]/(2Z); B_sigma,zero~-lambda*r*T/(4Z^2 q); q_IR=lambda*T/(8Z^2)",
        "units": {"T_mu_k_q_frequency": "E", "r_bubble_current": "E^2", "vertices": "E", "residues": "E^-1", "phase_gradient_correction": "dimensionless", "radial_IR_coefficient": "E^3"},
        "derivation_class": "ACTION_DERIVED_THERMAL_ONE_LOOP_1PI_FIXED_PHI_UPPER_HALF_PLANE",
        "observable": "formal_static_phase_gradient_and_condensed_2x2_response_kernel_not_material_sound",
        "data_role": "DERIVED_NATURAL_UNIT_NO_MEASURED_ROWS", "checks": checks,
        "method_references": [
            {"url": "https://arxiv.org/abs/hep-ph/0607102", "role": "finite_density_loop_method_context_different_SU2xU1_model"},
            {"url": "https://arxiv.org/html/1011.3324v2", "role": "Goldstone_longitudinal_IR_and_amplitude_direction_method_context_not_UET_resummation"},
            {"url": "https://arxiv.org/abs/1911.01829", "role": "relativistic_thermal_mass_perturbative_agreement_route_not_implemented"},
        ],
        "preregistered": {"q_grid": Q_GRID, "radial_orders": RADIAL_ORDERS, "angular_orders": ANGULAR_ORDERS,
                           "Matsubara_terms": MATSUBARA_TERMS, "point_tolerance": POINT_TOLERANCE,
                           "quadrature_tolerance": QUADRATURE_TOLERANCE, "current_tolerance": CURRENT_TOLERANCE},
        "numerical_refinement_record": {"initial_dynamic_quadrature": "linear_cosine_failed_absolute_1e-6",
                                        "repair": "log_ell_coordinate_with_exact_measure_same_equations_and_tolerance",
                                        "IR_limit_refinement": IR_Q_REFINEMENT,
                                        "IR_refinement_role": "numerical_test_of_analytic_1_over_q_not_parameter_selection"},
        "examples": examples, "matrix_frequency_checks": frequency_checks,
        "evidence_artifacts": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths],
        "protected_evidence_hashes": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in protected],
        "open_blockers": ["IR_resummation_and_controlled_error", "real_axis_limit_and_matched_vertices", "joint_Phi_background_and_material_map", "independent_source_detector_normal_component_admission"],
        "controlling_blocker": "nonuniform_IR_loop_expansion_and_real_axis_response_not_closed",
        "dependency_unlocked": ["finite_q_thermal_1PI_resummation_design_only"],
        "finite_q_thermal_bubble_computed": True, "upper_half_plane_continuation_computed": True,
        "order_matched_thermal_inverse_computed": True, "inverse_used_as_Dyson_resummation": False,
        "real_axis_damping_derived": False, "IR_resummation_derived": False, "controlled_truncation_error_established": False,
        "physical_Kubo_emitted": False, "g1_physical_unlock": False, "g2_science_unlock": False,
        "full_core_unlock": False, "core_composition_gate_overwritten": False,
        "claim_promotion": False, "parameter_fitting": False, "xie_2026_accessed": False,
        "clipping": False, "IR_filter": False, "momentum_cutoff": False,
        "claim_boundary": "Fixed-Phi thermal difference at formal one-loop, tree condensed propagators. Static and upper-half-plane kernel only, not a stable resummed state, physical sound/damping, independent material prediction or global closure. q_IR is an expansion diagnostic, not a causal cutoff."
    }
    record["report"] = {
        "MAJOR_RESULT_CLOSURE": record["major_result_id"]+": "+record["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": record["what_is_closed"],
        "WHAT_REMAINS_OPEN": record["open_blockers"],
        "DEPENDENCY_UNLOCKED": record["dependency_unlocked"],
        "STATUS": record["verification_status"],
        "WHAT_CHANGED": "Computed finite-q/frequency thermal bubble and order-matched inverse with exact zero-mode integration and upper-half-plane continuation; no Core edits.",
        "EQUATION_OR_MAPPING": record["equation_or_mapping"],
        "VERIFICATION": "Independent matrix Matsubara sums, momentum refinements, phase-current comparison and full radial IR limit; finite-q inverse is not resummed.",
        "CONTROLLING_BLOCKER": record["controlling_blocker"],
        "NEXT_ACTION": "Construct a Ward/current-consistent infrared treatment and test real-axis limit before admitting physical response.",
        "CLAIM_BOUNDARY": record["claim_boundary"],
    }
    return record


if __name__ == "__main__":
    record = audit()
    OUTPUT.write_bytes((json.dumps(record, indent=2, ensure_ascii=True, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": record["verification_status"], "checks": record["checks"], "examples": record["examples"]}, indent=2))
