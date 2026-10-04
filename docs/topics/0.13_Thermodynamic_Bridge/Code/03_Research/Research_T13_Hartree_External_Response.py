"""Three-channel external field response of the fixed-Phi Hartree candidate.

Zero-momentum subtraction matches the predecessor's finite tadpoles. The
convergent bubble difference is integrated without a momentum cutoff. This is
not a material match, a real-axis transport coefficient or a gauge-current
vertex calculation. The internal Hartree mass is never changed by hand.
"""

from __future__ import annotations

import hashlib
import json
from math import log, pi, sqrt
from pathlib import Path
import runpy

import numpy as np
from scipy.special import zeta

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
BACKGROUND_CODE = PREFIX+"Code/03_Research/Research_T13_Renormalized_Hartree_Background.py"
BACKGROUND_ARTIFACT = PREFIX+"Result/artifacts/t13_renormalized_hartree_background.json"
MATCH_CODE = PREFIX+"Code/03_Research/Research_T13_Hartree_Counterterm_Matching.py"
MATCH_ARTIFACT = PREFIX+"Result/artifacts/t13_hartree_counterterm_matching.json"
H = runpy.run_path(str(ROOT/BACKGROUND_CODE))
CT = runpy.run_path(str(ROOT/MATCH_CODE))
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_hartree_external_response.json")
BASIS = np.array([[[1., 0.], [0., 1.]], [[1., 0.], [0., -1.]],
                  [[0., 1.], [1., 0.]]])/sqrt(2.)
ORDERS = ((64, 32), (96, 48), (144, 72))
Q_GRID = (.02, .08, .16)
FREQUENCY = .15+.1j
POINT_TOLERANCE = 1e-7
QUADRATURE_TOLERANCE = 1e-5
STATIC_TOLERANCE = 2e-5
IDENTITY_TOLERANCE = 1e-9


def validate(t, mu, a, b, q=0., frequency=0j):
    H["validate"](t, mu, a, b)
    z = complex(frequency)
    if min(a, b) <= 0:
        raise ValueError("positive internal variational masses required; no IR mass repair")
    if not np.isfinite(q) or q < 0 or not np.isfinite(z):
        raise ValueError("finite q>=0 and frequency required")
    if z.imag < 0 or (z.imag == 0 and z != 0):
        raise ValueError("static zero or upper-half-plane frequency required; real axis not admitted")


def poles_and_residues(k, mu, a, b):
    k = np.asarray(k, dtype=float)
    validate(0., mu, a, b)
    if np.any(k < 0) or np.any(~np.isfinite(k)):
        raise ValueError("finite nonnegative internal momentum required")
    if mu == 0:
        energies = np.stack((np.sqrt(k*k+a), np.sqrt(k*k+b)), axis=-1)
        poles = np.stack((-energies[..., 0], -energies[..., 1],
                          energies[..., 0], energies[..., 1]), axis=-1)
        residues = np.zeros(poles.shape+(2, 2), dtype=complex)
        for j, field in enumerate((0, 1, 0, 1)):
            residues[..., j, field, field] = -1/(2*poles[..., j])
        return poles, residues
    low, high = H["modes"](k, mu, a, b)
    poles = np.stack((-high, -low, low, high), axis=-1)
    numerator = np.zeros(poles.shape+(2, 2), dtype=complex)
    numerator[..., 0, 0] = k[..., None]**2+b-poles*poles
    numerator[..., 1, 1] = k[..., None]**2+a-poles*poles
    numerator[..., 0, 1] = -2j*mu*poles
    numerator[..., 1, 0] = 2j*mu*poles
    derivative = 4*poles*(poles*poles-k[..., None]**2-(a+b)/2-2*mu*mu)
    return poles, numerator/derivative[..., None, None]


def pole_weight(p, ell, t, frequency=0j):
    """Full vacuum plus thermal divided difference, not just thermal difference."""
    p, ell = np.broadcast_arrays(p, ell)
    ep, el = np.abs(p), np.abs(ell)
    def bose(energy):
        if t == 0:
            return np.zeros_like(energy)
        return np.exp(-energy/t)/(-np.expm1(-energy/t))
    np_, nl = bose(ep), bose(el)
    numerator = np.sign(p)*(np_+.5)-np.sign(ell)*(nl+.5)
    z = complex(frequency)
    if z != 0:
        return -numerator/(z+p-ell)
    same = np.sign(p) == np.sign(ell)
    opposite = np.divide(-numerator, p-ell, out=np.zeros_like(p), where=~same)
    derivative = np.zeros_like(p)
    if t > 0:
        gap = np.abs(ep-el)
        factor = np.divide(-np.expm1(-gap/t), gap,
                           out=np.full_like(gap, 1/t), where=gap != 0)
        derivative = np.exp(-np.minimum(ep, el)/t)*factor/(
            (-np.expm1(-ep/t))*(-np.expm1(-el/t)))
    return np.where(same, derivative, opposite).astype(complex)


