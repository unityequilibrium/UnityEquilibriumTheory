from pathlib import Path


path = Path("docs/scripts/audit/audit_topic13_full_bridge_gate.py")
text = path.read_text(encoding="utf-8")

replacements = [
    (
        "'T13_OXFORD_TGS_COMPARATOR_PROVENANCE': 'oxford_tgs_comparator_provenance'}",
        "'T13_OXFORD_TGS_COMPARATOR_PROVENANCE': 'oxford_tgs_comparator_provenance', 'T13_PHONIX_MP47_GRAPHITE_HARMONIC_COMPARATOR': 'phonix_mp47_graphite_harmonic_comparator'}",
    ),
    (
        '    cv_uncertainty_package_path, cv_uncertainty_package = load(\n'
        '        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/iaea_graphite_cv_uncertainty_boundary_source_package.json"\n'
        '    )\n',
        '    cv_uncertainty_package_path, cv_uncertainty_package = load(\n'
        '        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/iaea_graphite_cv_uncertainty_boundary_source_package.json"\n'
        '    )\n'
        '    phonix_path, phonix = load(\n'
        '        "docs/core/07_artifacts/topic13/t13_phonix_mp47_graphite_comparator_audit.json"\n'
        '    )\n',
    ),
    (
        '    material_boundary_lane = discovered_lane_integrations.get(\n'
        '        "ding_material_regime_boundary"\n'
        '    )\n',
        '    phonix_lane = discovered_lane_integrations.get(\n'
        '        "phonix_mp47_graphite_harmonic_comparator"\n'
        '    )\n'
        '    if phonix_lane:\n'
        '        artifact["verification_status"]["source_package"][\n'
        '            "phonix_mp47_graphite_harmonic_comparator"\n'
        '        ] = phonix_lane\n'
        '        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n'
        '            "phonix_mp47_graphite_harmonic_comparator", None\n'
        '        )\n'
        '    material_boundary_lane = discovered_lane_integrations.get(\n'
        '        "ding_material_regime_boundary"\n'
        '    )\n',
    ),
    (
        '    if discovered_lane_integrations.get("ding_material_regime_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n'
        '        lane_closures.append("Ding/comparator material-regime equivalence is closed as a scoped no-go; comparator c_v and c_p lanes cannot substitute for Ding C_src")\n',
        '    if discovered_lane_integrations.get("ding_material_regime_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n'
        '        lane_closures.append("Ding/comparator material-regime equivalence is closed as a scoped no-go; comparator c_v and c_p lanes cannot substitute for Ding C_src")\n'
        '    if discovered_lane_integrations.get("phonix_mp47_graphite_harmonic_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n'
        '        lane_closures.append("Phonix mp-47 graphite harmonic comparator is closed for lane; arbitrary-unit DOS and uncertainty prevent volumetric c_v or Ding C_src promotion")\n',
    ),
    (
        '    artifact["source_acquisition_controller"] = "ding_pbte_author_data_or_independent_reproduction_package_missing"\n',
        '    phonix_rel = rel(phonix_path)\n'
        '    if phonix_rel not in {\n'
        '        item.get("path") for item in artifact.get("evidence_artifacts", [])\n'
        '        if isinstance(item, dict)\n'
        '    }:\n'
        '        artifact["evidence_artifacts"].append(\n'
        '            evidence(\n'
        '                phonix_rel,\n'
        '                phonix,\n'
        '                {\n'
        '                    "status": phonix.get("status"),\n'
        '                    "closure_level": phonix.get("major_result", {}).get("closure_level"),\n'
        '                    "data_role": phonix.get("major_result", {}).get("data_role"),\n'
        '                    "source_revision": phonix.get("source", {}).get("dataset_revision"),\n'
        '                    "dos_units": phonix.get("major_result", {}).get("units", {}).get("DOS"),\n'
        '                    "numeric_c_v_emitted": phonix.get("numeric_c_v_emitted"),\n'
        '                    "controlling_blocker": phonix.get("controlling_blocker"),\n'
        '                },\n'
        '            )\n'
        '        )\n'
        '    artifact["source_acquisition_controller"] = "ding_pbte_author_data_or_independent_reproduction_package_missing"\n',
    ),
]

for old, new in replacements:
    if old not in text:
        raise SystemExit(f"expected integration anchor not found: {old[:100]}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("integrated Phonix comparator into Topic 13 full gate")
