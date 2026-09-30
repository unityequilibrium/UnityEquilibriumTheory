"""A scoped two-fluid EFT witness: rest EOS does not fix sound stiffness.

This is a standard hydrodynamic EFT comparator, not a completion of UET.
The invariant construction and quadratic mode coefficients follow Nicolis,
arXiv:1108.2513, equations (14), (17)-(22), (24), and (32)-(38).
"""

from __future__ import annotations

import hashlib
import json
from math import isclose, sqrt
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
OUTPUT = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "t13_funding_rest_eos_dynamic_degeneracy.json"
)
SOURCE_PATHS = (
    "docs/core/02_equations/o2/uet_o2_finite_temperature_two_fluid_response.py",
    "docs/core/02_equations/o2/uet_o2_formal_transverse_response.py",
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "t13_he4_frozen_branch_compatibility.json",
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "t13_he4_condensed_state_identifiability.json",
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "t13_funding_condensed_scheme_selection_2026-09-28.json",
)
ZETA_VALUES = (0.1, 0.2)


def rest_state(b: float, y: float, zeta: float) -> dict[str, float]:
    """Evaluate F_zeta at X=-y^2 and the conserved equilibrium variables."""

    if b <= 0.0 or y <= 0.0 or zeta <= 0.0:
        raise ValueError("the witness requires b,y,zeta > 0")
    x = -(y * y)
    f = -0.75 * b ** (4.0 / 3.0) + y * y - 0.5 * zeta * (x + y * y)
    f_b = -(b ** (1.0 / 3.0))
    f_y = (2.0 - zeta) * y
    f_x = -0.5 * zeta
    return {
        "F": f,
        "pressure": f - f_b * b,
        "charge_density": f_y - 2.0 * f_x * y,
        "entropy_density": b,
        "temperature": -f_b,
        "energy_density": f_y * y - f - 2.0 * f_x * y * y,
        "relative_flow_curvature_minus_2_F_X": -2.0 * f_x,
    }


def longitudinal_state(b: float, y: float, zeta: float) -> dict[str, object]:
    """Solve the quadratic-action secular determinant for c^2=omega^2/k^2."""

    if b <= 0.0 or y <= 0.0 or zeta <= 0.0:
        raise ValueError("the witness requires b,y,zeta > 0")
    f_b = -(b ** (1.0 / 3.0))
    f_bb = -(b ** (-2.0 / 3.0)) / 3.0
    f_y = (2.0 - zeta) * y
    f_yy = 2.0 - zeta
    f_x = -0.5 * zeta
    k_n = f_y * y - f_b * b
    g_n = -f_bb * b * b
    k_s = (f_yy - 2.0 * f_x) * y * y
    g_s = -2.0 * f_x * y * y
    mixing = -f_y * y
    a = k_n * k_s
    coefficient = k_n * g_s + g_n * k_s + mixing * mixing
    constant = g_n * g_s
    discriminant = coefficient * coefficient - 4.0 * a * constant
    if discriminant < 0.0 or a <= 0.0:
        raise ValueError("no real positive quadratic-action roots")
    low = (coefficient - sqrt(discriminant)) / (2.0 * a)
    high = (coefficient + sqrt(discriminant)) / (2.0 * a)
    return {
        "K_N": k_n,
        "G_N": g_n,
        "K_S": k_s,
        "G_S": g_s,
        "M": mixing,
        "speed_sq_low": low,
        "speed_sq_high": high,
        "positive_quadratic_energy": min(k_n, g_n, k_s, g_s) > 0.0,
        "linear_longitudinal_subluminal": 0.0 < low < high < 1.0,
        "secular_residual_low": abs(a * low * low - coefficient * low + constant),
        "secular_residual_high": abs(a * high * high - coefficient * high + constant),
    }


def conditional_core_tree_mapping() -> dict[str, object]:
    """Compare tree phase-gradient coefficients without a material transfer."""

    artifact_dir = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts"
    frozen = json.loads(
        (artifact_dir / "t13_he4_frozen_branch_compatibility.json").read_text(
            encoding="utf-8"
        )
    )
    condensed = json.loads(
        (artifact_dir / "t13_he4_condensed_state_identifiability.json").read_text(
            encoding="utf-8"
        )
    )
    fixed = condensed["fixed_inputs"]
    z = float(fixed["tree_kinetic"])
    lam = float(fixed["tree_quartic"])
    mass_sq = float(fixed["tree_mass_sq_at_fixed_phi"])
    if z <= 0.0 or lam <= 0.0:
        raise ValueError("tree kinetic and quartic coefficients must be positive")
    frozen_q = float(frozen["frozen_natural_state"]["condensate_control"])
    frozen_stiffness = z * max(frozen_q, 0.0) / lam
    candidates = []
    for witness in condensed["witnesses"]:
        mu = float(witness["mu_natural"])
        q = z * mu * mu - mass_sq
        stiffness = z * max(q, 0.0) / lam
        amplitude_sq = float(witness["tree_condensate_amplitude"]) ** 2
        if not isclose(stiffness, z * amplitude_sq, abs_tol=1e-12):
            raise AssertionError("candidate tree stiffness and amplitude disagree")
        candidates.append(
            {
                "mu_natural": mu,
                "q": q,
                "f_s_tree": stiffness,
                "physical_HeII_state_admitted": bool(
                    witness["physical_HeII_state_admitted"]
                ),
            }
        )
    return {
        "conditional_equation": (
            "-2*F_X=f_s_tree=Z*q/lambda only if the EFT and UET phase "
            "normalizations, stationary branch and natural units are matched"
        ),
        "frozen_q": frozen_q,
        "frozen_f_s_tree": frozen_stiffness,
        "candidate_tree_states": candidates,
        "finite_T_physical_correspondence_admitted": False,
        "SI_or_HeII_material_map_admitted": False,
    }


