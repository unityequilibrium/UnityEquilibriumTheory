"""Validate final Wave 1 artifact identity, gate separation, and holdout policy."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "docs/core/07_artifacts/archive/uet_research_room_wave1_contract.json"
INTEGRATION = ROOT / "docs/core/07_artifacts/gates/uet_research_room_wave1_integration_gate.json"
FOUNDATION = ROOT / "docs/core/07_artifacts/gates/uet_foundation_dependency_gate.json"
BRANCH = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/thermal_wave1_branch_gate.json"
PROVENANCE = ROOT / "docs/core/07_artifacts/topic13/thermal_source_provenance_gate.json"
HOLDOUT_AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_xie_2026_holdout_access_audit.json"
REGISTRY = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"
INDEX = ROOT / "docs/topics/README.md"
OUT = ROOT / "docs/core/07_artifacts/archive/uet_research_room_wave1_integrity.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    contract = load(CONTRACT)
    integration = load(INTEGRATION)
    foundation = load(FOUNDATION)
    branch = load(BRANCH)
    provenance = load(PROVENANCE)
    holdout_audit = load(HOLDOUT_AUDIT)
    holdout_controls = holdout_audit.get("audit", {})
    registry = load(REGISTRY)
    required_ids = {
        "uet.thermal.ttg_normalized_observable",
        "uet.thermal.causal_reference_branch",
        "uet.phase.structure_factor_estimator_policy",
        "uet.fluid.standard_comparator",
    }
    artifact_paths = [
        CONTRACT,
        INTEGRATION,
        FOUNDATION,
        BRANCH,
        PROVENANCE,
        HOLDOUT_AUDIT,
        ROOT / "docs/core/07_artifacts/verification/matter_space_causal_reference_verification.json",
        ROOT / "docs/core/07_artifacts/verification/matter_space_variational_verification.json",
        ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_observable_map_readiness.json",
        ROOT / "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_structure_factor_source_archive_policy_gate.json",
        ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts/fluid_benchmark_validation.json",
    ]
    evidence_paths = [
        evidence.get("path")
        for room in contract.get("rooms", {}).values()
        for evidence in room.get("evidence", [])
        if evidence.get("path")
    ]
    missing_evidence = [path for path in evidence_paths if not (ROOT / path).is_file()]
    hash_errors: list[str] = []
    for room in contract.get("rooms", {}).values():
        for evidence in room.get("evidence", []):
            if "EXCLUDED" in str(evidence.get("hash_policy", "")).upper():
                continue
            if evidence.get("present") and evidence.get("sha256"):
                path = ROOT / evidence["path"]
                if path.is_file() and digest(path) != evidence["sha256"]:
                    hash_errors.append(evidence["path"])
    package = load(ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json")
    holdout = next(row for row in package["sources"] if "holdout" in row["source_id"])
    checks = {
        "contract_status": contract.get("status") == "PASS_WITH_BLOCKED_LANES",
        "integration_status": integration.get("status") == "PASS_WITH_BLOCKED_LANES",
        "claim_promotion_disabled": contract.get("claim_promotion") is False and integration.get("claim_promotion") is False,
        "required_registry_ids": required_ids <= {entry.get("equation_id") for entry in registry.get("entries", [])},
        "evidence_paths_present": not missing_evidence,
        "evidence_hashes_match": not hash_errors,
        "selected_reference_passes_locked_threshold": branch["gates"]["selected_causal_reference_prearrival_leakage"] and branch["selected_causal_branch"]["prearrival_leakage_fraction"] <= 1.0e-6,
        "full_candidate_gate_preserved_failed": branch["gates"]["full_candidate_prearrival_leakage"] is False and branch["full_candidate_branch"]["prearrival_leakage_fraction"] > 1.0e-6,
        "threshold_unchanged": branch["gates"]["locked_threshold_unchanged"] is True,
        "provenance_passes": provenance.get("status") in {"PASS_WITH_PROVISIONAL_DIGITIZATION", "PASS_WITH_FIGURE_DERIVED_NORMALIZED_COMPARISON"} and provenance.get("metrics", {}).get("provenance_complete") is True,
        "holdout_not_consumed": holdout_controls.get("numeric_payload_consumed") is False and holdout_controls.get("numeric_rows_consumed") is False and holdout_controls.get("used_for_fit") is False and holdout_controls.get("used_for_tuning") is False and holdout_controls.get("used_for_calibration") is False and holdout_controls.get("used_for_threshold_adjustment") is False and holdout_controls.get("locked_holdout_remains_unconsumed") is True,
        "foundation_link_matches": foundation.get("research_room_wave1", {}).get("contract", {}).get("sha256") == digest(CONTRACT),
        "topic_0_3_index_synced": "latest scalar Hubble artifact" in INDEX.read_text(encoding="utf-8") and "full cosmology remains blocked" in INDEX.read_text(encoding="utf-8"),
        "inbox_absent_is_explicit": not (ROOT / "docs/core/00_inbox").is_dir(),
    }
    report = {
        "schema_version": "1.0",
        "artifact": "uet_research_room_wave1_integrity",
        "generated_at": date.today().isoformat(),
        "status": "PASS_WITH_BLOCKED_LANES" if all(checks.values()) else "FAIL",
        "checks": checks,
        "missing_evidence": missing_evidence,
        "hash_errors": hash_errors,
        "artifact_paths": [rel(path) for path in artifact_paths if path.is_file()],
        "claim_boundary": "Integrity pass confirms artifact/gate consistency only; it does not promote UET physical claims.",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
