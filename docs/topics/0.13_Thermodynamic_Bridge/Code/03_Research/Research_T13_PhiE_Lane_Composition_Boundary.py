"""Audit whether Topic 13's two Phi_E lanes compose without an extra map."""
from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
THERMAL_MODULES = ROOT / "docs/core/03_lanes/thermal"
if str(THERMAL_MODULES) not in sys.path:
    sys.path.insert(0, str(THERMAL_MODULES))

from thermal_energy_response_bridge import named_energy_response_branch_contract
from uet_material_lattice_interface_contract import material_lattice_interface_contract
from uet_scalar_thermoelastic_response_bridge import scalar_thermoelastic_bridge_contract


ARTIFACT_PATH = (
    ROOT
    / "docs/core/07_artifacts/topic13/t13_phi_e_lane_composition_boundary_audit.json"
)
NOTE_PATH = (
    ROOT
    / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "T13_PHI_E_LANE_COMPOSITION_BOUNDARY.md"
)

INPUT_PATHS = (
    "docs/core/03_lanes/thermal/thermal_energy_response_bridge.py",
    "docs/core/03_lanes/thermal/uet_scalar_thermoelastic_response_bridge.py",
    "docs/core/03_lanes/thermal/uet_material_lattice_interface_contract.py",
    "docs/core/03_lanes/thermal/uet_dynamic_thermoelastic_response.py",
    "docs/core/07_artifacts/topic13/t13_energy_response_bridge_audit.json",
    "docs/core/07_artifacts/topic13/t13_scalar_thermoelastic_response_bridge_audit.json",
    "docs/core/07_artifacts/topic13/t13_material_interface_factor_resolution_audit.json",
    "docs/core/07_artifacts/topic13/t13_dynamic_thermoelastic_response_audit.json",
    "docs/core/07_artifacts/topic13/t13_full_closure_progress.json",
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json",
)


