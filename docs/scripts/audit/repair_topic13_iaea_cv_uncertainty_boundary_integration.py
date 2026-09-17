from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FULL_GATE_SCRIPT = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"
REGISTER_SCRIPT = ROOT / "docs/scripts/audit/sync_topic13_major_result_lanes.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    text = FULL_GATE_SCRIPT.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "'T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR': 'iaea_graphite_table_cv_comparator', 'T13_DING_MATERIAL_REGIME_BOUNDARY'",
        "'T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR': 'iaea_graphite_table_cv_comparator', 'T13_IAEA_CV_UNCERTAINTY_BOUNDARY': 'iaea_cv_uncertainty_boundary', 'T13_DING_MATERIAL_REGIME_BOUNDARY'",
        "lane registry",
    )
    text = replace_once(
        text,
        '    material_boundary_path, material_boundary = load(\n        "docs/core/07_artifacts/topic13/t13_ding_material_regime_boundary_audit.json"\n    )',
        '    cv_uncertainty_path, cv_uncertainty = load(\n        "docs/core/07_artifacts/topic13/t13_iaea_cv_uncertainty_boundary_audit.json"\n    )\n    cv_uncertainty_package_path, cv_uncertainty_package = load(\n        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/iaea_graphite_cv_uncertainty_boundary_source_package.json"\n    )\n    material_boundary_path, material_boundary = load(\n        "docs/core/07_artifacts/topic13/t13_ding_material_regime_boundary_audit.json"\n    )',
        "uncertainty boundary loading",
    )
    text = replace_once(
        text,
        '    material_boundary_lane = discovered_lane_integrations.get(\n        "ding_material_regime_boundary"\n    )',
        '    cv_uncertainty_lane = discovered_lane_integrations.get(\n        "iaea_cv_uncertainty_boundary"\n    )\n    if cv_uncertainty_lane:\n        artifact["verification_status"]["source_package"][\n            "iaea_cv_uncertainty_boundary"\n        ] = cv_uncertainty_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "iaea_cv_uncertainty_boundary", None\n        )\n    material_boundary_lane = discovered_lane_integrations.get(\n        "ding_material_regime_boundary"\n    )',
        "uncertainty boundary source projection",
    )
    text = replace_once(
        text,
        '    material_boundary_rel = rel(material_boundary_path)',
        '    cv_uncertainty_rel = rel(cv_uncertainty_path)\n    if cv_uncertainty_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                cv_uncertainty_rel,\n                cv_uncertainty,\n                {\n                    "status": cv_uncertainty.get("status"),\n                    "closure_level": cv_uncertainty.get("major_result", {}).get("closure_level"),\n                    "data_role": cv_uncertainty.get("major_result", {}).get("data_role"),\n                    "controlling_blocker": cv_uncertainty.get("controlling_blocker"),\n                    "direct_volumetric_cv_with_uncertainty": cv_uncertainty.get("boundary_observations", {}).get("direct_volumetric_cv_with_uncertainty"),\n                },\n            )\n        )\n    cv_uncertainty_package_rel = rel(cv_uncertainty_package_path)\n    if cv_uncertainty_package_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                cv_uncertainty_package_rel,\n                cv_uncertainty_package,\n                {\n                    "status": cv_uncertainty_package.get("status"),\n                    "data_role": "SOURCE_PROVENANCE_BOUNDARY_NOT_CALIBRATION",\n                    "raw_sha256": cv_uncertainty_package.get("source", {}).get("local_raw_sha256"),\n                    "equivalence_result": cv_uncertainty_package.get("mapping_contract", {}).get("equivalence_result"),\n                },\n            )\n        )\n    material_boundary_rel = rel(material_boundary_path)',
        "uncertainty boundary evidence projection",
    )
    text = replace_once(
        text,
        '    if discovered_lane_integrations.get("ding_material_regime_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Ding/comparator material-regime equivalence is closed as a scoped no-go; comparator c_v and c_p lanes cannot substitute for Ding C_src")',
        '    if discovered_lane_integrations.get("iaea_cv_uncertainty_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("IAEA Table 4.11 uncertainty-grade volumetric c_v route is closed as a scoped no-go; probable error is not promoted to c_v uncertainty")\n    if discovered_lane_integrations.get("ding_material_regime_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Ding/comparator material-regime equivalence is closed as a scoped no-go; comparator c_v and c_p lanes cannot substitute for Ding C_src")',
        "uncertainty boundary closure summary",
    )
    FULL_GATE_SCRIPT.write_text(text, encoding="utf-8")

    register = REGISTER_SCRIPT.read_text(encoding="utf-8")
    register = replace_once(
        register,
        '    ("T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR", "iaea_graphite_table_cv_comparator"),\n    ("T13_DING_MATERIAL_REGIME_BOUNDARY", "ding_material_regime_boundary"),',
        '    ("T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR", "iaea_graphite_table_cv_comparator"),\n    ("T13_IAEA_CV_UNCERTAINTY_BOUNDARY", "iaea_cv_uncertainty_boundary"),\n    ("T13_DING_MATERIAL_REGIME_BOUNDARY", "ding_material_regime_boundary"),',
        "register lane list",
    )
    REGISTER_SCRIPT.write_text(register, encoding="utf-8")
    print("integrated IAEA c_v uncertainty boundary into Topic 13 full gate and register sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
