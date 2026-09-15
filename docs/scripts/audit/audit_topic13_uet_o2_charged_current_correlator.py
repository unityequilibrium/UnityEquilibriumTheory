"""Audit the action-matched charged current-correlator interface for Topic 13."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_charged_current_correlator import (  # noqa: E402
    charged_current_correlator_contract,
    charged_current_correlator_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_charged_current_correlator_audit.json"
MODULE = ROOT / "docs/core/uet_o2_charged_current_correlator.py"
CONTINUUM = ROOT / "docs/core/uet_o2_continuum_collision_operator.py"
CONTACT = ROOT / "docs/core/uet_o2_contact_sk_transition_vertex_match.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = charged_current_correlator_state(0.35, 0.1, 0.8)
    contract = charged_current_correlator_contract()
    checks = {
        "state_is_finite": all(
            value == value and abs(float(value)) < float("inf")
            for value in asdict(state).values()
            if isinstance(value, (int, float))
        ),
        "current_source_formula_matches": state.current_source_formula_residual <= 1.0e-12,
        "current_source_is_Ward_projected": state.current_ward_projection_residual <= 1.0e-12,
        "charge_and_momentum_invariants_are_conserved": state.collision_conservation_residual <= 1.0e-12,
        "operator_is_symmetric": state.operator_symmetry_residual <= 1.0e-12,
        "operator_is_positive_semidefinite": state.positive_semidefinite_min_eigenvalue >= -1.0e-10,
        "five_conserved_zero_modes_are_present": state.null_mode_count == 5,
        "dc_current_response_is_positive": state.dc_current_response > 0.0,
        "retarded_response_is_finite": all(
            abs(float(value)) < float("inf")
            for value in (*state.retarded_response_real, *state.retarded_response_imag)
        ),
        "positive_frequency_spectral_density": all(value >= -1.0e-12 for value in state.spectral_density),
        "charged_contact_cross_section_match": state.contact_cross_section_match_residual <= 1.0e-15,
        "charged_contact_detailed_balance": state.contact_detailed_balance_residual <= 1.0e-12,
        "kms_ratio_matches": state.kms_ratio_max_residual <= 1.0e-12,
        "fdt_noise_matches": state.fdt_max_residual <= 1.0e-12,
        "entropy_witness_is_positive": state.entropy_production_witness > 0.0,
        "finite_cutoff_boundary_is_declared": state.finite_cutoff_boundary_declared,
        "off_shell_self_energy_remains_open": not state.microscopic_offshell_self_energy_completed,
        "microscopic_current_vertex_remains_open": not state.microscopic_current_vertex_completed,
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_or_holdout": not state.target_data_used and not state.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
    }
    status = (
        "PASS_ACTION_MATCHED_CHARGED_CURRENT_CORRELATOR_LANE"
        if all(checks.values())
        else "FAIL_T13_CHARGED_CURRENT_CORRELATOR_LANE"
    )
    open_blockers = [
        "continuum_limit_missing",
        "loop_renormalized_off_shell_self_energy_missing",
        "microscopic_current_vertex_and_physical_kubo_match_missing",
        "finite_temperature_two_fluid_completion_missing",
        "covariant_entropy_current_heat_flux_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    report = {
        "schema_version": "t13-charged-current-correlator-audit-v1",
        "artifact": "t13_uet_o2_charged_current_correlator_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CHARGED_CURRENT_CORRELATOR_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "charged quasiparticle current source b_Jx=q_s*(p_x/E_s)*sqrt(w_s)",
                "Ward/conservation projection of the current source against charge and four-momentum zero modes",
                "finite-cutoff retarded charged current-current correlator",
                "charged contact-SK normalization linkage to the action-derived transition kernel",
                "charged KMS/FDT ratios and positive entropy-production witness",
            ],
            "what_remains_open": open_blockers,
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": [
                {"path": "docs/core/uet_o2_charged_current_correlator.py", "sha256": sha256(MODULE)},
                {"path": "docs/core/uet_o2_continuum_collision_operator.py", "sha256": sha256(CONTINUUM)},
                {"path": "docs/core/uet_o2_contact_sk_transition_vertex_match.py", "sha256": sha256(CONTACT)},
            ],
            "verification_status": status,
            "open_blockers": open_blockers,
            "dependency_unlocked": "named charged finite-cutoff current-correlator/KMS interface only; no continuum, microscopic, physical Kubo, SI, or Full Topic 13 unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "checks": checks,
        "contract": contract,
        "state": {"reference": asdict(state)},
        "controlling_blocker": "loop_renormalized_off_shell_self_energy_and_microscopic_current_vertex_match_missing",
        "next_controller": "derive a charged finite-temperature off-shell retarded self-energy and match its current vertex/correlator to the SK/KMS construction before physical Kubo admission",
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                "failed_checks": [key for key, value in checks.items() if not value],
                "dc_current_response": state.dc_current_response,
                "kms_ratio_max_residual": state.kms_ratio_max_residual,
                "fdt_max_residual": state.fdt_max_residual,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