def audit() -> dict[str, object]:
    b = y = 1.0
    examples = []
    for zeta in ZETA_VALUES:
        examples.append(
            {
                "zeta": zeta,
                "rest_state": rest_state(b, y, zeta),
                "longitudinal_state": longitudinal_state(b, y, zeta),
            }
        )
    static_keys = (
        "F",
        "pressure",
        "charge_density",
        "entropy_density",
        "temperature",
        "energy_density",
    )
    same_static = all(
        isclose(
            examples[0]["rest_state"][key],
            examples[1]["rest_state"][key],
            rel_tol=0.0,
            abs_tol=1e-12,
        )
        for key in static_keys
    )
    different_speeds = not isclose(
        examples[0]["longitudinal_state"]["speed_sq_low"],
        examples[1]["longitudinal_state"]["speed_sq_low"],
        rel_tol=0.0,
        abs_tol=1e-6,
    )
    positive_energies = all(
        item["longitudinal_state"]["positive_quadratic_energy"]
        for item in examples
    )
    subluminal = all(
        item["longitudinal_state"]["linear_longitudinal_subluminal"]
        for item in examples
    )
    root_residuals = all(
        max(
            item["longitudinal_state"]["secular_residual_low"],
            item["longitudinal_state"]["secular_residual_high"],
        )
        < 1e-12
        for item in examples
    )
    checks = {
        "same_rest_EOS_and_charge_entropy_energy": same_static,
        "different_low_mode_speeds": different_speeds,
        "positive_quadratic_energy": positive_energies,
        "linear_longitudinal_subluminal": subluminal,
        "secular_roots_close": root_residuals,
    }
    if not all(checks.values()):
        raise AssertionError(f"two-fluid EFT witness failed: {checks}")
    return {
        "major_result_id": "T13_REST_EOS_DYNAMICAL_RESPONSE_NONIDENTIFIABILITY_BOUNDARY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "verification_status": "PASS_SCOPED_STANDARD_EFT_CONSTRUCTIVE_WITNESS",
        "what_is_closed": (
            "Within the stated nondissipative finite-T two-fluid EFT class, two "
            "positive-energy subluminal longitudinal linearizations have "
            "identical rest thermodynamics for every b,y but different low-mode speeds"
        ),
        "equation_or_mapping": (
            "F_zeta(b,X,y)=-3*b^(4/3)/4+y^2-zeta*(X+y^2)/2; "
            "X=-y^2+xi^2; det[[K_N*c^2-G_N,M*c],[M*c,K_S*c^2-G_S]]=0"
        ),
        "units": "rescaled dimensionless EFT comparator at b=y=1; dimensional coefficients and He-II SI map not supplied",
        "derivation_class": "CONSTRUCTIVE_STANDARD_EFT_CLASS_COUNTEREXAMPLE_NOT_UET_ACTION",
        "observable": "linear longitudinal low-mode characteristic speed, not a measured He-II response",
        "data_role": "SYNTHETIC_ANALYTIC_CONTROL_NO_EMPIRICAL_FIT",
        "evidence_artifacts": [
            {
                "path": path,
                "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
            }
            for path in SOURCE_PATHS
        ],
        "primary_source": "https://arxiv.org/html/1108.2513",
        "checks": checks,
        "examples": examples,
        "conditional_core_tree_mapping": conditional_core_tree_mapping(),
        "open_blockers": [
            "formal_tree_stiffness_to_finite_T_relative_flow_current_not_derived",
            "Core_formal_stiffness_not_independently_mapped_to_HeII",
            "driven_source_detector_and_dissipative_response_not_derived",
            "clean_Core_baseline_and_independent_source_not_admitted",
        ],
        "dependency_unlocked": ["independent_relative_flow_stiffness_measurement_design_only"],
        "g1_physical_unlock": False,
        "g2_science_unlock": False,
        "full_core_unlock": False,
        "xie_2026_accessed": False,
        "claim_boundary": (
            "Rest-EOS-only counterexample in an external EFT class; not two admitted "
            "UET completions, He-II second-sound prediction, proof that Core static "
            "stiffness is insufficient, or Full Topic 13 closure"
        ),
    }


def main() -> None:
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(audit(), indent=2, ensure_ascii=True) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
