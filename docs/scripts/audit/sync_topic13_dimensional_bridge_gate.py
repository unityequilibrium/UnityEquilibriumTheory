"""Attach the conditional dimensional-bridge result to the Topic 13 gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_dimensional_bridge_contract_audit.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    gate = json.loads(GATE.read_text(encoding="utf-8-sig"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    path = rel(AUDIT)
    digest = sha256(AUDIT)
    alpha = gate["verification_status"]["alpha_Phi_K"]
    alpha.update(
        {
            "conditional_derivation_status": audit["status"],
            "conditional_derivation_artifact": {"path": path, "sha256": digest},
            "conditional_formula_status": "CLOSED_FOR_LANE",
            "conditional_unit_contract_status": "CLOSED_FOR_LANE",
            "conditional_open_inputs": audit["major_result"]["open_blockers"],
            "conditional_next_controller": audit["next_controller"],
            "independent_calibration_or_derivation": False,
            "controlling_blocker": "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing",
        }
    )
    closed = gate["major_result"].setdefault("what_is_closed", [])
    item = "conditional local-equilibrium alpha formula and dimensional unit contract"
    if item not in closed:
        closed.append(item)
    remains = gate["major_result"].setdefault("what_remains_open", [])
    conditional_blocker = "conditional_alpha_inputs_a_Phi_T_e0_and_equilibrium_reference_not_source_locked"
    if conditional_blocker not in remains:
        remains.insert(0, conditional_blocker)
    evidence = gate.setdefault("evidence_artifacts", [])
    evidence[:] = [item for item in evidence if item.get("path") != path]
    evidence.append(
        {
            "path": path,
            "sha256": digest,
            "summary": {
                "status": audit["status"],
                "conditional_formula_status": "CLOSED_FOR_LANE",
                "independent_calibration": False,
                "target_data_used": False,
                "xie_2026_accessed": False,
            },
        }
    )
    gate["claim_promotion"] = False
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": gate["status"],
                "conditional_derivation_status": audit["status"],
                "controlling_blocker": gate["controlling_blocker"],
                "artifact": path,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
