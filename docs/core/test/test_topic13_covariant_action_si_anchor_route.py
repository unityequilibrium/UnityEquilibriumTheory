"""Regression checks for the conditional natural-unit action route."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_covariant_action_si_anchor_route_audit.json"


def test_action_route_is_natural_only_and_si_mapping_is_blocked() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_NATURAL_UNIT_ROUTE_IDENTIFIED_SI_MAPPING_BLOCKED"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["checks"]["formula_defaults_not_physical"] is True
    assert artifact["checks"]["formula_si_gate_open"] is True
    assert artifact["checks"]["response_gravitational_coefficient_default_is_control"] is True
    assert artifact["checks"]["spec_declares_kappa_dimension_only"] is True
    assert artifact["checks"]["candidate_route_has_no_newton_coupling_match"] is True
    assert artifact["major_result"]["coefficient_provenance"]["kappa_E"]["numeric_value"] is None
    assert artifact["major_result"]["coefficient_provenance"]["kappa_E"]["si_or_newton_match"] == "NOT_DECLARED"
    assert artifact["controlling_blocker"] == "system_specific_SI_contract_and_covariant_Phi_to_normalized_Phi_map_missing"
