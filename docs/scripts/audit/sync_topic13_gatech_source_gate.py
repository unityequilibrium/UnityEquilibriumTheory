"""Attach the independent Georgia Tech c_p source anchor to the Topic 13 gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_gatech_graphite_source_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "gatech_gen3csp_graphite_source_package.json"
)
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/gen3csp_graphite.xlsx"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    gate = json.loads(GATE.read_text(encoding="utf-8-sig"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    audit_path = rel(AUDIT)
    package_path = rel(PACKAGE)
    raw_path = rel(RAW)
    audit_digest = sha256(AUDIT)
    package_digest = sha256(PACKAGE)
    raw_digest = sha256(RAW)

    branch = gate["verification_status"]["alpha_Phi_K"].setdefault("named_energy_response_branch", {})
    branch["source_anchor"] = {
        "major_result_id": audit["major_result"]["major_result_id"],
        "status": audit["status"],
        "audit": {"path": audit_path, "sha256": audit_digest},
        "source_package": {"path": package_path, "sha256": package_digest},
        "raw_workbook": {"path": raw_path, "sha256": raw_digest},
        "temperature_K": audit["row_identity"]["temperature_K"],
        "cp_mass_specific_J_per_g_K": audit["reported_values"]["average_specific_heat_J_per_g_K"],
        "uncertainty_95pct_J_per_g_K": audit["reported_values"]["uncertainty_95pct_J_per_g_K"],
        "c_v_status": "OPEN",
        "consumed_for_calibration": False,
    }
    closed = gate["major_result"].setdefault("what_is_closed", [])
    item = "independent Georgia Tech c_p row with 95% confidence source anchor"
    if item not in closed:
        closed.append(item)
    remains = gate["major_result"].setdefault("what_remains_open", [])
    for blocker in audit["major_result"]["open_blockers"]:
        if blocker not in remains:
            remains.insert(0, blocker)
    gate["data_role"]["independent_heat_capacity_source"] = "CALIBRATION_CANDIDATE_NOT_CONSUMED; c_v conversion remains open"
    evidence = gate.setdefault("evidence_artifacts", [])
    evidence[:] = [item for item in evidence if item.get("path") not in {audit_path, package_path, raw_path}]
    evidence.extend(
        [
            {"path": audit_path, "sha256": audit_digest, "summary": {"status": audit["status"], "c_v_status": "OPEN"}},
            {"path": package_path, "sha256": package_digest, "summary": {"status": "RAW_ARCHIVED_CP_95CI_CV_OPEN"}},
            {"path": raw_path, "sha256": raw_digest, "summary": {"bytes": RAW.stat().st_size}},
        ]
    )
    gate["claim_promotion"] = False
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": gate["status"], "source_status": audit["status"], "source_audit": audit_path}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
