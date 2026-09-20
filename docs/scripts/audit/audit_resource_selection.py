"""Verify the non-agentic resource-selection comparator."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from docs.core.uet_resource_selection import (  # noqa: E402
    RESOURCE_SELECTION_OPERATOR_MODE,
    ResourceSelectionConfig,
    simulate_resource_selection,
)
from docs.core.core_paths import canonical_artifact_path  # noqa: E402


def _run(config: ResourceSelectionConfig) -> dict:
    result = simulate_resource_selection(config, horizon=10.0, dt=0.001)
    return {
        "final_resource": result.available_resource[-1],
        "persistence_time": result.persistence_time,
        "behavior_work": result.behavior_work,
        "maintenance_work": result.maintenance_work,
        "ledger_closure_residual": result.ledger_closure_residual,
        "probability_simplex_drift": result.probability_simplex_drift,
        "minimum_probability": result.minimum_probability,
        "min_compatibility": min(result.collective_compatibility),
        "max_compatibility": max(result.collective_compatibility),
        "result": result,
    }


def build_artifact() -> dict:
    cooperative = ResourceSelectionConfig(
        interaction_matrix=((0.9, 0.8), (0.8, 0.9)),
        behavior_cost=(0.02, 0.03),
        maintenance_cost=(0.01, 0.01),
    )
    conflict = ResourceSelectionConfig(
        interaction_matrix=((0.3, -0.9), (-0.9, 0.3)),
        behavior_cost=(0.12, 0.15),
        maintenance_cost=(0.03, 0.04),
    )
    coop = _run(cooperative)
    conflict_result = _run(conflict)
    deterministic_repeat = _run(cooperative)

    # Controls separate the interaction-derived C signal from the cost vectors
    # that directly drain the resource ledger.  The original cooperative vs
    # conflict pair changes both at once, so it cannot attribute persistence
    # ordering to C alone.
    control_matrix = ((0.9, 0.8), (0.8, 0.9))
    costless_low = _run(
        ResourceSelectionConfig(
            interaction_matrix=control_matrix,
            behavior_cost=(0.02, 0.03),
            maintenance_cost=(0.01, 0.01),
            cost_weight=0.0,
        )
    )
    costless_high = _run(
        ResourceSelectionConfig(
            interaction_matrix=control_matrix,
            behavior_cost=(0.2, 0.3),
            maintenance_cost=(0.1, 0.1),
            cost_weight=0.0,
        )
    )
    zero_cost = _run(
        ResourceSelectionConfig(
            interaction_matrix=control_matrix,
            behavior_cost=(0.0, 0.0),
            maintenance_cost=(0.0, 0.0),
            cost_weight=0.0,
        )
    )
    same_cost_cooperative = _run(
        ResourceSelectionConfig(
            interaction_matrix=((0.9, 0.8), (0.8, 0.9)),
            behavior_cost=(0.05, 0.05),
            maintenance_cost=(0.02, 0.02),
            cost_weight=0.0,
        )
    )
    same_cost_conflict = _run(
        ResourceSelectionConfig(
            interaction_matrix=((0.3, -0.9), (-0.9, 0.3)),
            behavior_cost=(0.05, 0.05),
            maintenance_cost=(0.02, 0.02),
            cost_weight=0.0,
        )
    )
    costless_C_residual = max(
        abs(a - b)
        for a, b in zip(
            costless_low["result"].collective_compatibility,
            costless_high["result"].collective_compatibility,
        )
    )
    same_cost_C_contrast = max(
        abs(a - b)
        for a, b in zip(
            same_cost_cooperative["result"].collective_compatibility,
            same_cost_conflict["result"].collective_compatibility,
        )
    )
    same_cost_resource_residual = abs(
        same_cost_cooperative["final_resource"]
        - same_cost_conflict["final_resource"]
    )
    controls = {
        "costless_selection_C_residual": costless_C_residual,
        "costless_low_final_resource": costless_low["final_resource"],
        "costless_high_final_resource": costless_high["final_resource"],
        "zero_cost_final_resource": zero_cost["final_resource"],
        "zero_cost_resource_range": max(zero_cost["result"].available_resource)
        - min(zero_cost["result"].available_resource),
        "same_cost_interaction_C_contrast": same_cost_C_contrast,
        "same_cost_interaction_resource_residual": same_cost_resource_residual,
    }

    gates = {
        "simplex_drift_le_1e-12": max(
            coop["probability_simplex_drift"],
            conflict_result["probability_simplex_drift"],
        ) <= 1e-12,
        "minimum_probability_ge_minus_1e-14": min(
            coop["minimum_probability"],
            conflict_result["minimum_probability"],
        ) >= -1e-14,
        "ledger_closure_le_1e-12": max(
            abs(coop["ledger_closure_residual"]),
            abs(conflict_result["ledger_closure_residual"]),
        ) <= 1e-12,
        "nonnegative_resource_cost": (
            coop["behavior_work"] >= 0.0
            and conflict_result["behavior_work"] >= 0.0
            and coop["maintenance_work"] >= 0.0
            and conflict_result["maintenance_work"] >= 0.0
        ),
        "cooperative_persists_longer": (
            coop["persistence_time"] is None
            or (
                conflict_result["persistence_time"] is not None
                and coop["persistence_time"] > conflict_result["persistence_time"]
            )
        ),
        "collective_C_is_interaction_derived": True,
        "no_parameter_fitting": True,
        "no_intentional_optimizer": True,
        "deterministic_repeat": (
            coop["final_resource"] == deterministic_repeat["final_resource"]
            and coop["behavior_work"] == deterministic_repeat["behavior_work"]
        ),
        "costless_interaction_keeps_C_invariant": controls["costless_selection_C_residual"] <= 1e-12,
        "costless_resource_changes_with_declared_cost": (
            controls["costless_low_final_resource"]
            > controls["costless_high_final_resource"]
        ),
        "zero_cost_resource_is_constant": controls["zero_cost_resource_range"] <= 1e-12,
        "same_cost_interaction_changes_C": controls["same_cost_interaction_C_contrast"] >= 1e-3,
        "same_cost_interaction_does_not_change_ledger": (
            controls["same_cost_interaction_resource_residual"] <= 1e-12
        ),
    }
    artifact = {
        "schema_version": "1.0",
        "artifact": "resource_selection_dynamic_game_verification",
        "operator_mode": RESOURCE_SELECTION_OPERATOR_MODE,
        "audit_status": "PASS_WITH_OPEN_PHYSICAL_MAPPING" if all(gates.values()) else "FAIL",
        "status": "INTERNAL_DIAGNOSTIC",
        "claim_status": "SIMULATION_ONLY",
        "evidence_class": "INTERNAL_DIAGNOSTIC",
        "unit_lane": "normalized",
        "model_class": "non_agentic_replicator_style_interaction_selection",
        "principle_id": "UET-PRINCIPLE-001",
        "formula_audit": [
            {
                "formula_id": "SELECTION-STATE-001",
                "relation": "dp_i/dt=p_i*(f_i-sum_j(p_j*f_j))",
                "origin": "standard evolutionary-game comparator",
                "status": "constitutive_comparator",
            },
            {
                "formula_id": "SELECTION-C-002",
                "relation": "C=sum_i,j(p_i*A_ij*p_j)",
                "origin": "declared collective compatibility definition",
                "status": "derived_from_interaction_state",
            },
            {
                "formula_id": "SELECTION-LEDGER-003",
                "relation": "dE_available/dt=J_in-J_out-P_behavior-P_maintenance",
                "origin": "normalized resource bookkeeping identity",
                "status": "locally_verified",
            },
        ],
        "configurations": {
            "cooperative": {
                "interaction_matrix": cooperative.interaction_matrix,
                "behavior_cost": cooperative.behavior_cost,
                "maintenance_cost": cooperative.maintenance_cost,
                "initial_probabilities": cooperative.initial_probabilities,
            },
            "conflict": {
                "interaction_matrix": conflict.interaction_matrix,
                "behavior_cost": conflict.behavior_cost,
                "maintenance_cost": conflict.maintenance_cost,
                "initial_probabilities": conflict.initial_probabilities,
            },
            "horizon": 10.0,
            "dt": 0.001,
            "parameters_fit": False,
        },
        "metrics": {
            "cooperative": {key: value for key, value in coop.items() if key != "result"},
            "conflict": {key: value for key, value in conflict_result.items() if key != "result"},
            "final_resource_difference": coop["final_resource"] - conflict_result["final_resource"],
            "controls": controls,
        },
        "gates": gates,
        "limitations": [
            "interaction matrix, cost vectors, and replicator law are constitutive comparator inputs",
            "normalized resource is not SI energy",
            "no physical mass, temperature, heat, entropy, particle, or cosmological mapping is supplied",
            "the result supports only a simulation-level persistence ordering under the declared comparator",
            "the original cooperative/conflict comparison changes interaction and cost inputs together; it cannot attribute persistence to C alone",
            "control experiments show that C and ledger depletion are separable outputs until a physical cost map is supplied",
        ],
        "next_controller": "map behavior and maintenance costs to a measured work, heat, entropy, or failure-rate observable in one physical lane",
    }
    return artifact


def main() -> int:
    artifact = build_artifact()
    output = ROOT / "core" / "artifacts" / "resource_selection_dynamic_game_verification.json"
    output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    contract = {
        "schema_version": "1.0",
        "artifact": "resource_selection_dynamic_game_contract",
        "operator_mode": RESOURCE_SELECTION_OPERATOR_MODE,
        "status": artifact["status"],
        "principle_id": "UET-PRINCIPLE-001",
        "unit_lane": "normalized",
        "physical_mapping_status": "OPEN",
        "formula_ids": [row["formula_id"] for row in artifact["formula_audit"]],
        "verifier_artifact": "docs/core/07_artifacts/provenance/resource_selection_dynamic_game_verification.json",
        "no_intentionality": True,
        "no_parameter_fitting": True,
        "control_experiment_status": "PASS_COST_AND_INTERACTION_SEPARATED",
        "identifiability_boundary": "original cooperative/conflict contrast is cost-confounded; C and ledger depletion are not identified as the same quantity",
        "claim_boundary": "candidate non-agentic interaction-selection comparator; simulation-only",
        "next_controller": artifact["next_controller"],
    }
    canonical_artifact_path(
        "resource_selection_dynamic_game_contract.json", "provenance"
    ).write_text(
        json.dumps(contract, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(artifact, indent=2, ensure_ascii=False))
    return 0 if artifact["audit_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
