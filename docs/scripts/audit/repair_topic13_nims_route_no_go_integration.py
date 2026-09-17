"""Integrate the NIMS graphite source-route no-go into the Topic 13 gate."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    text = GATE.read_text(encoding="utf-8-sig")
    text = replace_once(
        text,
        "'T13_CALORINE_ZENODO_NEP_BTE_CANDIDATE_BOUNDARY': 'calorine_zenodo_nep_bte_candidate_boundary'}",
        "'T13_CALORINE_ZENODO_NEP_BTE_CANDIDATE_BOUNDARY': 'calorine_zenodo_nep_bte_candidate_boundary', 'T13_NIMS_GRAPHITE_LTC_ROUTE_NO_GO': 'nims_graphite_ltc_route_no_go'}",
        "lane mapping",
    )
    text = replace_once(
        text,
        '    calorine_candidate_path, calorine_candidate = load(\n'
        '        "docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json"\n'
        '    )\n',
        '    calorine_candidate_path, calorine_candidate = load(\n'
        '        "docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json"\n'
        '    )\n'
        '    nims_graphite_route_path, nims_graphite_route = load(\n'
        '        "docs/core/07_artifacts/topic13/t13_nims_graphite_ltc_route_no_go.json"\n'
        '    )\n',
        "artifact load",
    )
    text = replace_once(
        text,
        '            evidence(rel(calorine_candidate_path), calorine_candidate, {\n'
        '                "status": calorine_candidate.get("status"),\n'
        '                "accepted_for_full_topic13": calorine_candidate.get("acceptance", {}).get("accepted_for_full_topic13"),\n'
        '                "controlling_blocker": calorine_candidate.get("controlling_blocker"),\n'
        '            }),\n',
        '            evidence(rel(calorine_candidate_path), calorine_candidate, {\n'
        '                "status": calorine_candidate.get("status"),\n'
        '                "accepted_for_full_topic13": calorine_candidate.get("acceptance", {}).get("accepted_for_full_topic13"),\n'
        '                "controlling_blocker": calorine_candidate.get("controlling_blocker"),\n'
        '            }),\n'
        '            evidence(rel(nims_graphite_route_path), nims_graphite_route, {\n'
        '                "status": nims_graphite_route.get("status"),\n'
        '                "route_closed_as_no_go": nims_graphite_route.get("acceptance", {}).get("route_closed_as_no_go"),\n'
        '                "controlling_blocker": nims_graphite_route.get("controlling_blocker"),\n'
        '            }),\n',
        "evidence projection",
    )
    text = replace_once(
        text,
        '    ding_public_supplementary_lane = discovered_lane_integrations.get(\n'
        '        "ding_public_supplementary_payload_boundary"\n'
        '    )\n',
        '    nims_graphite_route_lane = discovered_lane_integrations.get(\n'
        '        "nims_graphite_ltc_route_no_go"\n'
        '    )\n'
        '    if nims_graphite_route_lane:\n'
        '        artifact["verification_status"]["source_package"][\n'
        '            "nims_graphite_ltc_route_no_go"\n'
        '        ] = nims_graphite_route_lane\n'
        '        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n'
        '            "nims_graphite_ltc_route_no_go", None\n'
        '        )\n'
        '    ding_public_supplementary_lane = discovered_lane_integrations.get(\n'
        '        "ding_public_supplementary_payload_boundary"\n'
        '    )\n',
        "source-package projection",
    )
    GATE.write_text(text, encoding="utf-8")
    print("integrated NIMS route no-go")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
