"""Regression tests for the Topic 13 dimensional scale-dependency no-go."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "docs/core"))

from t13_thermal_bridge_scale_dependency import (  # noqa: E402
    build_scale_dependency_witness,
    scale_dependency_contract,
)


def test_field_rescaling_witness_preserves_declared_action_terms() -> None:
    witness = build_scale_dependency_witness()
    field = witness["field_rescaling"]
    assert all(field["checks"].values())
    assert field["checks"]["normalized_coordinate_invariant"] is True


def test_joint_scale_witness_separates_normalized_and_absolute_maps() -> None:
    witness = build_scale_dependency_witness()
    joint = witness["joint_scale"]
    assert joint["checks"]["normalized_response_invariant"] is True
    assert joint["checks"]["field_only_alpha_compensation_preserves_response"] is True
    assert joint["checks"]["joint_energy_scale_changes_absolute_response"] is True
    assert joint["checks"]["joint_scale_changes_beta"] is True


def test_contract_preserves_topic13_ontology_and_measurement_equations() -> None:
    contract = scale_dependency_contract()
    assert contract["normalized_observable"]["y_TTG_UET"] == "Delta_Phi(t) / Delta_Phi(0)"
    assert contract["dimensional_map"] == "Delta_Tq = alpha_Phi_K * Delta_Phi"
    assert "not temperature" in contract["ontology"]["Phi"]
    assert "derived physical/history trace" in contract["ontology"]["R_gen"]
