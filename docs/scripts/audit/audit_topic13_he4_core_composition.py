"""Compose the bounded O(2)/He-4 Topic 13 Core-ready result."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_he4_core_thermodynamic_bridge_composition_audit.json"

PATHS = {
    "causal": "docs/core/artifacts/t13_causal_named_branch_core_compatibility.json",
    "no_go": "docs/core/artifacts/conserved_c_finite_cone_no_go_assessment.json",
    "anchor": "docs/core/artifacts/t13_he4_svp_physical_anchor_audit.json",
    "alpha": "docs/core/artifacts/t13_he4_o2_response_calibration_audit.json",
    "beta": "docs/core/artifacts/t13_he4_o2_si_beta_mapping_audit.json",
    "natural_bridge": "docs/core/artifacts/t13_uet_o2_action_thermal_observable_bridge_audit.json",
    "action_beta": "docs/core/artifacts/t13_uet_o2_action_thermal_stiffness_beta_audit.json",
    "flat_components": "docs/core/artifacts/t13_flat_thermodynamic_bridge_components_gate.json",
    "entropy": "docs/core/artifacts/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json",
    "transport": "docs/core/artifacts/t13_he4_normal_viscosity_kubo_audit.json",
    "holdout": "docs/core/artifacts/t13_xie_2026_holdout_access_audit.json",
    "landauer": "docs/core/artifacts/t13_landauer_core_disposition_audit.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a: float, b: float) -> bool:
    return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-15)


def main() -> int:
    docs = {name: load(ROOT / rel) for name, rel in PATHS.items()}
    alpha = docs["alpha"]["record"]
    beta = docs["beta"]["record"]
    natural = docs["natural_bridge"]["state"]
    action_beta = docs["action_beta"]["state"]
    entropy = docs["entropy"]["state"]
    transport = docs["transport"]["record"]

    natural_state_checks = {
        "bridge_and_beta_temperature_match": close(natural["temperature"], action_beta["temperature"]),
        "bridge_and_beta_chemical_potential_match": close(natural["chemical_potential"], action_beta["chemical_potential"]),
        "bridge_and_beta_response_match": close(natural["space_response"], action_beta["space_response"]),
        "entropy_temperature_matches_action_state": close(entropy["temperature"], natural["temperature"]),
        "entropy_chemical_potential_matches_action_state": close(entropy["chemical_potential"], natural["chemical_potential"]),
        "entropy_response_matches_action_state": close(entropy["space_response"], natural["space_response"]),
    }
    physical_state_checks = {
        "beta_and_alpha_temperature_match": close(beta["temperature_K"], alpha["temperature_K"]),
        "transport_and_alpha_temperature_match": close(transport["state"]["temperature_K"], alpha["temperature_K"]),
        "transport_and_alpha_response_match": close(transport["state"]["space_response"], alpha["superfluid_fraction_reference"]),
        "same_physical_phase_path": transport["state"]["phase"] == "He II" and transport["state"]["pressure_path"] == "saturated vapour pressure",
    }
    mapping_checks = {
        "alpha_is_finite_and_uncertain": math.isfinite(alpha["alpha_Phi_K"]) and alpha["alpha_uncertainty_K_per_normalized_base_Phi"] > 0.0,
        "action_field_map_is_finite": math.isfinite(alpha["Z_Phi_normalized_per_natural_Phi"]) and alpha["Z_Phi_normalized_per_natural_Phi"] != 0.0,
        "normalized_beta_uses_same_field_map": close(beta["Z_Phi_normalized_per_natural_Phi"], alpha["Z_Phi_normalized_per_natural_Phi"]),
        "action_beta_is_the_declared_origin": close(beta["beta_action_natural"], action_beta["beta_phi_natural"]),
        "si_energy_scale_is_positive_with_uncertainty": beta["energy_density_scale_J_m3"] > 0.0 and beta["energy_density_scale_uncertainty_J_m3"] > 0.0,
        "landauer_not_used_for_beta": beta["holdout_policy"]["landauer_identity_used"] is False,
    }
    closure_checks = {
        "causal_named_branch_core_closed": docs["causal"]["status"] == "PASS_CAUSAL_NAMED_BRANCH_CORE_COMPATIBILITY" and docs["causal"]["major_result"]["closure_level"] == "CLOSED_FOR_CORE",
        "conserved_gradient_class_no_go_recorded": docs["no_go"]["status"] == "NO_GO_FOR_DECLARED_CONSERVED_CATTANEO_LOCAL_GRADIENT_CLASS",
        "he4_anchor_closed": docs["anchor"]["status"] == "PASS_HE4_EQUILIBRIUM_SOURCE_ANCHOR_UNCERTAINTY_OPEN",
        "alpha_and_field_normalization_closed": docs["alpha"]["status"] == "PASS_HE4_LOCAL_ALPHA_AND_FIELD_NORMALIZATION",
        "si_beta_closed": docs["beta"]["status"] == "PASS_HE4_SI_SCALE_AND_NORMALIZED_BETA",
        "action_bridge_closed": docs["natural_bridge"]["status"] == "PASS_ACTION_DERIVED_NATURAL_PHI_THERMAL_BRIDGE_LANE",
        "action_beta_origin_closed": docs["action_beta"]["status"] == "PASS_ACTION_DERIVED_THERMAL_STIFFNESS_BETA_LANE",
        "eos_sk_kms_interface_closed": docs["flat_components"]["status"] == "PASS_SCOPED_T13_FLAT_COMPONENTS_WITH_EXTERNAL_INPUT",
        "entropy_current_and_dissipative_balance_closed": docs["entropy"]["status"] == "PASS_ACTION_DERIVED_COVARIANT_ENTROPY_HEAT_FLUX_BALANCE_LANE",
        "physical_transport_input_closed": docs["transport"]["status"] == "PASS_HE4_PHYSICAL_SHEAR_KUBO_TRANSPORT" and docs["transport"]["record_validation"]["status"] == "PASS_PHYSICAL_TRANSPORT_RECORD",
        "landauer_core_role_closed": docs["landauer"]["status"] == "PASS_LANDAUER_CORE_ROLE_DISPOSITION",
        "holdout_unread": docs["holdout"]["status"] == "PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY",
    }
    integrity_checks = {
        "natural_state_interface_explicit": all(natural_state_checks.values()),
        "physical_state_interface_explicit": all(physical_state_checks.values()),
        "natural_and_physical_states_not_silently_identified": natural["temperature"] != alpha["temperature_K"],
        "declared_maps_connect_the_two_unit_lanes": all(mapping_checks.values()),
        "R_gen_absent_from_physical_state_vectors": "R_gen" not in alpha and "R_gen" not in beta and "R_gen" not in transport["state"],
        "claim_promotion_disabled_in_inputs": all(item.get("claim_promotion", False) is False for item in docs.values()),
    }
    checks = {**closure_checks, **integrity_checks}
    passed = all(checks.values())
    status = "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY" if passed else "BLOCKED_T13_HE4_CORE_COMPOSITION"
    evidence = [
        {"path": rel, "sha256": sha256(ROOT / rel), "status": docs[name].get("status")}
        for name, rel in PATHS.items()
    ]
    report = {
        "schema_version": "t13-he4-core-thermodynamic-bridge-composition-v1",
        "artifact": "t13_he4_core_thermodynamic_bridge_composition_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_CORE" if passed else "PARTIAL",
            "what_is_closed": [
                "named finite-cone causal branch plus scoped conserved-gradient no-go",
                "He-4 SVP physical response anchor, independent alpha_Phi_K, field normalization, and uncertainty",
                "non-Landauer action beta origin, normalized beta_T13, and SI energy-density scale",
                "declared finite-temperature normal EOS and formal SK/KMS/Onsager interface",
                "covariant heat-flux/entropy-current and dissipative conservation balance",
                "one source-locked physical He II normal-component shear Kubo/FDT/entropy channel",
                "Landauer imported-constraint role and Xie 2026 holdout isolation",
            ] if passed else [name for name, value in closure_checks.items() if value],
            "what_remains_open": [] if passed else [name for name, value in checks.items() if not value],
            "equation_or_mapping": {
                "measurement": "y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)",
                "dimensional_response": "Delta_Tq = alpha_Phi_K Delta_Phi_norm",
                "field_map": "Delta_Phi_norm = Z_Phi Delta_Phi_natural",
                "energy_scale": "f_SI = e0 f_natural",
                "beta": "beta_T13 = beta_natural/Z_Phi^2; beta_SI = e0 beta_T13",
                "kubo": transport["correlator_locator"],
                "entropy": transport["entropy_mapping"]["relation"],
            },
            "units": {
                "alpha_Phi_K": "K per normalized base Phi",
                "beta_SI": "J m^-3 per normalized Phi squared",
                "eta": "Pa s",
                "natural_action_lane": "natural units; connected by theta_T, Z_Phi, and e0",
            },
            "derivation_class": "COMPOSITION_OF_ACTION_DERIVATIONS_EXTERNAL_CALIBRATION_EXTERNAL_TRANSPORT_AND_SCOPED_NO_GO",
            "observable": "bounded local He-4/O(2) thermal-response and dissipative-interface lane at 1.7 K SVP",
            "data_role": "CORE_INTEGRATION_WITH_EXTERNAL_INPUTS_NOT_EXTERNAL_VALIDATION",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [] if passed else [name for name, value in checks.items() if not value],
            "dependency_unlocked": "Topic 13 flat thermal bridge may be handed to Core; curved 3+1 remains a separate Core gate.",
            "claim_boundary": "CLOSED_FOR_CORE is an internal, lane-bounded composition result. It is not a prediction of the imported He-4 coefficients, not graphite TTG validation, not a complete two-fluid transport tensor, not curved 3+1, and not global UET closure.",
        },
        "state_interface": {
            "natural_action_state": {"temperature": natural["temperature"], "chemical_potential": natural["chemical_potential"], "space_response": natural["space_response"], "branch": natural["branch"]},
            "physical_he4_state": {"temperature_K": alpha["temperature_K"], "pressure_path": transport["state"]["pressure_path"], "phase": transport["state"]["phase"], "superfluid_fraction": alpha["superfluid_fraction_reference"]},
            "connection_contract": [alpha["temperature_mapping"], alpha["action_mapping"], beta["energy_scale_mapping"]],
            "forbidden_identification": "The natural action state and physical He-4 state are not asserted to be numerically identical; only the declared theta_T, Z_Phi, and e0 maps connect their coordinates.",
            "natural_state_checks": natural_state_checks,
            "physical_state_checks": physical_state_checks,
            "mapping_checks": mapping_checks,
        },
        "checks": checks,
        "controlling_blocker": None if passed else next(name for name, value in checks.items() if not value),
        "next_action": "Integrate this bounded Core-ready result into the Topic 13 gate, closure matrix, registry, and dependency graph while retaining graphite TTG and curved 3+1 as separate open tracks.",
        "claim_boundary": "Core-ready internal composition only; external validation and global theory closure remain false.",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": OUT.relative_to(ROOT).as_posix(), "failed_checks": [name for name, value in checks.items() if not value]}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
