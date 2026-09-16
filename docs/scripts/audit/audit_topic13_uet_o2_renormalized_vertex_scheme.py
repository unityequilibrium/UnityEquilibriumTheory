"""Audit the declared renormalized O(2) one-loop vertex scheme."""

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

from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_renormalized_vertex_scheme import (  # noqa: E402
    RENORMALIZED_VERTEX_SCHEME_STATUS,
    renormalized_vertex_scheme_contract,
    renormalized_vertex_scheme_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_renormalized_vertex_scheme_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_renormalized_vertex_scheme.py"
UV_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_one_loop_vertex_uv_boundary.py"
RENORMALIZED_NORMAL_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_renormalized_normal_branch.py"
KMS_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_equilibrium_kms.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _config() -> FiniteTemperatureO2QuasiparticleConfig:
    return FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(
            matter=CovariantMatterConfig(
                matter_mass_sq=0.5,
                matter_quartic=0.8,
                response_coupling=0.3,
            ),
            response=CovariantResponseConfig(
                epsilon_nc=0.1,
                phi_equilibrium=0.0,
            ),
        ),
        quadrature_order=192,
        cutoff_factor=70.0,
    )


def main() -> int:
    state = renormalized_vertex_scheme_state(
        0.22,
        0.0,
        0.15,
        _config(),
        reference_space_response=0.0,
        quadrature_order=192,
        cutoff_multipliers=(8.0, 16.0, 32.0, 64.0, 128.0),
    )
    contract = renormalized_vertex_scheme_contract()
    checks = {
        "reference_and_target_masses_are_distinct": (
            abs(state.effective_mass - state.reference_mass) > 1.0e-6
        ),
        "raw_vacuum_growth_is_visible": state.raw_vacuum_growth_ratio > 1.5,
        "subtracted_vacuum_values_are_finite": all(
            isfinite(value) for value in state.subtracted_vacuum_values
        ),
        "thermal_piece_is_finite_and_stable": (
            all(value > 0.0 and isfinite(value) for value in state.thermal_values)
            and state.thermal_cutoff_relative_change <= 1.0e-8
        ),
        "renormalized_bubble_is_finite": all(
            isfinite(value) and value > 0.0
            for value in state.renormalized_bubble_values
        ),
        "renormalized_bubble_cutoff_change_is_bounded": (
            state.renormalized_bubble_last_relative_change <= 1.0e-3
        ),
        "renormalized_vertex_cutoff_change_is_bounded": (
            state.renormalized_vertex_last_relative_change <= 1.0e-3
        ),
        "reference_subtraction_condition_is_explicit": (
            state.reference_subtraction_residual <= 1.0e-15
        ),
        "equilibrium_kms_ratio_holds": state.kms_ratio_residual <= 1.0e-12,
        "equilibrium_kms_noise_fdt_holds": state.kms_noise_fdt_residual <= 1.0e-12,
        "declared_scheme_is_not_physical_scheme_match": (
            state.renormalized_vertex_scheme_completed is True
            and state.physical_renormalization_scheme_matched is False
        ),
        "finite_density_vertex_remains_open": state.finite_density_vertex_completed is False,
        "full_interacting_sk_remains_open": (
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
        "scheme_boundary_is_explicit": (
            contract["excluded"]["unique_physical_renormalization"] is True
            and contract["excluded"]["finite_chemical_potential_vertex"] is True
            and contract["excluded"]["full_interacting_sk_kms_match"] is True
        ),
        "thermal_external_boundaries_are_explicit": (
            contract["excluded"]["physical_kubo_coefficient"] is True
            and contract["excluded"]["SI_map"] is True
            and contract["excluded"]["alpha_Phi_K"] is True
            and contract["excluded"]["TTG_validation"] is True
        ),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = RENORMALIZED_VERTEX_SCHEME_STATUS if not failed else (
        "BLOCKED_ACTION_DERIVED_RENORMALIZED_O2_ONE_LOOP_VERTEX_SCHEME"
    )
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_renormalized_vertex_scheme.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_one_loop_vertex_uv_boundary.py", "sha256": sha256(UV_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_renormalized_normal_branch.py", "sha256": sha256(RENORMALIZED_NORMAL_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_equilibrium_kms.py", "sha256": sha256(KMS_MODULE)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-renormalized-vertex-scheme-v1",
        "artifact": "t13_uet_o2_renormalized_vertex_scheme_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_RENORMALIZED_VERTEX_SCHEME",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the existing mass-squared reference subtraction is applied explicitly to the O(2) one-loop bubble",
                "the raw vacuum growth and finite subtracted bubble are reported on the same cutoff sequence",
                "the retained finite thermal contribution, reference condition, and equilibrium KMS/FDT witness are verified",
                "the resulting finite natural-unit one-loop vertex is closed as one declared scheme lane",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "unique_physical_renormalization_scheme_match_missing",
                "finite_chemical_potential_charged_propagator_and_vertex_missing",
                "full_interacting_SK_action_and_KMS_match_missing",
                "continuum_limit_not_converged",
                "physical_Kubo_coefficient_missing",
                "entropy_current_heat_flux_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": (
                "one declared natural-unit renormalized zero-density vertex scheme only; no "
                "unique physical scheme, finite-density charged vertex, full SK/KMS, physical "
                "Kubo, SI, alpha, Core, Gravity, transport, or external-validation unlock"
            ),
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": asdict(state),
        "checks": checks,
        "failed_checks": failed,
        "renormalized_vertex_scheme_completed": True,
        "physical_renormalization_scheme_matched": False,
        "finite_density_vertex_completed": False,
        "full_interacting_sk_kms_match_completed": False,
        "physical_transport_coefficients_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "unique_physical_renormalization_and_finite_density_charged_vertex_missing",
        "next_controller": (
            "match the declared subtraction scheme to a finite-density charged propagator and "
            "full interacting SK/KMS construction; keep physical Kubo, alpha, source, and holdout gates independent"
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
        "raw_vacuum_growth_ratio": state.raw_vacuum_growth_ratio,
        "thermal_cutoff_relative_change": state.thermal_cutoff_relative_change,
        "renormalized_bubble_last_relative_change": state.renormalized_bubble_last_relative_change,
        "renormalized_vertex_last_relative_change": state.renormalized_vertex_last_relative_change,
        "evidence_hashes": evidence,
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
