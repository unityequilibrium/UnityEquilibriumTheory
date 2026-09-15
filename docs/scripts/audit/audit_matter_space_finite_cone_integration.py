"""Audit integration of the selected normalized finite-cone lane.

This joins already-generated characteristic, ledger, observable, and pilot
artifacts.  It does not replace the failing full Heun/RK2 causal gate and does
not create an SI or mass-density interpretation.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs/core/07_artifacts/archive/matter_space_finite_cone_shared_ledger_integration.json"


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def build() -> dict[str, Any]:
    characteristic = load("docs/core/07_artifacts/verification/matter_space_characteristic_cone_verification.json")
    observable = load("docs/core/07_artifacts/verification/matter_space_observable_verification.json")
    lane = load("docs/core/07_artifacts/archive/matter_space_causal_lane_selection.json")
    pilot_sync = load("docs/core/07_artifacts/archive/matter_space_topic_pilot_sync.json")
    full = load("docs/core/07_artifacts/verification/matter_space_variational_verification.json")

    characteristic_pass = (
        characteristic.get("audit_status") == "PASS"
        and characteristic.get("gates", {}).get("compact_support_no_prearrival_leakage") is True
        and characteristic.get("gates", {}).get("no_clipping") is True
        and characteristic.get("gates", {}).get("no_cone_padding") is True
    )
    observable_pass = (
        observable.get("audit_status") == "PASS_WITH_OPEN_SI_MAPPING"
        and observable.get("gates", {}).get("operator_contract_declared") is True
        and observable.get("gates", {}).get("trace_toggle_does_not_change_physical_state") is True
    )
    selected_lane_pass = lane.get("selected_lane", {}).get("operator_mode") == "matter_space_characteristic_cone_v1"
    pilot_reruns_present = (
        pilot_sync.get("topic_0_11", {}).get("selected_lane_available") is True
        and pilot_sync.get("topic_0_13", {}).get("selected_lane_available") is True
    )
    full_candidate_blocked = full.get("metrics", {}).get("prearrival_leakage", {}).get("gate") == "FAIL"
    checks = {
        "selected_lane_identity": selected_lane_pass,
        "characteristic_compact_support": characteristic_pass,
        "normalized_observable_contract": observable_pass,
        "pilot_selected_lane_reruns_present": pilot_reruns_present,
        "full_default_candidate_blocker_preserved": full_candidate_blocked,
        "si_mapping_remains_open": observable.get("measurement_operator", {}).get("SI_status") == "BLOCKED",
        "mass_density_mapping_remains_undefined": observable.get("measurement_operator", {}).get("mass_density_mapping") == "NOT_DEFINED",
    }
    status = "PASS_NORMALIZED_SHARED_LEDGER_WITH_OPEN_UNITS_AND_FULL_CANDIDATE_BLOCKED" if all(checks.values()) else "BLOCKED_INTEGRATION_CONTRACT"
    return {
        "schema_version": "1.0",
        "artifact": "matter_space_finite_cone_shared_ledger_integration",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS" if status.startswith("PASS") else "FAIL",
        "status": status,
        "operator_mode": "matter_space_characteristic_cone_v1",
        "unit_lane": "normalized_only_v1",
        "shared_ledger": {
            "characteristic_audit_status": characteristic.get("audit_status"),
            "max_ledger_relative_residual": characteristic.get("metrics", {}).get("max_ledger_relative_residual"),
            "closed_energy_increase": characteristic.get("metrics", {}).get("max_closed_energy_increase"),
            "trace_backreaction": "disabled/derived-observable-only",
        },
        "observable_contract": {
            "audit_status": observable.get("audit_status"),
            "operator": observable.get("measurement_operator"),
            "uncertainty_status": observable.get("measurement_operator", {}).get("uncertainty_status"),
        },
        "pilot_reruns": {
            "topic_0_11": pilot_sync.get("topic_0_11", {}).get("selected_lane_rerun_artifact"),
            "topic_0_13": pilot_sync.get("topic_0_13", {}).get("selected_lane_rerun_artifact"),
        },
        "checks": checks,
        "full_candidate_boundary": {
            "default_full_verification_status": full.get("status"),
            "prearrival_leakage": full.get("metrics", {}).get("prearrival_leakage"),
            "claim": "full nonlinear Heun/RK2 candidate remains blocked; selected characteristic lane is not a universal replacement",
        },
        "claim_boundary": "normalized selected-lane shared-ledger integration only; no SI physics, mass-density identity, covariant completion, or empirical validation",
        "next_controller": "derive a dimensional lane and close the full-candidate causal discretization separately without clipping or cone padding",
    }


def main() -> int:
    artifact = build()
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"audit_status={artifact['audit_status']}")
    print(f"status={artifact['status']}")
    print(f"full_candidate={artifact['full_candidate_boundary']['default_full_verification_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
