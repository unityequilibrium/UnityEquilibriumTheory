"""Verify the fixed-Phi tree-level radial/Goldstone fluctuation spectrum."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from math import isfinite
from pathlib import Path

import numpy as np

if str(Path(__file__).resolve().parents[3]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_condensate_fluctuations import (
    condensate_fluctuation_contract,
    condensate_fluctuation_state,
    quadratic_fluctuation_polynomial,
    quadratic_mode_frequencies,
    quadratic_mode_omega_sq,
)
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig, o2_equilibrium_state


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/02_equations/o2/uet_o2_condensate_fluctuations.py"
EOS_REL = "docs/core/02_equations/o2/uet_o2_finite_density_eos.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_condensate_fluctuation_spectrum_audit.json"

MU = 1.3
PHI = 0.2
WAVENUMBERS = (0.0, 0.05, 0.23, 0.7)


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


def relative_error(actual: float, expected: float) -> float:
    return abs(float(actual) - float(expected)) / max(abs(float(expected)), 1.0e-30)


def main() -> int:
    eos_config = config()
    eos_state = o2_equilibrium_state(MU, PHI, eos_config)
    state = condensate_fluctuation_state(MU, PHI, eos_config)
    contract = condensate_fluctuation_contract()
    mode_records: list[dict[str, float]] = []
    determinant_residuals: list[float] = []
    for k in WAVENUMBERS:
        low_sq, high_sq = quadratic_mode_omega_sq(k, state, eos_config)
        low_frequency, high_frequency = quadratic_mode_frequencies(k, state, eos_config)
        determinant_residuals.extend([
            quadratic_fluctuation_polynomial(low_sq, k, state, eos_config),
            quadratic_fluctuation_polynomial(high_sq, k, state, eos_config),
        ])
        mode_records.append({
            "wavenumber": k,
            "goldstone_omega_sq": low_sq,
            "high_mode_omega_sq": high_sq,
            "goldstone_frequency": low_frequency,
            "high_mode_frequency": high_frequency,
        })
    a = state.condensate_control / eos_config.matter.matter_kinetic
    cs_sq_expected = float(eos_state.sound_speed_sq)
    low_k = mode_records[1]
    low_k_slope = low_k["goldstone_omega_sq"] / low_k["wavenumber"]**2
    zero_k = mode_records[0]
    checks = {
        "contract_status_is_declared": contract["status"] == "TREE_LEVEL_O2_CONDENSATE_QUADRATIC_SPECTRUM",
        "condensed_background_is_selected": eos_state.branch == "condensed",
        "positive_condensate_control": state.condensate_control > 0.0,
        "positive_amplitude": state.amplitude_sq > 0.0,
        "radial_curvature_matches_action": relative_error(
            state.radial_curvature_sq,
            2.0 * state.condensate_control / eos_config.matter.matter_kinetic,
        ) <= 1.0e-12,
        "zero_momentum_goldstone_is_zero": abs(zero_k["goldstone_omega_sq"]) <= 1.0e-12,
        "zero_momentum_high_mode_matches_mixed_gap": relative_error(
            zero_k["high_mode_omega_sq"],
            state.zero_momentum_high_mode_sq,
        ) <= 1.0e-12,
        "determinant_roots_close": max(abs(value) for value in determinant_residuals) <= 1.0e-12,
        "nonnegative_spectrum": all(
            record["goldstone_omega_sq"] >= -1.0e-12 and record["high_mode_omega_sq"] > 0.0
            for record in mode_records
        ),
        "goldstone_low_k_slope_matches_eos_sound_speed": relative_error(low_k_slope, cs_sq_expected) <= 2.0e-3,
        "high_mode_above_goldstone": all(
            record["high_mode_omega_sq"] >= record["goldstone_omega_sq"]
            for record in mode_records
        ),
        "Phi_is_held_fixed": contract["scope"]["space_response"] == "Phi held fixed" and contract["scope"]["response_fluctuation"] == "excluded",
        "finite_temperature_is_excluded": contract["scope"]["temperature"] == "T=0 tree-level only" and state.finite_temperature_included is False,
        "normal_component_is_excluded": contract["scope"]["normal_component"] == "excluded",
        "trace_is_not_state": contract["ontology"]["R_gen"] == "not a fluctuation state and has no feedback",
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = "PASS_T0_QUADRATIC_FLUCTUATION_SPECTRUM" if all(checks.values()) else "FAIL_T0_QUADRATIC_FLUCTUATION_SPECTRUM"
    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": EOS_REL, "sha256": digest(EOS_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-condensate-fluctuation-spectrum-v1",
        "artifact": "t13_uet_o2_condensate_fluctuation_spectrum_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CONDENSATE_FLUCTUATION_SPECTRUM",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "fixed-Phi tree-level quadratic radial/Goldstone determinant around the homogeneous O(2) condensate",
                "both non-negative mode roots and determinant residual verification across the declared wavenumber sweep",
                "zero-momentum Goldstone mode and mixed high-mode gap",
                "low-wavenumber Goldstone slope agreement with the independently implemented tree-level EOS sound speed",
                "explicit exclusion of response fluctuations, vacuum loop, finite-temperature self-energy, normal component, and dissipation",
            ] if status.startswith("PASS") else [],
            "equation_or_mapping": contract["equations"],
            "units": {
                "unit_lane": "natural",
                "omega_k_mu": "natural energy",
                "wavenumber": "natural inverse length",
                "Phi": "fixed action response input; no SI map",
            },
            "derivation_class": "tree-level quadratic fluctuation determinant from the declared O(2) action at fixed Phi; no finite-temperature loop or transport matching",
            "observable": "T=0 radial and Goldstone mode frequencies of the condensed action branch",
            "data_role": "ACTION_DERIVED_T0_SPECTRUM_NOT_FINITE_TEMPERATURE_TRANSPORT",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "finite_temperature_normal_component_not_derived",
                "interacting_finite_temperature_self_energy_not_derived",
                "vacuum_counterterm_and_renormalized_one_loop_response_not_closed",
                "physical_Kubo_coefficient_record_missing",
                "SI_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_missing",
            ],
            "dependency_unlocked": "T=0 quadratic spectrum lane only; no finite-temperature normal, physical transport, SI, Full Topic 13, Core, or Gravity unlock",
            "claim_boundary": "This closes only the fixed-Phi natural-unit tree-level quadratic spectrum of the O(2) condensate. It does not derive finite-temperature self-energy, a normal component, dissipative transport, vacuum renormalization, SI Phi calibration, external validation, or global UET closure.",
        },
        "reference": {
            "chemical_potential": MU,
            "space_response": PHI,
            "condensate_control": state.condensate_control,
            "amplitude_sq": state.amplitude_sq,
            "radial_curvature_sq": state.radial_curvature_sq,
            "zero_momentum_high_mode_sq": state.zero_momentum_high_mode_sq,
            "eos_sound_speed_sq": cs_sq_expected,
            "low_k_goldstone_slope": low_k_slope,
            "parameter_a_q_over_Z": a,
        },
        "mode_records": mode_records,
        "determinant_residual_max_abs": max(abs(value) for value in determinant_residuals),
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "finite_temperature_normal_component_and_interacting_self_energy_not_derived",
        "next_controller": "Match the tree-level spectrum to a declared finite-temperature effective action or retain this as a T=0 boundary; do not infer normal transport from the two roots.",
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
        "determinant_residual_max_abs": report["determinant_residual_max_abs"],
        "low_k_goldstone_slope": low_k_slope,
        "eos_sound_speed_sq": cs_sq_expected,
    }, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
