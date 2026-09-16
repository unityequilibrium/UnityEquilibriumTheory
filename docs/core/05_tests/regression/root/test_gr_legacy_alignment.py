"""Regression gates for legacy covariance and conservation claim quarantine."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path

import json
from pathlib import Path

from docs.core.uet_lorentz import LEGACY_COVARIANCE_EVIDENCE_STATUS
from docs.core.uet_noether import LEGACY_NOETHER_EVIDENCE_STATUS
from docs.scripts.audit.audit_uet_gr_legacy_alignment import build_gate


def test_legacy_modules_export_blocked_evidence_status() -> None:
    assert LEGACY_COVARIANCE_EVIDENCE_STATUS == "BLOCKED_FOR_INVARIANCE_CLAIMS"
    assert LEGACY_NOETHER_EVIDENCE_STATUS == "BLOCKED_FOR_CONSERVATION_PROOF_CLAIMS"


def test_audit_detects_unapplied_transform_and_unwired_metrics() -> None:
    gate = build_gate()
    findings = gate["findings"]["lorentz"]
    assert findings["placeholder_field_assignments"] >= 1
    assert findings["lorentz_matrix_loads_after_assignment"] == 0
    assert findings["curved_metric_calls_in_claim_methods"] == 0
    assert findings["metric_argument_present"] is False
    assert gate["gates"]["actual_lorentz_transform_application"]["status"] == "FAIL"
    assert gate["gates"]["curved_metric_wiring"]["status"] == "FAIL"


def test_audit_detects_non_covariant_noether_diagnostic() -> None:
    gate = build_gate()
    findings = gate["findings"]["noether"]
    assert findings["time_derivative_argument_present"] is False
    assert findings["metric_argument_present"] is False
    assert findings["gradient_flow_update_present"] is True
    assert findings["real_field_u1_proxy_present"] is True
    assert gate["gates"]["covariant_noether_action"]["status"] == "FAIL"
    assert gate["gates"]["dynamics_consistent_conservation"]["status"] == "FAIL"


def test_generated_gate_quarantines_claims_without_pretending_physics_passes() -> None:
    path = canonical_artifact_path("legacy_covariance_alignment_gate.json")
    artifact = json.loads(path.read_text(encoding="utf-8"))
    assert artifact["audit_status"] == "PASS"
    assert artifact["evidence_status"] == "BLOCKED"
    assert artifact["gates"]["legacy_claim_quarantine"]["status"] == "PASS"
    assert all(
        artifact["gates"][name]["status"] == "FAIL"
        for name in (
            "actual_lorentz_transform_application",
            "curved_metric_wiring",
            "covariant_noether_action",
            "dynamics_consistent_conservation",
        )
    )
    assert "Einstein-equation derivation" in artifact["blocked_use"]


def test_claim_gate_keeps_lorentz_and_einstein_exports_blocked() -> None:
    path = canonical_artifact_path("gr_correspondence_claim_gate.json")
    artifact = json.loads(path.read_text(encoding="utf-8"))
    blocked = {entry["claim"] for entry in artifact["blocked_claims"]}
    assert "UET is Lorentz invariant." in blocked
    assert "UET derives Einstein's equations." in blocked
