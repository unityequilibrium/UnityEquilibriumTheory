"""Verify the normalized carrier-neutral impact/effect relation and emit artifacts."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_impact_effect import (
    COUPLED_RECEIVER_MODE,
    CarrierRecord,
    ImpactRecord,
    ReceiverDynamics,
    apply_receiver_effect,
    impact_effect_contract,
    impact_to_effect,
)
from docs.core.core_paths import canonical_artifact_path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIR = ROOT / "docs/core/07_artifacts"


def _fixture() -> tuple[ImpactRecord, CarrierRecord]:
    impact = ImpactRecord(
        source_id="source-A",
        receiver_id="receiver-B",
        interaction_type="emission",
        energy_transfer=0.5,
        mass_transfer=0.0,
        impact_id="impact-1",
    )
    carrier = CarrierRecord(
        carrier_type="declared_signal",
        source_id="source-A",
        receiver_id="receiver-B",
        energy=0.5,
        propagation_speed=1.0,
        rest_mass_status="massless",
        carrier_id="carrier-1",
        payload=np.array([2.0, 4.0]),
    )
    return impact, carrier


def run() -> dict[str, Any]:
    impact, carrier = _fixture()
    checks: dict[str, dict[str, Any]] = {}

    effect = impact_to_effect(impact, carrier, generated_trace=np.array([0.25, 0.5]), mode=COUPLED_RECEIVER_MODE)
    checks["effect_without_mass_transfer"] = {
        "passed": effect.active and impact.mass_transfer == 0.0,
        "metric": "active_effect_with_zero_source_mass_transfer",
    }

    missing = impact_to_effect(impact, None, generated_trace=np.zeros(2), mode=COUPLED_RECEIVER_MODE)
    missing_update = apply_receiver_effect(np.ones(2), missing, ReceiverDynamics(gain=2.0, feedback_enabled=True))
    checks["no_carrier_no_receiver_change"] = {
        "passed": (not missing.active) and np.allclose(missing_update.state, 1.0),
        "metric": "receiver_state_delta=0",
    }

    coupled = apply_receiver_effect(
        np.ones(2), effect, ReceiverDynamics(gain=0.5, feedback_enabled=True)
    )
    checks["explicit_receiver_feedback"] = {
        "passed": coupled.ledger["feedback_applied"] and np.allclose(coupled.state, [2.0, 3.0]),
        "metric": "explicit_linear_receiver_update",
    }

    observer_a = impact_to_effect(impact, carrier, generated_trace=np.array([0.25, 0.5]), observer_gain=1.0)
    observer_b = impact_to_effect(impact, carrier, generated_trace=np.array([0.25, 0.5]), observer_gain=0.25)
    checks["observer_protocol_only_changes_record"] = {
        "passed": np.allclose(observer_a.generated_trace, observer_b.generated_trace)
        and not np.allclose(observer_a.observer_record, observer_b.observer_record),
        "metric": "R_gen_equal_and_R_obs_different",
    }

    checks["trace_feedback_is_disabled"] = {
        "passed": effect.physical_ledger["trace_feedback"] is False
        and coupled.ledger["trace_feedback"] is False,
        "metric": "no_R_gen_to_core_feedback_edge",
    }

    passed = all(item["passed"] for item in checks.values())
    verification = {
        "schema_version": "impact-effect-core-verification-v1",
        "artifact": "impact_effect_core_verification",
        "generated_at": date.today().isoformat(),
        "status": "PASS" if passed else "FAIL",
        "verification_status": "PASS" if passed else "FAIL",
        "dependency_status": "BLOCKED",
        "operator_mode": "carrier_neutral_impact_effect_v1",
        "unit_lane": "normalized_only_v1",
        "checks": checks,
        "contract": impact_effect_contract(),
        "claim_boundary": "internally verified normalized relation only; no carrier identity or physical transition derivation",
        "next_controller": "add carrier-specific conservation, units, detector maps, and falsification tests without fitting",
    }
    gate = {
        "schema_version": "impact-effect-dependency-gate-v1",
        "artifact": "impact_effect_dependency_gate",
        "generated_at": date.today().isoformat(),
        "status": "BLOCKED",
        "local_verification_status": verification["verification_status"],
        "foundation_dependency": "BLOCKED",
        "carrier_specific_derivation": "OPEN",
        "observable_mapping": "OPEN",
        "claim_promotion": "BLOCKED",
        "allowed_status": "CANDIDATE / INTERNAL / SIMULATION_ONLY",
        "controlling_blocker": "foundation correspondence, units, and carrier/detector maps are incomplete",
    }
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    canonical_artifact_path("impact_effect_core_verification.json", "verification").write_text(
        json.dumps(verification, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    canonical_artifact_path("impact_effect_dependency_gate.json", "gates").write_text(
        json.dumps(gate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return verification


if __name__ == "__main__":
    result = run()
    print(f"verification_status={result['verification_status']}")
    print("dependency_status=BLOCKED")
