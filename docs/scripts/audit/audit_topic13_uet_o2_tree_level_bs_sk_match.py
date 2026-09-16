"""Audit the tree-level action vertex and formal SK/KMS match lane."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from datetime import date
from math import isfinite
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_tree_level_bs_sk_match import (  # noqa: E402
    TREE_LEVEL_BS_SK_STATUS,
    tree_level_bs_sk_match_contract,
    tree_level_bs_sk_match_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_tree_level_bs_sk_match_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_tree_level_bs_sk_match.py"
CONTINUUM_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_continuum_collision_operator.py"
TRANSITION_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py"
MOMENTUM_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py"
EOS_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_state(state: object) -> dict[str, object]:
    return asdict(state)


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=128,
        cutoff_factor=60.0,
    )
    state = tree_level_bs_sk_match_state(
        0.22,
        0.35,
        0.15,
        config,
        radial_order=8,
        transition_channel_count=64,
        transition_interpolation_order=40,
        cutoff_factor=48.0,
    )
    contract = tree_level_bs_sk_match_contract()
    checks = {
        "tree_level_action_match_is_declared": (
            state.tree_level_action_match_completed is True
        ),
        "action_vertex_cross_section_normalization_is_checked": (
            state.action_vertex_cross_section_residual <= 1.0e-12
        ),
        "exact_channel_kinematics_are_conserved": (
            state.exact_channel_kinematic_residual <= 1.0e-10
        ),
        "exact_channel_detailed_balance_holds": (
            state.exact_channel_detailed_balance_residual <= 1.0e-10
        ),
        "action_width_vertex_decomposition_is_resolved": (
            state.action_width_vertex_decomposition_residual <= 1.0e-12
        ),
        "algebraic_bethe_salpeter_identity_is_resolved": (
            state.algebraic_bethe_salpeter_residual <= 1.0e-10
        ),
        "formal_sk_action_kms_match_is_resolved": (
            state.formal_sk_action_kms_match_completed is True
            and state.formal_sk_action_kms_residual <= 1.0e-12
        ),
        "formal_sk_noise_fdt_match_is_resolved": (
            state.formal_sk_noise_fdt_residual <= 1.0e-12
        ),
        "formal_entropy_witness_is_positive": (
            state.formal_sk_entropy_witness > 0.0
            and isfinite(state.formal_sk_entropy_witness)
        ),
        "continuum_resolution_sequence_is_recorded": (
            len(state.continuum_sequence_radial_orders) == 4
            and len(state.continuum_sequence_channel_counts) == 4
            and len(state.continuum_sequence_dc_responses) == 4
            and len(state.continuum_sequence_relative_changes) == 3
        ),
        "continuum_sequence_is_finite": all(
            isfinite(float(value))
            for value in (
                *state.continuum_sequence_dc_responses,
                *state.continuum_sequence_relative_changes,
                state.continuum_sequence_max_relative_change,
            )
        ),
        "continuum_controller_is_visible": (
            state.continuum_sequence_max_relative_change > 1.0e-2
        ),
        "continuum_limit_is_not_claimed": state.continuum_limit_completed is False,
        "microscopic_bethe_salpeter_match_not_claimed": (
            state.microscopic_bethe_salpeter_match_completed is False
        ),
        "microscopic_sk_kms_match_not_claimed": (
            state.microscopic_sk_kms_match_completed is False
        ),
        "physical_kubo_coefficient_not_emitted": (
            state.physical_kubo_coefficient_emitted is False
        ),
        "numeric_alpha_not_emitted": state.numeric_alpha_Phi_K_emitted is False,
        "no_parameter_fitting": state.parameter_fitting_performed is False,
        "no_target_or_holdout": (
            state.target_data_used is False and state.xie_2026_accessed is False
        ),
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": (
            "derived history trace" in contract["unit_contract"]["R_gen"]
        ),
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "tree_level_boundary_is_explicit": (
            contract["excluded"]["loop_renormalized_vertex"] is True
            and contract["excluded"]["full_microscopic_bethe_salpeter_solution"] is True
            and contract["excluded"]["full_interacting_sk_influence_functional"] is True
        ),
        "thermal_and_external_boundaries_are_explicit": (
            contract["excluded"]["continuum_limit"] is True
            and contract["excluded"]["physical_kubo_coefficient"] is True
            and contract["excluded"]["SI_map"] is True
            and contract["excluded"]["alpha_Phi_K"] is True
            and contract["excluded"]["TTG_validation"] is True
        ),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = TREE_LEVEL_BS_SK_STATUS if not failed else (
        "BLOCKED_ACTION_DERIVED_TREE_LEVEL_BS_SK_MATCH_INTERFACE_LANE"
    )
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_tree_level_bs_sk_match.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_continuum_collision_operator.py", "sha256": sha256(CONTINUUM_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py", "sha256": sha256(TRANSITION_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py", "sha256": sha256(MOMENTUM_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py", "sha256": sha256(EOS_MODULE)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-tree-level-bs-sk-match-v1",
        "artifact": "t13_uet_o2_tree_level_bs_sk_match_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_TREE_LEVEL_BS_SK_MATCH_INTERFACE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the declared tree-level charged-sector action vertex normalization and cross-section relation",
                "exact elastic-channel kinematics and action-derived detailed-balance interface",
                "the finite-cutoff conservative operator vertex decomposition and algebraic Bethe-Salpeter identity",
                "the formal SK retarded/noise notation with algebraic KMS and fluctuation-dissipation matching",
                "a positive formal entropy witness and a recorded, nonconverged continuum-resolution controller",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "continuum_limit_not_converged",
                "loop_renormalized_microscopic_vertex_missing",
                "full_interacting_SK_action_and_KMS_match_missing",
                "full_entropy_current_heat_flux_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": (
                "named tree-level action vertex normalization and formal finite-cutoff SK/KMS/"
                "Bethe-Salpeter interface only; no continuum-limit, microscopic, physical Kubo, "
                "SI, alpha, Core, Gravity, transport, or external-validation unlock"
            ),
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": compact_state(state),
        "checks": checks,
        "failed_checks": failed,
        "continuum_limit_completed": False,
        "microscopic_bethe_salpeter_match_completed": False,
        "microscopic_sk_kms_match_completed": False,
        "physical_transport_coefficients_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "microscopic_bethe_salpeter_vertex_and_SK_action_match_missing",
        "next_controller": (
            "derive the loop-renormalized microscopic vertex and full interacting SK/KMS action "
            "match on top of the tree-level interface; test a declared continuum-limit sequence "
            "without consuming Xie 2026"
        ),
        "claim_promotion": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "artifact": str(OUT.relative_to(ROOT)),
        "closure_level": artifact["major_result"]["closure_level"],
        "failed_checks": failed,
        "max_continuum_relative_change": state.continuum_sequence_max_relative_change,
        "evidence_hashes": evidence,
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
