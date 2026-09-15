"""Audit the implemented boundary of the Topic 13 covariant transport lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TRANSPORT_REL = "docs/core/uet_covariant_superfluid_transport.py"
CONTRACT_REL = "docs/core/07_artifacts/archive/covariant_superfluid_transport_contract.json"
VERIFICATION_REL = "docs/core/07_artifacts/verification/covariant_superfluid_transport_verification.json"
TEST_REL = "docs/core/test/test_covariant_superfluid_transport.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_covariant_transport_implementation_boundary_audit.json"


def load(rel: str) -> dict:
    value = json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def main() -> int:
    source = (ROOT / TRANSPORT_REL).read_text(encoding="utf-8-sig")
    test = (ROOT / TEST_REL).read_text(encoding="utf-8-sig")
    contract = load(CONTRACT_REL)
    verification = load(VERIFICATION_REL)
    core = contract["core_contract"]
    eos = contract["eos_contract"]
    gates = verification["gates"]

    checks = {
        "contract_is_explicitly_blocked": contract["status"] == "BLOCKED",
        "interface_gate_passes": contract["interface_status"] == "PASS",
        "t0_pure_superfluid_scope_is_declared": core["temperature_scope"] == "T_ZERO_PURE_SUPERFLUID_ONLY",
        "normal_component_is_not_derived": core["normal_component"] == "OPEN_NOT_DERIVED",
        "dissipative_values_require_external_or_microscopic_match": core["transport_values"] == "REQUIRED_EXTERNAL_OR_MICROSCOPIC_MATCH_NO_DEFAULTS",
        "synthetic_controls_are_opt_in_only": core["synthetic_controls"] == "EXPLICIT_OPT_IN_SIMULATION_ONLY",
        "natural_unit_lane_is_declared": core["unit_lane"] if "unit_lane" in core else eos["unit_lane"] == "natural",
        "si_lane_is_blocked": core["si_lane"] == "BLOCKED",
        "curved_solver_is_not_implemented": core["curved_3p1_solver"] == "NOT_IMPLEMENTED",
        "full_tensor_is_deferred": core["full_superfluid_transport_tensor"] == "DEFERRED",
        "finite_temperature_code_path_is_rejected": '"the action-derived v1 EOS is T=0; a normal finite-temperature component is open"' in source,
        "missing_coefficient_has_no_default": '"missing KuboCoefficientRecord for {coefficient_name!r}; no default is allowed"' in source,
        "synthetic_control_requires_explicit_opt_in": "config.allow_synthetic_controls" in source,
        "trace_is_not_state_or_feedback": core["trace_input"] is False and core["trace_backreaction"] is False,
        "eos_is_tree_level_finite_density_mean_field": eos["status"] == "TREE_LEVEL_FINITE_DENSITY_O2_MEAN_FIELD_DERIVATION",
        "finite_temperature_eos_is_not_derived": eos["finite_temperature_normal_component"] == "NOT_DERIVED",
        "transport_not_derived_from_conservative_action": eos["transport_coefficients"] == "NOT_DERIVED_FROM_CONSERVATIVE_ACTION",
        "ideal_and_entropy_verification_gates_pass": all(gates[name] for name in (
            "projector", "josephson", "ideal_current_stress", "lorentz_covariance", "entropy_sign", "goldstone_sound", "causal_speed",
        )),
        "missing_provenance_blocks": verification["metrics"]["missing_provenance_blocked"] is True and gates["missing_provenance_blocks"] is True,
        "finite_temperature_two_fluid_is_blocked": verification["finite_temperature_two_fluid_completion"] == "BLOCKED",
        "full_sk_kms_is_blocked": verification["full_SK_KMS_completion"] == "BLOCKED",
        "physical_coefficient_is_not_emitted": verification["physical_coefficient_evidence"] == "BLOCKED_NOT_PROVIDED",
        "tests_encode_the_same_boundary": 'with pytest.raises(NotImplementedError, match="T=0")' in test and 'with pytest.raises(RuntimeError, match="no default")' in test,
    }
    status = "PASS_CLOSED_TRANSPORT_IMPLEMENTATION_BOUNDARY" if all(checks.values()) else "FAIL_TRANSPORT_IMPLEMENTATION_BOUNDARY"
    evidence = [
        {"path": TRANSPORT_REL, "sha256": digest(TRANSPORT_REL)},
        {"path": CONTRACT_REL, "sha256": digest(CONTRACT_REL)},
        {"path": VERIFICATION_REL, "sha256": digest(VERIFICATION_REL)},
        {"path": TEST_REL, "sha256": digest(TEST_REL)},
    ]
    report = {
        "schema_version": "t13-covariant-transport-implementation-boundary-v1",
        "artifact": "t13_covariant_transport_implementation_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_COVARIANT_TRANSPORT_IMPLEMENTATION_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the implemented covariant transport lane is bounded to a natural-unit Landau-frame T=0 pure-superfluid ideal sector",
                "the dissipative sector is a minimal longitudinal Kubo interface with no default physical coefficients",
                "Onsager positive-semidefinite entropy and causal Maxwell-Cattaneo controls are verified internally",
                "finite-temperature normal response, SI transport, full tensor, and curved 3+1 solver are explicit non-implemented boundaries",
                "R_gen is not consumed as transport state or feedback",
            ] if status.startswith("PASS") else [],
            "equation_or_mapping": {
                "ideal_eos": "P = P(X, Phi) from tree-level finite-density O(2) action",
                "ideal_current": "N^mu = (Z*q/lambda) xi^mu",
                "ideal_stress": "T^mu_nu = f_s xi^mu xi^nu + p g^mu_nu",
                "dissipative_admission": "KuboCoefficientRecord -> constitutive coefficient only when matched evidence passes",
                "entropy_control": "sigma = X_A L^(AB) X_B >= 0 with symmetric positive-semidefinite L",
                "causal_control": "tau_J dJ/dt + J = -sigma_reg grad(mu)",
            },
            "units": {
                "implementation_lane": "natural units",
                "hydrodynamic_frame": "Landau",
                "temperature_scope": "T=0 only",
                "SI_transport": "not implemented",
                "coefficient_value": "source-specific units required; no physical value supplied",
            },
            "derivation_class": "source-backed implementation-scope audit plus internal ideal/positivity verification; not physical transport derivation",
            "observable": "covariant ideal superfluid response and bounded dissipative interface",
            "data_role": "INTERNAL_IMPLEMENTATION_SCOPE_NOT_PHYSICAL_TRANSPORT",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "physical_Kubo_coefficient_record_missing",
                "finite_temperature_normal_component_not_derived",
                "full_superfluid_transport_tensor_deferred",
                "SI_transport_unit_map_missing",
                "curved_3p1_transport_solver_missing",
                "base_Phi_SI_anchor_and_alpha_Phi_K_missing",
            ],
            "dependency_unlocked": "implementation boundary only; no physical transport, Full Topic 13, Core curved 3+1, or Gravity unlock",
            "claim_boundary": "This result closes the implementation scope and admission boundary only. It is not a microscopic Kubo match, finite-temperature two-fluid derivation, SI transport result, external validation, or global UET closure.",
        },
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "checks": checks,
        "controlling_blocker": "physical_Kubo_coefficient_record_missing",
        "next_controller": "Acquire one state-matched physical Kubo coefficient record and independently derive the finite-temperature normal sector and SI Phi observable map; do not substitute synthetic controls.",
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
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "failed_checks": [key for key, value in checks.items() if not value],
        "closure_level": report["major_result"]["closure_level"],
    }, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
