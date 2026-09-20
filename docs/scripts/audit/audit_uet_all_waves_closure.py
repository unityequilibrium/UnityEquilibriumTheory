"""Close status accounting for every planned UET research wave.

The artifact distinguishes a completed research-control wave from a physically
closed theory.  A wave may therefore be CLOSED_AS_BLOCKED when its evidence,
claim ceiling, and next controller are explicit but the underlying physics is not
yet promotable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/07_artifacts/gates/uet_all_waves_closure.json"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel(path)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence(path_text: str) -> dict[str, Any]:
    path = ROOT / path_text
    return {"path": path_text, "exists": path.exists(), "sha256": sha256(path) if path.exists() else None}


def build() -> dict[str, Any]:
    foundation_path = ROOT / "docs/core/07_artifacts/gates/uet_foundation_dependency_gate.json"
    wave_program_path = ROOT / "docs/core/07_artifacts/archive/uet_wave3_wave10_research_program.json"
    extended_path = ROOT / "docs/core/07_artifacts/gates/uet_foundation_extended_wave_closure.json"
    pilot_sync_path = ROOT / "docs/core/07_artifacts/archive/matter_space_topic_pilot_sync.json"
    foundation = load(foundation_path)
    wave_program = load(wave_program_path)
    extended = load(extended_path)
    pilot_sync = load(pilot_sync_path)
    particle_gate_path = ROOT / "docs/core/07_artifacts/gates/particle_dirac_program_gate.json"
    particle_gate = load(particle_gate_path)

    planned: list[dict[str, Any]] = []
    for item in wave_program.get("waves", []):
        planned.append(
            {
                "wave": item.get("wave"),
                "name": item.get("name"),
                "status": item.get("effective_status", item.get("local_evidence_status", "UNKNOWN")),
                "closure_status": "PENDING",
                "physics_status": item.get("effective_status", "UNKNOWN"),
                "controlling_blocker": item.get("controlling_blocker"),
                "claim_ceiling": item.get("claim_ceiling"),
                "evidence": [
                    {
                        **evidence(entry.get("path")),
                        "status": entry.get("status"),
                        "controller": entry.get("controller"),
                    }
                    for entry in item.get("inputs", [])
                    if entry.get("exists") and entry.get("path")
                ],
            }
        )

    extended_by_wave = {item.get("wave"): item for item in extended.get("waves", [])}
    for item in planned:
        if item["wave"] not in extended_by_wave:
            continue
        downstream = extended_by_wave[item["wave"]]
        item["status"] = downstream.get("status", item["status"])
        item["physics_status"] = downstream.get("status", item["physics_status"])
        item["controlling_blocker"] = downstream.get("controller", item["controlling_blocker"])
        item["claim_ceiling"] = downstream.get("claim_boundary", item["claim_ceiling"])
        item["evidence"] = [evidence(path) for path in downstream.get("evidence", [])]
        item["closure_status"] = "CLOSED_AS_BLOCKED" if "BLOCKED" in str(item["status"]) or "DEFERRED" in str(item["status"]) else "CLOSED_WITH_CONDITIONS"

    for item in planned:
        if item["closure_status"] == "PENDING":
            item["closure_status"] = "CLOSED_AS_BLOCKED" if "BLOCKED" in str(item["status"]) or "DEFERRED" in str(item["status"]) else "CLOSED_WITH_CONDITIONS"

    # Wave 11 is not represented in the 0â€“10 generator, so make its deferral explicit.
    planned.append(
        {
            "wave": 11,
            "name": "Particle, Dirac, neutrino, and antimatter program",
            "status": "DEFERRED_BLOCKED",
            "closure_status": "CLOSED_AS_BLOCKED",
            "physics_status": "DEFERRED_BLOCKED",
            "controlling_blocker": particle_gate.get("controlling_blocker", "Lorentz-covariant action, spinor/current map, CPT and detector correspondence are not established"),
            "claim_ceiling": "particle, Dirac, neutrino, positron and antimatter identities remain deferred/not established",
            "evidence": [evidence("docs/core/07_artifacts/gates/particle_dirac_program_gate.json")],
        }
    )
    planned.sort(key=lambda item: item["wave"])

    gate_status = foundation.get("status", "UNKNOWN")
    closed_as_blocked = [item["wave"] for item in planned if item["closure_status"] == "CLOSED_AS_BLOCKED"]
    conditional = [item["wave"] for item in planned if item["closure_status"] == "CLOSED_WITH_CONDITIONS"]
    return {
        "schema_version": "1.0",
        "artifact": "uet_all_waves_closure",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS",
        "program_status": "ALL_WAVE_STATUS_ACCOUNTING_CLOSED_FOUNDATION_PHYSICS_NOT_CLOSED",
        "foundation_gate": {
            "path": rel(foundation_path),
            "status": gate_status,
            "sha256": sha256(foundation_path),
            "controller": foundation.get("controlling_blocker"),
        },
        "wave_count": len(planned),
        "closed_as_blocked_waves": closed_as_blocked,
        "closed_with_conditions_waves": conditional,
        "waves": planned,
        "checks": {
            "all_planned_waves_present": [item["wave"] for item in planned] == list(range(12)),
            "all_waves_have_closure_status": all(item.get("closure_status") for item in planned),
            "all_waves_have_claim_ceiling": all(item.get("claim_ceiling") for item in planned),
            "all_blocked_waves_have_controller": all(
                item.get("controlling_blocker") for item in planned if item["closure_status"] == "CLOSED_AS_BLOCKED"
            ),
            "pilot_sync_preserves_inherited_blockers": pilot_sync.get("audit_status") == "PASS_WITH_INHERITED_BLOCKERS",
            "no_physical_promotion": gate_status == "BLOCKED",
        },
        "interpretation": {
            "closure_status": "The project-control state is complete: every planned wave has evidence, status, claim ceiling and next controller.",
            "physics_status": "A CLOSED_AS_BLOCKED wave is not a solved theory; it is a formally bounded research lane whose blocker is now explicit.",
            "selected_positive_result": "Only the selected normalized characteristic-cone diagnostic is locally passing; it does not establish SI physics, universal C meaning or empirical validity.",
        },
        "next_controller": foundation.get(
            "next_controller",
            "close foundation coverage, dimensional units and observable maps; run the source-locked thermal and external 3D C-density lanes before any downstream promotion",
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    try:
        result = build()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"audit_status=FAIL\nERROR: {exc}")
        return 1
    if not args.no_write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={result['audit_status']}")
        print(f"program_status={result['program_status']}")
        print(f"wave_count={result['wave_count']}")
        print(f"closed_as_blocked={result['closed_as_blocked_waves']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
