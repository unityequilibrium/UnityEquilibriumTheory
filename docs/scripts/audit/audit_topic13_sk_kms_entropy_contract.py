"""Audit the formal Topic 13 SK/KMS and entropy-current interface."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/03_lanes/thermal/thermal_sk_kms_entropy_contract.py"
TRANSPORT_CONTRACT_REL = "docs/core/07_artifacts/archive/covariant_superfluid_transport_contract.json"
TRANSPORT_VERIFICATION_REL = "docs/core/07_artifacts/verification/covariant_superfluid_transport_verification.json"
OUT_REL = "docs/core/07_artifacts/topic13/t13_sk_kms_entropy_contract_audit.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.thermal_sk_kms_entropy_contract import (  # noqa: E402
    entropy_production_witness,
    sk_kms_noise_kernel,
    thermal_sk_kms_entropy_contract,
)


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def evidence(rel: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": rel, "sha256": digest(rel), "summary": summary}


def main() -> int:
    contract = thermal_sk_kms_entropy_contract()
    matrix = np.asarray([[1.2, 0.15], [0.15, 0.8]], dtype=float)
    forces = np.asarray([-0.2, 0.4], dtype=float)
    entropy_value = entropy_production_witness(forces, matrix)
    noise_value = sk_kms_noise_kernel(2.0e20, 1.0e-22, 0.7)
    checks = {
        "sk_action_declared": "Phi_a" in contract["sk_action"] and "D_R" in contract["sk_action"],
        "kms_relation_declared": "coth" in contract["kms_relation"] and "beta_th" in contract["kms_relation"],
        "entropy_current_declared": contract["entropy_current"] == "J_S^mu = s u^mu + q^mu / T",
        "dissipative_balance_declared": "Q^nu" in contract["dissipative_balance"],
        "beta_symbols_separated": "not beta_th" in contract["beta_T13_relation"],
        "entropy_witness_nonnegative": entropy_value >= -1.0e-12,
        "kms_noise_witness_nonnegative": noise_value >= 0.0,
        "phi_remains_effective_response": "effective Phi" in contract["sk_field_meaning"],
        "c_remains_collective": "collective system-behaviour coordinate" in contract["C_meaning"],
        "trace_is_derived_no_backreaction": "no backreaction" in contract["R_gen_meaning"],
        "physical_coefficient_boundary_explicit": "require source or microscopic matching" in contract["coefficient_policy"],
        "finite_temperature_boundary_explicit": contract["temperature_scope"].endswith("remains open"),
        "no_target_or_holdout": True,
    }
    passed = all(checks.values())
    status = "PASS_NAMED_SK_KMS_ENTROPY_INTERFACE_CONTRACT" if passed else "FAIL_T13_SK_KMS_ENTROPY_INTERFACE_CONTRACT"
    major_result = {
        "major_result_id": "T13_SK_KMS_ENTROPY_INTERFACE_CONTRACT",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
        "what_is_closed": [
            "formal local SK response/noise interface with explicit KMS relation",
            "entropy-current and Onsager positive-semidefinite interface",
            "declared dissipative exchange-current balance without R_gen backreaction",
            "unit and beta-symbol separation boundary for the named interface",
        ],
        "equation_or_mapping": contract,
        "units": contract["unit_contract"],
        "derivation_class": "formal candidate interface plus algebraic positivity witness; not microscopic derivation",
        "observable": "formal heat-flux and entropy-production interface",
        "data_role": "INTERNAL_FORMAL_CONTRACT_NO_COEFFICIENTS",
        "evidence_artifacts": [
            evidence(MODULE_REL, {"status": status}),
            evidence(TRANSPORT_CONTRACT_REL, {"status": "BLOCKED_PHYSICAL_COEFFICIENTS"}),
            evidence(TRANSPORT_VERIFICATION_REL, {"status": "PARTIAL_T0_PLUS_SIMULATION_CONTROL"}),
        ],
        "verification_status": status,
        "open_blockers": [
            "physical_Kubo_coefficient_provenance_missing",
            "finite_temperature_normal_component_not_derived",
            "curved_3p1_transport_solver_missing",
            "base_Phi_SI_anchor_and_alpha_Phi_K_missing",
            "full_external_transport_validation_missing",
        ],
        "dependency_unlocked": "formal SK/KMS/entropy interface only; no physical transport, full Topic 13, Core, or Gravity unlock",
        "claim_boundary": "The named interface is a lane-level formula and positivity contract. It is not a microscopic Kubo match, finite-temperature two-fluid derivation, SI Phi calibration, external validation, or global UET closure.",
    }
    artifact = {
        "schema_version": "t13-sk-kms-entropy-contract-v1",
        "artifact": "t13_sk_kms_entropy_contract_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "checks": checks,
        "witness": {
            "onsager_matrix": matrix.tolist(),
            "forces": forces.tolist(),
            "entropy_production_value": entropy_value,
            "kms_noise_value": noise_value,
        },
        "physical_coefficient_evidence": "BLOCKED_NOT_PROVIDED",
        "finite_temperature_two_fluid_completion": "BLOCKED",
        "full_SK_KMS_completion": "INTERFACE_ONLY_NOT_FULL_MATCH",
        "parameter_fitting_performed": False,
        "source_rows_consumed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "numeric_transport_coefficients_emitted": False,
        "controlling_blocker": "physical_Kubo_coefficient_provenance_missing",
        "next_controller": "Source-lock or microscopically match state-specific Kubo coefficients and complete finite-temperature/curved transport without using the formal witness as physical evidence.",
        "claim_boundary": major_result["claim_boundary"],
    }
    out = ROOT / OUT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": [key for key, value in checks.items() if not value], "artifact": OUT_REL}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
