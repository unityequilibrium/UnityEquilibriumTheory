"""Audit the state-matched condensed SK/KMS/Kubo interface."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402
from docs.core.uet_o2_condensed_sk_kms_kubo_match import (  # noqa: E402
    CONDENSED_SK_KMS_KUBO_STATUS,
    CONDENSED_SK_KMS_THRESHOLD,
    condensed_sk_kms_kubo_match_contract,
    condensed_sk_kms_kubo_match_state,
)
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_condensed_sk_kms_kubo_match_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_condensed_sk_kms_kubo_match.py"
LOOP_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_condensed_loop_renormalized_vertex.py"
KUBO_ADMISSION = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_condensed_relative_flow_kubo_admission_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _config() -> FiniteTemperatureO2QuasiparticleConfig:
    return FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(
            matter=CovariantMatterConfig(
                matter_mass_sq=0.5,
                matter_quartic=0.8,
                response_coupling=0.3,
            ),
            response=CovariantResponseConfig(
                epsilon_nc=0.1,
                phi_equilibrium=0.0,
            ),
        ),
        quadrature_order=192,
        cutoff_factor=70.0,
    )


def main() -> int:
    state = condensed_sk_kms_kubo_match_state(
        0.20,
        1.28,
        0.15,
        _config(),
        reference_space_response=0.0,
    )
    contract = condensed_sk_kms_kubo_match_contract()
    admission = json.loads(KUBO_ADMISSION.read_text(encoding="utf-8-sig"))
    admission_value = float(admission["state"]["coefficient_record"]["value"])
    numeric_values = tuple(
        value
        for value in asdict(state).values()
        if isinstance(value, (int, float))
    )
    checks = {
        "branch_is_condensed": state.branch == "condensed",
        "state_matched_kubo_admission_is_pass": admission["status"].startswith("PASS_KUBO_MATCHED"),
        "zero_frequency_matches_admission_record": abs(
            state.zero_frequency_kubo_coefficient - admission_value
        ) / max(abs(admission_value), 1.0e-300) <= 1.0e-12,
        "retarded_pole_is_lower_half_plane": state.retarded_pole_imaginary_part < 0.0,
        "negative_time_support_is_zero": state.negative_time_support_residual == 0.0,
        "positive_time_kernel_is_visible": state.positive_time_kernel_value > 0.0,
        "spectral_psd_is_nonnegative": state.spectral_psd_minimum >= -1.0e-12,
        "retarded_reality_condition_holds": state.retarded_reality_residual <= CONDENSED_SK_KMS_THRESHOLD,
        "kms_ratio_holds": state.kms_residual <= CONDENSED_SK_KMS_THRESHOLD,
        "fdt_noise_holds": state.fdt_residual <= CONDENSED_SK_KMS_THRESHOLD,
        "zero_frequency_kubo_match_holds": state.zero_frequency_kubo_match_residual <= CONDENSED_SK_KMS_THRESHOLD,
        "entropy_is_nonnegative": state.entropy_production_at_unit_force >= 0.0,
        "numeric_state_is_finite": all(math.isfinite(float(value)) for value in numeric_values),
        "declared_channel_match_completed": state.declared_channel_sk_kms_match_completed,
        "full_retarded_self_energy_remains_open": not state.physical_retarded_self_energy_completed,
        "full_interacting_match_remains_outside_scope": not state.full_interacting_sk_kms_match_completed,
        "physical_kubo_scope_is_declared": state.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": state.numeric_alpha_phi_k_emitted is False,
        "no_parameter_fitting": state.parameter_fitting_performed is False,
        "no_target_or_holdout": state.target_data_used is False and state.xie_2026_accessed is False,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_is_derived": "not an independent state" in contract["unit_contract"]["R_gen"],
        "R_obs_is_separate": "observer record" in contract["unit_contract"]["R_obs"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = CONDENSED_SK_KMS_KUBO_STATUS if not failed else (
        "BLOCKED_T13_CONDENSED_SK_KMS_KUBO_MATCH"
    )
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_condensed_sk_kms_kubo_match.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_condensed_loop_renormalized_vertex.py", "sha256": sha256(LOOP_MODULE)},
        {"path": "docs/core/07_artifacts/topic13/t13_uet_o2_condensed_relative_flow_kubo_admission_audit.json", "sha256": sha256(KUBO_ADMISSION)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-condensed-sk-kms-kubo-match-v1",
        "artifact": "t13_uet_o2_condensed_sk_kms_kubo_match_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CONDENSED_SK_KMS_KUBO_MATCH_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "state-matched relative-projector retarded response tied to the admitted Kubo coefficient",
                "retarded lower-half-plane pole and causal time-domain sign",
                "spectral positive semidefiniteness, KMS ratio, FDT noise identity, and retarded reality",
                "zero-frequency Kubo match and nonnegative declared-channel entropy witness",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "full_finite_temperature_retarded_1PI_self_energy_missing",
                "unique_physical_renormalization_all_channel_match_missing",
                "complete_condensed_two_fluid_constitutive_tensor_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": (
                "state-matched condensed SK/KMS/FDT/Kubo channel only; full retarded self-energy, all-channel transport, SI, alpha, Core, Gravity, and external-validation dependencies remain blocked"
            ),
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(state)},
        "checks": checks,
        "failed_checks": failed,
        "declared_channel_sk_kms_match_completed": state.declared_channel_sk_kms_match_completed,
        "physical_retarded_self_energy_completed": state.physical_retarded_self_energy_completed,
        "full_interacting_sk_kms_match_completed": state.full_interacting_sk_kms_match_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "physical_kubo_scope": "declared condensed relative-flow natural-unit channel only",
        "numeric_alpha_phi_k_emitted": state.numeric_alpha_phi_k_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "full_finite_temperature_retarded_1PI_self_energy_missing",
        "next_controller": (
            "derive the finite-temperature condensed retarded self-energy and all-channel SK/KMS influence kernel; keep the admitted natural-unit Kubo lane separate from SI, alpha, source, and holdout gates"
        ),
        "claim_promotion": False,
        "full_core_unlock": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "used_for_fit": False,
            "used_for_tuning": False,
            "used_for_calibration": False,
            "used_for_threshold_adjustment": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "failed_checks": failed,
        "closure_level": artifact["major_result"]["closure_level"],
        "kms_residual": state.kms_residual,
        "fdt_residual": state.fdt_residual,
        "retarded_reality_residual": state.retarded_reality_residual,
        "spectral_psd_minimum": state.spectral_psd_minimum,
        "zero_frequency_kubo_match_residual": state.zero_frequency_kubo_match_residual,
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
