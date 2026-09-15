"""Integrate the public Ding supplementary boundary lane into the full gate."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "'T13_DING_C_SRC_INDEPENDENT_REPRODUCTION_BOUNDARY': 'ding_c_src_independent_reproduction_boundary',",
        "'T13_DING_C_SRC_INDEPENDENT_REPRODUCTION_BOUNDARY': 'ding_c_src_independent_reproduction_boundary', 'T13_DING_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY': 'ding_public_supplementary_payload_boundary',",
        "lane registry",
    )
    text = replace_once(
        text,
        '''    ding_c_src_boundary_path, ding_c_src_boundary = load(\n        "docs/core/07_artifacts/topic13/t13_ding_c_src_independent_reproduction_boundary_audit.json"\n    )''',
        '''    ding_c_src_boundary_path, ding_c_src_boundary = load(\n        "docs/core/07_artifacts/topic13/t13_ding_c_src_independent_reproduction_boundary_audit.json"\n    )\n    ding_public_supplementary_path, ding_public_supplementary = load(\n        "docs/core/07_artifacts/topic13/t13_ding_public_supplementary_payload_boundary_audit.json"\n    )''',
        "artifact load",
    )
    old_placement = '''    if ding_c_src_boundary_lane:\n        artifact["verification_status"]["source_package"][\n            "ding_c_src_independent_reproduction_boundary"\n        ] = ding_c_src_boundary_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "ding_c_src_independent_reproduction_boundary", None\n        )'''
    new_placement = old_placement + '''\n    ding_public_supplementary_lane = discovered_lane_integrations.get(\n        "ding_public_supplementary_payload_boundary"\n    )\n    if ding_public_supplementary_lane:\n        artifact["verification_status"]["source_package"][\n            "ding_public_supplementary_payload_boundary"\n        ] = ding_public_supplementary_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "ding_public_supplementary_payload_boundary", None\n        )'''
    text = replace_once(text, old_placement, new_placement, "source lane placement")
    text = replace_once(
        text,
        '''    if discovered_lane_integrations.get("ding_c_src_independent_reproduction_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("independent c_v comparator boundary is closed for lane without promoting it to Ding C_src")''',
        '''    if discovered_lane_integrations.get("ding_c_src_independent_reproduction_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("independent c_v comparator boundary is closed for lane without promoting it to Ding C_src")\n    if discovered_lane_integrations.get("ding_public_supplementary_payload_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("Ding public supplementary payload boundary is closed for lane without promoting PDFs or figures to numeric C_src")''',
        "lane closure note",
    )
    text = replace_once(
        text,
        '''    existing_evidence_paths = {item.get("path") for item in artifact.get("evidence_artifacts", [])}''',
        '''    public_supplementary_rel = rel(ding_public_supplementary_path)\n    if public_supplementary_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                public_supplementary_rel,\n                ding_public_supplementary,\n                {\n                    "status": ding_public_supplementary.get("status"),\n                    "closure_level": ding_public_supplementary.get("major_result", {}).get("closure_level"),\n                    "numeric_payload_objects": len(ding_public_supplementary.get("source", {}).get("numeric_payload_objects", [])),\n                    "controlling_blocker": ding_public_supplementary.get("controlling_blocker"),\n                },\n            )\n        )\n    existing_evidence_paths = {item.get("path") for item in artifact.get("evidence_artifacts", [])}''',
        "top-level evidence",
    )
    TARGET.write_text(text, encoding="utf-8")
    print(f"integrated {TARGET.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
