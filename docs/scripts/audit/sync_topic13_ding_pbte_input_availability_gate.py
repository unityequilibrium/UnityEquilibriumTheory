"""Attach the Ding OA numeric-input availability no-go to the Topic 13 gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_ding_pbte_numeric_input_availability_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "ding_2022_pbte_numeric_input_availability_package.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def append_once(values: list[str], item: str) -> None:
    if item not in values:
        values.append(item)


def main() -> int:
    gate = load(GATE)
    audit = load(AUDIT)
    result = audit["major_result"]
    audit_path = rel(AUDIT)
    branch = gate["verification_status"]["alpha_Phi_K"][
        "named_energy_response_branch"
    ]
    branch["pbte_numeric_input_availability_no_go"] = {
        "major_result_id": result["major_result_id"],
        "status": audit["status"],
        "closure_level": result["closure_level"],
        "audit": {"path": audit_path, "sha256": sha256(AUDIT)},
        "source_package": {"path": rel(PACKAGE), "sha256": sha256(PACKAGE)},
        "direct_oa_numeric_route": "CLOSED_AS_SCOPED_NO_GO",
        "author_request_route": "OPEN_NOT_EXECUTED",
        "independent_reproduction_route": "OPEN_INPUT_PACKAGE_NOT_BUILT",
        "open_blockers": result["open_blockers"],
    }
    closed = gate["major_result"].setdefault("what_is_closed", [])
    append_once(
        closed,
        "scoped no-go for obtaining Ding PBTE numeric heat-capacity or reproduction inputs directly from the captured official PMC OA package",
    )
    remains = gate["major_result"].setdefault("what_remains_open", [])
    for blocker in result["open_blockers"]:
        append_once(remains, blocker)
    evidence = gate.setdefault("evidence_artifacts", [])
    evidence[:] = [item for item in evidence if item.get("path") != audit_path]
    evidence.append(
        {
            "path": audit_path,
            "sha256": sha256(AUDIT),
            "summary": {
                "status": audit["status"],
                "scope": "captured official PMC OA distribution only",
            },
        }
    )
    gate["data_role"]["ding_pbte_numeric_input_availability"] = (
        "SOURCE_PROVENANCE_NO_GO; no numeric C_src or calibration consumed"
    )
    gate["source_acquisition_controller"] = (
        "ding_pbte_author_data_or_independent_reproduction_package_missing"
    )
    gate["next_action"] = audit["next_action"]
    gate["controlling_blocker"] = (
        "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    )
    gate["claim_promotion"] = False
    GATE.write_text(
        json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": gate["status"],
                "availability_no_go": audit["status"],
                "controlling_blocker": gate["controlling_blocker"],
                "source_acquisition_controller": gate[
                    "source_acquisition_controller"
                ],
                "claim_promotion": gate["claim_promotion"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