def point_bubble(k, ell, t, mu, a, b, frequency=0j):
    validate(t, mu, a, b, frequency=frequency)
    k, ell = np.broadcast_arrays(np.asarray(k, float), np.asarray(ell, float))
    pk, rk = poles_and_residues(k, mu, a, b)
    pl, rl = poles_and_residues(ell, mu, a, b)
    contractions = np.einsum("aij,...tjk,bkl,...sli->...abst", BASIS, rl, BASIS, rk, optimize=True)
    weights = pole_weight(pk[..., :, None], pl[..., None, :], t, frequency)
    return -np.sum(contractions*weights[..., None, None, :, :], axis=(-2, -1))


def euclidean_kernel(nu, k, mu, a, b):
    return np.array([[nu*nu+k*k+a, -2*mu*nu],
                     [2*mu*nu, nu*nu+k*k+b]])


def matrix_frequency_check(k, ell, t, mu, a, b, harmonic=1, terms=256):
    validate(t, mu, a, b)
    if t <= 0 or harmonic not in (0, 1) or terms < 32:
        raise ValueError("positive T, harmonic 0/1 and >=32 terms required")
    omega = 2*pi*t*harmonic
    direct = np.zeros((3, 3))
    for n in range(-terms, terms+1):
        g = np.linalg.inv(euclidean_kernel(2*pi*t*n, k, mu, a, b))
        shifted = np.linalg.inv(euclidean_kernel(2*pi*t*n+omega, ell, mu, a, b))
        direct -= t*np.einsum("aij,jk,bkl,li->ab", BASIS, shifted, BASIS, g)
    direct -= 2*t*zeta(4., terms+1)/(2*pi*t)**4*np.eye(3)
    spectral = point_bubble(k, ell, t, mu, a, b, 1j*omega)
    return {"harmonic": harmonic, "terms": terms, "direct": direct.tolist(),
            "spectral": complex_matrix(spectral),
            "max_absolute_disagreement": float(np.max(np.abs(direct-spectral)))}


def static_finite_bubble(t, mu, a, b, scale=1., auxiliary=1., order=256):
    validate(t, mu, a, b)
    def tadpoles(am, bm):
        loop = H["loop_integrals"](t, mu, am, bm, scale=scale, auxiliary=auxiliary, order=order)
        return np.array([loop["sigma"], loop["phase"]])
    step = 1e-4*min(a, b)
    jacobian = np.column_stack(((tadpoles(a+step, b)-tadpoles(a-step, b))/(2*step),
                               (tadpoles(a, b+step)-tadpoles(a, b-step))/(2*step)))
    rotation = np.array([[1., 1.], [1., -1.]])/sqrt(2.)
    result = np.zeros((3, 3))
    result[:2, :2] = rotation@jacobian@rotation.T
    if a == b:
        result[2, 2] = (jacobian[0, 0]+jacobian[1, 1]-jacobian[0, 1]-jacobian[1, 0])/2
    else:
        covariance = tadpoles(a, b)
        result[2, 2] = (covariance[0]-covariance[1])/(a-b)
    return result


