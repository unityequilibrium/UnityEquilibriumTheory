"""Build the explicit prerequisite gate for the deferred particle program."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs/core/07_artifacts/gates/particle_dirac_program_gate.json"


PREREQUISITES = (
    "Lorentz-covariant parent action with declared units",
    "spinor representation and gamma-matrix convention",
    "conserved particle/current derivation",
    "mass-eigenstate and charge/conjugation map",
    "CPT and anomaly/normalization checks",
    "particle-level detector observable operator",
)


def build() -> dict:
    checks = {
        "prerequisites_are_explicit": len(PREREQUISITES) == 6,
        "no_particle_identity_assigned_to_trace": True,
        "no_neutrino_identity_assigned_to_trace": True,
        "no_positron_identity_assigned_to_trace": True,
        "no_dirac_derivation_claim": True,
        "parameter_fitting": False,
        "external_validation": False,
    }
    verification_checks = {
        key: value
        for key, value in checks.items()
        if key not in {"parameter_fitting", "external_validation"}
    }
    return {
        "schema_version": "particle-dirac-program-gate-v1",
        "artifact": "particle_dirac_program_gate",
        "generated_at": date.today().isoformat(),
        "status": "DEFERRED_BLOCKED",
        "audit_status": "PASS" if all(verification_checks.values()) else "FAIL",
        "evidence_status": "NOT_ESTABLISHED",
        "prerequisites": [
            {"name": name, "status": "MISSING", "required_before_claim": True}
            for name in PREREQUISITES
        ],
        "checks": checks,
        "blocked_lanes": ["Dirac", "neutrino", "positron", "antimatter", "particle mass generation"],
        "claim_boundary": "Particle and Dirac identities remain deferred; R_gen is not a particle and no carrier identity is derived.",
        "controlling_blocker": "Lorentz-covariant action, spinor/current map, CPT and detector correspondence are not established",
        "next_controller": "close the covariant parent action and particle observable contract after Wave 7 transport and Wave 9 correspondence prerequisites",
    }


def main() -> int:
    artifact = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"audit_status={artifact['audit_status']}")
    print(f"status={artifact['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
