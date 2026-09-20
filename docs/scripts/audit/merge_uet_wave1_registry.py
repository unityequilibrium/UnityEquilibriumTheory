"""Merge the Wave 1 registry addendum without promoting any claim."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"
ADDENDUM = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_wave1_research_rooms_addendum.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    registry = read_json(REGISTRY)
    addendum = read_json(ADDENDUM)
    entries = list(registry.get("entries", []))
    known = {entry.get("equation_id") for entry in entries}
    addendum_entries = addendum.get("equation_entries", addendum.get("entries", []))
    merged: list[str] = []
    already_present: list[str] = []
    conflicts: list[str] = []
    for entry in addendum_entries:
        equation_id = entry.get("equation_id")
        if not equation_id:
            conflicts.append("missing_equation_id")
        elif equation_id in known:
            already_present.append(equation_id)
        else:
            entries.append(entry)
            known.add(equation_id)
            merged.append(equation_id)

    relative_addendum = ADDENDUM.relative_to(ROOT).as_posix()
    coverage = dict(registry.get("coverage", {}))
    addenda = list(coverage.get("addenda_merged", []))
    if relative_addendum not in addenda:
        addenda.append(relative_addendum)
    coverage.update(
        {
            "extension_status": "CANDIDATE_ADDENDA_MERGED_NOT_EXHAUSTIVE",
            "addenda_merged": addenda,
            "rule": "merged candidate addenda do not promote downstream claims while foundation gates remain blocked",
        }
    )
    history = dict(registry.get("merge_history", {}))
    history["merged_equation_ids"] = list(history.get("merged_equation_ids", [])) + merged
    history["already_present"] = list(history.get("already_present", [])) + already_present
    history["conflicts"] = list(history.get("conflicts", [])) + conflicts
    history["source_policy"] = "addenda are merged as candidate records; evidence and claim boundaries are preserved"
    registry.update(
        {
            "schema_version": "1.1",
            "generated_at": date.today().isoformat(),
            "status": "CENTRAL_REGISTRY_WITH_CANDIDATE_ADDENDA_BLOCKED",
            "coverage": coverage,
            "entries": entries,
            "merge_history": history,
        }
    )
    addendum["status"] = "CANDIDATE_ENTRY_MERGED_INTO_CENTRAL_REGISTRY"
    addendum["merge_metadata"] = {
        "merged_into": REGISTRY.relative_to(ROOT).as_posix(),
        "merged_on": date.today().isoformat(),
        "equation_ids": [entry.get("equation_id") for entry in addendum_entries],
        "claim_promotion": False,
    }
    ADDENDUM.write_text(json.dumps(addendum, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REGISTRY.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"merged": merged, "already_present": already_present, "conflicts": conflicts, "entries": len(entries)}, indent=2))
    return 0 if not conflicts else 1


if __name__ == "__main__":
    raise SystemExit(main())
