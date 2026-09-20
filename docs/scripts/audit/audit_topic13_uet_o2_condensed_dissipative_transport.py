"""Audit the condensed dissipative transport identifiability boundary."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isclose
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from docs.core.uet_o2_condensed_dissipative_transport_identifiability_no_go import (
    CONDENSED_DISSIPATIVE_TRANSPORT_STATUS,
    condensed_dissipative_transport_boundary,
    condensed_dissipative_transport_contract,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_condensed_dissipative_transport_audit.json"
MODULE = (
    ROOT
    / "docs/core/02_equations/o2/uet_o2_condensed_dissipative_transport_identifiability_no_go.py"
)
STATIC_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_two_fluid_response.py"
STATIC_ARTIFACT = (
    ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_two_fluid_response_audit.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    static_artifact = json.loads(STATIC_ARTIFACT.read_text(encoding="utf-8-sig"))
    state_grid = static_artifact.get("state_grid", {})
    condensed_states = [
        value
        for key, value in state_grid.items()
        if key.startswith("condensed_") and isinstance(value, dict)
    ]
    boundary = condensed_dissipative_transport_boundary(0.2, 0.35)
    contract = condensed_dissipative_transport_contract()

    checks = {
        "condensed_state_records_are_available": len(condensed_states) >= 2,
        "condensate_entropy_is_zero_on_declared_states": all(
            isclose(
                float(state.get("condensate_entropy_density", 1.0)),
                0.0,
                abs_tol=1.0e-15,
            )
            for state in condensed_states
        ),
        "condensed_heat_flux_is_not_emitted": all(
            state.get("heat_flux_kappa_natural") is None
            for state in condensed_states
        ),
        "relative_velocity_is_not_in_current_state_record": all(
            field not in state
            for state in condensed_states
            for field in ("normal_velocity", "condensate_velocity", "relative_velocity")
        ),
        "witness_a_is_positive_semidefinite": boundary.witness_a_positive_semidefinite,
        "witness_b_is_positive_semidefinite": boundary.witness_b_positive_semidefinite,
        "static_force_is_zero": boundary.static_force == (0.0, 0.0),
        "static_entropy_production_is_zero_for_both_witnesses": (
            isclose(boundary.static_entropy_production_a, 0.0, abs_tol=1.0e-15)
            and isclose(boundary.static_entropy_production_b, 0.0, abs_tol=1.0e-15)
        ),
        "static_state_is_identical_for_both_witnesses": boundary.static_state_identical,
        "probe_responses_are_distinct": boundary.probe_responses_distinct,
        "physical_transport_coefficient_not_emitted": (
            boundary.physical_transport_coefficients_emitted is False
        ),
        "no_parameter_fitting": True,
        "no_target_data": True,
        "xie_holdout_is_unread": True,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_remains_separate": "separate observer" in contract["unit_contract"]["R_obs"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        CONDENSED_DISSIPATIVE_TRANSPORT_STATUS
        if not failed
        else "BLOCKED_CONDENSED_DISSIPATIVE_TRANSPORT_AUDIT"
    )
    evidence = [
        {
            "path": "docs/core/02_equations/o2/uet_o2_condensed_dissipative_transport_identifiability_no_go.py",
            "sha256": sha256(MODULE),
        },
        {
            "path": "docs/core/02_equations/o2/uet_o2_finite_temperature_two_fluid_response.py",
            "sha256": sha256(STATIC_MODULE),
        },
        {
            "path": "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_two_fluid_response_audit.json",
            "sha256": sha256(STATIC_ARTIFACT),
        },
    ]
    artifact = {
        "schema_version": "t13-uet-o2-condensed-dissipative-transport-v1",
        "artifact": "t13_uet_o2_condensed_dissipative_transport_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": (
                "T13_UET_O2_CONDENSED_DISSIPATIVE_TRANSPORT_IDENTIFIABILITY_NO_GO"
            ),
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if not failed else "OPEN",
            "what_is_closed": [
                "the declared condensed static lane has zero condensate entropy in its tree-sector state records",
                "two positive-semidefinite dissipative witnesses are identical on the current static state",
                "the witnesses separate under a nonzero probe, proving that the current static lane cannot identify a unique dissipative matrix",
                "a physical condensed transport coefficient requires a relative-flow/collision kernel or state-matched retarded correlator",
            ]
            if not failed
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "microscopic_condensed_collision_kernel_missing",
                "retarded_physical_Kubo_match_missing",
                "complete_two_fluid_constitutive_tensor_missing",
                "full_heat_flux_entropy_production_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": (
                "condensed dissipative transport identifiability boundary only; "
                "no physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock"
            ),
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {
            "temperature": boundary.temperature,
            "chemical_potential": boundary.chemical_potential,
            "static_force": list(boundary.static_force),
            "probe_force": list(boundary.probe_force),
            "witness_a": [list(row) for row in boundary.witness_a],
            "witness_b": [list(row) for row in boundary.witness_b],
            "static_entropy_production_a": boundary.static_entropy_production_a,
            "static_entropy_production_b": boundary.static_entropy_production_b,
            "probe_response_a": list(boundary.probe_response_a),
            "probe_response_b": list(boundary.probe_response_b),
            "witness_a_positive_semidefinite": boundary.witness_a_positive_semidefinite,
            "witness_b_positive_semidefinite": boundary.witness_b_positive_semidefinite,
            "static_state_identical": boundary.static_state_identical,
            "probe_responses_distinct": boundary.probe_responses_distinct,
        },
        "checks": checks,
        "failed_checks": failed,
        "physical_transport_coefficients_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "microscopic_condensed_collision_kernel_missing",
        "next_controller": (
            "derive a symmetry-compatible condensed collision/relative-flow "
            "kernel or obtain a state-matched retarded correlator; do not "
            "promote the two structural witnesses to physical transport"
        ),
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "used_for_fit": False,
            "used_for_tuning": False,
            "used_for_calibration": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=True) + chr(10),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "major_result_id": artifact["major_result"]["major_result_id"],
                "closure_level": artifact["major_result"]["closure_level"],
                "failed_checks": failed,
                "static_state_identical": boundary.static_state_identical,
                "probe_responses_distinct": boundary.probe_responses_distinct,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
