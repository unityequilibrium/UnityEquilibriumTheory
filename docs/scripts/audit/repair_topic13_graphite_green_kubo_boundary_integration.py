"""Integrate the public Green-Kubo source boundary into Topic 13 state metadata."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"
SYNC = ROOT / "docs/scripts/audit/sync_topic13_major_result_lanes.py"

LANE_ID = "T13_GRAPHITE_GREEN_KUBO_SOURCE_BOUNDARY"
LANE_KEY = "graphite_green_kubo_source_boundary"
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_graphite_green_kubo_source_boundary_audit.json"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_gate() -> bool:
    text = GATE.read_text(encoding="utf-8-sig")
    original = text

    if LANE_ID not in text:
        marker = "'T13_UET_O2_EQUILIBRIUM_KMS_LANE': 'uet_o2_equilibrium_kms_lane'}"
        replacement = marker[:-1] + f", '{LANE_ID}': '{LANE_KEY}'}}"
        text = replace_once(text, marker, replacement, "full-gate lane registry")

    load_marker = '''    equilibrium_kms_path, equilibrium_kms = load(
        "docs/core/07_artifacts/topic13/t13_uet_o2_equilibrium_kms_audit.json"
    )
'''
    load_block = load_marker + '''    graphite_green_kubo_path, graphite_green_kubo = load(
        "docs/core/07_artifacts/topic13/t13_graphite_green_kubo_source_boundary_audit.json"
    )
'''
    if "graphite_green_kubo_path, graphite_green_kubo" not in text:
        text = replace_once(text, load_marker, load_block, "full-gate Green-Kubo artifact load")

    evidence_marker = "    iaea_graphite_cv_rel = rel(iaea_graphite_cv_path)"
    evidence_block = '''    graphite_green_kubo_rel = rel(graphite_green_kubo_path)
    if graphite_green_kubo_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                graphite_green_kubo_rel,
                graphite_green_kubo,
                {
                    "status": graphite_green_kubo.get("status"),
                    "closure_level": graphite_green_kubo.get("major_result", {}).get("closure_level"),
                    "data_role": graphite_green_kubo.get("major_result", {}).get("data_role"),
                    "failed_checks": graphite_green_kubo.get("failed_checks"),
                    "controlling_blocker": graphite_green_kubo.get("controlling_blocker"),
                },
            )
        )
'''
    if "graphite_green_kubo_rel = rel(graphite_green_kubo_path)" not in text:
        text = replace_once(text, evidence_marker, evidence_block + evidence_marker, "full-gate Green-Kubo evidence")

    closure_marker = '    if discovered_lane_integrations.get("iaea_cv_uncertainty_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":'
    closure_block = '''    if discovered_lane_integrations.get("graphite_green_kubo_source_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("public graphite/graphene Green-Kubo source boundary is closed as comparator evidence without UET space-response, Ding state, physical Kubo, or alpha promotion")
'''
    if "public graphite/graphene Green-Kubo source boundary is closed" not in text:
        text = replace_once(text, closure_marker, closure_block + closure_marker, "lane-closure projection")

    if text != original:
        GATE.write_text(text, encoding="utf-8")
        return True
    return False


def patch_sync() -> bool:
    text = SYNC.read_text(encoding="utf-8-sig")
    original = text
    anchor = '    ("T13_UET_O2_EQUILIBRIUM_KMS_LANE", "uet_o2_equilibrium_kms_lane"),\n'
    addition = anchor + f'    ("{LANE_ID}", "{LANE_KEY}"),\n'
    if LANE_ID not in text:
        text = replace_once(text, anchor, addition, "major-result lane list")
    if text != original:
        SYNC.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed_gate = patch_gate()
    changed_sync = patch_sync()
    print(
        {
            "status": "PASS_TOPIC13_GRAPHITE_GREEN_KUBO_BOUNDARY_INTEGRATION_REPAIR",
            "gate_changed": changed_gate,
            "sync_changed": changed_sync,
            "audit_artifact": AUDIT_REL,
            "full_core_unlock": False,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

