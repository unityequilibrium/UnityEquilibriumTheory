"""Generate the Wave 7 interpretation-invariance verification package."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import canonical_artifact_path, canonical_existing_path  # noqa: E402
QUANTUM_INTERPRETATIONS_SOURCE = canonical_existing_path(ROOT / ("docs/core/" + "uet_quantum_interpretations.py")).relative_to(ROOT).as_posix()

from docs.core.uet_quantum_interpretations import (
    compare_empirical_predictions, interpretation_contract,
)
from docs.core.uet_quantum_measurement import DensityOperator, POVMRecord

ARTIFACTS = ROOT / "docs/core/07_artifacts"


def build_artifacts() -> tuple[dict, dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    plus = np.array([1.0, 1.0]) / np.sqrt(2.0)
    state = DensityOperator(np.outer(plus, plus), "plus")
    state_before = state.matrix.copy()
    povm = POVMRecord(("0", "1"), (np.diag([1.0, 0.0]), np.diag([0.0, 1.0])), "z")
    comparisons = [
        compare_empirical_predictions(state, povm, f"agent-{index}", "S", f"R-{index}")
        for index in range(5)
    ]
    metrics = {
        "maximum_prediction_residual": max(item.maximum_probability_residual for item in comparisons),
        "source_state_change_max_abs": float(np.max(np.abs(state.matrix - state_before))),
        "interpretation_count": 3,
    }
    thresholds = {"prediction_invariance": 1e-12, "state_invariance": 1e-12}
    checks = {
        "prediction_invariance": metrics["maximum_prediction_residual"] <= thresholds["prediction_invariance"],
        "physical_state_invariance": metrics["source_state_change_max_abs"] <= thresholds["state_invariance"],
        "no_physical_dynamics": all(not item.physical_dynamics_changed for item in comparisons),
        "no_trace_change": all(not item.generated_trace_changed for item in comparisons),
        "contract_has_no_new_dynamics": interpretation_contract()["new_dynamics"] is False,
    }
    passed = all(checks.values())
    verification = {
        "schema_version": "1.0", "artifact": "quantum_interpretation_invariance_verification",
        "generated_at": now, "audit_status": "PASS" if passed else "FAIL",
        "research_status": "INTERPRETATION_COMPARISON_ONLY",
        "metrics": metrics, "thresholds": thresholds, "checks": checks,
        "contract": interpretation_contract(),
        "claim_boundary": "QBism and RQM metadata views share operational Born predictions and add no UET dynamics",
    }
    gate = {
        "schema_version": "1.0", "artifact": "uet_main_theory_wave7_gate",
        "generated_at": now, "audit_status": "PASS" if passed else "FAIL",
        "interpretation_status": "PASS_PREDICTION_INVARIANT_ADAPTERS" if passed else "BLOCKED",
        "upstream_gate": "uet_main_theory_wave6_gate.json", "checks": checks,
        "controlling_blocker": "dimensional_observable_mapping_and_external_holdout_incomplete" if passed else "interpretation_prediction_invariance_failure",
        "claim_promotion": False,
        "next_controller": "close one dimensional physical observable lane with independent calibration and holdout",
    }
    addendum = {
        "schema_version": "1.0", "artifact": "uet_equation_correspondence_registry_quantum_interpretations_addendum",
        "extends": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json", "status": "CANDIDATE_ENTRY_PENDING_MERGE",
        "equation_entries": [{
            "equation_id": "uet.main_theory.quantum_interpretation_adapters", "version": "interpretation-adapters-v1",
            "classification": "observable_definition", "relation_or_code_path": QUANTUM_INTERPRETATIONS_SOURCE,
            "variables": {"rho_A": "agent-indexed probability assignment", "relation_SR": "system-reference metadata", "p_o": "shared operational Born probabilities"},
            "mathematical_role": "metadata views over one operational probability contract",
            "standard_physics_counterpart": "QBism, relational QM, and operational QM comparison",
            "observable_mapping": {"status": "FORMAL", "reason": "all views reference the same instrument outcomes"},
            "unit_lane": "dimensionless_probability", "parameter_dimensions": "none",
            "source_or_origin": "UET Main-Theory Wave 7 comparison layer",
            "assumptions": ["same preparation and instrument", "interpretations add no dynamics"],
            "symmetry_and_conservation": "empirical prediction invariance",
            "limiting_cases": ["changing agent or reference labels leaves probabilities unchanged"],
            "implementation_paths": [QUANTUM_INTERPRETATIONS_SOURCE],
            "verifier_paths": ["docs/scripts/audit/audit_uet_quantum_interpretations.py", "docs/core/07_artifacts/verification/quantum_interpretation_invariance_verification.json", "docs/core/test/test_uet_quantum_interpretations.py"],
            "evidence_class": "INTERNAL_FORMAL", "proof_status": "finite-dimensional invariance tests pass",
            "downstream_dependencies": ["uet.main_theory.operational_quantum_measurement", "uet.main_theory.detector_observables"],
            "claim_boundary": "interpretation comparison only; no new empirical prediction",
            "failure_mode": "metadata changes physical state or probabilities without declared dynamics",
            "next_hardening_step": "connect detector records to a dimensional physical observable lane",
        }],
    }
    return verification, gate, addendum


def main() -> int:
    names = ("quantum_interpretation_invariance_verification.json", "uet_main_theory_wave7_gate.json", "uet_equation_correspondence_registry_quantum_interpretations_addendum.json")
    outputs = dict(zip(names, build_artifacts()))
    for name, payload in outputs.items():
        canonical_artifact_path(name).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    gate = outputs["uet_main_theory_wave7_gate.json"]
    print(f"audit_status={gate['audit_status']}")
    print(f"interpretation_status={gate['interpretation_status']}")
    print(f"controlling_blocker={gate['controlling_blocker']}")
    return 0 if gate["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
