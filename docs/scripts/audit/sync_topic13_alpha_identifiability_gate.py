"""Attach the alpha_Phi_K normalized-scale no-go to the Topic 13 gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_alpha_phi_k_identifiability_audit.json"


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
    alpha.update({
        "status": "BLOCKED",
        "status_recorded": "NO_GO_NORMALIZED_SCALE_IDENTIFIABILITY",
        "independent_calibration_or_derivation": False,
        "uncertainty_status": "alpha uncertainty remains open because no dimensional anchor exists",
        "identifiability_status": "NO_GO_FROM_NORMALIZED_PHI",
        "identifiability_artifact": {"path": path, "sha256": digest},
        "controlling_blocker": "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing",
    })
    closed = gate["major_result"].setdefault("what_is_closed", [])
    item = "normalized Phi lane scale non-identifiability is closed as a structural no-go"
    if item not in closed:
        closed.append(item)
    remains = gate["major_result"].setdefault("what_remains_open", [])
    remains[:] = [
        item
        for item in remains
        if item != "alpha_Phi_K_independent_calibration_missing"
    ]
    blocker = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    if blocker not in remains:
        remains.insert(0, blocker)
    gate["controlling_blocker"] = blocker
    gate["next_action"] = (
        "Derive a dimensional Phi/energy normalization or create an independent alpha_Phi_K "
        "calibration record with uncertainty; do not use TTG target residuals or Xie 2026 to choose it."
    )
    evidence = gate.setdefault("evidence_artifacts", [])
    evidence[:] = [item for item in evidence if item.get("path") != path]
    evidence.append({
        "path": path,
        "sha256": digest,
        "summary": {
            "status": audit["status"],
            "identifiability_status": "NO_GO_FROM_NORMALIZED_PHI",
            "target_data_used": False,
            "xie_2026_accessed": False,
        },
    })
    gate["claim_promotion"] = False
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": gate["status"],
        "controlling_blocker": gate["controlling_blocker"],
        "artifact": path,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
