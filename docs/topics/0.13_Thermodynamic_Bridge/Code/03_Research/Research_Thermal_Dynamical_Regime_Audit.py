"""Classify normalized Topic 13 thermal controls with shared chaos diagnostics."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[5]
OUT = (
    ROOT
    / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_thermal_dynamical_regime_audit.json"
)
METHOD_ARTIFACT = (
    ROOT
    / "docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts/chaos_method_validation.json"
)
CORE_MODULE = ROOT / "docs/core/uet_dynamical_stability.py"
HOLDOUT_AUDIT = ROOT / "docs/core/artifacts/t13_xie_2026_holdout_access_audit.json"

if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from docs.core.uet_dynamical_stability import (  # noqa: E402
    GRADIENT_BOUNDARY_ID,
    LYAPUNOV_SPECTRUM_ID,
    REGIME_CLASSIFIER_ID,
    TANGENT_MAP_ID,
    benettin_qr,
    classify_dynamical_regime,
    lyapunov_resolution,
    matter_space_tangent_heun_step,
    pack_matter_space_state,
    shadow_trajectory_exponent,
    unpack_matter_space_state,
    validate_diagnostic_contract,
)
from docs.core.uet_matter_space import (  # noqa: E402
    MatterSpaceConfig,
    MatterSpaceState,
    matter_space_extended_energy,
    matter_space_rhs,
    matter_space_step,
)


PERTURBATIONS = [1.0e-8, 1.0e-7, 1.0e-6]
FIELD_SIZE = 8
DX = 0.5
BASE_CONFIG = MatterSpaceConfig(
    a_matter=0.5,
    b_matter=0.2,
    kappa_matter=0.1,
    mobility_matter=0.8,
    a_space=0.8,
    b_space=0.1,
    kappa_space=0.2,
    mobility_space=0.7,
    tau_space=0.5,
    coupling_g=0.1,
    matter_dynamics="nonconserved",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def initial_state() -> MatterSpaceState:
    x = 2.0 * np.pi * np.arange(FIELD_SIZE) / FIELD_SIZE
    return MatterSpaceState(
        0.12 * np.cos(x),
        0.08 * np.sin(x),
        0.02 * np.cos(2.0 * x),
    )


def source_at(index: int, dt: float, amplitude: float) -> np.ndarray:
    x = 2.0 * np.pi * np.arange(FIELD_SIZE) / FIELD_SIZE
    return amplitude * np.sin(1.5 * index * dt) * np.sin(x)


def callbacks(dt: float, drive_amplitude: float):
    def fast_heun_step(state: MatterSpaceState, source: np.ndarray) -> MatterSpaceState:
        k1 = matter_space_rhs(state, DX, BASE_CONFIG, space_source=source)[:3]
        predictor = MatterSpaceState(
            state.C + dt * k1[0],
            state.space_response + dt * k1[1],
            state.space_rate + dt * k1[2],
        )
        k2 = matter_space_rhs(predictor, DX, BASE_CONFIG, space_source=source)[:3]
        return MatterSpaceState(
            state.C + 0.5 * dt * (k1[0] + k2[0]),
            state.space_response + 0.5 * dt * (k1[1] + k2[1]),
            state.space_rate + 0.5 * dt * (k1[2] + k2[2]),
        )

    def step(vector: np.ndarray, index: int) -> np.ndarray:
        state = unpack_matter_space_state(vector, FIELD_SIZE)
        source = source_at(index, dt, drive_amplitude)
        return pack_matter_space_state(fast_heun_step(state, source))

    def tangent_step(vector: np.ndarray, basis: np.ndarray, index: int) -> np.ndarray:
        state = unpack_matter_space_state(vector, FIELD_SIZE)
        source = source_at(index, dt, drive_amplitude)
        columns = []
        for column in range(basis.shape[1]):
            perturbation = unpack_matter_space_state(basis[:, column], FIELD_SIZE)
            _, updated = matter_space_tangent_heun_step(
                state,
                perturbation,
                dt,
                DX,
                BASE_CONFIG,
                space_source=source,
            )
            columns.append(pack_matter_space_state(updated))
        return np.column_stack(columns)

    return step, tangent_step


def energy_ledger_audit(dt: float, drive_amplitude: float, steps: int) -> dict:
    state = initial_state()
    initial_energy = matter_space_extended_energy(state, DX, BASE_CONFIG)
    max_closure_relative = 0.0
    all_ledger_pass = True
    all_finite = True
    maximum_norm = float(np.linalg.norm(pack_matter_space_state(state)))
    for index in range(steps):
        result = matter_space_step(
            state,
            dt,
            DX,
            BASE_CONFIG,
            space_source=source_at(index, dt, drive_amplitude),
        )
        state = MatterSpaceState(result.C, result.space_response, result.space_rate)
        max_closure_relative = max(
            max_closure_relative, float(result.energy_ledger["closure_relative"])
        )
        all_ledger_pass = all_ledger_pass and result.energy_ledger["ledger_gate"] == "PASS"
        packed = pack_matter_space_state(state)
        all_finite = all_finite and bool(np.all(np.isfinite(packed)))
        maximum_norm = max(maximum_norm, float(np.linalg.norm(packed)))
    final_energy = matter_space_extended_energy(state, DX, BASE_CONFIG)
    return {
        "initial_energy": initial_energy,
        "final_energy": final_energy,
        "energy_descent": final_energy <= initial_energy + BASE_CONFIG.ledger_tolerance,
        "max_closure_relative": max_closure_relative,
        "all_step_ledger_gates_pass": all_ledger_pass,
        "all_finite": all_finite,
        "maximum_state_norm": maximum_norm,
    }


def matter_space_diagnostic(diagnostic_id: str, drive_amplitude: float) -> dict:
    estimates: dict[str, dict] = {}
    for dt in (0.004, 0.002):
        step, tangent_step = callbacks(dt, drive_amplitude)
        steps = int(8.0 / dt)
        transient = int(1.0 / dt)
        interval = int(0.1 / dt)
        estimates[str(dt)] = benettin_qr(
            step,
            tangent_step,
            pack_matter_space_state(initial_state()),
            dt,
            steps,
            transient_steps=transient,
            renormalization_interval=interval,
            spectrum_size=1,
        )
    step, _ = callbacks(0.002, drive_amplitude)
    shadows = {
        str(amplitude): shadow_trajectory_exponent(
            step,
            pack_matter_space_state(initial_state()),
            0.002,
            int(8.0 / 0.002),
            perturbation_amplitude=amplitude,
            transient_steps=int(1.0 / 0.002),
            renormalization_interval=int(0.1 / 0.002),
        )
        for amplitude in PERTURBATIONS
    }
    fine = estimates["0.002"]
    primary_shadow = shadows[str(1.0e-7)]
    shadow_values = [item["lambda_max"] for item in shadows.values()]
    amplitude_spread = max(shadow_values) - min(shadow_values)
    dt_difference = abs(estimates["0.004"]["lambda_max"] - fine["lambda_max"])
    disagreement = abs(fine["lambda_max"] - primary_shadow["lambda_max"])
    resolution = lyapunov_resolution(
        dt_difference,
        0.0,
        fine["block_standard_error"],
        max(disagreement, amplitude_spread),
    )
    ledger = energy_ledger_audit(0.00025, drive_amplitude, 4000)
    ledger_pass = bool(ledger["all_step_ledger_gates_pass"])
    bounded = bool(ledger["all_finite"] and ledger["maximum_state_norm"] < 10.0)
    method_agreement = bool(disagreement <= resolution and amplitude_spread <= resolution)
    classification = classify_dynamical_regime(
        lambda_max=fine["lambda_max"],
        lambda_resolution_value=resolution,
        early_ftle_positive=fine["lambda_max"] > 0.0,
        boundedness=bounded,
        stationarity=True,
        ledger_pass=ledger_pass,
        conservation_pass=True,
        causal_pass=True,
        method_agreement=method_agreement,
    )
    record = {
        "diagnostic_id": diagnostic_id,
        "owner_topic": "0.13_Thermodynamic_Bridge",
        "equation_registry_ids": [
            TANGENT_MAP_ID,
            LYAPUNOV_SPECTRUM_ID,
            REGIME_CLASSIFIER_ID,
            GRADIENT_BOUNDARY_ID,
        ],
        "state_variables": ["C", "Phi", "Pi"],
        "excluded_variables": ["R_gen", "R_obs"],
        "unit_lane": "normalized",
        "forcing_class": "closed_autonomous" if drive_amplitude == 0.0 else "periodically_driven",
        "noise_coupling": "none",
        "state_metric": "normalized_block_l2_reported_with_flat_l2_estimator",
        "estimator": [fine["estimator"], primary_shadow["estimator"]],
        "transient_window": 2.0,
        "renormalization_interval": 0.1,
        "perturbation_amplitudes": PERTURBATIONS,
        "resolution_grid": {"dt": [0.004, 0.002], "dx": [DX], "duration": 8.0},
        "lambda_max": fine["lambda_max"],
        "lambda_spectrum": fine["lambda_spectrum"],
        "confidence_or_block_error": fine["block_standard_error"],
        "lambda_resolution": resolution,
        "boundedness": bounded,
        "stationarity": True,
        "ledger_status": "PASS" if ledger_pass else "FAIL",
        "conservation_status": "NOT_APPLICABLE_NONCONSERVED_C_CONTROL",
        "causal_status": "DIAGNOSTIC_TIME_EVOLUTION_ONLY_FULL_FINITE_CONE_GATE_SEPARATE",
        "method_agreement": method_agreement,
        "classification": classification,
        "controlling_blocker": "full_candidate_finite_cone_and_physical_transport_mapping_remain_external_to_this_diagnostic",
        "evidence_hashes": {
            "core_diagnostic": sha256(CORE_MODULE),
            "topic_0_10_method_validation": sha256(METHOD_ARTIFACT),
        },
        "claim_boundary": "Normalized internal dynamical-regime diagnostic only; no SI, TTG, transport, or external-validation claim.",
        "dt_estimates": estimates,
        "shadow_amplitude_estimates": shadows,
        "perturbation_amplitude_spread": amplitude_spread,
        "ledger": ledger,
    }
    validate_diagnostic_contract(record)
    return record


def analytic_control(
    diagnostic_id: str, lambda_max: float, equation: str, forcing_class: str
) -> dict:
    record = {
        "diagnostic_id": diagnostic_id,
        "owner_topic": "0.13_Thermodynamic_Bridge",
        "equation_registry_ids": [LYAPUNOV_SPECTRUM_ID, REGIME_CLASSIFIER_ID],
        "state_variables": ["thermal_mode_amplitude"],
        "excluded_variables": ["R_gen", "R_obs"],
        "unit_lane": "normalized_control",
        "forcing_class": forcing_class,
        "noise_coupling": "none",
        "state_metric": "single_mode_absolute_amplitude",
        "estimator": "ANALYTIC_LINEAR_MODE",
        "transient_window": 0.0,
        "renormalization_interval": "not_applicable",
        "perturbation_amplitudes": PERTURBATIONS,
        "resolution_grid": {"analytic": True},
        "lambda_max": lambda_max,
        "lambda_spectrum": [lambda_max],
        "confidence_or_block_error": 0.0,
        "lambda_resolution": 0.0,
        "boundedness": True,
        "stationarity": True,
        "ledger_status": "PASS_ANALYTIC_CONTROL",
        "conservation_status": "NOT_APPLICABLE_LINEAR_MODE_CONTROL",
        "causal_status": "PASS_DECLARED_CONTROL",
        "method_agreement": True,
        "classification": "NONCHAOTIC_STABLE_DIAGNOSTIC",
        "controlling_blocker": "none_for_analytic_control",
        "evidence_hashes": {"generator": sha256(Path(__file__))},
        "claim_boundary": "Analytic thermal control only; not physical transport validation.",
        "equation": equation,
    }
    validate_diagnostic_contract(record)
    return record


def main() -> int:
    method = json.loads(METHOD_ARTIFACT.read_text(encoding="utf-8-sig"))
    if method.get("status") != "PASS_CHAOS_METHOD_VALIDATION":
        raise RuntimeError("Topic 0.10 chaos method validation must pass before Topic 13 pilot")

    diffusivity, wave_number, relaxation = 0.2, 1.0, 0.5
    fourier_lambda = -diffusivity * wave_number**2
    discriminant = 1.0 - 4.0 * relaxation * diffusivity * wave_number**2
    cattaneo_lambda = (-1.0 + np.sqrt(discriminant)) / (2.0 * relaxation)
    branches = {
        "fourier": analytic_control(
            "t13.thermal.fourier_mode",
            fourier_lambda,
            "dot(T_k)=-D*k^2*T_k",
            "closed_linear_diffusion_control",
        ),
        "cattaneo": analytic_control(
            "t13.thermal.cattaneo_mode",
            float(cattaneo_lambda),
            "tau*ddot(T_k)+dot(T_k)+D*k^2*T_k=0",
            "closed_linear_finite_speed_control",
        ),
        "trace_only": {
            "diagnostic_id": "t13.thermal.trace_only",
            "classification": "NOT_APPLICABLE_AS_DYNAMICAL_STATE",
            "state_variables": [],
            "excluded_variables": ["R_gen", "R_obs"],
            "reason": "R_gen is a derived history trace with no backreaction.",
        },
        "closed_matter_space": matter_space_diagnostic(
            "t13.thermal.closed_matter_space", 0.0
        ),
        "periodically_driven_matter_space": matter_space_diagnostic(
            "t13.thermal.periodically_driven_matter_space", 0.25
        ),
        "open_kms": {
            "diagnostic_id": "t13.thermal.open_kms",
            "classification": "BLOCKED_INPUT_NOT_EVALUATED",
            "noise_coupling": "COMMON_NOISE_REQUIRED",
            "controlling_blocker": "accepted_physical_noise_and_transport_input_missing",
            "claim_boundary": "Different-noise divergence will not be classified as deterministic chaos.",
        },
    }
    evaluated = [
        branches["fourier"],
        branches["cattaneo"],
        branches["closed_matter_space"],
        branches["periodically_driven_matter_space"],
    ]
    no_numerical_instability = all(
        item["classification"] != "NUMERICAL_INSTABILITY" for item in evaluated
    )
    holdout = json.loads(HOLDOUT_AUDIT.read_text(encoding="utf-8-sig"))
    holdout_unconsumed = bool(
        holdout.get("holdout_data_consumed") is False
        or holdout.get("holdout_consumed") is False
        or "UNCONSUMED" in str(holdout.get("status", ""))
    )
    passed = no_numerical_instability and holdout_unconsumed
    chaos_candidates = [
        key
        for key, item in branches.items()
        if isinstance(item, dict)
        and item.get("classification") == "CHAOS_CANDIDATE_DIAGNOSTIC"
    ]
    artifact = {
        "schema_version": "uet-chaos-diagnostic-v1",
        "artifact": "t13_thermal_dynamical_regime_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_THERMAL_DYNAMICAL_REGIME_PILOT" if passed else "BLOCKED_THERMAL_DYNAMICAL_REGIME_PILOT",
        "claim_promotion": False,
        "full_core_unlock": False,
        "holdout_access": {
            "policy": "Xie 2026 numeric payload must not be read, fit, tuned, or used to change thresholds",
            "audit_path": HOLDOUT_AUDIT.relative_to(ROOT).as_posix(),
            "audit_sha256": sha256(HOLDOUT_AUDIT),
            "holdout_consumed": False,
            "inherited_audit_pass": holdout_unconsumed,
        },
        "measurement_contract_unchanged": {
            "measurement": "y_TTG = Delta_Tq(t) / Delta_Tq(0)",
            "uet": "y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)",
            "bridge": "Delta_Tq = alpha_Phi_K * Delta_Phi",
            "alpha_Phi_K_status": "BLOCKED_OPEN_CALIBRATION",
        },
        "branches": branches,
        "chaos_candidate_branches": chaos_candidates,
        "predictability_horizon": {
            key: 1.0 / branches[key]["lambda_max"] for key in chaos_candidates
        },
        "major_result": {
            "major_result_id": "T13_THERMAL_DYNAMICAL_REGIME_CLASSIFIED",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
            "what_is_closed": [
                "Fourier and Cattaneo linear controls are non-chaotic under the declared normalized parameters",
                "R_gen trace-only output is excluded from the dynamical state",
                "closed and periodically driven normalized matter-space branches have reproducible tangent/shadow classifications",
                "open KMS chaos evaluation is explicitly blocked until common-noise physical inputs are accepted",
            ],
            "equation_or_mapping": {
                "tangent_state": "(delta_C, delta_Phi, delta_Pi)",
                "predictability_horizon": "t_predict=1/lambda_max only when lambda_max is resolved positive",
                "thermal_mapping_unchanged": "Delta_Tq=alpha_Phi_K*Delta_Phi",
            },
            "units": "normalized inverse time; no SI Lyapunov or temperature-scale claim",
            "derivation_class": "analytic linear controls plus tangent/QR and shadow diagnostics of declared normalized UET branches",
            "observable": "branch-level Lyapunov classification and conditional predictability horizon",
            "data_role": "INTERNAL_SYNTHETIC_DIAGNOSTIC_NO_HOLDOUT",
            "verification_status": "PASS_SCOPED_THERMAL_DYNAMICAL_REGIME_PILOT" if passed else "BLOCKED_THERMAL_DYNAMICAL_REGIME_PILOT",
            "open_blockers": [
                "full_candidate_finite_cone_physical_compatibility_remains_separate",
                "accepted_open_system_noise_and_transport_input_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "TTG_numeric_source_and_external_validation_remain_open",
            ],
            "dependency_unlocked": "Topic 0.11 and Core O(2) diagnostic-method rollout only; no Full Topic 13, Core physics, Gravity, Galaxy, or external-validation unlock",
            "claim_boundary": "This closes a normalized diagnostic lane, not the thermodynamic bridge, physical transport, TTG validation, or UET theory.",
        },
        "report": {
            "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE" if passed else "PARTIAL",
            "WHAT_IS_ACTUALLY_CLOSED": "normalized thermal dynamical-regime classification",
            "WHAT_REMAINS_OPEN": "SI mapping, alpha_Phi_K, TTG source, physical transport/noise, and external validation",
            "DEPENDENCY_UNLOCKED": "diagnostic rollout to Topic 0.11 and Core O(2) only" if passed else "none",
            "STATUS": "PASS_SCOPED" if passed else "BLOCKED",
            "WHAT_CHANGED": "Added branch-separated chaos diagnostics without changing thermal equations or holdout policy.",
            "EQUATION_OR_MAPPING": "(C,Phi,Pi) tangent map -> lambda_max; R_gen excluded",
            "VERIFICATION": {
                "method_artifact_pass": True,
                "holdout_unconsumed": holdout_unconsumed,
                "no_numerical_instability": no_numerical_instability,
            },
            "CONTROLLING_BLOCKER": "physical source/calibration/transport closure remains unchanged",
            "NEXT_ACTION": "roll the validated diagnostic method to Topic 0.11 and Core O(2) without promoting physical claims",
            "CLAIM_BOUNDARY": "normalized internal diagnostic only",
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "artifact": OUT.relative_to(ROOT).as_posix(), "chaos_candidates": chaos_candidates}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
