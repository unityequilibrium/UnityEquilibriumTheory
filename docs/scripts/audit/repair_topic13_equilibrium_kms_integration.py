"""Register the Topic 13 equilibrium KMS lane without changing full closure."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"
SYNC = ROOT / "docs/scripts/audit/sync_topic13_major_result_lanes.py"

LANE_ID = "T13_UET_O2_EQUILIBRIUM_KMS_LANE"
LANE_KEY = "uet_o2_equilibrium_kms_lane"
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_equilibrium_kms_audit.json"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        raise RuntimeError(f"missing integration anchor: {label}")
    if count > 1:
        raise RuntimeError(f"ambiguous integration anchor: {label} ({count})")
    return text.replace(old, new, 1)


def patch_gate() -> bool:
    text = GATE.read_text(encoding="utf-8-sig")
    original = text
    mapping_old = "'T13_UET_O2_FINITE_T_QUASIPARTICLE_EOS_LANE': 'uet_o2_finite_t_quasiparticle_eos_lane'}"
    mapping_new = "'T13_UET_O2_FINITE_T_QUASIPARTICLE_EOS_LANE': 'uet_o2_finite_t_quasiparticle_eos_lane', 'T13_UET_O2_EQUILIBRIUM_KMS_LANE': 'uet_o2_equilibrium_kms_lane'}"
    if LANE_ID not in text:
        text = replace_once(text, mapping_old, mapping_new, "full-gate lane registry")

    load_old = """    finite_qp_eos_path, finite_qp_eos = load(
        "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_quasiparticle_eos_audit.json"
    )
"""
    load_new = load_old + """    equilibrium_kms_path, equilibrium_kms = load(
        "docs/core/07_artifacts/topic13/t13_uet_o2_equilibrium_kms_audit.json"
    )
"""
    if "equilibrium_kms_path, equilibrium_kms" not in text:
        text = replace_once(text, load_old, load_new, "full-gate KMS artifact load")

    evidence_marker = "      iaea_graphite_cv_rel = rel(iaea_graphite_cv_path)"
    evidence_block = """      equilibrium_kms_rel = rel(equilibrium_kms_path)
      if equilibrium_kms_rel not in {
          item.get("path") for item in artifact.get("evidence_artifacts", [])
          if isinstance(item, dict)
      }:
          artifact["evidence_artifacts"].append(
              evidence(
                  equilibrium_kms_rel,
                  equilibrium_kms,
                  {
                      "status": equilibrium_kms.get("status"),
                      "closure_level": equilibrium_kms.get("major_result", {}).get("closure_level"),
                      "data_role": equilibrium_kms.get("major_result", {}).get("data_role"),
                      "failed_checks": equilibrium_kms.get("failed_checks"),
                      "controlling_blocker": equilibrium_kms.get("controlling_blocker"),
                  },
              )
          )
"""
    if "equilibrium_kms_rel = rel(equilibrium_kms_path)" not in text:
        text = replace_once(text, evidence_marker, evidence_block + evidence_marker, "full-gate KMS evidence")

    finite_clause = """    if discovered_lane_integrations.get("uet_o2_finite_t_quasiparticle_eos_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("finite-temperature O(2) tree-condensate plus quasiparticle EOS is closed for lane without interacting self-energy, physical Kubo, SI, or alpha promotion")
"""
    kms_clause = """    if discovered_lane_integrations.get("uet_o2_equilibrium_kms_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("equilibrium O(2) KMS/FDT identity lane is closed without promoting it to interacting SK, dissipative transport, physical Kubo, SI, or alpha")
"""
    if "equilibrium O(2) KMS/FDT identity lane is closed" not in text:
        if finite_clause in text:
            text = replace_once(text, finite_clause, finite_clause + kms_clause, "lane-closure projection")
        else:
            marker = '    if discovered_lane_integrations.get("iaea_cv_uncertainty_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":'
            text = replace_once(text, marker, kms_clause + marker, "lane-closure projection fallback")

    if text != original:
        GATE.write_text(text, encoding="utf-8")
        return True
    return False


def patch_sync() -> bool:
    text = SYNC.read_text(encoding="utf-8-sig")
    original = text
    anchor = '    ("T13_UET_O2_FINITE_T_QUASIPARTICLE_EOS_LANE", "uet_o2_finite_t_quasiparticle_eos_lane"),\n'
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
            "status": "PASS_TOPIC13_EQUILIBRIUM_KMS_INTEGRATION_REPAIR",
            "gate_changed": changed_gate,
            "sync_changed": changed_sync,
            "audit_artifact": AUDIT_REL,
            "full_core_unlock": False,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

