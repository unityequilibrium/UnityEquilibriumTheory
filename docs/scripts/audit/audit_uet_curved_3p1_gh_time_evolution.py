"""Verify periodic vacuum GH time evolution and constraint propagation."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_curved_3p1_generalized_harmonic import GHNonlinearParameters
from docs.core.uet_curved_3p1_gh_evolution import (
    GHEvolutionState,
    GHTimeIntegrationParameters,
    evolve_periodic_vacuum_gh,
    generalized_harmonic_time_evolution_contract,
    gh_constraint_norms,
    harmonic_gauge_wave_state,
)


ARTIFACTS = ROOT / "docs/core/artifacts"
VERIFY = ARTIFACTS / "curved_3p1_gh_time_evolution_verification.json"
FORMULA = ARTIFACTS / "curved_3p1_gh_time_evolution_formula_audit.json"
GATE = ARTIFACTS / "curved_3p1_gh_time_evolution_gate.json"
SOURCE_RECORD = ROOT / "docs/data/external/gr_3p1/lindblom_et_al_2006_gh/source_record.json"
RHS_VERIFY = ARTIFACTS / "curved_3p1_gh_nonlinear_vacuum_rhs_verification.json"
RHS_FORMULA = ARTIFACTS / "curved_3p1_gh_nonlinear_vacuum_formula_audit.json"
RHS_GATE = ARTIFACTS / "curved_3p1_gh_nonlinear_vacuum_gate.json"
MODULE = ROOT / "docs/core/uet_curved_3p1_gh_evolution.py"


THRESHOLDS = {
    "maximum_cfl": 0.20,
    "spatial_order_min": 1.80,
    "temporal_order_min": 3.50,
    "gauge_constraint_linf_max": 1.0e-12,
    "curl_constraint_linf_max": 1.0e-12,
    "reduction_damping_relative_error_max": 1.0e-8,
    "gauge_wave_metric_l2_error_max_finest": 2.0e-6,
    "minimum_lapse": 0.90,
    "minimum_spatial_inverse_eigenvalue": 0.90,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def l2(value: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(value))))


def minkowski_control() -> dict:
    shape = (5, 5, 5)
    metric = np.broadcast_to(
        np.diag([-1.0, 1.0, 1.0, 1.0]), shape + (4, 4)
    ).copy()
    state = GHEvolutionState(
        metric,
        np.zeros_like(metric),
        np.zeros(shape + (3, 4, 4)),
    )
    source = np.zeros(shape + (4,))
    source_derivative = np.zeros(shape + (4, 4))
    result = evolve_periodic_vacuum_gh(
        state,
        source,
        source_derivative,
        (0.2, 0.2, 0.2),
        0.05,
    )
    return {
        "metric_linf": float(np.max(np.abs(result.state.spacetime_metric - metric))),
        "normal_derivative_linf": float(np.max(np.abs(result.state.normal_derivative))),
        "spatial_derivative_linf": float(np.max(np.abs(result.state.spatial_derivative))),
        "final_gauge_linf": result.diagnostics[-1].gauge_linf,
        "final_reduction_linf": result.diagnostics[-1].reduction_linf,
        "maximum_observed_courant": result.maximum_observed_courant,
        "step_count": result.step_count,
    }


def gauge_wave_run(n: int, cfl: float, final_time: float = 0.05) -> dict:
    state, source, source_derivative, spacing = harmonic_gauge_wave_state(
        (n, 5, 5), (1.0, 1.0, 1.0), amplitude=0.05
    )
    result = evolve_periodic_vacuum_gh(
        state,
        source,
        source_derivative,
        spacing,
        final_time,
        integration=GHTimeIntegrationParameters(cfl=cfl),
    )
    exact = harmonic_gauge_wave_state(
        (n, 5, 5), (1.0, 1.0, 1.0), time=final_time, amplitude=0.05
    )[0]
    final = result.diagnostics[-1]
    return {
        "n": n,
        "cfl": cfl,
        "step_count": result.step_count,
        "metric_l2_error": l2(result.state.spacetime_metric - exact.spacetime_metric),
        "normal_derivative_l2_error": l2(result.state.normal_derivative - exact.normal_derivative),
        "spatial_derivative_l2_error": l2(result.state.spatial_derivative - exact.spatial_derivative),
        "gauge_linf": final.gauge_linf,
        "reduction_l2": final.reduction_l2,
        "reduction_linf": final.reduction_linf,
        "curl_linf": final.curl_linf,
        "minimum_lapse": min(item.minimum_lapse for item in result.diagnostics),
        "minimum_spatial_inverse_eigenvalue": min(
            item.minimum_spatial_inverse_eigenvalue for item in result.diagnostics
        ),
        "metric_symmetry_linf": max(item.metric_symmetry_linf for item in result.diagnostics),
        "maximum_observed_courant": result.maximum_observed_courant,
        "state": result.state,
        "run_contract": result.run_contract,
    }


def spatial_convergence() -> dict:
    rows = [gauge_wave_run(n, 0.08) for n in (12, 24, 48)]
    metric_errors = [row["metric_l2_error"] for row in rows]
    reduction_errors = [row["reduction_l2"] for row in rows]
    metric_orders = [
        math.log(metric_errors[i] / metric_errors[i + 1], 2.0) for i in range(2)
    ]
    reduction_orders = [
        math.log(reduction_errors[i] / reduction_errors[i + 1], 2.0)
        for i in range(2)
    ]
    for row in rows:
        row.pop("state")
    return {
        "grid_sizes": [12, 24, 48],
        "rows": rows,
        "metric_orders": metric_orders,
        "reduction_constraint_orders": reduction_orders,
        "minimum_metric_order": min(metric_orders),
        "minimum_reduction_constraint_order": min(reduction_orders),
    }


def temporal_convergence() -> dict:
    rows = [gauge_wave_run(24, cfl) for cfl in (0.16, 0.08, 0.04)]
    states = [row.pop("state") for row in rows]
    differences = [
        l2(states[i].spacetime_metric - states[i + 1].spacetime_metric)
        for i in range(2)
    ]
    order = math.log(differences[0] / differences[1], 2.0)
    return {
        "grid_size": 24,
        "cfl_values": [0.16, 0.08, 0.04],
        "rows": rows,
        "successive_metric_differences": differences,
        "rk4_self_convergence_order": order,
    }


def reduction_damping_control() -> dict:
    shape = (5, 5, 5)
    metric = np.broadcast_to(
        np.diag([-1.0, 1.0, 1.0, 1.0]), shape + (4, 4)
    ).copy()
    phi = np.zeros(shape + (3, 4, 4))
    phi[..., 0, 2, 3] = phi[..., 0, 3, 2] = 1.0e-6
    state = GHEvolutionState(metric, np.zeros_like(metric), phi)
    source = np.zeros(shape + (4,))
    source_derivative = np.zeros(shape + (4, 4))
    spacing = (0.2, 0.2, 0.2)
    initial = gh_constraint_norms(state, source, spacing)
    final_time = 0.2
    parameters = GHNonlinearParameters(gamma0=1.0, gamma2=1.0)
    result = evolve_periodic_vacuum_gh(
        state,
        source,
        source_derivative,
        spacing,
        final_time,
        parameters,
        GHTimeIntegrationParameters(cfl=0.08),
    )
    final = result.diagnostics[-1]
    observed_ratio = final.reduction_l2 / initial.reduction_l2
    expected_ratio = math.exp(-parameters.gamma2 * final_time)
    return {
        "initial_reduction_l2": initial.reduction_l2,
        "final_reduction_l2": final.reduction_l2,
        "observed_ratio": observed_ratio,
        "expected_exp_minus_gamma2_t": expected_ratio,
        "relative_error": abs(observed_ratio / expected_ratio - 1.0),
        "final_gauge_linf": final.gauge_linf,
        "perturbation_component": "Phi_x_yz=Phi_x_zy=1e-6",
    }


def negative_controls() -> dict:
    rejected = False
    try:
        GHTimeIntegrationParameters(cfl=0.21, maximum_cfl=0.20)
    except ValueError:
        rejected = True
    return {
        "cfl_above_preregistered_maximum_rejected": rejected,
        "constraint_projection_available": False,
        "filtering_available": False,
        "matter_source_available": False,
    }


def build_artifacts() -> tuple[dict, dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    rhs_verification = json.loads(RHS_VERIFY.read_text(encoding="utf-8"))
    rhs_formula = json.loads(RHS_FORMULA.read_text(encoding="utf-8"))
    rhs_gate = json.loads(RHS_GATE.read_text(encoding="utf-8"))
    minkowski = minkowski_control()
    spatial = spatial_convergence()
    temporal = temporal_convergence()
    damping = reduction_damping_control()
    negative = negative_controls()
    all_rows = spatial["rows"] + temporal["rows"]
    checks = {
        "nonlinear_rhs_dependency_passes": (
            rhs_verification["status"] == "PASS_GH_NONLINEAR_VACUUM_RHS"
            and rhs_formula["status"] == "PASS_SOURCE_LOCKED_GH_NONLINEAR_VACUUM_FORMULAS"
            and rhs_gate["status"] == "PARTIAL_GH_NONLINEAR_VACUUM_RHS_READY"
        ),
        "minkowski_is_exact_fixed_point": all(
            minkowski[key] == 0.0
            for key in (
                "metric_linf",
                "normal_derivative_linf",
                "spatial_derivative_linf",
                "final_gauge_linf",
                "final_reduction_linf",
            )
        ),
        "spatial_metric_convergence_passes": spatial["minimum_metric_order"] >= THRESHOLDS["spatial_order_min"],
        "spatial_constraint_convergence_passes": spatial["minimum_reduction_constraint_order"] >= THRESHOLDS["spatial_order_min"],
        "rk4_temporal_convergence_passes": temporal["rk4_self_convergence_order"] >= THRESHOLDS["temporal_order_min"],
        "finest_gauge_wave_error_passes": spatial["rows"][-1]["metric_l2_error"] <= THRESHOLDS["gauge_wave_metric_l2_error_max_finest"],
        "gauge_constraint_passes": max(row["gauge_linf"] for row in all_rows) <= THRESHOLDS["gauge_constraint_linf_max"],
        "curl_constraint_passes": max(row["curl_linf"] for row in all_rows) <= THRESHOLDS["curl_constraint_linf_max"],
        "reduction_damping_matches_gamma2": damping["relative_error"] <= THRESHOLDS["reduction_damping_relative_error_max"],
        "lorentzian_slicing_remains_bounded": (
            min(row["minimum_lapse"] for row in all_rows) >= THRESHOLDS["minimum_lapse"]
            and min(row["minimum_spatial_inverse_eigenvalue"] for row in all_rows)
            >= THRESHOLDS["minimum_spatial_inverse_eigenvalue"]
        ),
        "metric_symmetry_preserved": max(row["metric_symmetry_linf"] for row in all_rows) < 1.0e-14,
        "cfl_contract_passes": max(row["maximum_observed_courant"] for row in all_rows) <= THRESHOLDS["maximum_cfl"],
        "negative_controls_pass": all(
            value is True if key.endswith("rejected") else value is False
            for key, value in negative.items()
        ),
        "no_projection_filtering_clipping_or_fit": all(
            row["run_contract"][key] is False
            for row in all_rows
            for key in (
                "constraint_projection",
                "numerical_filtering",
                "artificial_dissipation",
                "field_clipping",
                "parameter_fitting",
            )
        ),
    }
    passed = all(checks.values())
    verification = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_gh_time_evolution_verification",
        "generated_at": now,
        "status": "PASS_GH_PERIODIC_VACUUM_TIME_EVOLUTION" if passed else "FAIL_GH_PERIODIC_VACUUM_TIME_EVOLUTION",
        "thresholds": THRESHOLDS,
        "controls": {
            "minkowski": minkowski,
            "harmonic_gauge_wave_spatial": spatial,
            "harmonic_gauge_wave_temporal": temporal,
            "reduction_constraint_damping": damping,
            "negative_controls": negative,
        },
        "checks": checks,
        "source_hashes": {
            SOURCE_RECORD.relative_to(ROOT).as_posix(): sha256(SOURCE_RECORD),
            RHS_VERIFY.relative_to(ROOT).as_posix(): sha256(RHS_VERIFY),
            RHS_FORMULA.relative_to(ROOT).as_posix(): sha256(RHS_FORMULA),
            RHS_GATE.relative_to(ROOT).as_posix(): sha256(RHS_GATE),
            MODULE.relative_to(ROOT).as_posix(): sha256(MODULE),
        },
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_PERIODIC_VACUUM_EVOLUTION_READY",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "classical RK4 integration of the verified nonlinear vacuum GH RHS",
                "fixed conservative characteristic CFL policy on a periodic grid",
                "exact Minkowski and exact harmonic gauge-wave evolution controls",
                "second-order spatial and fourth-order temporal convergence",
                "gauge, reduction, and curl constraint diagnostics over time",
                "gamma2 reduction-constraint damping rate",
            ] if passed else [name for name, value in checks.items() if value],
            "what_remains_open": [
                "constraint-preserving non-periodic boundaries",
                "Topic 13 stress-energy wiring",
                "dimensional detector observable mapping",
            ],
            "equation_or_mapping": {
                "time_step": "dt <= cfl min(dx_i)/max(alpha+||beta||_2)",
                "integrator": "classical RK4 applied to GH Eqs. 35-37",
                "gauge_constraint": "C_a=H_a+Gamma_a",
                "reduction_constraint": "C_iab=partial_i psi_ab-Phi_iab",
            },
            "units": "geometric c=1 periodic-coordinate lane",
            "derivation_class": "STANDARD_NUMERICAL_METHOD_APPLIED_TO_SOURCE_LOCKED_VACUUM_GH_SYSTEM",
            "observable": "solution-error and propagated-constraint diagnostics",
            "data_role": "INTERNAL_ANALYTIC_AND_CONVERGENCE_CONTROL",
            "evidence_artifacts": [],
            "verification_status": "PASS_GH_PERIODIC_VACUUM_TIME_EVOLUTION" if passed else "FAIL",
            "open_blockers": [
                "constraint_preserving_boundaries_missing",
                "topic13_stress_energy_projection_missing",
                "dimensional_observable_mapping_missing",
            ],
            "dependency_unlocked": "constraint-preserving boundary and Topic 13 matter-wiring waves only",
            "claim_boundary": "periodic vacuum evolution control only; not a production numerical-relativity solver, matter-coupled UET parent, Gravity validation, or external claim",
        },
        "claim_promotion": False,
    }
    formula = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_gh_time_evolution_formula_audit",
        "generated_at": now,
        "status": "PASS_GH_TIME_EVOLUTION_NUMERICAL_CONTRACT" if passed else "FAIL",
        "formulas": [
            {
                "formula_id": "UET-CURVED3P1-GH-RK4-018",
                "relation": "u_(n+1)=u_n+dt*(k1+2k2+2k3+k4)/6",
                "classification": "STANDARD_NUMERICAL_INTEGRATOR",
                "units": "each stage derivative carries state unit per coordinate time",
                "proof_status": "implemented and fourth-order self-convergence verified",
            },
            {
                "formula_id": "UET-CURVED3P1-GH-CFL-019",
                "relation": "dt<=cfl*min(dx_i)/max(alpha+||beta||_2)",
                "classification": "CONSERVATIVE_NUMERICAL_STABILITY_CONTRACT",
                "units": "coordinate time in geometric c=1 units",
                "proof_status": "runtime-enforced for the declared periodic controls; not a universal stability proof",
            },
            {
                "formula_id": "UET-CURVED3P1-GH-GAUGE-WAVE-020",
                "relation": "ds^2=H(-dt^2+dx^2)+dy^2+dz^2; H=1-A sin(2pi(x-t)/L)",
                "classification": "EXACT_VACUUM_HARMONIC_COORDINATE_CONTROL",
                "units": "dimensionless metric; coordinate length/time",
                "proof_status": "analytic control used for error and constraint convergence",
            },
        ],
        "checks": checks,
        "claim_boundary": verification["major_result"]["claim_boundary"],
        "claim_promotion": False,
    }
    requirements = {
        "nonlinear_vacuum_rhs": "PASS" if checks["nonlinear_rhs_dependency_passes"] else "FAIL",
        "rk4_time_integration": "PASS" if checks["rk4_temporal_convergence_passes"] else "FAIL",
        "characteristic_cfl_contract": "PASS" if checks["cfl_contract_passes"] else "FAIL",
        "periodic_gauge_wave_convergence": "PASS" if checks["spatial_metric_convergence_passes"] else "FAIL",
        "constraint_propagation_convergence": "PASS" if checks["spatial_constraint_convergence_passes"] else "FAIL",
        "constraint_damping": "PASS" if checks["reduction_damping_matches_gamma2"] else "FAIL",
        "constraint_preserving_boundaries": "OPEN",
        "matter_stress_energy_wiring": "OPEN",
        "dimensional_observable_mapping": "OPEN",
    }
    gate = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_gh_time_evolution_gate",
        "generated_at": now,
        "status": "PARTIAL_GH_PERIODIC_VACUUM_EVOLUTION_READY" if passed else "BLOCKED_GH_TIME_EVOLUTION",
        "requirements": requirements,
        "closed_requirements": [key for key, value in requirements.items() if value == "PASS"],
        "open_requirements": [key for key, value in requirements.items() if value != "PASS"],
        "controlling_blocker": "curved_3p1_constraint_preserving_boundaries_and_topic13_stress_energy_wiring_missing",
        "evidence_artifacts": [
            {"path": VERIFY.relative_to(ROOT).as_posix(), "sha256": None},
            {"path": FORMULA.relative_to(ROOT).as_posix(), "sha256": None},
        ],
        "dependency_unlocked": "constraint-preserving boundary and Topic 13 matter-wiring waves only",
        "claim_boundary": verification["major_result"]["claim_boundary"],
        "claim_promotion": False,
    }
    return verification, formula, gate


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    verification, formula, gate = build_artifacts()
    VERIFY.write_text(json.dumps(verification, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    FORMULA.write_text(json.dumps(formula, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    gate["evidence_artifacts"][0]["sha256"] = sha256(VERIFY)
    gate["evidence_artifacts"][1]["sha256"] = sha256(FORMULA)
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": verification["status"],
        "gate_status": gate["status"],
        "spatial_order": verification["controls"]["harmonic_gauge_wave_spatial"]["minimum_metric_order"],
        "temporal_order": verification["controls"]["harmonic_gauge_wave_temporal"]["rk4_self_convergence_order"],
        "controlling_blocker": gate["controlling_blocker"],
    }, indent=2))
    return 0 if verification["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
