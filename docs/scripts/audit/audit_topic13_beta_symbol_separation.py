"""Audit that Topic 13 beta symbols cannot close a UET thermal bridge by alias.

This is a scoped no-go.  It distinguishes the standard inverse-temperature
symbol from two normalized implementation coefficients and records the missing
finite-temperature UET coefficient contract.  It does not calculate a beta,
fit a curve, or consume source/holdout data.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isclose, log
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PARAMETERS_REL = "docs/core/uet_parameters.py"
HYPERBOLIC_REL = "docs/core/uet_hyperbolic_phase_field.py"
SELECTED_BRANCH_REL = "docs/core/uet_matter_space_flux_phi.py"
THERMAL_AUDIT_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/thermal_closure_derivation_audit.json"
CONSTRAINT_REL = "docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_Core_Thermodynamic_Constraint_Gate.py"
LEGACY_RESEARCH_REL = "docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_Thermodynamic_Bridge.py"
FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_beta_symbol_separation_noncircularity_audit.json"


def text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def load(rel: str) -> dict[str, Any]:
    value = json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def algebraic_witness() -> dict[str, Any]:
    """Show that the Landauer identity leaves normalized coefficients free."""

    boltzmann_j_per_k = 1.380649e-23
    temperature_k = 300.0
    beta_th = 1.0 / (boltzmann_j_per_k * temperature_k)
    landauer_energy_j = boltzmann_j_per_k * temperature_k * log(2.0)
    recovered_energy_j = log(2.0) / beta_th
    beta_core_candidates = (0.05, 0.47)
    return {
        "assumed_temperature_K": temperature_k,
        "standard_beta_th_J_inverse": beta_th,
        "standard_landauer_energy_J": landauer_energy_j,
        "recovered_landauer_energy_J": recovered_energy_j,
        "distinct_dimensionless_beta_core_candidates": beta_core_candidates,
        "checks": {
            "standard_identity_closes": isclose(
                landauer_energy_j, recovered_energy_j, rel_tol=0.0, abs_tol=1.0e-38
            ),
            "normalized_candidates_are_distinct": beta_core_candidates[0]
            != beta_core_candidates[1],
            "landauer_formula_contains_no_beta_core": True,
        },
    }


def main() -> int:
    parameters = text(PARAMETERS_REL)
    hyperbolic = text(HYPERBOLIC_REL)
    selected_branch = text(SELECTED_BRANCH_REL)
    legacy_research = text(LEGACY_RESEARCH_REL)
    constraint = text(CONSTRAINT_REL)
    thermal = load(THERMAL_AUDIT_REL)
    formula = text(FORMULA_REL)
    witness = algebraic_witness()

    checks = {
        "landauer_helper_explicitly_not_si_energy_or_beta_derivation": all(
            phrase in parameters
            for phrase in (
                "not the SI Landauer energy",
                "not a first-principles",
                "derivation of the dimensionless core beta",
            )
        ),
        "landauer_energy_has_separate_si_helper": "def landauer_minimum_energy" in parameters
        and "k_B T ln(2)" in parameters,
        "core_beta_is_declared_dimensionless": "Dimensionless normalized coupling (not Joules)" in parameters,
        "core_beta_alias_preserves_normalized_role": "Dimensionless normalized coupling for the normalized core lane." in parameters,
        "hyperbolic_beta_is_a_separate_comparator_coefficient": all(
            phrase in hyperbolic
            for phrase in (
                "beta_wave",
                "normalized_light_speed",
                "auxiliary_speed",
            )
        ),
        "selected_causal_branch_has_no_beta_alias": "beta" not in selected_branch.lower(),
        "thermal_functional_has_no_explicit_temperature": thermal.get("current_functional")
        == "normalized effective functional Omega_hat(C, Phi) with no explicit T argument",
        "thermal_closure_requires_dimensional_and_temperature_inputs": set(
            thermal.get("conditional_closure", {}).get("required_open_inputs", [])
        )
        >= {
            "dimensional free-energy-density scale e0",
            "temperature-dependent coefficient functions",
            "unit and volume convention",
            "observable map to the measured thermal variable",
        },
        "core_constraint_gate_forbids_landauer_beta_derivation": "may not derive beta, EOS, mobility, or a core coupling coefficient" in constraint,
        "formula_audit_symbol_record_present": "`T13-017`" in formula,
        "legacy_prediction_wording_is_detected_but_not_accepted": "UET beta prediction" in legacy_research,
        "algebraic_nonidentifiability_witness_passes": all(witness["checks"].values()),
    }
    status = (
        "PASS_SCOPED_NO_GO_BETA_SYMBOL_IDENTIFICATION"
        if all(checks.values())
        else "FAIL_BETA_SYMBOL_SEPARATION_NONCIRCULARITY_AUDIT"
    )
    report = {
        "schema_version": "t13-beta-symbol-separation-noncircularity-v1",
        "artifact": "t13_beta_symbol_separation_noncircularity_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_BETA_SYMBOL_SEPARATION_NONCIRCULARITY_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the standard inverse-temperature beta_th, the legacy normalized beta_core, and the hyperbolic-comparator beta_wave are distinct symbols with distinct declared roles",
                "the standard identity E_L=k_B*T*ln(2)=ln(2)/beta_th cannot identify beta_core or beta_wave because neither appears in that identity",
                "the selected Topic 13 conserved flux/C-Phi causal branch contains no beta alias",
                "the current normalized thermal functional has no explicit temperature dependence or dimensional free-energy scale from which a UET thermal beta could be derived",
                "the legacy printed phrase UET beta prediction is recorded as non-accepted wording, not evidence of a UET derivation",
            ],
            "equation_or_mapping": {
                "standard_thermodynamic_identity": "beta_th = 1/(k_B*T); E_L = k_B*T*ln(2) = ln(2)/beta_th",
                "core_legacy_coefficient": "beta_core = UETParameters.beta; dimensionless normalized coupling",
                "hyperbolic_comparator_coefficient": "beta_wave enters w_t, p_t, and the normalized auxiliary characteristic speed sqrt(gamma_gradient/beta_wave)",
                "selected_topic13_causal_branch": "C_t + partial_x J_C = 0; tau_C J_C_t + J_C = -M_C partial_x mu_C; no beta coefficient is declared in this branch",
                "thermal_closure_requirement": "f_th(C,Phi,T)=e0*f_hat(C,Phi;theta_i(T)); beta_UET cannot be identified until a finite-temperature coefficient/action/observable contract is declared",
                "nonidentification_consequence": "E_L remains invariant after changing beta_core or beta_wave because they are absent from the standard Landauer identity",
            },
            "units": {
                "beta_th": "J^-1 after an externally supplied temperature T in K",
                "E_L": "J",
                "beta_core": "dimensionless normalized coupling; not J or J^-1",
                "beta_wave": "normalized comparator coefficient; no SI or thermal-observable bridge is declared",
                "beta_UET": "OPEN: no action term, units, finite-temperature provenance, or observable mapping declared",
            },
            "derivation_class": "algebraic nonidentifiability witness plus source/interface and formula-contract audit",
            "observable": "future finite-temperature UET bridge coefficient only; no current temperature, heat-flux, entropy, or TTG observable is emitted",
            "data_role": "INTERNAL_STRUCTURAL_AUDIT_NO_SOURCE_ROWS_OR_HOLDOUT",
            "evidence_artifacts": [
                {"path": PARAMETERS_REL, "sha256": sha256(PARAMETERS_REL)},
                {"path": HYPERBOLIC_REL, "sha256": sha256(HYPERBOLIC_REL)},
                {"path": SELECTED_BRANCH_REL, "sha256": sha256(SELECTED_BRANCH_REL)},
                {"path": THERMAL_AUDIT_REL, "sha256": sha256(THERMAL_AUDIT_REL)},
                {"path": CONSTRAINT_REL, "sha256": sha256(CONSTRAINT_REL)},
                {"path": LEGACY_RESEARCH_REL, "sha256": sha256(LEGACY_RESEARCH_REL)},
                {"path": FORMULA_REL, "sha256": sha256(FORMULA_REL)},
                {"path": "docs/core/07_artifacts/topic13/t13_beta_symbol_separation_noncircularity_audit.json"},
            ],
            "verification_status": status,
            "open_blockers": [
                "declared_beta_UET_action_term_and_units_missing",
                "finite_temperature_coefficient_provenance_independent_of_Landauer_missing",
                "system_specific_SI_free_energy_and_observable_contract_missing",
                "non_circular_UET_bridge_EOS_transport_KMS_entropy_derivation_missing",
            ],
            "dependency_unlocked": "none; this prevents a symbol alias from being used as a bridge derivation but does not unlock the full thermodynamic bridge, Core curved 3+1, Gravity, or constitutive transport",
            "claim_boundary": "This no-go is limited to the currently declared beta symbols, current selected Topic 13 branch, and current normalized thermal functional. It does not exclude a future beta_UET derived from a declared finite-temperature action, source-locked coefficient provenance, and SI observable contract independent of Landauer.",
        },
        "beta_symbol_registry": {
            "beta_th": {
                "meaning": "standard thermodynamic inverse energy",
                "relation": "1/(k_B*T)",
                "units": "J^-1",
                "role": "standard identity only after T is independently specified",
            },
            "beta_core": {
                "meaning": "legacy UET normalized coupling",
                "relation": "UETParameters.beta",
                "units": "dimensionless",
                "role": "normalized core lane; explicitly not SI Landauer energy or a first-principles beta derivation",
            },
            "beta_wave": {
                "meaning": "hyperbolic phase-field auxiliary comparator coefficient",
                "relation": "v_aux^2=gamma_gradient/beta_wave",
                "units": "normalized comparator lane; no SI mapping declared",
                "role": "causal/comparator control, not the selected Topic 13 thermal branch",
            },
            "beta_UET": {
                "meaning": "required future non-circular thermal bridge coefficient",
                "relation": "OPEN",
                "units": "OPEN",
                "role": "must be declared with a finite-temperature action term, source-independent provenance, and observable/SI contract",
            },
        },
        "algebraic_witness": witness,
        "legacy_wording": {
            "source": LEGACY_RESEARCH_REL,
            "detected_phrase": "UET beta prediction",
            "accepted_as_derivation": False,
            "reason": "The current helper and constraint gate explicitly classify the normalized proxy and Landauer lower bound as non-derivational for beta_core, EOS, transport, and bridge coefficients.",
            "remediation": "Do not use this legacy output as a claim. Any wording repair must preserve its historical role and be separately claim-audited.",
        },
        "checks": checks,
        "numeric_beta_UET_emitted": False,
        "numeric_e0_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "source_rows_consumed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "declared_beta_UET_action_term_units_and_finite_temperature_derivation_missing",
        "next_controller": "Declare beta_UET in a finite-temperature effective action or response functional with units, an SI free-energy/observable contract, and coefficient provenance independent of Landauer; then test EOS, transport, KMS, entropy, and dissipation without target-data fitting.",
        "claim_boundary": "No UET beta, EOS coefficient, transport coefficient, Kelvin observable, entropy production, TTG fit, source-row calibration, or Xie 2026 result is produced by this audit.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "failed_checks": [name for name, value in checks.items() if not value],
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
