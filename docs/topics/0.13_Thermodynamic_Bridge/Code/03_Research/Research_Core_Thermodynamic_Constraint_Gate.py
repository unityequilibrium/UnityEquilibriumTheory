"""Constraint-only bridge from Topic 0.13 into the core GR response program.

This verifier does not rerun Landauer, Cattaneo, or matter-space simulations.
It records which standard thermodynamic constraints may be inherited and which
UET-specific EOS, transport, entropy-current, and observable maps remain open.
"""

from __future__ import annotations

import hashlib
import json
import platform
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
TOPIC = "0.13_Thermodynamic_Bridge"
TOPIC_DIR = ROOT / "docs" / "topics" / TOPIC
ARTIFACT_DIR = TOPIC_DIR / "Result" / "artifacts"
DATA_DIR = TOPIC_DIR / "Data" / "03_Research"

TOPIC_PRIMARY = ARTIFACT_DIR / "0_13_thermodynamic_bridge_verification.json"
FOUNDATION_GATE = DATA_DIR / "thermodynamic_bridge_foundation_claim_gate.json"
CATTANEO_ARTIFACT = ARTIFACT_DIR / "cattaneo_benchmark_artifact.json"
THERMAL_PILOT = ARTIFACT_DIR / "matter_space_thermal_control.json"
CORE_PROGRAM = ROOT / "docs/core/07_artifacts/gates/uet_gr_research_program_gate.json"
CORE_STATE_MAP = ROOT / "docs/core/07_artifacts/gates/noether_phase_field_dependency_gate.json"
READINESS_METADATA = ROOT / "docs/meta/topic_readiness.json"

ARTIFACT_PATH = ARTIFACT_DIR / "0_13_core_thermodynamic_constraint_gate.json"
CONTROLLING_BLOCKER = "topic_0_13_constraint_only_eos_transport_entropy_bridge_missing"
VOLATILE_JSON_KEYS = frozenset(
    {"generated_at", "generated_at_utc", "timestamp_utc", "environment"}
)


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


def _input_record(path: Path, role: str) -> dict[str, Any]:
    return {
        "path": relpath(path),
        "role": role,
        "exists": path.exists(),
        "scientific_payload_sha256": scientific_payload_sha256(path),
        "hash_scope": (
            "canonical_json_without_generated_at_generated_at_utc_"
            "timestamp_utc_or_environment"
        ),
    }


def _foundation_boundary_statuses(foundation: dict[str, Any]) -> dict[str, str]:
    """Recover conservative boundary statuses from the source claim gate.

    An older aggregate rerun may replace the Topic 0.13 primary artifact with
    a reduced schema that omits the embedded derivation/unit/mapping fields.
    The foundation claim gate remains authoritative for those blocked
    boundaries, so consuming it does not promote a claim or invent a result.
    """

    blockers: list[str] = []
    for export in foundation.get("blocked_foundation_exports", []):
        for blocker in export.get("blockers", []):
            if isinstance(blocker, str):
                blockers.append(blocker)

    prefixes = {
        "derivation": "Bridge derivation map status: ",
        "units": "Units contract status: ",
        "landauer": "Landauer-UET mapping status: ",
        "beta": "Beta role clarification status: ",
    }
    values: dict[str, str] = {}
    for key, prefix in prefixes.items():
        for blocker in blockers:
            if blocker.startswith(prefix):
                values[key] = blocker[len(prefix) :]
                break
    return values


