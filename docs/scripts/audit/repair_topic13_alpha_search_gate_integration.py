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
        "'T13_ALPHA_PHI_K_NORMALIZED_SCALE_NO_GO': 'alpha_phi_k_normalized_scale_no_go',",
        "'T13_ALPHA_PHI_K_NORMALIZED_SCALE_NO_GO': 'alpha_phi_k_normalized_scale_no_go', 'T13_ALPHA_PHI_K_PAIRED_RECORD_SEARCH': 'alpha_phi_k_paired_record_search',",
        "lane registry",
    )
    text = replace_once(
        text,
        '    ding_source_mapping_path, ding_source_mapping = load(\n        "docs/core/07_artifacts/provenance/ding_2022_source_mapping_audit.json"\n    )\n',
        '    ding_source_mapping_path, ding_source_mapping = load(\n        "docs/core/07_artifacts/provenance/ding_2022_source_mapping_audit.json"\n    )\n    alpha_search_path, alpha_search = load(\n        "docs/core/07_artifacts/topic13/t13_alpha_phi_k_calibration_candidate_audit.json"\n    )\n',
        "alpha search load",
    )
    text = replace_once(
        text,
        '            "uncertainty_status": measurement.get("uncertainty_status"),\n            "controlling_blocker": "alpha_Phi_K_independent_calibration_missing" if not alpha_ready else None,\n',
        '            "uncertainty_status": measurement.get("uncertainty_status"),\n            "candidate_search_status": alpha_search.get("status"),\n            "candidate_count": alpha_search.get("candidate_count"),\n            "eligible_candidate_count": alpha_search.get("eligible_candidate_count"),\n            "candidate_search_holdout_accessed": alpha_search.get("holdout_accessed"),\n            "candidate_search_fit_performed": alpha_search.get("target_fit_performed"),\n            "candidate_search_artifact": {"path": rel(alpha_search_path), "sha256": sha256(alpha_search_path)},\n            "controlling_blocker": "alpha_Phi_K_independent_calibration_missing" if not alpha_ready else None,\n',
        "alpha gate fields",
    )
    text = replace_once(
        text,
        '            evidence(rel(ding_source_mapping_path), ding_source_mapping, {\n                "status": ding_source_mapping.get("status"),\n                "raw_author_numeric_source_present": ding_source_mapping.get("checks", {}).get("raw_author_numeric_source_present"),\n                "permitted_figure_numeric_route_ready": ding_source_mapping.get("checks", {}).get("permitted_figure_numeric_route_ready"),\n            }),\n',
        '            evidence(rel(ding_source_mapping_path), ding_source_mapping, {\n                "status": ding_source_mapping.get("status"),\n                "raw_author_numeric_source_present": ding_source_mapping.get("checks", {}).get("raw_author_numeric_source_present"),\n                "permitted_figure_numeric_route_ready": ding_source_mapping.get("checks", {}).get("permitted_figure_numeric_route_ready"),\n            }),\n            evidence(rel(alpha_search_path), alpha_search, {\n                "status": alpha_search.get("status"),\n                "candidate_count": alpha_search.get("candidate_count"),\n                "eligible_candidate_count": alpha_search.get("eligible_candidate_count"),\n                "holdout_accessed": alpha_search.get("holdout_accessed"),\n                "numeric_alpha_Phi_K_emitted": alpha_search.get("numeric_alpha_Phi_K_emitted"),\n            }),\n',
        "alpha search evidence",
    )
    text = replace_once(
        text,
        '    if discovered_lane_integrations.get("oxford_tgs_comparator_provenance", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Oxford TGS Figure 1 provenance archive is closed for lane without numeric-row or calibration promotion")\n',
        '    if discovered_lane_integrations.get("oxford_tgs_comparator_provenance", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Oxford TGS Figure 1 provenance archive is closed for lane without numeric-row or calibration promotion")\n    if discovered_lane_integrations.get("alpha_phi_k_paired_record_search", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("current alpha_Phi_K paired-record search is closed for lane with no eligible calibration record")\n',
        "alpha search closure note",
    )
    TARGET.write_text(text, encoding="utf-8")
    print("patched", TARGET)


if __name__ == "__main__":
    main()
