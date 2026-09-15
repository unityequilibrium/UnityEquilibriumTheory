"""Generate Wave 4 open-system/KMS verification and dependency artifacts."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_covariant_open_system import (
    KMSCoefficientRecord, MemoryKernelRecord, OpenSystemConfig,
    derive_noise_kernel, derive_retarded_kernel, entropy_current_divergence,
    open_system_contract, open_system_evolution,
)

ARTIFACTS = ROOT / "docs/core/artifacts"


def _config() -> OpenSystemConfig:
    coefficient = KMSCoefficientRecord(
        coefficient_name="wave4_locked_onsager_control",
        value=np.array([[0.6, 0.1], [0.1, 0.4]]),
        units="natural_control_units", temperature=1.5,
        hydrodynamic_frame="Landau",
        source_path_or_url="internal://wave4-preregistered-control",
        source_hash="sha256:wave4-linear-control",
        evidence_status="SIMULATION_ONLY",
    )
    return OpenSystemConfig(
        memory=MemoryKernelRecord(np.array([0.3, 0.3]), coefficient),
        unit_lane="natural", state_metric=np.eye(2),
    )


def build_artifacts() -> tuple[dict, dict, dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    config = _config()
    negative = derive_retarded_kernel(np.array([-1.0, -1e-6]), config.memory)
    times = np.linspace(0.0, 8.0, 20001)
    kernel = derive_retarded_kernel(times, config.memory)
    integrated = np.trapezoid(kernel, times, axis=0)
    noise = derive_noise_kernel(np.linspace(-2.0, 2.0, 101), config.memory)
    rng = np.random.default_rng(20260809)
    entropy_rates = [
        entropy_current_divergence(force, config.memory.coefficient).total_rate
        for force in rng.normal(size=(100, 2))
    ]
    history = np.repeat(np.array([[0.4, -0.2]]), 100, axis=0)
    result = open_system_evolution(np.array([1.0, 0.5]), history, 0.01, config)
    metrics = {
        "pre_arrival_kernel_peak": float(np.max(np.abs(negative))),
        "kernel_normalization_max_abs": float(np.max(np.abs(integrated - config.memory.coefficient.value))),
        "kms_residual": noise.kms_residual,
        "noise_minimum_eigenvalue": noise.minimum_eigenvalue,
        "onsager_symmetry_residual": float(np.max(np.abs(config.memory.coefficient.value - config.memory.coefficient.value.T))),
        "onsager_minimum_eigenvalue": float(np.min(np.linalg.eigvalsh(config.memory.coefficient.value))),
        "minimum_entropy_production": float(min(entropy_rates)),
        "generated_trace_increment": result.generated_trace_increment,
    }
    thresholds = {
        "exact": 1e-10, "kms": 1e-8, "kernel_normalization": 2e-6,
        "positivity": -1e-12,
    }
    checks = {
        "retarded_support": metrics["pre_arrival_kernel_peak"] <= thresholds["exact"],
        "kernel_normalization": metrics["kernel_normalization_max_abs"] <= thresholds["kernel_normalization"],
        "kms_fdt": metrics["kms_residual"] <= thresholds["kms"],
        "noise_covariance_psd": metrics["noise_minimum_eigenvalue"] >= thresholds["positivity"],
        "onsager_symmetric": metrics["onsager_symmetry_residual"] <= thresholds["exact"],
        "onsager_psd": metrics["onsager_minimum_eigenvalue"] >= thresholds["positivity"],
        "entropy_nonnegative": metrics["minimum_entropy_production"] >= thresholds["positivity"],
        "trace_is_post_evolution_output": result.diagnostics["trace_used_as_input"] is False,
        "coefficient_provenance_present": bool(result.diagnostics["coefficient_provenance"]),
        "no_full_sk_overclaim": open_system_contract()["doubled_sk_action"] == "NOT_IMPLEMENTED",
    }
    passed = all(checks.values())
    verification = {
        "schema_version": "1.0", "artifact": "covariant_open_system_verification",
        "generated_at": now, "audit_status": "PASS" if passed else "FAIL",
        "research_status": "INTERNAL_LINEAR_CLASSICAL_KMS_CONTROL_ONLY",
        "unit_lane": "natural", "metrics": metrics, "thresholds": thresholds,
        "checks": checks, "contract": open_system_contract(),
        "coefficient_provenance": {
            "source": config.memory.coefficient.source_path_or_url,
            "hash": config.memory.coefficient.source_hash,
            "evidence_status": config.memory.coefficient.evidence_status,
        },
        "claim_boundary": "linear classical fluctuation-dissipation and exponential-memory constitutive control; not full Schwinger-Keldysh derivation or externally matched transport",
    }
    formula = {
        "schema_version": "1.0", "artifact": "covariant_open_system_formula_audit",
        "generated_at": now, "status": "WARN",
        "relations": [
            {"formula_id": "UET-OPEN-EXP-MEMORY-001", "relation": "K_R(t)=theta(t) exp(-t/tau)L/tau", "derivation_class": "causal constitutive ansatz", "proof_status": "support, normalization, and positivity domain checked", "unit_lane": "natural", "code_path": "docs/core/uet_covariant_open_system.py"},
            {"formula_id": "UET-OPEN-CLASSICAL-KMS-002", "relation": "N(t)=T[K_R(|t|)+K_R(|t|)^T]", "derivation_class": "classical KMS/FDT control relation", "proof_status": "internal numerical identity only", "unit_lane": "natural", "code_path": "docs/core/uet_covariant_open_system.py"},
            {"formula_id": "UET-OPEN-ENTROPY-003", "relation": "sigma_mem=z^T L^+ z >= 0 with force.z split into storage plus dissipation", "derivation_class": "extended-memory entropy ledger", "proof_status": "PSD numerical gate", "unit_lane": "natural", "code_path": "docs/core/uet_covariant_open_system.py"},
        ],
        "open_items": ["doubled-field SK action", "dynamical KMS symmetry", "microscopic influence functional", "covariant entropy current", "externally matched Kubo coefficients"],
        "claim_ceiling": "linearized classical KMS constitutive bridge",
    }
    gate = {
        "schema_version": "1.0", "artifact": "uet_main_theory_wave4_gate",
        "generated_at": now, "audit_status": "PASS" if passed else "FAIL",
        "open_system_status": "PASS_LINEAR_CLASSICAL_KMS_CONTROL_ONLY" if passed else "BLOCKED",
        "upstream_gate": "uet_main_theory_wave3_gate.json", "checks": checks,
        "controlling_blocker": "strongly_hyperbolic_curved_3p1_theory_spine_not_implemented" if passed else "open_system_positivity_or_kms_internal_failure",
        "claim_promotion": False,
        "next_controller": "define and test a first-order strongly-hyperbolic 3+1 theory-spine contract without claiming curved GR numerical validation",
    }
    addendum = {
        "schema_version": "1.0", "artifact": "uet_equation_correspondence_registry_open_system_addendum",
        "extends": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json",
        "status": "CANDIDATE_ENTRY_PENDING_MERGE",
        "equation_entries": [{
            "equation_id": "uet.main_theory.open_system_linear_kms", "version": "open-system-linear-kms-v1",
            "classification": "constitutive_lane_specific_equation", "relation_or_code_path": "docs/core/uet_covariant_open_system.py",
            "variables": {"L": "provenance-bearing Onsager matrix", "tau": "memory relaxation time", "K_R": "physical retarded memory kernel", "N": "noise covariance", "R_gen": "post-evolution derived trace"},
            "mathematical_role": "linear causal memory and classical fluctuation-dissipation bridge",
            "standard_physics_counterpart": "generalized Langevin/Maxwell memory with classical KMS fluctuation-dissipation",
            "observable_mapping": {"status": "OPEN", "reason": "coefficients are simulation-only and no dimensional detector mapping is attached"},
            "unit_lane": "natural_or_normalized_v1", "parameter_dimensions": "declared by coefficient record and lane contract",
            "source_or_origin": "UET Main-Theory Wave 4 constitutive bridge",
            "assumptions": ["linear response", "classical KMS limit", "exponential memory", "shared relaxation time for coupled sectors", "provenance-bearing coefficients"],
            "symmetry_and_conservation": "Onsager symmetry/PSD and extended entropy ledger; local covariant Q^mu integration remains open",
            "limiting_cases": ["tau to zero approaches instantaneous Onsager response distributionally", "zero coefficient removes dissipation and noise"],
            "implementation_paths": ["docs/core/uet_covariant_open_system.py"],
            "verifier_paths": ["docs/scripts/audit/audit_uet_covariant_open_system.py", "docs/core/07_artifacts/verification/covariant_open_system_verification.json", "docs/core/test/test_uet_covariant_open_system.py"],
            "evidence_class": "INTERNAL_FORMAL", "proof_status": "linear classical control passes; full SK/KMS derivation blocked",
            "downstream_dependencies": ["uet.main_theory.coarse_graining", "uet.main_theory.curved_3p1", "uet.main_theory.observables"],
            "claim_boundary": "candidate constitutive bridge, not microscopic transport derivation",
            "failure_mode": "KMS/PSD/entropy failure or generated trace used as an input state",
            "next_hardening_step": "embed physical memory in a strongly-hyperbolic covariant 3+1 spine",
        }],
    }
    return verification, formula, gate, addendum


def main() -> int:
    names = ("covariant_open_system_verification.json", "covariant_open_system_formula_audit.json", "uet_main_theory_wave4_gate.json", "uet_equation_correspondence_registry_open_system_addendum.json")
    outputs = dict(zip(names, build_artifacts()))
    for name, payload in outputs.items():
        (ARTIFACTS / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    gate = outputs["uet_main_theory_wave4_gate.json"]
    print(f"audit_status={gate['audit_status']}")
    print(f"open_system_status={gate['open_system_status']}")
    print(f"controlling_blocker={gate['controlling_blocker']}")
    return 0 if gate["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
