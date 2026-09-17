from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "'T13_DING_FIG1D_NORMALIZED_SOURCE_LANE': 'ding_fig1d_normalized_source_lane',",
        "'T13_DING_FIG1D_NORMALIZED_SOURCE_LANE': 'ding_fig1d_normalized_source_lane', 'T13_DING_C_SRC_INDEPENDENT_REPRODUCTION_BOUNDARY': 'ding_c_src_independent_reproduction_boundary',",
        "Ding boundary lane registry",
    )
    text = replace_once(
        text,
        '    alpha_search_path, alpha_search = load(\n        "docs/core/07_artifacts/topic13/t13_alpha_phi_k_calibration_candidate_audit.json"\n    )\n',
        '    alpha_search_path, alpha_search = load(\n        "docs/core/07_artifacts/topic13/t13_alpha_phi_k_calibration_candidate_audit.json"\n    )\n    ding_c_src_boundary_path, ding_c_src_boundary = load(\n        "docs/core/07_artifacts/topic13/t13_ding_c_src_independent_reproduction_boundary_audit.json"\n    )\n',
        "Ding boundary load",
    )
    text = replace_once(
        text,
        '            evidence(rel(alpha_search_path), alpha_search, {\n                "status": alpha_search.get("status"),\n                "candidate_count": alpha_search.get("candidate_count"),\n                "eligible_candidate_count": alpha_search.get("eligible_candidate_count"),\n                "holdout_accessed": alpha_search.get("holdout_accessed"),\n                "numeric_alpha_Phi_K_emitted": alpha_search.get("numeric_alpha_Phi_K_emitted"),\n            }),\n',
        '            evidence(rel(alpha_search_path), alpha_search, {\n                "status": alpha_search.get("status"),\n                "candidate_count": alpha_search.get("candidate_count"),\n                "eligible_candidate_count": alpha_search.get("eligible_candidate_count"),\n                "holdout_accessed": alpha_search.get("holdout_accessed"),\n                "numeric_alpha_Phi_K_emitted": alpha_search.get("numeric_alpha_Phi_K_emitted"),\n            }),\n            evidence(rel(ding_c_src_boundary_path), ding_c_src_boundary, {\n                "status": ding_c_src_boundary.get("status"),\n                "closure_level": ding_c_src_boundary.get("major_result", {}).get("closure_level"),\n                "mp48_is_ding_c_src": False,\n                "numeric_alpha_Phi_K_emitted": ding_c_src_boundary.get("numeric_alpha_Phi_K_emitted"),\n            }),\n',
        "Ding boundary evidence",
    )
    text = replace_once(
        text,
        '    if discovered_lane_integrations.get("alpha_phi_k_paired_record_search", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("current alpha_Phi_K paired-record search is closed for lane with no eligible calibration record")\n',
        '    if discovered_lane_integrations.get("alpha_phi_k_paired_record_search", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("current alpha_Phi_K paired-record search is closed for lane with no eligible calibration record")\n    if discovered_lane_integrations.get("ding_c_src_independent_reproduction_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("independent c_v comparator boundary is closed for lane without promoting it to Ding C_src")\n',
        "Ding boundary closure note",
    )
    text = replace_once(
        text,
        '    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
        '    ding_c_src_boundary_lane = discovered_lane_integrations.get(\n        "ding_c_src_independent_reproduction_boundary"\n    )\n    if ding_c_src_boundary_lane:\n        artifact["verification_status"]["source_package"][\n            "ding_c_src_independent_reproduction_boundary"\n        ] = ding_c_src_boundary_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "ding_c_src_independent_reproduction_boundary", None\n        )\n    oxford_source_lane = discovered_lane_integrations.get(\n        "oxford_tgs_comparator_provenance"\n    )\n',
        "Ding boundary source placement",
    )
    TARGET.write_text(text, encoding="utf-8")
    print("patched", TARGET)


if __name__ == "__main__":
    main()
