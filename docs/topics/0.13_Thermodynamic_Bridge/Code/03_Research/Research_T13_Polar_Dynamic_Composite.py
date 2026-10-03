"""Conditional phase-lane composite response, not a microscopic thermal closure.

Keep the same longitudinal Cartesian source. Compute its Gaussian two-phase
continuum rather than interpreting a static inverse as a single relaxation pole.
The unrenormalized background and microscopic finite-T current remain open.
"""

from __future__ import annotations

import hashlib
import json
from math import isfinite, pi, sqrt
from pathlib import Path
import runpy

import numpy as np
from scipy.integrate import quad
from scipy.special import zeta

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
POLAR_PATH = PREFIX+"Code/03_Research/Research_T13_Polar_Static_IR_Observable.py"
POLAR_ARTIFACT = PREFIX+"Result/artifacts/t13_polar_static_ir_observable.json"
POLAR = runpy.run_path(str(ROOT/POLAR_PATH))
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_polar_dynamic_composite.json")

# Fixed before running; scales are the previous witnesses, not material fits.
Q_REFINEMENT = (.005, .0025, .00125)
FREQUENCY_RATIOS = (.3+.4j, 1.4+.6j, .8j)
SPECTRAL_RATIOS = (.4, 1.6)
MATSUBARA_TERMS = (128, 256)
ALGEBRA_TOLERANCE = 1e-10
INTEGRAL_TOLERANCE = 1e-7
CLASSICAL_LIMIT_TOLERANCE = .01


def validate(q, t, x, stiffness, speed):
    if not all(isfinite(v) for v in (q, t, x, stiffness, speed)):
        raise ValueError("finite natural-unit inputs required")
    if min(q, x, stiffness, speed) <= 0 or t < 0 or speed > 1:
        raise ValueError("q,x,rho_s>0, T>=0 and 0<c<=1 required")


def retarded_frequency(z):
    z = complex(z)
    if not np.isfinite(z) or (z != 0 and z.imag <= 0):
        raise ValueError("static zero or upper-half-plane frequency required")
    return z


def bose(energy, t):
    if not isfinite(energy) or energy <= 0 or not isfinite(t) or t < 0:
        raise ValueError("positive energy and T>=0 required")
    if t == 0:
        return 0.
    return float(np.exp(-energy/t)/(-np.expm1(-energy/t)))


def point_thermal_bubble(e, f, t, z=0j):
    """T sum of [(nu^2+e^2)((nu+Omega)^2+f^2)]^-1 minus vacuum.

    Pair creation and thermally occupied scattering are separate. The static
    coincident-energy divided difference is taken analytically, not dropped.
    """
    z = retarded_frequency(z)
    ne, nf = bose(e, t), bose(f, t)
    total, difference = e+f, e-f
    pair = (ne+nf)*total/(2*e*f*(total*total-z*z))
    if t == 0:
        divided = 0.
    else:
        gap = abs(difference)
        factor = -np.expm1(-gap/t)/gap if gap != 0 else 1/t
        divided = np.exp(-min(e, f)/t)*factor/((-np.expm1(-e/t))*(-np.expm1(-f/t)))
    if z == 0:
        scatter = divided/(2*e*f)
    elif difference == 0:
        scatter = 0.
    else:
        scatter = divided*difference*difference/(2*e*f*(difference*difference-z*z))
    return pair+scatter


def point_matsubara_check(e, f, t, harmonic, terms):
    if t <= 0 or harmonic not in (0, 1) or not isinstance(terms, int) or isinstance(terms, bool) or terms < 32:
        raise ValueError("T>0, harmonic 0/1 and integer terms>=32 required")
    omega = 2*pi*t*harmonic
    nu = 2*pi*t*np.arange(-terms, terms+1, dtype=float)
    finite = t*np.sum(1/((nu*nu+e*e)*((nu+omega)**2+f*f)))
    # Independent nu^-4 tail; the next omitted even term is order terms^-5.
    tail = 2*t*zeta(4., terms+1)/(2*pi*t)**4
    vacuum = (e+f)/(2*e*f*((e+f)**2+omega*omega))
    direct = finite+tail-vacuum
    spectral = point_thermal_bubble(e, f, t, 1j*omega)
    return {"terms": terms, "harmonic": harmonic, "e": e, "f": f,
            "direct_thermal_sum": float(direct), "spectral_thermal_sum": float(spectral.real),
            "relative_disagreement": float(abs(direct-spectral)/abs(spectral))}


