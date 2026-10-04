"""Conditional pressure-Hessian two-fluid operator, not a UET completion.

The imported nondissipative EFT is Nicolis arXiv:1108.2513, eqs. 17-24,
32-44. Core supplies a tree-background thermal pressure and tree stiffness;
their finite-temperature relative-flow matching remains an assumption.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from math import isfinite, sqrt
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_finite_density_eos import condensate_control
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import quasiparticle_pressure

OUTPUT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_conditional_twofluid_operator.json"
INPUT_PATHS = (
    "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
    "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
    "docs/core/02_equations/o2/uet_o2_finite_density_eos.py",
    "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py",
    "docs/core/02_equations/covariant/uet_covariant_matter.py",
    "docs/core/02_equations/covariant/uet_covariant_response.py",
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_condensed_state_identifiability.json",
)
ORDERS = (128, 192, 256)
STEPS = (4e-4, 2e-4, 1e-4)
REFINEMENT_TOLERANCE = 1e-3


def pressure_jet(pressure, t: float, mu: float, step: float) -> dict[str, float]:
    """Central first/Hessian derivatives at fixed Phi and prescription."""
    if min(t, step) <= 0 or step >= t:
        raise ValueError("positive temperature and a smaller positive step required")
    p = pressure(t, mu)
    ptp, ptm = pressure(t + step, mu), pressure(t - step, mu)
    pmp, pmm = pressure(t, mu + step), pressure(t, mu - step)
    mixed = (
        pressure(t + step, mu + step) - pressure(t + step, mu - step)
        - pressure(t - step, mu + step) + pressure(t - step, mu - step)
    ) / (4 * step * step)
    return {
        "p": p, "s": (ptp - ptm) / (2 * step),
        "n": (pmp - pmm) / (2 * step),
        "a_p_TT": (ptp - 2 * p + ptm) / step**2,
        "h_p_Tmu": mixed, "c_p_mumu": (pmp - 2 * p + pmm) / step**2,
    }


def coefficients(t: float, mu: float, jet: dict, stiffness: float) -> dict[str, float]:
    """Legendre transform in entropy; all five coefficients have units E^4."""
    a, h, c = jet["a_p_TT"], jet["h_p_Tmu"], jet["c_p_mumu"]
    s, n = jet["s"], jet["n"]
    if not all(isfinite(v) for v in (t, mu, a, h, c, s, n, stiffness)) or a <= 0:
        raise ValueError("finite coefficients and positive p_TT required")
    return {
        "K_N": t * s + mu * n - stiffness * mu**2,
        "G_N": s**2 / a,
        "K_S": mu**2 * (c - h**2 / a),
        "G_S": stiffness * mu**2,
        "M": mu * (s * h / a - n + stiffness * mu),
    }


def modes(coef: dict[str, float]) -> dict:
    kn, gn, ks, gs, mixing = (coef[k] for k in ("K_N", "G_N", "K_S", "G_S", "M"))
    positive = min(kn, gn, ks, gs) > 0
    a, b, d = kn * ks, kn * gs + gn * ks + mixing**2, gn * gs
    disc = b * b - 4 * a * d
    if a <= 0 or disc < 0 or b <= 0:
        return {"positive_quadratic_energy": positive, "speed_sq": None,
                "subluminal": False, "secular_relative_residual": None}
    high = (b + sqrt(disc)) / (2 * a)
    low = d / (a * high)
    residual = max(abs(a * r * r - b * r + d) / max(abs(b * r), abs(d), 1e-30)
                   for r in (low, high))
    return {"positive_quadratic_energy": positive, "speed_sq": [low, high],
            "subluminal": 0 < low < high < 1,
            "secular_relative_residual": residual}


def relative_difference(left: dict, right: dict) -> float:
    return max(abs(left[k] - right[k]) / max(abs(right[k]), 1e-12) for k in left)


def causal_stiffness_interval(t: float, mu: float, jet: dict) -> dict:
    """Necessary and sufficient strict linear-mode bounds for this closure.

    For positive K/G, both c^2 roots lie in (0,1) iff P(1)>0 and
    2*A-B>0. In x=f_s*mu^2 both inequalities are affine: x^2 cancels.
    """
    zero = coefficients(t, mu, jet, 0.)
    w, k, g, m = (zero[key] for key in ("K_N", "K_S", "G_N", "M"))
    inequalities = {
        "x_positive": [0., 1.], "K_N_positive": [w, -1.],
        "P_at_one_positive": [(w - g) * k - m*m, -k - w - 2*m + g],
        "vertex_below_one": [2*w*k - g*k - m*m, -2*k - w - 2*m],
    }
    lower, upper = 0., w
    feasible = mu != 0 and min(w, k, g) > 0
    for constant, slope in inequalities.values():
        if slope > 0:
            lower = max(lower, -constant / slope)
        elif slope < 0:
            upper = min(upper, -constant / slope)
        elif constant <= 0:
            feasible = False
    feasible = feasible and lower < upper
    return {"exists": feasible, "f_s_lower_exclusive": lower / mu**2,
            "f_s_upper_exclusive": upper / mu**2,
            "affine_inequalities_in_x": inequalities,
            "role": "analytic_admissibility_bound_not_fitted_coefficient"}


def audit() -> dict:
    config = natural_bridge_config()
    source = json.loads((ROOT / INPUT_PATHS[-1]).read_text(encoding="utf-8"))
    examples = []
    for witness in source["witnesses"]:
        t, mu, phi = (float(witness[k]) for k in
                      ("temperature_natural", "mu_natural", "phi_natural"))
        q = condensate_control(mu, phi, config.eos)
        if q <= 0:
            raise ValueError("a declared condensed witness is required")
        fs = config.eos.matter.matter_kinetic * q / config.eos.matter.matter_quartic
        runs = []
        for order in ORDERS:
            cfg = replace(config, quadrature_order=order)
            pressure = lambda temp, chem: quasiparticle_pressure(temp, chem, phi, cfg)
            for step in STEPS:
                jet = pressure_jet(pressure, t, mu, step)
                coef = coefficients(t, mu, jet, fs)
                runs.append({"order": order, "step": step, "pressure_jet": jet,
                             "coefficients": coef, "modes": modes(coef)})
        reference = runs[-1]
        dt_ref = relative_difference(runs[-2]["coefficients"], reference["coefficients"])
        quad_ref = relative_difference(runs[-4]["coefficients"], reference["coefficients"])
        # Independent first-order companion matrix checks the secular roots.
        cf = reference["coefficients"]
        companion = np.array([
            [0., 0., 1., 0.], [0., 0., 0., 1.],
            [cf["G_N"] / cf["K_N"], 0., 0., -cf["M"] / cf["K_N"]],
            [0., cf["G_S"] / cf["K_S"], -cf["M"] / cf["K_S"], 0.],
        ])
        eigenvalues = np.linalg.eigvals(companion)
        eig_sq = sorted(float(v.real**2) for v in eigenvalues if v.real > 0 and abs(v.imag) < 1e-10)
        roots = reference["modes"]["speed_sq"]
        agree = roots is not None and len(eig_sq) == 2 and bool(np.allclose(eig_sq, roots, rtol=1e-9, atol=1e-12))
        interval = causal_stiffness_interval(t, mu, reference["pressure_jet"])
        interval["tree_stiffness_within_interval"] = bool(
            interval["exists"] and interval["f_s_lower_exclusive"] < fs < interval["f_s_upper_exclusive"]
        )
        interval["root_classification_agrees"] = interval["tree_stiffness_within_interval"] == reference["modes"]["subluminal"]
        examples.append({
            "T": t, "mu": mu, "Phi_fixed": phi, "q": q, "f_s_tree": fs,
            "pressure_branch": "TREE_CONDENSATE_PLUS_THERMAL_QUASIPARTICLES",
            "physical_HeII_state_admitted": False,
            "reference": reference, "refinement_runs": runs,
            "step_last_relative_change": dt_ref, "quadrature_last_relative_change": quad_ref,
            "first_order_speed_sq": eig_sq, "independent_eigensolver_agreement": agree,
            "causal_stiffness_interval": interval,
        })
    checks = {
        "positive_quadratic_energy": all(e["reference"]["modes"]["positive_quadratic_energy"] for e in examples),
        "subluminal_longitudinal_roots": all(e["reference"]["modes"]["subluminal"] for e in examples),
        "step_refinement": all(e["step_last_relative_change"] < REFINEMENT_TOLERANCE for e in examples),
        "quadrature_refinement": all(e["quadrature_last_relative_change"] < REFINEMENT_TOLERANCE for e in examples),
        "independent_eigensolver": all(e["independent_eigensolver_agreement"] for e in examples),
        "analytic_causal_bounds_match_roots": all(e["causal_stiffness_interval"]["root_classification_agrees"] for e in examples),
    }
    evidence = [{"path": p, "sha256": hashlib.sha256((ROOT / p).read_bytes()).hexdigest()}
                for p in (*INPUT_PATHS, Path(__file__).relative_to(ROOT).as_posix())]
    return {
        "major_result_id": "T13_CONDITIONAL_PRESSURE_HESSIAN_TWOFLUID_OPERATOR",
        "topic": "0.13",
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
        "verification_status": "PASS_CONDITIONAL_IMPORTED_EFT_OPERATOR" if all(checks.values()) else "FAIL_CONDITIONAL_OPERATOR_SCREEN",
        "derivation_class": "IMPORTED_EFT_CONSTITUTIVE_CLOSURE_WITH_UNPROVEN_UET_MATCH",
        "primary_source": "https://arxiv.org/html/1108.2513",
        "equation_or_mapping": "F=F0(b,y)-f_s(b,y)*(X+y^2)/2; F0=p-T*s; b=s=p_T; y=mu",
        "units": {"T_mu": "E", "p": "E^4", "s_n": "E^3", "pressure_Hessian_f_s": "E^2", "quadratic_coefficients": "E^4", "speed_sq": "dimensionless natural c=1"},
        "state_variables": ["normal_displacement_pi_L", "phase_displacement_pi_0"],
        "excluded_variables": ["R_gen", "R_obs"],
        "observable": "conditional_longitudinal_eigenmode_speeds_not_detector_response",
        "data_role": "DERIVED_CONDITIONAL_NUMERICAL_WITNESSES_NO_MEASURED_ROWS",
        "assumptions": ["single_charge_nondissipative_relativistic_EFT", "Phi_fixed",
                        "local_entropy_Legendre_transform_p_TT_positive", "-2F_X=f_s_tree_matching_postulated",
                        "normal_comoving_fields_imported_not_derived_from_UET_action",
                        "tree_background_not_joint_finite_T_stationary_solution"],
        "refinement_tolerance": REFINEMENT_TOLERANCE,
        "domain_decision": "TREE_STIFFNESS_LIFT_REJECTED_AT_MU_1_05_ADMISSIBLE_AT_MU_1_20_CONDITIONALLY",
        "what_is_closed": ["local_pressure_Hessian_to_quadratic_operator_identity",
                           "conditional_causal_stiffness_interval",
                           "tree_stiffness_lift_not_admissible_on_all_declared_witnesses"],
        "what_remains_open": ["finite_T_UET_current_matching", "physical_HeII_state_and_source_detector_map"],
        "checks": checks, "examples": examples,
        "evidence_artifacts": evidence,
        "evidence_hashes": evidence,
        "controlling_blocker": "finite_T_relative_flow_current_and_normal_component_UET_match_not_derived",
        "open_blockers": ["joint_finite_T_condensed_stationarity_and_Ward_response",
                          "independent_HeII_material_state_map", "source_detector_and_dissipative_response",
                          "clean_Core_baseline_and_independent_response_source_admission"],
        "dependency_unlocked": ["conditional_operator_and_relative_flow_measurement_design_only"],
        "g1_physical_unlock": False, "g2_science_unlock": False,
        "full_core_unlock": False, "claim_promotion": False, "xie_2026_accessed": False,
        "parameter_fitting": False, "finite_T_stiffness_numeric_value_emitted": False,
        "claim_boundary": "Conditional imported nondissipative EFT operator; not an action-derived finite-T UET completion, physical He-II prediction, full thermodynamic closure or external validation.",
    }


def main() -> None:
    result = audit()
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"],
                      "states": [{"mu": e["mu"], "modes": e["reference"]["modes"],
                                  "dt_ref": e["step_last_relative_change"], "quad_ref": e["quadrature_last_relative_change"]}
                                 for e in result["examples"]]}, indent=2))


if __name__ == "__main__":
    main()
