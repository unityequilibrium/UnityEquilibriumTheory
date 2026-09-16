from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_one_loop_retarded_self_energy_no_go import (  # noqa: E402
    ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO_STATUS,
    one_loop_retarded_self_energy_no_go_contract,
    one_loop_retarded_self_energy_no_go_state,
)
from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_retarded_self_energy_no_go_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_one_loop_retarded_self_energy_no_go.py"
ACTION_MODULE = ROOT / "docs/core/02_equations/covariant/uet_covariant_matter.py"
CHARGED_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_density_charged_vertex.py"


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
            response=CovariantResponseConfig(epsilon_nc=0.1),
        )
    )


def main() -> int:
    state = one_loop_retarded_self_energy_no_go_state(0.22, 0.25, 0.15, _config())
    contract = one_loop_retarded_self_energy_no_go_contract()
    checks = {
        "one_loop_self_energy_is_completed": state.one_loop_retarded_self_energy_completed,
        "thermal_tadpole_is_finite": state.tadpole_finite and state.thermal_tadpole > 0.0,
        "self_energy_is_real": state.imaginary_part_maximum == 0.0 and all(value == 0.0 for value in state.self_energy_imaginary),
        "one_loop_spectral_density_vanishes": state.spectral_density_maximum == 0.0 and all(value == 0.0 for value in state.self_energy_spectral_density),
        "external_frequency_independence_is_explicit": state.external_frequency_independence_residual == 0.0,
        "two_loop_or_microscopic_completion_is_required": state.two_loop_sunset_or_microscopic_source_required,
        "physical_dissipative_completion_remains_open": not state.dissipative_self_energy_completed,
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_or_holdout": not state.target_data_used and not state.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["ontology"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["ontology"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["ontology"]["R_obs"],
        "no_go_boundary_is_explicit": contract["excluded"]["physical_retarded_self_energy"] and contract["excluded"]["physical_kubo_coefficient"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO_STATUS if not failed else (
        "BLOCKED_ACTION_DERIVED_ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO"
    )
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_one_loop_retarded_self_energy_no_go.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/covariant/uet_covariant_matter.py", "sha256": sha256(ACTION_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_finite_density_charged_vertex.py", "sha256": sha256(CHARGED_MODULE)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-one-loop-retarded-self-energy-no-go-v1",
        "artifact": "t13_uet_o2_one_loop_retarded_self_energy_no_go_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if not failed else "OPEN",
            "what_is_closed": [
                "the local quartic one-loop retarded correction is a real, external-frequency-independent tadpole",
                "its dissipative spectral density is identically zero at one loop",
                "a two-loop sunset or source-locked microscopic open-system branch is required for nonzero dissipation",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "two_loop_sunset_or_microscopic_retarded_self_energy_missing",
                "physical_Kubo_coefficient_missing",
                "entropy_current_heat_flux_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "one-loop dissipation no-go only; it does not unlock physical transport, SI, alpha, Core, Gravity, or external validation",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": state.__dict__,
        "checks": checks,
        "failed_checks": failed,
        "one_loop_retarded_self_energy_completed": state.one_loop_retarded_self_energy_completed,
        "dissipative_self_energy_completed": state.dissipative_self_energy_completed,
        "two_loop_sunset_or_microscopic_source_required": state.two_loop_sunset_or_microscopic_source_required,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "two_loop_sunset_or_microscopic_retarded_self_energy_missing",
        "next_controller": "derive the two-loop sunset self-energy or obtain a state-matched microscopic retarded correlator; do not promote the zero one-loop spectral part to a transport prediction",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO",
        "closure_level": "CLOSED_AS_NO_GO" if not failed else "OPEN",
        "data_role": state.data_role,
        "audit": {
            "path": "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_retarded_self_energy_no_go_audit.json",
            "summary": {
                "status": status,
                "major_result_id": "T13_UET_O2_ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO",
                "closure_level": "CLOSED_AS_NO_GO" if not failed else "OPEN",
            },
        },
        "open_blockers": [
            "two_loop_sunset_or_microscopic_retarded_self_energy_missing",
            "physical_Kubo_coefficient_missing",
            "entropy_current_heat_flux_and_dissipative_balance_missing",
            "dimensional_Phi_to_thermal_observable_map_missing",
            "alpha_Phi_K_independent_calibration_missing",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ],
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": failed, "artifact": str(OUT.relative_to(ROOT))}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
