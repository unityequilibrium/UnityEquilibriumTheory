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
    "'T13_MP48_SPECTRAL_C_SRC_REPRODUCTION': 'mp48_spectral_csrc_reproduction',",
    "'T13_MP48_SPECTRAL_C_SRC_REPRODUCTION': 'mp48_spectral_csrc_reproduction', 'T13_MP48_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION': 'mp48_force_constant_harmonic_reconstruction',",
    "registry mapping",
)
replace_once(
    '    spectral_csrc_path, spectral_csrc = load(\n        "docs/core/07_artifacts/topic13/t13_mp48_spectral_csrc_reproduction_audit.json"\n    )\n',
    '    spectral_csrc_path, spectral_csrc = load(\n        "docs/core/07_artifacts/topic13/t13_mp48_spectral_csrc_reproduction_audit.json"\n    )\n    force_constant_path, force_constant = load(\n        "docs/core/07_artifacts/topic13/t13_mp48_force_constant_harmonic_reconstruction_audit.json"\n    )\n',
    "force-constant artifact load",
)
replace_once(
    '    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    '    force_constant_lane = discovered_lane_integrations.get(\n        "mp48_force_constant_harmonic_reconstruction"\n    )\n    if force_constant_lane:\n        artifact["verification_status"]["source_package"][\n            "mp48_force_constant_harmonic_reconstruction"\n        ] = force_constant_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "mp48_force_constant_harmonic_reconstruction", None\n        )\n    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    "source lane projection",
)
replace_once(
    '    if discovered_lane_integrations.get("mp48_spectral_csrc_reproduction", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("MP48 harmonic DOS C_src-like cross-file reproduction is closed for lane without Ding-source or alpha promotion")\n',
    '    if discovered_lane_integrations.get("mp48_spectral_csrc_reproduction", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("MP48 harmonic DOS C_src-like cross-file reproduction is closed for lane without Ding-source or alpha promotion")\n    if discovered_lane_integrations.get("mp48_force_constant_harmonic_reconstruction", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("MP48 force-constant harmonic reconstruction is closed for lane without Ding-source, transport, or alpha promotion")\n',
    "closure summary",
)
replace_once(
    '    existing_evidence_paths = {item.get("path") for item in artifact.get("evidence_artifacts", [])}\n',
    '    force_constant_rel = rel(force_constant_path)\n    if force_constant_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                force_constant_rel,\n                force_constant,\n                {\n                    "status": force_constant.get("status"),\n                    "closure_level": force_constant.get("major_result", {}).get("closure_level"),\n                    "data_role": force_constant.get("major_result", {}).get("data_role"),\n                    "q_grid_max_frequency_THz": force_constant.get("reconstruction", {}).get("q_grid_frequency_max_THz"),\n                    "numeric_alpha_Phi_K_emitted": force_constant.get("numeric_alpha_Phi_K_emitted"),\n                },\n            )\n        )\n    existing_evidence_paths = {item.get("path") for item in artifact.get("evidence_artifacts", [])}\n',
    "force-constant evidence",
)
path.write_text(text, encoding="utf-8")
print("integrated MP48 force-constant harmonic lane into Topic 13 full gate")
