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
        "'T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR': 'iaea_graphite_table_cv_comparator', 'T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR'",
        "'T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR': 'iaea_graphite_table_cv_comparator', 'T13_DING_MATERIAL_REGIME_BOUNDARY': 'ding_material_regime_boundary', 'T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR'",
        "lane registry",
    )
    text = replace_once(
        text,
        '    iaea_graphite_cv_package_path, iaea_graphite_cv_package = load(\n        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/iaea_graphite_handbook_constant_volume_source_package.json"\n    )\n    phi_e_comparator_path, phi_e_comparator = load(',
        '    iaea_graphite_cv_package_path, iaea_graphite_cv_package = load(\n        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/iaea_graphite_handbook_constant_volume_source_package.json"\n    )\n    material_boundary_path, material_boundary = load(\n        "docs/core/07_artifacts/topic13/t13_ding_material_regime_boundary_audit.json"\n    )\n    material_boundary_package_path, material_boundary_package = load(\n        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_graphite_material_regime_boundary_source_package.json"\n    )\n    phi_e_comparator_path, phi_e_comparator = load(',
        "material boundary source loading",
    )
    text = replace_once(
        text,
        '    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )',
        '    material_boundary_lane = discovered_lane_integrations.get(\n        "ding_material_regime_boundary"\n    )\n    if material_boundary_lane:\n        artifact["verification_status"]["source_package"][\n            "ding_material_regime_boundary"\n        ] = material_boundary_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "ding_material_regime_boundary", None\n        )\n    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )',
        "material boundary source projection",
    )
    text = replace_once(
        text,
        '    if discovered_lane_integrations.get("iaea_graphite_table_cv_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("IAEA manufactured-graphite table-derived mass-specific c_v comparator is closed for lane without source-grade uncertainty, density conversion, or Ding material-match promotion")\n    if discovered_lane_integrations.get("mp48_phi_e_dimensional_anchor_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":',
        '    if discovered_lane_integrations.get("iaea_graphite_table_cv_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("IAEA manufactured-graphite table-derived mass-specific c_v comparator is closed for lane without source-grade uncertainty, density conversion, or Ding material-match promotion")\n    if discovered_lane_integrations.get("ding_material_regime_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Ding/comparator material-regime equivalence is closed as a scoped no-go; comparator c_v and c_p lanes cannot substitute for Ding C_src")\n    if discovered_lane_integrations.get("mp48_phi_e_dimensional_anchor_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":',
        "material boundary closure summary",
    )
    iaea_package_evidence = '''    iaea_graphite_cv_package_rel = rel(iaea_graphite_cv_package_path)\n    if iaea_graphite_cv_package_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                iaea_graphite_cv_package_rel,\n                iaea_graphite_cv_package,\n                {\n                    "status": iaea_graphite_cv_package.get("status"),\n                    "data_role": "COMPARISON_ONLY_NOT_CALIBRATION",\n                    "raw_sha256": iaea_graphite_cv_package.get("source", {}).get("local_raw_sha256"),\n                    "material_match_to_Ding_TTG": iaea_graphite_cv_package.get("derived_comparator", {}).get("material_match_to_Ding_TTG"),\n                },\n            )\n        )\n'''
    boundary_evidence = iaea_package_evidence + '''    material_boundary_rel = rel(material_boundary_path)\n    if material_boundary_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                material_boundary_rel,\n                material_boundary,\n                {\n                    "status": material_boundary.get("status"),\n                    "closure_level": material_boundary.get("major_result", {}).get("closure_level"),\n                    "data_role": material_boundary.get("major_result", {}).get("data_role"),\n                    "equivalence_result": material_boundary.get("mapping_contract", {}).get("equivalence_result"),\n                    "comparator_count": len(material_boundary.get("source", {}).get("comparators", [])),\n                    "controlling_blocker": material_boundary.get("controlling_blocker"),\n                },\n            )\n        )\n    material_boundary_package_rel = rel(material_boundary_package_path)\n    if material_boundary_package_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                material_boundary_package_rel,\n                material_boundary_package,\n                {\n                    "status": material_boundary_package.get("status"),\n                    "data_role": "SOURCE_PROVENANCE_BOUNDARY_NOT_CALIBRATION",\n                    "equivalence_result": material_boundary_package.get("mapping_contract", {}).get("equivalence_result"),\n                },\n            )\n        )\n'''
    text = replace_once(text, iaea_package_evidence, boundary_evidence, "material boundary evidence projection")
    FULL_GATE_SCRIPT.write_text(text, encoding="utf-8")

    register = REGISTER_SCRIPT.read_text(encoding="utf-8")
    register = replace_once(
        register,
        '    ("T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR", "iaea_graphite_table_cv_comparator"),\n)',
        '    ("T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR", "iaea_graphite_table_cv_comparator"),\n    ("T13_DING_MATERIAL_REGIME_BOUNDARY", "ding_material_regime_boundary"),\n)',
        "register lane list",
    )
    REGISTER_SCRIPT.write_text(register, encoding="utf-8")
    print("integrated Ding material-regime boundary into Topic 13 full gate and register sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