def bubble_difference(q, frequency, t, mu, a, b, radial_order=144,
                      angular_order=72, map_scale=None, routing="symmetric"):
    validate(t, mu, a, b, q, frequency)
    if routing not in ("symmetric", "one_sided"):
        raise ValueError("declared symmetric or one_sided momentum routing required")
    if any(isinstance(n, bool) or not isinstance(n, int) or n < 16 for n in (radial_order, angular_order)):
        raise ValueError("quadrature integer orders >=16 required")
    scale = max(mu, sqrt(a), sqrt(b), t, .1) if map_scale is None else map_scale
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("positive finite quadrature scale required")
    nodes, weights = np.polynomial.legendre.leggauss(radial_order)
    x, w = (nodes+1)/2, weights/2
    k = scale*x/(1-x)
    radial = scale*w/(1-x)**2
    c, cw = np.polynomial.legendre.leggauss(angular_order)
    kk = k[:, None]
    if routing == "symmetric":
        k1 = np.sqrt(kk*kk+q*q/4-kk*q*c[None, :])
        k2 = np.sqrt(kk*kk+q*q/4+kk*q*c[None, :])
    else:
        k1 = np.broadcast_to(kk, (len(k), len(c)))
        k2 = np.sqrt(kk*kk+q*q+2*kk*q*c[None, :])
    difference = point_bubble(k1, k2, t, mu, a, b, frequency)
    difference -= point_bubble(kk, kk, t, mu, a, b)
    measure = radial[:, None]*kk*kk*cw[None, :]/(4*pi*pi)
    return np.sum(difference*measure[..., None, None], axis=(0, 1))


def finite_bubble(q, frequency, t, mu, a, b, **kwargs):
    return static_finite_bubble(t, mu, a, b)+bubble_difference(q, frequency, t, mu, a, b, **kwargs)


def direct_subtracted_bubble(q, frequency, t, mu, a, b, radial_order=144,
                             angular_order=72, scale=1., auxiliary=1.):
    """Absolute loop subtraction, independent of the tadpole derivative anchor."""
    validate(t, mu, a, b, q, frequency)
    if min(scale, auxiliary) <= 0 or not np.isfinite(scale+auxiliary):
        raise ValueError("positive finite subtraction references required")
    if any(isinstance(n, bool) or not isinstance(n, int) or n < 16 for n in (radial_order, angular_order)):
        raise ValueError("quadrature integer orders >=16 required")
    x, w = np.polynomial.legendre.leggauss(radial_order)
    x, w = (x+1)/2, w/2
    mapping = max(mu, sqrt(a), sqrt(b), t, auxiliary)
    k = mapping*x/(1-x)
    measure = mapping*w/(1-x)**2*k*k/(2*pi*pi)
    c, cw = np.polynomial.legendre.leggauss(angular_order)
    kk = k[:, None]
    k1 = np.sqrt(kk*kk+q*q/4-kk*q*c[None, :])
    k2 = np.sqrt(kk*kk+q*q/4+kk*q*c[None, :])
    raw = point_bubble(k1, k2, t, mu, a, b, frequency)
    angular = np.sum(cw[None, :, None, None]*raw, axis=1)/2
    angular += np.eye(3)[None, ...]/(4*(k*k+auxiliary*auxiliary)**1.5)[:, None, None]
    reference = log(auxiliary*auxiliary/(scale*scale))/(16*pi*pi)
    return np.sum(measure[:, None, None]*angular, axis=0)+reference*np.eye(3)


def equal_mass_vacuum_reference(q, frequency, mass_sq, scale=1., order=128):
    """Independent four-dimensional Feynman-parameter scalar bubble."""
    validate(0., 0., mass_sq, mass_sq, q, frequency)
    nodes, weights = np.polynomial.legendre.leggauss(order)
    x, weights = (nodes+1)/2, weights/2
    invariant = q*q-complex(frequency)**2
    scalar = (log(mass_sq/(scale*scale))+np.sum(weights*np.log(1+x*(1-x)*invariant/mass_sq)))/(16*pi*pi)
    return scalar*np.eye(3)


def source_vertices(s, coupling):
    if not np.isfinite(s) or not np.isfinite(coupling) or min(s, coupling) <= 0:
        raise ValueError("positive canonical s,u required")
    quadratic_source = sqrt(2*s)*np.array([[1., 0.], [1., 0.], [0., 1.]])
    wick_kernel = np.diag([4*coupling, 2*coupling, 2*coupling])
    return quadratic_source, wick_kernel, wick_kernel@quadratic_source


def external_inverse(q, frequency, mu, a, b, s, coupling, bubble):
    validate(0., mu, a, b, q, frequency)
    z = complex(frequency)
    w, kernel, vertices = source_vertices(s, coupling)
    bubble = np.asarray(bubble, dtype=complex)
    if bubble.shape != (3, 3) or np.any(~np.isfinite(bubble)):
        raise ValueError("finite full symmetric covariance bubble required")
    mass_response = np.linalg.solve(np.eye(3)-kernel@bubble, vertices)
    internal = np.array([[q*q+a-z*z, 2j*mu*z], [-2j*mu*z, q*q+b-z*z]])
    correction = .5*vertices.T@bubble@mass_response
    return internal+correction


