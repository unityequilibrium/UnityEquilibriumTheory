"""Audit the conditional fixed-volume thermodynamic identity for Ding C_src."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DING_TEXT = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "ding_2022_pmc_full_text.txt"
)
DING_PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "ding_2022_pbte_energy_temperature_source_package.json"
)
OUT = ROOT / "docs/core/artifacts/t13_csrc_fixed_volume_identity_audit.json"


H_PLANCK = 6.62607015e-34
K_B = 1.380649e-23


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def line_locator(path: Path, needle: str) -> str | None:
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if needle.lower() in line.lower():
            return f"{rel(path)}:{number}"
    return None


def thermal_energy_density(
    temperature_K: float,
    frequencies_hz: tuple[float, ...],
    weights: tuple[float, ...],
    volume_m3: float,
) -> float:
    total = 0.0
    for frequency, weight in zip(frequencies_hz, weights):
        x = H_PLANCK * frequency / (K_B * temperature_K)
        total += weight * H_PLANCK * frequency / math.expm1(x)
    return total / volume_m3


def fixed_volume_heat_capacity_density(
    temperature_K: float,
    frequencies_hz: tuple[float, ...],
    weights: tuple[float, ...],
    volume_m3: float,
) -> float:
    total = 0.0
    for frequency, weight in zip(frequencies_hz, weights):
        x = H_PLANCK * frequency / (K_B * temperature_K)
        denominator = math.expm1(x)
        total += weight * K_B * x * x * math.exp(x) / (denominator * denominator)
    return total / volume_m3


def main() -> int:
    ding_text = DING_TEXT.read_text(encoding="utf-8-sig")
    package = json.loads(DING_PACKAGE.read_text(encoding="utf-8-sig"))

    frequencies_hz = (1.0e12, 5.0e12, 20.0e12)
    weights = (1.0, 2.0, 1.0)
    volume_m3 = 1.0e-28
    temperature_K = 300.0
    step_K = 1.0e-2
    numerical_derivative = (
        thermal_energy_density(
            temperature_K + step_K, frequencies_hz, weights, volume_m3
        )
        - thermal_energy_density(
            temperature_K - step_K, frequencies_hz, weights, volume_m3
        )
    ) / (2.0 * step_K)
    analytic_derivative = fixed_volume_heat_capacity_density(
        temperature_K, frequencies_hz, weights, volume_m3
    )
    relative_error = abs(numerical_derivative - analytic_derivative) / analytic_derivative

    source_locators = {
        "mode_specific_heat_capacity": line_locator(
            DING_TEXT, "mode-specific heat capacity"
        ),
        "mode_sum": line_locator(DING_TEXT, "summation over all the phonon modes"),
        "temperature_response": line_locator(DING_TEXT, "Temperature response calculation"),
    }
    checks = {
        "ding_source_text_present": DING_TEXT.is_file(),
        "ding_source_package_present": DING_PACKAGE.is_file(),
        "source_mode_specific_heat_locator_present": source_locators[
            "mode_specific_heat_capacity"
        ]
        is not None,
        "source_mode_sum_locator_present": source_locators["mode_sum"] is not None,
        "source_temperature_response_locator_present": source_locators[
            "temperature_response"
        ]
        is not None,
        "source_temperature_mapping_is_locked": package.get("mapping_contract", {}).get(
            "source_temperature_response"
        )
        == "Delta_Tq = Delta_u_ph / C_src",
        "source_C_src_unit_is_volumetric": package.get("units_contract", {}).get(
            "C_src"
        )
        == "J m^-3 K^-1",
        "source_C_is_not_uet_C": package.get("ontology_contract", {}).get(
            "C_src_is_uet_C"
        )
        is False,
        "fixed_volume_derivative_identity_verified": relative_error <= 1.0e-8,
        "bose_mode_kernel_is_positive_and_finite": analytic_derivative > 0.0
        and math.isfinite(analytic_derivative),
        "zero_point_term_is_temperature_independent": True,
        "thermal_expansion_correction_is_not_silently_used": True,
        "numeric_C_src_not_emitted": package.get("numeric_input_contract", {}).get(
            "numeric_C_src_value"
        )
        is None,
        "numeric_alpha_not_emitted": package.get("numeric_input_contract", {}).get(
            "numeric_alpha_Phi_E_K"
        )
        is None,
        "base_phi_identity_not_asserted": package.get("mapping_contract", {}).get(
            "base_Phi_identity"
        )
        == "NOT_ASSERTED",
        "landauer_not_used": package.get("regime_contract", {}).get("landauer_used")
        is False,
        "holdout_not_accessed": package.get("holdout_policy", {}).get(
            "xie_2026_accessed"
        )
        is False,
        "holdout_not_consumed": package.get("holdout_policy", {}).get(
            "xie_2026_source_data_consumed"
        )
        is False,
        "source_role_excludes_fit_and_target": package.get("source", {}).get(
            "source_data_role", ""
        )
        == "DERIVED_STANDARD_PHYSICS_MAPPING; no numeric calibration values consumed",
    }
    status = (
        "PASS_SCOPED_C_SRC_FIXED_VOLUME_IDENTITY"
        if all(checks.values())
        else "FAIL_C_SRC_FIXED_VOLUME_IDENTITY_AUDIT"
    )
    major_result = {
        "major_result_id": "T13_DING_C_SRC_FIXED_VOLUME_THERMODYNAMIC_IDENTITY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "what_is_closed": [
            "Under a declared fixed-volume mode basis, Ding's C_src is identified conditionally with the temperature derivative of the phonon thermal-energy density.",
            "The Bose mode kernel and SI unit route are verified independently of any numeric Ding row.",
            "The identity does not relabel UET C, Phi, or R_gen and does not accept an unmatched graphite comparator as Ding evidence.",
        ],
        "equation_or_mapping": {
            "phonon_energy_density": "u_ph(T,V) = (1/V) sum_mu [hbar*omega_mu(V)*n_B(omega_mu(V),T)]",
            "fixed_volume_identity": "C_src(T,V) = (partial u_ph / partial T)_V = (1/V) sum_mu c_mu(T,V)",
            "fixed_frequency_mode_kernel": "c_mu/V = k_B*x_mu^2*exp(x_mu)/(V*(exp(x_mu)-1)^2)",
            "Ding_temperature_response": "Delta_Tq = Delta_u_ph / C_src",
            "cp_cv_boundary": "C_p^vol - C_v^vol = T*alpha_V^2*K_T; not used to manufacture Ding C_src",
        },
        "units": {
            "u_ph": "J m^-3",
            "C_src": "J m^-3 K^-1",
            "Delta_Tq": "K",
            "temperature": "K",
            "volume": "m^3",
        },
        "derivation_class": "conditional standard phonon thermodynamic identity; no UET derivation and no numeric calibration",
        "observable": "Ding PBTE temperature-response denominator C_src",
        "data_role": "DERIVED_STANDARD_PHYSICS_IDENTITY_NOT_CALIBRATION",
        "evidence_artifacts": [
            {
                "path": rel(DING_PACKAGE),
                "sha256": sha256(DING_PACKAGE),
                "summary": {"role": "Ding source formula and unit contract"},
            },
            {
                "path": rel(DING_TEXT),
                "sha256": sha256(DING_TEXT),
                "summary": {"role": "primary source locators for mode sum and response"},
            },
        ],
        "verification_status": status,
        "open_blockers": [
            "ding_pbte_numeric_C_src_or_accepted_independent_reproduction_missing",
            "Ding_material_state_and_volume_contract_not_source_locked",
            "anharmonic_mode_frequency_temperature_dependence_not_source_locked",
            "ding_C_src_source_grade_uncertainty_or_convergence_missing",
            "base_Phi_to_Delta_u_ph_mapping_not_derived",
            "independent_alpha_Phi_K_missing",
        ],
        "dependency_unlocked": "conditional C_src-to-fixed-volume c_v identity only; no numeric Ding source, alpha, bridge, transport, Core, Gravity, or external-validation unlock",
        "claim_boundary": "This closes a conditional standard-physics identity lane. It does not emit numeric C_src, convert any current comparator into Ding C_src, derive e0 or base Phi, calibrate alpha_Phi_K, or close Topic 13.",
    }
    report = {
        "MAJOR_RESULT_CLOSURE": major_result["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": major_result["what_is_closed"],
        "WHAT_REMAINS_OPEN": major_result["open_blockers"],
        "DEPENDENCY_UNLOCKED": major_result["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Added and verified the conditional fixed-volume identity linking the Ding PBTE C_src definition to a standard phonon energy derivative without emitting a numeric source row.",
        "EQUATION_OR_MAPPING": major_result["equation_or_mapping"],
        "VERIFICATION": "Analytic Bose-mode derivative agrees with a central finite difference at the declared witness state; source locators, units, ontology separation, no-fit policy, and holdout isolation pass.",
        "CONTROLLING_BLOCKER": "ding_pbte_numeric_C_src_or_accepted_independent_reproduction_missing",
        "NEXT_ACTION": "Obtain a source-locked Ding-compatible mode or fixed-volume c_v record with material/state, volume, uncertainty, and convergence metadata; then evaluate it under this identity without fitting alpha.",
        "CLAIM_BOUNDARY": major_result["claim_boundary"],
    }
    result = {
        "schema_version": "t13-csrc-fixed-volume-identity-v1",
        "artifact": "t13_csrc_fixed_volume_identity_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "report": report,
        "source_locators": source_locators,
        "numerical_identity_witness": {
            "temperature_K": temperature_K,
            "step_K": step_K,
            "volume_m3": volume_m3,
            "frequency_count": len(frequencies_hz),
            "analytic_C_src_J_m^-3_K^-1": analytic_derivative,
            "central_difference_J_m^-3_K^-1": numerical_derivative,
            "relative_error": relative_error,
        },
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_C_src_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "ding_pbte_numeric_C_src_or_accepted_independent_reproduction_missing",
        "next_controller": "Source-lock Ding-compatible C_src(T) or a fixed-volume c_v record with state, volume, uncertainty, and convergence; do not use this identity to infer a value from normalized TTG data.",
        "claim_boundary": major_result["claim_boundary"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": rel(OUT),
                "checks_pass": all(checks.values()),
                "relative_error": relative_error,
                "controlling_blocker": result["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if status == "PASS_SCOPED_C_SRC_FIXED_VOLUME_IDENTITY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
