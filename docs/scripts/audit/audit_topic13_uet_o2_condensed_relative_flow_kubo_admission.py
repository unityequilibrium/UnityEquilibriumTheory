"""Audit the state-matched Kubo admission record for Topic 13."""

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

from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402
from docs.core.uet_o2_condensed_relative_flow_kubo_admission import (  # noqa: E402
    ACCEPTED_EVIDENCE_STATUSES,
    KUBO_ADMISSION_STATUS,
    KUBO_EVIDENCE_STATUS,
    KUBO_FORMULA_ID,
    condensed_relative_flow_kubo_admission_contract,
    condensed_relative_flow_kubo_admission_state,
)
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_condensed_relative_flow_kubo_admission_audit.json"
MODULE = ROOT / "docs/core/uet_o2_condensed_relative_flow_kubo_admission.py"
LOOP_MODULE = ROOT / "docs/core/uet_o2_condensed_loop_renormalized_vertex.py"
REGISTRY = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"


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
    loop_hash = sha256(LOOP_MODULE)
    state = condensed_relative_flow_kubo_admission_state(
        0.20,
        1.28,
        0.15,
        source_path_or_url="docs/core/uet_o2_condensed_loop_renormalized_vertex.py",
        source_hash=loop_hash,
        reference_space_response=0.0,
        config=_config(),
        loop_state=None,
    )
    contract = condensed_relative_flow_kubo_admission_contract()
    record = state.record()
    required = contract["required_coefficient_fields"]
    checks = {
        "admission_status_is_kubo_matched": state.evidence_status == KUBO_EVIDENCE_STATUS,
        "all_required_fields_are_present": all(key in record for key in required),
        "accepted_evidence_status_is_declared": state.evidence_status in ACCEPTED_EVIDENCE_STATUSES,
        "coefficient_is_positive_and_finite": state.value > 0.0 and math.isfinite(state.value),
        "units_are_explicitly_natural_not_si": "natural-unit" in state.units and "not SI" in state.units,
        "state_match_is_explicit": state.state_match,
        "correlator_formula_is_registry_id": state.correlator_formula_id == KUBO_FORMULA_ID,
        "source_hash_matches_loop_module": state.source_hash == loop_hash,
        "uncertainty_is_finite_and_within_unchanged_threshold": (
            math.isfinite(state.uncertainty)
            and state.uncertainty >= 0.0
            and state.uncertainty <= 1.0e-2
        ),
        "uncertainty_scope_is_narrow": "numerical quadrature" in state.uncertainty_scope,
        "target_and_holdout_are_independent": state.independent_of_target_data,
        "holdout_is_unread": state.holdout_accessed is False,
        "no_parameter_fitting": state.parameter_fitting_performed is False,
        "physical_kubo_admission_completed": state.physical_kubo_admission_completed,
        "full_core_unlock_remains_false": state.full_core_unlock is False,
        "registry_contains_correlator_id": any(
            entry.get("equation_id") == KUBO_FORMULA_ID
            for entry in json.loads(REGISTRY.read_text(encoding="utf-8-sig")).get("entries", [])
        ),
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_is_derived": "not an independent state" in contract["unit_contract"]["R_gen"],
        "R_obs_is_separate": "observer record" in contract["unit_contract"]["R_obs"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = KUBO_ADMISSION_STATUS if not failed else (
        "BLOCKED_T13_CONDENSED_RELATIVE_FLOW_KUBO_ADMISSION"
    )
    evidence = [
        {"path": "docs/core/uet_o2_condensed_relative_flow_kubo_admission.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/uet_o2_condensed_loop_renormalized_vertex.py", "sha256": loop_hash},
        {"path": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json", "sha256": sha256(REGISTRY)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-condensed-relative-flow-kubo-admission-v1",
        "artifact": "t13_uet_o2_condensed_relative_flow_kubo_admission_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CONDENSED_RELATIVE_FLOW_KUBO_ADMISSION_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the declared coefficient record contains the transport-contract fields",
                "the zero-frequency retarded coefficient is matched to the loop-renormalized relative-flow response",
                "state, correlator formula, source hash, evidence status, and numerical uncertainty are explicit",
                "admission remains scoped to one natural-unit condensed contact channel",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "independent_physical_condensed_vertex_anchor_missing",
                "complete_condensed_1PI_vertex_and_scattering_channels_missing",
                "full_interacting_SK_KMS_match_missing",
                "complete_two_fluid_constitutive_tensor_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": (
                "state-matched Kubo admission for one declared condensed relative-flow natural-unit channel only; "
                "full physical transport, SI, complete SK/KMS, Core, Gravity, alpha, and external-validation dependencies remain blocked"
            ),
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {
            "admission": asdict(state),
            "coefficient_record": record,
        },
        "checks": checks,
        "failed_checks": failed,
        "physical_kubo_coefficient_emitted": state.physical_kubo_admission_completed,
        "physical_kubo_admission_completed": state.physical_kubo_admission_completed,
        "physical_kubo_admission_scope": contract["scope"],
        "physical_anchor_supplied": state.physical_anchor_supplied,
        "full_core_unlock": False,
        "numeric_alpha_phi_k_emitted": False,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": not state.independent_of_target_data,
        "xie_2026_accessed": state.holdout_accessed,
        "controlling_blocker": "independent_physical_condensed_vertex_anchor_missing",
        "next_controller": (
            "source-lock an independent physical condensed vertex anchor or complete the full interacting SK/KMS and all-channel match; "
            "retain the admitted coefficient as natural-unit lane evidence and do not promote it to SI or Full Topic 13"
        ),
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "used_for_fit": False,
            "used_for_tuning": False,
            "used_for_calibration": False,
            "used_for_threshold_adjustment": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "failed_checks": failed,
        "closure_level": artifact["major_result"]["closure_level"],
        "coefficient_name": state.coefficient_name,
        "value": state.value,
        "units": state.units,
        "uncertainty": state.uncertainty,
        "evidence_status": state.evidence_status,
        "physical_kubo_admission_completed": state.physical_kubo_admission_completed,
        "full_core_unlock": False,
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
