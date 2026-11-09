"""Topic 0.11 dependency gate for the core Noether/phase-field map.

This verifier performs no simulation and no parameter fit.  It checks whether
the core Wave 9 coordinate result can be consumed by Topic 0.11 without
silently identifying the topic's normalized order parameter with a microscopic
field, a Noether charge, UET Phi, or a derived trace.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _bootstrap() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("UET repository root not found")


ROOT = _bootstrap()
TOPIC = "0.11_Phase_Transitions"
TOPIC_DIR = ROOT / "docs" / "topics" / TOPIC
DATA_DIR = TOPIC_DIR / "Data" / "03_Research"
ARTIFACT_DIR = TOPIC_DIR / "Result" / "artifacts"

CORE_VERIFICATION_DIR = ROOT / "docs" / "core" / "07_artifacts" / "verification"
CORE_GATE_DIR = ROOT / "docs" / "core" / "07_artifacts" / "gates"
CORE_STATE_MAP = CORE_VERIFICATION_DIR / "noether_phase_field_state_map_verification.json"
CORE_FORMULA_AUDIT = ROOT / "docs" / "core" / "07_artifacts" / "correspondence" / "noether_phase_field_map_formula_audit.json"
CORE_DEPENDENCY_GATE = CORE_GATE_DIR / "noether_phase_field_dependency_gate.json"
CORE_PROGRAM_GATE = CORE_GATE_DIR / "uet_gr_research_program_gate.json"
WAVE55_GATE = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_next_path_decision_gate.json"
MATTER_SPACE_PILOT = ARTIFACT_DIR / "0_11_matter_space_coupled_diagnostic.json"
READINESS_METADATA = ROOT / "docs" / "meta" / "topic_readiness.json"

# A candidate manifest is now present at this path.  It must still satisfy the
# explicit acceptance contract below; declaration alone is not sufficient to
# promote the topic field.
TOPIC_CHARGE_MAP = DATA_DIR / "noether_charge_coordinate_mapping.json"

ARTIFACT_PATH = ARTIFACT_DIR / "0_11_noether_phase_field_dependency_gate.json"
CONTROLLING_BLOCKER = "topic_0_11_signed_noether_charge_eos_transport_matching_missing"
TOPIC_CONTROLLER = "ch_finite_k_replicate_temporal_acquisition_plan_defined_execution_open"

VOLATILE_JSON_KEYS = frozenset({"generated_at", "timestamp_utc", "environment"})


def relpath(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _strip_volatile(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_volatile(item)
            for key, item in sorted(value.items())
            if key not in VOLATILE_JSON_KEYS
        }
    if isinstance(value, list):
        return [_strip_volatile(item) for item in value]
    return value


def scientific_payload_sha256(path: Path) -> str:
    """Hash semantic JSON content while excluding declared run-time metadata."""

    payload = _strip_volatile(load_json(path))
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def gate(status: str, required_condition: str, **details: Any) -> dict[str, Any]:
    return {"status": status, "required_condition": required_condition, **details}


def _readiness_topic(metadata: dict[str, Any]) -> dict[str, Any]:
    for topic in metadata.get("topics", []):
        if topic.get("name") == TOPIC:
            return topic
    raise RuntimeError(f"Canonical readiness entry not found for {TOPIC}")


def _formula_registry(audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in audit.get("formula_registry", [])}


def _accepted_topic_charge_map() -> tuple[bool, dict[str, Any] | None]:
    if not TOPIC_CHARGE_MAP.exists():
        return False, None
    mapping = load_json(TOPIC_CHARGE_MAP)
    accepted = (
        mapping.get("status") == "ACCEPTED"
        and mapping.get("physical_conserved_variable") == "signed_O2_noether_charge"
        and mapping.get("coarse_graining_prescription_status") == "PASS"
        and mapping.get("equation_of_state_matching_status") == "PASS"
        and mapping.get("transport_matching_status") == "PASS"
        and bool(mapping.get("source_records"))
    )
    return accepted, mapping


def _input_record(path: Path, role: str) -> dict[str, Any]:
    return {
        "path": relpath(path),
        "role": role,
        "exists": path.exists(),
        "scientific_payload_sha256": scientific_payload_sha256(path),
        "hash_scope": "canonical_json_without_generated_at_timestamp_utc_or_environment",
    }


def build_artifact() -> dict[str, Any]:
    state_map = load_json(CORE_STATE_MAP)
    formula_audit = load_json(CORE_FORMULA_AUDIT)
    core_dependency = load_json(CORE_DEPENDENCY_GATE)
    program = load_json(CORE_PROGRAM_GATE)
    wave55 = load_json(WAVE55_GATE)
    matter_space = load_json(MATTER_SPACE_PILOT)
    readiness_metadata = load_json(READINESS_METADATA)
    readiness = _readiness_topic(readiness_metadata)
    registry = _formula_registry(formula_audit)
    charge_map_accepted, charge_map = _accepted_topic_charge_map()

    thresholds = state_map.get("thresholds", {})
    numeric = state_map.get("numeric", {})
    achieved = state_map.get("achieved_gates", {})
    blocked = state_map.get("blocked_gates", {})

    coordinate_checks = {
        "core_audit_pass": state_map.get("audit_status") == "PASS",
        "partial_coordinate_evidence_only": state_map.get("evidence_status")
        == "PARTIAL_HYDRODYNAMIC_STATE_COORDINATE_MAP",
        "signed_charge_declared": achieved.get("signed_O2_charge_variable_declared") == "PASS",
        "affine_coordinate_pass": achieved.get("affine_coarse_density_coordinate_bijection") == "PASS",
        "continuity_scale_pass": achieved.get("continuity_and_current_scale_map") == "PASS",
        "affine_roundtrip_within_threshold": numeric.get("maximum_affine_roundtrip_error", float("inf"))
        <= thresholds.get("maximum_affine_roundtrip_error", 0.0),
        "continuity_scaling_within_threshold": numeric.get("maximum_continuity_scaling_error", float("inf"))
        <= thresholds.get("maximum_continuity_scaling_error", 0.0),
    }
    coordinate_pass = all(coordinate_checks.values())

    microscopic_boundary_checks = {
        "microscopic_counterexample_pass": achieved.get("microscopic_noninvertibility_counterexample") == "PASS",
        "coarse_graining_counterexample_pass": achieved.get("coarse_graining_noninvertibility_counterexample")
        == "PASS",
        "microscopic_difference_resolved": numeric.get("microscopic_state_difference", 0.0)
        >= thresholds.get("minimum_microscopic_state_difference", float("inf")),
        "coarse_microstate_difference_resolved": numeric.get("coarse_microstate_difference", 0.0)
        >= thresholds.get("minimum_coarse_microstate_difference", float("inf")),
        "inverse_shortcut_forbidden": "do_not_invert_C_to_microscopic_O2_fields"
        in core_dependency.get("forbidden_shortcuts", []),
    }
    microscopic_boundary_pass = all(microscopic_boundary_checks.values())

    trace_space_checks = {
        "core_trace_and_space_absent": numeric.get("trace_and_space_response_absent") is True,
        "core_trace_feedback_forbidden": "do_not_import_trace_as_state_or_feedback"
        in core_dependency.get("forbidden_shortcuts", []),
        "matter_space_trace_switch_invariant": matter_space.get("metrics", {}).get(
            "trace_switch_physical_difference"
        )
        == 0.0,
        "matter_space_history_invariant": matter_space.get("metrics", {}).get(
            "different_trace_history_physical_difference"
        )
        == 0.0,
        "matter_space_trace_backreaction_false": matter_space.get("run_integrity", {}).get("trace_backreaction")
        is False,
    }
    trace_space_pass = all(trace_space_checks.values())

    wave55_gates = wave55.get("gates", {})
    wave55_checks = {
        "status_warn": wave55.get("status") == "WARN",
        "controller_unchanged": wave55.get("blocker_label") == TOPIC_CONTROLLER,
        "replicate_temporal_path_selected": wave55.get("selected_next_path")
        == "replicate_temporal_acquisition",
        "estimator_acceptance_blocked": wave55_gates.get("estimator_acceptance_gate", {}).get("status")
        == "BLOCKED",
        "exponent_rerun_blocked": wave55_gates.get("exponent_rerun_gate", {}).get("status") == "BLOCKED",
    }
    wave55_pass = all(wave55_checks.values())

    constitutive_checks = {
        "formula_audit_warn": formula_audit.get("status") == "WARN",
        "double_well_is_constitutive": registry.get("symmetric_double_well_conjugacy", {}).get("status")
        == "DERIVED_EXACT_CONSTITUTIVE",
        "normalized_scales_are_not_microscopic_derivation": registry.get(
            "normalized_constitutive_scales", {}
        ).get("status")
        == "DIMENSIONAL_COORDINATE_MAP_NOT_MICROSCOPIC_DERIVATION",
        "equation_of_state_still_blocked": blocked.get("equation_of_state_from_covariant_O2_action")
        == "BLOCKED_CONTROLLING",
        "transport_matching_still_blocked": blocked.get("susceptibility_and_transport_coefficient_matching")
        == "BLOCKED",
    }

    canonical_status_pass = readiness.get("status") == "Structured" and readiness.get("audit_tier") == "B"
    historical_snapshot = matter_space.get("topic_readiness_before_after", [])
    historical_snapshot_drift = bool(historical_snapshot) and historical_snapshot[-1] != readiness.get("status")

    gates = {
        "core_hydrodynamic_coordinate_gate": gate(
            "PASS" if coordinate_pass else "BLOCKED",
            "The core result must verify only the fixed-scale affine coarse charge-density/current coordinate layer.",
            checks=coordinate_checks,
            map="C=(n_bar-n_ref)/n_scale; J=j_bar/(n_scale*L/T)",
        ),
        "microscopic_inverse_boundary_gate": gate(
            "PASS" if microscopic_boundary_pass else "BLOCKED",
            "Microscopic and coarse-graining inverses must remain rejected as many-to-one.",
            checks=microscopic_boundary_checks,
        ),
        "topic_C_signed_charge_identity_gate": gate(
            "PASS" if charge_map_accepted else "BLOCKED",
            "Topic 0.11 C may be identified with a signed O2 charge coordinate only after an accepted system-specific mapping, coarse-graining prescription, EOS match, transport match, and source package.",
            mapping_path=relpath(TOPIC_CHARGE_MAP),
            mapping_exists=TOPIC_CHARGE_MAP.exists(),
            mapping_status=None if charge_map is None else charge_map.get("status"),
        ),
        "equation_of_state_and_transport_gate": gate(
            "BLOCKED",
            "The phase-field free energy and transport coefficients require independent O2 equation-of-state and covariant transport matching.",
            checks=constitutive_checks,
            core_controller=core_dependency.get("controlling_blocker"),
        ),
        "trace_and_space_separation_gate": gate(
            "PASS" if trace_space_pass else "BLOCKED",
            "Neither derived trace R nor matter-space Phi may be imported into the Noether coordinate map or used as hidden feedback.",
            checks=trace_space_checks,
        ),
        "wave55_controller_preservation_gate": gate(
            "PASS" if wave55_pass else "BLOCKED",
            "The Noether dependency lane must not replace Topic 0.11's accepted-estimator controller.",
            checks=wave55_checks,
            topic_controller=TOPIC_CONTROLLER,
        ),
        "canonical_topic_status_gate": gate(
            "PASS" if canonical_status_pass else "BLOCKED",
            "Topic status must be read from docs/meta/topic_readiness.json without promotion by this dependency wave.",
            status_before=readiness.get("status"),
            status_after=readiness.get("status"),
            tier_before=readiness.get("audit_tier"),
            tier_after=readiness.get("audit_tier"),
        ),
        "historical_pilot_status_snapshot_gate": gate(
            "WARN" if historical_snapshot_drift else "PASS",
            "Historical pilot artifacts are not rewritten solely to update later canonical readiness metadata.",
            historical_snapshot=historical_snapshot,
            canonical_status=readiness.get("status"),
            drift_detected=historical_snapshot_drift,
        ),
        "global_closure_boundary_gate": gate(
            "PASS"
            if program.get("global_universe_closure") == "UNRESOLVED"
            and program.get("gr_null_model", {}).get("value") == 0
            else "BLOCKED",
            "The exact epsilon_nc=0 GR response-null must not be relabeled as proof that the universe is globally closed.",
            global_universe_closure=program.get("global_universe_closure"),
            gr_null_model=program.get("gr_null_model"),
        ),
        "topic_promotion_gate": gate(
            "BLOCKED",
            "Coordinate compatibility alone cannot promote the estimator, exponent, universality, material, RG, external-validation, or theory claim.",
        ),
    }

    input_paths = [
        (CORE_STATE_MAP, "Core Wave 9 state-coordinate verification"),
        (CORE_FORMULA_AUDIT, "Core Wave 9 formula audit"),
        (CORE_DEPENDENCY_GATE, "Core Wave 9 dependency gate"),
        (CORE_PROGRAM_GATE, "Core GR research-program gate"),
        (WAVE55_GATE, "Topic 0.11 accepted-estimator controller"),
        (MATTER_SPACE_PILOT, "Topic 0.11 isolated matter-space pilot"),
        (READINESS_METADATA, "Canonical topic readiness metadata"),
    ]
    if TOPIC_CHARGE_MAP.exists():
        input_paths.append((TOPIC_CHARGE_MAP, "Topic 0.11 candidate signed-charge mapping manifest"))

    return {
        "schema_version": "1.0",
        "artifact": "0_11_noether_phase_field_dependency_gate",
        "topic": TOPIC,
        "version": "core_wave9_topic_dependency_v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Noether_Phase_Field_Dependency_Gate.py",
        "benchmark_role": "DEPENDENCY_ONLY_NO_SIMULATION",
        "status": "BLOCKED",
        "evidence_status": "CONDITIONAL_HYDRODYNAMIC_COORDINATE_COMPATIBILITY",
        "claim_class": "internal_dependency_boundary",
        "controlling_blocker": CONTROLLING_BLOCKER,
        "topic_controlling_blocker_unchanged": TOPIC_CONTROLLER,
        "topic_status_impact": "NONE",
        "canonical_topic_status": readiness.get("status"),
        "canonical_topic_tier": readiness.get("audit_tier"),
        "global_universe_closure": "UNRESOLVED",
        "scientific_inputs": [_input_record(path, role) for path, role in input_paths],
        "gates": gates,
        "completed_scope": [
            "fixed-scale affine map from coarse signed O2 charge density/current to normalized C/J coordinates",
            "continuity-residual scale transformation",
            "explicit microscopic and coarse-graining noninvertibility boundary",
            "trace and Phi exclusion from the coordinate map",
        ],
        "blocked_scope": [
            "identification of the current Topic 0.11 C field as signed O2 charge",
            "equation of state derived from the covariant O2 action",
            "susceptibility and transport coefficient matching",
            "source-equivalent phase-field amplitude and averaging convention",
            "estimator acceptance and exponent rerun",
            "universality, material, RG, external-validation, global-closure, or solved-theory promotion",
        ],
        "required_next_evidence": [
            "declare and source a system-specific conserved signed O2 charge variable for Topic 0.11, or explicitly reject that identity",
            "specify a covariant coarse-graining prescription from Noether current to the topic field",
            "derive or independently calibrate the charge-density equation of state without fitting the evaluation set",
            "match susceptibility, mobility, relaxation, and gradient coefficients to the covariant transport theory",
            "keep Wave 55 replicate/temporal acquisition as the independent estimator controller",
        ],
        "allowed_language": [
            "conditional hydrodynamic state-coordinate compatibility",
            "exact affine map after a signed O2 charge declaration and fixed scales",
            "microscopic reconstruction is many-to-one",
            "constitutive double-well coordinate map",
        ],
        "blocked_language": [
            "Topic 0.11 C is derived from the microscopic O2 field",
            "the double-well equation of state is derived from the O2 action",
            "the Noether map validates the matter-space Phi field or trace",
            "the Noether map accepts the finite-k estimator or critical exponent",
            "epsilon_nc=0 proves that the universe is globally closed",
            "Topic 0.11 is externally validated or solved",
        ],
        "limitations": [
            "No simulation, parameter fit, estimator rerun, or external-data comparison is performed.",
            "The present Topic 0.11 field has only a declared candidate signed-O2-charge mapping manifest; acceptance remains blocked.",
            "The exact affine layer is a coordinate result, not a microscopic derivation or physical equation of state.",
            "The historical matter-space pilot retains its run-time Draft snapshot; canonical metadata now controls status.",
        ],
        "claim_boundary": (
            "Core Wave 9 can support only a conditional coarse hydrodynamic coordinate interpretation in Topic 0.11. "
            "It does not identify the existing C field as a signed O2 charge, derive the double-well EOS or transport, "
            "introduce Phi or trace feedback, alter the Wave 55 controller, or promote topic status or claims."
        ),
        "environment": {
            # Runtime metadata is descriptive only; keep the artifact portable
            # across local and CI patch versions and operating systems.
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "platform": "portable-research-runtime",
        },
    }


def main() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    artifact = build_artifact()
    ARTIFACT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    return artifact


if __name__ == "__main__":
    result = main()
    print(
        json.dumps(
            {
                "status": result["status"],
                "evidence_status": result["evidence_status"],
                "controlling_blocker": result["controlling_blocker"],
                "topic_controlling_blocker_unchanged": result[
                    "topic_controlling_blocker_unchanged"
                ],
                "gates": {
                    name: value["status"]
                    for name, value in result["gates"].items()
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
