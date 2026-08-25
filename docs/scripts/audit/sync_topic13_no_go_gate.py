"""Attach the scoped conserved-C no-go assessment to the Topic 13 gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
NO_GO = ROOT / "docs/core/artifacts/conserved_c_finite_cone_no_go_assessment.json"


def main() -> int:
    gate = json.loads(GATE.read_text(encoding="utf-8-sig"))
    no_go = json.loads(NO_GO.read_text(encoding="utf-8-sig"))
    no_go_path = NO_GO.relative_to(ROOT).as_posix()
    no_go_hash = hashlib.sha256(NO_GO.read_bytes()).hexdigest()
    telegraph_path = ROOT / "docs/core/artifacts/matter_space_conserved_flux_telegraph_verification.json"
    coupled_path = ROOT / "docs/core/artifacts/matter_space_flux_phi_coupled_verification.json"
    telegraph = json.loads(telegraph_path.read_text(encoding="utf-8-sig"))
    coupled = json.loads(coupled_path.read_text(encoding="utf-8-sig"))
    named_finite_cone_branch_pass = telegraph.get("status") == "PASS" and telegraph.get("major_result", {}).get("closure_level") == "CLOSED_FOR_LANE"
    named_coupled_branch_pass = coupled.get("status") == "PASS" and coupled.get("major_result", {}).get("closure_level") == "CLOSED_FOR_LANE"
    causal = gate["verification_status"]["causal_full_candidate_or_formal_no_go_branch"]
    causal["formal_no_go_recorded"] = no_go["status"] == "NO_GO_FOR_DECLARED_CONSERVED_CATTANEO_LOCAL_GRADIENT_CLASS"
    causal["no_go_scope"] = no_go["proof_scope"]
    causal["no_go_artifact"] = {"path": no_go_path, "sha256": no_go_hash}
    causal["named_finite_cone_branch_pass"] = named_finite_cone_branch_pass
    causal["named_finite_cone_branch_closure_level"] = telegraph.get("major_result", {}).get("closure_level", "OPEN")
    causal["named_coupled_branch_pass"] = named_coupled_branch_pass
    causal["named_coupled_branch_closure_level"] = coupled.get("major_result", {}).get("closure_level", "OPEN")
    causal["controlling_blocker"] = "original_conserved_c_gradient_baseline_blocked" if (causal["formal_no_go_recorded"] and named_finite_cone_branch_pass and named_coupled_branch_pass) else "named_finite_cone_branch_or_explicit_regularization_missing"
    alpha_gate = gate["verification_status"].get("alpha_Phi_K", {})
    gate["controlling_blocker"] = (
        "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
        if alpha_gate.get("status") == "BLOCKED"
        else gate.get("controlling_blocker")
    )
    closed_item = "scoped structural no-go assessment for the declared conserved-C local-gradient class"
    if closed_item not in gate["major_result"]["what_is_closed"]:
        gate["major_result"]["what_is_closed"].append(closed_item)
    gate["major_result"]["what_remains_open"] = [
        item
        for item in gate["major_result"]["what_remains_open"]
        if item not in {
            "formal_conserved_C_no_go_or_explicit_regularization_missing",
            "named finite-cone branch or explicit conserved-C regularization",
            "named_finite_cone_branch_or_explicit_regularization_missing",
        }
    ]
    evidence = gate.setdefault("evidence_artifacts", [])
    evidence[:] = [item for item in evidence if item.get("path") != no_go_path]
    evidence.append({"path": no_go_path, "sha256": no_go_hash, "summary": {"status": no_go["status"], "proof_scope": no_go["proof_scope"]}})
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": gate["status"], "controlling_blocker": gate["controlling_blocker"], "no_go_status": no_go["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
