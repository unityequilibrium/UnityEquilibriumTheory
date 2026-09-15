from pathlib import Path


path = Path("docs/scripts/audit/audit_topic13_full_bridge_gate.py")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    text = text.replace(old, new)


replace_once(
    "'T13_GRAPHITE_ISOTHERMAL_KT_SOURCE': 'graphite_isothermal_kt_source',",
    "'T13_GRAPHITE_ISOTHERMAL_KT_SOURCE': 'graphite_isothermal_kt_source', 'T13_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR': 'tpg_anisotropic_alpha_v_comparator',",
    "registry mapping",
)
replace_once(
    '    isothermal_kt_path, isothermal_kt = load(\n        "docs/core/07_artifacts/topic13/t13_graphite_isothermal_kt_source_audit.json"\n    )\n',
    '    isothermal_kt_path, isothermal_kt = load(\n        "docs/core/07_artifacts/topic13/t13_graphite_isothermal_kt_source_audit.json"\n    )\n    tpg_alpha_v_path, tpg_alpha_v = load(\n        "docs/core/07_artifacts/topic13/t13_tpg_anisotropic_alpha_v_source_audit.json"\n    )\n',
    "TPG alpha_V artifact load",
)
replace_once(
    '    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    '    tpg_alpha_v_lane = discovered_lane_integrations.get(\n        "tpg_anisotropic_alpha_v_comparator"\n    )\n    if tpg_alpha_v_lane:\n        artifact["verification_status"]["source_package"][\n            "tpg_anisotropic_alpha_v_comparator"\n        ] = tpg_alpha_v_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "tpg_anisotropic_alpha_v_comparator", None\n        )\n    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    "TPG alpha_V source lane projection",
)
replace_once(
    '    if discovered_lane_integrations.get("graphite_isothermal_kt_source", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Hanfland 300 K graphite isothermal K_T source is closed for lane without same-grade alpha_V or Ding material-match promotion")\n',
    '    if discovered_lane_integrations.get("graphite_isothermal_kt_source", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Hanfland 300 K graphite isothermal K_T source is closed for lane without same-grade alpha_V or Ding material-match promotion")\n    if discovered_lane_integrations.get("tpg_anisotropic_alpha_v_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("IHEP TPG anisotropic alpha_V comparator is closed for lane without same-specimen K_T or Ding material-match promotion")\n',
    "closure summary",
)
replace_once(
    '    isothermal_kt_rel = rel(isothermal_kt_path)\n',
    '    tpg_alpha_v_rel = rel(tpg_alpha_v_path)\n    if tpg_alpha_v_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                tpg_alpha_v_rel,\n                tpg_alpha_v,\n                {\n                    "status": tpg_alpha_v.get("status"),\n                    "closure_level": tpg_alpha_v.get("major_result", {}).get("closure_level"),\n                    "data_role": tpg_alpha_v.get("major_result", {}).get("data_role"),\n                    "alpha_V_per_K": tpg_alpha_v.get("derived_comparator", {}).get("alpha_V_per_K"),\n                    "alpha_V_uncertainty_per_K": tpg_alpha_v.get("derived_comparator", {}).get("alpha_V_uncertainty_per_K"),\n                    "same_specimen_alpha_V": tpg_alpha_v.get("derived_comparator", {}).get("same_specimen_alpha_V"),\n                },\n            )\n        )\n    isothermal_kt_rel = rel(isothermal_kt_path)\n',
    "TPG alpha_V evidence",
)
path.write_text(text, encoding="utf-8")
print("integrated TPG anisotropic alpha_V comparator into Topic 13 full gate")
