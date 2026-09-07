from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/core/artifacts/t13_ding_csrc_heating_backcalculation_identifiability_no_go.json"
MATRIX = ROOT / "docs/core/artifacts/t13_topic13_closure_matrix.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_heating_backcalculation_route_is_closed_as_scoped_no_go() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_SCOPED_NO_GO_DING_C_SRC_HEATING_BACKCALCULATION"
    assert all(audit["checks"].values())
    assert audit["major_result"]["closure_level"] == "CLOSED_AS_NO_GO"
    assert audit["numeric_witness"]["incident_fluence_J_m2"] == pytest.approx(
        6.189358898018153
    )
    assert audit["numeric_witness"]["surface_temperature_upper_bound_K"] == 3.0
    assert audit["numeric_witness"]["absolute_delta_Tq_point_available"] is False
    assert audit["numeric_witness"]["numeric_C_src_emitted"] is False
    assert audit["claim_promotion"] is False


def test_identifiability_witness_keeps_csrc_and_absorption_scale_separate() -> None:
    equation = load(AUDIT)["major_result"]["equation_or_mapping"]
    assert "C_src" in equation["source_temperature"]
    assert "eta_abs/l_th" in equation["identifiability_witness"]
    assert "normalized y_TTG" in equation["identifiability_witness"]


def test_no_go_is_visible_in_source_requirement_without_closing_numeric_csrc() -> None:
    matrix = load(MATRIX)
    source = next(
        item
        for item in matrix["requirements"]
        if item["requirement_id"] == "source_and_uncertainty"
    )
    assert "docs/core/artifacts/t13_ding_csrc_heating_backcalculation_identifiability_no_go.json" in {
        ref["path"] for ref in source["evidence_artifacts"]
    }
    accepted = next(
        item
        for item in source["required_subresults"]
        if item["subresult_id"] == "accepted_numeric_csrc"
    )
    assert accepted["status"] == "OPEN"