def counterterm_source_check(q, frequency, mu, a, b, s, coupling, bubble, D):
    w, kernel, _ = source_vertices(s, coupling)
    _, bare_kernel = CT["symmetric_tensor_projection"](coupling, D)
    bare_bubble = bubble+D*np.eye(3)
    bare_mass_response = np.linalg.solve(np.linalg.inv(bare_kernel)-bare_bubble, w)
    z = complex(frequency)
    internal = np.array([[q*q+a-z*z, 2j*mu*z], [-2j*mu*z, q*q+b-z*z]])
    bare_external = internal-np.diag([6*coupling*s, 2*coupling*s])+.5*w.T@bare_mass_response
    finite = external_inverse(q, frequency, mu, a, b, s, coupling, bubble)
    return float(np.max(np.abs(bare_external-finite)))


def complex_matrix(value):
    return {"real": value.real.tolist(), "imaginary": value.imag.tolist()}


def audit():
    old = json.loads((ROOT/BACKGROUND_ARTIFACT).read_text(encoding="utf-8"))
    matching = json.loads((ROOT/MATCH_ARTIFACT).read_text(encoding="utf-8"))
    examples = []
    for e in old["examples"]:
        t, mu, u = e["T"], e["mu"], e["u_canonical"]
        s, a, b = (e["background"][key] for key in ("s", "a", "b"))
        zero = static_finite_bubble(t, mu, a, b)
        inverse0 = external_inverse(0., 0j, mu, a, b, s, u, zero)
        checks_frequency = [matrix_frequency_check(.4, .55, t, mu, a, b, n) for n in (0, 1)]
        rows = []
        for q, z in [(v, 0j) for v in Q_GRID]+[(.08, FREQUENCY), (.08, 2j*pi*t)]:
            runs = [zero+bubble_difference(q, z, t, mu, a, b, n, m) for n, m in ORDERS]
            bubble = runs[-1]
            gamma = external_inverse(q, z, mu, a, b, s, u, bubble)
            one_sided = zero+bubble_difference(q, z, t, mu, a, b, routing="one_sided")
            absolute = direct_subtracted_bubble(q, z, t, mu, a, b)
            opposite = zero+bubble_difference(q, -z.conjugate(), t, mu, a, b)
            rows.append({"q": q, "frequency": [z.real, z.imag], "bubble": complex_matrix(bubble),
                         "external_inverse": complex_matrix(gamma),
                         "quadrature_refinements": [complex_matrix(v) for v in runs],
                         "last_quadrature_absolute_difference": float(np.max(np.abs(runs[-1]-runs[-2]))),
                         "routing_absolute_difference": float(np.max(np.abs(bubble-one_sided))),
                         "absolute_subtraction_disagreement": float(np.max(np.abs(bubble-absolute))),
                         "retarded_reality_residual": float(np.max(np.abs(opposite-bubble.conjugate()))),
                         "counterterm_source_residual": max(counterterm_source_check(q, z, mu, a, b, s, u, bubble, D) for D in (-.03, .04)),
                         "external_internal_difference": float(np.max(np.abs(gamma-np.array([[q*q+a-z*z, 2j*mu*z], [-2j*mu*z, q*q+b-z*z]]))))})
        uv = []
        for k in (40., 80., 160.):
            raw = point_bubble(k, k, 0., mu, a, b)
            uv.append({"k": k, "leading_identity_residual": float(np.max(np.abs(4*k**3*raw+np.eye(3))))})
        zero_direct = direct_subtracted_bubble(0., 0j, t, mu, a, b)
        examples.append({"mu": mu, "T": t, "Phi_fixed": e["Phi_fixed"], "s": s, "a": a, "b": b,
                         "static_bubble": complex_matrix(zero), "static_external_inverse": complex_matrix(inverse0),
                         "direct_zero_bubble": complex_matrix(zero_direct),
                         "zero_bubble_derivative_disagreement": float(np.max(np.abs(zero_direct-zero))),
                         "external_static_radial_reference": e["external_response"]["external_radial_curvature"],
                         "static_radial_relative_residual": abs(inverse0[0, 0].real/e["external_response"]["external_radial_curvature"]-1),
                         "static_transverse_absolute_residual": float(abs(inverse0[1, 1])),
                         "matrix_frequency_checks": checks_frequency, "responses": rows, "UV_leading_checks": uv})
    rows = [row for e in examples for row in e["responses"]]
    vacuum_reference = []
    for q, z in ((.16, 0j), (.08, FREQUENCY), (.08, .3j)):
        expected = equal_mass_vacuum_reference(q, z, .7)
        for auxiliary in (.8, 1., 1.3):
            direct = direct_subtracted_bubble(q, z, 0., 0., .7, .7, auxiliary=auxiliary)
            vacuum_reference.append({"q": q, "frequency": [z.real, z.imag], "auxiliary": auxiliary,
                                     "absolute_error": float(np.max(np.abs(direct-expected)))})
    checks = {
        "accepted_predecessors_without_physical_promotion": all(all(v["checks"].values()) and v["closure_level"] == "CLOSED_FOR_LANE" and v["full_core_unlock"] is False for v in (old, matching)),
        "full_vacuum_thermal_matrix_frequency_sums": all(v["max_absolute_disagreement"] < POINT_TOLERANCE for e in examples for v in e["matrix_frequency_checks"]),
        "static_radial_recovers_reoptimized_potential": all(e["static_radial_relative_residual"] < STATIC_TOLERANCE for e in examples),
        "static_transverse_Ward_without_internal_mass_fix": all(e["static_transverse_absolute_residual"] < IDENTITY_TOLERANCE and e["b"] > 0 for e in examples),
        "finite_q_frequency_quadrature": all(v["last_quadrature_absolute_difference"] < QUADRATURE_TOLERANCE for v in rows),
        "convergent_subtracted_routing_check": all(v["routing_absolute_difference"] < QUADRATURE_TOLERANCE for v in rows),
        "absolute_loop_subtraction_matches_tadpole_derivatives": all(e["zero_bubble_derivative_disagreement"] < STATIC_TOLERANCE for e in examples),
        "absolute_and_difference_subtractions_match_at_finite_Q": all(v["absolute_subtraction_disagreement"] < QUADRATURE_TOLERANCE for v in rows),
        "independent_four_dimensional_vacuum_reference": all(v["absolute_error"] < POINT_TOLERANCE for v in vacuum_reference),
        "upper_half_plane_retarded_reality": all(v["retarded_reality_residual"] < QUADRATURE_TOLERANCE for v in rows),
        "actual_bubble_in_counterterm_source_response": all(v["counterterm_source_residual"] < IDENTITY_TOLERANCE for v in rows),
        "external_not_internal_propagator": all(v["external_internal_difference"] > .001 for v in rows),
        "vacuum_leading_divergence_is_channel_identity": all(e["UV_leading_checks"][-1]["leading_identity_residual"] < 1e-3 and e["UV_leading_checks"][-1]["leading_identity_residual"] < e["UV_leading_checks"][0]["leading_identity_residual"] for e in examples),
    }
    paths = (BACKGROUND_ARTIFACT, MATCH_ARTIFACT, BACKGROUND_CODE, MATCH_CODE, Path(__file__).relative_to(ROOT).as_posix())
    protected = (PREFIX+"Result/artifacts/t13_conditional_twofluid_operator.json",
                 PREFIX+"Result/artifacts/t13_polar_dynamic_composite.json",
                 "docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json",
                 "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json")
    passed = all(checks.values())
    record = {
        "major_result_id": "T13_FIXED_PHI_HARTREE_EXTERNAL_FIELD_RESPONSE",
        "topic": "0.13", "branch_id": old["branch_id"],
        "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
        "verification_status": "PASS_SUBTRACTED_HARTREE_EXTERNAL_FIELD_RESPONSE" if passed else "FAIL_HARTREE_EXTERNAL_RESPONSE",
        "what_is_closed": ["computed_three_channel_vacuum_plus_thermal_subtracted_bubble", "source_responsive_covariance_Bethe_Salpeter", "external_static_Hessian_and_transverse_Ward_recovery", "finite_q_upper_half_plane_field_response_in_declared_subtraction"],
        "equation_or_mapping": "J_F(Q)=J_F(0)+integral[J_raw(Q)-J_raw(0)]; deltaM=(I-KJ_F)^-1*L*deltaphi; Gamma_ext=G_int^-1+L^T*J_F*(I-KJ_F)^-1*L/2",
        "units": {"T_mu_q_frequency_field": "E", "a_b_s_Gamma": "E^2", "bubble_K_u": "dimensionless", "source_vertices": "E"},
        "derivation_class": "SOURCE_DERIVATIVE_HARTREE_WITH_ZERO_MOMENTUM_SUBTRACTION_NOT_FULL_COVARIANT_RG_MATCH",
        "observable": "canonical_Cartesian_field_source_response_not_temperature_or_gauge_current",
        "data_role": "DERIVED_FIXED_NATURAL_UNIT_WITNESSES_NO_MEASURED_ROWS",
        "state_variables": ["same_O2_Cartesian_fields_at_fixed_Phi"], "excluded_variables": ["R_gen", "R_obs"],
        "equation_registry_ids": ["t13.diagnostic.hartree_covariance_bubble", "t13.diagnostic.hartree_external_BSE"],
        "examples": examples, "vacuum_Feynman_parameter_reference": vacuum_reference, "checks": checks,
        "thresholds": {"point_frequency": POINT_TOLERANCE, "quadrature_and_routing_absolute": QUADRATURE_TOLERANCE, "static_radial_relative": STATIC_TOLERANCE, "static_Ward_and_source_algebra": IDENTITY_TOLERANCE},
        "evidence_artifacts": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths],
        "protected_evidence_hashes": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in protected],
        "method_references": [{"url": "https://arxiv.org/pdf/hep-ph/0203008", "locator": "III, external effective action and Bethe-Salpeter response", "role": "established_method_not_UET_novelty"}, {"url": "https://arxiv.org/abs/1410.1337", "locator": "renormalization requires symmetry/translation preserving regulators", "role": "full_regulator_obligation_retained"}],
        "open_blockers": ["gauge_current_vertices_and_nonzero_Q_Ward_contact", "full_covariant_regulator_and_RG_action_input_match", "real_axis_spectral_and_IR_truncation_control", "joint_Phi_global_state_material_source_detector_admission", "normal_component_SK_KMS_collision_transport_and_independent_measurement"],
        "controlling_blocker": "gauge_current_real_axis_and_regulator_material_matching_not_closed",
        "dependency_unlocked": ["same_candidate_gauge_current_and_real_axis_matching_only"],
        "actual_three_channel_bubble_computed": True, "external_finite_frequency_response_derived": passed,
        "zero_momentum_subtraction_prescription": True, "finite_momentum_routing_checked": True,
        "full_covariant_counterterm_match": False, "RG_invariance_established": False,
        "gauge_current_vertex_computed": False, "real_axis_limit_admitted": False,
        "joint_Phi_stationarity_derived": False, "controlled_truncation_error_established": False,
        "internal_gap_used_as_physical_Goldstone_mass": False, "physical_Kubo_emitted": False,
        "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False,
        "core_composition_gate_overwritten": False, "claim_promotion": False,
        "parameter_fitting": False, "xie_2026_accessed": False, "clipping": False, "IR_filter": False,
        "causal_leakage_threshold_changed": False, "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False,
        "claim_boundary": "External field response of one fixed-Phi Hartree candidate in an explicit zero-momentum-subtracted prescription. Not complete gauge-current, covariant regulator/RG, real-axis spectrum, physical He-II/TTG prediction, microscopic KMS/transport or global UET closure.",
    }
    record["report"] = {
        "MAJOR_RESULT_CLOSURE": record["major_result_id"]+": "+record["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": record["what_is_closed"], "WHAT_REMAINS_OPEN": record["open_blockers"],
        "DEPENDENCY_UNLOCKED": record["dependency_unlocked"], "STATUS": record["verification_status"],
        "WHAT_CHANGED": "Computed the actual symmetric covariance bubble and external source response using the prior stationary witnesses and subtraction contract.",
        "EQUATION_OR_MAPPING": record["equation_or_mapping"],
        "VERIFICATION": "Direct frequency sums, static Hessian/Ward, quadrature/routing/reality and actual-bubble counterterm checks.",
        "CONTROLLING_BLOCKER": record["controlling_blocker"],
        "NEXT_ACTION": "Derive gauge-current contacts/vertices and real-axis prescription, then regulator/RG, joint Phi and independent material admission.",
        "CLAIM_BOUNDARY": record["claim_boundary"],
    }
    return record


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"],
                      "summary": [{"mu": e["mu"], "static_Ward": e["static_transverse_absolute_residual"],
                                   "refinement": max(v["last_quadrature_absolute_difference"] for v in e["responses"]),
                                   "routing": max(v["routing_absolute_difference"] for v in e["responses"])} for e in result["examples"]]}, indent=2))
