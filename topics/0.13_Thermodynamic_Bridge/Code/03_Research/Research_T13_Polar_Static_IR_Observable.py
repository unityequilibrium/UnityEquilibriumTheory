"""Same-field polar coordinates and conditional static Goldstone observable.

Reconstruct a Cartesian longitudinal source susceptibility from its composite
phase contribution. Do not add a phase mass, invert a bare-loop failure as a
physical state, or claim that a polar Hessian establishes thermal stationarity.
"""

from __future__ import annotations

import hashlib
import json
from math import cos, exp, isfinite, pi, sin, sqrt
from pathlib import Path
import runpy

import numpy as np
from scipy.integrate import quad
from scipy.special import i0e

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
FINITE_SCRIPT = PREFIX+"Code/03_Research/Research_T13_Finite_Momentum_Thermal_1PI.py"
FINITE_ARTIFACT = PREFIX+"Result/artifacts/t13_finite_momentum_thermal_1pi.json"
WARD_ARTIFACT = PREFIX+"Result/artifacts/t13_thermal_oneloop_ward_current.json"
FINITE = runpy.run_path(str(ROOT/FINITE_SCRIPT))
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_polar_static_ir_observable.json")
Q_REFINEMENT = (.005, .0025, .00125)
ALGEBRA_TOLERANCE = 1e-10
SOURCE_DIFFERENCE_TOLERANCE = 1e-5


def validate(t, mu, r, Z, lam):
    FINITE["WARD"]["validate"](t, mu, r, Z, lam)


def polar_map(rho: float, theta: float):
    if not isfinite(rho) or not isfinite(theta) or rho <= 0:
        raise ValueError("finite rho>0 and theta required; the polar origin is singular")
    return np.array([rho*cos(theta), rho*sin(theta)])


def polar_jacobian(rho: float, theta: float):
    polar_map(rho, theta)
    return np.array([[cos(theta), -rho*sin(theta)], [sin(theta), rho*cos(theta)]])


def cartesian_density(field, dt, gradients, mu, r, Z, lam, source=(0., 0.)):
    validate(0., mu, r, Z, lam)
    field, dt, gradients, source = map(lambda v: np.asarray(v, dtype=float),
                                      (field, dt, gradients, source))
    if field.shape != (2,) or dt.shape != (2,) or source.shape != (2,) or gradients.ndim != 2 or gradients.shape[1] != 2:
        raise ValueError("two Cartesian components and spatial derivative rows required")
    if not all(np.all(np.isfinite(v)) for v in (field, dt, gradients, source)):
        raise ValueError("finite field, derivatives and source required")
    x = float(field@field)
    return (Z/2*(float(dt@dt)+float(np.sum(gradients*gradients)))
            -Z*r*x/2+lam*x*x/4-float(source@field)
            +1j*Z*mu*(field[0]*dt[1]-field[1]*dt[0]))


def polar_density(rho, theta, drho_dt, dtheta_dt, drho_dx, dtheta_dx,
                  mu, r, Z, lam, source=(0., 0.)):
    field = polar_map(rho, theta)
    validate(0., mu, r, Z, lam)
    drho_dx, dtheta_dx = np.asarray(drho_dx, dtype=float), np.asarray(dtheta_dx, dtype=float)
    if drho_dx.ndim != 1 or drho_dx.shape != dtheta_dx.shape:
        raise ValueError("equal spatial derivative vectors required")
    if not all(np.all(np.isfinite(v)) for v in (drho_dt, dtheta_dt, drho_dx, dtheta_dx, source)):
        raise ValueError("finite derivatives and source required")
    return (Z/2*(drho_dt**2+rho*rho*dtheta_dt**2+float(drho_dx@drho_dx)
                 +rho*rho*float(dtheta_dx@dtheta_dx))
            -Z*r*rho*rho/2+lam*rho**4/4-float(np.asarray(source)@field)
            +1j*Z*mu*rho*rho*dtheta_dt)


