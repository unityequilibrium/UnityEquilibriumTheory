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
    "'T13_NIST_GRAPHITE_ALPHA_V_SOURCE_BOUNDARY': 'nist_graphite_alpha_v_source_boundary',",
    "'T13_NIST_GRAPHITE_ALPHA_V_SOURCE_BOUNDARY': 'nist_graphite_alpha_v_source_boundary', 'T13_GRAPHITE_ELASTIC_BULK_MODULUS_SOURCE': 'graphite_elastic_bulk_modulus_source',",
    "registry mapping",
)
replace_once(
    '    nist_alpha_v_path, nist_alpha_v = load(\n        "docs/core/07_artifacts/topic13/t13_nist_graphite_alpha_v_source_boundary_audit.json"\n    )\n',
    '    nist_alpha_v_path, nist_alpha_v = load(\n        "docs/core/07_artifacts/topic13/t13_nist_graphite_alpha_v_source_boundary_audit.json"\n    )\n    elastic_bulk_path, elastic_bulk = load(\n        "docs/core/07_artifacts/topic13/t13_graphite_elastic_bulk_modulus_source_audit.json"\n    )\n',
    "elastic bulk artifact load",
)
replace_once(
    '    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    '    elastic_bulk_lane = discovered_lane_integrations.get(\n        "graphite_elastic_bulk_modulus_source"\n    )\n    if elastic_bulk_lane:\n        artifact["verification_status"]["source_package"][\n            "graphite_elastic_bulk_modulus_source"\n        ] = elastic_bulk_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "graphite_elastic_bulk_modulus_source", None\n        )\n    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    "source lane projection",
)
replace_once(
    '    if discovered_lane_integrations.get("nist_graphite_alpha_v_source_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("NIST AXM-5Q1 graphite alpha_V source boundary is closed for lane without K_T or Ding material-match promotion")\n',
    '    if discovered_lane_integrations.get("nist_graphite_alpha_v_source_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("NIST AXM-5Q1 graphite alpha_V source boundary is closed for lane without K_T or Ding material-match promotion")\n    if discovered_lane_integrations.get("graphite_elastic_bulk_modulus_source", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Bosak single-crystal graphite elastic bulk comparator is closed for lane without isothermal K_T or Ding material-match promotion")\n',
    "closure summary",
)
replace_once(
    '    nist_alpha_v_rel = rel(nist_alpha_v_path)\n',
    '    elastic_bulk_rel = rel(elastic_bulk_path)\n    if elastic_bulk_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                elastic_bulk_rel,\n                elastic_bulk,\n                {\n                    "status": elastic_bulk.get("status"),\n                    "closure_level": elastic_bulk.get("major_result", {}).get("closure_level"),\n                    "data_role": elastic_bulk.get("major_result", {}).get("data_role"),\n                    "reconstructed_B_elastic_GPa": elastic_bulk.get("reconstruction", {}).get("reconstructed_B_elastic_GPa"),\n                    "K_T_emitted": elastic_bulk.get("isothermal_boundary", {}).get("K_T_emitted"),\n                },\n            )\n        )\n    nist_alpha_v_rel = rel(nist_alpha_v_path)\n',
    "elastic bulk evidence",
)
path.write_text(text, encoding="utf-8")
print("integrated graphite elastic bulk source comparator into Topic 13 full gate")
