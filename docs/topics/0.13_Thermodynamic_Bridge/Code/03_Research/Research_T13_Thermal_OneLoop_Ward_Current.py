"""Thermal one-loop zero-momentum Ward and static-current matching.

Compute the transverse tadpole AND bubble, not a coefficient imposed to make
a Ward test pass. Keep the response field fixed and use formal loop ordering;
the shifted bare Gaussian background is not evaluated as an exact solution.
"""

from __future__ import annotations

import hashlib
import json
from math import exp, expm1, isfinite, pi, sqrt
from pathlib import Path
import sys

import numpy as np
from scipy.integrate import quad
from scipy.special import zeta

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_finite_density_eos import effective_mass_sq
from docs.core.uet_o2_gaussian_offshell_background import off_shell_mode_omega_sq

PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
CURVATURE_SCRIPT = PREFIX + "Code/03_Research/Research_T13_Moving_Background_Thermal_Stiffness.py"
CURVATURE_ARTIFACT = PREFIX + "Result/artifacts/t13_moving_background_thermal_stiffness.json"
OUTPUT = ROOT / (PREFIX + "Result/artifacts/t13_thermal_oneloop_ward_current.json")
RADIAL_ORDERS = (128, 192, 256)
CUTOFF_FACTORS = (50., 70., 90.)
MATSUBARA_TERMS = (128, 256, 512)
ALGEBRA_TOLERANCE = 1e-10
MATSUBARA_TOLERANCE = 1e-6
CONVERGENCE_TOLERANCE = 1e-3


def validate(t: float, mu: float, r: float, z: float, lam: float) -> None:
    if not all(isfinite(v) for v in (t, mu, r, z, lam)):
        raise ValueError("finite natural-unit inputs required")
    if t < 0 or mu < 0 or min(r, z, lam) <= 0:
        raise ValueError("T,mu>=0 and r,Z,lambda>0 required")


def energies(k: float, mu: float, r: float) -> tuple[float, float]:
    if not all(isfinite(v) for v in (k, mu, r)) or k <= 0 or mu < 0 or r <= 0:
        raise ValueError("finite k,r>0 and mu>=0 required")
    high_sq = k*k + r + 2*mu*mu + sqrt((r+2*mu*mu)**2+4*mu*mu*k*k)
    # Product of the roots avoids subtraction loss in the gapless mode.
    low_sq = k*k*(k*k+2*r)/high_sq
    return sqrt(low_sq), sqrt(high_sq)


def occupation(energy: float, t: float) -> float:
    if not all(isfinite(v) for v in (energy, t)) or energy <= 0 or t < 0:
        raise ValueError("finite positive energy and T>=0 required")
    if t == 0:
        return 0.
    argument = energy/t
    return exp(-argument) if argument > 50 else 1/expm1(argument)


def thermal_resolvents(k: float, t: float, mu: float, r: float) -> tuple[float, float, float]:
    """Thermal parts of G_sigma, G_pi and 1/det(K), with K divided by Z."""
    validate(t, mu, r, 1., 1.)
    low, high = energies(k, mu, r)
    gap = high*high-low*low
    jl, jh = occupation(low, t)/low, occupation(high, t)/high
    sigma = ((k*k-low*low)*jl + (high*high-k*k)*jh)/gap
    phase = ((k*k+2*r-low*low)*jl + (high*high-k*k-2*r)*jh)/gap
    determinant = (jl-jh)/gap
    return sigma, phase, determinant


def euclidean_kernel(nu: float, k: float, mu: float, r: float,
                     z: float, lam: float, amplitude: float, transverse: float = 0.) -> np.ndarray:
    validate(0., mu, r, z, lam)
    if not all(isfinite(v) for v in (nu, k, amplitude, transverse)) or k < 0:
        raise ValueError("finite frequency and fields, nonnegative momentum required")
    g = lam/z
    a, y = amplitude, transverse
    base = nu*nu+k*k-r
    cross = 2*g*a*y
    return np.array([[base+g*(3*a*a+y*y), cross-2*mu*nu],
                     [cross+2*mu*nu, base+g*(a*a+3*y*y)]])


def ward_kernel(nu: float, k: float, mu: float, r: float, z: float, lam: float) -> np.ndarray:
    """Independent matrix derivatives of (1/2) Tr log K at the tree amplitude."""
    g, amplitude = lam/z, sqrt(z*r/lam)
    propagator = np.linalg.inv(euclidean_kernel(nu, k, mu, r, z, lam, amplitude))
    first = 2*g*amplitude*np.array([[0., 1.], [1., 0.]])
    second = 2*g*np.diag([1., 3.])
    derivative_x = g*np.diag([3., 1.])
    tadpole = np.trace(propagator@second)/(2*z)
    bubble = -np.trace(propagator@first@propagator@first)/(2*z)
    ward_rhs = np.trace(propagator@derivative_x)/z
    return np.array([tadpole, bubble, ward_rhs], dtype=float)