def classical_response(q, z, t, x, stiffness, speed):
    validate(q, t, x, stiffness, speed)
    z = retarded_frequency(z)
    if z == 0:
        return complex(x*t/(16*stiffness**2*q))
    a = speed*q
    return 1j*x*t/(16*pi*stiffness**2*q)*np.log((z+a)/(z-a))


def classical_loop_integral(q, z, t, x, stiffness, speed):
    """Independent pair/scattering momentum integral in S=e+f,D=e-f.

    |D|<=c*q<=S; integrating the triangle's other variable analytically
    leaves two real intervals. No mass, momentum cutoff or broadening enters.
    """
    validate(q, t, x, stiffness, speed)
    zbar = retarded_frequency(z)/(speed*q)
    def integrand(v):
        logarithm = np.log1p(v)-np.log1p(-v)
        pair = logarithm/(v*(1-zbar*zbar*v*v))
        scatter = v*logarithm/(v*v-zbar*zbar)
        return pair+scatter
    real = quad(lambda v: integrand(v).real, 0., 1., epsabs=2e-10, epsrel=2e-10)[0]
    imaginary = quad(lambda v: integrand(v).imag, 0., 1., epsabs=2e-10, epsrel=2e-10)[0]
    return x*t/(8*pi*pi*stiffness**2*q)*complex(real, imaginary)


def spectral_response(q, omega, t, x, stiffness, speed, thermal_only=True):
    """Exact Im chi in the declared all-momentum linear Gaussian extension.

    The vacuum continuum is finite spectrally but its static dispersion needs
    UV subtraction. Return the UV-finite thermal difference by default.
    The logarithmic threshold is unbounded and integrable; never clip it.
    """
    validate(q, t, x, stiffness, speed)
    if not isfinite(omega) or omega < 0:
        raise ValueError("finite omega>=0 required")
    a = speed*q
    if omega == a:
        raise ValueError("exact two-phase threshold is singular; no broadening/clipping")
    if omega == 0:
        return 0.
    low, high = abs(omega-a)/2, (omega+a)/2
    logarithm = (np.log(-np.expm1(-high/t))-np.log(-np.expm1(-low/t))) if t > 0 else 0.
    vacuum = a/2 if omega > a and not thermal_only else 0.
    return float(x/(16*pi*stiffness**2*q)*(vacuum+t*logarithm))


def spectral_phase_space_check(q, omega, t, x, stiffness, speed):
    """Independent Bose integral over the on-shell triangle, not a log formula."""
    validate(q, t, x, stiffness, speed)
    if omega <= 0 or omega == speed*q:
        raise ValueError("positive off-threshold frequency required")
    a = speed*q
    low, high = abs(omega-a)/2, (omega+a)/2
    integral = quad(lambda u: bose(u, t), low, high, epsabs=2e-11, epsrel=2e-11)[0]
    vacuum = a/2 if omega > a else 0.
    value = x/(16*pi*stiffness**2*q)*(vacuum+integral)
    exact = spectral_response(q, omega, t, x, stiffness, speed, thermal_only=False)
    return {"omega_over_cq": omega/a, "channel": "PAIR_CREATION" if omega > a else "THERMAL_SCATTERING",
            "direct_phase_space": value, "closed_logarithm": exact,
            "relative_disagreement": abs(value/exact-1)}