def build_artifact() -> dict[str, Any]:
    primary = load_json(TOPIC_PRIMARY)
    foundation = load_json(FOUNDATION_GATE)
    cattaneo = load_json(CATTANEO_ARTIFACT)
    thermal = load_json(THERMAL_PILOT)
    core_program = load_json(CORE_PROGRAM)
    core_state = load_json(CORE_STATE_MAP)
    readiness = _readiness_topic(load_json(READINESS_METADATA))
    foundation_boundary = _foundation_boundary_statuses(foundation)

    accepted_exports = {
        item.get("export_id"): item
        for item in foundation.get("accepted_foundation_exports", [])
    }
    blocked_exports = {
        item.get("export_id"): item
        for item in foundation.get("blocked_foundation_exports", [])
    }
    row_controllers = foundation.get("row_controller_summary", [])

    foundation_checks = {
        "foundation_warn": foundation.get("status") == "FOUNDATION_WARN",
        "claim_ceiling_is_C": foundation.get("claim_ceiling")
        == "C - formula/lower-bound consistency only",
        "landauer_export_pass": accepted_exports.get(
            "T13_EXPORT_LANDAUER_LOWER_BOUND", {}
        ).get("status")
        == "PASS",
        "standard_identity_export_pass": accepted_exports.get(
            "T13_EXPORT_STANDARD_THERMO_GRAVITY_IDENTITIES", {}
        ).get("status")
        == "PASS",
        "uet_bridge_export_blocked": blocked_exports.get(
            "T13_EXPORT_UET_BRIDGE_PROOF", {}
        ).get("status")
        == "BLOCKED",
        "source_dataset_export_blocked": blocked_exports.get(
            "T13_EXPORT_SOURCE_NORMALIZED_LANDAUER_DATASET", {}
        ).get("status")
        == "BLOCKED",
        "cattaneo_external_export_not_allowed": blocked_exports.get(
            "T13_EXPORT_CATTANEO_EXTERNAL_VALIDATION", {}
        ).get("status")
        == "SIMULATION_ONLY",
    }

    derivation_checks = {
        "primary_warn": primary.get("status") == "WARN",
        "claim_class_C": primary.get("claim_class") == "C",
        "derivation_boundary_open": (
            primary.get("bridge_derivation_map", {}).get("status")
            or foundation_boundary.get("derivation")
        )
        == "open_boundary_mapped_not_derived",
        "units_contract_partial": (
            primary.get("units_contract", {}).get("status")
            or foundation_boundary.get("units")
        )
        == "partial_contract_dimensional_and_proxy_layers_separated",
        "landauer_is_imported_constraint": (
            primary.get("landauer_uet_mapping", {}).get("status")
            or foundation_boundary.get("landauer")
        )
        == "imported_constraint_not_noncircular_uet_derivation",
        "beta_not_derived": (
            primary.get("beta_role_clarification", {}).get("status")
            or foundation_boundary.get("beta")
        )
        == "beta_present_but_not_closed_as_derived_bridge_coefficient",
    }

    cattaneo_checks = {
        "simulation_only": cattaneo.get("status") == "SIMULATION_ONLY",
        "external_validation_false": cattaneo.get("external_validation") is False,
        "all_control_gates_pass": all(cattaneo.get("gates", {}).values()),
        "analytical_residual_pass": cattaneo.get("metrics", {}).get(
            "analytical_residual", float("inf")
        )
        <= cattaneo.get("thresholds", {}).get("analytical_residual_max", 0.0),
        "causal_control_leakage_pass": cattaneo.get("metrics", {}).get(
            "causal_leakage_ratio", float("inf")
        )
        <= cattaneo.get("thresholds", {}).get("causal_leakage_ratio_max", 0.0),
    }

    thermal_checks = {
        "simulation_only": thermal.get("status") == "SIMULATION_ONLY",
        "internal_gate_failed": thermal.get("internal_gate_status") == "FAIL",
        "dependency_blocked": thermal.get("dependency_status") == "BLOCKED",
        "prearrival_gate_failed": thermal.get("gates", {}).get(
            "prearrival_leakage"
        )
        is False,
        "external_source_gate_failed": thermal.get("gates", {}).get(
            "external_source_ready"
        )
        is False,
        "no_external_numeric_data": thermal.get("run_integrity", {}).get(
            "external_numeric_data_used"
        )
        is False,
        "trace_no_backreaction": thermal.get("run_integrity", {}).get(
            "trace_backreaction"
        )
        is False,
    }

    core_dependency_checks = {
        "core_program_blocked": core_program.get("status") == "BLOCKED",
        "core_eos_blocked": core_state.get("blocked_layers", {}).get(
            "equation_of_state_from_covariant_O2_action"
        )
        == "BLOCKED_CONTROLLING",
        "core_transport_blocked": core_state.get("blocked_layers", {}).get(
            "susceptibility_and_transport_coefficient_matching"
        )
        == "BLOCKED",
        "entropy_current_blocked": core_state.get("blocked_layers", {}).get(
            "entropy_current_and_dissipative_Bianchi_closure"
        )
        == "BLOCKED",
        "trace_feedback_forbidden": "do_not_import_trace_as_state_or_feedback"
        in core_state.get("forbidden_shortcuts", []),
    }

    canonical_status_pass = readiness.get("status") == "Draft" and readiness.get(
        "audit_tier"
    ) == "B"
    row_controller_pass = (
        len(row_controllers) == 4
        and all(item.get("next_controller") for item in row_controllers)
    )

    gates = {
        "foundation_constraint_export_gate": gate(
            "PASS" if all(foundation_checks.values()) else "BLOCKED",
            "Only the Landauer lower bound and standard thermodynamic/gravity identities may be exported as class-C constraints.",
            checks=foundation_checks,
            accepted_export_ids=sorted(accepted_exports),
        ),
        "uet_bridge_derivation_gate": gate(
            "BLOCKED",
            "The UET-specific information-entropy-energy bridge requires a non-circular derivation and closed proxy-to-SI map.",
            checks=derivation_checks,
        ),
        "landauer_coefficient_non_derivation_gate": gate(
            "PASS"
            if derivation_checks["landauer_is_imported_constraint"]
            and derivation_checks["beta_not_derived"]
            else "BLOCKED",
            "Landauer k_B*T*ln(2) must remain an imported lower bound and may not derive beta, EOS, mobility, or a core coupling coefficient.",
            landauer_mapping_status=(
                primary.get("landauer_uet_mapping", {}).get("status")
                or foundation_boundary.get("landauer")
            ),
            beta_role_status=(
                primary.get("beta_role_clarification", {}).get("status")
                or foundation_boundary.get("beta")
            ),
        ),
        "cattaneo_simulation_control_gate": gate(
            "PASS" if all(cattaneo_checks.values()) else "BLOCKED",
            "The Cattaneo artifact may serve only as an analytical/synthetic control-system benchmark.",
            checks=cattaneo_checks,
        ),
        "thermal_pilot_physical_gate": gate(
            "BLOCKED",
            "Physical interpretation requires the pre-arrival leakage and external numeric-source gates to pass without changing thresholds after inspection.",
            checks=thermal_checks,
            controlling_blocker=thermal.get("controlling_blocker"),
            failed_gates=thermal.get("failed_gates", []),
        ),
        "core_eos_transport_entropy_gate": gate(
            "BLOCKED",
            "Topic 0.13 constraints do not derive the core charge EOS, covariant transport, entropy current, or dissipative-Bianchi completion.",
            checks=core_dependency_checks,
            core_controller=core_program.get("controlling_blocker"),
        ),
        "trace_phi_observable_separation_gate": gate(
            "PASS"
            if thermal_checks["trace_no_backreaction"]
            and thermal_checks["no_external_numeric_data"]
            and core_dependency_checks["trace_feedback_forbidden"]
            else "BLOCKED",
            "Normalized Phi and R must not be relabeled as temperature, heat flux, entropy, or feedback without a dimensional observable map.",
        ),
        "row_controller_preservation_gate": gate(
            "PASS" if row_controller_pass else "BLOCKED",
            "The four active Landauer source-row controllers remain independent of the core dependency lane.",
            row_controllers=row_controllers,
        ),
        "canonical_topic_status_gate": gate(
            "PASS" if canonical_status_pass else "BLOCKED",
            "Canonical Topic 0.13 status must remain unchanged by this constraint packet.",
            status_before=readiness.get("status"),
            status_after=readiness.get("status"),
            tier_before=readiness.get("audit_tier"),
            tier_after=readiness.get("audit_tier"),
        ),
        "topic_promotion_gate": gate(
            "BLOCKED",
            "Constraint exports and synthetic controls cannot promote bridge proof, source-normalized validation, external heat transport, or the topic tier.",
        ),
    }

    input_paths = [
        (TOPIC_PRIMARY, "Topic 0.13 primary Landauer/formula artifact"),
        (FOUNDATION_GATE, "Topic 0.13 foundation export contract"),
        (CATTANEO_ARTIFACT, "Synthetic Cattaneo control artifact"),
        (THERMAL_PILOT, "Matter-space thermal control pilot"),
        (CORE_PROGRAM, "Current core GR response program gate"),
        (CORE_STATE_MAP, "Core Noether/EOS/transport dependency gate"),
        (READINESS_METADATA, "Canonical topic readiness metadata"),
    ]

    return {
        "schema_version": "1.0",
        "artifact": "0_13_core_thermodynamic_constraint_gate",
        "topic": TOPIC,
        "version": "core_wave9_topic_constraint_v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "command": "python docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_Core_Thermodynamic_Constraint_Gate.py",
        "benchmark_role": "CONSTRAINT_EXPORT_ONLY_NO_SIMULATION_RERUN",
        "status": "BLOCKED",
        "evidence_status": "THERMODYNAMIC_CONSTRAINT_EXPORTS_AVAILABLE_CORE_CLOSURE_NOT_DERIVED",
        "claim_class": "internal_dependency_boundary",
        "controlling_blocker": CONTROLLING_BLOCKER,
        "core_program_controller": core_program.get("controlling_blocker"),
        "foundation_status_unchanged": foundation.get("status"),
        "foundation_claim_ceiling_unchanged": foundation.get("claim_ceiling"),
        "row_controllers_unchanged": row_controllers,
        "thermal_pilot_status_unchanged": thermal.get("status"),
        "thermal_pilot_failed_gates_unchanged": thermal.get("failed_gates", []),
        "topic_status_impact": "NONE",
        "canonical_topic_status": readiness.get("status"),
        "canonical_topic_tier": readiness.get("audit_tier"),
        "scientific_inputs": [_input_record(path, role) for path, role in input_paths],
        "gates": gates,
        "completed_scope": [
            "Landauer lower-bound export as a class-C constraint",
            "standard Bekenstein/Unruh/Hawking formula constraints",
            "synthetic Cattaneo analytical/control benchmark",
            "explicit beta non-derivation and imported-constraint boundary",
            "trace/Phi no-backreaction and non-observable boundary",
        ],
        "blocked_scope": [
            "UET information-entropy-energy bridge proof",
            "source-normalized Landauer dataset",
            "external heat-transport or second-sound validation",
            "dimensional Phi/R to temperature or heat-flux observable map",
            "charge-density EOS, covariant transport, entropy current, and dissipative-Bianchi closure",
            "beta or any core coefficient derived from Landauer by identity reuse",
            "topic or core claim promotion",
        ],
        "required_next_evidence": [
            "close the four active Berut/Jun/Hong/Peterson source-row controllers",
            "derive a non-circular UET bridge with a closed proxy-to-SI units contract",
            "repair physical pre-arrival leakage under the locked causal threshold",
            "add licensed dimensional heat-transport rows, uncertainty, preprocessing, locators, and hashes",
            "derive or independently calibrate EOS/transport and construct entropy-current/dissipative-Bianchi closure",
        ],
        "allowed_language": [
            "Landauer lower-bound constraint",
            "standard thermodynamic/gravity formula consistency",
            "synthetic Cattaneo control benchmark",
            "normalized internal thermal pilot with failed physical gates",
        ],
        "blocked_language": [
            "0.13 derives the UET thermodynamic bridge",
            "Landauer derives beta or the core EOS/transport coefficients",
            "the thermal pilot is external second-sound validation",
            "Phi or trace is measured temperature, heat flux, entropy, or information matter",
            "0.13 closes the core entropy current or dissipative Bianchi identity",
            "Topic 0.13 is externally validated or solved",
        ],
        "limitations": [
            "No Landauer, Cattaneo, thermal pilot, or core solver is rerun.",
            "The foundation gate remains WARN and exports only class-C constraints.",
            "The thermal pilot retains failed causal and external-source gates.",
            "The core EOS, transport, and entropy-current blockers remain open.",
        ],
        "claim_boundary": (
            "Topic 0.13 may constrain the core program with Landauer and standard identities and may provide synthetic "
            "control benchmarks. It does not derive the UET bridge, beta, EOS, transport, entropy current, or a dimensional "
            "Phi/trace observable, and it does not promote Topic 0.13 or the core program."
        ),
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
    }


def main() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    artifact = build_artifact()
    ARTIFACT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
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
                "gates": {
                    name: value["status"]
                    for name, value in result["gates"].items()
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