def offshell_angular_hessian(rho, r, Z, lam):
    """Full Hessian chain rule, including the radial gradient term."""
    if not all(isfinite(v) for v in (rho, r, Z, lam)) or min(rho, r, Z, lam) <= 0:
        raise ValueError("positive finite field and coefficients required")
    tadpole = rho*(-Z*r+lam*rho*rho)
    cartesian_transverse = -Z*r+lam*rho*rho
    linear_pullback = rho*rho*cartesian_transverse
    gradient_term = -rho*tadpole
    return {"radial_tadpole": tadpole, "cartesian_transverse_hessian": cartesian_transverse,
            "linear_pullback": linear_pullback, "gradient_chain_term": gradient_term,
            "polar_angular_hessian": linear_pullback+gradient_term}


def source_completed_gaussian(nu, k, rho, mu, r, Z, lam, energy_reference=1.):
    """Cartesian Legendre source restores the offshell polar Gaussian kernel.

    At theta=0 the classical source J_l=U'(rho). Its +J_l*rho theta^2/2
    contribution must be included before identifying a Cartesian 1PI action.
    The constant-background polar Jacobian cancels the rho^2 determinant
    factor mode by mode in a common regulator; vacuum counterterms remain open.
    """
    validate(0., mu, r, Z, lam)
    polar_map(rho, 0.)
    if not isfinite(energy_reference) or energy_reference <= 0:
        raise ValueError("positive natural-unit energy reference required for dimensionless logs")
    if not all(isfinite(v) for v in (nu, k)) or k < 0:
        raise ValueError("finite nu and k>=0 required")
    source = rho*(-Z*r+lam*rho*rho)
    kernel = np.array([[Z*(nu*nu+k*k-r)+3*lam*rho*rho, -2*Z*mu*rho*nu],
                       [2*Z*mu*rho*nu, Z*rho*rho*(nu*nu+k*k)+source*rho]])
    # H_hh, H_h_theta, H_theta_theta carry E^2, E^3, E^4 respectively.
    reference_metric = np.diag([1/energy_reference, 1/energy_reference**2])
    sign, logdet = np.linalg.slogdet(reference_metric@kernel@reference_metric)
    if sign <= 0 or kernel[0, 0] <= 0 or kernel[1, 1] <= 0:
        raise ValueError("stable positive Gaussian diagonal/determinant required; no clipping")
    return kernel, float(.5*logdet-np.log(rho/energy_reference)), source


def polar_quadratic_kernel(nu, k, mu, r, Z, lam):
    validate(0., mu, r, Z, lam)
    if not all(isfinite(v) for v in (nu, k)) or k < 0:
        raise ValueError("finite nu and nonnegative k required")
    A = sqrt(Z*r/lam)
    return Z*np.array([[nu*nu+k*k+2*r, -2*mu*A*nu],
                       [2*mu*A*nu, A*A*(nu*nu+k*k)]])


def phase_schur(nu, k, mu, r, Z, lam):
    kernel = polar_quadratic_kernel(nu, k, mu, r, Z, lam)
    return float(kernel[1, 1]-kernel[1, 0]*kernel[0, 1]/kernel[0, 0])


def spatial_source_density(phase_gradient, connection, stiffness):
    phase_gradient, connection = np.asarray(phase_gradient), np.asarray(connection)
    if phase_gradient.shape != connection.shape or phase_gradient.ndim != 1 or not isfinite(stiffness) or stiffness <= 0:
        raise ValueError("matching gradient vectors and positive stiffness required")
    if not np.all(np.isfinite(phase_gradient)) or not np.all(np.isfinite(connection)):
        raise ValueError("finite gradients required")
    shifted = phase_gradient-connection
    return float(.5*stiffness*(shifted@shifted))


def action_coordinate_check(rho, mu, r, Z, lam):
    theta, drho_dt, dtheta_dt = .7, .12, -.18
    drho_dx, dtheta_dx, source = np.array([.1, -.2, .3]), np.array([-.08, .04, .09]), (.03, -.02)
    jacobian = polar_jacobian(rho, theta)
    dt = jacobian@np.array([drho_dt, dtheta_dt])
    gradients = np.stack((drho_dx, dtheta_dx), axis=-1)@jacobian.T
    cartesian = cartesian_density(polar_map(rho, theta), dt, gradients, mu, r, Z, lam, source)
    polar = polar_density(rho, theta, drho_dt, dtheta_dt, drho_dx, dtheta_dx, mu, r, Z, lam, source)
    step = 1e-5
    def local_action(angle):
        return polar_density(rho, angle, 0., 0., [0.], [0.], mu, r, Z, lam, source).real
    torque = rho*(source[0]*sin(theta)-source[1]*cos(theta))
    numeric_torque = (local_action(theta+step)-local_action(theta-step))/(2*step)
    return {"full_source_action_residual": float(abs(cartesian-polar)),
            "Jacobian_determinant_residual": abs(float(np.linalg.det(jacobian))-rho),
            "source_phase_torque": torque, "source_torque_difference_residual": abs(torque-numeric_torque)}


