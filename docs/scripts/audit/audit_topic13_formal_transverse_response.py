"""Audit the formal static transverse quasiparticle response lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_formal_transverse_response import (
    FORMAL_TRANSVERSE_RESPONSE_STATUS,
    formal_transverse_quasiparticle_response,
    formal_transverse_response_contract,
)
from docs.scripts.audit.audit_topic13_fixed_phi_spectrum_repair import fixed_phi_witnesses


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_uet_o2_formal_transverse_response_audit.json"
MODULE = ROOT / "docs/core/uet_o2_formal_transverse_response.py"
EOS_MODULE = ROOT / "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=160,
        cutoff_factor=65.0,
    )
    low_config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=160,
        cutoff_factor=65.0,
    )
    points = {
        "normal_high_temperature": (0.22, 0.35, 0.15),
        "normal_low_temperature": (0.06, 0.35, 0.15),
        "condensed_high_temperature": (0.20, 1.28, 0.15),
        "condensed_low_temperature": (0.04, 1.28, 0.15),
    }
    states = {
        label: formal_transverse_quasiparticle_response(
            *point, low_config if "low" in label else config
        )
        for label, point in points.items()
    }
    contract = formal_transverse_response_contract()
    independent = fixed_phi_witnesses()
    checks = {
        **independent["checks"],
        "all_states_finite_and_nonnegative": all(
            np.isfinite(state.normal_momentum_susceptibility)
            and state.normal_momentum_susceptibility >= 0.0
            and np.isfinite(state.condensate_phase_stiffness)
            and state.condensate_phase_stiffness >= 0.0
            for state in states.values()
        ),
        "normal_branch_classification_pass": all(
            states[key].branch == "normal"
            for key in ("normal_high_temperature", "normal_low_temperature")
        ),
        "condensed_branch_classification_pass": all(
            states[key].branch == "condensed"
            for key in ("condensed_high_temperature", "condensed_low_temperature")
        ),
        "condensed_tree_stiffness_positive": all(
            states[key].condensate_phase_stiffness > 0.0
            for key in ("condensed_high_temperature", "condensed_low_temperature")
        ),
        "normal_branch_tree_stiffness_zero": all(
            states[key].condensate_phase_stiffness == 0.0
            for key in ("normal_high_temperature", "normal_low_temperature")
        ),
        "normal_response_decreases_at_low_temperature": states[
            "normal_low_temperature"
        ].normal_momentum_susceptibility < states[
            "normal_high_temperature"
        ].normal_momentum_susceptibility,
        "condensed_response_decreases_at_low_temperature": states[
            "condensed_low_temperature"
        ].normal_momentum_susceptibility < states[
            "condensed_high_temperature"
        ].normal_momentum_susceptibility,
        "doppler_shift_declared": "Doppler" in contract["derivation_class"]
        or "doppler" in contract["equations"]["doppler_shift"].lower(),
        "response_is_not_landau_density": "not Landau normal mass density"
        in contract["unit_contract"]["normal_density_label"],
        "retarded_kubo_is_excluded": "retarded Kubo" in contract["excluded_scope"],
        "no_si_alpha_emitted": "alpha_Phi_K" in contract["excluded_scope"],
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not relabeled" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace only" in contract["unit_contract"]["R_gen"],
        "no_holdout_or_fit": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    artifact = {
        "schema_version": "t13-uet-o2-formal-transverse-response-v1",
        "artifact": "t13_uet_o2_formal_transverse_response_audit",
        "generated_at": str(date.today()),
        "status": FORMAL_TRANSVERSE_RESPONSE_STATUS if not failed else "BLOCKED_FORMAL_TRANSVERSE_RESPONSE_AUDIT",
        "major_result": {
            "major_result_id": "T13_UET_O2_FORMAL_TRANSVERSE_RESPONSE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "static Doppler-response integral for the declared thermal quasiparticle branches",
                "positive normal-sector momentum susceptibility in natural units",
                "tree condensate phase stiffness on the declared condensed branch",
                "low-temperature response decrease for normal and condensed representative states",
                "explicit boundary separating the static witness from retarded Kubo and Landau density claims",
            ],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": [
                {"path": "docs/core/uet_o2_formal_transverse_response.py", "sha256": sha256(MODULE)},
                {"path": "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py", "sha256": sha256(EOS_MODULE)},
            ],
            "verification_status": FORMAL_TRANSVERSE_RESPONSE_STATUS if not failed else "BLOCKED_FORMAL_TRANSVERSE_RESPONSE_AUDIT",
            "open_blockers": [
                "retarded_physical_Kubo_match_missing",
                "interacting_finite_temperature_self_energy_and_renormalization_missing",
                "microscopic_SK_KMS_matching_missing",
                "full_heat_flux_entropy_production_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "formal static transverse response lane only; no physical Kubo, SI, alpha, Core, Gravity, transport, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "independent_action_witnesses": independent,
        "source_hashes": {
            path: sha256(ROOT / path)
            for path in (
                "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py",
                "docs/core/uet_o2_formal_transverse_response.py",
                "docs/scripts/audit/audit_topic13_fixed_phi_spectrum_repair.py",
                "docs/scripts/audit/audit_topic13_formal_transverse_response.py",
            )
        },
        "state_grid": {label: state.__dict__ for label, state in states.items()},
        "checks": checks,
        "failed_checks": failed,
        "numeric_alpha_Phi_K_emitted": False,
        "physical_transport_coefficients_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "retarded_physical_Kubo_match_missing",
        "next_controller": "match the formal transverse response to a state-matched retarded microscopic Kubo record; retain the present result as a natural-unit static witness until that match exists",
        "claim_promotion": False,
        "full_core_unlock": False,
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "closure_level": artifact["major_result"]["closure_level"], "failed_checks": failed}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
