"""Generate the main-theory axiom registry and ontology gate."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import (  # noqa: E402
    CANONICAL_ARTIFACT_ROOT,
    canonical_artifact_path,
    canonical_existing_path,
)

ARTIFACTS = CANONICAL_ARTIFACT_ROOT
SPEC = canonical_existing_path(ROOT / "docs/core/01_contracts/UET_MAIN_THEORY_AXIOMS_SPEC.md")

POSTULATES = (
    (
        "UET-P0",
        "declared_physical_state",
        "state-space modeling and field representations",
        "declared state does not determine fixed-input predictions",
        "coordinates are not automatically matter, energy, information, or observables",
    ),
    (
        "UET-P1",
        "lane_specific_collective_coordinate",
        "order parameters, hydrodynamic densities, and Noether densities",
        "no stable refinement-consistent lane map exists",
        "C is not universal mass, energy, force, probability, or charge",
    ),
    (
        "UET-P2",
        "conservative_generator",
        "Lagrangian, Hamiltonian, and variational field theory",
        "declared equations or currents are not derivatives of the same generator",
        "separate ansatz equations are not one derived conservative theory",
    ),
    (
        "UET-P3",
        "open_system_reduction",
        "Schwinger-Keldysh/KMS, GKSL, Mori-Zwanzig, nonequilibrium thermodynamics",
        "positivity, entropy, fluctuation-dissipation, or exchange balance fails",
        "normalized damping is not automatically microscopic dissipation",
    ),
    (
        "UET-P4",
        "causal_physical_influence",
        "relativistic source-field-detector propagation",
        "influence precedes its declared cone or lacks a physical ledger",
        "carrier identity is not inferred from the word information",
    ),
    (
        "UET-P5",
        "detector_generated_record",
        "operational measurement and detector response",
        "observer protocol alone changes source dynamics",
        "records are not an independent substance",
    ),
    (
        "UET-P6",
        "operational_quantum_probability",
        "density operators, CPTP channels, POVMs, and the Born rule",
        "positivity, normalization, no-signalling, or benchmark gates fail",
        "QBism or RQM does not alter propagation equations by interpretation alone",
    ),
    (
        "UET-P7",
        "derived_persistence_selection",
        "stochastic thermodynamics, survival analysis, and dynamical selection",
        "physical resource/failure mapping has no holdout value beyond baseline",
        "persistence is not intention or a universal least-energy law",
    ),
    (
        "UET-P8",
        "competing_closed_and_nonclosed_branches",
        "nested-model testing and covariant stress-energy balance",
        "closed limit is discontinuous or alternative fails penalized holdout comparison",
        "global-universe openness is not assumed",
    ),
)

LANES = {
    "phase": "coarse-grained order or compatibility coordinate",
    "charge": "coarse-grained signed Noether-charge coordinate",
    "density": "declared mass/number-density realization",
    "telegraph": "finite-cone non-conserved response coordinate",
}


def build() -> tuple[dict, dict]:
    records = [
        {
            "postulate_id": postulate_id,
            "name": name,
            "status": "CANDIDATE_FOUNDATION_CONTRACT",
            "standard_physics_counterpart": counterpart,
            "falsification_condition": falsification,
            "prohibited_inference": prohibited,
            "derivation_status": "POSTULATE_OR_METHOD_RULE",
            "unit_lane": "not_applicable_until_realized",
            "observable_mapping": "lane_or_measurement_specific",
        }
        for postulate_id, name, counterpart, falsification, prohibited in POSTULATES
    ]
    registry = {
        "schema_version": "1.0",
        "artifact": "uet_main_theory_axiom_registry",
        "generated_at": date.today().isoformat(),
        "specification": str(SPEC.relative_to(ROOT)).replace("\\", "/"),
        "canonical_chain": (
            "X_micro -> C_lane -> (C_lane,Phi,Pi) -> "
            "(T_munu,N_mu,Q_mu,sigma) -> R_gen -> carrier -> R_obs -> p_A(o|a)"
        ),
        "collective_coordinate_policy": {
            "status": "MULTI_LANE_REQUIRED",
            "lanes": LANES,
            "universal_identity": "REJECTED_UNLESS_DERIVED_BY_A_FUTURE_GATE",
        },
        "quantum_policy": "OPERATIONAL_BASELINE_WITH_QBISM_RQM_COMPARISON_ADAPTERS",
        "persistence_policy": "DERIVED_SELECTION_HYPOTHESIS",
        "open_system_policy": "H0_CLOSED_VERSUS_H1_NONCLOSED_TESTABLE_BRANCH",
        "postulates": records,
    }

    required_fields = {
        "postulate_id",
        "name",
        "status",
        "standard_physics_counterpart",
        "falsification_condition",
        "prohibited_inference",
        "derivation_status",
        "unit_lane",
        "observable_mapping",
    }
    ids = [record["postulate_id"] for record in records]
    checks = {
        "spec_exists": SPEC.exists(),
        "nine_postulates_present": ids == [f"UET-P{i}" for i in range(9)],
        "required_fields_complete": all(
            required_fields <= set(record)
            and all(record[field] for field in required_fields)
            for record in records
        ),
        "multi_lane_C_locked": set(LANES) == {"phase", "charge", "density", "telegraph"},
        "operational_quantum_baseline_locked": registry["quantum_policy"].startswith(
            "OPERATIONAL"
        ),
        "persistence_nonteleological": (
            registry["persistence_policy"] == "DERIVED_SELECTION_HYPOTHESIS"
        ),
        "global_openness_not_assumed": registry["open_system_policy"].startswith(
            "H0_CLOSED"
        ),
    }
    passed = all(checks.values())
    gate = {
        "schema_version": "1.0",
        "artifact": "uet_main_theory_ontology_gate",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS" if passed else "FAIL",
        "ontology_status": "PASS_CONTRACT_ONLY" if passed else "BLOCKED",
        "checks": checks,
        "upstream_gate": "uet_main_theory_wave0_gate.json",
        "controlling_blocker": (
            "covariant_parent_contract_not_integrated"
            if passed
            else "main_theory_axiom_or_ontology_contract_incomplete"
        ),
        "claim_ceiling": (
            "candidate covariant effective-theory ontology; no physical, empirical, "
            "fundamental-unification, or global-cosmology promotion"
        ),
        "next_controller": (
            "integrate the existing conservative covariant modules under one parent contract"
        ),
    }
    return registry, gate


def main() -> int:
    registry, gate = build()
    outputs = {
        "uet_main_theory_axiom_registry.json": registry,
        "uet_main_theory_ontology_gate.json": gate,
    }
    for name, payload in outputs.items():
        path = canonical_artifact_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(f"audit_status={gate['audit_status']}")
    print(f"ontology_status={gate['ontology_status']}")
    print(f"controlling_blocker={gate['controlling_blocker']}")
    return 0 if gate["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
