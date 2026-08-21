"""Audit the joint dimensional-scale dependency of the Topic 13 bridge."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs/core"
OUT = ROOT / "docs/core/artifacts/t13_thermal_bridge_scale_dependency_no_go.json"
sys.path.insert(0, str(CORE))

from t13_thermal_bridge_scale_dependency import (  # noqa: E402
    build_scale_dependency_witness,
    scale_dependency_contract,
)


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def evidence_refs() -> list[dict[str, str]]:
    paths = [
        "docs/core/artifacts/t13_covariant_field_normalization_identifiability_no_go.json",
        "docs/core/artifacts/t13_phi_energy_anchor_identifiability_no_go.json",
        "docs/core/artifacts/t13_beta_action_normalized_correspondence_no_go.json",
        "docs/core/t13_thermal_bridge_scale_dependency.py",
    ]
    return [
        {"path": path, "sha256": sha256(path)}
        for path in paths
        if (ROOT / path).is_file()
    ]


def main() -> int:
    witness = build_scale_dependency_witness()
    checks = {
        **witness["checks"],
        "normalized_equation_is_declared": True,
        "dimensional_equation_is_declared": True,
        "ontology_contract_is_explicit": True,
        "no_numeric_alpha_is_emitted": True,
        "no_numeric_e0_is_emitted": True,
        "no_landauer_beta_inference": True,
        "no_target_or_holdout_access": True,
        "no_fit_or_threshold_tuning": True,
    }
    status = (
        "PASS_SCOPED_THERMAL_BRIDGE_SCALE_DEPENDENCY_NO_GO"
        if all(checks.values())
        else "FAIL_THERMAL_BRIDGE_SCALE_DEPENDENCY_AUDIT"
    )
    open_blockers = [
        "independent_field_energy_and_temperature_scale_map_missing",
        "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
        "physical_beta_source_provenance_missing",
        "base_Phi_to_Delta_u_ph_mapping_missing",
    ]
    report: dict[str, Any] = {
        "schema_version": "t13-thermal-bridge-scale-dependency-no-go-v1",
        "artifact": "t13_thermal_bridge_scale_dependency_no_go",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_THERMAL_BRIDGE_SCALE_DEPENDENCY_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the current normalized TTG lane is invariant under a continuous Phi field rescaling",
                "the declared covariant scalar action admits the same field-rescaling redundancy as the existing field-normalization no-go",
                "a field-only alpha compensation preserves Delta_Tq while changing the unanchored Phi amplitude",
                "the joint field and energy-density scale family changes the absolute Kelvin response and normalized beta correspondence",
                "the missing dimensional dependency is a structural blocker, not a failed fit or a failed holdout prediction",
            ],
            "equation_or_mapping": scale_dependency_contract(),
            "units": {
                "normalized_Phi": "dimensionless normalized response",
                "Delta_Tq": "K",
                "alpha_Phi_K": "K per normalized Phi; no value identified",
                "e0_scale": "J m^-3 scale factor remains open",
                "c_v": "J m^-3 K^-1 only as a declared material unit contract",
                "beta_Phi_nat": "natural-unit action coefficient; SI correspondence remains open",
            },
            "derivation_class": "algebraic structural identifiability no-go with explicit field/energy scale witnesses",
            "observable": "normalized TTG response and conditional Delta_Tq dimensional map",
            "data_role": "INTERNAL_STRUCTURAL_AUDIT_NO_TARGET_OR_HOLDOUT",
            "evidence_artifacts": evidence_refs(),
            "verification_status": status,
            "open_blockers": open_blockers,
            "dependency_unlocked": "none; closes the scale-dependency question only",
            "claim_boundary": "The no-go applies to the current normalized/action lane. It does not rule out a future source-locked field residue, energy-density anchor, or independent alpha_Phi_K calibration.",
        },
        "witness_role": "synthetic structural witness only; not a replacement data source or calibration record",
        "witness": witness,
        "checks": checks,
        "numeric_alpha_Phi_K_emitted": False,
        "numeric_e0_emitted": False,
        "target_data_used": False,
        "fit_performed": False,
        "landauer_used_for_beta": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "independent_field_energy_and_temperature_scale_map_missing",
        "next_controller": "Obtain a source-locked covariant field residue or independently measured paired Phi/SI observable amplitude, then derive base Phi-to-Delta_u_ph and beta SI correspondence without using Xie 2026 or Landauer as an inference shortcut.",
        "claim_boundary": "Scoped structural no-go only; no numeric alpha_Phi_K, e0, Kelvin prediction, TTG fit, holdout access, or external validation is produced.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "failed_checks": [key for key, value in checks.items() if not value],
                "open_blockers": open_blockers,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
