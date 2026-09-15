"""Audit the Topic 13 transport/KMS/entropy status boundary.

The artifact separates structural/formal lane closures from the physical
coefficient and finite-temperature evidence still required by the full gate.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT_REL = "docs/core/07_artifacts/topic13/t13_transport_kms_entropy_status_boundary_audit.json"

SOURCE_RELS = {
    "transport_identifiability": "docs/core/07_artifacts/topic13/t13_transport_coefficient_identifiability_no_go.json",
    "formal_sk_kms_entropy": "docs/core/07_artifacts/topic13/t13_sk_kms_entropy_contract_audit.json",
    "open_system_sk_kms": "docs/core/07_artifacts/topic13/t13_uet_o2_open_system_sk_kms_audit.json",
    "covariant_entropy_heat_flux": "docs/core/07_artifacts/topic13/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json",
    "physical_kubo_gate": "docs/core/07_artifacts/topic13/t13_physical_kubo_coefficient_provenance_audit.json",
    "transport_verification": "docs/core/07_artifacts/verification/covariant_superfluid_transport_verification.json",
}


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def evidence(relative: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": relative, "sha256": digest(relative), "summary": summary}


def main() -> int:
    sources = {key: load(relative) for key, relative in SOURCE_RELS.items()}
    transport_no_go = sources["transport_identifiability"]
    formal_contract = sources["formal_sk_kms_entropy"]
    open_system = sources["open_system_sk_kms"]
    covariant_balance = sources["covariant_entropy_heat_flux"]
    physical_kubo = sources["physical_kubo_gate"]
    transport_verification = sources["transport_verification"]

    checks = {
        "conservative_action_identifiability_no_go_passes": (
            transport_no_go.get("status") == "PASS_SCOPED_NO_GO_CONSERVATIVE_ACTION_KUBO_IDENTIFIABILITY"
            and transport_no_go.get("major_result", {}).get("closure_level") == "CLOSED_AS_NO_GO"
        ),
        "formal_sk_kms_entropy_interface_passes": (
            formal_contract.get("status") == "PASS_NAMED_SK_KMS_ENTROPY_INTERFACE_CONTRACT"
            and formal_contract.get("major_result", {}).get("closure_level") == "CLOSED_FOR_LANE"
        ),
        "formal_open_system_sk_kms_lane_passes": (
            open_system.get("status") == "PASS_FORMAL_OPEN_SYSTEM_SK_KMS_ENTROPY_LANE"
            and open_system.get("major_result", {}).get("closure_level") == "CLOSED_FOR_LANE"
        ),
        "natural_covariant_entropy_balance_lane_passes": (
            covariant_balance.get("status") == "PASS_ACTION_DERIVED_COVARIANT_ENTROPY_HEAT_FLUX_BALANCE_LANE"
            and covariant_balance.get("major_result", {}).get("closure_level") == "CLOSED_FOR_LANE"
        ),
        "physical_kubo_admission_boundary_is_explicit": (
            physical_kubo.get("status") == "PASS_KUBO_PROVENANCE_GATE_OPEN_PHYSICAL_COEFFICIENT"
            and physical_kubo.get("major_result", {}).get("closure_level") == "CLOSED_FOR_LANE"
            and physical_kubo.get("controlling_blocker") == "physical_Kubo_coefficient_record_missing"
        ),
        "physical_coefficient_is_not_emitted": (
            transport_verification.get("physical_coefficient_evidence") == "BLOCKED_NOT_PROVIDED"
        ),
        "finite_temperature_normal_sector_is_not_promoted": (
            transport_verification.get("finite_temperature_two_fluid_completion") == "BLOCKED"
        ),
        "full_sk_kms_match_is_not_promoted": (
            transport_verification.get("full_SK_KMS_completion") == "BLOCKED"
        ),
        "no_physical_result_flags_are_present": (
            open_system.get("checks", {}).get("no_parameter_fitting") is True
            and open_system.get("checks", {}).get("no_target_or_holdout") is True
            and transport_no_go.get("checks", {}).get("no_holdout_or_fit") is True
            and formal_contract.get("checks", {}).get("no_target_or_holdout") is True
        ),
        "ontology_boundary_is_preserved": (
            transport_no_go.get("checks", {}).get("C_ontology_is_preserved") is True
            and transport_no_go.get("checks", {}).get("Phi_ontology_is_preserved") is True
            and transport_no_go.get("checks", {}).get("R_gen_has_no_feedback") is True
            and formal_contract.get("checks", {}).get("phi_remains_effective_response") is True
            and formal_contract.get("checks", {}).get("c_remains_collective") is True
            and formal_contract.get("checks", {}).get("trace_is_derived_no_backreaction") is True
        ),
    }

    status = "PASS_SCOPED_TRANSPORT_KMS_ENTROPY_STATUS_BOUNDARY" if all(checks.values()) else "FAIL_TRANSPORT_KMS_ENTROPY_STATUS_BOUNDARY"
    major_result = {
        "major_result_id": "T13_TRANSPORT_KMS_ENTROPY_STATUS_BOUNDARY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
        "what_is_closed": [
            "the conservative single-copy action is shown not to identify a unique physical dissipative/Kubo sector",
            "formal local and open-system SK/KMS/FDT interfaces are named and kept separate from microscopic matching",
            "the natural-unit covariant heat-flux, entropy-current, and conserved dissipative-balance lane is verified",
            "the physical Kubo admission boundary requires state, units, correlator locator, source identity, and hash",
            "the absence of a physical coefficient, finite-temperature normal sector, and full SK/KMS match is machine-readable",
        ] if status.startswith("PASS") else [],
        "equation_or_mapping": {
            "dissipative_response": "J_diss^A = -L^(AB) X_B",
            "entropy_production": "nabla_mu J_S^mu = X_A L^(AB) X_B >= 0",
            "sk_kms": "N(omega) = coth(beta_th omega / 2) * 2 Im D_R(omega)",
            "heat_flux": "q^mu = kappa_natural * X_T^mu; J_S^mu = s*u^mu + q^mu/T",
            "physical_admission": "KuboCoefficientRecord -> constitutive coefficient only after matched physical evidence",
        },
        "units": {
            "formal_lane": "natural units and declared local SI interface",
            "physical_coefficient": "coefficient-specific source-declared units required",
            "physical_temperature": "K or source-declared equivalent with conversion contract",
            "physical_heat_flux": "W m^-2 only after dimensional and source matching",
        },
        "derivation_class": "structural identifiability no-go plus formal SK/KMS/entropy and natural-unit balance boundary; no physical coefficient derivation",
        "observable": "transport/KMS/entropy closure state and physical-evidence admission boundary",
        "data_role": "INTERNAL_STATUS_BOUNDARY_NO_PHYSICAL_TRANSPORT_EVIDENCE",
        "evidence_artifacts": [
            evidence(relative, {"role": key, "status": sources[key].get("status")})
            for key, relative in SOURCE_RELS.items()
        ],
        "verification_status": status,
        "open_blockers": [
            "physical_Kubo_coefficient_record_missing",
            "finite_temperature_normal_component_not_derived",
            "microscopic_interacting_SK_match_missing",
            "dimensional_Phi_to_thermal_observable_map_missing",
            "curved_3p1_transport_solver_missing",
        ],
        "dependency_unlocked": "structural/formal transport, KMS, entropy, and heat-flux lane only; no physical transport, Full Topic 13, Core, Gravity, or external-validation unlock",
        "claim_boundary": "This closes the transport/KMS/entropy status boundary and scoped formal lanes only. It does not provide a physical Kubo coefficient, complete finite-temperature two-fluid transport, SI Phi calibration, TTG prediction, external validation, or Full Topic 13 closure.",
    }
    artifact = {
        "schema_version": "t13-transport-kms-entropy-status-boundary-v1",
        "artifact": "t13_transport_kms_entropy_status_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "checks": checks,
        "physical_closure_status": "BLOCKED",
        "controlling_blocker": "physical_Kubo_coefficient_record_missing",
        "next_controller": "Obtain a state-matched physical Kubo record or a microscopic interacting SK/influence-functional match, then complete the finite-temperature normal sector and dimensional Phi-to-thermal map without using synthetic controls or the locked holdout.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "used_for_fit": False,
            "used_for_tuning": False,
            "used_for_calibration": False,
        },
    }
    (ROOT / OUT_REL).write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "major_result_id": major_result["major_result_id"], "controlling_blocker": artifact["controlling_blocker"], "artifact": OUT_REL}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
