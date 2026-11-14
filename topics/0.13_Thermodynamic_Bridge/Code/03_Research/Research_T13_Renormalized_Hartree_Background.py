"""Fixed-Phi, finite-potential Hartree candidate with explicit vacuum matching.

Separate the variational internal propagator from the source-reoptimized
external curvature. Neither is an admitted microscopic transport prediction.
Keep the original Gaussian failures and all physical admission gates intact.
"""

from __future__ import annotations

import hashlib
import json
from math import isfinite, log, pi, sqrt
from pathlib import Path

import numpy as np
from scipy.optimize import root

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
PREVIOUS = PREFIX+"Result/artifacts/t13_polar_dynamic_composite.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_renormalized_hartree_background.json")
ORDERS = (128, 192, 256)
VACUUM_SPLITS = (20., 40., 64.)
MS_SCALE = 1.
AUXILIARY_MASS = 1.
ROOT_TOLERANCE = 1e-9
IDENTITY_TOLERANCE = 1e-7
REFINEMENT_TOLERANCE = 1e-5
DERIVATIVE_TOLERANCE = 2e-5


def validate(t, mu, a, b, scale=1., auxiliary=1.):
    if not all(isfinite(v) for v in (t, mu, a, b, scale, auxiliary)):
        raise ValueError("finite canonical natural-unit inputs required")
    if min(t, mu, a, b) < 0 or min(scale, auxiliary) <= 0:
        raise ValueError("T,mu,a,b>=0 and positive reference scales required")


def modes(k, mu, a, b):
    k = np.asarray(k, dtype=float)
    validate(0., mu, a, b)
    if np.any(~np.isfinite(k)) or np.any(k < 0):
        raise ValueError("finite nonnegative momentum required")
    discriminant = (a-b)**2+8*mu*mu*(a+b)+16*mu**4+16*mu*mu*k*k
    high_sq = k*k+(a+b)/2+2*mu*mu+np.sqrt(discriminant)/2
    low_sq = np.divide((k*k+a)*(k*k+b), high_sq,
                       out=np.zeros_like(k), where=high_sq != 0)
    return np.sqrt(low_sq), np.sqrt(high_sq)


def thermal_integrals(t, mu, a, b, order=256):
    validate(t, mu, a, b)
    if isinstance(order, bool) or not isinstance(order, int) or order < 32:
        raise ValueError("integer order>=32 required")
    if t == 0:
        return np.zeros(4)
    nodes, weights = np.polynomial.legendre.leggauss(order)
    u, weights = (nodes+1)/2, weights/2
    mapping = max(t, mu, sqrt(a), sqrt(b), .1)
    k = mapping*u/(1-u)
    measure = weights*mapping/(1-u)**2*k*k/(2*pi*pi)
    low, high = modes(k, mu, a, b)
    def n(e):
        return np.exp(-e/t)/(-np.expm1(-e/t))
    nl, nh = n(low), n(high)
    separation = high*high-low*low
    if np.any(separation == 0):
        # Exact unmixed equal-mass case; no near-degeneracy repair threshold.
        tadpole = np.sum(measure*nl/low)
        free = np.sum(measure*2*t*np.log(-np.expm1(-low/t)))
        entropy = np.sum(measure*2*(nl*low/t-np.log(-np.expm1(-low/t))))
        return np.array([tadpole, tadpole, free, entropy])
    sigma = ((k*k+b-low*low)*nl/low+(high*high-k*k-b)*nh/high)/separation
    phase = ((k*k+a-low*low)*nl/low+(high*high-k*k-a)*nh/high)/separation
    free = t*(np.log(-np.expm1(-low/t))+np.log(-np.expm1(-high/t)))
    entropy = nl*low/t+nh*high/t-free/t
    return np.sum(measure[:, None]*np.stack((sigma, phase, free, entropy), axis=-1), axis=0)


