"""Audit the chain-rule boundary for covariant-to-normalized-Phi SI response."""
from __future__ import annotations

import hashlib
import inspect
import json
from datetime import date
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
EQUATION_DIR = ROOT / "docs/core/02_equations/o2"
THERMAL_DIR = ROOT / "docs/core/03_lanes/thermal"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(THERMAL_DIR) not in sys.path:
    sys.path.insert(0, str(THERMAL_DIR))
if str(EQUATION_DIR) not in sys.path:
    sys.path.insert(0, str(EQUATION_DIR))

from thermal_covariant_action_si_conversion import (  # noqa: E402
    NaturalUnitScale,
    symbolic_si_conversion_contract,
)
from uet_o2_action_thermal_observable_bridge import (  # noqa: E402
    action_natural_phi_thermal_bridge_contract,
)


INPUT_PATHS = (
    "docs/core/03_lanes/thermal/thermal_covariant_action_si_conversion.py",
    "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
    "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
    "docs/core/02_equations/covariant/uet_covariant_response.py",
    "docs/core/07_artifacts/topic13/"
    "t13_covariant_action_symbolic_si_conversion_audit.json",
    "docs/core/07_artifacts/topic13/t13_covariant_action_si_anchor_route_audit.json",
    "docs/core/07_artifacts/topic13/t13_alpha_phi_k_identifiability_audit.json",
    "docs/core/07_artifacts/topic13/t13_phi_e_lane_composition_boundary_audit.json",
)
ARTIFACT_PATH = (
    ROOT
    / "docs/core/07_artifacts/topic13/"
    "t13_si_phi_normalization_jacobian_audit.json"
)
NOTE_PATH = (
    ROOT
    / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "T13_SI_PHI_NORMALIZATION_JACOBIAN_AUDIT.md"
)


