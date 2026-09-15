"""Integrate the Oxford numeric-row audit into the canonical Topic 13 gate."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, got {count}")
    return text.replace(old, new, 1)


def main() -> int:
    text = TARGET.read_text(encoding="utf-8-sig")
    text = replace_once(
        text,
        "'T13_PHONIX_MP47_GRAPHITE_HARMONIC_COMPARATOR': 'phonix_mp47_graphite_harmonic_comparator'}",
        "'T13_PHONIX_MP47_GRAPHITE_HARMONIC_COMPARATOR': 'phonix_mp47_graphite_harmonic_comparator', 'T13_OXFORD_TGS_NUMERIC_ROWS_COMPARATOR': 'oxford_tgs_numeric_rows_comparator'}",
        "lane key mapping",
    )
    text = replace_once(
        text,
        '    phonix_path, phonix = load(\n        "docs/core/07_artifacts/topic13/t13_phonix_mp47_graphite_comparator_audit.json"\n    )\n',
        '    phonix_path, phonix = load(\n        "docs/core/07_artifacts/topic13/t13_phonix_mp47_graphite_comparator_audit.json"\n    )\n    oxford_numeric_path, oxford_numeric = load(\n        "docs/core/07_artifacts/topic13/t13_oxford_tgs_numeric_rows_audit.json"\n    )\n',
        "numeric audit load",
    )
    oxford_anchor = '''    oxford_source_lane = discovered_lane_integrations.get(
        "oxford_tgs_comparator_provenance"
    )
    if oxford_source_lane:
        artifact["verification_status"]["source_package"][
            "oxford_tgs_comparator_provenance"
        ] = oxford_source_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "oxford_tgs_comparator_provenance", None
        )
'''
    oxford_addition = oxford_anchor + '''    oxford_numeric_lane = discovered_lane_integrations.get(
        "oxford_tgs_numeric_rows_comparator"
    )
    if oxford_numeric_lane:
        artifact["verification_status"]["source_package"][
            "oxford_tgs_numeric_rows_comparator"
        ] = oxford_numeric_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "oxford_tgs_numeric_rows_comparator", None
        )
'''
    text = replace_once(text, oxford_anchor, oxford_addition, "numeric lane placement")
    text = replace_once(
        text,
        '    if discovered_lane_integrations.get("oxford_tgs_comparator_provenance", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Oxford TGS Figure 1 provenance archive is closed for lane without numeric-row or calibration promotion")\n',
        '    if discovered_lane_integrations.get("oxford_tgs_comparator_provenance", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Oxford TGS Figure 1 provenance archive is closed for lane without numeric-row or calibration promotion")\n    if discovered_lane_integrations.get("oxford_tgs_numeric_rows_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Oxford TGS Figure 1 numeric rows are closed for lane without physical thermal or Phi calibration promotion")\n',
        "numeric lane closure projection",
    )
    evidence_anchor = '    mp48_package_path = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/mp48_independent_graphite_cv_source_package.json"\n'
    evidence_addition = '''    oxford_numeric_rel = rel(oxford_numeric_path)
    if oxford_numeric_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                oxford_numeric_rel,
                oxford_numeric,
                {
                    "status": oxford_numeric.get("status"),
                    "closure_level": oxford_numeric.get("major_result", {}).get("closure_level"),
                    "data_role": oxford_numeric.get("major_result", {}).get("data_role"),
                    "numeric_rows_emitted": oxford_numeric.get("numeric_rows_emitted"),
                    "numeric_alpha_Phi_K_emitted": oxford_numeric.get("numeric_alpha_Phi_K_emitted"),
                    "controlling_blocker": oxford_numeric.get("controlling_blocker"),
                },
            )
        )
'''
    text = replace_once(text, evidence_anchor, evidence_addition + evidence_anchor, "numeric evidence linkage")
    TARGET.write_text(text, encoding="utf-8")
    print("integrated Oxford numeric-row lane into Topic 13 full gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