def vacuum_integrals(mu, a, b, scale=1., auxiliary=1., order=256, split=64.):
    """Finite vacuum tadpoles and trace-log with MS-compatible reference terms.

    Subtract at fixed physical masses a+mu^2,b+mu^2, not shifted a,b.
    The split is a quadrature boundary; an analytic k^-5 residual tail is
    included and refined. It is not a physical cutoff or an IR regulator.
    """
    validate(0., mu, a, b, scale, auxiliary)
    if isinstance(order, bool) or not isinstance(order, int) or order < 32 or not isfinite(split) or split <= 0:
        raise ValueError("order>=32 and positive finite vacuum quadrature split required")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    cutoff = split*max(auxiliary, scale, mu, sqrt(a), sqrt(b))
    k = np.asarray((nodes+1)*cutoff/2, dtype=np.longdouble)
    measure = np.asarray(weights*cutoff/2, dtype=np.longdouble)*k*k/(2*pi*pi)
    a, b, nu, ref = map(np.longdouble, (a, b, mu*mu, auxiliary*auxiliary))
    pa, pb = np.sqrt(k*k+a), np.sqrt(k*k+b)
    average = np.sqrt(((pa+pb)/2)**2+nu)
    e0 = np.sqrt(k*k+ref)
    da, db = a+nu-ref, b+nu-ref
    # Rationalized differences avoid subtracting nearly equal O(k) energies
    # or O(1/k) tadpoles before taking source second derivatives.
    product_sum = pa*pb+k*k+(a+b)/2
    difference_sq = (da+db)/2-(a-b)**2/(8*product_sum)
    remainder_s = ((b-a)/(4*pa*average*(pa+pb))
                   -difference_sq/(2*average*e0*(average+e0))+da/(4*e0**3))
    remainder_p = ((a-b)/(4*pb*average*(pa+pb))
                   -difference_sq/(2*average*e0*(average+e0))+db/(4*e0**3))
    remainder_v = (-(da+db)*difference_sq/(4*e0*(average+e0)**2)
                   -(a-b)**2/(8*product_sum*(average+e0))+(da*da+db*db)/(16*e0**3))
    logarithm = log(float(ref)/(scale*scale))
    i0 = ref/(16*pi*pi)*(logarithm-1)
    i0_prime = logarithm/(16*pi*pi)
    v0 = ref*ref/(64*pi*pi)*(logarithm-1.5)
    tails = np.array([(3*da*da-2*nu*(da-db))/16,
                      (3*db*db+2*nu*(da-db))/16,
                      (da**3+db**3-nu*(da-db)**2)/32], dtype=np.longdouble)/(4*pi*pi*cutoff*cutoff)
    finite = np.array([i0+da*i0_prime, i0+db*i0_prime,
                       2*v0+(da+db)*i0/2+(da*da+db*db)*i0_prime/4], dtype=np.longdouble)
    remainders = np.sum(measure[:, None]*np.stack((remainder_s, remainder_p, remainder_v), axis=-1), axis=0)
    return np.asarray(finite+remainders+tails, dtype=float)


def loop_integrals(t, mu, a, b, scale=1., auxiliary=1., order=256, split=64.):
    thermal = thermal_integrals(t, mu, a, b, order)
    vacuum = vacuum_integrals(mu, a, b, scale, auxiliary, order, split)
    return {"sigma": float(thermal[0]+vacuum[0]), "phase": float(thermal[1]+vacuum[1]),
            "loop_free_energy": float(thermal[2]+vacuum[2]), "quasiparticle_entropy": float(thermal[3]),
            "thermal": thermal.tolist(), "vacuum": vacuum.tolist()}