def thermal_diagrams(t: float, mu: float, r: float, z: float, lam: float,
                     order: int = 256, cutoff_factor: float = 60.) -> dict:
    validate(t, mu, r, z, lam)
    if isinstance(order, bool) or not isinstance(order, int) or order < 32:
        raise ValueError("quadrature order must be an integer >=32")
    if not isfinite(cutoff_factor) or cutoff_factor <= 0:
        raise ValueError("positive finite cutoff factor required")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    cutoff = cutoff_factor*max(t, mu, sqrt(r))
    grid, weights = .5*cutoff*(nodes+1), .5*cutoff*weights
    integrands = np.array([thermal_resolvents(float(k), t, mu, r) for k in grid])
    sigma, phase, determinant = np.sum(weights[:, None]*grid[:, None]**2*integrands/(2*pi*pi), axis=0)
    x0 = z*r/lam
    tadpole = lam/z**2*(sigma+3*phase)
    bubble = -4*lam**2*x0/z**3*determinant
    omega_x = lam/(2*z)*(3*sigma+phase)
    delta_x = -2*omega_x/lam
    shifted_tree_inverse = lam*delta_x/z
    return {
        "x_tree": float(x0), "thermal_sigma_resolvent": float(sigma),
        "thermal_phase_resolvent": float(phase), "thermal_determinant_resolvent": float(determinant),
        "transverse_tadpole": float(tadpole), "transverse_bubble": float(bubble),
        "transverse_loop_inverse_at_zero": float(tadpole+bubble),
        "Omega_G_x": float(omega_x), "Ward_rhs_2_Omega_G_x_over_Z": float(2*omega_x/z),
        "delta_x_order_one_loop": float(delta_x),
        "fractional_amplitude_sq_shift": float(delta_x/x0),
        "shifted_tree_transverse_inverse": float(shifted_tree_inverse),
        "Ward_cancellation_absolute_residual": float(abs(shifted_tree_inverse+tadpole+bubble)),
        "radial_order": order, "cutoff": float(cutoff),
    }


def matsubara_thermal_check(k: float, t: float, mu: float, r: float, z: float,
                           lam: float, terms: int) -> dict:
    """Direct matrix sum minus a numerical T=0 frequency integral.

    Add the analytic nu^-2 and nu^-4 ultraviolet tails. These are derived
    from the matrix kernel, not from the thermal pole-residue answers.
    """
    validate(t, mu, r, z, lam)
    if t <= 0 or isinstance(terms, bool) or not isinstance(terms, int) or terms < 32:
        raise ValueError("positive T and integer Matsubara terms >=32 required")
    zero = ward_kernel(0., k, mu, r, z, lam)
    finite_sum = t*(zero+2*sum((ward_kernel(2*pi*t*n, k, mu, r, z, lam)
                              for n in range(1, terms+1)), start=np.zeros(3)))
    g = lam/z
    c2 = np.array([4*g/z, 0., 4*g/z])
    c4 = np.array([-g/z*(4*k*k+2*r+16*mu*mu),
                   -4*g*r/z, -g/z*(4*k*k+6*r+16*mu*mu)])
    tail = 2*t*(c2*zeta(2., terms+1)/(2*pi*t)**2 + c4*zeta(4., terms+1)/(2*pi*t)**4)
    vacuum = np.array([quad(lambda nu: float(ward_kernel(nu, k, mu, r, z, lam)[i]),
                            0., np.inf, epsabs=1e-12, epsrel=1e-12)[0]/pi for i in range(3)])
    direct = finite_sum+tail-vacuum
    sigma, phase, determinant = thermal_resolvents(k, t, mu, r)
    residue = np.array([lam/z**2*(sigma+3*phase), -4*lam*r/z**2*determinant,
                        lam/z**2*(3*sigma+phase)])
    return {"k": k, "terms": terms, "direct_matrix_sum_thermal": direct.tolist(),
            "pole_residue_thermal": residue.tolist(),
            "maximum_relative_disagreement": float(np.max(np.abs(direct-residue)/np.maximum(np.abs(residue), 1e-12)))}


