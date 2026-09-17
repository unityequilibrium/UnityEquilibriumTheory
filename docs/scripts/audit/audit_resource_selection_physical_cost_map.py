"""Audit the opt-in dimensional cost-map contract.

The audit proves contract behavior and deliberate blocking. It also applies a
TEST_ONLY SI fixture to the dynamic-game controls to check that the algebraic
map does not collapse interaction-derived C into ledger depletion. It does not
claim that a physical cost scale has been sourced or derived.
"""

from __future__ import annotations

import json
import sys
from math import isclose
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from docs.core.core_paths import canonical_artifact_path
from docs.core.resource_selection_physical_cost_map import (
    PHYSICAL_COST_MAP_OPERATOR_MODE,
    PHYSICAL_COST_MAP_STATUS,
    PhysicalCostMapRecord,
    PhysicalCostMapValidationError,
    map_normalized_work_to_si,
)
from docs.core.uet_resource_selection import (
    ResourceSelectionConfig,
    simulate_resource_selection,
)


HORIZON = 10.0
DT = 0.001


def selection(matrix, behavior_cost, maintenance_cost):
    return simulate_resource_selection(
        ResourceSelectionConfig(
            interaction_matrix=matrix,
            behavior_cost=behavior_cost,
            maintenance_cost=maintenance_cost,
            cost_weight=0.0,
        ),
        horizon=HORIZON,
        dt=DT,
    )


