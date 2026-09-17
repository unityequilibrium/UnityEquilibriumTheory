from pathlib import Path


path = Path("docs/scripts/audit/audit_topic13_full_bridge_gate.py")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected one match, found {text.count(old)}")
    text = text.replace(old, new)


replace_once(
    "'T13_MP48_SPECTRAL_C_SRC_REPRODUCTION': 'mp48_spectral_csrc_reproduction',",
    "'T13_MP48_SPECTRAL_C_SRC_REPRODUCTION': 'mp48_spectral_csrc_reproduction', 'T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR': 'mp48_phi_e_dimensional_anchor_comparator',",
    "registry mapping",
)
replace_once(
    '    spectral_csrc_path, spectral_csrc = load(\n        "docs/core/07_artifacts/topic13/t13_mp48_spectral_csrc_reproduction_audit.json"\n    )\n',
    '    spectral_csrc_path, spectral_csrc = load(\n        "docs/core/07_artifacts/topic13/t13_mp48_spectral_csrc_reproduction_audit.json"\n    )\n    phi_e_comparator_path, phi_e_comparator = load(\n        "docs/core/07_artifacts/topic13/t13_mp48_phi_e_dimensional_comparator_audit.json"\n    )\n',
    "Phi_E artifact load",
)
replace_once(
    '    "dimensional_observable_map": {\n            "status": "PASS" if dimensional_map_ready else "BLOCKED",\n            "relation": "Delta_Tq = alpha_Phi_K * Delta_Phi",\n            "physical_mapping_ready": dimensional_map_ready,\n            "calibration_status": calibration.get("claim_status"),\n            "controlling_blocker": "dimensional_phi_to_thermal_observable_map_missing" if not dimensional_map_ready else None,\n        },\n',
    '    "dimensional_observable_map": {\n            "status": "PASS" if dimensional_map_ready else "BLOCKED",\n            "relation": "Delta_Tq = alpha_Phi_K * Delta_Phi",\n            "physical_mapping_ready": dimensional_map_ready,\n            "calibration_status": calibration.get("claim_status"),\n            "controlling_blocker": "dimensional_phi_to_thermal_observable_map_missing" if not dimensional_map_ready else None,\n        },\n',
    "dimensional gate anchor",
)
replace_once(
    '    spectral_csrc_lane = discovered_lane_integrations.get(\n        "mp48_spectral_csrc_reproduction"\n    )\n',
    '    phi_e_comparator_lane = discovered_lane_integrations.get(\n        "mp48_phi_e_dimensional_anchor_comparator"\n    )\n    if phi_e_comparator_lane:\n        artifact["verification_status"]["dimensional_observable_map"][\n            "mp48_phi_e_dimensional_anchor_comparator"\n        ] = phi_e_comparator_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "mp48_phi_e_dimensional_anchor_comparator", None\n        )\n    spectral_csrc_lane = discovered_lane_integrations.get(\n        "mp48_spectral_csrc_reproduction"\n    )\n',
    "dimensional lane projection",
)
replace_once(
    '    if discovered_lane_integrations.get("mp48_spectral_csrc_reproduction", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("MP48 harmonic DOS C_src-like cross-file reproduction is closed for lane without Ding-source or alpha promotion")\n',
    '    if discovered_lane_integrations.get("mp48_spectral_csrc_reproduction", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("MP48 harmonic DOS C_src-like cross-file reproduction is closed for lane without Ding-source or alpha promotion")\n    if discovered_lane_integrations.get("mp48_phi_e_dimensional_anchor_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("MP48 named Phi_E dimensional comparator is closed for lane without base-Phi or alpha_Phi_K promotion")\n',
    "Phi_E closure summary",
)
replace_once(
    '    spectral_rel = rel(spectral_csrc_path)\n',
    '    phi_e_rel = rel(phi_e_comparator_path)\n    if phi_e_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                phi_e_rel,\n                phi_e_comparator,\n                {\n                    "status": phi_e_comparator.get("status"),\n                    "closure_level": phi_e_comparator.get("major_result", {}).get("closure_level"),\n                    "data_role": phi_e_comparator.get("major_result", {}).get("data_role"),\n                    "reference_alpha_Phi_E_K": phi_e_comparator.get("reference_alpha_Phi_E_K"),\n                    "numeric_alpha_Phi_K_emitted": phi_e_comparator.get("numeric_alpha_Phi_K_emitted"),\n                },\n            )\n        )\n    spectral_rel = rel(spectral_csrc_path)\n',
    "Phi_E evidence",
)
path.write_text(text, encoding="utf-8")
print("integrated MP48 Phi_E dimensional comparator into the Topic 13 full gate")
