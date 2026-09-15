"""Attach the generated Topic 0.13 branch gate to the Wave 1 contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "docs/core/07_artifacts/archive/uet_research_room_wave1_contract.json"
BRANCH = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/thermal_wave1_branch_gate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    branch = json.loads(BRANCH.read_text(encoding="utf-8-sig"))
    room = contract["rooms"]["topic_0_13"]
    room["verification_status"] = branch.get("status")
    room["controlling_blocker"] = branch.get("controlling_blocker")
    room["selected_causal_branch"] = {
        "verification_status": branch.get("selected_causal_branch", {}).get("status", branch.get("status")),
        "prearrival_leakage_fraction": branch.get("selected_causal_branch", {}).get("prearrival_leakage_fraction"),
        "threshold": branch.get("selected_causal_branch", {}).get("threshold"),
        "full_candidate_gate_preserved": True,
        "full_candidate_prearrival_leakage_fraction": branch.get("full_candidate_branch", {}).get("prearrival_leakage_fraction"),
        "claim_boundary": branch.get("selected_causal_branch", {}).get("claim_boundary"),
        "evidence": [{"path": "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/thermal_wave1_branch_gate.json", "present": True, "sha256": sha256(BRANCH), "summary": {"status": branch.get("status"), "gates": branch.get("gates")}}],
    }
    room["evidence"].insert(1, {"path": "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/thermal_wave1_branch_gate.json", "present": True, "sha256": sha256(BRANCH), "summary": {"status": branch.get("status"), "controlling_blocker": branch.get("controlling_blocker")}})
    contract["integration_blockers"] = sorted(set(contract.get("integration_blockers", []) + [branch.get("controlling_blocker"), "alpha_Phi_K has no independent derivation or calibration with uncertainty"]))
    contract["thermal_branch_gate"] = {"path": "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/thermal_wave1_branch_gate.json", "sha256": sha256(BRANCH), "status": branch.get("status")}
    CONTRACT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": branch.get("status"), "contract": str(CONTRACT)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
