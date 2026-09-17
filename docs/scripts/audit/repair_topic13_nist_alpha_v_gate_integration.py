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
    "'T13_MP48_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION': 'mp48_force_constant_harmonic_reconstruction',",
    "'T13_MP48_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION': 'mp48_force_constant_harmonic_reconstruction', 'T13_NIST_GRAPHITE_ALPHA_V_SOURCE_BOUNDARY': 'nist_graphite_alpha_v_source_boundary',",
    "registry mapping",
)
replace_once(
    '    force_constant_path, force_constant = load(\n        "docs/core/07_artifacts/topic13/t13_mp48_force_constant_harmonic_reconstruction_audit.json"\n    )\n',
    '    force_constant_path, force_constant = load(\n        "docs/core/07_artifacts/topic13/t13_mp48_force_constant_harmonic_reconstruction_audit.json"\n    )\n    nist_alpha_v_path, nist_alpha_v = load(\n        "docs/core/07_artifacts/topic13/t13_nist_graphite_alpha_v_source_boundary_audit.json"\n    )\n',
    "NIST artifact load",
)
replace_once(
    '    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    '    nist_alpha_v_lane = discovered_lane_integrations.get(\n        "nist_graphite_alpha_v_source_boundary"\n    )\n    if nist_alpha_v_lane:\n        artifact["verification_status"]["source_package"][\n            "nist_graphite_alpha_v_source_boundary"\n        ] = nist_alpha_v_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "nist_graphite_alpha_v_source_boundary", None\n        )\n    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    "source lane projection",
)
replace_once(
    '    if discovered_lane_integrations.get("mp48_force_constant_harmonic_reconstruction", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("MP48 force-constant harmonic reconstruction is closed for lane without Ding-source, transport, or alpha promotion")\n',
    '    if discovered_lane_integrations.get("mp48_force_constant_harmonic_reconstruction", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("MP48 force-constant harmonic reconstruction is closed for lane without Ding-source, transport, or alpha promotion")\n    if discovered_lane_integrations.get("nist_graphite_alpha_v_source_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("NIST AXM-5Q1 graphite alpha_V source boundary is closed for lane without K_T or Ding material-match promotion")\n',
    "closure summary",
)
replace_once(
    '    existing_evidence_paths = {item.get("path") for item in artifact.get("evidence_artifacts", [])}\n',
    '    nist_alpha_v_rel = rel(nist_alpha_v_path)\n    if nist_alpha_v_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                nist_alpha_v_rel,\n                nist_alpha_v,\n                {\n                    "status": nist_alpha_v.get("status"),\n                    "closure_level": nist_alpha_v.get("major_result", {}).get("closure_level"),\n                    "data_role": nist_alpha_v.get("major_result", {}).get("data_role"),\n                    "row_count": len(nist_alpha_v.get("rows", [])),\n                    "numeric_alpha_Phi_K_emitted": nist_alpha_v.get("numeric_alpha_Phi_K_emitted"),\n                },\n            )\n        )\n    existing_evidence_paths = {item.get("path") for item in artifact.get("evidence_artifacts", [])}\n',
    "NIST evidence",
)
path.write_text(text, encoding="utf-8")
print("integrated NIST graphite alpha_V source boundary into Topic 13 full gate")
