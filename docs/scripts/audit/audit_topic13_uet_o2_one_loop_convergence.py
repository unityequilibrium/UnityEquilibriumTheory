"""Audit cutoff and quadrature convergence for the one-loop normal branch."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import date
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
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_convergence_audit.json"

METRICS = (
    "pressure",
    "pressure_phi_derivative",
    "thermal_scalar_density",
    "charge_density",
    "entropy_density",
    "energy_density",
    "charge_susceptibility",
)
CUTOFF_FACTORS = (30.0, 40.0, 50.0, 70.0, 100.0)
QUADRATURE_ORDERS = (64, 96, 128, 192, 256)
PLATEAU_MIN_ORDER = 96
REFERENCE_CUTOFF = 70.0
REFERENCE_ORDER = 256
RELATIVE_DRIFT_THRESHOLD = 1.0e-8


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


def relative_delta(a: float, b: float) -> float:
    denominator = max(abs(float(a)), abs(float(b)), 1.0e-30)
    return abs(float(a) - float(b)) / denominator


def state_record(state: object) -> dict[str, float]:
    return {name: float(getattr(state, name)) for name in METRICS}


def main() -> int:
    eos_config = config()
    grid: dict[str, dict[str, dict[str, float]]] = {}
    for cutoff in CUTOFF_FACTORS:
        cutoff_key = str(int(cutoff))
        grid[cutoff_key] = {}
        for order in QUADRATURE_ORDERS:
            state = uet_o2_one_loop_normal_state(
                0.35,
                0.2,
                0.2,
                eos_config,
                quadrature_order=order,
                cutoff_factor=cutoff,
            )
            grid[cutoff_key][str(order)] = state_record(state)

    reference = grid[str(int(REFERENCE_CUTOFF))][str(REFERENCE_ORDER)]
    plateau_records = [
        (cutoff, order, grid[str(int(cutoff))][str(order)])
        for cutoff in CUTOFF_FACTORS
        for order in QUADRATURE_ORDERS
        if order >= PLATEAU_MIN_ORDER
    ]
    plateau_drift = {
        metric: max(relative_delta(values[metric], reference[metric]) for _, _, values in plateau_records)
        for metric in METRICS
    }
    tail_drift = {
        metric: relative_delta(
            grid["70"]["192"][metric],
            grid["100"]["192"][metric],
        )
        for metric in METRICS
    }
    order_drift = {
        metric: relative_delta(
            grid["70"]["192"][metric],
            grid["70"]["256"][metric],
        )
        for metric in METRICS
    }
    low_order_drift = {
        metric: relative_delta(
            grid["100"]["64"][metric],
            reference[metric],
        )
        for metric in METRICS
    }
    branch_audit = json.loads((ROOT / BRANCH_AUDIT_REL).read_text(encoding="utf-8-sig"))
    module_text = (ROOT / MODULE_REL).read_text(encoding="utf-8-sig")
    comparator_text = (ROOT / COMPARATOR_REL).read_text(encoding="utf-8-sig")
    checks = {
        "reference_is_high_order": REFERENCE_ORDER == max(QUADRATURE_ORDERS),
        "reference_cutoff_is_in_sweep": REFERENCE_CUTOFF in CUTOFF_FACTORS,
        "plateau_contains_multiple_orders": len({order for _, order, _ in plateau_records}) >= 3,
        "plateau_contains_multiple_cutoffs": len({cutoff for cutoff, _, _ in plateau_records}) >= 3,
        "plateau_metric_drift_is_bounded": all(value <= RELATIVE_DRIFT_THRESHOLD for value in plateau_drift.values()),
        "cutoff_tail_is_resolved": all(value <= RELATIVE_DRIFT_THRESHOLD for value in tail_drift.values()),
        "quadrature_order_is_resolved": all(value <= RELATIVE_DRIFT_THRESHOLD for value in order_drift.values()),
        "low_order_is_not_used_as_reference": any(value > RELATIVE_DRIFT_THRESHOLD for value in low_order_drift.values()),
        "cutoff_factor_is_explicit_in_comparator": "cutoff_factor" in comparator_text,
        "cutoff_factor_is_forwarded_to_branch": "cutoff_factor=cutoff_factor" in module_text,
        "branch_audit_passes": branch_audit["status"] == "PASS_ACTION_DERIVED_ONE_LOOP_NORMAL_LANE",
        "vacuum_counterterm_remains_excluded": branch_audit["state"]["vacuum_counterterm_included"] is False,
        "condensate_remains_excluded": branch_audit["state"]["condensate_contribution_included"] is False,
        "no_holdout_or_alpha_fit": branch_audit["holdout_policy"]["xie_2026_accessed"] is False and branch_audit["holdout_policy"]["alpha_fit_used"] is False,
    }
    status = "PASS_ACTION_DERIVED_ONE_LOOP_CONVERGENCE" if all(checks.values()) else "FAIL_ACTION_DERIVED_ONE_LOOP_CONVERGENCE"
    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": COMPARATOR_REL, "sha256": digest(COMPARATOR_REL)},
        {"path": BRANCH_AUDIT_REL, "sha256": digest(BRANCH_AUDIT_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-one-loop-convergence-v1",
        "artifact": "t13_uet_o2_one_loop_convergence_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_ONE_LOOP_CONVERGENCE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "cutoff-factor sweep for the thermal-only one-loop normal determinant",
                "quadrature-order convergence for pressure, Phi response derivative, scalar density, charge, entropy, energy, and susceptibility",
                "a reproducible plateau baseline at cutoff_factor=70 and quadrature_order=256",
                "low-order quadrature is excluded from the reference when high-cutoff resolution is insufficient",
            ] if status.startswith("PASS") else [],
            "equation_or_mapping": {
                "cutoff_control": "p in [0, cutoff_factor * max(T, m_eff, |mu|)]",
                "quadrature_control": "Gauss-Legendre order N over the explicit thermal-only integral",
                "acceptance": "max relative drift on the declared plateau <= 1e-8",
            },
            "units": {
                "cutoff": "natural momentum units",
                "pressure": "natural energy density",
                "response_derivative": "natural energy density per natural Phi field unit",
                "charge_density": "natural charge density",
                "entropy_density": "natural entropy density",
                "energy_density": "natural energy density",
                "susceptibility": "natural charge density per natural chemical-potential unit",
            },
            "derivation_class": "numerical convergence audit of an action-derived thermal one-loop normal-background integral; not renormalization or physical validation",
            "observable": "converged thermal normal-background thermodynamic outputs and Phi response derivative",
            "data_role": "ACTION_DERIVED_NUMERICAL_CONVERGENCE_NOT_PHYSICAL_TRANSPORT",
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
            "dependency_unlocked": "numerical stability of action-derived normal branch only; no full thermal, transport, Core, or Gravity unlock",
            "claim_boundary": "This closes numerical convergence of the declared thermal-only one-loop normal-background integral. It does not close vacuum renormalization, interacting finite-temperature UET dynamics, condensate/two-fluid response, Kubo transport, SI Phi calibration, external validation, or global UET closure.",
        },
        "reference": {
            "temperature": 0.35,
            "chemical_potential": 0.2,
            "space_response": 0.2,
            "cutoff_factor": REFERENCE_CUTOFF,
            "quadrature_order": REFERENCE_ORDER,
            "values": reference,
        },
        "policy": {
            "cutoff_factors": CUTOFF_FACTORS,
            "quadrature_orders": QUADRATURE_ORDERS,
            "plateau_min_order": PLATEAU_MIN_ORDER,
            "relative_drift_threshold": RELATIVE_DRIFT_THRESHOLD,
            "thermal_only": True,
            "vacuum_counterterm_included": False,
            "condensate_included": False,
            "parameter_fitting": False,
        },
        "grid": grid,
        "drift": {
            "plateau_max_relative_drift": plateau_drift,
            "cutoff_tail_relative_drift_order_192": tail_drift,
            "quadrature_order_relative_drift_cutoff_70": order_drift,
            "excluded_low_order_relative_drift_cutoff_100_order_64": low_order_drift,
        },
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "vacuum_counterterm_and_renormalized_one_loop_response_not_closed",
        "next_controller": "Close the thermal one-loop vacuum/renormalization contract or retain the thermal-only scope, then derive interacting finite-temperature and condensate/two-fluid sectors before physical transport matching.",
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
        "reference": report["reference"],
        "plateau_max_relative_drift": plateau_drift,
        "cutoff_tail_max_relative_drift": max(tail_drift.values()),
        "quadrature_order_max_relative_drift": max(order_drift.values()),
    }, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
