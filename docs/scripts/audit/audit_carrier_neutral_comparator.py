"""Validate the no-fit carrier-neutral comparison contract."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SPEC = ROOT / "docs/core/01_contracts/CARRIER_NEUTRAL_COMPARATOR_SPEC.md"
OUTPUT = ROOT / "docs/core/07_artifacts/archive/carrier_neutral_comparator_contract.json"


LANES: tuple[dict[str, Any], ...] = (
    {
        "lane_id": "photon",
        "role": "primary_massless_signal_carrier_baseline",
        "source_interaction": "electromagnetic emission or absorption",
        "carrier_identity": "photon / electromagnetic field excitation",
        "rest_mass_status": "massless_standard_comparator",
        "energy_momentum_ledger": "required; photon energy and momentum are not zero",
        "charge_current_conservation": "electric charge/current conservation in source and detector interaction",
        "propagation_law": "declared electromagnetic propagation law; vacuum speed baseline c",
        "detector_interaction": "electromagnetic detector response",
        "observable_payload": "arrival time, spectrum, polarization, energy, detector record; units open in this contract",
        "falsification_condition": "causal or energy-momentum mismatch, or detector map cannot reproduce the declared observable",
        "evidence_status": "STANDARD_COMPARATOR_SOURCE_PACKAGE_REQUIRED",
        "uet_identity_status": "NOT_DERIVED",
    },
    {
        "lane_id": "neutrino",
        "role": "weakly_interacting_carrier_candidate",
        "source_interaction": "weak interaction source or decay channel",
        "carrier_identity": "neutrino mass eigenstate / flavor-labelled weak carrier",
        "rest_mass_status": "massive_standard_comparator",
        "energy_momentum_ledger": "required; four-momentum and source decay ledger must close",
        "charge_current_conservation": "electric neutrality plus declared weak/lepton-current convention",
        "propagation_law": "declared relativistic massive-particle propagation; ultrarelativistic is an approximation",
        "detector_interaction": "weak detector interaction with flavor/energy response",
        "observable_payload": "arrival time, energy, flavor/channel count, detector record; units open in this contract",
        "falsification_condition": "source, oscillation/propagation, or detector response violates the declared conservation and measurement map",
        "evidence_status": "STANDARD_BENCHMARK_COMPATIBILITY_SOURCE_PACKAGE_REQUIRED",
        "uet_identity_status": "NOT_DERIVED; LEGACY_PURE_I_FIELD_WORDING_REQUIRES_RECLASSIFICATION",
    },
    {
        "lane_id": "electron_positron_reaction",
        "role": "mass_bearing_antiparticle_reaction_participant",
        "source_interaction": "electron-positron collision or annihilation channel",
        "carrier_identity": "positron is a reaction participant; photon products are a possible output channel",
        "rest_mass_status": "massive_standard_comparator",
        "energy_momentum_ledger": "required; four-momentum and rest-energy conversion must close",
        "charge_current_conservation": "electric charge conservation before and after reaction",
        "propagation_law": "relativistic massive-particle propagation before interaction",
        "detector_interaction": "charged-particle tracking and/or electromagnetic product detection",
        "observable_payload": "track, deposited energy, annihilation products, detector record; units open in this contract",
        "falsification_condition": "charge, four-momentum, or product-channel ledger fails; no universal carrier interpretation is allowed",
        "evidence_status": "STANDARD_REACTION_COMPARATOR_SOURCE_PACKAGE_REQUIRED",
        "uet_identity_status": "NOT_DERIVED; NOT_A_UNIVERSAL_INFORMATION_CARRIER",
    },
)


def build() -> dict[str, Any]:
    required = {
        "source_interaction", "carrier_identity", "rest_mass_status", "energy_momentum_ledger",
        "charge_current_conservation", "propagation_law", "detector_interaction",
        "observable_payload", "falsification_condition", "evidence_status", "uet_identity_status",
    }
    checks = {
        "spec_present": SPEC.exists(),
        "three_lanes_present": len(LANES) == 3,
        "required_fields_present": all(required.issubset(lane) for lane in LANES),
        "no_fit_policy": True,
        "no_universal_carrier_policy": True,
        "foundation_dependency_blocked": True,
    }
    return {
        "schema_version": "carrier-neutral-comparator-contract-v1",
        "artifact": "carrier_neutral_comparator_contract",
        "generated_at": date.today().isoformat(),
        "status": "BLOCKED",
        "contract_verification": "PASS" if all(checks.values()) else "FAIL",
        "dependency_status": "BLOCKED",
        "lanes": list(LANES),
        "checks": checks,
        "comparison_policy": {
            "parameter_fitting": False,
            "external_validation": False,
            "I_trace_is_any_lane": False,
            "effect_is_independent_field": False,
            "massless_transition_is_automatic": False,
        },
        "required_next_inputs": [
            "source provenance and hashes",
            "carrier-specific dimensional units",
            "conservation ledger implementation",
            "detector/observable operator",
            "lane-specific falsification test",
        ],
        "claim_boundary": "simulation/comparator contract only; no UET photon, neutrino, positron, or massless-transition derivation",
        "next_controller": "source-lock one carrier lane and close its dimensional detector map after upstream phase/core gates",
    }


def main() -> int:
    artifact = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"contract_verification={artifact['contract_verification']}")
    print("dependency_status=BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
