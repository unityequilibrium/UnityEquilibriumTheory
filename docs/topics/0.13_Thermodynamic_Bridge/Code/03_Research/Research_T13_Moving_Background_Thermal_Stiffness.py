"""Thermal phase-gradient curvature on the declared tree-relaxed background.

This extends the existing tree-condensate thermal determinant to a uniform
spatial phase gradient. It is not a jointly stationary interacting finite-T
completion, a retarded response or a physical helium correspondence.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from math import exp, expm1, pi, sqrt
from pathlib import Path
import runpy
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_finite_density_eos import condensate_control, effective_mass_sq
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    condensed_quasiparticle_energies, quasiparticle_pressure,
)
from docs.core.uet_o2_gaussian_thermal_stationarity_no_go import (
    mode_omega_sq_x_derivatives, thermal_gaussian_stationarity_no_go,
)

OPERATOR_PATH = "docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Conditional_TwoFluid_Operator.py"
OPERATOR = runpy.run_path(str(ROOT / OPERATOR_PATH))
OUTPUT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_moving_background_thermal_stiffness.json"
SOURCE_PATHS = (*OPERATOR["INPUT_PATHS"], OPERATOR_PATH,
                "docs/core/02_equations/o2/uet_o2_gaussian_thermal_stationarity_no_go.py",
                "docs/core/02_equations/o2/uet_o2_gaussian_offshell_background.py",
                "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_conditional_twofluid_operator.json")
RADIAL_ORDERS = (128, 192, 256)
FLOW_STEPS = (2e-3, 1e-3, 5e-4)
NUMERIC_TOLERANCE = 1e-3


def moving_energies(k: float, cosine: float, xi: float, mu: float, r: float) -> tuple[float, float]:
    """Positive-frequency roots for psi=mu*t+xi*z, q_xi/Z=r-xi^2."""
    if k <= 0 or r <= xi**2 or abs(cosine) > 1:
        raise ValueError("positive momentum and a condensed moving domain required")
    ksq, rz = k*k, r - xi*xi
    roots = np.roots([1., 0., -(2*ksq + 2*rz + 4*mu*mu),
                      -8*mu*xi*k*cosine,
                      ksq*ksq + 2*rz*ksq - 4*xi*xi*ksq*cosine*cosine])
    if np.max(np.abs(roots.imag)) > 1e-9:
        raise ValueError("complex moving-background frequencies; no stable thermal pressure")
    positive = sorted(float(v.real) for v in roots if v.real > 0.)
    if len(positive) != 2:
        raise ValueError("moving-background positive-energy domain violated")
    return positive[0], positive[1]


def root_derivatives(k: float, energy: float, mu: float, r: float,
                     relax_amplitude: bool = True) -> tuple[float, float]:
    """Return coefficient E'=d1*cos(theta) and isotropic mean E'' at xi=0."""
    a = energy*energy - k*k
    dw = 4*energy*(a - r - 2*mu*mu)
    d1 = 8*mu*energy*k / dw
    dww = 12*energy*energy - 4*k*k - 4*r - 8*mu*mu
    dxi2 = 4*a if relax_amplitude else -4*(a-r)
    d2_mean = -(dxi2 - 8*k*k/3 - 16*mu*k*d1/3 + dww*d1*d1/3) / dw
    return d1, d2_mean


def root_directional_second(k: float, energy: float, cosine: float, mu: float, r: float) -> float:
    a = energy*energy - k*k
    dw = 4*energy*(a - r - 2*mu*mu)
    first = 8*mu*energy*k*cosine / dw
    dww = 12*energy*energy - 4*k*k - 4*r - 8*mu*mu
    return -(4*a - 8*k*k*cosine*cosine - 16*mu*k*cosine*first + dww*first*first) / dw


def radial_grid(t: float, mu: float, phi: float, config, cutoff_factor=None):
    factor = config.cutoff_factor if cutoff_factor is None else cutoff_factor
    z = config.eos.matter.matter_kinetic
    mass = sqrt(effective_mass_sq(phi, config.eos) / z)
    r = condensate_control(mu, phi, config.eos) / z
    cutoff = max(factor*t, factor*mass, factor*abs(mu), factor*sqrt(r), 1.)
    nodes, weights = np.polynomial.legendre.leggauss(config.quadrature_order)
    return .5*cutoff*(nodes+1), .5*cutoff*weights, cutoff


