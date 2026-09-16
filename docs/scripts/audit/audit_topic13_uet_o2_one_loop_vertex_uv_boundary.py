"""Audit the action-derived O(2) one-loop vertex UV boundary."""

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

from docs.core.uet_o2_one_loop_vertex_uv_boundary import (  # noqa: E402
    ONE_LOOP_VERTEX_UV_STATUS,
    one_loop_vertex_uv_contract,
    one_loop_vertex_uv_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_vertex_uv_boundary_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_one_loop_vertex_uv_boundary.py"
TREE_LEVEL_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_tree_level_bs_sk_match.py"
KMS_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_equilibrium_kms.py"
UV_BOUNDARY_ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_uv_boundary_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=192,
        cutoff_factor=70.0,
    )
    state = one_loop_vertex_uv_state(
        0.22,
        0.0,
        0.15,
        config,
        quadrature_order=192,
        cutoff_multipliers=(8.0, 16.0, 32.0, 64.0),
    )
    contract = one_loop_vertex_uv_contract()
    checks = {
        "zero_chemical_potential_domain_is_explicit": state.chemical_potential == 0.0,
        "o2_vertex_permutation_symmetry_holds": state.tree_vertex_symmetry_residual <= 1.0e-12,
        "o2_vertex_rotation_invariance_holds": state.tree_vertex_o2_rotation_residual <= 1.0e-12,
        "tree_level_sk_contour_identity_holds": state.contour_action_identity_residual <= 1.0e-12,
        "thermal_bubble_is_positive_and_finite": all(
            value > 0.0 and isfinite(value) for value in state.bubble_thermal_values
        ),
        "vacuum_bubble_is_positive_and_finite": all(
            value > 0.0 and isfinite(value) for value in state.bubble_vacuum_values
        ),
        "thermal_bubble_is_cutoff_stable": state.thermal_cutoff_relative_change <= 1.0e-10,
        "vacuum_bubble_grows_with_cutoff": state.vacuum_growth_ratio > 1.5,
        "one_loop_correction_growth_is_visible": state.one_loop_correction_growth_ratio > 1.5,
        "one_loop_vertex_values_are_finite": all(
            isfinite(value)
            for value in (*state.one_loop_vertex_norms, *state.one_loop_correction_norms)
        ),
        "equilibrium_kms_ratio_holds": state.kms_ratio_residual <= 1.0e-12,
        "equilibrium_kms_noise_fdt_holds": state.kms_noise_fdt_residual <= 1.0e-12,
        "renormalized_vertex_not_claimed": (
            state.one_loop_renormalized_vertex_completed is False
        ),
        "full_interacting_sk_not_claimed": (
            state.full_interacting_sk_kms_match_completed is False
        ),
        "physical_kubo_not_emitted": state.physical_kubo_coefficient_emitted is False,
        "numeric_alpha_not_emitted": state.numeric_alpha_Phi_K_emitted is False,
        "no_parameter_fitting": state.parameter_fitting_performed is False,
        "no_target_or_holdout": (
            state.target_data_used is False and state.xie_2026_accessed is False
        ),
        "Phi_ontology_preserved": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["ontology"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["ontology"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["ontology"]["R_obs"],
        "renormalization_boundary_is_explicit": (
            contract["excluded"]["vacuum_counterterm"] is True
            and contract["excluded"]["renormalized_one_loop_vertex"] is True
        ),
        "finite_density_boundary_is_explicit": (
            contract["excluded"]["finite_chemical_potential_vertex"] is True
        ),
        "thermal_and_external_boundaries_are_explicit": (
            contract["excluded"]["full_interacting_sk_influence_functional"] is True
            and contract["excluded"]["physical_kubo_coefficient"] is True
            and contract["excluded"]["SI_map"] is True
            and contract["excluded"]["alpha_Phi_K"] is True
            and contract["excluded"]["TTG_validation"] is True
        ),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = ONE_LOOP_VERTEX_UV_STATUS if not failed else (
        "BLOCKED_ACTION_DERIVED_O2_ONE_LOOP_VERTEX_UV_BOUNDARY"
    )
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_one_loop_vertex_uv_boundary.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_tree_level_bs_sk_match.py", "sha256": sha256(TREE_LEVEL_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_equilibrium_kms.py", "sha256": sha256(KMS_MODULE)},
        {"path": "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_uv_boundary_audit.json", "sha256": sha256(UV_BOUNDARY_ARTIFACT)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-one-loop-vertex-uv-boundary-v1",
        "artifact": "t13_uet_o2_one_loop_vertex_uv_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_ONE_LOOP_VERTEX_UV_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the O(2)-invariant bare four-point tensor and its permutation/rotation identities",
                "the tree-level Keldysh contour interaction expansion into classical and quantum vertices",
                "the zero-external-momentum one-loop Euclidean bubble decomposition into finite thermal and logarithmically growing vacuum parts",
                "the equilibrium KMS/FDT witness attached to the declared finite-temperature mode",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "vacuum_counterterm_and_renormalized_microscopic_vertex_missing",
                "finite_chemical_potential_charged_propagator_and_vertex_missing",
                "full_interacting_SK_action_and_KMS_match_missing",
                "continuum_limit_not_converged",
                "physical_Kubo_coefficient_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": (
                "named O(2) bare tensor and one-loop UV boundary only; no renormalized "
                "microscopic vertex, finite-density SK match, physical Kubo, SI, alpha, "
                "Core, Gravity, transport, or external-validation unlock"
            ),
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": asdict(state),
        "checks": checks,
        "failed_checks": failed,
        "one_loop_renormalized_vertex_completed": False,
        "full_interacting_sk_kms_match_completed": False,
        "physical_transport_coefficients_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "vacuum_counterterm_and_renormalized_microscopic_vertex_missing",
        "next_controller": (
            "derive a declared vacuum counterterm and finite-density charged propagator/vertex "
            "before claiming an interacting microscopic SK/KMS match; keep alpha/source/holdout gates independent"
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
        "thermal_cutoff_relative_change": state.thermal_cutoff_relative_change,
        "vacuum_growth_ratio": state.vacuum_growth_ratio,
        "one_loop_correction_growth_ratio": state.one_loop_correction_growth_ratio,
        "evidence_hashes": evidence,
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
