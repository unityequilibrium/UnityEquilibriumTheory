"""Unit checks for the open Topic 13 base-Phi calibration requirement."""

from __future__ import annotations

from docs.scripts.audit.audit_topic13_base_phi_independent_calibration_requirement import (
    REQUIRED_SNIPPETS,
    build_artifact,
)


def test_requirement_is_open_and_has_no_numeric_calibration() -> None:
    artifact = build_artifact()
    assert artifact["status"] == "PASS_OPEN_CALIBRATION_REQUIREMENT"
    assert artifact["major_result"]["closure_level"] == "OPEN"
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["parameter_fitting_performed"] is False
    assert artifact["target_data_used"] is False
    assert artifact["xie_2026_accessed"] is False


def test_protocol_declares_all_required_fields() -> None:
    artifact = build_artifact()
    assert all(artifact["protocol"]["checks"].values())
    assert set(artifact["required_record_fields"]) >= {
        "source_identity",
        "locator",
        "base_Phi_amplitude",
        "SI_energy_or_response_amplitude",
        "uncertainty",
        "preprocessing",
        "row_identity",
        "source_hash",
        "independence_statement",
    }
    assert len(REQUIRED_SNIPPETS) == len(artifact["protocol"]["required_snippets"])