def thermal_stiffness(t: float, mu: float, phi: float, config, cutoff_factor=None) -> dict:
    q = condensate_control(mu, phi, config.eos)
    if t <= 0 or q <= 0:
        raise ValueError("positive T and a condensed tree background required")
    z = config.eos.matter.matter_kinetic
    tree = z*q/config.eos.matter.matter_quartic
    r = q/z
    grid, weights, cutoff = radial_grid(t, mu, phi, config, cutoff_factor)
    curvature, occupation, fixed_curvature, amplitude_tadpole = [], [], [], []
    proof = thermal_gaussian_stationarity_no_go(mu, phi, config.eos)
    for k in grid:
        energies = condensed_quasiparticle_energies(float(k), mu, phi, config)
        curve, occ, fixed_curve, tadpole = 0., 0., 0., 0.
        low, high, dlow_dx, dhigh_dx, _ = mode_omega_sq_x_derivatives(
            float(k), proof.x_boundary, mu, proof
        )
        energy_x = (dhigh_dx/(2*energies[0]), dlow_dx/(2*energies[1]))
        for energy, ex in zip(energies, energy_x):
            x = energy/t
            f = exp(-x) if x > 50 else 1/expm1(x)
            d1, d2 = root_derivatives(float(k), energy, mu, r)
            curve += f*d2
            _, fixed_d2 = root_derivatives(float(k), energy, mu, r, False)
            fixed_curve += f*fixed_d2
            tadpole += f*ex
            occ -= f*(1+f)*d1*d1/(3*t)
        curvature.append(curve)
        occupation.append(occ)
        fixed_curvature.append(fixed_curve)
        amplitude_tadpole.append(tadpole)
    measure = weights*grid**2/(2*pi*pi)
    curved = float(np.sum(measure*np.array(curvature)))
    doppler = float(np.sum(measure*np.array(occupation)))
    fixed = float(np.sum(measure*np.array(fixed_curvature)))
    omega_x = float(np.sum(measure*np.array(amplitude_tadpole)))
    path_term = -2*z*omega_x/config.eos.matter.matter_quartic
    delta_x = -2*omega_x/config.eos.matter.matter_quartic
    return {"f_s_tree": tree, "thermal_spectral_curvature": curved,
            "thermal_occupation_term": doppler, "thermal_correction": curved+doppler,
            "f_s_tree_relaxed_thermal": tree+curved+doppler,
            "thermal_held_amplitude_spectral_curvature": fixed,
            "f_s_held_amplitude_thermal": tree+fixed+doppler,
            "Omega_x_at_tree_amplitude": omega_x,
            "amplitude_path_term": path_term,
            "linearized_tadpole_delta_x_not_stationary_solution": delta_x,
            "fractional_linearized_amplitude_shift": delta_x/proof.x_boundary,
            "unresummed_phase_mass_sq_after_linearized_shift": config.eos.matter.matter_quartic*delta_x/z,
            "required_Ward_loop_inverse_at_zero_not_computed": 2*omega_x/z,
            "path_chain_rule_absolute_residual": abs(curved-fixed-path_term),
            "radial_order": config.quadrature_order, "cutoff": cutoff}


def moving_pressure(t: float, mu: float, phi: float, xi: float, config,
                    angular_order: int = 8) -> float:
    """Thermal positive-root determinant plus tree pressure at fixed cutoff."""
    z = config.eos.matter.matter_kinetic
    q = condensate_control(mu, phi, config.eos)
    r = q/z
    if r <= xi*xi:
        raise ValueError("moving background must stay condensed")
    momenta, weights, _ = radial_grid(t, mu, phi, config)
    angles, angular_weights = np.polynomial.legendre.leggauss(angular_order)
    pressure = (q-z*xi*xi)**2/(4*config.eos.matter.matter_quartic)
    thermal = 0.
    for k, weight in zip(momenta, weights):
        integral = 0.
        for cosine, angular_weight in zip(angles, angular_weights):
            energies = moving_energies(float(k), float(cosine), xi, mu, r)
            integral += angular_weight*sum(-np.log(-np.expm1(-energy/t)) for energy in energies)
        thermal += weight*k*k*integral/(4*pi*pi)
    return float(pressure+t*thermal)


