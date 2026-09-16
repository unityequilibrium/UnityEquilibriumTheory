"""Audit the local SK contact vertex to charged transition-kernel match."""

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

from docs.core.uet_o2_contact_sk_transition_vertex_match import (  # noqa: E402
    contact_sk_transition_vertex_match_contract,
    contact_sk_transition_vertex_match_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_contact_sk_transition_vertex_match_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_contact_sk_transition_vertex_match.py"
ACTION = ROOT / "docs/core/02_equations/o2/uet_o2_interacting_sk_kms_action.py"
KERNEL = ROOT / "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = contact_sk_transition_vertex_match_state(0.35, 0.1, 0.8)
    contract = contact_sk_transition_vertex_match_contract()
    checks = {
        "state_is_finite": all(
            value == value and abs(float(value)) < float("inf")
            for value in asdict(state).values()
            if isinstance(value, (int, float))
        ),
        "same_declared_quartic_coupling": state.contact_vertex_amplitude == state.quartic_coupling,
        "r3a_coefficient_is_action_value": state.r3a_vertex_coefficient == state.quartic_coupling,
        "ra3_coefficient_is_action_value": abs(state.ra3_vertex_coefficient - state.quartic_coupling / 4.0) <= 1.0e-15,
        "contact_cross_section_match": state.cross_section_match_residual <= 1.0e-15,
        "charged_detailed_balance": state.max_channel_detailed_balance_residual <= 1.0e-12,
        "channel_invariants_close": state.max_channel_invariant_residual <= 1.0e-12,
        "local_contour_expansion_close": state.contour_ra_expansion_residual <= 1.0e-12,
        "charged_particle_kms_close": state.charged_particle_kms_residual <= 1.0e-12,
        "charged_antiparticle_kms_close": state.charged_antiparticle_kms_residual <= 1.0e-12,
        "off_shell_self_energy_remains_open": not state.microscopic_offshell_self_energy_completed,
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
        "PASS_ACTION_MATCHED_CONTACT_SK_TRANSITION_VERTEX_LANE"
        if all(checks.values())
        else "FAIL_T13_CONTACT_SK_TRANSITION_VERTEX_LANE"
    )
    open_blockers = [
        "loop_renormalized_microscopic_vertex_missing",
        "complete_off_shell_finite_temperature_1pi_self_energy_missing",
        "physical_current_correlator_kubo_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    report = {
        "schema_version": "t13-contact-sk-transition-vertex-match-audit-v1",
        "artifact": "t13_uet_o2_contact_sk_transition_vertex_match_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CONTACT_SK_TRANSITION_VERTEX_MATCH_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "local O(2) SK r/a quartic vertex content for the declared contact channel",
                "contact amplitude M_22=lambda to the exact-kinematic kernel cross-section normalization",
                "charged exact-kinematic channel detailed balance and particle/antiparticle KMS interface",
            ],
            "what_remains_open": open_blockers,
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": [
                {"path": "docs/core/02_equations/o2/uet_o2_contact_sk_transition_vertex_match.py", "sha256": sha256(MODULE)},
                {"path": "docs/core/02_equations/o2/uet_o2_interacting_sk_kms_action.py", "sha256": sha256(ACTION)},
                {"path": "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py", "sha256": sha256(KERNEL)},
            ],
            "verification_status": status,
            "open_blockers": open_blockers,
            "dependency_unlocked": "declared local contact SK-to-transition-kernel normalization and charged detailed-balance interface only; no physical retarded self-energy or Kubo unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "checks": checks,
        "contract": contract,
        "state": {"reference": asdict(state)},
        "controlling_blocker": "loop_renormalized_off_shell_self_energy_and_physical_current_kubo_match_missing",
        "next_controller": "match the loop-renormalized charged off-shell retarded self-energy and current correlator to the SK/KMS construction",
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "failed_checks": [key for key, value in checks.items() if not value],
        "cross_section_match_residual": state.cross_section_match_residual,
        "max_channel_detailed_balance_residual": state.max_channel_detailed_balance_residual,
    }, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
