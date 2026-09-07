"""Regression checks for the Topic 13 flat component closure contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_flat_thermodynamic_bridge_components_gate.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_flat_components_close_formal_lane_only() -> None:
    artifact = load(ARTIFACT)
    assert artifact["status"] == "PASS_SCOPED_T13_FLAT_COMPONENTS_WITH_EXTERNAL_INPUT"
    assert artifact["major_result"]["major_result_id"] == "T13_FLAT_THERMODYNAMIC_BRIDGE_COMPONENTS"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["full_core_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["uet_physical_kubo_record_present"] is False
    assert artifact["uet_numeric_transport_coefficients_emitted"] is False
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["xie_2026_accessed"] is False
    assert "physical_Kubo_coefficient_record_missing" in artifact["major_result"]["open_blockers"]


def test_external_input_has_units_hash_and_no_uet_relabel() -> None:
    artifact = load(ARTIFACT)
    external = artifact["external_transport_input"]
    assert external["source_payload_sha256"]
    assert external["payload_hash_matches_declared"] is True
    assert external["accepted_for_external_transport_input"] is True
    assert external["accepted_for_uet_physical_kubo_coefficient"] is False
    assert external["accepted_for_full_topic13"] is False
    assert artifact["units"]["external_transport"] == "W m^-1 K^-1"
    assert artifact["units"]["alpha_Phi_K"] == "K per normalized Phi; not emitted"


def test_flat_components_are_linked_into_full_gate_without_promotion() -> None:
    artifact = load(ARTIFACT)
    full = load(FULL)
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "topic13_flat_thermodynamic_bridge_components"
    ]
    assert lane["major_result_id"] == artifact["major_result"]["major_result_id"]
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert any(item["path"] == "docs/core/artifacts/t13_flat_thermodynamic_bridge_components_gate.json" for item in full["evidence_artifacts"])


def test_register_contains_hash_locked_major_result() -> None:
    register = load(REGISTER)
    entry = next(
        item for item in register["entries"]
        if item.get("major_result_id") == "T13_FLAT_THERMODYNAMIC_BRIDGE_COMPONENTS"
    )
    assert entry["closure_level"] == "CLOSED_FOR_LANE"
    evidence = next(
        item for item in entry["evidence_artifacts"]
        if item["path"] == "docs/core/artifacts/t13_flat_thermodynamic_bridge_components_gate.json"
    )
    assert evidence["sha256"] == digest(ARTIFACT)
    assert register["claim_promotion"] is False
