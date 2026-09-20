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
    "'T13_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR': 'tpg_anisotropic_alpha_v_comparator',",
    "'T13_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR': 'tpg_anisotropic_alpha_v_comparator', 'T13_NATURAL_GRAPHITE_NELSON_RILEY_ALPHA_V_COMPARATOR': 'natural_graphite_nelson_riley_alpha_v_comparator',",
    "registry mapping",
)
replace_once(
    '    tpg_alpha_v_path, tpg_alpha_v = load(\n        "docs/core/07_artifacts/topic13/t13_tpg_anisotropic_alpha_v_source_audit.json"\n    )\n',
    '    tpg_alpha_v_path, tpg_alpha_v = load(\n        "docs/core/07_artifacts/topic13/t13_tpg_anisotropic_alpha_v_source_audit.json"\n    )\n    natural_alpha_v_path, natural_alpha_v = load(\n        "docs/core/07_artifacts/topic13/t13_natural_graphite_nelson_riley_alpha_v_source_audit.json"\n    )\n',
    "natural graphite alpha_V artifact load",
)
replace_once(
    '    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    '    natural_alpha_v_lane = discovered_lane_integrations.get(\n        "natural_graphite_nelson_riley_alpha_v_comparator"\n    )\n    if natural_alpha_v_lane:\n        artifact["verification_status"]["source_package"][\n            "natural_graphite_nelson_riley_alpha_v_comparator"\n        ] = natural_alpha_v_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "natural_graphite_nelson_riley_alpha_v_comparator", None\n        )\n    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    "natural graphite alpha_V source lane projection",
)
replace_once(
    '    if discovered_lane_integrations.get("tpg_anisotropic_alpha_v_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("IHEP TPG anisotropic alpha_V comparator is closed for lane without same-specimen K_T or Ding material-match promotion")\n',
    '    if discovered_lane_integrations.get("tpg_anisotropic_alpha_v_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("IHEP TPG anisotropic alpha_V comparator is closed for lane without same-specimen K_T or Ding material-match promotion")\n    if discovered_lane_integrations.get("natural_graphite_nelson_riley_alpha_v_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("official Nelson-Riley natural/crystalline graphite alpha_V comparator is closed for lane without matched uncertainty or Ding material-match promotion")\n',
    "closure summary",
)
replace_once(
    '    isothermal_kt_rel = rel(isothermal_kt_path)\n',
    '    natural_alpha_v_rel = rel(natural_alpha_v_path)\n    if natural_alpha_v_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                natural_alpha_v_rel,\n                natural_alpha_v,\n                {\n                    "status": natural_alpha_v.get("status"),\n                    "closure_level": natural_alpha_v.get("major_result", {}).get("closure_level"),\n                    "data_role": natural_alpha_v.get("major_result", {}).get("data_role"),\n                    "alpha_V_per_K": natural_alpha_v.get("derived_comparator", {}).get("alpha_V_per_K"),\n                    "alpha_V_uncertainty_per_K": natural_alpha_v.get("derived_comparator", {}).get("alpha_V_uncertainty_per_K"),\n                    "same_specimen_alpha_V": natural_alpha_v.get("derived_comparator", {}).get("same_specimen_alpha_V"),\n                },\n            )\n        )\n    isothermal_kt_rel = rel(isothermal_kt_path)\n',
    "natural graphite alpha_V evidence",
)
path.write_text(text, encoding="utf-8")
print("integrated natural/crystalline graphite Nelson-Riley alpha_V comparator into Topic 13 full gate")