def main() -> int:
    open_record = PhysicalCostMapRecord(
        map_id="open-map",
        material_or_system="unresolved-material-lane",
    )
    open_rejected = False
    try:
        map_normalized_work_to_si(0.25, 0.1, open_record)
    except PhysicalCostMapValidationError:
        open_rejected = True

    fit_rejected = False
    try:
        PhysicalCostMapRecord(
            map_id="fit-map",
            material_or_system="target-material",
            behavior_energy_scale_j=2.0,
            maintenance_energy_scale_j=3.0,
            bath_temperature_k=300.0,
            source_locator="fit://target-data",
            source_hash="fit-only",
            uncertainty_record="not-independent",
            measurement_operator_id="heat",
            parameter_origin="fit",
        ).validate_contract()
    except PhysicalCostMapValidationError:
        fit_rejected = True

    fixture_record = PhysicalCostMapRecord(
        map_id="synthetic-contract-fixture",
        material_or_system="synthetic-material",
        behavior_energy_scale_j=2.0,
        maintenance_energy_scale_j=3.0,
        bath_temperature_k=300.0,
        source_locator="synthetic://physical-cost-contract",
        source_hash="fixture-hash",
        uncertainty_record="fixture-only; not external evidence",
        measurement_operator_id="integrated_heat_fixture",
        parameter_origin="test_fixture",
        status="TEST_ONLY",
    )
    fixture_result = map_normalized_work_to_si(0.25, 0.1, fixture_record)

    costless_low = selection(
        ((0.9, 0.8), (0.8, 0.9)),
        (0.02, 0.03),
        (0.01, 0.01),
    )
    costless_high = selection(
        ((0.9, 0.8), (0.8, 0.9)),
        (0.2, 0.3),
        (0.1, 0.1),
    )
    same_cost_cooperative = selection(
        ((0.9, 0.8), (0.8, 0.9)),
        (0.05, 0.05),
        (0.02, 0.02),
    )
    same_cost_conflict = selection(
        ((0.3, -0.9), (-0.9, 0.3)),
        (0.05, 0.05),
        (0.02, 0.02),
    )
    low_heat = map_normalized_work_to_si(
        costless_low.behavior_work,
        costless_low.maintenance_work,
        fixture_record,
    )
    high_heat = map_normalized_work_to_si(
        costless_high.behavior_work,
        costless_high.maintenance_work,
        fixture_record,
    )
    same_cost_cooperative_heat = map_normalized_work_to_si(
        same_cost_cooperative.behavior_work,
        same_cost_cooperative.maintenance_work,
        fixture_record,
    )
    same_cost_conflict_heat = map_normalized_work_to_si(
        same_cost_conflict.behavior_work,
        same_cost_conflict.maintenance_work,
        fixture_record,
    )
    mapped_cost_C_residual = max(
        abs(a - b)
        for a, b in zip(
            costless_low.collective_compatibility,
            costless_high.collective_compatibility,
        )
    )
    mapped_same_cost_C_contrast = max(
        abs(a - b)
        for a, b in zip(
            same_cost_cooperative.collective_compatibility,
            same_cost_conflict.collective_compatibility,
        )
    )
    mapped_cost_heat_difference_j = low_heat.heat_j - high_heat.heat_j
    mapped_same_cost_heat_residual_j = (
        same_cost_cooperative_heat.heat_j - same_cost_conflict_heat.heat_j
    )

    gates = {
        "open_map_is_rejected": open_rejected,
        "fit_origin_is_rejected": fit_rejected,
        "fixture_heat_formula_closes": isclose(
            fixture_result.heat_j, 0.8, rel_tol=0.0, abs_tol=1e-12
        ),
        "fixture_entropy_formula_closes": isclose(
            fixture_result.entropy_j_per_k, 0.8 / 300.0, rel_tol=0.0, abs_tol=1e-12
        ),
        "no_default_physical_scale": (
            open_record.behavior_energy_scale_j is None
            and open_record.maintenance_energy_scale_j is None
        ),
        "measurement_operator_is_explicit": bool(
            fixture_result.measurement_operator_id
        ),
        "mapped_cost_control_keeps_C_invariant": mapped_cost_C_residual <= 1e-12,
        "mapped_cost_control_changes_heat": abs(mapped_cost_heat_difference_j) > 1e-6,
        "mapped_same_cost_interaction_changes_C": mapped_same_cost_C_contrast > 1e-3,
        "mapped_same_cost_keeps_heat_invariant": abs(mapped_same_cost_heat_residual_j) <= 1e-12,
    }
    artifact = {
        "schema_version": "1.0",
        "artifact": "resource_selection_physical_cost_map_verification",
        "operator_mode": PHYSICAL_COST_MAP_OPERATOR_MODE,
        "audit_status": (
            "PASS_WITH_BLOCKED_INDEPENDENT_CALIBRATION"
            if all(gates.values())
            else "FAIL"
        ),
        "status": "INTERNAL_CONTRACT",
        "claim_status": "CONTRACT_ONLY",
        "evidence_class": "INTERNAL_CONTRACT",
        "unit_lane": "si_contract_only",
        "physical_mapping_status": PHYSICAL_COST_MAP_STATUS,
        "formula_audit": [
            {
                "formula_id": "PHYSICAL-COST-001",
                "relation": "Q_J=alpha_b*W_behavior+alpha_m*W_maintenance",
                "origin": "explicit dimensional mapping contract",
                "status": "contractual; alpha values are not inferred",
            },
            {
                "formula_id": "PHYSICAL-COST-002",
                "relation": "Delta_S_bath_J_per_K=Q_J/T_bath_K",
                "origin": "isothermal thermodynamic comparator",
                "status": "contractual; not external entropy evidence",
            },
        ],
        "fixture": {
            "behavior_work_normalized": 0.25,
            "maintenance_work_normalized": 0.1,
            "behavior_energy_scale_j": 2.0,
            "maintenance_energy_scale_j": 3.0,
            "bath_temperature_k": 300.0,
            "heat_j": fixture_result.heat_j,
            "entropy_j_per_k": fixture_result.entropy_j_per_k,
            "parameters_fit": False,
            "evidence_status": "TEST_ONLY",
        },
        "control_mapping_metrics": {
            "cost_control_C_residual": mapped_cost_C_residual,
            "cost_control_heat_difference_j": mapped_cost_heat_difference_j,
            "same_cost_interaction_C_contrast": mapped_same_cost_C_contrast,
            "same_cost_heat_residual_j": mapped_same_cost_heat_residual_j,
            "evidence_status": "TEST_ONLY",
        },
        "gates": gates,
        "limitations": [
            "the fixture is a contract test, not a material measurement",
            "no independent alpha_b or alpha_m source is supplied",
            "no calorimetry/heat-flux dataset, uncertainty distribution, or detector response is supplied",
            "normalized C and normalized work are not identified with temperature or SI energy",
            "the mapped control result tests algebraic separation only; it is not physical validation",
            "a ready map must be derived or source-locked and cannot be fit to the target result",
        ],
        "claim_boundary": (
            "The SI conversion interface preserves the declared C/cost separation in a "
            "test fixture and blocks incomplete or fitted maps; no physical heat, entropy, "
            "or persistence prediction is promoted."
        ),
        "next_controller": (
            "source-lock independent alpha_b and alpha_m in one material lane with "
            "calorimetry or heat-flux measurement, uncertainty, detector operator, and holdout"
        ),
    }
    output = ROOT.parent / canonical_artifact_path("resource_selection_physical_cost_map_verification.json", "provenance")
    output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2))
    return 0 if artifact["audit_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