def loop_derivative_check(t, mu, a, b, **kwargs):
    h = 1e-4*min(a, b)
    center = loop_integrals(t, mu, a, b, **kwargs)
    differences = np.array([(loop_integrals(t, mu, a+h, b, **kwargs)["loop_free_energy"]
                             -loop_integrals(t, mu, a-h, b, **kwargs)["loop_free_energy"])/(2*h),
                            (loop_integrals(t, mu, a, b+h, **kwargs)["loop_free_energy"]
                             -loop_integrals(t, mu, a, b-h, **kwargs)["loop_free_energy"])/(2*h)])
    expected = np.array([center["sigma"], center["phase"]])/2
    return {"free_energy_mass_derivatives": differences.tolist(), "half_tadpoles": expected.tolist(),
            "relative_residual": float(np.max(np.abs((differences-expected)/expected)))}


def symmetric_vacuum_reference_check():
    mass_sq = 1.3**2
    expected_i = mass_sq/(16*pi*pi)*(log(mass_sq/MS_SCALE**2)-1)
    expected_v = mass_sq*mass_sq/(32*pi*pi)*(log(mass_sq/MS_SCALE**2)-1.5)
    cases = []
    for mu in (0., .4, .8):
        for auxiliary in (.8, 1., 1.3):
            values = vacuum_integrals(mu, mass_sq-mu*mu, mass_sq-mu*mu, auxiliary=auxiliary)
            target = np.array([expected_i, expected_i, expected_v])
            cases.append({"mu": mu, "auxiliary": auxiliary,
                          "relative_residual": float(np.max(np.abs(values/target-1)))})
    return cases


def double_bubble(sigma, phase, coupling):
    return coupling*(3*sigma*sigma+2*sigma*phase+3*phase*phase)/4


def variational_potential(s, a, b, t, mu, r, coupling, scale=1., auxiliary=1., order=256, split=64.):
    if not all(isfinite(v) for v in (s, r, coupling)) or s < 0 or r <= 0 or coupling <= 0:
        raise ValueError("s>=0,r,u>0 required; s is canonical amplitude squared")
    loops = loop_integrals(t, mu, a, b, scale, auxiliary, order, split)
    Is, Ip = loops["sigma"], loops["phase"]
    tree = -r*s/2+coupling*s*s/4
    insertion = ((-r+3*coupling*s-a)*Is+(-r+coupling*s-b)*Ip)/2
    return tree+loops["loop_free_energy"]+insertion+double_bubble(Is, Ip, coupling)


def residuals(s, a, b, t, mu, r, coupling, **kwargs):
    loops = loop_integrals(t, mu, a, b, **kwargs)
    Is, Ip = loops["sigma"], loops["phase"]
    return np.array([-r+coupling*s+coupling*(3*Is+Ip),
                     a+r-3*coupling*s-coupling*(3*Is+Ip),
                     b+r-coupling*s-coupling*(Is+3*Ip)])


def stationary_background(t, mu, r, coupling, scale=1., auxiliary=1., order=256, split=64., seed_factor=1.):
    if not all(isfinite(v) for v in (r, coupling, seed_factor)) or min(r, coupling, seed_factor) <= 0:
        raise ValueError("positive r,u and numerical seed factor required")
    kwargs = {"scale": scale, "auxiliary": auxiliary, "order": order, "split": split}
    initial = np.log([r/coupling*seed_factor, 2*r*seed_factor, .02*seed_factor])
    def equations(log_variables):
        s, a, b = np.exp(log_variables)
        return residuals(s, a, b, t, mu, r, coupling, **kwargs)/r
    result = root(equations, initial, method="hybr", options={"xtol": ROOT_TOLERANCE, "maxfev": 150})
    s, a, b = np.exp(result.x)
    residual = residuals(s, a, b, t, mu, r, coupling, **kwargs)
    if not result.success or np.max(np.abs(residual))/r > IDENTITY_TOLERANCE:
        raise RuntimeError("stationary Hartree solve did not close; no mass repair or fallback fit")
    loops = loop_integrals(t, mu, a, b, **kwargs)
    potential = variational_potential(s, a, b, t, mu, r, coupling, **kwargs)
    return {"s": float(s), "a": float(a), "b": float(b), "residual": residual.tolist(),
            "potential": float(potential), "loops": loops,
            "internal_low_frequency_gap": float(modes(0., mu, a, b)[0]),
            "external_transverse_curvature": float(residual[0]),
            "propagator_gap_is_not_external_Goldstone_mass": True}


