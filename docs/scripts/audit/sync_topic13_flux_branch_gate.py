"""Attach the passing named flux branch to the Topic 13 closure gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
BRANCH = ROOT / "docs/core/07_artifacts/verification/matter_space_conserved_flux_telegraph_verification.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    gate = json.loads(GATE.read_text(encoding="utf-8-sig"))
    branch = json.loads(BRANCH.read_text(encoding="utf-8-sig"))
    checks = branch.get("verification", {}).get("checks", {})
    branch_pass = branch.get("status") == "PASS" and all(checks.values())
    branch_path = rel(BRANCH)
    major_result = branch.setdefault("major_result", {})
    major_result.update(
        {
            "major_result_id": "T13_CAUSAL_FLUX_TELEGRAPH_BRANCH",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if branch_pass else "PARTIAL",
            "what_is_closed": [
                "conserved C flux-telegraph equations with local chemical potential",
                "finite-volume compact discrete domain of dependence",
                "mass conservation and normalized energy/dissipation diagnostic",
            ] if branch_pass else [],
            "equation_or_mapping": branch.get("equations", {}),
            "units": branch.get("units", {}),
            "derivation_class": branch.get("derivation_class"),
            "observable": "normalized C response and conserved flux diagnostic",
            "data_role": "internal numerical branch verification; not external thermal data",
            "evidence_artifacts": [{"path": branch_path}],
            "verification_status": branch.get("status"),
            "open_blockers": [
                "full coupled Phi integration",
                "full-candidate leakage rerun",
            ] if branch_pass else ["branch verifier is not passing"],
            "dependency_unlocked": "none; Topic 13 full bridge remains open",
            "claim_boundary": (
                "CLOSED_FOR_LANE only: this named normalized C flux branch does not "
                "replace the original kappa_C>0 baseline, close Phi transport, or "
                "establish SI or external thermal validity."
            ),
        }
    )
    BRANCH.write_text(json.dumps(branch, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    branch_hash = sha256(BRANCH)

    causal = gate["verification_status"]["causal_full_candidate_or_formal_no_go_branch"]
    causal["named_finite_cone_branch_pass"] = bool(branch_pass)
    causal["named_branch_closure_level"] = major_result["closure_level"]
    causal["named_branch_artifact"] = {"path": branch_path, "sha256": branch_hash}
    causal["full_candidate_pass"] = False
    causal["status"] = "BLOCKED"
    causal["controlling_blocker"] = (
        "full_coupled_flux_branch_integration_missing"
        if branch_pass
        else "named_finite_cone_branch_or_explicit_regularization_missing"
    )
    if branch_pass:
        if "named conserved flux-telegraph branch with CLOSED_FOR_LANE internal verification" not in gate["major_result"]["what_is_closed"]:
            gate["major_result"]["what_is_closed"].append(
                "named conserved flux-telegraph branch with CLOSED_FOR_LANE internal verification"
            )
        gate["major_result"]["what_remains_open"] = [
            item
            for item in gate["major_result"]["what_remains_open"]
            if item != "named finite-cone branch or explicit conserved-C regularization"
        ]
        gate["major_result"]["what_remains_open"].insert(
            0, "full coupled flux-telegraph C/Phi integration and rerun of full-candidate gate"
        )
        gate["controlling_blocker"] = "full_coupled_flux_branch_integration_missing"
        gate["next_action"] = (
            "Integrate the passing named C flux branch with the causal Phi lane, "
            "then rerun full-candidate leakage, temporal/spatial convergence, and shared energy ledger."
        )
    else:
        gate["controlling_blocker"] = "named_finite_cone_branch_or_explicit_regularization_missing"
    gate["evidence_artifacts"].append(
        {
            "path": branch_path,
            "sha256": branch_hash,
            "summary": {
                "status": branch.get("status"),
                "branch_id": branch.get("branch_id"),
                "closure_level": major_result["closure_level"],
            },
        }
    )
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": gate["status"],
        "controlling_blocker": gate["controlling_blocker"],
        "branch_status": branch.get("status"),
        "branch_closure_level": major_result["closure_level"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
