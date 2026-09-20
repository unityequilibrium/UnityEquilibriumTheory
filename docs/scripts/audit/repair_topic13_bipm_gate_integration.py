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
        "'T13_NATURAL_GRAPHITE_NELSON_RILEY_ALPHA_V_COMPARATOR': 'natural_graphite_nelson_riley_alpha_v_comparator', 'T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR'",
        "'T13_NATURAL_GRAPHITE_NELSON_RILEY_ALPHA_V_COMPARATOR': 'natural_graphite_nelson_riley_alpha_v_comparator', 'T13_BIPM_SPECIFIC_HEAT_CP_COMPARATOR': 'bipm_specific_heat_cp_comparator', 'T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR'",
        "lane registry",
    )
    text = replace_once(
        text,
        '    natural_alpha_v_path, natural_alpha_v = load(\n        "docs/core/07_artifacts/topic13/t13_natural_graphite_nelson_riley_alpha_v_source_audit.json"\n    )\n    phi_e_comparator_path, phi_e_comparator = load(',
        '    natural_alpha_v_path, natural_alpha_v = load(\n        "docs/core/07_artifacts/topic13/t13_natural_graphite_nelson_riley_alpha_v_source_audit.json"\n    )\n    bipm_specific_heat_path, bipm_specific_heat = load(\n        "docs/core/07_artifacts/topic13/t13_bipm_specific_heat_source_audit.json"\n    )\n    bipm_package_path, bipm_package = load(\n        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/bipm_2006_01_graphite_specific_heat_source_package.json"\n    )\n    phi_e_comparator_path, phi_e_comparator = load(',
        "BIPM source loading",
    )
    text = replace_once(
        text,
        '    natural_alpha_v_lane = discovered_lane_integrations.get(\n        "natural_graphite_nelson_riley_alpha_v_comparator"\n    )\n    if natural_alpha_v_lane:\n        artifact["verification_status"]["source_package"][\n            "natural_graphite_nelson_riley_alpha_v_comparator"\n        ] = natural_alpha_v_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "natural_graphite_nelson_riley_alpha_v_comparator", None\n        )\n    oxford_source_lane = discovered_lane_integrations.get(',
        '    natural_alpha_v_lane = discovered_lane_integrations.get(\n        "natural_graphite_nelson_riley_alpha_v_comparator"\n    )\n    if natural_alpha_v_lane:\n        artifact["verification_status"]["source_package"][\n            "natural_graphite_nelson_riley_alpha_v_comparator"\n        ] = natural_alpha_v_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "natural_graphite_nelson_riley_alpha_v_comparator", None\n        )\n    bipm_specific_heat_lane = discovered_lane_integrations.get(\n        "bipm_specific_heat_cp_comparator"\n    )\n    if bipm_specific_heat_lane:\n        artifact["verification_status"]["source_package"][\n            "bipm_specific_heat_cp_comparator"\n        ] = bipm_specific_heat_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "bipm_specific_heat_cp_comparator", None\n        )\n    oxford_source_lane = discovered_lane_integrations.get(',
        "BIPM source projection",
    )
    text = replace_once(
        text,
        '    natural_alpha_v_rel = rel(natural_alpha_v_path)\n    if natural_alpha_v_rel not in {',
        '    natural_alpha_v_rel = rel(natural_alpha_v_path)\n    if natural_alpha_v_rel not in {',
        "natural evidence anchor",
    )
    natural_block = '''        artifact["evidence_artifacts"].append(\n            evidence(\n                natural_alpha_v_rel,\n                natural_alpha_v,\n                {\n                    "status": natural_alpha_v.get("status"),\n                    "closure_level": natural_alpha_v.get("major_result", {}).get("closure_level"),\n                    "data_role": natural_alpha_v.get("major_result", {}).get("data_role"),\n                    "alpha_V_per_K": natural_alpha_v.get("derived_comparator", {}).get("alpha_V_per_K"),\n                    "alpha_V_uncertainty_per_K": natural_alpha_v.get("derived_comparator", {}).get("alpha_V_uncertainty_per_K"),\n                    "same_specimen_alpha_V": natural_alpha_v.get("derived_comparator", {}).get("same_specimen_alpha_V"),\n                },\n            )\n        )\n'''
    bipm_block = natural_block + '''    bipm_specific_heat_rel = rel(bipm_specific_heat_path)\n    if bipm_specific_heat_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                bipm_specific_heat_rel,\n                bipm_specific_heat,\n                {\n                    "status": bipm_specific_heat.get("status"),\n                    "closure_level": bipm_specific_heat.get("major_result", {}).get("closure_level"),\n                    "data_role": bipm_specific_heat.get("major_result", {}).get("data_role"),\n                    "volumetric_cp_J_per_m3_K": bipm_specific_heat.get("derived_comparator", {}).get("volumetric_cp_J_per_m3_K"),\n                    "volumetric_cp_uncertainty_J_per_m3_K": bipm_specific_heat.get("derived_comparator", {}).get("volumetric_cp_standard_uncertainty_J_per_m3_K"),\n                    "cv_emitted": bipm_specific_heat.get("derived_comparator", {}).get("cv_emitted"),\n                    "controlling_blocker": bipm_specific_heat.get("controlling_blocker"),\n                },\n            )\n        )\n    bipm_package_rel = rel(bipm_package_path)\n    if bipm_package_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                bipm_package_rel,\n                bipm_package,\n                {\n                    "status": bipm_package.get("status"),\n                    "data_role": "COMPARISON_ONLY_NOT_CALIBRATION",\n                    "raw_sha256": bipm_package.get("source", {}).get("local_raw_sha256"),\n                    "material_match_to_Ding_TTG": bipm_package.get("derived_comparator", {}).get("material_match_to_Ding_TTG"),\n                },\n            )\n        )\n'''
    text = replace_once(text, natural_block, bipm_block, "BIPM evidence projection")
    text = replace_once(
        text,
        '    if discovered_lane_integrations.get("natural_graphite_nelson_riley_alpha_v_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("official Nelson-Riley natural/crystalline graphite alpha_V comparator is closed for lane without matched uncertainty or Ding material-match promotion")\n    if discovered_lane_integrations.get("mp48_phi_e_dimensional_anchor_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":',
        '    if discovered_lane_integrations.get("natural_graphite_nelson_riley_alpha_v_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("official Nelson-Riley natural/crystalline graphite alpha_V comparator is closed for lane without matched uncertainty or Ding material-match promotion")\n    if discovered_lane_integrations.get("bipm_specific_heat_cp_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("BIPM ultra-pure graphite volumetric c_p comparator is closed for lane without c_v conversion or Ding material-match promotion")\n    if discovered_lane_integrations.get("mp48_phi_e_dimensional_anchor_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":',
        "BIPM closure summary",
    )
    FULL_GATE_SCRIPT.write_text(text, encoding="utf-8")

    register = REGISTER_SCRIPT.read_text(encoding="utf-8")
    register = replace_once(
        register,
        '    (\n        "T13_NATURAL_GRAPHITE_NELSON_RILEY_ALPHA_V_COMPARATOR",\n        "natural_graphite_nelson_riley_alpha_v_comparator",\n    ),\n)',
        '    (\n        "T13_NATURAL_GRAPHITE_NELSON_RILEY_ALPHA_V_COMPARATOR",\n        "natural_graphite_nelson_riley_alpha_v_comparator",\n    ),\n    ("T13_BIPM_SPECIFIC_HEAT_CP_COMPARATOR", "bipm_specific_heat_cp_comparator"),\n)',
        "register lane list",
    )
    REGISTER_SCRIPT.write_text(register, encoding="utf-8")
    print("integrated BIPM source lane into Topic 13 full gate and register sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