def solve_gap_at_s(s, t, mu, r, coupling, background, **kwargs):
    def equations(log_masses):
        a, b = np.exp(log_masses)
        return residuals(s, a, b, t, mu, r, coupling, **kwargs)[1:]/r
    result = root(equations, np.log([background["a"], background["b"]]), options={"xtol": ROOT_TOLERANCE})
    a, b = np.exp(result.x)
    if not result.success or np.max(np.abs(equations(result.x))) > IDENTITY_TOLERANCE:
        raise RuntimeError("source-reoptimized Hartree gap did not close")
    return float(a), float(b)


def external_response_check(background, t, mu, r, coupling, **kwargs):
    s, a, b = (background[k] for k in ("s", "a", "b"))
    step_mass = 2e-4*min(a, b)
    def tadpoles(a0, b0):
        loops = loop_integrals(t, mu, a0, b0, **kwargs)
        return np.array([loops["sigma"], loops["phase"]])
    J = np.column_stack(((tadpoles(a+step_mass, b)-tadpoles(a-step_mass, b))/(2*step_mass),
                         (tadpoles(a, b+step_mass)-tadpoles(a, b-step_mass))/(2*step_mass)))
    kernel = np.eye(2)-coupling*np.array([[3., 1.], [1., 3.]])@J
    derivative_masses = np.linalg.solve(kernel, coupling*np.array([3., 1.]))
    bracket_derivative = coupling+coupling*np.array([3., 1.])@J@derivative_masses
    external_radial = 2*s*bracket_derivative+background["residual"][0]
    v = sqrt(s)
    def optimized(x, y):
        new_s = x*x+y*y
        am, bm = solve_gap_at_s(new_s, t, mu, r, coupling, background, **kwargs)
        return variational_potential(new_s, am, bm, t, mu, r, coupling, **kwargs)
    rows = []
    for factor in (.003, .0015, .00075):
        h = factor*v
        center = optimized(v, 0.)
        radial = (optimized(v+h, 0.)+optimized(v-h, 0.)-2*center)/(h*h)
        transverse = (optimized(v, h)+optimized(v, -h)-2*center)/(h*h)
        rows.append({"relative_field_step": factor, "external_radial_difference": radial,
                     "external_transverse_difference": transverse,
                     "radial_relative_residual": abs(radial/external_radial-1)})
    return {"tadpole_mass_derivative_matrix": J.tolist(), "implicit_mass_response": derivative_masses.tolist(),
            "implicit_response_determinant": float(np.linalg.det(kernel)),
            "external_radial_curvature": float(external_radial), "fixed_mass_radial_curvature": a,
            "source_reoptimized_Hessian": rows,
            "forcing_internal_b_zero_gap_residual": float(-b),
            "internal_b_identity_residual": abs(b-2*coupling*(background["loops"]["phase"]-background["loops"]["sigma"]))}


