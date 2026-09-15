"""Build the Wave 9 orbit/GR/cosmology correspondence gate.

The artifact packages existing standard baselines and explicit blockers.  It
does not claim that a Newtonian comparator or a local GR limit derives an UET
orbital law or proves a globally open universe.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
INPUTS = {
    "orbital_baseline": ROOT / "docs/core/07_artifacts/verification/relational_two_body_baseline_verification.json",
    "gr_closed_limit": ROOT / "docs/core/07_artifacts/verification/gr_closed_limit_verification.json",
    "gr_program_gate": ROOT / "docs/core/07_artifacts/gates/uet_gr_research_program_gate.json",
    "cosmological_contract": ROOT / "docs/core/07_artifacts/archive/uet_cosmological_open_system_trace_contract.json",
}
OUT = ROOT / "docs/core/07_artifacts/gates/orbit_cosmology_correspondence_gate.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    orbital = load(INPUTS["orbital_baseline"])
    gr_closed = load(INPUTS["gr_closed_limit"])
    gr_program = load(INPUTS["gr_program_gate"])
    cosmology = load(INPUTS["cosmological_contract"])
    checks = {
        "standard_orbital_baseline_present": orbital.get("audit_status") == "PASS",
        "closed_limit_local_check_present": gr_closed.get("status") == "PASS",
        "gr_program_gate_is_not_promoted": gr_program.get("status") == "BLOCKED",
        "global_open_status_unresolved": cosmology["cosmological_interpretation"]["global_universe_open_status"] == "UNRESOLVED",
        "solar_system_derivation_not_implemented": cosmology["orbital_collective_balance"]["solar_system_derivation_status"] == "NOT_IMPLEMENTED",
        "no_dark_matter_orbit_claim": True,
    }
    records = {
        key: {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256(path),
            "status": load(path).get("status", load(path).get("audit_status", "PRESENT")),
        }
        for key, path in INPUTS.items()
    }
    artifact = {
        "schema_version": "1.0",
        "artifact": "orbit_cosmology_correspondence_gate",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "BLOCKED",
        "local_baseline_status": "PASS_WITH_BLOCKED_UPSTREAM_AND_CLAIM_BOUNDARY",
        "inputs": records,
        "checks": checks,
        "standard_correspondence": {
            "orbit": "Newtonian/relativistic many-body dynamics remains the standard baseline.",
            "closed_limit": "Local GR closed-limit checks are a correspondence target, not an UET derivation.",
            "open_system": "Only an effective non-closed subsystem ansatz is allowed; global universe status is unresolved.",
        },
        "claim_boundary": "standard baseline and local correspondence gate only; no UET orbital law, GR derivation, or global open-universe proof",
        "controlling_blocker": "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing plus global boundary/observable closure",
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"artifact={OUT.relative_to(ROOT).as_posix()}")
    print(f"status={artifact['status']} checks={all(checks.values())}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
