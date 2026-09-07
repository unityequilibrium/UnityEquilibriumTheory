"""Build the Topic 13 formal thermodynamic bridge integration artifact."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from docs.core.thermal_collective_response_eos import collective_response_eos_contract
from docs.core.thermal_sk_kms_entropy_contract import thermal_sk_kms_entropy_contract
from docs.core.t13_formal_thermodynamic_bridge_integration import (
    formal_thermodynamic_bridge_witness,
)
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import (
    covariant_entropy_heat_flux_balance_contract,
)
OUT = ROOT / "docs/core/artifacts/t13_formal_thermodynamic_bridge_integration_audit.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence(path: Path, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": rel(path), "sha256": sha256(path), "summary": summary}


def main() -> int:
    witness = formal_thermodynamic_bridge_witness()
    eos_contract = collective_response_eos_contract()
    sk_contract = thermal_sk_kms_entropy_contract()
    heat_contract = covariant_entropy_heat_flux_balance_contract()
    evidence_paths = [
        ROOT / "docs/core/t13_formal_thermodynamic_bridge_integration.py",
        ROOT / "docs/core/thermal_collective_response_eos.py",
        ROOT / "docs/core/thermal_sk_kms_entropy_contract.py",
        ROOT / "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py",
        ROOT / "docs/core/artifacts/t13_collective_response_eos_stability_audit.json",
        ROOT / "docs/core/artifacts/t13_sk_kms_entropy_contract_audit.json",
        ROOT / "docs/core/artifacts/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json",
    ]
    artifact = {
        "schema_version": "t13-formal-thermodynamic-bridge-integration-v1",
        "artifact": "t13_formal_thermodynamic_bridge_integration_audit",
        "generated_at": date.today().isoformat(),
        "status": witness["status"] if witness["all_checks_pass"] else "FAIL_FORMAL_T13_THERMODYNAMIC_BRIDGE_INTEGRATION",
        "major_result": {
            "major_result_id": "T13_FORMAL_THERMODYNAMIC_BRIDGE_INTEGRATION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if witness["all_checks_pass"] else "OPEN",
            "what_is_closed": [
                "cross-module composition of the named normalized EOS derivative and stability contract",
                "formal SK/KMS noise relation and Onsager entropy-positivity interface connected to the EOS lane",
                "covariant finite-cutoff heat-flux, entropy-current, and conserved dissipative-balance interface",
                "shared ontology, beta-symbol separation, and claim boundary across the formal bridge",
            ],
            "what_remains_open": [
                "physical charge-density EOS and source-backed finite-temperature coefficients",
                "microscopic finite-temperature SK/KMS matching and physical Kubo coefficients",
                "SI Phi normalization, independent alpha_Phi_K, and TTG source mapping",
                "curved 3+1 transport and external thermal validation",
            ],
            "equation_or_mapping": witness["equations"],
            "units": witness["units"],
            "derivation_class": "cross-module formal interface integration with algebraic positivity and covariance witnesses; not a microscopic derivation",
            "observable": "formal local heat-flux response, entropy-production scalar, and conserved dissipative-balance interface",
            "data_role": "INTERNAL_FORMAL_INTEGRATION_NO_SOURCE_ROWS_NO_HOLDOUT",
            "evidence_artifacts": [
                evidence(path, {"role": "implementation_or_prior_lane", "status": "HASH_LOCKED"})
                for path in evidence_paths
            ],
            "verification_status": witness["status"],
            "open_blockers": [
                "physical_Kubo_coefficient_record_missing",
                "eos_transport_kms_entropy_completion_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "formal EOS-to-SK/KMS-to-entropy-to-heat-flux interface only; no full Topic 13, Core, Gravity, or external unlock",
            "claim_boundary": (
                "This closes only the cross-module formal thermodynamic bridge on the declared "
                "normalized/natural-unit lane. It is not a physical charge EOS, SI transport "
                "coefficient, alpha_Phi_K calibration, TTG validation, curved 3+1 result, or "
                "Full Topic 13 closure."
            ),
        },
        "contract_inputs": {
            "eos": eos_contract,
            "sk_kms": sk_contract,
            "covariant_entropy_heat_flux": heat_contract,
        },
        "checks": witness["checks"],
        "witness": witness["witness"],
        "physical_coefficient_evidence": "BLOCKED_NOT_PROVIDED",
        "finite_temperature_two_fluid_completion": "BLOCKED",
        "full_SK_KMS_completion": "INTERFACE_ONLY_NOT_FULL_MATCH",
        "numeric_transport_coefficients_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "source_rows_consumed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "full_core_unlock": False,
        "controlling_blocker": "physical_Kubo_coefficient_record_missing",
        "next_controller": (
            "Provide an admissible physical Kubo or microscopic transport match and an "
            "independent Phi/SI calibration without reading the locked holdout."
        ),
        "claim_boundary": (
            "Formal bridge integration only; no physical transport, SI calibration, TTG "
            "prediction, external validation, or global UET closure."
        ),
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "closure_level": artifact["major_result"]["closure_level"], "artifact": rel(OUT)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
