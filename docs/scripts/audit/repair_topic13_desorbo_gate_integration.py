"""Integrate the DeSorbo Ceylon graphite Cp lane into Topic 13 metadata."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FULL_GATE_SCRIPT = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"
REGISTER_SCRIPT = ROOT / "docs/scripts/audit/sync_topic13_major_result_lanes.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    text = FULL_GATE_SCRIPT.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "'T13_OXFORD_TGS_NUMERIC_ROWS_COMPARATOR': 'oxford_tgs_numeric_rows_comparator'}",
        "'T13_OXFORD_TGS_NUMERIC_ROWS_COMPARATOR': 'oxford_tgs_numeric_rows_comparator', 'T13_DESORBO_1955_CEYLON_GRAPHITE_CP_COMPARATOR': 'desorbo_1955_ceylon_graphite_cp_comparator'}",
        "lane registry",
    )
    text = replace_once(
        text,
        '    oxford_numeric_path, oxford_numeric = load(\n        "docs/core/07_artifacts/topic13/t13_oxford_tgs_numeric_rows_audit.json"\n    )\n    material_boundary_path, material_boundary = load(',
        '    oxford_numeric_path, oxford_numeric = load(\n        "docs/core/07_artifacts/topic13/t13_oxford_tgs_numeric_rows_audit.json"\n    )\n    desorbo_ceylon_path, desorbo_ceylon = load(\n        "docs/core/07_artifacts/topic13/t13_desorbo_ceylon_graphite_cp_audit.json"\n    )\n    desorbo_ceylon_package_path, desorbo_ceylon_package = load(\n        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/desorbo_1955_ceylon_graphite_cp_source_package.json"\n    )\n    material_boundary_path, material_boundary = load(',
        "DeSorbo source loading",
    )
    text = replace_once(
        text,
        '    iaea_graphite_cv_lane = discovered_lane_integrations.get(\n        "iaea_graphite_table_cv_comparator"\n    )\n',
        '    desorbo_ceylon_lane = discovered_lane_integrations.get(\n        "desorbo_1955_ceylon_graphite_cp_comparator"\n    )\n    if desorbo_ceylon_lane:\n        artifact["verification_status"]["source_package"][\n            "desorbo_1955_ceylon_graphite_cp_comparator"\n        ] = desorbo_ceylon_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "desorbo_1955_ceylon_graphite_cp_comparator", None\n        )\n    iaea_graphite_cv_lane = discovered_lane_integrations.get(\n        "iaea_graphite_table_cv_comparator"\n    )\n',
        "DeSorbo source projection",
    )
    text = replace_once(
        text,
        '    if discovered_lane_integrations.get("iaea_graphite_table_cv_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("IAEA manufactured-graphite table-derived mass-specific c_v comparator is closed for lane without source-grade uncertainty, density conversion, or Ding material-match promotion")\n',
        '    if discovered_lane_integrations.get("iaea_graphite_table_cv_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("IAEA manufactured-graphite table-derived mass-specific c_v comparator is closed for lane without source-grade uncertainty, density conversion, or Ding material-match promotion")\n    if discovered_lane_integrations.get("desorbo_1955_ceylon_graphite_cp_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("DeSorbo 1955 Ceylon natural-graphite numeric Cp comparator is closed for lane without standard uncertainty, volumetric c_v conversion, or Ding material-match promotion")\n',
        "DeSorbo closure summary",
    )
    evidence_anchor = '    iaea_graphite_cv_rel = rel(iaea_graphite_cv_path)\n'
    desorbo_evidence = '''    desorbo_ceylon_rel = rel(desorbo_ceylon_path)
    if desorbo_ceylon_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                desorbo_ceylon_rel,
                desorbo_ceylon,
                {
                    "status": desorbo_ceylon.get("status"),
                    "closure_level": desorbo_ceylon.get("major_result", {}).get("closure_level"),
                    "data_role": desorbo_ceylon.get("major_result", {}).get("data_role"),
                    "numeric_cp_J_per_mol_K": desorbo_ceylon.get("source_row", {}).get("value_J_per_mol_K"),
                    "volumetric_cv_emitted": desorbo_ceylon.get("volumetric_cv_emitted"),
                    "controlling_blocker": desorbo_ceylon.get("controlling_blocker"),
                },
            )
        )
    desorbo_ceylon_package_rel = rel(desorbo_ceylon_package_path)
    if desorbo_ceylon_package_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                desorbo_ceylon_package_rel,
                desorbo_ceylon_package,
                {
                    "status": desorbo_ceylon_package.get("status"),
                    "data_role": desorbo_ceylon_package.get("source_row", {}).get("data_role"),
                    "raw_sha256": desorbo_ceylon_package.get("source", {}).get("local_raw_sha256"),
                    "standard_uncertainty": desorbo_ceylon_package.get("uncertainty_boundary", {}).get("standard_uncertainty_value"),
                    "conversion_status": desorbo_ceylon_package.get("required_quantity_contract", {}).get("conversion_status"),
                },
            )
        )
'''
    text = replace_once(text, evidence_anchor, desorbo_evidence + evidence_anchor, "DeSorbo evidence projection")
    FULL_GATE_SCRIPT.write_text(text, encoding="utf-8")

    register = REGISTER_SCRIPT.read_text(encoding="utf-8")
    register = replace_once(
        register,
        '    ("T13_OXFORD_TGS_NUMERIC_ROWS_COMPARATOR", "oxford_tgs_numeric_rows_comparator"),\n',
        '    ("T13_OXFORD_TGS_NUMERIC_ROWS_COMPARATOR", "oxford_tgs_numeric_rows_comparator"),\n    ("T13_DESORBO_1955_CEYLON_GRAPHITE_CP_COMPARATOR", "desorbo_1955_ceylon_graphite_cp_comparator"),\n',
        "register lane list",
    )
    REGISTER_SCRIPT.write_text(register, encoding="utf-8")
    print("integrated DeSorbo Ceylon graphite Cp lane into Topic 13 full gate and register sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
