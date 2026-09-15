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
    "'T13_GRAPHITE_ELASTIC_BULK_MODULUS_SOURCE': 'graphite_elastic_bulk_modulus_source',",
    "'T13_GRAPHITE_ELASTIC_BULK_MODULUS_SOURCE': 'graphite_elastic_bulk_modulus_source', 'T13_GRAPHITE_ISOTHERMAL_KT_SOURCE': 'graphite_isothermal_kt_source',",
    "registry mapping",
)
replace_once(
    '    elastic_bulk_path, elastic_bulk = load(\n        "docs/core/07_artifacts/topic13/t13_graphite_elastic_bulk_modulus_source_audit.json"\n    )\n',
    '    elastic_bulk_path, elastic_bulk = load(\n        "docs/core/07_artifacts/topic13/t13_graphite_elastic_bulk_modulus_source_audit.json"\n    )\n    isothermal_kt_path, isothermal_kt = load(\n        "docs/core/07_artifacts/topic13/t13_graphite_isothermal_kt_source_audit.json"\n    )\n',
    "isothermal K_T artifact load",
)
replace_once(
    '    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    '    isothermal_kt_lane = discovered_lane_integrations.get(\n        "graphite_isothermal_kt_source"\n    )\n    if isothermal_kt_lane:\n        artifact["verification_status"]["source_package"][\n            "graphite_isothermal_kt_source"\n        ] = isothermal_kt_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "graphite_isothermal_kt_source", None\n        )\n    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    "source lane projection",
)
replace_once(
    '    if discovered_lane_integrations.get("graphite_elastic_bulk_modulus_source", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Bosak single-crystal graphite elastic bulk comparator is closed for lane without isothermal K_T or Ding material-match promotion")\n',
    '    if discovered_lane_integrations.get("graphite_elastic_bulk_modulus_source", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Bosak single-crystal graphite elastic bulk comparator is closed for lane without isothermal K_T or Ding material-match promotion")\n    if discovered_lane_integrations.get("graphite_isothermal_kt_source", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Hanfland 300 K graphite isothermal K_T source is closed for lane without same-grade alpha_V or Ding material-match promotion")\n',
    "closure summary",
)
replace_once(
    '    elastic_bulk_rel = rel(elastic_bulk_path)\n',
    '    isothermal_kt_rel = rel(isothermal_kt_path)\n    if isothermal_kt_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                isothermal_kt_rel,\n                isothermal_kt,\n                {\n                    "status": isothermal_kt.get("status"),\n                    "closure_level": isothermal_kt.get("major_result", {}).get("closure_level"),\n                    "data_role": isothermal_kt.get("major_result", {}).get("data_role"),\n                    "K_T_GPa": isothermal_kt.get("source_row", {}).get("K_T_GPa"),\n                    "K_T_uncertainty_GPa": isothermal_kt.get("source_row", {}).get("K_T_uncertainty_GPa"),\n                    "Ding_material_regime_mapping_closed": isothermal_kt.get("thermodynamic_contract", {}).get("Ding_material_regime_mapping_closed"),\n                },\n            )\n        )\n    elastic_bulk_rel = rel(elastic_bulk_path)\n',
    "isothermal K_T evidence",
)
path.write_text(text, encoding="utf-8")
print("integrated graphite isothermal K_T source into Topic 13 full gate")
