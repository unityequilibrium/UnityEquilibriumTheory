"""Audit the UV boundary of the action-derived O(2) one-loop normal branch.

The thermal Bose-log and occupation integrals have exponential tails on the
declared normal branch.  The vacuum/zero-point term is deliberately absent
from the implementation; this audit records its cutoff divergence rather
than pretending that a renormalized action has been supplied.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import date
from math import factorial, isfinite, pi, sqrt
from pathlib import Path

if str(Path(__file__).resolve().parents[3]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_one_loop_normal_branch import uet_o2_one_loop_normal_state


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/uet_o2_one_loop_normal_branch.py"
COMPARATOR_REL = "docs/core/standard_o2_finite_temperature_comparator.py"
BRANCH_AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_normal_branch_audit.json"
CONVERGENCE_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_convergence_audit.json"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_uv_boundary_audit.json"

REFERENCE = {
    "temperature": 0.35,
    "chemical_potential": 0.2,
    "space_response": 0.2,
}
TAIL_RELATIVE_THRESHOLD = 1.0e-10
THERMAL_METRICS = (
    "pressure",
    "charge_density",
    "entropy_density",
    "energy_density",
    "charge_susceptibility",
    "thermal_scalar_density",
    "pressure_phi_derivative",
)


def load(rel: str) -> dict:
    value = json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def config() -> O2FiniteDensityEOSConfig:
    return O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(
            matter_kinetic=1.2,
            matter_mass_sq=0.5,
            matter_quartic=0.8,
            response_coupling=0.3,
        ),
        response=CovariantResponseConfig(epsilon_nc=0.1),
    )


def exp_tail_moment(power: int, lower: float, temperature: float, shift: float) -> float:
    """Return integral_lower^infinity p**power exp(-(p-shift)/T) dp."""

    if power < 0 or int(power) != power:
        raise ValueError("power must be a non-negative integer")
    inverse_temperature = 1.0 / temperature
    polynomial = 0.0
    for k in range(power + 1):
        coefficient = factorial(power) / factorial(power - k)
        polynomial += coefficient * lower ** (power - k) / inverse_temperature ** (k + 1)
    value = math.exp(-inverse_temperature * (lower - shift)) * polynomial
    if not isfinite(value) or value < 0.0:
        raise FloatingPointError("non-finite exponential tail moment")
    return value


def thermal_tail_bounds(
    *,
    temperature: float,
    chemical_potential: float,
    mass: float,
    lower: float,
    dm_eff_sq_dphi: float,
) -> dict[str, float]:
    """Bound thermal tails using E_k >= p and Bose-log <= exp(-x)/(1-exp(-x))."""

    abs_mu = abs(chemical_potential)
    x_lower = (lower - abs_mu) / temperature
    if x_lower <= 0.0:
        raise ValueError("tail lower bound must be above the Bose singularity")
    denominator = 1.0 - math.exp(-x_lower)
    bose_factor = 1.0 / denominator
    moments = {
        power: bose_factor * exp_tail_moment(power, lower, temperature, abs_mu)
        for power in (1, 2, 3)
    }
    measure_constant = 1.0 / (2.0 * pi**2)
    pressure = 2.0 * temperature * measure_constant * moments[2]
    charge = 2.0 * measure_constant * moments[2]
    scalar = measure_constant * moments[1]
    response = abs(dm_eff_sq_dphi) * scalar
    energy = 2.0 * measure_constant * (moments[3] + mass * moments[2])
    entropy = 2.0 * measure_constant * (
        moments[2] + (moments[3] + (mass + abs_mu) * moments[2]) / temperature
    )
    occupation_at_lower = math.exp(-x_lower) / denominator
    susceptibility = (
        2.0
        * measure_constant
        * (1.0 + occupation_at_lower)
        * moments[2]
        / temperature
    )
    result = {
        "pressure": pressure,
        "charge_density": charge,
        "entropy_density": entropy,
        "energy_density": energy,
        "charge_susceptibility": susceptibility,
        "thermal_scalar_density": scalar,
        "pressure_phi_derivative": response,
    }
    if not all(isfinite(value) and value >= 0.0 for value in result.values()):
        raise FloatingPointError("thermal tail bound is non-finite or negative")
    return result


def vacuum_lower_bounds(mass: float, cutoffs: tuple[float, ...]) -> dict[str, dict[str, float]]:
    """Record lower bounds showing quartic and quadratic cutoff growth.

    The bounds are for the unweighted scalar mode integrals.  Degeneracy and
    zero-point convention factors are intentionally not inferred here.
    """

    result: dict[str, dict[str, float]] = {}
    for cutoff in cutoffs:
        if cutoff <= mass:
            raise ValueError("vacuum diagnostic cutoff must exceed mass")
        zero_point = cutoff**4 / (8.0 * pi**2)
        response = (cutoff**2 - mass**2) / (4.0 * sqrt(2.0) * pi**2)
        result[str(cutoff)] = {
            "unweighted_zero_point_integral_lower_bound": zero_point,
            "unweighted_mass_response_integral_lower_bound": response,
            "zero_point_scaled_by_cutoff_four": zero_point / cutoff**4,
            "response_scaled_by_cutoff_two": response / cutoff**2,
        }
    return result


def main() -> int:
    eos_config = config()
    convergence = load(CONVERGENCE_REL)
    branch_audit = load(BRANCH_AUDIT_REL)
    state = uet_o2_one_loop_normal_state(
        REFERENCE["temperature"],
        REFERENCE["chemical_potential"],
        REFERENCE["space_response"],
        eos_config,
        quadrature_order=int(convergence["reference"]["quadrature_order"]),
        cutoff_factor=float(convergence["reference"]["cutoff_factor"]),
    )
    mass_sq = float(state.effective_mass_sq)
    mass = float(state.thermal_state.effective_mass)
    cutoff = float(state.thermal_state.momentum_cutoff)
    dm_eff_sq_dphi = float(state.dm_eff_sq_dphi)
    bounds = thermal_tail_bounds(
        temperature=state.temperature,
        chemical_potential=state.chemical_potential,
        mass=mass,
        lower=cutoff,
        dm_eff_sq_dphi=dm_eff_sq_dphi,
    )
    reference_values = convergence["reference"]["values"]
    reference_values = {
        **reference_values,
        "thermal_scalar_density": float(branch_audit["state"]["thermal_scalar_density"]),
        "pressure_phi_derivative": float(branch_audit["state"]["pressure_phi_derivative"]),
    }
    relative_bounds = {
        metric: bounds[metric] / max(abs(float(reference_values[metric])), 1.0e-300)
        for metric in THERMAL_METRICS
    }
    vacuum_cutoffs = (10.0 * mass, 20.0 * mass, 40.0 * mass)
    vacuum_bounds = vacuum_lower_bounds(mass, vacuum_cutoffs)
    first, last = vacuum_bounds[str(vacuum_cutoffs[0])], vacuum_bounds[str(vacuum_cutoffs[-1])]
    module_text = (ROOT / MODULE_REL).read_text(encoding="utf-8-sig")
    comparator_text = (ROOT / COMPARATOR_REL).read_text(encoding="utf-8-sig")
    checks = {
        "normal_branch_condition_passes": state.thermal_state.effective_mass**2 > eos_config.matter.matter_kinetic * state.chemical_potential**2,
        "thermal_only_convergence_audit_passes": convergence["status"] == "PASS_ACTION_DERIVED_ONE_LOOP_CONVERGENCE",
        "thermal_tail_bound_is_finite": all(isfinite(value) and value >= 0.0 for value in bounds.values()),
        "thermal_tail_is_below_declared_threshold": all(value <= TAIL_RELATIVE_THRESHOLD for value in relative_bounds.values()),
        "bose_log_exponential_bound_domain_is_positive": (cutoff - abs(state.chemical_potential)) / state.temperature > 0.0,
        "vacuum_counterterm_is_explicitly_excluded": branch_audit["state"]["vacuum_counterterm_included"] is False,
        "zero_point_term_is_not_implemented_as_renormalized": "Vacuum counterterms" in module_text and "zero-point terms" in comparator_text,
        "zero_point_lower_bound_grows_with_cutoff": last["unweighted_zero_point_integral_lower_bound"] > first["unweighted_zero_point_integral_lower_bound"],
        "mass_response_lower_bound_grows_with_cutoff": last["unweighted_mass_response_integral_lower_bound"] > first["unweighted_mass_response_integral_lower_bound"],
        "holdout_is_not_consumed": branch_audit["holdout_policy"]["xie_2026_accessed"] is False and branch_audit["holdout_policy"]["alpha_fit_used"] is False,
        "phi_is_not_relabelled_as_temperature": branch_audit["checks"]["phi_is_not_temperature"] is True,
    }
    status = "PASS_THERMAL_UV_BOUNDARY" if all(checks.values()) else "FAIL_THERMAL_UV_BOUNDARY"
    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": COMPARATOR_REL, "sha256": digest(COMPARATOR_REL)},
        {"path": BRANCH_AUDIT_REL, "sha256": digest(BRANCH_AUDIT_REL)},
        {"path": CONVERGENCE_REL, "sha256": digest(CONVERGENCE_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-one-loop-uv-boundary-v1",
        "artifact": "t13_uet_o2_one_loop_uv_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_ONE_LOOP_THERMAL_UV_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the thermal-only Bose-log and occupation tails are bounded analytically on the declared normal branch",
                "the declared cutoff baseline is sufficient for the thermal-only outputs under the separate tail threshold",
                "the vacuum/zero-point term is explicitly classified as omitted and not silently treated as renormalized",
                "the unweighted vacuum mode integrals have recorded quartic and quadratic cutoff lower bounds",
            ] if status.startswith("PASS") else [],
            "equation_or_mapping": {
                "thermal_tail_inequality": "-log(1-exp(-x)) <= exp(-x)/(1-exp(-x)), n_B(x) <= exp(-x)/(1-exp(-x))",
                "normal_branch_domain": "E_k >= p and x_min=(p-|mu|)/T > 0 for p >= cutoff",
                "thermal_pressure_tail": "R_p <= 2*T/(2*pi^2) * integral_cutoff^infinity p^2 exp(-(p-|mu|)/T)/(1-exp(-x_cutoff)) dp",
                "vacuum_zero_point_boundary": "I_0(Lambda)=integral_0^Lambda p^2*E_p dp/(2*pi^2) >= Lambda^4/(8*pi^2)",
                "vacuum_response_boundary": "I_1(Lambda)=integral_m^Lambda p^2/E_p dp/(2*pi^2) >= (Lambda^2-m^2)/(4*sqrt(2)*pi^2)",
            },
            "units": {
                "all_integrals": "natural units",
                "cutoff_and_mass": "natural momentum/energy",
                "tail_bounds": "same natural units as the corresponding thermal observable",
                "vacuum_bounds": "unweighted natural-unit mode-integral diagnostics",
            },
            "derivation_class": "analytic thermal-tail bound plus structural UV divergence boundary; not a counterterm derivation",
            "observable": "thermal-only one-loop normal-branch outputs and their omitted-vacuum boundary",
            "data_role": "ACTION_DERIVED_SCOPE_BOUNDARY_NOT_RENORMALIZED_PHYSICAL_INPUT",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "vacuum_counterterm_and_renormalized_one_loop_response_not_closed",
                "interacting_finite_temperature_self_energy_not_derived",
                "condensate_goldstone_and_normal_two_fluid_completion_not_derived",
                "physical_Kubo_coefficient_record_missing",
                "SI_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_missing",
            ],
            "dependency_unlocked": "thermal-only UV scope boundary and explicit renormalization blocker; no physical transport, SI, Full Topic 13, Core, or Gravity unlock",
            "claim_boundary": "This closes the scope and tail-control boundary of the declared thermal-only normal branch. It does not provide vacuum counterterms, a renormalized one-loop action, interacting finite-temperature dynamics, physical transport, SI Phi calibration, external validation, or global UET closure.",
        },
        "reference": {
            **REFERENCE,
            "effective_mass_sq": mass_sq,
            "effective_mass": mass,
            "dm_eff_sq_dphi": dm_eff_sq_dphi,
            "momentum_cutoff": cutoff,
            "quadrature_order": int(convergence["reference"]["quadrature_order"]),
            "cutoff_factor": float(convergence["reference"]["cutoff_factor"]),
        },
        "thermal_tail": {
            "lower_momentum": cutoff,
            "bose_argument_lower_bound": (cutoff - abs(state.chemical_potential)) / state.temperature,
            "relative_threshold": TAIL_RELATIVE_THRESHOLD,
            "absolute_bounds": bounds,
            "relative_to_reference": relative_bounds,
        },
        "vacuum_boundary": {
            "zero_point_term_included": False,
            "renormalized_action_claimed": False,
            "zero_point_expression": "Omega_vac(Lambda) is proportional to integral_0^Lambda p^2*sqrt(p^2+m_eff^2) dp/(2*pi^2)",
            "response_expression": "dOmega_vac/dPhi is proportional to (dm_eff^2/dPhi) * integral_0^Lambda p^2/E_p dp/(2*pi^2)",
            "lower_bounds": vacuum_bounds,
            "interpretation": "The lower bounds establish the UV divergence boundary of the omitted vacuum term; they are not a renormalized prediction.",
        },
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "vacuum_counterterm_and_renormalized_one_loop_response_not_closed",
        "next_controller": "Derive a source-backed vacuum renormalization contract from the declared action, or retain the thermal-only lane and proceed only with separately proven finite-temperature sectors.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "failed_checks": [key for key, value in checks.items() if not value],
        "max_relative_tail_bound": max(relative_bounds.values()),
        "reference_cutoff": cutoff,
    }, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
