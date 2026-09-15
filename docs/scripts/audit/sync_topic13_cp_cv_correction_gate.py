"""Attach the cp-cv formula contract to the Topic 13 full bridge gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_cp_cv_correction_audit.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_once(values: list[str], item: str) -> None:
    if item not in values:
        values.append(item)


def main() -> int:
    gate = json.loads(GATE.read_text(encoding="utf-8-sig"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    audit_path = rel(AUDIT)
    audit_digest = sha256(AUDIT)
    branch = gate["verification_status"]["alpha_Phi_K"].setdefault(
        "named_energy_response_branch", {}
    )
    branch["cp_cv_correction_contract"] = {
        "major_result_id": audit["major_result"]["major_result_id"],
        "status": audit["status"],
        "audit": {"path": audit_path, "sha256": audit_digest},
        "c_v_status": "OPEN_SOURCE_INPUTS",
        "numeric_material_inputs_consumed": False,
        "open_blockers": audit["major_result"]["open_blockers"],
    }
    closed = gate["major_result"].setdefault("what_is_closed", [])
    append_once(
        closed,
        "standard c_p-to-c_v correction formula, unit contract, and first-order uncertainty propagation",
    )
    remains = gate["major_result"].setdefault("what_remains_open", [])
    for blocker in audit["major_result"]["open_blockers"]:
        append_once(remains, blocker)
    evidence = gate.setdefault("evidence_artifacts", [])
    evidence[:] = [item for item in evidence if item.get("path") != audit_path]
    evidence.append(
        {
            "path": audit_path,
            "sha256": audit_digest,
            "summary": {"status": audit["status"], "numeric_inputs_consumed": False},
        }
    )
    gate["data_role"]["cp_cv_correction_contract"] = (
        "FORMULA_CONTRACT_ONLY; alpha_V, K_T, density uncertainty, and material regime remain open"
    )
    gate["claim_promotion"] = False
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"status": gate["status"], "correction_status": audit["status"], "audit": audit_path},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
