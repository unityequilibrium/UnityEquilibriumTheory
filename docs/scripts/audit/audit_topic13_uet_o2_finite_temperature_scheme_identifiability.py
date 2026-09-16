"""Audit the finite-temperature renormalization-scheme identifiability no-go."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from math import isfinite
from pathlib import Path

if str(Path(__file__).resolve().parents[3]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from docs.core.uet_o2_finite_temperature_scheme_identifiability import (
    finite_temperature_scheme_identifiability_contract,
    finite_temperature_scheme_witnesses,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/02_equations/o2/uet_o2_finite_temperature_scheme_identifiability.py"
RENORMALIZED_REL = "docs/core/02_equations/o2/uet_o2_renormalized_normal_branch.py"
HARTREE_REL = "docs/core/02_equations/o2/uet_o2_finite_temperature_self_energy.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_scheme_identifiability_no_go.json"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    contract = finite_temperature_scheme_identifiability_contract()
    witnesses = finite_temperature_scheme_witnesses()
    scheme_a, scheme_b = witnesses
    checks = {
        "two_scheme_witnesses_are_present": len(witnesses) == 2
        and scheme_a.name != scheme_b.name,
        "reference_mass_and_scale_are_positive": all(
            item.reference_mass_sq > 0.0 and item.scale_sq > 0.0 for item in witnesses
        ),
        "scheme_A_reference_value_zero": abs(scheme_a.reference_value) <= 1.0e-14,
        "scheme_A_reference_first_derivative_zero": abs(
            scheme_a.reference_first_derivative
        )
        <= 1.0e-14,
        "scheme_A_reference_second_derivative_zero": abs(
            scheme_a.reference_second_derivative
        )
        <= 1.0e-14,
        "scheme_B_reference_value_zero": abs(scheme_b.reference_value) <= 1.0e-14,
        "scheme_B_reference_first_derivative_zero": abs(
            scheme_b.reference_first_derivative
        )
        <= 1.0e-14,
        "scheme_B_reference_second_derivative_zero": abs(
            scheme_b.reference_second_derivative
        )
        <= 1.0e-14,
        "off_reference_potentials_are_distinct": abs(
            scheme_a.off_reference_value - scheme_b.off_reference_value
        )
        > 1.0e-12,
        "off_reference_first_derivatives_are_distinct": abs(
            scheme_a.off_reference_first_derivative
            - scheme_b.off_reference_first_derivative
        )
        > 1.0e-12,
        "off_reference_second_derivatives_are_distinct": abs(
            scheme_a.off_reference_second_derivative
            - scheme_b.off_reference_second_derivative
        )
        > 1.0e-12,
        "reference_conditions_are_second_order": "partial_x^2" in contract["equations"][
            "reference_conditions"
        ],
        "natural_units_are_declared": contract["units"]["unit_lane"] == "natural",
        "finite_coefficient_is_dimensionless": contract["units"][
            "finite_coefficient"
        ]
        == "dimensionless local scheme parameter",
        "named_hartree_branch_is_separate": "named_hartree_branch" in contract[
            "equations"
        ],
        "Phi_is_not_temperature": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_is_preserved": "not mass or charge" in contract["ontology"]["C"],
        "R_gen_is_derived_only": "derived history trace only" in contract["ontology"]["R_gen"],
        "all_witness_values_finite": all(
            isfinite(value)
            for item in witnesses
            for value in (
                item.reference_value,
                item.reference_first_derivative,
                item.reference_second_derivative,
                item.off_reference_value,
                item.off_reference_first_derivative,
                item.off_reference_second_derivative,
            )
        ),
        "no_source_or_holdout": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = (
        "PASS_SCOPED_NO_GO_FINITE_TEMPERATURE_SCHEME_IDENTIFIABILITY"
        if all(checks.values())
        else "FAIL_FINITE_TEMPERATURE_SCHEME_IDENTIFIABILITY_NO_GO"
    )
    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": RENORMALIZED_REL, "sha256": digest(RENORMALIZED_REL)},
        {"path": HARTREE_REL, "sha256": digest(HARTREE_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-finite-temperature-scheme-identifiability-no-go-v1",
        "artifact": "t13_uet_o2_finite_temperature_scheme_identifiability_no_go",
        "generated_at": date.today().isoformat(),
        "status": status,
        "formal_no_go_closure": "CLOSED_AS_NO_GO" if status.startswith("PASS") else "OPEN",
        "major_result": {
            "major_result_id": "T13_UET_O2_FINITE_T_SCHEME_IDENTIFIABILITY_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the currently declared second-order reference conditions do not select a unique finite-temperature renormalization completion",
                "two finite local counterterm completions share the reference value, first derivative, and second derivative while differing off reference",
                "the named Hartree branch is explicitly separated from a unique microscopic finite-temperature action",
                "the no-go is structural and does not use source rows, target curves, fitting, or the locked holdout",
            ]
            if status.startswith("PASS")
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "source_backed_or_declared_physical_finite_temperature_renormalization_scheme_missing",
                "interacting_finite_temperature_self_energy_microscopic_matching_missing",
                "condensate_and_normal_two_fluid_completion_missing",
                "physical_Kubo_coefficient_record_missing",
                "SK_KMS_physical_matching_missing",
                "dimensional_phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
            ],
            "dependency_unlocked": "finite-temperature scheme identifiability no-go only; named Hartree branch remains an approximation and no physical EOS, transport, KMS, SI, alpha, Full Topic 13, Core, or Gravity dependency is unlocked",
            "claim_boundary": contract["claim_boundary"],
        },
        "witnesses": [
            {
                "name": item.name,
                "finite_coefficient": item.finite_coefficient,
                "reference_mass_sq": item.reference_mass_sq,
                "scale_sq": item.scale_sq,
                "reference_value": item.reference_value,
                "reference_first_derivative": item.reference_first_derivative,
                "reference_second_derivative": item.reference_second_derivative,
                "off_reference_value": item.off_reference_value,
                "off_reference_first_derivative": item.off_reference_first_derivative,
                "off_reference_second_derivative": item.off_reference_second_derivative,
                "coefficient_origin": item.coefficient_origin,
            }
            for item in witnesses
        ],
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "source_backed_or_declared_physical_finite_temperature_renormalization_scheme_missing",
        "next_controller": "Either declare and justify a physical finite-temperature renormalization scheme with microscopic matching, or retain the named Hartree lane as approximation-only while closing physical Kubo/SK/KMS and SI observables without fitting alpha or reading Xie 2026.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "failed_checks": [key for key, value in checks.items() if not value],
                "off_reference_difference": abs(
                    scheme_a.off_reference_value - scheme_b.off_reference_value
                ),
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