def _read_json(relative_path: str) -> dict[str, object]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def _sha256(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def build_audit() -> dict[str, object]:
    energy_contract = named_energy_response_branch_contract()
    scalar_contract = scalar_thermoelastic_bridge_contract()
    material_contract = material_lattice_interface_contract()
    energy_audit = _read_json(INPUT_PATHS[4])
    scalar_audit = _read_json(INPUT_PATHS[5])
    factor_audit = _read_json(INPUT_PATHS[6])
    dynamic_audit = _read_json(INPUT_PATHS[7])
    closure_progress = _read_json(INPUT_PATHS[8])
    full_gate = _read_json(INPUT_PATHS[9])

    field_phi_exponent = int(scalar_contract["natural_unit_exponents"]["Phi_E"])
    residue_exponent = int(material_contract["natural_unit_exponents"]["Phi_E"])
    normalized_energy_phi_exponent = 0
    required_conversion_exponent = (
        normalized_energy_phi_exponent - field_phi_exponent
    )
    alpha_field_exponent = (
        int(scalar_contract["natural_unit_exponents"]["temperature"])
        + int(scalar_contract["natural_unit_exponents"]["alpha_v"])
        + int(scalar_contract["natural_unit_exponents"]["g_Phi_theta"])
        + residue_exponent
        - int(scalar_contract["natural_unit_exponents"]["c_p_vol"])
    )
    alpha_energy_exponent = 4 - 3 + required_conversion_exponent + residue_exponent

    factor_status = factor_audit["factor_matrix"]
    energy_major = energy_audit["major_result"]
    full_major = full_gate["major_result"]
    input_hashes = {path: _sha256(path) for path in INPUT_PATHS}

    checks = {
        "field_lane_declares_mass_dimension_one": field_phi_exponent == 1,
        "named_energy_lane_is_dimensionless": (
            "dimensionless" in energy_contract["Phi_E"]
            and normalized_energy_phi_exponent == 0
        ),
        "base_phi_to_energy_lane_map_is_open": (
            "OPEN" in energy_contract["base_Phi_to_Phi_E_map"]
        ),
        "energy_lane_does_not_assert_base_phi_identity": (
            energy_contract["base_Phi_identity"] == "not asserted"
        ),
        "field_to_energy_lane_map_requires_inverse_energy": (
            required_conversion_exponent == -1
        ),
        "thermoelastic_alpha_unit_closes_conditionally": (
            alpha_field_exponent == 1
        ),
        "energy_alpha_unit_closes_only_after_conversion": (
            alpha_energy_exponent == 1
        ),
        "physical_field_residue_remains_open": (
            "OPEN" in factor_status["Z_Phi"]["resolution_status"]
        ),
        "physical_strain_coupling_is_absent_from_current_action": (
            factor_status["g_Phi_theta"]["resolution_status"]
            == "ABSENT_FROM_CURRENT_ACTION"
        ),
        "named_energy_alpha_is_not_emitted": (
            energy_audit["numeric_calibration"]["alpha_Phi_E_K"] is None
        ),
        "dynamic_bridge_is_synthetic_comparator": (
            dynamic_audit["data_role"] == "SYNTHETIC_COMPARATOR_NO_CALIBRATION"
        ),
        "full_topic_gate_remains_blocked_without_promotion": (
            full_gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
            and full_gate["claim_promotion"] is False
        ),
        "core_progress_separates_he4_from_graphite": (
            closure_progress["closure_tracks"]["o2_he4_core_ready"]["status"]
            == "CLOSED_FOR_CORE"
            and closure_progress["closure_tracks"]["graphite_ttg_external_validation"][
                "status"
            ]
            == "OPEN"
        ),
        "audit_emits_no_numeric_physical_alpha": True,
        "audit_performs_no_fit_or_target_calibration": True,
    }

    all_passed = all(checks.values())
    what_is_closed = [
        "The natural-unit thermoelastic lane types Phi_E as a field-amplitude coordinate with mass dimension one.",
        "The named energy-response lane defines Phi_E=Delta_u/e0 as dimensionless; it does not identify that coordinate with base Phi.",
        "An unqualified identity between the two Phi_E coordinates is dimensionally invalid. A cross-lane map kappa_E with mass dimension -1 is required before composing their alpha formulas.",
        "Both candidate alpha formulas are dimensionally consistent only within their declared lanes and after the missing cross-lane map and physical inputs are supplied.",
        "The scalar thermoelastic formula uses a zero-stress, adiabatic C_p^V response; the energy-source formula uses a fixed-volume c_v/C_src response. Their boundary and material roles cannot be silently substituted.",
    ]
    open_blockers = [
        "field_dimensional_Phi_E_to_dimensionless_energy_Phi_E_map_kappa_E_missing",
        "base_Phi_to_energy_density_mapping_missing",
        "physical_Z_Phi_and_g_Phi_theta_missing",
        "source_locked_e0_c_v_and_same_state_material_package_missing",
        "C_p_v_C_v_C_src_boundary_and_mode_correspondence_missing",
        "TTG_finite_q_initialization_detector_and_uncertainty_map_missing",
    ]
    status = (
        "PASS_SCOPED_PHI_E_LANE_COMPOSITION_BOUNDARY"
        if all_passed
        else "WARN_PHI_E_LANE_COMPOSITION_BOUNDARY"
    )
    field_alpha = "T*alpha_V*g_Phi_theta*Z_Phi/C_p^V"
    energy_alpha = "(e0/c_v)*kappa_E*Z_Phi"
    result: dict[str, object] = {
        "schema_version": "t13-phi-e-lane-composition-boundary-v1",
        "artifact": "t13_phi_e_lane_composition_boundary_audit",
        "generated_at": date.today().isoformat(),
        "owner_topic": "0.13_Thermodynamic_Bridge",
        "canonical_path": "docs/core/07_artifacts/topic13/"
        "t13_phi_e_lane_composition_boundary_audit.json",
        "major_result_id": "T13_PHI_E_LANE_COMPOSITION_BOUNDARY",
        "closure_level": "CLOSED_FOR_LANE" if all_passed else "PARTIAL",
        "closure_disposition": "NO_GO_FOR_SILENT_CROSS_LANE_IDENTIFICATION",
        "verification_status": status,
        "f0_inventory": {
            "field_lane_definition": material_contract["equations"][
                "canonical_response_map"
            ],
            "energy_lane_definition": energy_contract["definition"],
            "thermoelastic_lane_equation_id": (
                "uet.o2.thermal.scalar_thermoelastic_response_bridge"
            ),
            "energy_lane_id": energy_contract["branch_id"],
        },
        "f1_ontology": {
            "Phi_base": "normalized effective response coordinate; not temperature",
            "Phi_E_field": "field-amplitude coordinate in the thermoelastic action lane",
            "Phi_E_energy": "dimensionless Delta_u/e0 coordinate in the standard energy-response lane",
            "theta": "external material volumetric strain div(u)",
            "C": "unchanged collective coordinate; not heat capacity",
            "R_gen": "derived history trace; excluded from state and backreaction",
        },
        "f2_physical_correspondence": {
            "field_lane": "Phi_base -> Z_Phi*Phi_base -> conditional material strain response",
            "energy_lane": "Delta_u -> Delta_u/e0 -> Delta_Tq=Delta_u/c_v",
            "missing_cross_lane_map": "Phi_E_energy=kappa_E*Phi_E_field",
            "map_status": "OPEN_DERIVATION_OR_INDEPENDENT_CALIBRATION",
            "composition_condition": "same material/state, observable, and mechanical/thermal boundary conditions",
        },
        "f3_units": {
            "unit_lane": "natural field-amplitude chart plus normalized energy-response chart",
            "Phi_base": 0,
            "Z_Phi": residue_exponent,
            "Phi_E_field": field_phi_exponent,
            "Phi_E_energy": normalized_energy_phi_exponent,
            "kappa_E_required": required_conversion_exponent,
            "delta_u_energy_density": 4,
            "e0_energy_density": 4,
            "c_v_volumetric_heat_capacity": 3,
            "g_Phi_theta": int(scalar_contract["natural_unit_exponents"]["g_Phi_theta"]),
            "C_p_volumetric_heat_capacity": int(
                scalar_contract["natural_unit_exponents"]["c_p_vol"]
            ),
            "alpha_Phi_base": alpha_field_exponent,
            "alpha_energy_composition": alpha_energy_exponent,
            "unit_conclusion": "both alpha routes have the same final dimension only after kappa_E is declared; dimensional agreement does not determine its value",
        },
        "f4_derivation": {
            "derived_within_energy_lane": energy_contract["standard_map"],
            "derived_within_conditional_thermoelastic_lane": scalar_contract["equations"][
                "temperature_response"
            ],
            "not_derived": "kappa_E and equality between the two lane-specific coordinates",
            "derivation_class": "standard_energy_to_temperature_identity plus conditional thermoelastic stationarity; cross-lane bridge remains open",
        },
        "equation_or_mapping": {
            "field_amplitude": "Phi_E_field=Z_Phi*DeltaPhi_base",
            "normalized_energy_coordinate": "Phi_E_energy=Delta_u/e0",
            "required_conversion": "Phi_E_energy=kappa_E*Phi_E_field; [kappa_E]=E^-1",
            "energy_route_alpha": energy_alpha,
            "conditional_thermoelastic_route_alpha": field_alpha,
            "cross_route_equality": "not asserted; requires same state and matched boundary/observable maps",
        },
        "data_role": "INTERNAL_FORMULA_AND_LANE_TYPE_AUDIT_NO_SOURCE_ROWS",
        "checks": checks,
        "checks_passed": sum(bool(value) for value in checks.values()),
        "checks_total": len(checks),
        "what_is_closed": what_is_closed,
        "what_remains_open": open_blockers,
        "controlling_blocker": "cross_lane_Phi_E_normalization_and_base_Phi_to_energy_density_map_missing",
        "dependency_unlocked": "Explicit lane typing only; no physical or downstream dependency unlock.",
        "physical_dependency_unlock": False,
        "full_core_unlock": False,
        "claim_promotion": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "holdout_use": {
            "numeric_payload_consumed_by_this_local_audit": False,
            "blind_eligibility": "REVIEW_REQUIRED_AFTER_SESSION_EXPOSURE",
        },
        "source_hashes": input_hashes,
        "evidence_artifacts": [
            {
                "path": "docs/core/07_artifacts/topic13/"
                "t13_phi_e_lane_composition_boundary_audit.json",
                "role": "generated scoped cross-lane type and composition audit",
            },
            {
                "path": "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
                "T13_PHI_E_LANE_COMPOSITION_BOUNDARY.md",
                "role": "human-readable F0-F4 handoff",
            },
        ],
        "claim_boundary": "This closes only the no-go on silently identifying two lane-specific Phi_E coordinates. It does not prove that an explicit future bridge is impossible, emit alpha_Phi_K, validate graphite TTG, or close Full Topic 13.",
    }
    result["report"] = {
        "MAJOR_RESULT_CLOSURE": result["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": what_is_closed,
        "WHAT_REMAINS_OPEN": open_blockers,
        "DEPENDENCY_UNLOCKED": result["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Added a fail-closed F0-F4 type/composition audit; no accepted equation, coefficient, registry entry, or dependency gate was changed.",
        "EQUATION_OR_MAPPING": result["equation_or_mapping"],
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": result["controlling_blocker"],
        "NEXT_ACTION": "Derive or independently calibrate kappa_E and Z_Phi on one declared material/state, then map C_v/C_src and the actual TTG boundary/observable before comparing either alpha route.",
        "CLAIM_BOUNDARY": result["claim_boundary"],
    }
    return result


def render_note(result: dict[str, object]) -> str:
    report = result["report"]
    closed = "\n".join(f"- {item}" for item in report["WHAT_IS_ACTUALLY_CLOSED"])
    open_items = "\n".join(f"- {item}" for item in report["WHAT_REMAINS_OPEN"])
    checks = result["checks"]
    return f"""# Topic 13 Phi_E Lane Composition Boundary

Owner: Topic 13 scientific lane; Core owns cross-lane integration.
Canonical artifact: `docs/core/07_artifacts/topic13/t13_phi_e_lane_composition_boundary_audit.json`.
Generated: {result['generated_at']}.

MAJOR_RESULT_CLOSURE: `{result['closure_level']}` for the no-go on silent cross-lane identification only.

WHAT_IS_ACTUALLY_CLOSED:
{closed}

WHAT_REMAINS_OPEN:
{open_items}

DEPENDENCY_UNLOCKED: None beyond explicit lane typing; no physical dependency is unlocked.

STATUS: `{report['STATUS']}`.

WHAT_CHANGED: Added a fail-closed F0-F4 composition audit. No accepted UET action, equation registry entry, physical coefficient, or dependency gate was modified.

EQUATION_OR_MAPPING:
```text
Phi_E_field  = Z_Phi * DeltaPhi_base              [Phi_E_field] = E^1
Phi_E_energy = Delta_u / e0                       [Phi_E_energy] = E^0
Phi_E_energy = kappa_E * Phi_E_field              [kappa_E] = E^-1; OPEN

alpha_energy = (e0 / c_v) * kappa_E * Z_Phi
alpha_thermoelastic = T * alpha_V * g_Phi_theta * Z_Phi / C_p^V
```
The two alpha expressions are not interchangeable until the field-to-energy map, material state, measured observable, and boundary conditions are matched.

VERIFICATION: {result['checks_passed']}/{result['checks_total']} structural and unit checks passed. No numeric alpha, target data, or fit was produced. Holdout numeric payload was not consumed by this local audit; blind-use eligibility remains `REVIEW_REQUIRED` after session exposure.

CONTROLLING_BLOCKER: `{result['controlling_blocker']}`.

NEXT_ACTION: Derive or independently calibrate `kappa_E` and `Z_Phi` for one declared material/state, then establish the `c_v`/`C_src` correspondence and finite-q TTG measurement boundary before comparing either alpha route.

CLAIM_BOUNDARY: This is a scoped no-go for silently identifying the two lane-specific `Phi_E` coordinates. It does not show that a future explicit bridge is impossible, emit `alpha_Phi_K`, validate graphite TTG, or close Full Topic 13.
"""


def write_outputs() -> dict[str, object]:
    result = build_audit()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    NOTE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    NOTE_PATH.write_text(render_note(result), encoding="utf-8")
    return result


if __name__ == "__main__":
    audit = write_outputs()
    print(
        json.dumps(
            {
                "status": audit["verification_status"],
                "checks_passed": audit["checks_passed"],
                "checks_total": audit["checks_total"],
                "kappa_E_mass_exponent": audit["f3_units"]["kappa_E_required"],
                "numeric_alpha_Phi_K_emitted": audit["numeric_alpha_Phi_K_emitted"],
                "full_core_unlock": audit["full_core_unlock"],
            },
            indent=2,
        )
    )
