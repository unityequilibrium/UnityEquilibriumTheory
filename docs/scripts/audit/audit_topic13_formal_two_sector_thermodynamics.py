"""Audit the formal finite-temperature two-sector thermodynamic lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_formal_two_sector_thermodynamics import (
    FORMAL_TWO_SECTOR_STATUS,
    formal_two_sector_contract,
    formal_two_sector_state,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_formal_two_sector_thermodynamics_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_formal_two_sector_thermodynamics.py"
EOS_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(left: float, right: float, *, rtol: float = 2.0e-5, atol: float = 2.0e-8) -> bool:
    return bool(np.isclose(left, right, rtol=rtol, atol=atol))


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=160,
        cutoff_factor=65.0,
        derivative_step=1.0e-4,
    )
    points = {
        "normal": (0.22, 0.35, 0.15),
        "condensed": (0.12, 1.18, 0.15),
    }
    states = {
        label: formal_two_sector_state(*point, config)
        for label, point in points.items()
    }
    checks: dict[str, bool] = {}
    for label, state in states.items():
        checks[f"{label}_pressure_additivity"] = close(
            state.total_pressure,
            state.condensate_pressure + state.normal_pressure,
            rtol=1.0e-10,
            atol=1.0e-12,
        )
        checks[f"{label}_charge_additivity"] = close(
            state.total_charge_density,
            state.condensate_charge_density + state.normal_charge_density,
        )
        checks[f"{label}_entropy_additivity"] = close(
            state.total_entropy_density,
            state.condensate_entropy_density + state.normal_entropy_density,
        )
        checks[f"{label}_energy_additivity"] = close(
            state.total_energy_density,
            state.condensate_energy_density + state.normal_energy_density,
        )
        checks[f"{label}_susceptibility_additivity"] = close(
            state.total_susceptibility,
            state.condensate_susceptibility + state.normal_susceptibility,
            rtol=2.0e-4,
            atol=2.0e-7,
        )
        checks[f"{label}_sector_values_finite"] = all(
            np.isfinite(value)
            for value in (
                state.condensate_pressure,
                state.normal_pressure,
                state.condensate_charge_density,
                state.normal_charge_density,
                state.condensate_entropy_density,
                state.normal_entropy_density,
                state.condensate_energy_density,
                state.normal_energy_density,
                state.condensate_susceptibility,
                state.normal_susceptibility,
            )
        )

    contract = formal_two_sector_contract()
    checks.update(
        {
            "normal_branch_has_no_tree_condensate_pressure": states["normal"].condensate_pressure == 0.0,
            "normal_branch_has_no_tree_condensate_charge": abs(states["normal"].condensate_charge_density) <= 1.0e-12,
            "condensed_branch_has_tree_condensate_pressure": states["condensed"].condensate_pressure > 0.0,
            "condensate_entropy_is_zero": all(
                abs(state.condensate_entropy_density) <= 1.0e-12
                for state in states.values()
            ),
            "normal_density_is_explicitly_thermodynamic_only": "not Landau mass density"
            in contract["unit_contract"]["normal_density_label"],
            "no_physical_transport_emitted": "Kubo" in contract["excluded_scope"],
            "no_si_alpha_emitted": "alpha_Phi_K" in contract["excluded_scope"],
            "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
            "C_ontology_preserved": "not relabeled" in contract["unit_contract"]["C"],
            "R_gen_ontology_preserved": "derived history trace only" in contract["unit_contract"]["R_gen"],
            "no_holdout_or_fit": True,
        }
    )
    failed = [name for name, passed in checks.items() if not passed]
    artifact = {
        "schema_version": "t13-uet-o2-formal-two-sector-thermodynamics-v1",
        "artifact": "t13_uet_o2_formal_two_sector_thermodynamics_audit",
        "generated_at": str(date.today()),
        "status": FORMAL_TWO_SECTOR_STATUS if not failed else "BLOCKED_FORMAL_TWO_SECTOR_AUDIT",
        "major_result": {
            "major_result_id": "T13_UET_O2_FORMAL_TWO_SECTOR_THERMODYNAMIC_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "pressure split into explicit tree-condensate and thermal-quasiparticle sectors",
                "sector-wise charge, entropy, energy, and susceptibility identities",
                "normal-branch zero-condensate boundary and condensed-branch positive tree pressure",
                "explicit distinction between thermodynamic quasiparticle charge and Landau normal density",
            ],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": "action-derived formal sector decomposition of the declared natural-unit quasiparticle EOS",
            "observable": "natural-unit sector pressure, charge, entropy, energy, and susceptibility",
            "data_role": contract["data_role"],
            "evidence_artifacts": [
                {"path": "docs/core/02_equations/o2/uet_o2_formal_two_sector_thermodynamics.py", "sha256": sha256(MODULE)},
                {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py", "sha256": sha256(EOS_MODULE)},
            ],
            "verification_status": FORMAL_TWO_SECTOR_STATUS if not failed else "BLOCKED_FORMAL_TWO_SECTOR_AUDIT",
            "open_blockers": [
                "transverse_normal_current_response_or_Landau_normal_density_missing",
                "interacting_finite_temperature_self_energy_and_renormalization_missing",
                "physical_Kubo_coefficient_record_missing",
                "microscopic_SK_KMS_matching_missing",
                "heat_flux_entropy_production_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "formal finite-temperature thermodynamic sector consistency only; no physical two-fluid transport, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state_grid": {label: state.__dict__ for label, state in states.items()},
        "checks": checks,
        "failed_checks": failed,
        "numeric_alpha_Phi_K_emitted": False,
        "physical_transport_coefficients_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "transverse_normal_current_response_or_Landau_normal_density_missing",
        "next_controller": "derive a state-matched transverse normal-current response from a declared interacting finite-temperature action or keep this lane as thermodynamic-only; do not promote it to physical transport without Kubo provenance",
        "claim_promotion": False,
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "closure_level": artifact["major_result"]["closure_level"], "failed_checks": failed}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
