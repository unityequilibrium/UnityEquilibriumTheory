"""Attach the passing coupled C/Phi lane to the Topic 13 closure gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
COUPLED = ROOT / "docs/core/07_artifacts/verification/matter_space_flux_phi_coupled_verification.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _append_once(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def main() -> int:
    gate = json.loads(GATE.read_text(encoding="utf-8-sig"))
    coupled = json.loads(COUPLED.read_text(encoding="utf-8-sig"))
    checks = coupled.get("verification", {}).get("checks", {})
    coupled_pass = coupled.get("status") == "PASS" and all(checks.values())
    coupled_path = rel(COUPLED)

    major_result = coupled.setdefault("major_result", {})
    major_result.update(
        {
            "major_result_id": "T13_CAUSAL_FLUX_PHI_COUPLED_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if coupled_pass else "PARTIAL",
            "verification_status": coupled.get("status"),
            "evidence_artifacts": [{"path": coupled_path}],
        }
    )
    COUPLED.write_text(
        json.dumps(coupled, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    coupled_hash = sha256(COUPLED)

    causal = gate["verification_status"]["causal_full_candidate_or_formal_no_go_branch"]
    causal["named_coupled_branch_pass"] = bool(coupled_pass)
    causal["named_coupled_branch_closure_level"] = major_result["closure_level"]
    causal["named_coupled_branch_artifact"] = {
        "path": coupled_path,
        "sha256": coupled_hash,
    }
    causal["full_candidate_pass"] = False
    causal["status"] = "BLOCKED"

    remains = gate["major_result"].setdefault("what_remains_open", [])
    remains[:] = [
        item
        for item in remains
        if item != "full coupled flux-telegraph C/Phi integration and rerun of full-candidate gate"
    ]
    closed = gate["major_result"].setdefault("what_is_closed", [])

    if coupled_pass:
        causal["controlling_blocker"] = "original_conserved_c_gradient_baseline_blocked"
        _append_once(
            closed,
            "named conserved C/Phi flux-telegraph lane with CLOSED_FOR_LANE internal verification",
        )
        _append_once(
            remains,
            "original conserved-C kappa_C>0 gradient baseline remains blocked by scoped no-go",
        )
        gate["controlling_blocker"] = "ttg_numeric_source_package_is_provisional"
        gate["next_action"] = (
            "Lock a permitted numeric TTG source package with locator, units, "
            "uncertainty, preprocessing, row identity, and hash; then close "
            "independent alpha_Phi_K calibration without reading Xie 2026."
        )
    else:
        causal["controlling_blocker"] = "full_coupled_flux_branch_integration_missing"
        _append_once(
            remains,
            "full coupled flux-telegraph C/Phi integration and rerun of full-candidate gate",
        )
        gate["controlling_blocker"] = "full_coupled_flux_branch_integration_missing"
        gate["next_action"] = (
            "Repair the named coupled C/Phi lane, then rerun full-candidate leakage, "
            "temporal/spatial convergence, and shared energy ledger."
        )

    evidence = gate.setdefault("evidence_artifacts", [])
    evidence[:] = [item for item in evidence if item.get("path") != coupled_path]
    evidence.append(
        {
            "path": coupled_path,
            "sha256": coupled_hash,
            "summary": {
                "status": coupled.get("status"),
                "branch_id": coupled.get("branch_id"),
                "closure_level": major_result["closure_level"],
            },
        }
    )
    gate["claim_promotion"] = False
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": gate["status"],
        "controlling_blocker": gate["controlling_blocker"],
        "coupled_status": coupled.get("status"),
        "coupled_closure_level": major_result["closure_level"],
        "full_candidate_pass": causal["full_candidate_pass"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