def static_response(q, t, mu, r, Z, lam, stiffness=None):
    validate(t, mu, r, Z, lam)
    if not isfinite(q) or q <= 0:
        raise ValueError("finite q>0 required; longitudinal susceptibility diverges at q=0")
    x = Z*r/lam
    rho_s = Z*x if stiffness is None else stiffness
    if not isfinite(rho_s) or rho_s <= 0:
        raise ValueError("positive finite phase stiffness required")
    radial = 1/(Z*(q*q+2*r))
    # Cartesian phi_l = A+h-A*theta^2/2. Connected Wick contraction
    # contributes 2; one beta=1/T converts static covariance to susceptibility.
    composite = x*t/(2*rho_s*rho_s)*FINITE["convolution_3d"](q, 0., 0.)
    chi = radial+composite
    return {"x_tree": x, "stiffness": rho_s,
            "radial_modulus_susceptibility": radial,
            "cartesian_longitudinal_composite_susceptibility": composite,
            "cartesian_longitudinal_susceptibility": chi,
            "normalized_longitudinal_inverse": 1/(Z*chi),
            "inverse_expansion_parameter": composite/radial,
            "small_correction_inverse_term": -(q*q+2*r)**2*Z*composite,
            "leading_inverse_per_q": 16*rho_s*rho_s/(Z*x*t) if t > 0 else None,
            "small_q_over_radial_scale": q/sqrt(2*r)}


def gaussian_source_check(t=.22, amplitude=.7):
    """Independent Gaussian generating function vs connected quadratic observable."""
    H = np.diag([.8, 1.3, 2.])
    V = np.array([[.4, .2, 0.], [.2, -.3, .1], [0., .1, .5]])
    def free_energy(j):
        sign, logdet = np.linalg.slogdet(H+j*amplitude*V)
        if sign <= 0:
            raise ValueError("Gaussian source matrix not positive")
        return .5*t*logdet
    step = 1e-4
    difference = -(free_energy(step)+free_energy(-step)-2*free_energy(0.))/step**2
    # For O=-A/2 theta^T V theta, connected Var(O)/T follows Wick's theorem.
    covariance = t*np.linalg.inv(H)
    wick = amplitude*amplitude*np.trace(covariance@V@covariance@V)/(2*t)
    return {"source_difference": float(difference), "connected_Wick_susceptibility": float(wick),
            "relative_disagreement": float(abs(difference/wick-1))}


def measure_integral(a, source):
    if not isfinite(a) or a <= 0 or not isfinite(source):
        raise ValueError("a>0 and finite source required")
    def integrand(rho, jacobian):
        argument = abs(source*rho)
        return 2*pi*(rho if jacobian else 1.)*exp(-a*rho*rho+argument)*i0e(argument)
    polar = quad(lambda rho: integrand(rho, True), 0., np.inf, epsabs=1e-11, epsrel=1e-11)[0]
    omitted = quad(lambda rho: integrand(rho, False), 0., np.inf, epsabs=1e-11, epsrel=1e-11)[0]
    cartesian = pi/a*exp(source*source/(4*a))
    return {"cartesian_integral": cartesian, "polar_with_jacobian": polar,
            "polar_without_jacobian": omitted, "relative_disagreement": abs(polar/cartesian-1)}


