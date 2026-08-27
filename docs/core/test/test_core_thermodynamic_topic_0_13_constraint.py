"""Regression tests for the Topic 0.13 core constraint-export gate."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    ROOT
    / "docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research"
    / "Research_Core_Thermodynamic_Constraint_Gate.py"
)
ARTIFACT = (
    ROOT
    / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts"
    / "0_13_core_thermodynamic_constraint_gate.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("topic_0_13_constraint", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _stable(payload: dict) -> dict:
    value = json.loads(json.dumps(payload))
    value.pop("generated_at", None)
    value.pop("environment", None)
    return value


def test_persisted_artifact_matches_current_generator() -> None:
    assert _stable(_module().build_artifact()) == _stable(_artifact())


def test_only_class_c_foundation_constraints_are_exportable() -> None:
    artifact = _artifact()
    gate = artifact["gates"]["foundation_constraint_export_gate"]
    assert artifact["status"] == "BLOCKED"
    assert gate["status"] == "PASS"
    assert all(gate["checks"].values())
    assert artifact["foundation_status_unchanged"] == "FOUNDATION_WARN"
    assert artifact["foundation_claim_ceiling_unchanged"] == (
        "C - formula/lower-bound consistency only"
    )


def test_uet_bridge_and_core_completion_remain_blocked() -> None:
    artifact = _artifact()
    derivation = artifact["gates"]["uet_bridge_derivation_gate"]
    core = artifact["gates"]["core_eos_transport_entropy_gate"]
    assert derivation["status"] == core["status"] == "BLOCKED"
    assert all(derivation["checks"].values())
    assert all(core["checks"].values())


def test_landauer_does_not_derive_beta_or_core_coefficients() -> None:
    artifact = _artifact()
    gate = artifact["gates"]["landauer_coefficient_non_derivation_gate"]
    assert gate["status"] == "PASS"
    assert gate["landauer_mapping_status"] == (
        "imported_constraint_not_noncircular_uet_derivation"
    )
    assert gate["beta_role_status"] == (
        "beta_present_but_not_closed_as_derived_bridge_coefficient"
    )
    assert "Landauer derives beta or the core EOS/transport coefficients" in artifact[
        "blocked_language"
    ]


def test_cattaneo_pass_is_simulation_control_only() -> None:
    artifact = _artifact()
    gate = artifact["gates"]["cattaneo_simulation_control_gate"]
    assert gate["status"] == "PASS"
    assert all(gate["checks"].values())
    assert "synthetic Cattaneo control benchmark" in artifact["allowed_language"]


def test_thermal_pilot_keeps_causal_and_external_gates_failed() -> None:
    artifact = _artifact()
    gate = artifact["gates"]["thermal_pilot_physical_gate"]
    assert gate["status"] == "BLOCKED"
    assert gate["checks"]["internal_gate_failed"] is True
    assert gate["checks"]["prearrival_gate_failed"] is True
    assert gate["checks"]["external_source_gate_failed"] is True
    assert artifact["thermal_pilot_failed_gates_unchanged"] == [
        "prearrival_leakage",
        "external_source_ready",
    ]


def test_phi_and_trace_are_not_relabelled_as_observables_or_feedback() -> None:
    artifact = _artifact()
    assert artifact["gates"]["trace_phi_observable_separation_gate"]["status"] == "PASS"
    assert "Phi or trace is measured temperature, heat flux, entropy, or information matter" in artifact[
        "blocked_language"
    ]


def test_landauer_row_controllers_remain_independent() -> None:
    artifact = _artifact()
    gate = artifact["gates"]["row_controller_preservation_gate"]
    assert gate["status"] == "PASS"
    assert len(artifact["row_controllers_unchanged"]) == 4
    assert all(item["next_controller"] for item in artifact["row_controllers_unchanged"])


def test_canonical_topic_status_remains_draft_tier_b() -> None:
    artifact = _artifact()
    gate = artifact["gates"]["canonical_topic_status_gate"]
    assert artifact["topic_status_impact"] == "NONE"
    assert artifact["canonical_topic_status"] == "Draft"
    assert artifact["canonical_topic_tier"] == "B"
    assert gate["status"] == "PASS"
    assert gate["status_before"] == gate["status_after"] == "Draft"
    assert gate["tier_before"] == gate["tier_after"] == "B"


def test_topic_promotion_remains_blocked() -> None:
    artifact = _artifact()
    assert artifact["gates"]["topic_promotion_gate"]["status"] == "BLOCKED"
    assert artifact["evidence_status"] == (
        "THERMODYNAMIC_CONSTRAINT_EXPORTS_AVAILABLE_CORE_CLOSURE_NOT_DERIVED"
    )


def test_scientific_input_hashes_ignore_declared_volatile_metadata_only() -> None:
    module = _module()
    artifact = _artifact()
    for record in artifact["scientific_inputs"]:
        path = ROOT / record["path"]
        assert path.exists()
        assert module.scientific_payload_sha256(path) == record[
            "scientific_payload_sha256"
        ]


def test_claim_boundary_rejects_external_or_solved_overread() -> None:
    artifact = _artifact()
    assert "the thermal pilot is external second-sound validation" in artifact[
        "blocked_language"
    ]
    assert "Topic 0.13 is externally validated or solved" in artifact[
        "blocked_language"
    ]