def audit() -> dict:
    old = json.loads((ROOT / SOURCE_PATHS[-1]).read_text(encoding="utf-8"))
    config = natural_bridge_config()
    examples = []
    for anchor in old["examples"]:
        t, mu, phi = anchor["T"], anchor["mu"], anchor["Phi_fixed"]
        runs = [thermal_stiffness(t, mu, phi, replace(config, quadrature_order=order))
                for order in RADIAL_ORDERS]
        cfg = replace(config, quadrature_order=RADIAL_ORDERS[-1])
        reference = runs[-1]
        direct_zero = moving_pressure(t, mu, phi, 0., cfg)
        original_zero = quasiparticle_pressure(t, mu, phi, cfg)
        direct = []
        for step in FLOW_STEPS:
            plus = moving_pressure(t, mu, phi, step, cfg)
            minus = moving_pressure(t, mu, phi, -step, cfg)
            direct.append({"flow_step": step, "f_s_direct": -(plus+minus-2*direct_zero)/step**2,
                           "pressure_even_residual": abs(plus-minus)})
        angular_twelve = moving_pressure(t, mu, phi, FLOW_STEPS[-1], cfg, 12)
        cutoff_runs = [thermal_stiffness(t, mu, phi, cfg, factor) for factor in (50., 70., 90.)]
        fs = reference["f_s_tree_relaxed_thermal"]
        jet = anchor["reference"]["pressure_jet"]
        mapped = OPERATOR["coefficients"](t, mu, jet, fs)
        updated_modes = OPERATOR["modes"](mapped)
        held_coefficients = OPERATOR["coefficients"](t, mu, jet, reference["f_s_held_amplitude_thermal"])
        held_modes = OPERATOR["modes"](held_coefficients)
        interval = anchor["causal_stiffness_interval"]
        allowed = interval["f_s_lower_exclusive"] < fs < interval["f_s_upper_exclusive"]
        relative = lambda value: abs(value-fs)/max(abs(fs), 1e-12)
        examples.append({
            "T": t, "mu": mu, "Phi_fixed": phi, "tree_relaxed_amplitude_not_joint_finite_T_stationarity": True,
            "reference": reference, "radial_runs": runs, "direct_pressure_runs": direct,
            "zero_flow_pressure_relative_residual": abs(direct_zero-original_zero)/abs(original_zero),
            "radial_last_relative_change": relative(runs[-2]["f_s_tree_relaxed_thermal"]),
            "direct_derivative_relative_disagreement": relative(direct[-1]["f_s_direct"]),
            "flow_step_last_relative_change": abs(direct[-1]["f_s_direct"]-direct[-2]["f_s_direct"])/abs(fs),
            "angular_pressure_difference": abs(angular_twelve-moving_pressure(t, mu, phi, FLOW_STEPS[-1], cfg)),
            "cutoff_runs": cutoff_runs,
            "cutoff_relative_span": (max(v["f_s_tree_relaxed_thermal"] for v in cutoff_runs)-min(v["f_s_tree_relaxed_thermal"] for v in cutoff_runs))/abs(fs),
            "old_tree_modes": anchor["reference"]["modes"],
            "thermal_curvature_coefficients": mapped, "thermal_curvature_modes": updated_modes,
            "conditional_normal_current_coefficient_not_mass_density": jet["n"]-mu*fs,
            "held_amplitude_curvature_modes": held_modes,
            "held_amplitude_mode_mixing_role": "INCONSISTENT_EOS_DERIVATIVE_PROTOCOL_SCREEN_ONLY",
            "path_current_identification_admitted": False,
            "stiffness_in_previous_causal_interval": allowed,
            "physical_HeII_state_admitted": False,
        })
    checks = {
        "zero_flow_pressure_matches_Core": all(e["zero_flow_pressure_relative_residual"] < 1e-10 for e in examples),
        "radial_refinement": all(e["radial_last_relative_change"] < NUMERIC_TOLERANCE for e in examples),
        "direct_pressure_curvature_agreement": all(e["direct_derivative_relative_disagreement"] < NUMERIC_TOLERANCE for e in examples),
        "flow_step_refinement": all(e["flow_step_last_relative_change"] < NUMERIC_TOLERANCE for e in examples),
        "angular_refinement": all(e["angular_pressure_difference"] < 1e-12 for e in examples),
        "cutoff_stability": all(e["cutoff_relative_span"] < NUMERIC_TOLERANCE for e in examples),
        "updated_linear_modes_positive_subluminal": all(e["thermal_curvature_modes"]["positive_quadratic_energy"] and e["thermal_curvature_modes"]["subluminal"] for e in examples),
        "nonstationary_amplitude_tadpole_positive": all(e["reference"]["Omega_x_at_tree_amplitude"] > 0 for e in examples),
        "amplitude_path_chain_rule": all(e["reference"]["path_chain_rule_absolute_residual"] < 1e-12 for e in examples),
    }
    paths = (*SOURCE_PATHS, Path(__file__).relative_to(ROOT).as_posix())
    evidence = [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths]
    return {
        "major_result_id": "T13_TREE_RELAXED_THERMAL_PHASE_GRADIENT_CURVATURE",
        "topic": "0.13", "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
        "verification_status": "PASS_TREE_RELAXED_THERMAL_CURVATURE" if all(checks.values()) else "FAIL_TREE_RELAXED_THERMAL_CURVATURE_SCREEN",
        "what_is_closed": ["phase_gradient_thermal_pressure_curvature_in_declared_tree_relaxed_prescription",
                           "independent_implicit_root_and_direct_pressure_derivative_check",
                           "nonzero_amplitude_tadpole_and_path_term_quantified_without_stationary_current_admission"],
        "equation_or_mapping": "f_s=-p_xixi=f_s_tree+integral[f_B*E_xixi-f_B*(1+f_B)*E_xi^2/T]",
        "units": {"xi_T_mu_E": "E", "pressure": "E^4", "stiffness": "E^2", "E_xi": "dimensionless", "E_xixi": "E^-1", "speed_sq": "natural c=1"},
        "derivation_class": "ACTION_DERIVED_TREE_RELAXED_THERMAL_GAUSSIAN_DETERMINANT",
        "observable": "static_phase_gradient_pressure_curvature_in_natural_units",
        "data_role": "DERIVED_APPROXIMATE_NO_MEASURED_ROWS",
        "primary_reference": "https://arxiv.org/abs/1212.0670",
        "numeric_tolerance": NUMERIC_TOLERANCE, "flow_steps": list(FLOW_STEPS),
        "checks": checks, "examples": examples, "evidence_artifacts": evidence,
        "open_blockers": ["joint_finite_T_condensate_amplitude_and_Phi_stationarity",
                          "Ward_consistent_interacting_retarded_source_detector_response",
                          "independent_physical_material_and_normal_component_match",
                          "clean_Core_admission_and_independent_data"],
        "controlling_blocker": "joint_finite_T_stationary_current_response_not_derived",
        "dependency_unlocked": ["static_relative_flow_current_design_in_declared_approximation_only"],
        "source_detector_response_derived": False, "physical_finite_T_stiffness_admitted": False,
        "microscopic_Ward_loop_response_computed": False,
        "weak_coupling_or_truncation_error_bound_established": False,
        "normal_component_dictionary": "n_normal_current=n-mu*f_s conditional imported EFT decomposition; not Landau mass density",
        "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False,
        "claim_promotion": False, "parameter_fitting": False, "xie_2026_accessed": False,
        "claim_boundary": "Static curvature on a tree-relaxed thermal-only background; not a jointly stationary finite-T UET completion, physical normal density/Kubo or He-II prediction. Prior failed tree-only lift remains preserved.",
    }


def main() -> None:
    result = audit()
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2, ensure_ascii=True)+"\n")
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"],
                      "examples": [{"mu": e["mu"], "curvature": e["reference"],
                                    "modes": e["thermal_curvature_modes"],
                                    "direct_rel": e["direct_derivative_relative_disagreement"],
                                    "cutoff_rel": e["cutoff_relative_span"]} for e in result["examples"]]}, indent=2))


if __name__ == "__main__":
    main()
