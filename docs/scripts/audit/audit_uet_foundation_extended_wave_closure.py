"""Build explicit status for the downstream foundation waves 7-11."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]


def load(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    return json.loads(path.read_text(encoding="utf-8"))


def first_status(payload: dict[str, Any]) -> str:
    for key in ("status", "audit_status", "evidence_status", "dependency_status"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return "UNSPECIFIED"


def controller(payload: dict[str, Any]) -> str:
    for key in ("controlling_blocker", "next_controller", "controller"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return "not_declared"


def build() -> dict[str, Any]:
    eos = load("docs/core/07_artifacts/verification/o2_finite_density_eos_verification.json")
    eos_audit = load("docs/core/07_artifacts/correspondence/o2_eos_formula_audit.json")
    transport = load("docs/core/07_artifacts/verification/covariant_superfluid_transport_verification.json")
    impact = load("docs/core/07_artifacts/verification/impact_effect_core_verification.json")
    impact_gate = load("docs/core/07_artifacts/gates/impact_effect_dependency_gate.json")
    carrier = load("docs/core/07_artifacts/archive/carrier_neutral_comparator_contract.json")
    observer = load("docs/core/07_artifacts/archive/carrier_observer_thought_experiment.json")
    photon = load("docs/core/07_artifacts/verification/photon_observer_baseline_verification.json")
    orbit = load("docs/core/07_artifacts/gates/orbit_cosmology_correspondence_gate.json")
    gr = load("docs/core/07_artifacts/gates/uet_gr_research_program_gate.json")
    galaxy = load("docs/topics/0.1_Galaxy_Rotation_Problem/Result/artifacts/galaxy_history_comparison.json")
    cosmic = load("docs/topics/0.26_Cosmic_Dynamic_Frame/Result/artifacts/0_26_cosmic_dynamic_frame_verification.json")
    particle = load("docs/core/07_artifacts/gates/particle_dirac_program_gate.json")

    waves = [
        {
            "wave": 7,
            "name": "O2 finite-density EOS and covariant transport",
            "status": "PASS_CONDITIONAL_WITH_OPEN_TRANSPORT",
            "evidence": [
                "docs/core/07_artifacts/verification/o2_finite_density_eos_verification.json",
                "docs/core/07_artifacts/correspondence/o2_eos_formula_audit.json",
                "docs/core/07_artifacts/verification/covariant_superfluid_transport_verification.json",
            ],
            "local_results": {
                "eos": first_status(eos),
                "formula_audit": first_status(eos_audit),
                "transport": first_status(transport),
                "physical_coefficient_evidence": transport.get("physical_coefficient_evidence"),
                "finite_temperature_two_fluid_completion": transport.get("finite_temperature_two_fluid_completion"),
            },
            "controller": controller(eos_audit) if controller(eos_audit) != "not_declared" else "covariant_superfluid_kubo_transport_and_entropy_matching_missing",
            "claim_boundary": "tree-level natural-unit O2 EOS and conditional ideal covariant constitutive structure; transport coefficient values and SI remain open",
        },
        {
            "wave": 8,
            "name": "Impact/effect/carrier and observer",
            "status": "BLOCKED",
            "evidence": [
                "docs/core/07_artifacts/verification/impact_effect_core_verification.json",
                "docs/core/07_artifacts/gates/impact_effect_dependency_gate.json",
                "docs/core/07_artifacts/archive/carrier_neutral_comparator_contract.json",
                "docs/core/07_artifacts/archive/carrier_observer_thought_experiment.json",
                "docs/core/07_artifacts/verification/photon_observer_baseline_verification.json",
            ],
            "local_results": {
                "impact_core": first_status(impact),
                "impact_dependency": first_status(impact_gate),
                "carrier": first_status(carrier),
                "observer": first_status(observer),
                "photon_baseline": photon.get("standard_comparator_verification", first_status(photon)),
                "photon_baseline_status": first_status(photon),
                "photon_uet_mapping": photon.get("dependency_status", "UNSPECIFIED"),
            },
            "controller": controller(impact_gate) + "; photon=SI detector/observable map and UET source-to-carrier law remain open",
            "claim_boundary": "carrier-neutral and observer thought-experiment contracts only; no photon/neutrino/positron identity for R_gen",
        },
        {
            "wave": 9,
            "name": "Gravity, orbit, cosmology, and effective open subsystem",
            "status": "BLOCKED",
            "evidence": [
                "docs/core/07_artifacts/gates/orbit_cosmology_correspondence_gate.json",
                "docs/core/07_artifacts/gates/uet_gr_research_program_gate.json",
            ],
            "local_results": {
                "orbit_cosmology": first_status(orbit),
                "gr_program": first_status(gr),
            },
            "controller": controller(gr),
            "claim_boundary": "local conditional covariant/closed-limit checks only; no Einstein derivation or global-open-universe claim",
        },
        {
            "wave": 10,
            "name": "Galaxy 0.1 and cosmic dynamic frame 0.26",
            "status": "BLOCKED",
            "evidence": [
                "docs/topics/0.1_Galaxy_Rotation_Problem/Result/artifacts/galaxy_history_comparison.json",
                "docs/topics/0.26_Cosmic_Dynamic_Frame/Result/artifacts/0_26_cosmic_dynamic_frame_verification.json",
            ],
            "local_results": {
                "galaxy": first_status(galaxy),
                "cosmic": first_status(cosmic),
            },
            "controller": (
                f"galaxy={controller(galaxy)}; "
                "cosmic=raw-frame provenance, units, and residual policy remain open"
            ),
            "claim_boundary": "internal/external comparison only; dark-matter replacement and global cosmic law blocked",
        },
        {
            "wave": 11,
            "name": "Particle, Dirac, neutrino, and antimatter program",
            "status": "DEFERRED_BLOCKED",
            "evidence": ["docs/core/07_artifacts/gates/particle_dirac_program_gate.json"],
            "local_results": {
                "required_prerequisites": [
                    "Lorentz-covariant action",
                    "spinor representation",
                    "conserved current",
                    "mass-eigenstate map",
                    "charge/conjugation convention",
                    "CPT and detector-observable gates",
                ],
                "current_status": "not established as a closed UET derivation",
            },
            "controller": particle.get("controlling_blocker", "complete covariant foundation and particle correspondence prerequisites before particle claims"),
            "claim_boundary": "photon, neutrino, positron, antimatter, and Dirac relations remain deferred/not established",
        },
    ]

    return {
        "schema_version": "1.0",
        "artifact": "uet_foundation_extended_wave_closure",
        "audit_status": "PASS_WITH_DECLARED_DOWNSTREAM_BLOCKERS",
        "program_status": "FOUNDATION_BLOCKED_DOWNSTREAM_STATUS_EXPLICIT",
        "waves": waves,
        "checks": {
            "all_wave_statuses_explicit": all(item["status"] for item in waves),
            "no_downstream_pass_promoted_to_physical_claim": True,
            "o2_transport_open_boundary_disclosed": (
                waves[0]["local_results"]["physical_coefficient_evidence"]
                == "BLOCKED_NOT_PROVIDED"
            ),
            "carrier_dependency_blocked": waves[1]["status"] == "BLOCKED",
            "photon_standard_comparator_verified": waves[1]["local_results"]["photon_baseline"] == "PASS",
            "global_open_claim_blocked": waves[2]["status"] == "BLOCKED",
            "galaxy_cosmic_claim_blocked": waves[3]["status"] == "BLOCKED",
            "particle_program_deferred": waves[4]["status"] == "DEFERRED_BLOCKED",
        },
        "claim_boundary": (
            "This artifact closes the status accounting for downstream waves; it "
            "does not close their physics. A local EOS/transport or observer check "
            "cannot override the foundation dependency gate."
        ),
        "next_controller": (
            "complete foundation correspondence and dimensional observable gates, "
            "then revisit downstream waves in dependency order"
        ),
    }


def main() -> int:
    artifact = build()
    output = ROOT / "docs/core/07_artifacts/gates/uet_foundation_extended_wave_closure.json"
    output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())