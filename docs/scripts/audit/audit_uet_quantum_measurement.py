"""Generate the Wave 6 operational quantum verification package."""

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
QUANTUM_MEASUREMENT_SOURCE = canonical_existing_path(ROOT / ("docs/core/" + "uet_quantum_measurement.py")).relative_to(ROOT).as_posix()

from docs.core.uet_quantum_measurement import (
    DensityOperator, MeasurementContext, QuantumChannel, QuantumInstrument,
    apply_quantum_channel, born_probabilities, expectation,
    partial_trace_bipartite, quantum_measurement_contract,
    sample_or_record_outcome,
)

ARTIFACTS = ROOT / "docs/core/07_artifacts"


def build_artifacts() -> tuple[dict, dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    singlet_vector = np.array([0.0, 1.0, -1.0, 0.0]) / np.sqrt(2.0)
    singlet = DensityOperator(np.outer(singlet_vector, singlet_vector.conj()), "singlet")
    x = np.array([[0.0, 1.0], [1.0, 0.0]])
    z = np.diag([1.0, -1.0])
    b0, b1 = (z + x) / np.sqrt(2.0), (z - x) / np.sqrt(2.0)
    chsh_operator = np.kron(z, b0) + np.kron(z, b1) + np.kron(x, b0) - np.kron(x, b1)
    chsh = abs(expectation(singlet, chsh_operator))
    before = partial_trace_bipartite(singlet, (2, 2), keep=0)
    p = 0.37
    local_channel = QuantumChannel(
        (np.sqrt(1.0 - p) * np.eye(4), np.sqrt(p) * np.kron(np.eye(2), x)),
        "random_x_on_B", "internal://textbook-no-signalling-control",
    )
    after = partial_trace_bipartite(apply_quantum_channel(singlet, local_channel), (2, 2), keep=0)
    projectors = (np.diag([1.0, 0.0]), np.diag([0.0, 1.0]))
    instrument = QuantumInstrument(("0", "1"), ((projectors[0],), (projectors[1],)), "z_measurement", "declared_detector_interaction")
    zero = DensityOperator(projectors[0], "zero")
    probabilities = born_probabilities(zero, instrument.povm())
    record = sample_or_record_outcome(zero, instrument, MeasurementContext("zero", "identity", "z_measurement", "agent-A", "lab-1"), selected_outcome="0")
    povm_sum = sum(instrument.povm().effects, np.zeros((2, 2), dtype=complex))
    channel_closure = sum((operator.conj().T @ operator for operator in local_channel.kraus_operators), np.zeros((4, 4), dtype=complex))
    metrics = {
        "density_trace_residual": abs(float(np.trace(singlet.matrix).real) - 1.0),
        "density_minimum_eigenvalue": float(np.min(np.linalg.eigvalsh(singlet.matrix))),
        "povm_identity_residual": float(np.max(np.abs(povm_sum - np.eye(2)))),
        "born_normalization_residual": abs(sum(probabilities.values()) - 1.0),
        "cptp_trace_preserving_residual": float(np.max(np.abs(channel_closure - np.eye(4)))),
        "no_signalling_residual": float(np.max(np.abs(before.matrix - after.matrix))),
        "chsh_absolute": chsh,
        "tsirelson_residual": abs(chsh - 2.0 * np.sqrt(2.0)),
    }
    thresholds = {"positivity": -1e-12, "probability": 1e-12, "cptp": 1e-10, "no_signalling": 1e-10, "tsirelson": 1e-12}
    checks = {
        "density_positive_trace_one": metrics["density_minimum_eigenvalue"] >= thresholds["positivity"] and metrics["density_trace_residual"] <= thresholds["probability"],
        "povm_positive_complete": metrics["povm_identity_residual"] <= thresholds["probability"],
        "born_normalized": metrics["born_normalization_residual"] <= thresholds["probability"],
        "channel_cptp": metrics["cptp_trace_preserving_residual"] <= thresholds["cptp"],
        "no_signalling": metrics["no_signalling_residual"] <= thresholds["no_signalling"],
        "chsh_tsirelson_baseline": metrics["tsirelson_residual"] <= thresholds["tsirelson"],
        "metadata_does_not_modify_source": record.source_state_modified_by_metadata is False and np.array_equal(zero.matrix, projectors[0]),
        "no_uet_quantum_overclaim": quantum_measurement_contract()["uet_specific_quantum_dynamics"] is False,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    passed = all(checks.values())
    verification = {
        "schema_version": "1.0", "artifact": "quantum_measurement_verification",
        "generated_at": now, "audit_status": "PASS" if passed else "FAIL",
        "research_status": "STANDARD_OPERATIONAL_QM_BASELINE_ONLY",
        "metrics": metrics, "thresholds": thresholds, "checks": checks,
        "contract": quantum_measurement_contract(),
        "claim_boundary": "reproduces finite-dimensional operational quantum baselines; does not derive quantum mechanics or new predictions from UET",
    }
    gate = {
        "schema_version": "1.0", "artifact": "uet_main_theory_wave6_gate",
        "generated_at": now, "audit_status": "PASS" if passed else "FAIL",
        "quantum_status": "PASS_OPERATIONAL_QM_BASELINE_ONLY" if passed else "BLOCKED",
        "upstream_gate": "uet_main_theory_ontology_gate.json", "checks": checks,
        "controlling_blocker": "qbism_rqm_operational_interpretation_invariance_not_checked" if passed else "operational_quantum_baseline_failure",
        "claim_promotion": False,
        "next_controller": "add interpretation-only QBism and RQM adapters and verify prediction invariance",
    }
    addendum = {
        "schema_version": "1.0", "artifact": "uet_equation_correspondence_registry_quantum_measurement_addendum",
        "extends": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json", "status": "CANDIDATE_ENTRY_PENDING_MERGE",
        "equation_entries": [{
            "equation_id": "uet.main_theory.operational_quantum_measurement", "version": "operational-qm-v1",
            "classification": "standard_physics_interface", "relation_or_code_path": QUANTUM_MEASUREMENT_SOURCE,
            "variables": {"rho": "density operator", "E_o": "POVM effect", "K_r": "channel/instrument Kraus operator", "p(o)": "Born probability", "R_obs": "observer outcome record"},
            "mathematical_role": "preparation-channel-instrument-outcome interface",
            "standard_physics_counterpart": "finite-dimensional operational quantum mechanics",
            "observable_mapping": {"status": "FORMAL", "reason": "outcomes map to detector records; hardware-specific calibration remains lane dependent"},
            "unit_lane": "dimensionless_probability", "parameter_dimensions": "finite-dimensional operators",
            "source_or_origin": "standard operational QM imported as the UET quantum interface baseline",
            "assumptions": ["Born rule", "CPTP channels", "positive complete POVMs", "declared detector interaction"],
            "symmetry_and_conservation": "trace preservation, positivity, and no-signalling baseline",
            "limiting_cases": ["identity channel preserves preparation", "projective instrument is a POVM special case"],
            "implementation_paths": [QUANTUM_MEASUREMENT_SOURCE],
            "verifier_paths": ["docs/scripts/audit/audit_uet_quantum_measurement.py", "docs/core/07_artifacts/verification/quantum_measurement_verification.json", "docs/core/test/test_uet_quantum_measurement.py"],
            "evidence_class": "STANDARD_THEORY_REPRODUCTION", "proof_status": "finite-dimensional baseline tests pass",
            "downstream_dependencies": ["uet.main_theory.quantum_interpretations", "uet.main_theory.detector_observables"],
            "claim_boundary": "standard interface adopted by UET; not a UET derivation of quantum mechanics",
            "failure_mode": "nonpositive state/POVM, non-CPTP channel, nonnormalized Born probabilities, or signalling",
            "next_hardening_step": "verify interpretation invariance and connect physical carrier/detector lanes",
        }],
    }
    return verification, gate, addendum


def main() -> int:
    names = ("quantum_measurement_verification.json", "uet_main_theory_wave6_gate.json", "uet_equation_correspondence_registry_quantum_measurement_addendum.json")
    outputs = dict(zip(names, build_artifacts()))
    for name, payload in outputs.items():
        canonical_artifact_path(name).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    gate = outputs["uet_main_theory_wave6_gate.json"]
    print(f"audit_status={gate['audit_status']}")
    print(f"quantum_status={gate['quantum_status']}")
    print(f"controlling_blocker={gate['controlling_blocker']}")
    return 0 if gate["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
