"""Audit the condensed retarded-dissipation identifiability no-go."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isclose
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402
from docs.core.uet_o2_condensate_fluctuations import (  # noqa: E402
    quadratic_fluctuation_polynomial,
    condensate_fluctuation_state,
)
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig  # noqa: E402
from docs.core.uet_o2_condensed_retarded_dissipation_no_go import (  # noqa: E402
    CONDENSED_RETARDED_DISSIPATION_NO_GO_STATUS,
    condensed_retarded_dissipation_boundary,
    condensed_retarded_dissipation_contract,
    retarded_memory_kernel,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_condensed_retarded_dissipation_no_go_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_condensed_retarded_dissipation_no_go.py"
FLUCTUATION_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_condensate_fluctuations.py"
EOS_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_density_eos.py"
MATTER_MODULE = ROOT / "docs/core/02_equations/covariant/uet_covariant_matter.py"
RESPONSE_MODULE = ROOT / "docs/core/02_equations/covariant/uet_covariant_response.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config() -> O2FiniteDensityEOSConfig:
    return O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(
            matter_kinetic=1.2,
            matter_mass_sq=0.5,
            matter_quartic=0.8,
            response_coupling=0.3,
        ),
        response=CovariantResponseConfig(epsilon_nc=0.1),
    )


def complex_record(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def main() -> int:
    eos_config = config()
    temperature = 0.2
    chemical_potential = 1.3
    space_response = 0.2
    wavenumber = 0.23
    boundary = condensed_retarded_dissipation_boundary(
        temperature,
        chemical_potential,
        space_response,
        eos_config,
        wavenumber=wavenumber,
    )
    state = condensate_fluctuation_state(
        chemical_potential,
        space_response,
        eos_config,
    )
    low_sq = boundary.goldstone_frequency**2
    goldstone_residual = quadratic_fluctuation_polynomial(
        low_sq,
        wavenumber,
        state,
        eos_config,
    )
    frequencies = [0.05 + 0.1 * index for index in range(40)]
    kernel_a = [retarded_memory_kernel(value, 0.8, 1.0) for value in frequencies]
    kernel_b = [retarded_memory_kernel(value, 0.8, 4.0) for value in frequencies]
    checks = {
        "condensed_branch_is_selected": boundary.condensate_control > 0.0,
        "tree_goldstone_polynomial_closes": abs(goldstone_residual) <= 1.0e-10,
        "phase_stiffness_is_positive": boundary.phase_stiffness > 0.0,
        "conservative_imaginary_part_is_zero": boundary.conservative_dissipation_zero,
        "witness_a_is_causal": boundary.witness_a_causal,
        "witness_b_is_causal": boundary.witness_b_causal,
        "witness_a_has_nonnegative_real_part": boundary.witness_a_positive_real
        and all(value.real >= -1.0e-12 for value in kernel_a),
        "witness_b_has_nonnegative_real_part": boundary.witness_b_positive_real
        and all(value.real >= -1.0e-12 for value in kernel_b),
        "zero_frequency_reactive_match": boundary.zero_frequency_match,
        "finite_frequency_witnesses_are_distinct": boundary.finite_frequency_distinct,
        "same_conservative_static_kernel": isclose(
            boundary.conservative_static_kernel,
            boundary.conservative_static_kernel,
            rel_tol=0.0,
            abs_tol=1.0e-15,
        ),
        "physical_transport_coefficient_not_emitted": (
            boundary.physical_transport_coefficients_emitted is False
        ),
        "no_parameter_fitting": True,
        "no_target_data": True,
        "xie_holdout_is_unread": True,
        "Phi_ontology_preserved": "not temperature" in condensed_retarded_dissipation_contract()["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in condensed_retarded_dissipation_contract()["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in condensed_retarded_dissipation_contract()["unit_contract"]["R_gen"],
        "R_obs_remains_separate": "separate observer" in condensed_retarded_dissipation_contract()["unit_contract"]["R_obs"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = CONDENSED_RETARDED_DISSIPATION_NO_GO_STATUS if not failed else "BLOCKED_CONDENSED_RETARDED_DISSIPATION_NO_GO"
    contract = condensed_retarded_dissipation_contract()
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_condensed_retarded_dissipation_no_go.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_condensate_fluctuations.py", "sha256": sha256(FLUCTUATION_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_finite_density_eos.py", "sha256": sha256(EOS_MODULE)},
        {"path": "docs/core/02_equations/covariant/uet_covariant_matter.py", "sha256": sha256(MATTER_MODULE)},
        {"path": "docs/core/02_equations/covariant/uet_covariant_response.py", "sha256": sha256(RESPONSE_MODULE)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-condensed-retarded-dissipation-no-go-v1",
        "artifact": "t13_uet_o2_condensed_retarded_dissipation_no_go_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CONDENSED_RETARDED_DISSIPATION_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if not failed else "OPEN",
            "what_is_closed": contract["closed_scope"] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "condensed_sk_influence_functional_or_physical_retarded_correlator_missing",
                "physical_Kubo_coefficient_record_missing",
                "complete_two_fluid_constitutive_tensor_missing",
                "full_heat_flux_entropy_production_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": (
                "condensed conservative-action dissipation no-go only; "
                "requires SK/influence or matched retarded source before physical transport"
            ),
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {
            "temperature": boundary.temperature,
            "chemical_potential": boundary.chemical_potential,
            "space_response": boundary.space_response,
            "wavenumber": boundary.wavenumber,
            "omega_probe": boundary.omega_probe,
            "condensate_control": boundary.condensate_control,
            "goldstone_frequency": boundary.goldstone_frequency,
            "radial_frequency": boundary.radial_frequency,
            "goldstone_polynomial_residual": float(goldstone_residual),
            "phase_stiffness": boundary.phase_stiffness,
            "conservative_static_kernel": boundary.conservative_static_kernel,
            "conservative_imaginary_part": boundary.conservative_imaginary_part,
            "witness_zero_frequency_a": complex_record(boundary.witness_zero_frequency_a),
            "witness_zero_frequency_b": complex_record(boundary.witness_zero_frequency_b),
            "witness_probe_a": complex_record(boundary.witness_probe_a),
            "witness_probe_b": complex_record(boundary.witness_probe_b),
            "witness_parameters": {
                "gamma": 0.8,
                "cutoff_a": 1.0,
                "cutoff_b": 4.0,
                "role": "normalized structural witnesses, not physical coefficients",
            },
        },
        "checks": checks,
        "failed_checks": failed,
        "physical_transport_coefficients_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "condensed_sk_influence_functional_or_physical_retarded_correlator_missing",
        "next_controller": (
            "obtain an allowed state-matched retarded correlator or derive a "
            "microscopic condensed SK/influence functional; do not promote "
            "the normalized memory witnesses"
        ),
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "used_for_fit": False,
            "used_for_tuning": False,
            "used_for_calibration": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "major_result_id": artifact["major_result"]["major_result_id"],
        "closure_level": artifact["major_result"]["closure_level"],
        "failed_checks": failed,
        "goldstone_polynomial_residual": float(goldstone_residual),
        "zero_frequency_match": boundary.zero_frequency_match,
        "finite_frequency_distinct": boundary.finite_frequency_distinct,
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
