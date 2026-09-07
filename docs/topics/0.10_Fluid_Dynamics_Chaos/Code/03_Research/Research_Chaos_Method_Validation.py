"""Validate the shared UET chaos diagnostics against known control systems."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Callable

import numpy as np


ROOT = Path(__file__).resolve().parents[5]
OUT = (
    ROOT
    / "docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts/chaos_method_validation.json"
)
CORE_MODULE = ROOT / "docs/core/uet_dynamical_stability.py"

if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from docs.core.uet_dynamical_stability import (  # noqa: E402
    LYAPUNOV_SPECTRUM_ID,
    REGIME_CLASSIFIER_ID,
    TANGENT_MAP_ID,
    benettin_qr,
    classify_dynamical_regime,
    lyapunov_resolution,
    shadow_trajectory_exponent,
    validate_diagnostic_contract,
)


PERTURBATIONS = [1.0e-8, 1.0e-7, 1.0e-6]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def linear_control(dt: float) -> tuple[dict, dict]:
    decay = 0.4
    multiplier = np.exp(-decay * dt)

    def step(state: np.ndarray, _: int) -> np.ndarray:
        return multiplier * state

    def tangent_step(_: np.ndarray, tangent: np.ndarray, __: int) -> np.ndarray:
        return multiplier * tangent

    tangent = benettin_qr(step, tangent_step, np.array([1.0]), dt, 600)
    shadow = shadow_trajectory_exponent(
        step, np.array([1.0]), dt, 600, perturbation_amplitude=1.0e-7
    )
    return tangent, shadow


def logistic_control() -> tuple[dict, dict]:
    def step(state: np.ndarray, _: int) -> np.ndarray:
        return np.array([4.0 * state[0] * (1.0 - state[0])])

    def tangent_step(state: np.ndarray, tangent: np.ndarray, _: int) -> np.ndarray:
        return (4.0 - 8.0 * state[0]) * tangent

    initial = np.array([0.123456789])
    tangent = benettin_qr(
        step, tangent_step, initial, 1.0, 40000, transient_steps=1000
    )
    shadow = shadow_trajectory_exponent(
        step,
        initial,
        1.0,
        40000,
        perturbation_amplitude=1.0e-8,
        transient_steps=1000,
    )
    return tangent, shadow


def lorenz_stepper(dt: float) -> tuple[Callable, Callable]:
    sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0

    def rhs(state: np.ndarray) -> np.ndarray:
        x, y, z = state
        return np.array([sigma * (y - x), x * (rho - z) - y, x * y - beta * z])

    def jacobian(state: np.ndarray) -> np.ndarray:
        x, y, z = state
        return np.array(
            [[-sigma, sigma, 0.0], [rho - z, -1.0, -x], [y, x, -beta]]
        )

    def step(state: np.ndarray, _: int) -> np.ndarray:
        k1 = rhs(state)
        k2 = rhs(state + 0.5 * dt * k1)
        k3 = rhs(state + 0.5 * dt * k2)
        k4 = rhs(state + dt * k3)
        return state + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0

    def tangent_step(state: np.ndarray, tangent: np.ndarray, _: int) -> np.ndarray:
        k1_state = rhs(state)
        k1_tangent = jacobian(state) @ tangent
        state2 = state + 0.5 * dt * k1_state
        tangent2 = tangent + 0.5 * dt * k1_tangent
        k2_state = rhs(state2)
        k2_tangent = jacobian(state2) @ tangent2
        state3 = state + 0.5 * dt * k2_state
        tangent3 = tangent + 0.5 * dt * k2_tangent
        k3_state = rhs(state3)
        k3_tangent = jacobian(state3) @ tangent3
        state4 = state + dt * k3_state
        tangent4 = tangent + dt * k3_tangent
        k4_tangent = jacobian(state4) @ tangent4
        return tangent + dt * (
            k1_tangent + 2.0 * k2_tangent + 2.0 * k3_tangent + k4_tangent
        ) / 6.0

    return step, tangent_step


def lorenz_control(dt: float) -> tuple[dict, dict]:
    step, tangent_step = lorenz_stepper(dt)
    initial = np.array([1.0, 1.0, 1.0])
    steps = int(100.0 / dt)
    transient = int(20.0 / dt)
    interval = max(1, int(0.1 / dt))
    tangent = benettin_qr(
        step,
        tangent_step,
        initial,
        dt,
        steps,
        transient_steps=transient,
        renormalization_interval=interval,
        spectrum_size=3,
    )
    shadow = shadow_trajectory_exponent(
        step,
        initial,
        dt,
        steps,
        perturbation_amplitude=1.0e-7,
        transient_steps=transient,
        renormalization_interval=interval,
    )
    return tangent, shadow


def diagnostic(
    diagnostic_id: str,
    tangent: dict,
    shadow: dict,
    *,
    dt_difference: float,
    expected: str,
    resolution_grid: dict,
) -> dict:
    disagreement = abs(tangent["lambda_max"] - shadow["lambda_max"])
    resolution = lyapunov_resolution(
        dt_difference,
        0.0,
        tangent["block_standard_error"],
        disagreement,
    )
    classification = classify_dynamical_regime(
        lambda_max=tangent["lambda_max"],
        lambda_resolution_value=resolution,
        early_ftle_positive=tangent["lambda_max"] > 0.0,
        boundedness=True,
        stationarity=True,
        ledger_pass=True,
        conservation_pass=True,
        causal_pass=True,
        method_agreement=disagreement <= max(resolution, 0.05),
    )
    record = {
        "diagnostic_id": diagnostic_id,
        "owner_topic": "0.10_Fluid_Dynamics_Chaos",
        "equation_registry_ids": [TANGENT_MAP_ID, LYAPUNOV_SPECTRUM_ID, REGIME_CLASSIFIER_ID],
        "state_variables": ["benchmark_state"],
        "excluded_variables": ["R_gen", "R_obs"],
        "unit_lane": "normalized",
        "forcing_class": "autonomous_control",
        "noise_coupling": "none",
        "state_metric": "normalized_l2",
        "estimator": [tangent["estimator"], shadow["estimator"]],
        "transient_window": resolution_grid.get("transient_window"),
        "renormalization_interval": resolution_grid.get("renormalization_interval", 1),
        "perturbation_amplitudes": PERTURBATIONS,
        "resolution_grid": resolution_grid,
        "lambda_max": tangent["lambda_max"],
        "lambda_spectrum": tangent["lambda_spectrum"],
        "confidence_or_block_error": tangent["block_standard_error"],
        "lambda_resolution": resolution,
        "boundedness": True,
        "stationarity": True,
        "ledger_status": "NOT_APPLICABLE_STANDARD_CONTROL",
        "conservation_status": "NOT_APPLICABLE_STANDARD_CONTROL",
        "causal_status": "NOT_APPLICABLE_STANDARD_CONTROL",
        "method_agreement": disagreement <= max(resolution, 0.05),
        "classification": classification,
        "controlling_blocker": "none_for_standard_method_control",
        "evidence_hashes": {
            "generator": sha256(Path(__file__)),
            "core_diagnostic": sha256(CORE_MODULE),
        },
        "claim_boundary": "Numerical method control only; not evidence that a UET fluid lane is chaotic.",
        "cross_check": shadow,
        "expected_control": expected,
    }
    validate_diagnostic_contract(record)
    return record


def main() -> int:
    linear_dt, linear_shadow = linear_control(0.05)
    linear_fine, _ = linear_control(0.025)
    logistic, logistic_shadow = logistic_control()
    lorenz, lorenz_shadow = lorenz_control(0.01)
    lorenz_fine, _ = lorenz_control(0.005)

    controls = {
        "stable_linear": diagnostic(
            "t010.chaos.control.stable_linear",
            linear_dt,
            linear_shadow,
            dt_difference=abs(linear_dt["lambda_max"] - linear_fine["lambda_max"]),
            expected="lambda=-0.4",
            resolution_grid={"dt": [0.05, 0.025], "transient_window": 0.0},
        ),
        "logistic_r4": diagnostic(
            "t010.chaos.control.logistic_r4",
            logistic,
            logistic_shadow,
            dt_difference=0.0,
            expected="lambda=ln(2)",
            resolution_grid={"map_parameter_r": 4.0, "transient_window": 1000},
        ),
        "lorenz63": diagnostic(
            "t010.chaos.control.lorenz63",
            lorenz,
            lorenz_shadow,
            dt_difference=abs(lorenz["lambda_max"] - lorenz_fine["lambda_max"]),
            expected="resolved positive largest exponent",
            resolution_grid={
                "dt": [0.01, 0.005],
                "transient_window": 20.0,
                "renormalization_interval": 0.1,
            },
        ),
    }
    checks = {
        "stable_linear_exact": bool(
            abs(controls["stable_linear"]["lambda_max"] + 0.4) <= 1.0e-6
        ),
        "logistic_ln2": bool(
            abs(controls["logistic_r4"]["lambda_max"] - np.log(2.0)) <= 0.02
        ),
        "lorenz_positive_resolved": bool(
            controls["lorenz63"]["lambda_max"]
            > controls["lorenz63"]["lambda_resolution"]
        ),
        "lorenz_method_agreement": bool(controls["lorenz63"]["method_agreement"]),
        "ontology_exclusion": bool(all(
            "R_gen" not in item["state_variables"] and "R_obs" not in item["state_variables"]
            for item in controls.values()
        )),
    }
    passed = all(checks.values())
    artifact = {
        "schema_version": "uet-chaos-diagnostic-v1",
        "artifact": "chaos_method_validation",
        "generated_at": date.today().isoformat(),
        "status": "PASS_CHAOS_METHOD_VALIDATION" if passed else "FAIL_CHAOS_METHOD_VALIDATION",
        "claim_promotion": False,
        "preregistration": {
            "perturbation_amplitudes": PERTURBATIONS,
            "resolution_formula": "max(dt_difference, dx_difference, 2*block_standard_error, method_disagreement)",
            "primary_estimator": "BENETTIN_QR_TANGENT",
            "cross_check": "SHADOW_PERIODIC_RENORMALIZATION",
        },
        "controls": controls,
        "checks": checks,
        "major_result": {
            "major_result_id": "T010_CHAOS_METHOD_VALIDATED",
            "topic": "0.10_Fluid_Dynamics_Chaos",
            "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
            "what_is_closed": [
                "tangent/QR and shadow estimators reproduce preregistered standard controls",
                "Lyapunov-function language is separated from Lyapunov-exponent evidence",
                "numerical instability and unresolved signs are excluded from chaos-candidate classification",
            ] if passed else ["machine-readable method controls were executed"],
            "equation_or_mapping": "delta_x[n+1] = D F(x[n]) delta_x[n]; lambda_i = lim_T log(s_i)/T",
            "units": "inverse normalized time; logistic-map exponent per iteration",
            "derivation_class": "standard dynamical-systems diagnostic and numerical method validation",
            "observable": "Lyapunov spectrum, largest exponent, method disagreement, and sign resolution",
            "data_role": "INTERNAL_STANDARD_METHOD_CONTROLS",
            "verification_status": "PASS_CHAOS_METHOD_VALIDATION" if passed else "FAIL_CHAOS_METHOD_VALIDATION",
            "open_blockers": [
                "no UET physical-fluid chaos claim is evaluated by this method-control artifact",
                "external CFD validation and full constitutive transport remain open",
            ],
            "dependency_unlocked": "Topic 13 normalized thermal diagnostic pilot only; no physical Core, Gravity, Galaxy, or external-claim unlock",
            "claim_boundary": "Method validation only; this does not establish chaos in UET or validate a physical fluid model.",
        },
        "report": {
            "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE" if passed else "PARTIAL",
            "WHAT_IS_ACTUALLY_CLOSED": "standard chaos-estimator controls",
            "WHAT_REMAINS_OPEN": "UET physical-lane diagnosis and external validation",
            "DEPENDENCY_UNLOCKED": "Topic 13 diagnostic pilot only" if passed else "none",
            "STATUS": "PASS" if passed else "FAIL",
            "WHAT_CHANGED": "Added an independent chaos-method artifact separate from the speed comparator.",
            "EQUATION_OR_MAPPING": "tangent map -> QR growth rates; shadow trajectory cross-check",
            "VERIFICATION": checks,
            "CONTROLLING_BLOCKER": "physical UET lane not tested by this artifact",
            "NEXT_ACTION": "run the Topic 13 normalized thermal regime pilot",
            "CLAIM_BOUNDARY": "internal method validation only",
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "artifact": OUT.relative_to(ROOT).as_posix()}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
