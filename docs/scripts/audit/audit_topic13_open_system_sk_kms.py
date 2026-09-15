"""Audit the formal Topic 13 open-system SK/KMS lane."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/uet_o2_open_system_sk_kms.py"
OUT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_open_system_sk_kms_audit.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_open_system_sk_kms import (  # noqa: E402
    OpenSystemParameters,
    formal_entropy_production,
    kms_correlators,
    noise_kernel,
    open_system_sk_contract,
    retarded_kernel,
    retarded_poles,
)


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def evidence(relative: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": relative, "sha256": digest(relative), "summary": summary}


def main() -> int:
    parameters = OpenSystemParameters(beta_th=4.0, kappa=1.2, chi=0.8, gamma=0.3)
    frequencies = np.asarray([0.15, 0.4, 0.9, 1.7, 2.6], dtype=float)
    records: list[dict[str, float | bool]] = []
    for omega in frequencies:
        kernel = retarded_kernel(float(omega), parameters)
        correlators = kms_correlators(float(omega), parameters)
        noise = noise_kernel(float(omega), parameters)
        records.append(
            {
                "omega": float(omega),
                "retarded_real": float(kernel.real),
                "retarded_imag": float(kernel.imag),
                "rho": correlators["rho"],
                "greater": correlators["greater"],
                "lesser": correlators["lesser"],
                "kms_ratio": correlators["kms_ratio"],
                "kms_target": correlators["kms_target"],
                "noise": noise,
                "fdt_residual": float(noise - correlators["noise"]),
                "spectral_positivity": correlators["rho"] >= 0.0,
            }
        )

    poles = retarded_poles(parameters)
    temperature = 1.0 / parameters.beta_th
    velocities = np.asarray([0.0, 0.3, -0.7, 1.1], dtype=float)
    entropy_values = [
        formal_entropy_production(float(velocity), temperature, parameters)
        for velocity in velocities
    ]
    contract = open_system_sk_contract()
    max_kms_residual = max(
        abs(row["kms_ratio"] - row["kms_target"]) / row["kms_target"]
        for row in records
    )
    max_fdt_residual = max(abs(row["fdt_residual"]) for row in records)
    checks = {
        "sk_action_declared": "Phi_a" in contract["sk_action"] and "K_R" in contract["sk_action"],
        "local_retarded_kernel_declared": "- i gamma omega" in contract["retarded_kernel"],
        "retarded_poles_in_lower_half_plane": bool(np.max(np.imag(poles)) <= 1.0e-12),
        "spectral_density_nonnegative": all(bool(row["spectral_positivity"]) for row in records),
        "damping_sign_nonnegative": all(
            float(row["retarded_imag"]) <= 1.0e-12 for row in records
        ),
        "kms_ratio_residual": bool(max_kms_residual <= 2.0e-12),
        "fdt_noise_residual": bool(max_fdt_residual <= 2.0e-12),
        "noise_kernel_nonnegative": all(float(row["noise"]) >= 0.0 for row in records),
        "entropy_production_nonnegative": all(value >= -1.0e-12 for value in entropy_values),
        "equilibrium_entropy_production_zero": abs(entropy_values[0]) <= 1.0e-12,
        "formal_parameters_not_physical_kubo": "verifier parameters only" in contract["coefficient_policy"],
        "phi_remains_effective_response": "effective response variable" in contract["ontology"]["Phi"],
        "c_remains_collective": "collective system-behaviour coordinate" in contract["ontology"]["C"],
        "r_gen_remains_derived": "derived history trace" in contract["ontology"]["R_gen"],
        "no_source_rows_consumed": True,
        "no_parameter_fitting": True,
        "no_target_or_holdout": True,
    }
    passed = all(checks.values())
    status = "PASS_FORMAL_OPEN_SYSTEM_SK_KMS_ENTROPY_LANE" if passed else "FAIL_FORMAL_OPEN_SYSTEM_SK_KMS_ENTROPY_LANE"
    major_result = {
        "major_result_id": "T13_UET_O2_OPEN_SYSTEM_SK_KMS_ENTROPY_LANE",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
        "what_is_closed": [
            "local doubled-field SK action with an explicit retarded dissipative kernel",
            "positive spectral density and lower-half-plane retarded poles for the declared ansatz",
            "greater/lesser KMS ratio and fluctuation-dissipation noise identity",
            "formal nonnegative entropy-production witness with an equilibrium zero limit",
        ],
        "equation_or_mapping": contract,
        "units": contract["unit_contract"],
        "derivation_class": "formal local open-system ansatz plus algebraic KMS/FDT and positivity verification; not microscopic derivation",
        "observable": "formal dissipative response, noise, and entropy-production witness",
        "data_role": "INTERNAL_FORMAL_SYNTHETIC_CONTROL_NO_SOURCE",
        "evidence_artifacts": [
            evidence(MODULE_REL, {"status": status}),
            evidence(
                "docs/scripts/audit/audit_topic13_open_system_sk_kms.py",
                {"status": status, "record_count": len(records)},
            ),
        ],
        "verification_status": status,
        "open_blockers": [
            "microscopic_interacting_SK_match_missing",
            "physical_Kubo_coefficient_provenance_missing",
            "base_Phi_SI_anchor_and_alpha_Phi_K_missing",
            "TTG_material_state_mapping_missing",
        ],
        "dependency_unlocked": "formal open-system SK/KMS/entropy lane only; physical transport, full Topic 13, Core, Gravity, and Galaxy remain blocked",
        "claim_boundary": "This closes only a declared formal open-system KMS/FDT and entropy-positivity lane. It is not a microscopic interacting match, physical Kubo coefficient, SI Phi calibration, TTG prediction, external validation, or global UET closure.",
    }
    artifact = {
        "schema_version": "t13-open-system-sk-kms-v1",
        "artifact": "t13_uet_o2_open_system_sk_kms_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "checks": checks,
        "parameters": {
            "beta_th": parameters.beta_th,
            "kappa": parameters.kappa,
            "chi": parameters.chi,
            "gamma": parameters.gamma,
            "temperature_formal": temperature,
        },
        "records": records,
        "retarded_poles": [
            {"real": float(pole.real), "imag": float(pole.imag)} for pole in poles
        ],
        "entropy_production_values": entropy_values,
        "physical_kubo_coefficient_emitted": False,
        "si_mapping_emitted": False,
        "source_rows_consumed": False,
        "target_data_used": False,
        "parameter_fitting_performed": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "microscopic_interacting_SK_match_and_physical_Kubo_provenance_missing",
        "next_controller": "Obtain a state-matched microscopic or source-locked retarded correlator with units and uncertainty; do not promote formal gamma or noise to physical transport or alpha calibration.",
        "claim_boundary": major_result["claim_boundary"],
    }
    out = ROOT / OUT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "failed_checks": [key for key, value in checks.items() if not value],
                "max_kms_relative_residual": max_kms_residual,
                "max_fdt_residual": max_fdt_residual,
                "artifact": OUT_REL,
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
