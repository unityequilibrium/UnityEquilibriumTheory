"""Attach the Ding OA numeric-input availability decision to the energy branch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ENERGY = ROOT / "docs/core/07_artifacts/topic13/t13_energy_response_bridge_audit.json"
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
    energy = load(ENERGY)
    audit = load(AUDIT)
    result = audit["major_result"]
    audit_ref = {"path": rel(AUDIT), "sha256": sha256(AUDIT)}
    package_ref = {"path": rel(PACKAGE), "sha256": sha256(PACKAGE)}
    energy["pbte_numeric_input_availability"] = {
        "major_result_id": result["major_result_id"],
        "status": audit["status"],
        "closure_level": result["closure_level"],
        "audit": audit_ref,
        "source_package": package_ref,
        "direct_oa_numeric_route": "CLOSED_AS_SCOPED_NO_GO",
        "author_request_route": "OPEN_NOT_EXECUTED",
        "independent_reproduction_route": "OPEN_INPUT_PACKAGE_NOT_BUILT",
        "xie_2026_accessed": False,
    }
    closed = energy["major_result"].setdefault("what_is_closed", [])
    if isinstance(closed, str):
        closed = [closed]
        energy["major_result"]["what_is_closed"] = closed
    append_once(
        closed,
        "scoped no-go for obtaining Ding mode heat capacity or first-principles reproduction payload directly from the captured PMC OA package",
    )
    evidence = energy["major_result"].setdefault("evidence_artifacts", [])
    evidence[:] = [item for item in evidence if item.get("path") != rel(AUDIT)]
    evidence.extend([audit_ref, package_ref])
    blockers = energy["major_result"].setdefault("open_blockers", [])
    for blocker in result["open_blockers"]:
        append_once(blockers, blocker)
    energy["controlling_blocker"] = (
        "ding_pbte_author_data_or_independent_reproduction_package_missing"
    )
    energy["next_controller"] = audit["next_action"]
    ENERGY.write_text(
        json.dumps(energy, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "artifact": rel(ENERGY),
                "availability_no_go": audit["status"],
                "controlling_blocker": energy["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
