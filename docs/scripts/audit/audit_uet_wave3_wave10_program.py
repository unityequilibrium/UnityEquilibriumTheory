"""Build the dependency-gated UET Wave 3--10 program artifact.

This audit does not rerun physics models and does not promote any claim.  It
joins the latest stable lane artifacts, records their local evidence status,
and applies the foundation dependency rule: a downstream wave cannot be
reported as PASS while the foundation gate is BLOCKED or FAIL.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs" / "core" / "artifacts" / "uet_wave3_wave10_research_program.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def status_of(payload: dict[str, Any]) -> str:
    for key in ("status", "audit_status", "program_status", "evidence_status"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return "UNSPECIFIED"


def controller_of(payload: dict[str, Any]) -> str:
    for key in ("controlling_blocker", "blocker_label", "next_controller", "controller"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    for block in payload.get("blocking_reasons", []):
        if isinstance(block, str):
            return block
    return "not_declared"


def evidence(path_text: str) -> dict[str, Any]:
    path = ROOT / Path(path_text)
    if not path.exists():
        return {"path": path_text, "exists": False, "status": "MISSING"}
    payload = load(path) if path.suffix.lower() == ".json" else None
    return {
        "path": path_text,
        "exists": True,
        "sha256": sha256(path),
        "status": status_of(payload) if payload is not None else "PRESENT",
        "controller": controller_of(payload) if payload is not None else "not_json",
    }


def wave(
    number: int,
    name: str,
    controller: str,
    inputs: list[str],
    local_status: str,
    claim_ceiling: str,
    foundation_blocked: bool,
) -> dict[str, Any]:
    dependency_blocked = foundation_blocked and number >= 4
    effective_status = "BLOCKED_BY_FOUNDATION" if dependency_blocked else local_status
    return {
        "wave": number,
        "name": name,
        "local_evidence_status": local_status,
        "effective_status": effective_status,
        "dependency_blocked": dependency_blocked,
        "controlling_blocker": controller,
        "claim_ceiling": claim_ceiling,
        "inputs": [evidence(item) for item in inputs],
    }


def build() -> dict[str, Any]:
    foundation_path = ROOT / "docs/core/07_artifacts/gates/uet_foundation_dependency_gate.json"
    wording_path = ROOT / "docs/core/07_artifacts/verification/impact_effect_legacy_wording_audit.json"
    foundation = load(foundation_path)
    wording = load(wording_path)
    foundation_status = status_of(foundation)
    foundation_blocked = foundation_status in {"BLOCKED", "FAIL", "WARN"}

    causal = load(ROOT / "docs/core/07_artifacts/archive/matter_space_causal_lane_comparison.json")
    causal_selection = load(ROOT / "docs/core/07_artifacts/archive/matter_space_causal_lane_selection.json")
    causal_status = status_of(causal_selection)
    thermal = load(ROOT / "docs/core/07_artifacts/topic13/thermal_observable_bridge_verification.json")
    observable = load(ROOT / "docs/core/07_artifacts/verification/matter_space_observable_verification.json")
    persistence_dynamic = load(ROOT / "docs/core/07_artifacts/provenance/resource_selection_dynamic_game_verification.json")
    persistence_thermal = load(ROOT / "docs/core/07_artifacts/provenance/resource_selection_thermal_bridge_verification.json")
    extended_closure = load(ROOT / "docs/core/07_artifacts/gates/uet_foundation_extended_wave_closure.json")
    eos = load(ROOT / "docs/core/07_artifacts/verification/o2_finite_density_eos_verification.json")
    transport = load(ROOT / "docs/core/07_artifacts/verification/covariant_superfluid_transport_verification.json")
    gr = load(ROOT / "docs/core/07_artifacts/gates/uet_gr_research_program_gate.json")
    carrier = load(ROOT / "docs/core/07_artifacts/archive/carrier_neutral_comparator_contract.json")
    photon = load(ROOT / "docs/core/07_artifacts/verification/photon_observer_baseline_verification.json")
    pilot_sync = load(ROOT / "docs/core/07_artifacts/archive/matter_space_topic_pilot_sync.json")
    phase = load(ROOT / "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_matter_space_coupled_diagnostic.json")
    thermal_pilot = load(ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_control.json")
    phase_rerun = load(ROOT / "docs/topics/0.11_Phase_Transitions/Result/artifacts/matter_space_0_11_characteristic_lane_rerun.json")
    thermal_rerun = load(ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_0_13_characteristic_thermal_lane_rerun.json")
    galaxy = load(ROOT / "docs/topics/0.1_Galaxy_Rotation_Problem/Result/artifacts/galaxy_history_comparison.json")
    cosmic = load(ROOT / "docs/topics/0.26_Cosmic_Dynamic_Frame/Result/artifacts/0_26_cosmic_dynamic_frame_verification.json")

    waves = [
        wave(
            0,
            "Foundation inventory and metadata repair",
            controller_of(foundation),
            ["docs/core/07_artifacts/gates/uet_foundation_dependency_gate.json", "docs/core/07_artifacts/gates/uet_foundation_equation_inventory.json"],
            foundation_status,
            "inventory and correspondence repair only",
            foundation_blocked,
        ),
        wave(
            1,
            "Ontology and standard-physics correspondence",
            wording.get("next_controller", "active prose legacy wording review") + "; complete F2 lane matrix",
            ["docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json", "docs/core/07_artifacts/correspondence/matter_space_ontology_contract.json", "docs/core/07_artifacts/verification/impact_effect_legacy_wording_audit.json", "docs/core/07_artifacts/provenance/uet_topic_formula_correspondence_manifest.json"],
            foundation.get("gates", {}).get("F2_physical_correspondence", {}).get("status", "BLOCKED"),
            "lane-specific correspondence; no universal identity",
            foundation_blocked,
        ),
        wave(
            2,
            "Units and derivation registry",
            "complete dimensional contract and derivation-origin coverage",
            ["docs/core/07_artifacts/correspondence/matter_space_formula_audit.json", "docs/core/07_artifacts/correspondence/o2_eos_formula_audit.json"],
            foundation.get("gates", {}).get("F3_units", {}).get("status", "BLOCKED"),
            "normalized/natural lanes only until dimensional maps close",
            foundation_blocked,
        ),
        wave(
            3,
            "Mathematical closure and causal two-arm decision",
            causal_selection.get("next_controller", controller_of(causal_selection)) + "; normalized observable operator verified; SI mapping remains open",
            ["docs/core/07_artifacts/archive/matter_space_causal_lane_selection.json", "docs/core/07_artifacts/verification/matter_space_characteristic_cone_verification.json", "docs/core/07_artifacts/archive/matter_space_finite_cone_shared_ledger_integration.json", "docs/core/07_artifacts/archive/matter_space_causal_lane_comparison.json", "docs/core/07_artifacts/verification/matter_space_causal_reference_verification.json", "docs/core/07_artifacts/gates/matter_space_dependency_gate.json", "docs/core/07_artifacts/verification/matter_space_observable_verification.json"],
            causal_status,
            "selected characteristic finite-cone candidate plus conserved-C comparator; no physical promotion",
            foundation_blocked,
        ),
        wave(
            4,
            "Observable mapping and synthetic control",
            "normalized_observable_operator_passes; dimensional_observable_operator_and_uncertainty_missing",
            ["docs/core/07_artifacts/topic13/thermal_observable_bridge_verification.json", "docs/core/07_artifacts/provenance/resource_selection_thermal_bridge_verification.json", "docs/core/07_artifacts/gates/matter_space_research_program_gate.json", "docs/core/07_artifacts/verification/matter_space_observable_verification.json"],
            "PASS_WITH_OPEN_SI_MAPPING" if status_of(observable).startswith("PASS") else status_of(thermal),
            "declared measurement operators and simulation-only controls",
            foundation_blocked,
        ),
        wave(
            5,
            "Topic 0.11 matter-space phase pilot",
            pilot_sync.get("topic_0_11", {}).get("controller", phase.get("controlling_blocker", controller_of(phase))),
            ["docs/core/07_artifacts/archive/matter_space_phase_pilot.json", "docs/core/07_artifacts/archive/matter_space_topic_pilot_sync.json", "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_matter_space_phase_coupling_diagnostic.json", "docs/topics/0.11_Phase_Transitions/Result/artifacts/matter_space_0_11_characteristic_lane_rerun.json", "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_conserved_order_spectral_finite_size_replication.json", "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_noether_phase_field_dependency_gate.json"],
            status_of(phase),
            "internal normalized diagnostic; no universality or mass-generation claim",
            foundation_blocked,
        ),
        wave(
            6,
            "Topic 0.13 thermodynamic and thermal pilot",
            thermal_pilot.get("controlling_blocker", controller_of(thermal_pilot)),
            ["docs/core/07_artifacts/archive/matter_space_topic_pilot_sync.json", "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_control.json", "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_0_13_characteristic_thermal_lane_rerun.json", "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json", "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_observable_map_readiness.json"],
            status_of(thermal_pilot),
            "simulation-only Fourier/Cattaneo/trace comparator; external validation blocked",
            foundation_blocked,
        ),
        wave(
            7,
            "O(2) finite-density EOS and covariant transport",
            gr.get("controlling_blocker", controller_of(gr)),
            ["docs/core/07_artifacts/verification/o2_finite_density_eos_verification.json", "docs/core/07_artifacts/verification/covariant_superfluid_transport_verification.json", "docs/core/07_artifacts/gates/uet_gr_research_program_gate.json"],
            "PASS_INTERNAL_EOS_AND_IDEAL_TRANSPORT_WITH_PROGRAM_BLOCKER" if status_of(eos) == "PASS" and status_of(transport) == "PASS" else "BLOCKED",
            "tree-level finite-density O(2) EOS and ideal covariant constitutive structure",
            foundation_blocked,
        ),
        wave(
            8,
            "Impact/effect/carrier and observer program",
            carrier.get("next_controller", controller_of(carrier)) + "; photon=SI detector/observable map and UET source-to-carrier law remain open",
            ["docs/core/07_artifacts/verification/impact_effect_core_verification.json", "docs/core/07_artifacts/gates/impact_effect_dependency_gate.json", "docs/core/07_artifacts/archive/carrier_neutral_comparator_contract.json", "docs/core/07_artifacts/archive/carrier_observer_thought_experiment.json", "docs/core/07_artifacts/verification/photon_observer_baseline_verification.json"],
            "BLOCKED_WITH_NORMALIZED_PHOTON_BASELINE" if photon.get("standard_comparator_verification") == "PASS" else status_of(carrier),
            "carrier-neutral comparator contract; no photon/neutrino/positron identity for R_gen",
            foundation_blocked,
        ),
        wave(
            9,
            "Standard gravity, orbit, and open-system correspondence",
            gr.get("controlling_blocker", controller_of(gr)),
            ["docs/core/07_artifacts/gates/orbit_cosmology_correspondence_gate.json", "docs/core/07_artifacts/verification/gr_closed_limit_verification.json", "docs/core/07_artifacts/gates/gr_correspondence_claim_gate.json", "docs/core/07_artifacts/gates/uet_gr_research_program_gate.json", "docs/topics/0.19_Gravity_GR/Result/artifacts/0_19_core_gr_program_dependency_gate.json"],
            status_of(gr),
            "local covariant/closed-limit checks only; no GR derivation or global-open claim",
            foundation_blocked,
        ),
        wave(
            10,
            "Galaxy 0.1 and cosmic dynamic frame 0.26 comparisons",
            f"galaxy={controller_of(galaxy)}; cosmic=raw_frame_metadata_and_numeric_residuals_open",
            ["docs/topics/0.1_Galaxy_Rotation_Problem/Result/artifacts/galaxy_history_comparison.json", "docs/topics/0.26_Cosmic_Dynamic_Frame/Result/artifacts/0_26_cosmic_dynamic_frame_verification.json"],
            "BLOCKED" if status_of(galaxy) == "BLOCKED" else status_of(cosmic),
            "internal/external comparison only; dark-matter replacement and global cosmic law blocked",
            foundation_blocked,
        ),
    ]

    blocked_waves = [entry["wave"] for entry in waves if entry["effective_status"].startswith("BLOCKED") or entry["effective_status"] in {"BLOCKED_BY_FOUNDATION", "FAIL"}]
    return {
        "schema_version": "1.0",
        "artifact": "uet_wave3_wave10_research_program",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "program_scope": "UET Foundation-First Research Program Waves 0-10",
        "workflow": ["inventory", "ontology", "standard_physics_correspondence", "units", "derivation", "formal_verification", "numerical_verification", "observable_mapping", "real_data_comparison", "claim"],
        "foundation_gate": {
            "path": rel(foundation_path),
            "sha256": sha256(foundation_path),
            "status": foundation_status,
            "controller": controller_of(foundation),
        },
        "status": "BLOCKED" if blocked_waves else "PASS",
        "controlling_blocker": "foundation_dependency_gate_and_wave3_causal_compact_support",
        "waves": waves,
        "causal_decision": {
            "conserved_C": "parabolic/conserved phase comparator; no changing-C finite-cone claim",
            "finite_cone_C": "selected non-conserved telegraph/characteristic candidate passes its normalized compact-support contract and public adapter smoke gate",
            "default_full_candidate": "blocked; original nonlinear Heun lane retains pre-arrival leakage above threshold",
            "conserved_Cattaneo": "negative control; high-k speed unbounded without UV/nonlocal regularization",
            "reference_lane": "strict-CFL compact-support control does not promote the full coupled candidate",
        },
        "persistence_program": {
            "dynamic_selection": {
                "status": status_of(persistence_dynamic),
                "controller": controller_of(persistence_dynamic),
                "artifact": "docs/core/07_artifacts/provenance/resource_selection_dynamic_game_verification.json",
            },
            "thermal_bridge": {
                "status": status_of(persistence_thermal),
                "controller": controller_of(persistence_thermal),
                "artifact": "docs/core/07_artifacts/provenance/resource_selection_thermal_bridge_verification.json",
            },
            "claim_boundary": "normalized internal diagnostics only; physical work/heat/entropy mapping and external validation remain open",
        },
        "extended_wave_closure": {
            "status": status_of(extended_closure),
            "controller": controller_of(extended_closure),
            "artifact": "docs/core/07_artifacts/gates/uet_foundation_extended_wave_closure.json",
        },
        "claim_boundary": {
            "allowed": ["candidate collective-behaviour coordinate", "candidate normalized effective model", "internal diagnostic", "tree-level finite-density O(2) EOS", "covariant ideal-superfluid constitutive structure", "simulation/comparator contract"],
            "blocked": ["C is universal mass", "R_gen is an independent substance", "Phi is metric/particle/ether", "photon or neutrino or positron equals R_gen", "UET derives GR", "global universe is proved open", "dark-matter replacement", "simulation equals empirical proof"],
        },
    }


def main() -> int:
    artifact = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"artifact={rel(OUT)}")
    print(f"status={artifact['status']}")
    print(f"blocked_waves={sum(item['effective_status'] in {'BLOCKED', 'BLOCKED_BY_FOUNDATION', 'FAIL'} for item in artifact['waves'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
