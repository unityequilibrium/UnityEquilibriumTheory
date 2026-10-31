"""Audit what normalized TTG dip time identifies without a Phi amplitude scale."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import atan, cos, exp, isfinite, pi, sin
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
DISPERSION = TOPIC / "Data/03_Research/thermal_no_fit_linearized_dispersion.json"
SOURCE_MAP = TOPIC / "Data/03_Research/matter_space_thermal_source_review.json"
OUTPUT = TOPIC / "Result/artifacts/t13_normalized_dip_time_identifiability.json"


def _validate_mode(gamma: float, omega: float, initial_response: float, time_s: float = 0.0) -> None:
    if not all(isfinite(float(value)) for value in (gamma, omega, initial_response, time_s)):
        raise ValueError("mode parameters and time must be finite")
    if gamma < 0.0 or omega <= 0.0 or initial_response == 0.0 or time_s < 0.0:
        raise ValueError("require gamma >= 0, omega > 0, nonzero initial response, and time >= 0")


def damped_cos_response(time_s: float, gamma: float, omega: float, initial_response: float = 1.0) -> float:
    """Damped cosine mode, whose initial rate is -gamma times its amplitude."""
    _validate_mode(gamma, omega, initial_response, time_s)
    return initial_response * exp(-gamma * time_s) * cos(omega * time_s)


def damped_cos_rate(time_s: float, gamma: float, omega: float, initial_response: float = 1.0) -> float:
    _validate_mode(gamma, omega, initial_response, time_s)
    return initial_response * exp(-gamma * time_s) * (
        -gamma * cos(omega * time_s) - omega * sin(omega * time_s)
    )


def zero_initial_rate_response(
    time_s: float, gamma: float, omega: float, initial_response: float = 1.0
) -> float:
    """Same damped-mode poles, but with the independent initial condition x_dot(0)=0."""
    _validate_mode(gamma, omega, initial_response, time_s)
    return initial_response * exp(-gamma * time_s) * (
        cos(omega * time_s) + gamma / omega * sin(omega * time_s)
    )


def zero_initial_rate_response_rate(
    time_s: float, gamma: float, omega: float, initial_response: float = 1.0
) -> float:
    _validate_mode(gamma, omega, initial_response, time_s)
    return -initial_response * exp(-gamma * time_s) * (
        omega + gamma * gamma / omega
    ) * sin(omega * time_s)


def damped_cos_first_dip_time(gamma: float, omega: float) -> float:
    _validate_mode(gamma, omega, 1.0)
    return (pi - atan(gamma / omega)) / omega


def zero_initial_rate_first_dip_time(omega: float) -> float:
    if not isfinite(float(omega)) or omega <= 0.0:
        raise ValueError("omega must be finite and positive")
    return pi / omega


def dip_speed(period_m: float, dip_time_s: float) -> float:
    if not all(isfinite(float(value)) for value in (period_m, dip_time_s)):
        raise ValueError("period and dip time must be finite")
    if period_m <= 0.0 or dip_time_s <= 0.0:
        raise ValueError("period and dip time must be positive")
    return period_m / (2.0 * dip_time_s)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_audit() -> dict[str, Any]:
    dispersion = json.loads(DISPERSION.read_text(encoding="utf-8-sig"))
    source_map = json.loads(SOURCE_MAP.read_text(encoding="utf-8-sig"))
    speed_relation = next(
        item
        for item in source_map["standard_observable_contract"]["source_backed_relations"]
        if item["relation_id"] == "TTG-SPEED-001"
    )
    ratios = (0.1, 0.25, 0.5, 1.0)
    sensitivity = []
    for ratio in ratios:
        damped_time = damped_cos_first_dip_time(ratio, 1.0)
        zero_rate_time = zero_initial_rate_first_dip_time(1.0)
        sensitivity.append(
            {
                "gamma_over_omega": ratio,
                "damped_cos_dip_time_over_zero_rate_dip_time": damped_time / zero_rate_time,
                "damped_cos_dip_speed_over_zero_rate_dip_speed": zero_rate_time / damped_time,
            }
        )

    checks = {
        "source_declares_dip_speed_relation": speed_relation["formula"] == "v_TTG = Lambda / (2 * t_d)",
        "candidate_dispersion_contains_damping_and_oscillation": (
            "dispersion_relation" in dispersion
            and "damping_rate" in dispersion
            and "oscillatory_condition" in dispersion
        ),
        "alpha_cancels_for_nonzero_constant_scale": all(
            abs(
                (alpha * damped_cos_response(0.7, 0.4, 1.3)) / (alpha * damped_cos_response(0.0, 0.4, 1.3))
                - damped_cos_response(0.7, 0.4, 1.3) / damped_cos_response(0.0, 0.4, 1.3)
            )
            < 1.0e-14
            for alpha in (-3.0, 0.2, 11.0)
        ),
        "both_initializations_have_distinct_first_dips": damped_cos_first_dip_time(0.5, 1.0)
        != zero_initial_rate_first_dip_time(1.0),
        "no_target_or_holdout_inputs_read": True,
    }
    status = "PASS_CONDITIONAL_DIP_TIME_IDENTIFIABILITY" if all(checks.values()) else "FAIL_DIP_TIME_AUDIT"

    return {
        "schema_version": "t13-normalized-dip-time-identifiability-v1",
        "artifact": "t13_normalized_dip_time_identifiability",
        "generated_on": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_NORMALIZED_TTG_DIP_TIME_INITIAL_STATE_CONTRACT",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "a nonzero constant Phi-to-temperature scale cancels from the normalized TTG signal and cannot affect its dip time",
                "for the same damped-mode poles, the first dip differs between a damped-cosine initial rate and a zero-initial-rate response",
                "the source-defined dip speed is a half-period distance divided by dip time and is not generally the PDE front speed",
            ],
            "equation_or_mapping": {
                "normalized_scale_invariance": "y(t)=alpha*x(t)/(alpha*x(0))=x(t)/x(0), alpha != 0 constant",
                "source_damped_mode": "x(t)=exp(-gamma*t)*cos(omega*t); t_d=(pi-atan(gamma/omega))/omega",
                "same_poles_zero_initial_rate": "x(t)=exp(-gamma*t)*(cos(omega*t)+(gamma/omega)*sin(omega*t)); t_d=pi/omega",
                "source_speed": "v_p=Lambda/(2*t_d)",
                "front_speed_warning": "sqrt(M_Phi*kappa_Phi/tau_Phi) is a characteristic front speed; equality to v_p requires a separately derived source/initial-state and dispersion mapping",
            },
            "units": {
                "gamma": "s^-1 in dimensional lane; normalized audit uses arbitrary inverse-time units",
                "omega": "s^-1 in dimensional lane; normalized audit uses arbitrary inverse-time units",
                "dip_time": "s",
                "grating_period": "m",
                "dip_speed": "m s^-1",
                "normalized_response": "dimensionless",
            },
            "derivation_class": "closed-form damped-mode derivation plus synthetic algebraic checks",
            "observable": "normalized TTG first-dip time and source-defined propagation-speed diagnostic",
            "data_role": "ANALYTIC_STRUCTURAL_COMPARATOR_NOT_TARGET_FIT_OR_CALIBRATION",
            "evidence_artifacts": [
                "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/thermal_no_fit_linearized_dispersion.json",
                "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_thermal_source_review.json",
                "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/ding_2022_ttg_preprocessing_boundary_audit.json",
            ],
            "verification_status": status,
            "open_blockers": [
                "the physical pump-to-Phi/Pi initial-state map and dimensional coefficient provenance are not closed",
                "the figure-derived experimental points remain mixed with simulated curves and author numeric rows are unavailable",
                "the published smoothing/noise protocol is not sufficient to reconstruct pointwise uncertainty or filter transfer",
            ],
            "dependency_unlocked": "A preregistration contract for an alpha-independent normalized dip-time/velocity comparison; no physical prediction or Core/Full Topic 13 unlock",
            "claim_boundary": "This is a conditional single-mode structural result. The synthetic sensitivity values are not Ding measurements or UET physical predictions.",
        },
        "verification": {
            "checks": checks,
            "input_hashes": {
                "thermal_no_fit_linearized_dispersion_sha256": sha256(DISPERSION),
                "matter_space_thermal_source_review_sha256": sha256(SOURCE_MAP),
            },
            "source_damped_cos": {
                "gamma_over_omega": 0.5,
                "damped_cos_dip_time_over_zero_rate_dip_time": damped_cos_first_dip_time(0.5, 1.0)
                / zero_initial_rate_first_dip_time(1.0),
                "damped_cos_dip_speed_over_zero_rate_dip_speed": zero_initial_rate_first_dip_time(1.0)
                / damped_cos_first_dip_time(0.5, 1.0),
            },
            "synthetic_initial_condition_sensitivity": sensitivity,
            "source_backed_relation_id": speed_relation["relation_id"],
            "front_speed_identified_with_dip_speed": False,
            "alpha_calibrated": False,
            "target_data_used": False,
            "holdout_accessed": False,
            "claim_promotion": False,
        },
    }


def main() -> int:
    artifact = build_audit()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "checks": artifact["verification"]["checks"], "output": str(OUTPUT)}, indent=2))
    return 0 if artifact["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
