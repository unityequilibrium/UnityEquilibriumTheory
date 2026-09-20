"""Expose raw-author provenance status in the canonical Topic 13 source gate."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    text = TARGET.read_text(encoding="utf-8-sig")
    if "ding_source_mapping_path, ding_source_mapping" in text:
        print("FULL_GATE_SOURCE_PROVENANCE_FIELD_ALREADY_PRESENT")
        return 0

    text = replace_once(
        text,
        '    source_package_path, source_package = load(\n'
        '        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json"\n'
        '    )\n',
        '    source_package_path, source_package = load(\n'
        '        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json"\n'
        '    )\n'
        '    ding_source_mapping_path, ding_source_mapping = load(\n'
        '        "docs/core/07_artifacts/provenance/ding_2022_source_mapping_audit.json"\n'
        '    )\n',
        "full-gate Ding source input",
    )
    text = replace_once(
        text,
        '            "source_ready_for_full_closure": source_ready,\n'
        '            "provisional_source_present": bool(source_contract.get("provisional_source_present")),\n'
        '            "numeric_fitting_allowed": bool(source_contract.get("numeric_fitting_allowed")),\n',
        '            "source_ready_for_full_closure": source_ready,\n'
        '            "provisional_source_present": bool(source_contract.get("provisional_source_present")),\n'
        '            "raw_author_numeric_source_present": bool(\n'
        '                ding_source_mapping.get("checks", {}).get("raw_author_numeric_source_present", False)\n'
        '            ),\n'
        '            "figure_derived_numeric_route_ready": bool(\n'
        '                ding_source_mapping.get("checks", {}).get("permitted_figure_numeric_route_ready", False)\n'
        '            ),\n'
        '            "numeric_fitting_allowed": bool(source_contract.get("numeric_fitting_allowed")),\n',
        "full-gate source provenance fields",
    )
    text = replace_once(
        text,
        '            evidence(rel(source_package_path), source_package, {"status": source_package.get("status")}),\n',
        '            evidence(rel(source_package_path), source_package, {"status": source_package.get("status")}),\n'
        '            evidence(rel(ding_source_mapping_path), ding_source_mapping, {\n'
        '                "status": ding_source_mapping.get("status"),\n'
        '                "raw_author_numeric_source_present": ding_source_mapping.get("checks", {}).get("raw_author_numeric_source_present"),\n'
        '                "permitted_figure_numeric_route_ready": ding_source_mapping.get("checks", {}).get("permitted_figure_numeric_route_ready"),\n'
        '            }),\n',
        "full-gate Ding source evidence",
    )
    TARGET.write_text(text, encoding="utf-8")
    print("ADDED_FULL_GATE_SOURCE_PROVENANCE_FIELD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