def amplitude_hessian_integrand(k: float, t: float, mu: float, r: float,
                               z: float, lam: float) -> float:
    """Radial integrand of Omega_G,xx at the tree boundary; no IR clipping."""
    validate(t, mu, r, z, lam)
    g, x0 = lam/z, z*r/lam
    low, high = energies(k, mu, r)
    disc = 4*g*g*x0*x0+8*mu*mu*(-2*r+4*g*x0)+16*mu**4+16*mu*mu*k*k
    root = sqrt(disc)
    disc_x, disc_xx = 8*g*g*x0+32*mu*mu*g, 8*g*g
    low_x = 2*g-disc_x/(4*root)
    low_xx = -disc_xx/(4*root)+disc_x**2/(8*root**3)
    result = 0.
    for energy, y_x, y_xx in ((low, low_x, low_xx), (high, 4*g-low_x, -low_xx)):
        n = occupation(energy, t)
        e_x = y_x/(2*energy)
        e_xx = y_xx/(2*energy)-y_x*y_x/(4*energy**3)
        result += n*e_xx-(n*(1+n)/t*e_x*e_x if t > 0 else 0.)
    return k*k*result/(2*pi*pi)


def audit() -> dict:
    old = json.loads((ROOT/CURVATURE_ARTIFACT).read_text(encoding="utf-8"))
    config = natural_bridge_config()
    z, lam = config.eos.matter.matter_kinetic, config.eos.matter.matter_quartic
    examples, direct_checks = [], []
    for anchor in old["examples"]:
        t, mu, phi = anchor["T"], anchor["mu"], anchor["Phi_fixed"]
        r = mu*mu-effective_mass_sq(phi, config.eos)/z
        runs = [thermal_diagrams(t, mu, r, z, lam, order) for order in RADIAL_ORDERS]
        reference = runs[-1]
        cutoff_runs = [thermal_diagrams(t, mu, r, z, lam, cutoff_factor=f) for f in CUTOFF_FACTORS]
        fs_held = anchor["reference"]["f_s_held_amplitude_thermal"]
        current_matched = fs_held+z*reference["delta_x_order_one_loop"]
        shifted_x = reference["x_tree"]+reference["delta_x_order_one_loop"]
        bare_modes = off_shell_mode_omega_sq(0., sqrt(shifted_x), mu, phi, config.eos)
        ir_constant = -lam**2/z**2*t/(4*pi*pi)
        ir = [{"k": k, "k_sq_times_amplitude_hessian_integrand": k*k*amplitude_hessian_integrand(k, t, mu, r, z, lam)}
              for k in (1e-3, 5e-4, 2.5e-4)]
        examples.append({
            "T": t, "mu": mu, "Phi_fixed": phi, "Z": z, "lambda": lam, "r": r,
            "reference": reference, "radial_runs": runs, "cutoff_runs": cutoff_runs,
            "current_stiffness_order_one_loop": current_matched,
            "previous_path_stiffness": anchor["reference"]["f_s_tree_relaxed_thermal"],
            "static_current_order_matching_absolute_residual": abs(current_matched-anchor["reference"]["f_s_tree_relaxed_thermal"]),
            "bare_shifted_low_mode_sq_at_k_zero": bare_modes[0],
            "bare_shifted_Gaussian_not_evaluated_as_equilibrium": True,
            "infrared_amplitude_hessian_asymptotic_constant": ir_constant,
            "infrared_witnesses": ir,
        })
        for k in (.2, .8, 2.):
            direct_checks.append({"mu": mu, "runs": [matsubara_thermal_check(k, t, mu, r, z, lam, n)
                                                      for n in MATSUBARA_TERMS]})
    checks = {
        "thermal_tadpole_plus_bubble_Ward_identity": all(e["reference"]["Ward_cancellation_absolute_residual"] < ALGEBRA_TOLERANCE for e in examples),
        "independent_Matsubara_matrix_sum": all(e["runs"][-1]["maximum_relative_disagreement"] < MATSUBARA_TOLERANCE for e in direct_checks),
        "Matsubara_refinement": all(e["runs"][-1]["maximum_relative_disagreement"] <= e["runs"][0]["maximum_relative_disagreement"]+1e-10 for e in direct_checks),
        "radial_refinement": all(abs(e["radial_runs"][-2]["Omega_G_x"]-e["reference"]["Omega_G_x"])/abs(e["reference"]["Omega_G_x"]) < CONVERGENCE_TOLERANCE for e in examples),
        "cutoff_refinement": all((max(v["Omega_G_x"] for v in e["cutoff_runs"])-min(v["Omega_G_x"] for v in e["cutoff_runs"]))/abs(e["reference"]["Omega_G_x"]) < CONVERGENCE_TOLERANCE for e in examples),
        "previous_tadpole_independently_reproduced": all(abs(e["reference"]["Omega_G_x"]-a["reference"]["Omega_x_at_tree_amplitude"]) < ALGEBRA_TOLERANCE for e, a in zip(examples, old["examples"])),
        "static_current_loop_order_matching": all(e["static_current_order_matching_absolute_residual"] < ALGEBRA_TOLERANCE for e in examples),
        "bare_shift_instability_not_hidden": all(e["bare_shifted_low_mode_sq_at_k_zero"] < 0 for e in examples),
        "infrared_Hessian_boundary": all(abs(e["infrared_witnesses"][-1]["k_sq_times_amplitude_hessian_integrand"]/e["infrared_amplitude_hessian_asymptotic_constant"]-1) < CONVERGENCE_TOLERANCE for e in examples),
    }
    paths = (CURVATURE_ARTIFACT, CURVATURE_SCRIPT,
             "docs/core/02_equations/o2/uet_o2_gaussian_offshell_background.py",
             "docs/core/02_equations/o2/uet_o2_gaussian_thermal_stationarity_no_go.py",
             "docs/core/02_equations/o2/uet_o2_finite_density_eos.py",
             "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
             Path(__file__).relative_to(ROOT).as_posix())
    protected_paths = (
        PREFIX + "Result/artifacts/t13_conditional_twofluid_operator.json",
        "docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json",
        "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json",
    )
    return {
        "major_result_id": "T13_THERMAL_ONE_LOOP_WARD_AND_STATIC_CURRENT_MATCH",
        "topic": "0.13", "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
        "verification_status": "PASS_THERMAL_ONE_LOOP_WARD_CURRENT" if all(checks.values()) else "FAIL_THERMAL_ONE_LOOP_WARD_CURRENT_CHECK",
        "what_is_closed": ["computed_thermal_transverse_tadpole_and_bubble_at_zero_external_momentum",
                           "one_loop_amplitude_shift_Ward_cancellation_at_fixed_Phi",
                           "one_loop_static_current_matches_tree_relaxed_pressure_curvature",
                           "nonintegrable_bare_amplitude_Hessian_IR_boundary_identified"],
        "equation_or_mapping": "Sigma_pi,T(0)=lambda/Z^2*(I_sigma+3I_pi)-4lambda^2*x0/Z^3*B=2Omega_G,x/Z; delta_x=-2Omega_G,x/lambda; f_1loop=f_held+Z*delta_x=f_path",
        "units": {"T_mu_k_nu_A": "E", "x_r_loop_inverse_stiffness": "E^2", "Omega": "E^4", "Omega_x": "E^2", "Z_lambda": "dimensionless", "Omega_xx": "dimensionless after radial integration"},
        "derivation_class": "ACTION_DERIVED_THERMAL_ONE_LOOP_1PI_DIFFERENCE_FIXED_PHI_FORMAL_ORDER",
        "observable": "zero_momentum_transverse_inverse_and_static_phase_gradient_current_coefficient",
        "data_role": "DERIVED_NATURAL_UNIT_NO_MEASURED_ROWS",
        "primary_reference": {"url": "https://arxiv.org/abs/1212.0670", "scope": "method context and low_T_weak_coupling caveat; not material admission or an error bound"},
        "tolerances": {"algebra": ALGEBRA_TOLERANCE, "Matsubara_relative": MATSUBARA_TOLERANCE, "quadrature_relative": CONVERGENCE_TOLERANCE},
        "checks": checks, "examples": examples, "Matsubara_checks": direct_checks,
        "evidence_artifacts": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths],
        "protected_evidence_hashes": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in protected_paths],
        "open_blockers": ["finite_frequency_and_momentum_retarded_Ward_response_and_IR_resummation",
                          "joint_Phi_and_amplitude_renormalized_finite_T_background",
                          "physical_material_normal_component_and_source_detector_matching",
                          "controlled_truncation_error_and_independent_comparison_inputs"],
        "controlling_blocker": "finite_momentum_retarded_Ward_current_and_IR_resummation_not_derived",
        "dependency_unlocked": ["fixed_Phi_thermal_one_loop_current_design_only"],
        "thermal_zero_momentum_loop_computed": True, "loop_order_amplitude_shift_computed": True,
        "finite_momentum_retarded_response_derived": False, "joint_Phi_stationarity_derived": False,
        "exact_stationary_finite_T_background_derived": False, "vacuum_renormalization_matched": False,
        "controlled_truncation_error_established": False, "physical_Kubo_emitted": False,
        "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False,
        "claim_promotion": False, "parameter_fitting": False, "xie_2026_accessed": False,
        "claim_boundary": "Thermal difference of the one-loop 1PI functional at a tree condensed, fixed-Phi background. Formal order matching, not an exact stable resummed state, finite-q retarded kernel, physical transport or He-II prediction. The exact Gaussian no-go and old failing tree lift remain preserved.",
    }


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, ensure_ascii=True)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"],
                      "examples": [{"mu": e["mu"], "reference": e["reference"],
                                    "current": e["current_stiffness_order_one_loop"],
                                    "infrared_constant": e["infrared_amplitude_hessian_asymptotic_constant"]}
                                   for e in result["examples"]]}, indent=2))
