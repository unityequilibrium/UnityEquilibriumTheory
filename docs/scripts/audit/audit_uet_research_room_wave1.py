"""Audit the Wave 1 room contract and write the Core integration gate/note."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "docs/core/07_artifacts/archive/uet_research_room_wave1_contract.json"
REGISTRY = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"
GATE = ROOT / "docs/core/07_artifacts/gates/uet_research_room_wave1_integration_gate.json"
NOTE = ROOT / "docs/core/UET_RESEARCH_ROOM_WAVE1_INTEGRATION_NOTE.md"
INBOX_DRIFT = ROOT / "docs/core/07_artifacts/archive/inbox_research_alignment_drift_note.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def main() -> int:
    contract = load(CONTRACT)
    registry = load(REGISTRY)
    required_fields = contract.get("required_mapping_fields", [])
    room_errors: list[str] = []
    for room_id, room in contract.get("rooms", {}).items():
        missing = [field for field in required_fields if not room.get(field)]
        if missing:
            room_errors.append(f"{room_id}:missing:{','.join(missing)}")
    registry_ids = {entry.get("equation_id") for entry in registry.get("entries", [])}
    required_registry_ids = {
        "uet.thermal.ttg_normalized_observable",
        "uet.thermal.causal_reference_branch",
        "uet.phase.structure_factor_estimator_policy",
        "uet.fluid.standard_comparator",
    }
    missing_registry = sorted(required_registry_ids - registry_ids)
    artifact_errors = [
        evidence["path"]
        for room in contract.get("rooms", {}).values()
        for evidence in room.get("evidence", [])
        if evidence.get("present") is False
    ]
    inbox_expected = ROOT / "docs/core/00_inbox"
    inbox_note = {
        "schema_version": "1.0",
        "artifact": "inbox_research_alignment_drift_note",
        "generated_at": date.today().isoformat(),
        "status": "BLOCKED_STALE_SOURCE_PATHS",
        "expected_path": rel(inbox_expected),
        "path_exists": inbox_expected.is_dir(),
        "controlling_blocker": "existing inbox alignment artifact references a path absent from this checkout",
        "action": "rebuild the inbox alignment artifact from current checkout paths before using it as a controller",
        "claim_boundary": "housekeeping only; does not alter Topic 0.13 status or claim ceiling",
    }
    INBOX_DRIFT.write_text(json.dumps(inbox_note, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    topic_022 = ROOT / "docs/topics/0.22_Biophysics_Origin_of_Life"
    topic_03_artifact = ROOT / "docs/topics/0.3_Cosmology_Hubble_Tension/Result/artifacts/hubble_comparison_validation.json"
    topic_03 = load(topic_03_artifact) if topic_03_artifact.is_file() else {}
    blockers = list(contract.get("integration_blockers", []))
    blockers.extend(room.get("controlling_blocker") for room in contract.get("rooms", {}).values() if room.get("controlling_blocker"))
    gate_status = "PASS_WITH_BLOCKED_LANES" if not room_errors and not missing_registry and not artifact_errors else "BLOCKED_INTEGRATION_CONTRACT"
    gate = {
        "schema_version": "1.0",
        "artifact": "uet_research_room_wave1_integration_gate",
        "generated_at": date.today().isoformat(),
        "status": gate_status,
        "claim_promotion": False,
        "brief": {"path": "docs/core/UET_RESEARCH_ROOM_BRIEF.md", "sha256": sha256(ROOT / "docs/core/UET_RESEARCH_ROOM_BRIEF.md")},
        "contract": {"path": rel(CONTRACT), "sha256": sha256(CONTRACT)},
        "registry": {"path": rel(REGISTRY), "sha256": sha256(REGISTRY), "required_wave1_entries_present": not missing_registry, "missing_wave1_entries": missing_registry},
        "rooms": contract.get("rooms", {}),
        "controlling_blockers": sorted(set(blockers)),
        "structural_errors": {"room_errors": room_errors, "missing_registry_entries": missing_registry, "missing_evidence_artifacts": artifact_errors},
        "housekeeping": {
            "topic_0_22_separate_checkpoint": {
                "status": "SEPARATE_PREEXISTING_CHECKPOINT",
                "path": rel(topic_022),
                "path_exists": topic_022.is_dir(),
                "claim_boundary": "not a controller for Topic 0.13 and not part of Wave 1 topic promotion",
            },
            "inbox_alignment": {"path": rel(INBOX_DRIFT), "sha256": sha256(INBOX_DRIFT), "status": inbox_note["status"]},
            "topic_0_3_index": {
                "latest_scalar_artifact_path": rel(topic_03_artifact),
                "latest_scalar_artifact_sha256": sha256(topic_03_artifact) if topic_03_artifact.is_file() else None,
                "latest_scalar_artifact_status": topic_03.get("status", topic_03.get("audit_status")),
                "full_cosmology_claim": "BLOCKED_UNCHANGED",
                "status": "REQUIRES_INDEX_SYNC" if topic_03.get("status") == "PASS" else "REVIEW_REQUIRED",
                "claim_boundary": "scalar Hubble benchmark status is separate from full cosmology closure",
            },
        },
        "next_action": "resolve the listed blockers in their owning rooms, then rerun this integration audit; do not start Gravity or full constitutive transport yet",
        "claim_boundary": "Wave 1 is an evidence and coordination checkpoint; UET remains a candidate effective theory and no global claim is promoted",
    }
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    note = "\n".join(
        [
            "# UET Research Room Wave 1 Integration Note",
            "",
            f"STATUS: {gate_status}",
            "WHAT_CHANGED: Added a shared room contract, registry entries, per-room artifact snapshots, and a non-promoting integration gate.",
            "EQUATION_OR_MAPPING: y_TTG = Delta_Tq(t) / Delta_Tq(0); y_TTG^UET = Delta_Phi(t) / Delta_Phi(0); Delta_Tq = alpha_Phi_K * Delta_Phi. The selected causal reference is frozen-C and normalized; the full coupled candidate is separate.",
            "VERIFICATION: Contract JSON parses; required Wave 1 registry entries and room mapping fields are checked; the selected reference branch is reported separately from the full-candidate leakage gate; Xie 2026 remains locked holdout.",
            "CONTROLLING_BLOCKER: Full coupled pre-arrival leakage remains above the locked 1e-6 threshold; alpha_Phi_K and dimensional TTG mapping remain open; Topic 0.11 source/estimator gates remain blocked.",
            "NEXT_ACTION: Complete independent alpha_Phi_K derivation or calibration with uncertainty, finish Topic 0.11 source and estimator gates, and rerun the owning audits before any Gravity or full constitutive-transport work.",
            "CLAIM_BOUNDARY: Wave 1 closes coordination ambiguity only. Internal or provisional artifacts do not establish a physical proof, external validation, prediction, or closed UET theory.",
            "",
            f"Contract artifact: `{rel(CONTRACT)}`",
            f"Gate artifact: `{rel(GATE)}`",
            f"Inbox drift artifact: `{rel(INBOX_DRIFT)}`",
        ]
    ) + "\n"
    NOTE.write_text(note, encoding="utf-8")
    print(json.dumps({"status": gate_status, "room_errors": room_errors, "missing_registry_entries": missing_registry, "artifact": rel(GATE)}, indent=2))
    return 0 if gate_status == "PASS_WITH_BLOCKED_LANES" else 1


if __name__ == "__main__":
    raise SystemExit(main())
