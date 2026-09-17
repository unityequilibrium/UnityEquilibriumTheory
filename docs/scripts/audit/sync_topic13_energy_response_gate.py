"""Attach the named Phi_E energy-response result to the Topic 13 gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_energy_response_bridge_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "graphite_heat_capacity_source_package.json"
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    gate = json.loads(GATE.read_text(encoding="utf-8-sig"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    audit_path = rel(AUDIT)
    package_path = rel(PACKAGE)
    audit_digest = sha256(AUDIT)
    package_digest = sha256(PACKAGE)

    alpha = gate["verification_status"]["alpha_Phi_K"]
    alpha["named_energy_response_branch"] = {
        "branch_id": "T13-PHI-E-001",
        "status": audit["status"],
        "artifact": {"path": audit_path, "sha256": audit_digest},
        "source_package": {"path": package_path, "sha256": package_digest},
        "formula_status": "CLOSED_FOR_LANE",
        "base_Phi_identity": "not asserted",
        "base_Phi_to_Phi_E_mapping": "OPEN_DERIVATION_OR_CALIBRATION",
        "c_v_status": "OPEN_CP_TO_CV_UNCERTAINTY",
        "e0_status": "OPEN_NOT_SOURCE_LOCKED",
        "independent_base_alpha_calibration": False,
        "xie_2026_accessed": False,
    }

    closed = gate["major_result"].setdefault("what_is_closed", [])
    closed_item = "named Phi_E energy-response bridge algebra and uncertainty contract"
    if closed_item not in closed:
        closed.append(closed_item)
    remains = gate["major_result"].setdefault("what_remains_open", [])
    for blocker in audit["major_result"]["open_blockers"]:
        if blocker not in remains:
            remains.insert(0, blocker)

    gate["equation_or_mapping"]["named_energy_response"] = (
        "Phi_E = Delta_u/e0; Delta_Tq = Delta_u/c_v = (e0/c_v) Phi_E"
    )
    gate["units"]["Phi_E"] = "dimensionless named energy-response coordinate"
    gate["units"]["alpha_Phi_E_K"] = "K per normalized Phi_E; open until e0 and c_v are source-locked"
    gate["data_role"]["named_energy_response_source"] = "NIST Cp candidate only; c_v conversion and uncertainty open"

    evidence = gate.setdefault("evidence_artifacts", [])
    evidence[:] = [
        item for item in evidence if item.get("path") not in {audit_path, package_path}
    ]
    evidence.extend(
        [
            {
                "path": audit_path,
                "sha256": audit_digest,
                "summary": {
                    "status": audit["status"],
                    "branch_id": "T13-PHI-E-001",
                    "formula_status": "CLOSED_FOR_LANE",
                    "base_Phi_mapping": "OPEN",
                    "base_alpha_calibrated": False,
                    "xie_2026_accessed": False,
                },
            },
            {
                "path": package_path,
                "sha256": package_digest,
                "summary": {
                    "status": "SOURCE_IDENTITY_READY_CV_UNCERTAINTY_OPEN",
                    "required_quantity": "volumetric c_v",
                    "candidate_quantity": "molar Cp",
                    "numeric_rows_consumed": False,
                },
            },
        ]
    )
    gate["next_action"] = audit["next_controller"]
    gate["claim_promotion"] = False
    gate["claim_boundary"] = (
        "Full Topic 13 is not Core-ready. The named Phi_E branch closes only the "
        "conditional energy-response algebra; no identity with base Phi, numeric "
        "alpha_Phi_K, temperature prediction, external validation, or global UET closure is claimed."
    )
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": gate["status"],
                "named_branch_status": audit["status"],
                "controlling_blocker": gate["controlling_blocker"],
                "audit": audit_path,
                "source_package": package_path,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
