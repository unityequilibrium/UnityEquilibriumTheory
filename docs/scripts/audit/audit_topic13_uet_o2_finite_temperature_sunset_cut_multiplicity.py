"""Audit the action-level finite-temperature sunset cut multiplicity."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_finite_temperature_sunset_cut_multiplicity import (  # noqa: E402
    CUT_MULTIPLICITY_STATUS,
    finite_temperature_sunset_cut_multiplicity_contract,
    finite_temperature_sunset_cut_multiplicity_state,
)


OUT = ROOT / (
    "docs/core/artifacts/"
    "t13_uet_o2_finite_temperature_sunset_cut_multiplicity_audit.json"
)
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_cut_multiplicity.py"
TENSOR = ROOT / "docs/core/02_equations/o2/uet_o2_action_1pi_sunset_tensor.py"
SCATTERING = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_scattering_sk_kms.py"
TAXONOMY = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_signed_cut_coverage.py"
PHYSICAL_COMPARATOR = ROOT / "docs/core/02_equations/o2/uet_o2_action_sunset_1pi_spectral.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = finite_temperature_sunset_cut_multiplicity_state(
        mass_squared=0.5,
        quartic=0.8,
        species_count=2,
    )
    contract = finite_temperature_sunset_cut_multiplicity_contract()
    numeric_values = tuple(
        value
        for key, value in asdict(state).items()
        if isinstance(value, (int, float)) and key != "species_count"
    ) + tuple(state.physical_final_state_weight_values)
    finite_state = all(math.isfinite(float(value)) for value in numeric_values)
    checks = {
        "one_to_three_sign_count_is_one": state.one_to_three_sign_pattern_count == 1,
        "two_to_two_sign_count_is_three": state.two_to_two_sign_pattern_count == 3,
        "sunset_symmetry_factor_is_one_sixth": abs(
            state.sunset_symmetry_factor - 1.0 / 6.0
        )
        <= 1.0e-15,
        "one_to_three_graph_weight_is_one_sixth": abs(
            state.one_to_three_graph_weight - 1.0 / 6.0
        )
        <= 1.0e-15,
        "two_to_two_graph_weight_is_three_sixths": abs(
            state.two_to_two_graph_weight - 0.5
        )
        <= 1.0e-15,
        "two_to_two_to_one_to_three_ratio_is_three": abs(
            state.two_to_two_to_one_to_three_graph_weight_ratio - 3.0
        )
        <= 1.0e-15,
        "current_representative_factor_matches_graph_weight": state.current_factor_matches_two_to_two_graph_weight,
        "action_level_multiplicity_is_completed": state.action_level_signed_cut_multiplicity_completed,
        "current_factor_semantics_is_explicit": state.current_graph_weight_semantics_completed,
        "physical_final_state_formula_is_present": state.physical_final_state_weight_formula_present,
        "physical_final_state_has_species_dependent_weights": state.physical_final_state_has_species_dependent_weights,
        "physical_scattering_normalization_is_not_promoted": not state.physical_scattering_normalization_match_completed,
        "full_finite_temperature_1pi_remains_open": not state.full_finite_temperature_1pi_self_energy_completed,
        "physical_renormalization_remains_open": not state.unique_physical_renormalization_scheme_match_completed,
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_data": not state.target_data_used,
        "xie_2026_not_accessed": not state.xie_2026_accessed,
        "finite_state": finite_state,
        "contract_includes_graph_weight": contract["included"][
            "two_to_two_graph_weight_three_sixths"
        ],
        "contract_separates_final_state_factor": contract["included"][
            "species_resolved_final_state_factor_separation"
        ],
        "contract_excludes_physical_identity": contract["excluded"][
            "physical_scattering_normalization_identity"
        ],
        "contract_excludes_holdout": contract["excluded"]["Xie_2026_holdout"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed_checks = [key for key, value in checks.items() if not value]
    status = CUT_MULTIPLICITY_STATUS if not failed_checks else (
        "FAIL_ACTION_DERIVED_O2_FINITE_T_SUNSET_CUT_MULTIPLICITY_LANE"
    )
    evidence = [
        {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path)}
        for path in (MODULE, TENSOR, SCATTERING, TAXONOMY, PHYSICAL_COMPARATOR)
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed_checks else "OPEN"
    major_result_id = "T13_UET_O2_FINITE_T_SUNSET_CUT_MULTIPLICITY_LANE"
    open_blockers = [
        "physical_scattering_normalization_identity_not_admitted",
        "complete_finite_temperature_1pi_self_energy_missing",
        "unique_physical_renormalization_scheme_match_missing",
        "physical_Kubo_coefficient_missing",
    ]
    payload = {
        "schema_version": "t13-uet-o2-finite-t-sunset-cut-multiplicity-v1",
        "artifact": "t13_uet_o2_finite_temperature_sunset_cut_multiplicity_audit",
        "generated_at": str(date.today()),
        "status": status,
        "major_result_id": major_result_id,
        "closure_level": closure_level,
        "state": asdict(state),
        "contract": contract,
        "checks": checks,
        "failed_checks": failed_checks,
        "full_core_unlock": False,
        "claim_promotion": False,
        "evidence_artifacts": evidence,
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": state.data_role,
        "controlling_blocker": (
            "physical_scattering_normalization_identity_and_complete_"
            "finite_temperature_1pi_missing"
        ),
        "next_action": (
            "Use the action-level graph weight as the admitted natural-unit cut "
            "weight, then evaluate the complete retarded/advanced/Keldysh 1PI "
            "object and independently establish its physical renormalization anchor."
        ),
        "claim_boundary": contract["claim_boundary"],
    }
    payload["major_result"] = {
        "major_result_id": major_result_id,
        "topic": "Topic 13 Thermodynamic Bridge",
        "closure_level": closure_level,
        "what_is_closed": [
            "one positive-energy 1<->3 sign pattern and three positive-energy 2<->2 sign permutations",
            "sunset graph symmetry factor S_sunset=1/6",
            "two-to-two graph weight 3*S_sunset=1/2",
            "mapping of the current representative factor 1/2 to the graph-summed 2<->2 weight",
            "separation of species-resolved physical final-state weight 1/(1+delta_cd) from the graph weight",
        ]
        if not failed_checks
        else [],
        "equation_or_mapping": contract["equations"],
        "units": contract["unit_contract"],
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": state.data_role,
        "verification_status": status,
        "open_blockers": open_blockers,
        "dependency_unlocked": (
            "action-level finite-temperature sunset cut multiplicity only; no physical "
            "scattering coefficient, complete 1PI, physical renormalization, Kubo, SI, "
            "alpha, Core, Gravity, Galaxy, or external-validation unlock"
        ),
        "claim_boundary": contract["claim_boundary"],
        "evidence_artifacts": evidence,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "failed_checks": failed_checks,
                "artifact": str(OUT.relative_to(ROOT)),
                "one_to_three_graph_weight": state.one_to_three_graph_weight,
                "two_to_two_graph_weight": state.two_to_two_graph_weight,
                "current_factor_matches": state.current_factor_matches_two_to_two_graph_weight,
                "physical_final_state_weights": state.physical_final_state_weight_values,
            },
            indent=2,
        )
    )
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
