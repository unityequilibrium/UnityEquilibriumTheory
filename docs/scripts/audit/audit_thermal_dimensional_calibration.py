"""Audit the explicit Phi-to-kelvin calibration contract.

This closes the interface and anti-fitting rule, not the physical calibration
itself.  The output remains blocked until an independent source/calibration
record supplies a scale and uncertainty.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from core.core_paths import canonical_existing_path
from docs.core.thermal_source_observable_map import (  # noqa: E402
    ThermalPhiCalibration,
    normalized_ttg_signal,
    quasi_temperature_difference_from_calibration,
)


SOURCE_REVIEW_PATH = ROOT / "topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_thermal_source_review.json"
OUTPUT_PATH = ROOT / "core/artifacts/thermal_dimensional_calibration_contract.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(canonical_existing_path(path).read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _open_record() -> ThermalPhiCalibration:
    return ThermalPhiCalibration(
        temperature_scale_K_per_phi=None,
        uncertainty_K_per_phi=None,
        source_id="open:phi-to-kelvin-calibration",
        source_locator="not-yet-sourced",
        source_hash="NOT_AVAILABLE",
        status="EXTERNAL_CALIBRATION_REQUIRED",
        fitted=False,
        holdout_policy="LOCK_BEFORE_EXTERNAL_COMPARISON",
    )


def build_artifact() -> dict[str, Any]:
    source_review = json.loads(canonical_existing_path(SOURCE_REVIEW_PATH).read_text(encoding="utf-8-sig"))
    open_record = _open_record()
    open_record.validate()
    open_mapping = quasi_temperature_difference_from_calibration(0.25, -0.25, open_record)

    # Structural identifiability witness: a normalized Phi observable is invariant
    # under Phi -> s Phi, while alpha_Phi_K -> alpha_Phi_K / s preserves the
    # dimensional temperature response. This is an algebraic ambiguity, not a
    # request to fit a value from the target data.
    phi_peak = 0.75
    phi_valley = -0.25
    phi_initial = 1.0
    scale_witness = 7.0
    normalized_reference = normalized_ttg_signal(phi_peak, phi_valley, phi_initial)
    normalized_rescaled = normalized_ttg_signal(
        scale_witness * phi_peak,
        scale_witness * phi_valley,
        scale_witness * phi_initial,
    )
    alpha_reference = 3.5
    dimensional_reference = alpha_reference * (phi_peak - phi_valley)
    dimensional_rescaled = (alpha_reference / scale_witness) * (
        scale_witness * phi_peak - scale_witness * phi_valley
    )
    identifiability = {
        "status": "NON_IDENTIFIABLE_FROM_NORMALIZED_PHI",
        "transformation": "Delta_Phi' = s * Delta_Phi; alpha_Phi_K' = alpha_Phi_K / s",
        "witness_scale": scale_witness,
        "normalized_signal_residual": abs(normalized_reference - normalized_rescaled),
        "dimensional_response_residual": abs(dimensional_reference - dimensional_rescaled),
        "interpretation": "normalized dynamics alone cannot fix an absolute K per Phi scale; a dimensional action/energy anchor or independent calibration is required",
    }

    fitted_rejected = False
    try:
        ThermalPhiCalibration(
            temperature_scale_K_per_phi=4.0,
            uncertainty_K_per_phi=0.2,
            source_id="synthetic:fitted-forbidden",
            source_locator="synthetic://forbidden-fit",
            source_hash="synthetic-forbidden-fit",
            status="INDEPENDENTLY_CALIBRATED",
            fitted=True,
            holdout_policy="LOCK_BEFORE_EXTERNAL_COMPARISON",
        ).validate()
    except ValueError:
        fitted_rejected = True

    gates = {
        "calibration_record_schema_defined": True,
        "open_record_has_explicit_status_and_units": (
            open_record.status == "EXTERNAL_CALIBRATION_REQUIRED"
            and open_mapping is None
        ),
        "open_record_does_not_emit_kelvin": open_mapping is None,
        "physical_mapping_requires_independent_record": not open_record.physical_mapping_ready(),
        "fitted_calibration_is_rejected": fitted_rejected,
        "normalized_observable_is_scale_invariant": identifiability["normalized_signal_residual"] <= 1.0e-15,
        "absolute_scale_and_calibration_are_degenerate": identifiability["dimensional_response_residual"] <= 1.0e-15,
        "identifiability_blocker_is_explicit": identifiability["status"] == "NON_IDENTIFIABLE_FROM_NORMALIZED_PHI",
        "source_review_disallows_numeric_fitting": source_review.get("numeric_fitting_allowed") is False,
        "holdout_is_not_consumed": source_review.get("holdout_consumed") is False,
        "dimensional_map_remains_blocked": True,
    }
    required = tuple(gates)
    return {
        "schema_version": "1.0",
        "artifact": "thermal_dimensional_calibration_contract",
        "audit_status": "PASS_WITH_BLOCKED_INDEPENDENT_CALIBRATION" if all(gates[key] for key in required) else "FAIL",
        "claim_status": "CONTRACT_DEFINED_CALIBRATION_OPEN",
        "evidence_class": "INTERNAL_INTERFACE_AND_ANTI_FITTING_DIAGNOSTIC",
        "structural_identifiability": identifiability,
        "formula_audit": {
            "formula_id": "THERMAL-MAP-DIM-004",
            "relation": "Delta_Tq = alpha_Phi_K * Delta_Phi",
            "variables_and_units": "Delta_Phi normalized; Delta_Tq K; alpha_Phi_K K per normalized Phi",
            "constant_origin": "calibration_dependent_relation",
            "proof_status": "open",
            "verification_role": "prevent normalized Phi from being reported as kelvin without an independent record",
            "failure_mode": "a fitted or default gain is presented as a UET derivation",
            "next_hardening_step": "derive a dimensional Phi/energy anchor or independently calibrate alpha_Phi_K with uncertainty and a holdout protocol",
        },
        "source_review": {
            "path": _relative(SOURCE_REVIEW_PATH),
            "sha256": _sha256(SOURCE_REVIEW_PATH),
            "numeric_fitting_allowed": source_review.get("numeric_fitting_allowed"),
            "holdout_consumed": source_review.get("holdout_consumed"),
        },
        "open_calibration_record": {
            "status": open_record.status,
            "temperature_scale_K_per_phi": None,
            "uncertainty_K_per_phi": None,
            "source_id": open_record.source_id,
            "source_locator": open_record.source_locator,
            "source_hash": open_record.source_hash,
            "holdout_policy": open_record.holdout_policy,
            "physical_mapping_ready": False,
        },
        "gates": gates,
        "blockers": [
            "normalized Phi has no absolute Kelvin scale in the current lane",
            "no independently calibrated alpha_Phi_K",
            "no source-normalized local TTG numeric table with row-level uncertainty",
            "no holdout comparison after parameter/calibration lock",
            "heat flux and entropy production maps remain downstream of Tq closure",
        ],
        "claim_boundary": "The calibration interface is explicit and anti-fitting, but Phi is not temperature and no dimensional thermal claim is promoted.",
        "next_controller": "derive a dimensional Phi/energy anchor or source-lock an independent alpha_Phi_K with uncertainty; only then package TTG rows before Kelvin, heat-flux, or entropy-production claims",
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, ensure_ascii=False))
    return 0 if artifact["audit_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
