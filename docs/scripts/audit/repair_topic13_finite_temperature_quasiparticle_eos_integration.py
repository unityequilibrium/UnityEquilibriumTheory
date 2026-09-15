"""Integrate the finite-temperature O(2) quasiparticle EOS lane."""

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
    text = FULL_GATE_SCRIPT.read_text(encoding="utf-8-sig")
    text = replace_once(
        text,
        "'T13_DESORBO_1955_CEYLON_GRAPHITE_CP_COMPARATOR': 'desorbo_1955_ceylon_graphite_cp_comparator'}",
        "'T13_DESORBO_1955_CEYLON_GRAPHITE_CP_COMPARATOR': 'desorbo_1955_ceylon_graphite_cp_comparator', 'T13_UET_O2_FINITE_T_QUASIPARTICLE_EOS_LANE': 'uet_o2_finite_t_quasiparticle_eos_lane'}",
        "finite-temperature EOS lane registry",
    )
    text = replace_once(
        text,
        '    material_boundary_path, material_boundary = load(\n',
        '    finite_qp_eos_path, finite_qp_eos = load(\n        "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_quasiparticle_eos_audit.json"\n    )\n    material_boundary_path, material_boundary = load(\n',
        "finite-temperature EOS audit loading",
    )
    text = replace_once(
        text,
        '    if discovered_lane_integrations.get("desorbo_1955_ceylon_graphite_cp_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("DeSorbo 1955 Ceylon natural-graphite numeric Cp comparator is closed for lane without standard uncertainty, volumetric c_v conversion, or Ding material-match promotion")\n',
        '    if discovered_lane_integrations.get("desorbo_1955_ceylon_graphite_cp_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("DeSorbo 1955 Ceylon natural-graphite numeric Cp comparator is closed for lane without standard uncertainty, volumetric c_v conversion, or Ding material-match promotion")\n    if discovered_lane_integrations.get("uet_o2_finite_t_quasiparticle_eos_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("finite-temperature O(2) tree-condensate plus quasiparticle EOS is closed for lane without interacting self-energy, physical Kubo, SI, or alpha promotion")\n',
        "finite-temperature EOS closure summary",
    )
    evidence_anchor = '    iaea_graphite_cv_rel = rel(iaea_graphite_cv_path)\n'
    evidence_addition = '''    finite_qp_eos_rel = rel(finite_qp_eos_path)
    if finite_qp_eos_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                finite_qp_eos_rel,
                finite_qp_eos,
                {
                    "status": finite_qp_eos.get("status"),
                    "closure_level": finite_qp_eos.get("major_result", {}).get("closure_level"),
                    "data_role": finite_qp_eos.get("major_result", {}).get("data_role"),
                    "failed_checks": finite_qp_eos.get("failed_checks"),
                    "controlling_blocker": finite_qp_eos.get("controlling_blocker"),
                },
            )
        )
'''
    text = replace_once(text, evidence_anchor, evidence_addition + evidence_anchor, "finite-temperature EOS evidence linkage")
    FULL_GATE_SCRIPT.write_text(text, encoding="utf-8")

    register = REGISTER_SCRIPT.read_text(encoding="utf-8")
    register = replace_once(
        register,
        '    ("T13_DESORBO_1955_CEYLON_GRAPHITE_CP_COMPARATOR", "desorbo_1955_ceylon_graphite_cp_comparator"),\n',
        '    ("T13_DESORBO_1955_CEYLON_GRAPHITE_CP_COMPARATOR", "desorbo_1955_ceylon_graphite_cp_comparator"),\n    ("T13_UET_O2_FINITE_T_QUASIPARTICLE_EOS_LANE", "uet_o2_finite_t_quasiparticle_eos_lane"),\n',
        "finite-temperature EOS register lane",
    )
    REGISTER_SCRIPT.write_text(register, encoding="utf-8")
    print("integrated finite-temperature O(2) quasiparticle EOS lane")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