def thermal_dispersion(q, z, t, x, stiffness, speed):
    """Kramers-Kronig thermal difference with both continuum intervals.

    omega=c*q*v below threshold and omega=c*q/v above threshold. These
    changes of integration coordinate cover all positive frequencies.
    """
    validate(q, t, x, stiffness, speed)
    zbar = retarded_frequency(z)/(speed*q)
    a = speed*q
    def integrand(v):
        lower = v*spectral_response(q, a*v, t, x, stiffness, speed)/(v*v-zbar*zbar)
        upper = spectral_response(q, a/v, t, x, stiffness, speed)/(v*(1-zbar*zbar*v*v))
        return lower+upper
    real = quad(lambda v: integrand(v).real, 0., 1., epsabs=2e-8, epsrel=2e-9)[0]
    imaginary = quad(lambda v: integrand(v).imag, 0., 1., epsabs=2e-8, epsrel=2e-9)[0]
    return 2/pi*complex(real, imaginary)


def classical_time_response(time, q, t, x, stiffness, speed):
    validate(q, t, x, stiffness, speed)
    if not isfinite(time):
        raise ValueError("finite real time required")
    if time < 0:
        return 0.
    # np.sinc implements the continuous t=0+ limit, not a time cutoff.
    return float(x*t*speed/(8*pi*stiffness**2)*np.sinc(speed*q*time/pi))


def time_transform_check(q, z, t, x, stiffness, speed):
    validate(q, t, x, stiffness, speed)
    zbar = retarded_frequency(z)/(speed*q)
    if zbar.imag <= 0:
        raise ValueError("upper-half-plane frequency required for convergent time integral")
    def integrand(u):
        return np.exp(1j*zbar*u)*np.sinc(u/pi)
    real = quad(lambda u: integrand(u).real, 0., np.inf, epsabs=2e-10, epsrel=2e-10)[0]
    imaginary = quad(lambda u: integrand(u).imag, 0., np.inf, epsabs=2e-10, epsrel=2e-10)[0]
    integrated = x*t/(8*pi*stiffness**2*q)*complex(real, imaginary)
    closed = classical_response(q, z, t, x, stiffness, speed)
    return {"integrated": [integrated.real, integrated.imag], "closed": [closed.real, closed.imag],
            "relative_disagreement": float(abs(integrated/closed-1))}


def phase_current_kernel(nu, momentum, stiffness, speed):
    """Euclidean gauge-source Hessian including its local contact term."""
    q = np.concatenate(([nu], np.asarray(momentum, dtype=float)))
    if q.shape != (4,) or not np.all(np.isfinite(q)) or not np.any(q) or not isfinite(stiffness) or stiffness <= 0 or not isfinite(speed) or not 0 < speed <= 1:
        raise ValueError("nonzero finite Euclidean four-momentum and positive coefficients required")
    metric = np.diag([stiffness/speed**2, stiffness, stiffness, stiffness])
    v = metric@q
    return metric-np.outer(v, v)/float(q@v)


def source_current_check(nu, momentum, stiffness, speed):
    q = np.concatenate(([nu], np.asarray(momentum, dtype=float)))
    W = np.diag([stiffness/speed**2, stiffness, stiffness, stiffness])
    def source_action(a):
        theta = float(q@W@a)/(q@W@q)
        shifted = theta*q-a
        return float(.5*shifted@W@shifted)
    h = 1e-4
    numeric = np.empty((4, 4))
    eye = np.eye(4)
    for i in range(4):
        for j in range(4):
            numeric[i, j] = (source_action(h*(eye[i]+eye[j]))+source_action(-h*(eye[i]+eye[j]))
                             -source_action(h*(eye[i]-eye[j]))-source_action(-h*(eye[i]-eye[j])))/(4*h*h)
    kernel = phase_current_kernel(nu, momentum, stiffness, speed)
    return {"source_Hessian_residual": float(np.max(np.abs(kernel-numeric))),
            "Ward_residual": float(np.max(np.abs(q@kernel))),
            "without_contact_Ward_residual": float(np.max(np.abs(q@(kernel-W))))}


