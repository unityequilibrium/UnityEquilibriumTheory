from pathlib import Path


path = Path("docs/scripts/audit/audit_topic13_full_bridge_gate.py")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected one match, found {text.count(old)}")
    text = text.replace(old, new)


replace_once(
    "'T13_MP48_INDEPENDENT_GRAPHITE_CV_REPRODUCTION': 'mp48_independent_graphite_cv_reproduction',",
    "'T13_MP48_INDEPENDENT_GRAPHITE_CV_REPRODUCTION': 'mp48_independent_graphite_cv_reproduction', 'T13_MP48_SPECTRAL_C_SRC_REPRODUCTION': 'mp48_spectral_csrc_reproduction',",
    "registry mapping",
)
replace_once(
    '    ding_public_supplementary_path, ding_public_supplementary = load(\n        "docs/core/07_artifacts/topic13/t13_ding_public_supplementary_payload_boundary_audit.json"\n    )\n',
    '    ding_public_supplementary_path, ding_public_supplementary = load(\n        "docs/core/07_artifacts/topic13/t13_ding_public_supplementary_payload_boundary_audit.json"\n    )\n    spectral_csrc_path, spectral_csrc = load(\n        "docs/core/07_artifacts/topic13/t13_mp48_spectral_csrc_reproduction_audit.json"\n    )\n',
    "spectral artifact load",
)
replace_once(
    '    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    '    spectral_csrc_lane = discovered_lane_integrations.get(\n        "mp48_spectral_csrc_reproduction"\n    )\n    if spectral_csrc_lane:\n        artifact["verification_status"]["source_package"][\n            "mp48_spectral_csrc_reproduction"\n        ] = spectral_csrc_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "mp48_spectral_csrc_reproduction", None\n        )\n    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
    "source lane projection",
)
replace_once(
    '    if discovered_lane_integrations.get("mp48_independent_graphite_cv_reproduction", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("independent harmonic graphite c_v comparator (mp-48) is closed for lane without calibration promotion")\n',
    '    if discovered_lane_integrations.get("mp48_independent_graphite_cv_reproduction", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("independent harmonic graphite c_v comparator (mp-48) is closed for lane without calibration promotion")\n    if discovered_lane_integrations.get("mp48_spectral_csrc_reproduction", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("MP48 harmonic DOS C_src-like cross-file reproduction is closed for lane without Ding-source or alpha promotion")\n',
    "closure summary",
)
replace_once(
    '    existing_evidence_paths = {item.get("path") for item in artifact.get("evidence_artifacts", [])}\n',
    '    spectral_rel = rel(spectral_csrc_path)\n    if spectral_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                spectral_rel,\n                spectral_csrc,\n                {\n                    "status": spectral_csrc.get("status"),\n                    "closure_level": spectral_csrc.get("major_result", {}).get("closure_level"),\n                    "data_role": spectral_csrc.get("major_result", {}).get("data_role"),\n                    "max_abs_relative_reproduction_residual": spectral_csrc.get("convergence", {}).get("max_abs_relative_reproduction_residual"),\n                    "numeric_alpha_Phi_K_emitted": spectral_csrc.get("numeric_alpha_Phi_K_emitted"),\n                },\n            )\n        )\n    existing_evidence_paths = {item.get("path") for item in artifact.get("evidence_artifacts", [])}\n',
    "spectral evidence",
)
path.write_text(text, encoding="utf-8")
print("integrated MP48 spectral C_src-like lane into Topic 13 full gate")