def audit():
    previous = json.loads((ROOT/FINITE_ARTIFACT).read_text(encoding="utf-8"))
    ward = json.loads((ROOT/WARD_ARTIFACT).read_text(encoding="utf-8"))
    examples = []
    for anchor, zero in zip(previous["examples"], ward["examples"]):
        t, mu, r, Z, lam = (anchor[key] for key in ("T", "mu", "r", "Z", "lambda"))
        assert all(anchor[key] == zero[key] for key in ("T", "mu", "r", "Z", "lambda", "Phi_fixed"))
        x, A = Z*r/lam, sqrt(Z*r/lam)
        coefficient = -(2*r)**2*Z*x*t/(16*(Z*x)**2)
        q_records = [{"q": q, **static_response(q, t, mu, r, Z, lam)} for q in Q_REFINEMENT]
        rho_off = 1.1*A
        offshell = offshell_angular_hessian(rho_off, r, Z, lam)
        nu, k = .13, .2
        transform = np.diag([1., A])
        cart_kernel = Z*FINITE["WARD"]["euclidean_kernel"](nu, k, mu, r, Z, lam, A)
        polar_kernel = polar_quadratic_kernel(nu, k, mu, r, Z, lam)
        schur = phase_schur(nu, k, mu, r, Z, lam)
        analytic_schur = Z*x*(nu*nu+k*k+4*mu*mu*nu*nu/(nu*nu+k*k+2*r))
        c_sq = r/(r+2*mu*mu)
        low_mode = FINITE["WARD"]["energies"](.0001, mu, r)[0]
        source_stiffness = zero["current_stiffness_order_one_loop"]
        complete_kernel, complete_logdet, source_value = source_completed_gaussian(nu, k, rho_off, mu, r, Z, lam)
        cart_off = Z*FINITE["WARD"]["euclidean_kernel"](nu, k, mu, r, Z, lam, rho_off)
        off_transform = np.diag([1., rho_off])
        cart_logdet = .5*np.linalg.slogdet(cart_off)[1]
        g = lam/Z
        original_Omega_x = zero["reference"]["Omega_G_x"]
        naive_Omega_x = 3*g*zero["reference"]["thermal_sigma_resolvent"]/2
        missing_Omega_x = g*zero["reference"]["thermal_phase_resolvent"]/2
        examples.append({"T": t, "mu": mu, "r": r, "Z": Z, "lambda": lam,
                         "Phi_fixed": anchor["Phi_fixed"], "tree_stiffness": Z*x,
                         "formal_matched_current_stiffness": source_stiffness,
                         "tree_IR_coefficient": coefficient,
                         "previous_full_loop_IR_coefficient": anchor["radial_IR_coefficient"],
                         "susceptibility_refinement": q_records,
                         "matched_current_conditional_template": static_response(.0025, t, mu, r, Z, lam, source_stiffness),
                         "matched_template_is_not_a_new_loop_resummation": True,
                         "radial_amplitude_stationarity_or_UV_measure_not_closed": True,
                         "offshell_coordinate_trap": offshell,
                         "action_coordinate_check": action_coordinate_check(rho_off, mu, r, Z, lam),
                         "source_completed_Gaussian": {"classical_Cartesian_source": source_value,
                                                       "kernel_pullback_residual": float(np.max(np.abs(complete_kernel-off_transform.T@cart_off@off_transform))),
                                                       "measure_corrected_logdet_residual": abs(complete_logdet-cart_logdet),
                                                       "original_thermal_Omega_x": original_Omega_x,
                                                       "naive_source_free_polar_Omega_x": naive_Omega_x,
                                                       "missing_source_derivative_phase_term": missing_Omega_x,
                                                       "thermal_derivative_reconstruction_residual": abs(original_Omega_x-naive_Omega_x-missing_Omega_x)},
                         "tree_polar_kernel_pullback_residual": float(np.max(np.abs(polar_kernel-transform.T@cart_kernel@transform))),
                         "tree_Schur_residual": abs(schur-analytic_schur),
                         "tree_low_mode_speed_squared": c_sq,
                         "exact_tree_spectrum_low_k_speed_squared": (low_mode/.0001)**2,
                         "static_spatial_source_current": "j_i=rho_s*(partial_i theta-a_i); div(j)=0 at J=0; div(j)=rho*(J_l sin(theta)-J_t cos(theta)) with Cartesian sources"})
    source = gaussian_source_check()
    measure = [measure_integral(1.4, j) for j in (0., .3, 1.)]
    checks = {
        "full_source_action_coordinate_identity": all(e["action_coordinate_check"]["full_source_action_residual"] < ALGEBRA_TOLERANCE for e in examples),
        "coordinate_Jacobian_and_source_torque": all(e["action_coordinate_check"]["Jacobian_determinant_residual"] < ALGEBRA_TOLERANCE and e["action_coordinate_check"]["source_torque_difference_residual"] < ALGEBRA_TOLERANCE for e in examples),
        "source_completed_offshell_Gaussian_measure_identity": all(e["source_completed_Gaussian"]["kernel_pullback_residual"] < ALGEBRA_TOLERANCE and e["source_completed_Gaussian"]["measure_corrected_logdet_residual"] < ALGEBRA_TOLERANCE for e in examples),
        "original_thermal_stationarity_blocker_preserved": all(e["source_completed_Gaussian"]["thermal_derivative_reconstruction_residual"] < ALGEBRA_TOLERANCE and e["source_completed_Gaussian"]["original_thermal_Omega_x"] > 0 and e["source_completed_Gaussian"]["missing_source_derivative_phase_term"] > 0 for e in examples),
        "tree_polar_action_kernel_pullback": all(e["tree_polar_kernel_pullback_residual"] < ALGEBRA_TOLERANCE for e in examples),
        "tree_phase_Schur_and_spectrum": all(e["tree_Schur_residual"] < ALGEBRA_TOLERANCE and abs(e["tree_low_mode_speed_squared"]-e["exact_tree_spectrum_low_k_speed_squared"]) < 1e-7 for e in examples),
        "same_radial_one_loop_IR_coefficient": all(abs(e["tree_IR_coefficient"]-e["previous_full_loop_IR_coefficient"]) < ALGEBRA_TOLERANCE for e in examples),
        "positive_static_composite_susceptibility_and_inverse": all(row["cartesian_longitudinal_susceptibility"] > 0 and row["normalized_longitudinal_inverse"] > 0 for e in examples for row in e["susceptibility_refinement"]),
        "IR_inverse_tends_linearly_to_zero": all(abs(e["susceptibility_refinement"][-1]["normalized_longitudinal_inverse"]/(e["susceptibility_refinement"][-1]["q"]*e["susceptibility_refinement"][-1]["leading_inverse_per_q"])-1) < .05 for e in examples),
        "offshell_polar_zero_is_not_stationarity": all(abs(e["offshell_coordinate_trap"]["radial_tadpole"]) > .001 and abs(e["offshell_coordinate_trap"]["polar_angular_hessian"]) < ALGEBRA_TOLERANCE for e in examples),
        "independent_quadratic_source_generating_function": source["relative_disagreement"] < SOURCE_DIFFERENCE_TOLERANCE,
        "finite_dimensional_measure_Jacobian": all(v["relative_disagreement"] < ALGEBRA_TOLERANCE for v in measure),
        "omitting_measure_changes_the_integral": all(abs(v["polar_without_jacobian"]/v["cartesian_integral"]-1) > .1 for v in measure),
    }
    paths = (FINITE_ARTIFACT, FINITE_SCRIPT, WARD_ARTIFACT, Path(__file__).relative_to(ROOT).as_posix())
    protected = (PREFIX+"Result/artifacts/t13_conditional_twofluid_operator.json",
                 "docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json",
                 "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json")
    record = {
        "major_result_id": "T13_POLAR_STATIC_IR_OBSERVABLE_MATCH", "topic": "0.13",
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
        "verification_status": "PASS_CONDITIONAL_POLAR_STATIC_IR_OBSERVABLE" if all(checks.values()) else "FAIL_POLAR_STATIC_IR_OBSERVABLE_CHECK",
        "what_is_closed": ["same_field_polar_action_and_source_map", "measure_Jacobian_and_offshell_hessian_chain_rule", "source_completed_offshell_Gaussian_measure_equivalence", "static_Cartesian_longitudinal_Goldstone_composite_IR_coefficient", "conditional_positive_static_susceptibility_without_bare_inverse_instability"],
        "equation_or_mapping": "phi_l=A+h-A*theta^2/2; chi_l=1/[Z(q^2+2r)]+x*T/(16*rho_s^2*q); Gamma_l/Z=1/(Z*chi_l); rho_s_tree=Z*x",
        "units": {"rho_h_A_q_T_mu": "E", "theta": "dimensionless", "x_r_stiffness_inverse": "E^2", "chi": "E^-2", "source_J": "E^3", "phase_temporal_coefficient": "E^2", "Cartesian_polar_Jacobian": "E", "Gaussian_logs": "dimensionless H/E_ref metric and rho/E_ref; E_ref=1 is a natural-unit convention, not SI calibration"},
        "derivation_class": "SAME_ACTION_COORDINATE_IDENTITY_AND_LEADING_STATIC_GOLDSTONE_OBSERVABLE_MATCH",
        "observable": "Cartesian_longitudinal_source_susceptibility_distinct_from_radial_modulus_or_temperature",
        "data_role": "DERIVED_NATURAL_UNIT_NO_MEASURED_ROWS",
        "method_reference": {"url": "https://arxiv.org/html/1011.3324v2", "locator": "II.2 equations 30-39", "role": "standard_amplitude_direction_method_adapted_to_declared_Z_T_normalization_not_material_validation"},
        "assumptions": ["three_spatial_dimensions", "ordered_long_wavelength_phase_with_positive_stiffness", "fixed_Phi", "tree_parameter_matching_for_one_loop_IR_coefficient", "Gaussian_leading_phase_correlations", "q_much_less_than_sqrt_2r", "T_positive_for_thermal_IR_asymptote"],
        "Q_refinement": Q_REFINEMENT, "checks": checks, "examples": examples,
        "Gaussian_source_check": source, "finite_dimensional_measure_checks": measure,
        "evidence_artifacts": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths],
        "protected_evidence_hashes": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in protected],
        "open_blockers": ["renormalized_order_parameter_and_Phi_stationarity_with_UV_measure_matching", "finite_frequency_composite_current_and_real_axis_response", "controlled_IR_matching_remainder", "physical_material_normal_component_and_independent_measurements"],
        "controlling_blocker": "microscopic_polar_background_and_dynamical_observable_matching_not_closed",
        "dependency_unlocked": ["same_action_static_IR_completion_design_only"],
        "static_IR_observable_match_derived": True,
        "source_completed_Gaussian_coordinate_measure_matched": True,
        "microscopic_IR_resummation_derived": False, "continuum_measure_counterterms_matched": False,
        "vacuum_renormalization_matched": False,
        "joint_Phi_stationarity_derived": False, "renormalized_order_parameter_matched": False,
        "real_axis_response_derived": False, "controlled_truncation_error_established": False,
        "physical_Kubo_emitted": False, "g1_physical_unlock": False, "g2_science_unlock": False,
        "full_core_unlock": False, "core_composition_gate_overwritten": False,
        "claim_promotion": False, "parameter_fitting": False, "xie_2026_accessed": False,
        "phase_mass_added": False, "IR_filter": False, "clipping": False,
        "arbitrary_Pade_prescription": False, "C_relabelled_as_charge_or_mass": False,
        "R_gen_added_as_state": False,
        "claim_boundary": "Conditional leading static composite susceptibility in the existing O2 coordinates, not a microscopic finite-T resummation, exact background, temperature response, real-axis transport, independent material prediction or global closure. A vanishing offshell polar phase Hessian does not establish stationarity."
    }
    record["report"] = {
        "MAJOR_RESULT_CLOSURE": record["major_result_id"]+": "+record["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": record["what_is_closed"], "WHAT_REMAINS_OPEN": record["open_blockers"],
        "DEPENDENCY_UNLOCKED": record["dependency_unlocked"], "STATUS": record["verification_status"],
        "WHAT_CHANGED": "Derived the same-field polar map, Jacobian and Cartesian static composite susceptibility; preserved the nonstationary-background blocker.",
        "EQUATION_OR_MAPPING": record["equation_or_mapping"],
        "VERIFICATION": "Independent Gaussian source/logdet vs Wick calculation, measure integral, prior finite-q IR coefficient, tree kernel/Schur and spectrum.",
        "CONTROLLING_BLOCKER": record["controlling_blocker"],
        "NEXT_ACTION": "Match renormalized order parameter and continuum measure/current prescription, then the finite-frequency observable before physical admission.",
        "CLAIM_BOUNDARY": record["claim_boundary"],
    }
    return record


if __name__ == "__main__":
    record = audit()
    OUTPUT.write_bytes((json.dumps(record, indent=2, ensure_ascii=True, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": record["verification_status"], "checks": record["checks"],
                      "source": record["Gaussian_source_check"], "examples": record["examples"]}, indent=2))