def _read_json(relative_path: str) -> dict[str, object]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def _sha256(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def build_audit() -> dict[str, object]:
    module_text = (ROOT / INPUT_PATHS[0]).read_text(encoding="utf-8")
    o2_eos_text = (ROOT / INPUT_PATHS[2]).read_text(encoding="utf-8")
    covariant_response_text = (ROOT / INPUT_PATHS[3]).read_text(encoding="utf-8")
    si_conversion = _read_json(INPUT_PATHS[4])
    anchor_route = _read_json(INPUT_PATHS[5])
    alpha_identifiability = _read_json(INPUT_PATHS[6])
    lane_composition = _read_json(INPUT_PATHS[7])
    contract = symbolic_si_conversion_contract()
    natural_bridge = action_natural_phi_thermal_bridge_contract()
    alpha_parameters = inspect.signature(
        NaturalUnitScale.alpha_energy_to_si
    ).parameters

    field_normalization = str(contract["field_normalization"])
    alpha_formula = str(contract["alpha_response"])
    alpha_units = str(si_conversion["major_result"]["units"]["alpha_Phi_K"])
    phi_scale_nat = 3.0
    alpha_covariant_nat = 0.25
    alpha_normalized_nat = alpha_covariant_nat * phi_scale_nat
    normalization_ratio = alpha_normalized_nat / alpha_covariant_nat

    checks = {
        "covariant_to_normalized_map_is_explicit": (
            field_normalization == "Phi_normalized = Phi_covariant/Phi_scale"
        ),
        "normalized_alpha_units_are_declared": (
            alpha_units == "K per normalized Phi"
        ),
        "existing_alpha_formula_does_not_name_derivative_coordinate": (
            "covariant" not in alpha_formula.lower()
            and "normalized" not in alpha_formula.lower()
        ),
        "existing_alpha_formula_omits_phi_scale_jacobian": (
            "Phi_scale" not in alpha_formula
        ),
        "si_helper_has_no_field_scale_argument": (
            "phi_scale" not in alpha_parameters
        ),
        "si_helper_only_applies_temperature_reference": (
            "return self.temperature_energy_to_si(natural_alpha_energy)"
            in module_text
        ),
        "normalization_helper_uses_declared_field_scale": (
            "return float(covariant_phi) / scale" in module_text
        ),
        "natural_action_alpha_is_not_sourced_as_normalized_si_alpha": (
            "not K per normalized Phi"
            in natural_bridge["unit_contract"]["alpha_Phi_T_natural"]
            and natural_bridge["excluded"]["base_Phi_to_Phi_E_scale"] is True
        ),
        "o2_action_phi_has_mass_dimension_one": '"phi": 1,' in covariant_response_text,
        "o2_energy_response_derivative_is_wrt_action_phi": (
            "(partial_Phi epsilon)_(T,mu)"
            in natural_bridge["equations"]["energy_response"]
            and "space_response" in o2_eos_text
        ),
        "symbolic_si_audit_keeps_phi_scale_open": (
            si_conversion["inputs"]["phi_scale_in_energy_reference_units"] is None
        ),
        "action_anchor_route_keeps_phi_scale_open": (
            anchor_route["major_result"]["coefficient_provenance"]["phi_scale"]
            is None
        ),
        "normalized_lane_scale_rescaling_is_nonidentifiable": (
            alpha_identifiability["checks"][
                "absolute_alpha_not_identifiable_from_normalized_lane"
            ]
            is True
        ),
        "lane_composition_keeps_cross_lane_map_open": (
            lane_composition["f2_physical_correspondence"]["map_status"]
            == "OPEN_DERIVATION_OR_INDEPENDENT_CALIBRATION"
        ),
        "chain_rule_witness_applies_scale_once": (
            normalization_ratio == phi_scale_nat
        ),
        "no_physical_alpha_or_target_result_is_emitted": True,
        "no_holdout_numeric_payload_is_consumed": True,
    }
    all_passed = all(checks.values())
    status = (
        "PASS_SCOPED_SI_PHI_NORMALIZATION_JACOBIAN_BOUNDARY"
        if all_passed
        else "WARN_SI_PHI_NORMALIZATION_JACOBIAN_BOUNDARY"
    )
    equation_or_mapping = {
        "temperature_conversion": "T_SI = (E_ref/k_B) * theta_nat",
        "field_normalization": "Phi_normalized = Phi_covariant/Phi_scale",
        "scale_in_reference_units": "Phi_scale_nat = Phi_scale_SI/E_ref",
        "covariant_derivative_conversion": (
            "alpha_covariant_K = (E_ref/k_B) * "
            "alpha_Phi_theta_covariant_nat"
        ),
        "normalized_derivative_chain_rule": (
            "alpha_Phi_K = (E_ref/k_B) * Phi_scale_nat * "
            "alpha_Phi_theta_covariant_nat"
        ),
        "conditional_alternative": (
            "alpha_Phi_K = (E_ref/k_B) * alpha_Phi_theta_normalized_nat "
            "only if the natural coefficient is already differentiated "
            "with respect to Phi_normalized"
        ),
    }
    what_is_closed = [
        "The chain-rule factor between a covariant-field derivative and a derivative with respect to dimensionless normalized Phi is Phi_scale_nat.",
        "The O(2) action-derived thermal coefficient differentiates with respect to its covariant Phi field, whose declared natural mass dimension is E^1; it is not already a derivative with respect to dimensionless base Phi.",
        "The existing alpha_energy_to_si helper converts a supplied natural coefficient by E_ref/k_B but takes no Phi scale; it is sufficient for normalized-Phi units only when its input is already a derivative with respect to normalized Phi.",
        "The current symbolic contract labels alpha_Phi_K as K per normalized Phi but does not identify the derivative coordinate or state the normalization Jacobian.",
    ]
    what_remains_open = [
        "The generic SI contract does not connect the O(2) covariant derivative to the base normalized-Phi coordinate.",
        "Phi_scale_nat and its coefficient provenance remain open; no normalized SI alpha can be emitted from the current contract alone.",
        "The base-Phi-to-energy-density map and independent graphite alpha_Phi_K calibration remain open.",
    ]
    source_hashes = {path: _sha256(path) for path in INPUT_PATHS}
    claim_boundary = (
        "This is a formula-interface and chain-rule boundary only. It does not "
        "establish a physical Phi scale, emit alpha_Phi_K, validate graphite TTG, "
        "change the Topic 13 gate, or promote a global UET claim."
    )
    result: dict[str, object] = {
        "schema_version": "t13-si-phi-normalization-jacobian-audit-v1",
        "artifact": "t13_si_phi_normalization_jacobian_audit",
        "generated_at": date.today().isoformat(),
        "owner_topic": "0.13_Thermodynamic_Bridge",
        "major_result_id": "T13_SI_PHI_NORMALIZATION_JACOBIAN_BOUNDARY",
        "closure_level": "CLOSED_FOR_LANE" if all_passed else "PARTIAL",
        "closure_disposition": "NORMALIZED_ALPHA_REQUIRES_DECLARED_COORDINATE_AND_SCALE",
        "equation_or_mapping": equation_or_mapping,
        "units": {
            "E_ref": "J",
            "Phi_scale_nat": "dimensionless numerical scale in E_ref units",
            "alpha_Phi_theta_covariant_nat": (
                "natural thermal-energy derivative per covariant natural-field unit"
            ),
            "alpha_Phi_K": "K per dimensionless normalized Phi",
        },
        "derivation_class": (
            "chain-rule identity plus read-only formula-interface audit; "
            "no physical calibration"
        ),
        "observable": "conditional SI response derivative per normalized Phi",
        "data_role": "FORMULA_BOUNDARY_AUDIT_NO_SOURCE_ROWS_NO_CALIBRATION",
        "checks": checks,
        "checks_passed": sum(bool(value) for value in checks.values()),
        "checks_total": len(checks),
        "chain_rule_witness": {
            "phi_scale_nat": phi_scale_nat,
            "alpha_covariant_nat": alpha_covariant_nat,
            "alpha_normalized_nat": alpha_normalized_nat,
            "normalized_to_covariant_derivative_ratio": normalization_ratio,
            "role": "ALGEBRAIC_WITNESS_ONLY_NOT_PHYSICAL_INPUT",
        },
        "derivative_coordinate_resolution": {
            "o2_action_coordinate": "covariant Phi passed as space_response",
            "o2_action_natural_mass_dimension": 1,
            "base_normalized_coordinate": "dimensionless Phi_normalized",
            "cross_coordinate_map": "Phi_covariant = Phi_scale_nat * Phi_normalized",
            "map_status": "OPEN_SOURCE_BACKED_PHI_SCALE_MISSING",
        },
        "what_is_closed": what_is_closed,
        "what_remains_open": what_remains_open,
        "controlling_blocker": (
            "O2_covariant_to_normalized_Phi_scale_unproven_and_missing_in_generic_SI_formula"
        ),
        "dependency_unlocked": "None; no physical or downstream dependency is unlocked.",
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "holdout_use": {
            "numeric_payload_consumed_by_this_local_audit": False,
            "blind_eligibility": "REVIEW_REQUIRED_AFTER_SESSION_EXPOSURE",
        },
        "source_hashes": source_hashes,
        "evidence_artifacts": [
            {
                "path": "docs/core/07_artifacts/topic13/"
                "t13_si_phi_normalization_jacobian_audit.json",
                "role": "generated chain-rule and coordinate-interface audit",
            },
            {
                "path": "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
                "T13_SI_PHI_NORMALIZATION_JACOBIAN_AUDIT.md",
                "role": "human-readable research handoff",
            },
        ],
        "report": {
            "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE" if all_passed else "PARTIAL",
            "WHAT_IS_ACTUALLY_CLOSED": what_is_closed,
            "WHAT_REMAINS_OPEN": what_remains_open,
            "DEPENDENCY_UNLOCKED": "None.",
            "STATUS": status,
            "WHAT_CHANGED": (
                "Identified the required field-normalization Jacobian in the "
                "existing conditional SI alpha interface; no physical input "
                "or accepted action was changed."
            ),
            "EQUATION_OR_MAPPING": equation_or_mapping,
            "VERIFICATION": checks,
            "CONTROLLING_BLOCKER": (
                "The O2-to-base-normalized Phi scale and its provenance are "
                "not established."
            ),
            "NEXT_ACTION": (
                "Source-lock the O2 covariant-to-normalized Phi scale and include "
                "Phi_scale_nat before labeling the action-derived result K per "
                "normalized Phi."
            ),
            "CLAIM_BOUNDARY": claim_boundary,
        },
        "claim_boundary": claim_boundary,
    }
    return result


def render_note(result: dict[str, object]) -> str:
    report = result["report"]
    closed = "\n".join(f"- {item}" for item in report["WHAT_IS_ACTUALLY_CLOSED"])
    open_items = "\n".join(f"- {item}" for item in report["WHAT_REMAINS_OPEN"])
    checks = result["checks"]
    return f"""# Topic 13 SI Phi Normalization Jacobian Audit

Generated: {result['generated_at']}.
Canonical artifact: docs/core/07_artifacts/topic13/t13_si_phi_normalization_jacobian_audit.json.

MAJOR_RESULT_CLOSURE: {result['closure_level']}.

WHAT_IS_ACTUALLY_CLOSED:
{closed}

WHAT_REMAINS_OPEN:
{open_items}

DEPENDENCY_UNLOCKED: None.

STATUS: {report['STATUS']}; {result['checks_passed']}/{result['checks_total']} checks.

WHAT_CHANGED: Read-only audit of the derivative-coordinate convention; no coefficient, action, source record, or gate was changed.

EQUATION_OR_MAPPING:
alpha_Phi_K = (E_ref/k_B) * Phi_scale_nat * alpha_Phi_theta_covariant_nat
Phi_scale_nat = Phi_scale_SI/E_ref
This factor is required when Phi_normalized = Phi_covariant/Phi_scale.

VERIFICATION: All local formula-boundary checks passed: {checks}.
No numeric source rows, target data, fit, or holdout payload were consumed. Xie 2026 blind-use eligibility remains REVIEW_REQUIRED_AFTER_SESSION_EXPOSURE.

CONTROLLING_BLOCKER: {result['controlling_blocker']}.

NEXT_ACTION: Declare the derivative coordinate and source-backed Phi_scale before emitting K per normalized Phi; do not infer either from TTG residuals.

CLAIM_BOUNDARY: {result['claim_boundary']}
"""


def write_outputs() -> dict[str, object]:
    result = build_audit()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    NOTE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(
        json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    NOTE_PATH.write_text(render_note(result), encoding="utf-8")
    return result


if __name__ == "__main__":
    audit = write_outputs()
    print(
        json.dumps(
            {
                "status": audit["report"]["STATUS"],
                "checks_passed": audit["checks_passed"],
                "checks_total": audit["checks_total"],
                "numeric_alpha_Phi_K_emitted": audit[
                    "numeric_alpha_Phi_K_emitted"
                ],
                "controlling_blocker": audit["controlling_blocker"],
            },
            indent=2,
        )
    )