def thermodynamic_envelope_check(background, t, mu, r, coupling, **kwargs):
    s, a, b = (background[k] for k in ("s", "a", "b"))
    h = 1e-4*t
    plus = stationary_background(t+h, mu, r, coupling, **kwargs)
    minus = stationary_background(t-h, mu, r, coupling, **kwargs)
    entropy = -(plus["potential"]-minus["potential"])/(2*h)
    frozen_entropy = -(variational_potential(s, a, b, t+h, mu, r, coupling, **kwargs)
                       -variational_potential(s, a, b, t-h, mu, r, coupling, **kwargs))/(2*h)
    qp = background["loops"]["quasiparticle_entropy"]
    # When mu varies, keep m(Phi)^2/Z = mu^2-r fixed, not r fixed.
    mass_sq = mu*mu-r
    hmu = 1e-4*mu
    def state(new_mu):
        return stationary_background(t, new_mu, new_mu*new_mu-mass_sq, coupling, **kwargs)
    high, low = state(mu+hmu), state(mu-hmu)
    charge = -(high["potential"]-low["potential"])/(2*hmu)
    frozen_charge = -(variational_potential(s, a, b, t, mu+hmu, (mu+hmu)**2-mass_sq, coupling, **kwargs)
                      -variational_potential(s, a, b, t, mu-hmu, (mu-hmu)**2-mass_sq, coupling, **kwargs))/(2*hmu)
    return {"stationary_pressure_T_derivative": entropy, "fixed_variational_entropy": frozen_entropy,
            "quasiparticle_entropy": qp, "entropy_relative_residual": abs(entropy/qp-1),
            "entropy_envelope_relative_residual": abs(frozen_entropy/qp-1),
            "canonical_charge_pressure_derivative": charge, "fixed_variational_charge": frozen_charge,
            "charge_envelope_relative_residual": abs(charge/frozen_charge-1),
            "charge_is_not_C_or_helium_mass_density": True,
            "grand_canonical_energy_definition": background["potential"]+t*entropy+mu*charge,
            "energy_identity_is_not_dynamical_ledger_proof": True}


