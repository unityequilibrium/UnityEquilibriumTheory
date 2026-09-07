"""Merge reviewed equation-registry addenda without promoting their claims.

The central registry is the machine-readable index for the foundation workflow.
Addenda remain candidate records; this script only makes their membership explicit
and repeatable. It never changes an addendum's evidence class or claim boundary.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry.json"
ADDENDA = (
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_impact_effect_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_cosmology_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_persistence_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_wave_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_sunset_width_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_contact_sk_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_current_correlator_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_tree_level_charged_ward_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_thermodynamic_normal_component_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_condensed_relative_flow_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_continuum_relative_flow_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_condensed_loop_vertex_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_mass_density_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_main_theory_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_coarse_graining_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_open_system_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_theory_spine_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_quantum_measurement_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_quantum_interpretations_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_gr_controls_addendum.json",
    ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_dynamical_stability_addendum.json",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    registry = read_json(REGISTRY)
    entries = list(registry.get("entries", []))
    known = {entry.get("equation_id") for entry in entries}
    merged: list[str] = []
    skipped: list[str] = []
    conflicts: list[str] = []

    for path in ADDENDA:
        addendum = read_json(path)
        newly_merged_for_addendum: list[str] = []
        addendum_entries = addendum.get("equation_entries", addendum.get("entries", []))
        for entry in addendum_entries:
            equation_id = entry.get("equation_id")
            if not equation_id:
                conflicts.append(f"{path.name}:missing_equation_id")
                continue
            if equation_id in known:
                skipped.append(equation_id)
                continue
            entries.append(entry)
            known.add(equation_id)
            merged.append(equation_id)
            newly_merged_for_addendum.append(equation_id)

        previous_metadata = dict(addendum.get("merge_metadata", {}))
        previous_date = previous_metadata.get("merged_on")
        merged_on = (
            previous_date
            if previous_date and not newly_merged_for_addendum
            else date.today().isoformat()
        )

        addendum["status"] = "CANDIDATE_ENTRY_MERGED_INTO_CENTRAL_REGISTRY"
        addendum["merge_metadata"] = {
            "merged_into": str(REGISTRY.relative_to(ROOT)).replace("\\", "/"),
            "merged_on": merged_on,
            "equation_ids": [entry.get("equation_id") for entry in addendum_entries],
            "claim_promotion": False,
        }
        path.write_text(json.dumps(addendum, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    coverage = dict(registry.get("coverage", {}))
    missing_scope = list(coverage.get("missing_scope", []))
    required_gap = "complete impact/effect/carrier and cosmological lane correspondence"
    if required_gap not in missing_scope:
        missing_scope.append(required_gap)
    coverage.update(
        {
            "coverage_status": "INITIAL_SEED_NOT_EXHAUSTIVE",
            "extension_status": "CANDIDATE_ADDENDA_MERGED_NOT_EXHAUSTIVE",
            "addenda_merged": [path.relative_to(ROOT).as_posix() for path in ADDENDA],
            "missing_scope": missing_scope,
            "rule": "merged candidate addenda do not promote downstream claims while foundation gates remain blocked",
        }
    )
    registry.update(
        {
            "schema_version": "1.1",
            "generated_at": date.today().isoformat(),
            "status": "CENTRAL_REGISTRY_WITH_CANDIDATE_ADDENDA_BLOCKED",
            "coverage": coverage,
            "entries": entries,
            "merge_history": {
                "merged_equation_ids": merged,
                "already_present": skipped,
                "conflicts": conflicts,
                "source_policy": "addenda are merged as candidate records; evidence and claim boundaries are preserved",
            },
        }
    )
    REGISTRY.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"merged={len(merged)}")
    print(f"already_present={len(skipped)}")
    print(f"conflicts={len(conflicts)}")
    print(f"entries={len(entries)}")
    return 0 if not conflicts else 1


if __name__ == "__main__":
    raise SystemExit(main())
