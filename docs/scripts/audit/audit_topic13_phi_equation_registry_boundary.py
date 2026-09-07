"""Audit the central equation registry for hidden dimensionful Phi mappings."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs/core/artifacts/t13_phi_equation_registry_mapping_boundary_audit.json"
REGISTRY = "docs/core/artifacts/uet_equation_correspondence_registry.json"
ACTIVE_LANE = "docs/core/artifacts/uet_active_lane_units_observable_register.json"
BASE_PHI_AUDIT = "docs/core/artifacts/t13_base_phi_registry_completeness_audit.json"


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def entry_text(entry: dict) -> str:
    return json.dumps(entry, sort_keys=True)


def main() -> int:
    registry = read_json(REGISTRY)
    active = read_json(ACTIVE_LANE)
    base_phi = read_json(BASE_PHI_AUDIT)
    entries = registry["entries"]
    phi_entries = [
        entry for entry in entries if "phi" in entry_text(entry).lower()
    ]
    thermal_entry = next(
        entry
        for entry in entries
        if entry.get("equation_id") == "uet.thermal.ttg_normalized_observable"
    )
    parent_entry = next(
        entry
        for entry in entries
        if entry.get("equation_id") == "uet.main_theory.covariant_parent"
    )
    thermal_lane = next(
        lane for lane in active["lanes"] if lane["lane_id"] == "thermal_ttg_observable_bridge"
    )

    phi_unit_lanes = sorted(
        {entry.get("unit_lane", "UNDECLARED") for entry in phi_entries}
    )
    checks = {
        "registry_loaded": len(entries) == 43,
        "thermal_phi_entry_present": thermal_entry["unit_lane"]
        == "normalized_with_open_K_scale",
        "thermal_dimensional_status_blocked": thermal_entry["observable_mapping"][
            "status"
        ]
        == "NORMALIZED_DEFINED_DIMENSIONAL_BLOCKED",
        "covariant_parent_is_natural_only": parent_entry["unit_lane"]
        == "natural_only_v1",
        "all_phi_entries_are_non_si_or_explicitly_open": all(
            "si" not in lane.lower() for lane in phi_unit_lanes
        ),
        "active_thermal_lane_matches_registry": thermal_lane["unit_lane"]
        == "normalized_plus_external_K_contract_open"
        and thermal_lane["units_status"] == "BLOCKED_INDEPENDENT_ALPHA_Phi_K",
        "base_phi_audit_also_reports_no_hidden_anchor": base_phi["status"]
        == "PASS_SCOPED_NO_HIDDEN_SI_ANCHOR",
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"Topic 13 Phi equation-registry audit failed: {failed}")

    evidence = [
        {"path": path, "sha256": sha256(path)}
        for path in (REGISTRY, ACTIVE_LANE, BASE_PHI_AUDIT)
    ]
    payload = {
        "schema_version": "t13-phi-equation-registry-boundary-v1",
        "artifact": "t13_phi_equation_registry_mapping_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_NO_ACCEPTED_DIMENSIONFUL_PHI_MAPPING",
        "major_result": {
            "major_result_id": "T13_PHI_EQUATION_REGISTRY_MAPPING_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "The central registry contains the thermal normalized operator and explicitly marks its dimensional status as blocked.",
                "The covariant parent Phi entry remains natural-only rather than an SI observable map.",
                "All registry entries that mention Phi use normalized, natural, or conceptual unit lanes; no accepted dimensionful Phi mapping is registered.",
                "The central registry and active-lane units register agree on the open alpha_Phi_K boundary.",
            ],
            "equation_or_mapping": {
                "thermal_entry": "y_TTG^UET = Delta_Phi(t) / Delta_Phi(0); Delta_Tq = alpha_Phi_K * Delta_Phi",
                "thermal_registry_status": "NORMALIZED_DEFINED_DIMENSIONAL_BLOCKED",
                "covariant_parent_lane": "natural_only_v1",
                "required_next_map": "base Phi -> SI energy/temperature observable with independent provenance",
            },
            "units": {
                "Phi": "normalized or natural action lane only",
                "Delta_Tq": "K only after independent mapping",
                "alpha_Phi_K": "open K per normalized Phi",
                "registry_entry_count": len(entries),
                "Phi_entry_count": len(phi_entries),
                "Phi_unit_lanes": phi_unit_lanes,
            },
            "derivation_class": "central equation-registry consistency and mapping-boundary audit",
            "observable": "normalized TTG operator and conditional dimensional response operator",
            "data_role": "INTERNAL_REGISTRY_AUDIT_NO_TARGET_OR_HOLDOUT",
            "evidence_artifacts": evidence,
            "verification_status": "PASS_SCOPED_NO_ACCEPTED_DIMENSIONFUL_PHI_MAPPING",
            "open_blockers": [
                "base_phi_si_anchor",
                "independent_alpha_record",
                "normalized_beta_si_map",
                "physical_source_backed_eos",
                "physical_heat_flux_entropy_map",
            ],
            "dependency_unlocked": "None; registry boundary only, with no Full Topic 13 or downstream unlock.",
            "claim_boundary": "This audit establishes that the current central registry does not contain an accepted dimensionful Phi mapping. It does not rule out a future action-derived or independently calibrated mapping and does not close Full Topic 13.",
        },
        "checks": checks,
        "registry_entry_ids_with_phi": [entry["equation_id"] for entry in phi_entries],
        "phi_unit_lanes": phi_unit_lanes,
        "controlling_blocker": "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing",
        "next_controller": "Register a dimensionful Phi/observable map only after its derivation or independent calibration, units, uncertainty, and source provenance are accepted.",
        "claim_boundary": "Scoped registry boundary only; no numeric alpha_Phi_K, e0, SI Phi map, target fit, or holdout result is emitted.",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": str(OUTPUT.relative_to(ROOT)),
                "registry_entries": len(entries),
                "phi_entries": len(phi_entries),
                "holdout_used": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
