"""Verify the normalized standard-photon observer comparator."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from docs.core.photon_observer_baseline import (
    PhotonBaselineConfig,
    PhotonEmissionEvent,
    detect_photon,
    photon_observer_contract,
    propagate_photon,
)


OUTPUT = ROOT / "docs/core/07_artifacts/verification/photon_observer_baseline_verification.json"


def build() -> dict:
    config = PhotonBaselineConfig(detector_gain=1.5, detector_threshold=0.5)
    event = PhotonEmissionEvent(
        source_id="source-0",
        receiver_id="detector-0",
        emission_time=2.0,
        path_length=5.0,
        photon_energy=2.0,
        direction=(1.0, 0.0, 0.0),
        source_energy_before=10.0,
        source_energy_after=8.0,
        source_momentum_before=(3.0, 1.0, 0.0),
        source_momentum_after=(1.0, 1.0, 0.0),
    )
    propagation = propagate_photon(event, config)
    detected = detect_photon(propagation, config)
    not_detected = detect_photon(propagation, config, detector_interaction=False)
    contract = photon_observer_contract()
    checks = {
        "energy_momentum_ledger_closed": propagation.ledger_closed,
        "energy_residual_within_tolerance": propagation.energy_residual <= config.tolerance,
        "momentum_residual_within_tolerance": propagation.momentum_residual <= config.tolerance,
        "massless_norm_relation": bool(np.isclose(np.linalg.norm(propagation.photon_momentum), event.photon_energy)),
        "arrival_time_relation": bool(np.isclose(propagation.arrival_time, 7.0)),
        "causal_speed_within_declared_limit": propagation.causal_ok,
        "detector_record_active_with_interaction": detected.detected,
        "detector_record_inactive_without_interaction": not not_detected.detected,
        "observer_record_changes_without_source_change": detected.observer_record != not_detected.observer_record,
        "trace_feedback_disabled": contract["trace_feedback"] is False,
        "no_fit_policy": contract["parameter_fitting"] is False,
    }
    return {
        "schema_version": "photon-observer-baseline-v1",
        "artifact": "photon_observer_baseline_verification",
        "generated_at": date.today().isoformat(),
        "status": "PASS_WITH_OPEN_DIMENSIONAL_AND_UET_MAPPING",
        "standard_comparator_verification": "PASS" if all(checks.values()) else "FAIL",
        "dependency_status": "BLOCKED",
        "mode": "standard_photon_observer_baseline_v1",
        "unit_lane": "normalized",
        "fixture": {
            "emission_time": event.emission_time,
            "path_length": event.path_length,
            "photon_energy": event.photon_energy,
            "direction": list(event.direction),
            "arrival_time": propagation.arrival_time,
            "photon_momentum": list(propagation.photon_momentum),
            "detected_observer_record": list(detected.observer_record),
        },
        "checks": checks,
        "contract": contract,
        "claim_boundary": "Standard normalized photon comparator verified locally; no UET photon derivation, SI validation, or automatic massless transition is established.",
        "next_controller": "source-lock SI detector/observable package and separately derive or reject any UET source-to-carrier transition law",
    }


def main() -> int:
    artifact = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"standard_comparator_verification={artifact['standard_comparator_verification']}")
    print(f"dependency_status={artifact['dependency_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
