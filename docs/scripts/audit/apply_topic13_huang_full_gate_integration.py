from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"
text = PATH.read_text(encoding="utf-8")

old = "'T13_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE': 'mp48_force_constant_csrc_mesh_convergence', 'T13_NIST_GRAPHITE_ALPHA_V_SOURCE_BOUNDARY'"
new = "'T13_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE': 'mp48_force_constant_csrc_mesh_convergence', 'T13_HUANG_2023_SUPPLEMENTARY_PAYLOAD_BOUNDARY': 'huang_2023_supplementary_payload_boundary', 'T13_NIST_GRAPHITE_ALPHA_V_SOURCE_BOUNDARY'"
assert text.count(old) == 1
text = text.replace(old, new)

old = (
    '    mesh_convergence_path, mesh_convergence = load(\n'
    '        "docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json"\n'
    '    )\n'
)
new = old + (
    '    huang_supplementary_path, huang_supplementary = load(\n'
    '        "docs/core/07_artifacts/topic13/t13_huang_2023_supplementary_payload_boundary_audit.json"\n'
    '    )\n'
)
assert text.count(old) == 1
text = text.replace(old, new)

old = "    tpg_alpha_v_rel = rel(tpg_alpha_v_path)\n"
new = (
    '    huang_supplementary_rel = rel(huang_supplementary_path)\n'
    '    if huang_supplementary_rel not in {\n'
    '        item.get("path") for item in artifact.get("evidence_artifacts", [])\n'
    '        if isinstance(item, dict)\n'
    '    }:\n'
    '        artifact["evidence_artifacts"].append(\n'
    '            evidence(\n'
    '                huang_supplementary_rel,\n'
    '                huang_supplementary,\n'
    '                {\n'
    '                    "status": huang_supplementary.get("status"),\n'
    '                    "closure_level": huang_supplementary.get("major_result", {}).get("closure_level"),\n'
    '                    "data_role": huang_supplementary.get("major_result", {}).get("data_role"),\n'
    '                    "reviewed_page_count": huang_supplementary.get("source", {}).get("reviewed_page_count"),\n'
    '                    "machine_readable_payload_files": len(huang_supplementary.get("source", {}).get("machine_readable_payload_files", [])),\n'
    '                    "controlling_blocker": huang_supplementary.get("controlling_blocker"),\n'
    '                },\n'
    '            )\n'
    '        )\n'
    '    tpg_alpha_v_rel = rel(tpg_alpha_v_path)\n'
)
assert text.count(old) == 1
text = text.replace(old, new)

old = (
    '    nist_alpha_v_lane = discovered_lane_integrations.get(\n'
    '        "nist_graphite_alpha_v_source_boundary"\n'
    '    )\n'
)
new = (
    '    huang_supplementary_lane = discovered_lane_integrations.get(\n'
    '        "huang_2023_supplementary_payload_boundary"\n'
    '    )\n'
    '    if huang_supplementary_lane:\n'
    '        artifact["verification_status"]["source_package"][\n'
    '            "huang_2023_supplementary_payload_boundary"\n'
    '        ] = huang_supplementary_lane\n'
    '        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n'
    '            "huang_2023_supplementary_payload_boundary", None\n'
    '        )\n'
    + old
)
assert text.count(old) == 1
text = text.replace(old, new)

old = (
    '    if discovered_lane_integrations.get("nist_graphite_alpha_v_source_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n'
)
new = (
    '    if discovered_lane_integrations.get("huang_2023_supplementary_payload_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n'
    '        lane_closures.append("Huang 2023 graphite supplementary boundary is closed for lane without numeric PBTE, Ding C_src, or alpha promotion")\n'
    + old
)
assert text.count(old) == 1
text = text.replace(old, new)

PATH.write_text(text, encoding="utf-8")
print(PATH)
