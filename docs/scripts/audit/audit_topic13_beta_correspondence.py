"""Audit the correspondence boundary between action beta and beta_T13."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from docs.core.uet_o2_beta_correspondence import (
    beta_correspondence_contract,
    scale_witness,
)


ROOT = Path(__file__).resolve().parents[3]
CURVATURE_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_normal_response_curvature_audit.json"
BETA_REL = "docs/core/07_artifacts/topic13/t13_thermal_response_beta_contract_audit.json"
PHI_ANCHOR_REL = "docs/core/07_artifacts/topic13/t13_phi_energy_anchor_identifiability_no_go.json"
MODULE_REL = "docs/core/02_equations/o2/uet_o2_beta_correspondence.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_beta_action_normalized_correspondence_no_go.json"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    curvature = load(CURVATURE_REL)
    beta = load(BETA_REL)
    phi_anchor = load(PHI_ANCHOR_REL)
    contract = beta_correspondence_contract()
    action_beta = float(curvature["reference"]["beta_action_natural"])
    beta_t13 = float(beta["synthetic_derivative_witness"]["computed"]["recovered_beta_t13_dimensionless"])
    witness_a = scale_witness(
        field_scale=1.0,
        energy_scale=1.0,
        temperature_scale=1.0,
        normalized_beta_t13=beta_t13,
        action_beta_natural=action_beta,
    )
    witness_b = scale_witness(
        field_scale=10.0,
        energy_scale=100.0,
        temperature_scale=2.0,
        normalized_beta_t13=beta_t13,
        action_beta_natural=action_beta,
    )
    checks = {
        "curvature_lane_passes": curvature["status"] == "PASS_ACTION_DERIVED_NORMAL_THERMAL_RESPONSE_CURVATURE",
        "curvature_is_natural_unit": curvature["major_result"]["units"]["unit_lane"] == "natural",
        "action_beta_has_mass_dimension_two": curvature["major_result"]["units"]["beta_action_natural"] == "natural mass dimension two",
        "beta_t13_is_dimensionless": beta["major_result"]["units"]["beta_T13"] == "dimensionless local stiffness-temperature slope",
        "beta_contract_is_candidate_not_derived": beta["major_result"]["derivation_class"].startswith("declared local finite-temperature effective-functional definition"),
        "phi_anchor_no_go_is_passing": phi_anchor["status"] == "PASS_SCOPED_NO_GO_NORMALIZED_PHI_ENERGY_ANCHOR",
        "witness_scales_are_distinct": witness_a.field_scale != witness_b.field_scale and witness_a.energy_scale != witness_b.energy_scale,
        "same_named_beta_contract_under_witnesses": witness_a.normalized_beta_t13 == witness_b.normalized_beta_t13,
        "action_beta_is_not_relabelled": witness_a.inferred_beta_t13_from_bridge is None and witness_b.inferred_beta_t13_from_bridge is None,
        "alpha_is_not_inferred": witness_a.inferred_alpha_phi_k is None and witness_b.inferred_alpha_phi_k is None,
        "no_target_or_holdout": curvature["holdout_policy"]["xie_2026_accessed"] is False and beta["xie_2026_accessed"] is False,
    }
    status = "PASS_SCOPED_NO_GO_ACTION_BETA_T13_CORRESPONDENCE" if all(checks.values()) else "FAIL_ACTION_BETA_T13_CORRESPONDENCE_AUDIT"
    evidence = [
        {"path": CURVATURE_REL, "sha256": digest(CURVATURE_REL)},
        {"path": BETA_REL, "sha256": digest(BETA_REL)},
        {"path": PHI_ANCHOR_REL, "sha256": digest(PHI_ANCHOR_REL)},
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
    ]
    report = {
        "schema_version": "t13-beta-action-normalized-correspondence-no-go-v1",
        "artifact": "t13_beta_action_normalized_correspondence_no_go",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_BETA_ACTION_NORMALIZED_CORRESPONDENCE_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the action-derived normal response slope and the named normalized beta_T13 have different declared units and derivation origins",
                "field, free-energy, and temperature scale inputs are required before a correspondence function can be evaluated",
                "two distinct positive scale completions preserve the current normalized beta contract while leaving the physical correspondence value unidentified",
                "the result does not infer alpha_Phi_K, beta_T13, e0, or a Kelvin observable",
            ],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": "scoped dimensional/normalization identifiability no-go using explicit scale witnesses",
            "observable": "correspondence boundary between action response curvature and normalized thermal functional; no physical coefficient emitted",
            "data_role": "INTERNAL_STRUCTURAL_AUDIT_NO_SOURCE_ROWS_OR_HOLDOUT",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "declared_field_normalization_and_free_energy_scale_missing",
                "natural_to_kelvin_temperature_map_missing",
                "beta_T13_source_backed_coefficient_provenance_missing",
                "independent_alpha_Phi_K_missing",
                "renormalized_finite_temperature_action_and_transport_KMS_entropy_completion_missing",
            ],
            "dependency_unlocked": "beta correspondence no-go only; no beta value, SI map, physical transport, Full Topic 13, Core, Gravity, or external-validation dependency is unlocked",
            "claim_boundary": contract["claim_boundary"],
        },
        "input_records": {
            "action_beta_natural": action_beta,
            "normalized_beta_t13_witness": beta_t13,
            "action_beta_units": curvature["major_result"]["units"]["beta_action_natural"],
            "normalized_beta_units": beta["major_result"]["units"]["beta_T13"],
        },
        "scale_witnesses": [witness_a.__dict__, witness_b.__dict__],
        "checks": {key: bool(value) for key, value in checks.items()},
        "controlling_blocker": "declared_field_normalization_free_energy_scale_and_natural_to_kelvin_beta_correspondence_missing",
        "next_controller": "Declare the missing field/free-energy/temperature normalization from a finite-temperature action or obtain an independent source-backed coefficient; then test the correspondence without using target fitting or Xie 2026.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "failed_checks": [key for key, value in checks.items() if not value],
        "closure_level": report["major_result"]["closure_level"],
    }, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
