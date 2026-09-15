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
        "'T13_BIPM_SPECIFIC_HEAT_CP_COMPARATOR': 'bipm_specific_heat_cp_comparator', 'T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR'",
        "'T13_BIPM_SPECIFIC_HEAT_CP_COMPARATOR': 'bipm_specific_heat_cp_comparator', 'T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR': 'iaea_graphite_table_cv_comparator', 'T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR'",
        "lane registry",
    )
    text = replace_once(
        text,
        '    bipm_package_path, bipm_package = load(\n        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/bipm_2006_01_graphite_specific_heat_source_package.json"\n    )\n    phi_e_comparator_path, phi_e_comparator = load(',
        '    bipm_package_path, bipm_package = load(\n        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/bipm_2006_01_graphite_specific_heat_source_package.json"\n    )\n    iaea_graphite_cv_path, iaea_graphite_cv = load(\n        "docs/core/07_artifacts/topic13/t13_iaea_graphite_constant_volume_source_audit.json"\n    )\n    iaea_graphite_cv_package_path, iaea_graphite_cv_package = load(\n        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/iaea_graphite_handbook_constant_volume_source_package.json"\n    )\n    phi_e_comparator_path, phi_e_comparator = load(',
        "IAEA source loading",
    )
    text = replace_once(
        text,
        '    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )',
        '    iaea_graphite_cv_lane = discovered_lane_integrations.get(\n        "iaea_graphite_table_cv_comparator"\n    )\n    if iaea_graphite_cv_lane:\n        artifact["verification_status"]["source_package"][\n            "iaea_graphite_table_cv_comparator"\n        ] = iaea_graphite_cv_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "iaea_graphite_table_cv_comparator", None\n        )\n    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )',
        "IAEA source projection",
    )
    text = replace_once(
        text,
        '    if discovered_lane_integrations.get("bipm_specific_heat_cp_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("BIPM ultra-pure graphite volumetric c_p comparator is closed for lane without c_v conversion or Ding material-match promotion")\n    if discovered_lane_integrations.get("mp48_phi_e_dimensional_anchor_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":',
        '    if discovered_lane_integrations.get("bipm_specific_heat_cp_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("BIPM ultra-pure graphite volumetric c_p comparator is closed for lane without c_v conversion or Ding material-match promotion")\n    if discovered_lane_integrations.get("iaea_graphite_table_cv_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("IAEA manufactured-graphite table-derived mass-specific c_v comparator is closed for lane without source-grade uncertainty, density conversion, or Ding material-match promotion")\n    if discovered_lane_integrations.get("mp48_phi_e_dimensional_anchor_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":',
        "IAEA closure summary",
    )
    bipm_package_evidence = '''    bipm_package_rel = rel(bipm_package_path)\n    if bipm_package_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                bipm_package_rel,\n                bipm_package,\n                {\n                    "status": bipm_package.get("status"),\n                    "data_role": "COMPARISON_ONLY_NOT_CALIBRATION",\n                    "raw_sha256": bipm_package.get("source", {}).get("local_raw_sha256"),\n                    "material_match_to_Ding_TTG": bipm_package.get("derived_comparator", {}).get("material_match_to_Ding_TTG"),\n                },\n            )\n        )\n'''
    iaea_evidence = bipm_package_evidence + '''    iaea_graphite_cv_rel = rel(iaea_graphite_cv_path)\n    if iaea_graphite_cv_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                iaea_graphite_cv_rel,\n                iaea_graphite_cv,\n                {\n                    "status": iaea_graphite_cv.get("status"),\n                    "closure_level": iaea_graphite_cv.get("major_result", {}).get("closure_level"),\n                    "data_role": iaea_graphite_cv.get("major_result", {}).get("data_role"),\n                    "cv_mass_J_per_kg_K": iaea_graphite_cv.get("derived_comparator", {}).get("cv_mass_J_per_kg_K"),\n                    "cv_standard_uncertainty_J_per_kg_K": iaea_graphite_cv.get("derived_comparator", {}).get("cv_standard_uncertainty_J_per_kg_K"),\n                    "cv_volumetric_emitted": iaea_graphite_cv.get("derived_comparator", {}).get("cv_volumetric_emitted"),\n                    "controlling_blocker": iaea_graphite_cv.get("controlling_blocker"),\n                },\n            )\n        )\n    iaea_graphite_cv_package_rel = rel(iaea_graphite_cv_package_path)\n    if iaea_graphite_cv_package_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                iaea_graphite_cv_package_rel,\n                iaea_graphite_cv_package,\n                {\n                    "status": iaea_graphite_cv_package.get("status"),\n                    "data_role": "COMPARISON_ONLY_NOT_CALIBRATION",\n                    "raw_sha256": iaea_graphite_cv_package.get("source", {}).get("local_raw_sha256"),\n                    "material_match_to_Ding_TTG": iaea_graphite_cv_package.get("derived_comparator", {}).get("material_match_to_Ding_TTG"),\n                },\n            )\n        )\n'''
    text = replace_once(text, bipm_package_evidence, iaea_evidence, "IAEA evidence projection")
    FULL_GATE_SCRIPT.write_text(text, encoding="utf-8")

    register = REGISTER_SCRIPT.read_text(encoding="utf-8")
    register = replace_once(
        register,
        '    ("T13_BIPM_SPECIFIC_HEAT_CP_COMPARATOR", "bipm_specific_heat_cp_comparator"),\n)',
        '    ("T13_BIPM_SPECIFIC_HEAT_CP_COMPARATOR", "bipm_specific_heat_cp_comparator"),\n    ("T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR", "iaea_graphite_table_cv_comparator"),\n)',
        "register lane list",
    )
    REGISTER_SCRIPT.write_text(register, encoding="utf-8")
    print("integrated IAEA c_v comparator into Topic 13 full gate and register sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