def detailed_balance_check(e, f, t, pair=True):
    if t <= 0 or e <= 0 or f <= 0 or (not pair and e <= f):
        raise ValueError("positive T/energies; scattering test requires e>f")
    ne, nf = bose(e, t), bose(f, t)
    greater = (1+ne)*(1+nf) if pair else nf*(1+ne)
    lesser = ne*nf if pair else ne*(1+nf)
    omega = e+f if pair else e-f
    # The positive-frequency commutator is greater-lesser; symmetric noise
    # is their half-sum. Use the full Gaussian correlator, not thermal-only chi.
    commutator = greater-lesser
    symmetric = .5*(greater+lesser)
    return {"channel": "PAIR" if pair else "SCATTERING", "omega": omega,
            "detailed_balance_residual": abs(lesser/greater-np.exp(-omega/t)),
            "FDT_relative_residual": abs(symmetric/(.5*commutator/np.tanh(omega/(2*t)))-1),
            "positive_commutator": bool(commutator > 0)}


def audit():
    prior = json.loads((ROOT/POLAR_ARTIFACT).read_text(encoding="utf-8"))
    examples = []
    for anchor in prior["examples"]:
        t, mu, r, Z, lam = (anchor[k] for k in ("T", "mu", "r", "Z", "lambda"))
        x, stiffness, c = Z*r/lam, Z*Z*r/lam, sqrt(r/(r+2*mu*mu))
        q = Q_REFINEMENT[1]
        dynamic = []
        for ratio in FREQUENCY_RATIOS:
            z = ratio*c*q
            value = classical_response(q, z, t, x, stiffness, c)
            integral = classical_loop_integral(q, z, t, x, stiffness, c)
            dynamic.append({"frequency_over_cq": [ratio.real, ratio.imag],
                            "classical_response": [value.real, value.imag],
                            "pair_scattering_integral_relative_residual": float(abs(integral/value-1)),
                            "time_transform": time_transform_check(q, z, t, x, stiffness, c)})
        refinement = []
        for q0 in Q_REFINEMENT:
            static = thermal_dispersion(q0, 0j, t, x, stiffness, c).real
            expected = POLAR["static_response"](q0, t, mu, r, Z, lam)["cartesian_longitudinal_composite_susceptibility"]
            z = FREQUENCY_RATIOS[0]*c*q0
            quantum = thermal_dispersion(q0, z, t, x, stiffness, c)
            classical = classical_response(q0, z, t, x, stiffness, c)
            refinement.append({"q": q0, "thermal_static_dispersion": static,
                               "previous_classical_static": expected, "static_relative_difference": abs(static/expected-1),
                               "quantum_thermal_response": [quantum.real, quantum.imag],
                               "dynamic_classical_relative_difference": float(abs(quantum/classical-1)),
                               "cq_over_T": c*q0/t, "q_over_amplitude_scale": q0/sqrt(2*r)})
        examples.append({"T": t, "mu": mu, "r": r, "Z": Z, "lambda": lam,
                         "Phi_fixed": anchor["Phi_fixed"], "x_tree": x, "rho_s_tree": stiffness, "c_tree": c,
                         "T_over_linear_phase_energy_domain": t/(c*sqrt(2*r)),
                         "all_momentum_linear_extension_is_not_microscopic_admission": True,
                         "dynamic": dynamic, "thermal_to_classical_refinement": refinement,
                         "spectral_phase_space": [spectral_phase_space_check(q, ratio*c*q, t, x, stiffness, c) for ratio in SPECTRAL_RATIOS],
                         "current_source_check": source_current_check(.13, [.1, -.04, .02], stiffness, c),
                         "negative_time_response": classical_time_response(-1., q, t, x, stiffness, c),
                         "future_time_values": [classical_time_response(v/(c*q), q, t, x, stiffness, c) for v in (.1, 2., 4.)]})
    matsubara = [point_matsubara_check(e, f, .22, h, n) for e, f in ((.029, .041), (.07, .07)) for h in (0, 1) for n in MATSUBARA_TERMS]
    balance = [detailed_balance_check(.13, .07, .22, pair) for pair in (True, False)]
    checks = {
        "independent_pair_scattering_integral": all(d["pair_scattering_integral_relative_residual"] < INTEGRAL_TOLERANCE for e in examples for d in e["dynamic"]),
        "independent_retarded_time_transform": all(d["time_transform"]["relative_disagreement"] < INTEGRAL_TOLERANCE for e in examples for d in e["dynamic"]),
        "point_Matsubara_vs_thermal_spectral_sum": all(v["relative_disagreement"] < INTEGRAL_TOLERANCE for v in matsubara),
        "on_shell_phase_space_vs_logarithmic_spectrum": all(v["relative_disagreement"] < INTEGRAL_TOLERANCE for e in examples for v in e["spectral_phase_space"]),
        "thermal_static_returns_previous_IR_coefficient": all(e["thermal_to_classical_refinement"][-1]["static_relative_difference"] < CLASSICAL_LIMIT_TOLERANCE for e in examples),
        "static_and_dynamic_classical_refinement_improves": all(all(b[k] < a[k] for a, b in zip(e["thermal_to_classical_refinement"], e["thermal_to_classical_refinement"][1:])) for e in examples for k in ("static_relative_difference", "dynamic_classical_relative_difference")),
        "dynamic_classical_IR_limit": all(e["thermal_to_classical_refinement"][-1]["dynamic_classical_relative_difference"] < CLASSICAL_LIMIT_TOLERANCE for e in examples),
        "current_source_Hessian_and_contact_Ward_identity": all(e["current_source_check"]["source_Hessian_residual"] < ALGEBRA_TOLERANCE and e["current_source_check"]["Ward_residual"] < ALGEBRA_TOLERANCE and e["current_source_check"]["without_contact_Ward_residual"] > .001 for e in examples),
        "conditional_Gaussian_detailed_balance_and_FDT": all(v["detailed_balance_residual"] < ALGEBRA_TOLERANCE and v["FDT_relative_residual"] < ALGEBRA_TOLERANCE and v["positive_commutator"] for v in balance),
        "retarded_time_support_and_nonexponential_tail": all(e["negative_time_response"] == 0 and e["future_time_values"][-1] < 0 for e in examples),
    }
    paths = (POLAR_PATH, POLAR_ARTIFACT, Path(__file__).relative_to(ROOT).as_posix())
    protected = (PREFIX+"Result/artifacts/t13_conditional_twofluid_operator.json",
                 "docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json",
                 "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json")
    record = {
        "major_result_id": "T13_CONDITIONAL_DYNAMIC_COMPOSITE_AND_CURRENT_MATCH", "topic": "0.13",
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
        "verification_status": "PASS_CONDITIONAL_PHASE_DYNAMIC_RESPONSE" if all(checks.values()) else "FAIL_DYNAMIC_RESPONSE_CHECK",
        "what_is_closed": ["same_Cartesian_composite_source_dynamic_IR_response", "pair_creation_and_thermal_scattering_spectrum", "causal_time_kernel_and_static_IR_limit", "contact_completed_Gaussian_current_Ward_identity", "conditional_Gaussian_detailed_balance_not_microscopic_SK_matching"],
        "equation_or_mapping": "chi_cl^R=i*x*T/(16*pi*rho_s^2*q)*log[(z+cq)/(z-cq)]; chi_cl^R(t)=Theta(t)*x*T/(8*pi*rho_s^2*q)*sin(cqt)/t",
        "units": {"T_q_z_mu": "E", "x_rho_s": "E^2", "c_theta": "dimensionless", "chi_frequency": "E^-2", "chi_time": "E^-1", "time": "E^-1", "gauge_source_a": "E", "current_source_Hessian": "E^2", "Cartesian_source_J": "E^3"},
        "derivation_class": "CONDITIONAL_LEADING_GAUSSIAN_PHASE_SOURCE_RESPONSE_WITH_LINEAR_DISPERSION",
        "observable": "Cartesian_longitudinal_source_composite_not_temperature_heat_flux_or_Kubo",
        "data_role": "DERIVED_NATURAL_UNIT_NO_MEASURED_ROWS",
        "assumptions": ["fixed_Phi", "three_spatial_dimensions", "existing_tree_x_stiffness_speed_for_prior_IR_match", "ordered_positive_stiffness_phase", "classical_IR_external_frequencies_and_cq_much_less_than_T", "linear_Gaussian_continuum_extension_only_for_quantum_thermal_crosscheck", "microscopic_high_momentum_and_vacuum_matching_open"],
        "method_references": [{"url": "https://arxiv.org/html/1011.3324v2", "locator": "II.2 and introduction; model classes differ", "role": "amplitude_direction_method_context_not_finiteT_UET_validation"}, {"url": "https://arxiv.org/abs/1108.5207", "locator": "abstract; longitudinal_vs_scalar_observable distinction", "role": "observable_choice_context_not_imported_thermal_data"}],
        "thresholds": {"algebra": ALGEBRA_TOLERANCE, "independent_integrals": INTEGRAL_TOLERANCE, "thermal_to_classical_IR_relative": CLASSICAL_LIMIT_TOLERANCE},
        "Q_refinement": Q_REFINEMENT, "frequency_ratios": [[v.real, v.imag] for v in FREQUENCY_RATIOS],
        "checks": checks, "examples": examples, "point_Matsubara_checks": matsubara, "detailed_balance_checks": balance,
        "evidence_artifacts": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths],
        "protected_evidence_hashes": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in protected],
        "open_blockers": ["source_complete_renormalized_interacting_background_and_joint_Phi_stationarity", "dynamic_current_vertices_beyond_leading_phase_lane_and_controlled_remainder", "material_source_detector_and_independent_parameter_inputs", "finiteT_normal_component_transport_and_microscopic_SK_KMS_matching"],
        "controlling_blocker": "renormalized_stationary_background_and_dynamic_matching_remainder_not_closed",
        "dependency_unlocked": ["same_lane_dynamic_source_and_measurement_design_only"],
        "conditional_real_axis_composite_spectrum_derived": True, "conditional_time_response_derived": True,
        "full_Cartesian_response_assembled": False, "amplitude_phase_hybrid_response_included": False,
        "microscopic_real_axis_response_admitted": False, "joint_Phi_stationarity_derived": False,
        "renormalized_order_parameter_matched": False, "microscopic_IR_resummation_derived": False,
        "controlled_truncation_error_established": False, "microscopic_SK_KMS_matched": False,
        "physical_Kubo_emitted": False, "g1_physical_unlock": False, "g2_science_unlock": False,
        "full_core_unlock": False, "core_composition_gate_overwritten": False,
        "claim_promotion": False, "parameter_fitting": False, "xie_2026_accessed": False,
        "phase_mass_added": False, "IR_filter": False, "clipping": False, "threshold_broadening": False,
        "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False,
        "claim_boundary": "Conditional leading phase/composite contribution, not the full Cartesian susceptibility with amplitude/phase hybrid modes. Continuum absorption and a retarded tail are not collision damping, viscosity, thermal conductivity, complete SK/KMS, independent material prediction, microscopic stationarity or global UET closure. The q-dependent composite frequency protocol must not be replaced by a single fitted relaxation pole."
    }
    record["report"] = {
        "MAJOR_RESULT_CLOSURE": record["major_result_id"]+": "+record["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": record["what_is_closed"], "WHAT_REMAINS_OPEN": record["open_blockers"],
        "DEPENDENCY_UNLOCKED": record["dependency_unlocked"], "STATUS": record["verification_status"],
        "WHAT_CHANGED": "Derived conditional composite pair/scattering spectrum and time kernel with current contact/source checks; preserved microscopic background failures.",
        "EQUATION_OR_MAPPING": record["equation_or_mapping"],
        "VERIFICATION": "Independent Matsubara, phase-space, classical loop, time-transform, spectral-static refinement and source-current Hessian checks.",
        "CONTROLLING_BLOCKER": record["controlling_blocker"],
        "NEXT_ACTION": "Close source-complete renormalized/interacting background and dynamic remainder before admitting physical response or source/detector comparison.",
        "CLAIM_BOUNDARY": record["claim_boundary"],
    }
    return record


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"], "examples": result["examples"]}, indent=2))
