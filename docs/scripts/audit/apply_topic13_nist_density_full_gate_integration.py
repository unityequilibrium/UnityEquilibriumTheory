from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"
text = PATH.read_text(encoding="utf-8")

old = "'T13_HUANG_2023_SUPPLEMENTARY_PAYLOAD_BOUNDARY': 'huang_2023_supplementary_payload_boundary', 'T13_NIST_GRAPHITE_ALPHA_V_SOURCE_BOUNDARY'"
new = "'T13_HUANG_2023_SUPPLEMENTARY_PAYLOAD_BOUNDARY': 'huang_2023_supplementary_payload_boundary', 'T13_NIST_AXM5Q1_DENSITY_SOURCE_BOUNDARY': 'nist_axm5q1_density_source_boundary', 'T13_NIST_GRAPHITE_ALPHA_V_SOURCE_BOUNDARY'"
assert text.count(old) == 1
text = text.replace(old, new)

old = (
    '    huang_supplementary_path, huang_supplementary = load(\n'
    '        "docs/core/07_artifacts/topic13/t13_huang_2023_supplementary_payload_boundary_audit.json"\n'
    '    )\n'
)
new = old + (
    '    nist_density_path, nist_density = load(\n'
    '        "docs/core/07_artifacts/topic13/t13_nist_axm5q1_density_source_boundary_audit.json"\n'
    '    )\n'
)
assert text.count(old) == 1
text = text.replace(old, new)

old = (
    '    huang_supplementary_lane = discovered_lane_integrations.get(\n'
    '        "huang_2023_supplementary_payload_boundary"\n'
    '    )\n'
)
new = old + (
    '    nist_density_lane = discovered_lane_integrations.get(\n'
    '        "nist_axm5q1_density_source_boundary"\n'
    '    )\n'
    '    if nist_density_lane:\n'
    '        artifact["verification_status"]["source_package"][\n'
    '            "nist_axm5q1_density_source_boundary"\n'
    '        ] = nist_density_lane\n'
    '        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n'
    '            "nist_axm5q1_density_source_boundary", None\n'
    '        )\n'
)
assert text.count(old) == 1
text = text.replace(old, new)

old = (
    '    if discovered_lane_integrations.get("nist_graphite_alpha_v_source_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n'
)
new = (
    '    if discovered_lane_integrations.get("nist_axm5q1_density_source_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n'
    '        lane_closures.append("NIST AXM-5Q1 same-grade density availability is closed for lane; density uncertainty, c_v, and Ding mapping remain open")\n'
    + old
)
assert text.count(old) == 1
text = text.replace(old, new)

old = (
    '    source_level_blockers = {\n'
    '        "independent_same_grade_density_or_direct_volumetric_heat_capacity_missing",\n'
    '        "same_grade_alpha_V_and_K_T_missing",\n'
    '        "material_regime_mapping_to_TTG_not_closed",\n'
    '        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",\n'
    '    }\n'
)
new = (
    '    source_level_blockers = {\n'
    '        "independent_same_grade_density_or_direct_volumetric_heat_capacity_missing",\n'
    '        "density_uncertainty_not_source_locked",\n'
    '        "c_v_source_uncertainty_not_closed",\n'
    '        "direct_volumetric_c_v_or_same_state_Cp_source_missing",\n'
    '        "same_grade_alpha_V_and_K_T_missing",\n'
    '        "material_regime_mapping_to_TTG_not_closed",\n'
    '        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",\n'
    '    }\n'
)
assert text.count(old) == 1
text = text.replace(old, new)

old = (
    '    # Preserve unresolved source-dependency blockers in the major-result\n'
    '    # projection. A scoped no-go closes the circular route, but does not close\n'
    '    # the independent source requirement that the no-go exposes.\n'
    '    for blocker in source_independence_lane.get("open_blockers", []):\n'
    '        if blocker in source_level_blockers:\n'
    '            blockers.append(blocker)\n'
)
new = (
    '    # Preserve unresolved source-dependency blockers in the major-result\n'
    '    # projection. A scoped no-go closes the circular route. The independently\n'
    '    # measured AXM-5Q1 density lane removes only the density-availability\n'
    '    # blocker; its precision and c_v uncertainty remain explicit.\n'
    '    density_availability_closed = (\n'
    '        nist_density_lane.get("closure_level") == "CLOSED_FOR_LANE"\n'
    '        and str(nist_density_lane.get("status", "")).startswith("PASS_")\n'
    '    )\n'
    '    for blocker in source_independence_lane.get("open_blockers", []):\n'
    '        if blocker not in source_level_blockers:\n'
    '            continue\n'
    '        if blocker == "independent_same_grade_density_or_direct_volumetric_heat_capacity_missing" and density_availability_closed:\n'
    '            continue\n'
    '        blockers.append(blocker)\n'
    '    if density_availability_closed:\n'
    '        for blocker in nist_density_lane.get("open_blockers", []):\n'
    '            if blocker in source_level_blockers:\n'
    '                blockers.append(blocker)\n'
)
assert text.count(old) == 1
text = text.replace(old, new)

old = "    tpg_alpha_v_rel = rel(tpg_alpha_v_path)\n"
new = (
    '    nist_density_rel = rel(nist_density_path)\n'
    '    if nist_density_rel not in {\n'
    '        item.get("path") for item in artifact.get("evidence_artifacts", [])\n'
    '        if isinstance(item, dict)\n'
    '    }:\n'
    '        artifact["evidence_artifacts"].append(\n'
    '            evidence(\n'
    '                nist_density_rel,\n'
    '                nist_density,\n'
    '                {\n'
    '                    "status": nist_density.get("status"),\n'
    '                    "closure_level": nist_density.get("major_result", {}).get("closure_level"),\n'
    '                    "data_role": nist_density.get("major_result", {}).get("data_role"),\n'
    '                    "density_kg_per_m3": nist_density.get("rows", [{}])[0].get("density_kg_per_m3"),\n'
    '                    "precision_bound": nist_density.get("rows", [{}])[0].get("uncertainty_boundary", {}).get("reported_relative_precision_bound"),\n'
    '                    "controlling_blocker": nist_density.get("controlling_blocker"),\n'
    '                },\n'
    '            )\n'
    '        )\n'
    + old
)
assert text.count(old) == 1
text = text.replace(old, new)

PATH.write_text(text, encoding="utf-8")
print(PATH)
