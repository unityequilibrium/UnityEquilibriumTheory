"""Audit whether the canonical Topic 13 inputs already contain a SI Phi anchor."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs/core/artifacts/t13_base_phi_registry_completeness_audit.json"

ACTIVE_LANE = "docs/core/artifacts/uet_active_lane_units_observable_register.json"
ALPHA_AUDIT = "docs/core/artifacts/t13_alpha_phi_k_calibration_candidate_audit.json"
CALIBRATION_REQUIREMENT = (
    "docs/core/artifacts/t13_base_phi_independent_calibration_requirement.json"
)
PHI_ANCHOR_BOUNDARY = (
    "docs/core/artifacts/t13_phi_si_anchor_public_source_boundary_audit.json"
)
SI_CONVERSION = "docs/core/thermal_covariant_action_si_conversion.py"
ENERGY_BRIDGE = "docs/core/thermal_energy_response_bridge.py"
DIMENSIONAL_BRIDGE = "docs/core/thermal_dimensional_bridge.py"


EVIDENCE_PATHS = [
    ACTIVE_LANE,
    ALPHA_AUDIT,
    CALIBRATION_REQUIREMENT,
    PHI_ANCHOR_BOUNDARY,
    SI_CONVERSION,
    ENERGY_BRIDGE,
    DIMENSIONAL_BRIDGE,
]


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    active = read_json(ACTIVE_LANE)
    alpha = read_json(ALPHA_AUDIT)
    requirement = read_json(CALIBRATION_REQUIREMENT)
    anchor_boundary = read_json(PHI_ANCHOR_BOUNDARY)
    si_conversion_text = (ROOT / SI_CONVERSION).read_text(encoding="utf-8")
    energy_bridge_text = (ROOT / ENERGY_BRIDGE).read_text(encoding="utf-8")
    dimensional_bridge_text = (ROOT / DIMENSIONAL_BRIDGE).read_text(encoding="utf-8")

    thermal_lane = next(
        lane for lane in active["lanes"] if lane["lane_id"] == "thermal_ttg_observable_bridge"
    )
    checks = {
        "canonical_thermal_lane_loaded": thermal_lane["unit_lane"]
        == "normalized_plus_external_K_contract_open",
        "phi_declared_normalized": thermal_lane["variables"]["Phi"]
        == "normalized effective response variable",
        "alpha_declared_open": thermal_lane["variables"]["alpha_Phi_K"]
        == "open scale in K per normalized Phi",
        "thermal_lane_blocks_si_units": thermal_lane["units_status"]
        == "BLOCKED_INDEPENDENT_ALPHA_Phi_K",
        "si_conversion_requires_external_scale": all(
            token in si_conversion_text
            for token in ("E_ref [J] is an explicit external/provenance input", "Phi_scale", "e0")
        ),
        "base_phi_identity_not_asserted": "base_Phi_identity" in energy_bridge_text
        and "not asserted" in energy_bridge_text,
        "base_phi_to_energy_map_open": "OPEN_DERIVATION_OR_CALIBRATION" in energy_bridge_text,
        "conditional_e0_not_a_source": "e0_J_per_m3: float | None = None" in dimensional_bridge_text,
        "no_eligible_numeric_alpha_record": alpha["eligible_candidate_count"] == 0
        and alpha["numeric_alpha_Phi_K_emitted"] is False,
        "independent_calibration_remains_open": requirement["status"]
        == "PASS_OPEN_CALIBRATION_REQUIREMENT",
        "public_anchor_boundary_has_no_pair": anchor_boundary["checks"][
            "paired_base_phi_si_record_absent"
        ],
        "holdout_not_used": alpha["holdout_accessed"] is False
        and alpha["target_fit_performed"] is False,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"Topic 13 base-Phi registry audit failed: {failed}")

    evidence = [
        {"path": path, "sha256": sha256(path)} for path in EVIDENCE_PATHS
    ]
    payload = {
        "schema_version": "t13-base-phi-registry-completeness-v1",
        "artifact": "t13_base_phi_registry_completeness_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_NO_HIDDEN_SI_ANCHOR",
        "major_result": {
            "major_result_id": "T13_BASE_PHI_REGISTRY_COMPLETENESS_AUDIT",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "The canonical thermal lane explicitly declares Phi as normalized and alpha_Phi_K as open.",
                "The canonical SI conversion route exposes E_ref and Phi_scale as external inputs rather than hidden constants.",
                "The canonical bridge code does not assert base Phi equals the named energy-response coordinate Phi_E.",
                "No eligible non-holdout numeric alpha record or public paired base-Phi SI anchor is present in the audited inputs.",
            ],
            "equation_or_mapping": {
                "normalized_observable": "y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)",
                "dimensional_observable": "Delta_Tq = alpha_Phi_K * Delta_Phi",
                "si_conversion": "alpha_Phi_K = (E_ref/k_B) * alpha_Phi_theta",
                "named_energy_branch": "Phi_E = Delta_u/e0; base Phi to Phi_E map remains open",
            },
            "units": {
                "Phi": "dimensionless normalized response",
                "Delta_Tq": "K only after independent mapping",
                "alpha_Phi_K": "K per normalized Phi; no numeric value emitted",
                "E_ref": "J; external/provenance input",
                "Phi_scale": "explicit field normalization input; not supplied",
                "e0": "J m^-3; open input",
            },
            "derivation_class": "canonical registry completeness and provenance boundary audit",
            "observable": "normalized TTG response and conditional thermal response operator",
            "data_role": "INTERNAL_AUDIT_NO_TARGET_OR_HOLDOUT",
            "evidence_artifacts": evidence,
            "verification_status": "PASS_SCOPED_NO_HIDDEN_SI_ANCHOR",
            "open_blockers": [
                "base_phi_si_anchor",
                "independent_alpha_record",
                "normalized_beta_si_map",
                "physical_source_backed_eos",
                "physical_heat_flux_entropy_map",
            ],
            "dependency_unlocked": "None; this audit closes only registry completeness, not the physical dimensional lane.",
            "claim_boundary": "This result rules out a hidden canonical SI anchor in the audited inputs. It does not prove that a future action-derived or independently calibrated anchor is impossible and does not close Full Topic 13.",
        },
        "checks": checks,
        "searched_canonical_inputs": EVIDENCE_PATHS,
        "controlling_blocker": "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing",
        "next_controller": "Obtain a declared dimensionful action/free-energy anchor or an independent paired base-Phi/SI response record; do not fit the anchor to TTG residuals or read Xie 2026.",
        "claim_boundary": "Scoped negative audit only; no numeric alpha_Phi_K, e0, or SI Phi map is emitted.",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": str(OUTPUT.relative_to(ROOT)),
                "evidence_count": len(evidence),
                "numeric_alpha_emitted": False,
                "holdout_used": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