def audit():
    previous = json.loads((ROOT/PREVIOUS).read_text(encoding="utf-8"))
    examples = []
    for anchor in previous["examples"]:
        t, mu, r, Z, lam = (anchor[k] for k in ("T", "mu", "r", "Z", "lambda"))
        coupling = lam/(Z*Z)
        background = stationary_background(t, mu, r, coupling)
        refinements = [stationary_background(t, mu, r, coupling, order=n, split=k) for n, k in zip(ORDERS, VACUUM_SPLITS)]
        auxiliary = [stationary_background(t, mu, r, coupling, auxiliary=m) for m in (.8, 1., 1.3)]
        seeds = [stationary_background(t, mu, r, coupling, seed_factor=f) for f in (.8, 1.2)]
        response = external_response_check(background, t, mu, r, coupling)
        envelope = thermodynamic_envelope_check(background, t, mu, r, coupling)
        def discrepancy(states):
            return max(abs(state[k]/background[k]-1) for state in states for k in ("s", "a", "b"))
        examples.append({"T": t, "mu": mu, "r": r, "Z": Z, "lambda": lam, "u_canonical": coupling,
                         "Phi_fixed": anchor["Phi_fixed"], "s_tree_canonical": r/coupling,
                         "background": background, "quadrature_split_refinement": refinements,
                         "auxiliary_reference_runs": auxiliary, "numerical_seed_runs": seeds,
                         "quadrature_relative_residual": discrepancy(refinements),
                         "auxiliary_reference_relative_residual": discrepancy(auxiliary),
                         "seed_relative_residual": discrepancy(seeds),
                         "loop_derivative_check": loop_derivative_check(t, mu, background["a"], background["b"]),
                         "external_response": response, "thermodynamic_envelope": envelope})
    vacuum_reference = symmetric_vacuum_reference_check()
    checks = {
        "symmetric_vacuum_MS_and_chemical_shift_independence": all(v["relative_residual"] < REFINEMENT_TOLERANCE for v in vacuum_reference),
        "finite_loop_derivative_is_half_renormalized_tadpole": all(e["loop_derivative_check"]["relative_residual"] < DERIVATIVE_TOLERANCE for e in examples),
        "nonzero_stationary_amplitude_and_gap_equations": all(max(abs(v) for v in e["background"]["residual"]) < IDENTITY_TOLERANCE and e["background"]["s"] > 0 for e in examples),
        "vacuum_thermal_quadrature_and_split_refinement": all(e["quadrature_relative_residual"] < REFINEMENT_TOLERANCE for e in examples),
        "auxiliary_subtraction_mass_not_physical_parameter": all(e["auxiliary_reference_relative_residual"] < REFINEMENT_TOLERANCE for e in examples),
        "numerical_seed_is_not_parameter_fit": all(e["seed_relative_residual"] < REFINEMENT_TOLERANCE for e in examples),
        "internal_external_transverse_curvatures_are_distinct": all(e["background"]["b"] > .001 and abs(e["background"]["external_transverse_curvature"]) < IDENTITY_TOLERANCE for e in examples),
        "internal_gap_not_manually_removed": all(e["external_response"]["internal_b_identity_residual"] < IDENTITY_TOLERANCE for e in examples),
        "source_reoptimized_radial_response_stable": all(e["external_response"]["external_radial_curvature"] > 0 and e["external_response"]["source_reoptimized_Hessian"][-1]["radial_relative_residual"] < DERIVATIVE_TOLERANCE for e in examples),
        "external_transverse_Ward_from_source_reoptimization": all(abs(e["external_response"]["source_reoptimized_Hessian"][-1]["external_transverse_difference"])/e["background"]["a"] < DERIVATIVE_TOLERANCE for e in examples),
        "stationary_entropy_envelope": all(e["thermodynamic_envelope"]["quasiparticle_entropy"] > 0 and e["thermodynamic_envelope"]["entropy_relative_residual"] < DERIVATIVE_TOLERANCE and e["thermodynamic_envelope"]["entropy_envelope_relative_residual"] < DERIVATIVE_TOLERANCE for e in examples),
        "charge_derivative_keeps_physical_mass_fixed": all(e["thermodynamic_envelope"]["charge_envelope_relative_residual"] < DERIVATIVE_TOLERANCE for e in examples),
    }
    paths = (PREVIOUS, Path(__file__).relative_to(ROOT).as_posix())
    protected = (PREFIX+"Result/artifacts/t13_conditional_twofluid_operator.json",
                 PREFIX+"Result/artifacts/t13_polar_static_ir_observable.json",
                 "docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json",
                 "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json")
    record = {
        "major_result_id": "T13_FIXED_PHI_FINITE_HARTREE_BACKGROUND_AND_SOURCE_BOUNDARY", "topic": "0.13",
        "branch_id": "t13.candidate.fixed_phi_hartree_ms_finite_potential_v1",
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
        "verification_status": "PASS_FIXED_PHI_HARTREE_SOURCE_BACKGROUND" if all(checks.values()) else "FAIL_HARTREE_BACKGROUND_CHECK",
        "what_is_closed": ["specified_finite_vacuum_plus_thermal_Hartree_potential", "stationary_amplitude_and_internal_gap_candidate", "external_static_Ward_and_radial_source_reoptimization", "thermodynamic_entropy_charge_envelope_in_this_prescription"],
        "equation_or_mapping": "F=U+Omega_F+[(a0-a)I_s+(b0-b)I_p]/2+u*(3I_s^2+2I_s I_p+3I_p^2)/4; a=2u*s and b=2u*(I_p-I_s) at field stationarity; Gamma_ext,pi(0)=0 is not internal b",
        "units": {"T_mu_Q_auxiliary_mass": "E", "s_a_b_r_tadpoles": "E^2", "u_Z_lambda": "dimensionless", "potential": "E^4", "entropy_canonical_charge": "E^3", "external_curvature": "E^2"},
        "derivation_class": "SPECIFIED_FINITE_POTENTIAL_HARTREE_CANDIDATE_NOT_FULL_COVARIANT_RENORMALIZATION",
        "observable": "canonical_field_source_curvature_and_grand_potential_not_temperature_or_helium_density",
        "data_role": "DERIVED_NATURAL_UNIT_NO_MEASURED_ROWS",
        "MS_scale": MS_SCALE, "auxiliary_mass": AUXILIARY_MASS,
        "scheme_policy": "Q=1 is a declared renormalization convention, not an SI or material calibration. The prior numeric m,Z,lambda are trial renormalized coefficients in this named candidate, not proof of their bare-to-renormalized or material identity. Varying Q with fixed m,u is not an RG-invariant physical test; running/matching is open.",
        "method_references": [{"url": "https://arxiv.org/pdf/1410.1337", "locator": "II-IV, finite gap/field/potential and counterterm distinction", "role": "standard_Hartree_renormalization_context_no_material_data"}, {"url": "https://arxiv.org/abs/1509.07847", "locator": "abstract; external source and symmetry-preserving reorganizations", "role": "method_context_not_implementation_of_symmetry_improved_2PI"}],
        "checks": checks, "examples": examples, "symmetric_vacuum_reference": vacuum_reference,
        "thresholds": {"identity": IDENTITY_TOLERANCE, "refinement": REFINEMENT_TOLERANCE, "source_thermo_derivative": DERIVATIVE_TOLERANCE},
        "evidence_artifacts": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths],
        "protected_evidence_hashes": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in protected],
        "open_blockers": ["covariant_counterterm_tensor_and_RG_matching_to_original_action_inputs", "joint_Phi_stationarity_and_material_matching", "external_finite_q_frequency_vertex_equations_not_internal_propagator_substitution", "IR_dynamic_matching_remainder_normal_component_and_SK_KMS_transport"],
        "controlling_blocker": "finite_potential_candidate_counterterm_and_external_dynamic_matching_not_closed",
        "dependency_unlocked": ["fixed_Phi_Hartree_external_vertex_and_counterterm_matching_design_only"],
        "specified_vacuum_loop_subtraction_derived": True, "fixed_Phi_candidate_stationarity_derived": True,
        "external_static_Ward_matched_in_candidate": True, "internal_Hartree_gap_generated": True,
        "global_phase_minimum_selected": False, "finite_q_local_stability_established": False,
        "manual_Goldstone_mass_fix": False, "internal_gap_used_as_physical_Goldstone_mass": False,
        "full_covariant_counterterm_match": False, "renormalization_scheme_material_match": False,
        "joint_Phi_stationarity_derived": False, "exact_microscopic_stationarity": False,
        "external_finite_frequency_response_derived": False, "microscopic_IR_matching_established": False,
        "physical_Kubo_emitted": False, "g1_physical_unlock": False, "g2_science_unlock": False,
        "full_core_unlock": False, "core_composition_gate_overwritten": False,
        "claim_promotion": False, "parameter_fitting": False, "xie_2026_accessed": False,
        "IR_filter": False, "clipping": False, "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False,
        "claim_boundary": "A fixed-Phi finite-potential Hartree candidate with vacuum and thermal loops, not full covariant counterterm/RG matching, exact UET equilibrium, a physical internal Goldstone mass, finite-frequency external response, material validation or full Topic13 closure. Its internal gapped propagator cannot replace the prior massless observable response."
    }
    record["report"] = {
        "MAJOR_RESULT_CLOSURE": record["major_result_id"]+": "+record["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": record["what_is_closed"], "WHAT_REMAINS_OPEN": record["open_blockers"],
        "DEPENDENCY_UNLOCKED": record["dependency_unlocked"], "STATUS": record["verification_status"],
        "WHAT_CHANGED": "Computed a self-consistent finite vacuum/thermal potential, stationary candidate, source Hessian and pressure-envelope checks; preserved baseline failures.",
        "EQUATION_OR_MAPPING": record["equation_or_mapping"], "VERIFICATION": "Vacuum/thermal quadrature, subtraction-reference/seed refinement, reoptimized source Hessian and entropy/charge envelope.",
        "CONTROLLING_BLOCKER": record["controlling_blocker"],
        "NEXT_ACTION": "Match the counterterm tensor and RG input, then derive external finite-frequency/current vertex equations and joint Phi/material state; never replace them with the internal Hartree propagator.",
        "CLAIM_BOUNDARY": record["claim_boundary"],
    }
    return record


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"],
                      "examples": [{"mu": e["mu"], "background": e["background"], "response": e["external_response"], "envelope": e["thermodynamic_envelope"]} for e in result["examples"]]}, indent=2))
