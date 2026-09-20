"""Attach the scoped Georgia Tech source-independence no-go to Topic 13."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_gatech_volumetric_cp_independence_audit.json"


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
    branch["source_independence_no_go"] = {
        "major_result_id": audit["major_result"]["major_result_id"],
        "status": audit["status"],
        "closure_level": audit["major_result"]["closure_level"],
        "audit": {"path": audit_path, "sha256": audit_digest},
        "same_workbook_density_inversion_allowed": False,
        "same_workbook_volumetric_cp_inversion_allowed": False,
        "open_blockers": audit["major_result"]["open_blockers"],
    }

    closed = gate["major_result"].setdefault("what_is_closed", [])
    append_once(
        closed,
        "scoped no-go for independent density or volumetric heat-capacity recovery from the Georgia Tech k/D/c_p row",
    )
    remains = gate["major_result"].setdefault("what_remains_open", [])
    stale = {
        "Cp_to_c_v_thermodynamic_correction_missing",
        "density_uncertainty_missing_for_volumetric_conversion",
        "source_k_is_derived_not_independent_density_evidence",
    }
    remains[:] = [item for item in remains if item not in stale]
    for blocker in audit["major_result"]["open_blockers"]:
        append_once(remains, blocker)

    evidence = gate.setdefault("evidence_artifacts", [])
    evidence[:] = [item for item in evidence if item.get("path") != audit_path]
    evidence.append(
        {
            "path": audit_path,
            "sha256": audit_digest,
            "summary": {
                "status": audit["status"],
                "scope": "Georgia Tech same-workbook k/D/c_p independence only",
            },
        }
    )
    gate["data_role"]["gatech_volumetric_property_route"] = (
        "SOURCE_ROUTE_REJECTED_AS_CIRCULAR; no density, volumetric c_p, or c_v calibration consumed"
    )
    gate["next_action"] = (
        "source-lock a direct volumetric c_v or independently measured same-grade density "
        "with uncertainty plus same-regime alpha_V and K_T; do not invert Georgia Tech k/D/c_p; "
        "then independently derive or calibrate e0 and prove base Phi-to-Phi_E without TTG target "
        "residuals or Xie 2026"
    )
    gate["claim_promotion"] = False
    GATE.write_text(
        json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": gate["status"],
                "source_no_go": audit["status"],
                "audit": audit_path,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
