"""Bookkeeping: the lane-card validator accepts the template and rejects malformed cards."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from core.engine import lanes  # noqa: E402

TEMPLATE = Path(__file__).resolve().parents[2] / "engine" / "LANE_CARD_TEMPLATE.json"


def test_template_is_valid():
    assert lanes.validate_lane_card(lanes.load_lane_card(TEMPLATE)) == []


def test_registered_lane_cards_are_valid():
    cards = sorted((TEMPLATE.parent / "lane_cards").glob("*.json"))
    assert cards
    for path in cards:
        assert lanes.validate_lane_card(lanes.load_lane_card(path)) == [], path.name


def test_rejects_topic_local_fit_and_unknown_function():
    card = copy.deepcopy(lanes.load_lane_card(TEMPLATE))
    card["parameters"][0]["origin"] = "FITTED"
    card["engine_functions"].append("layer23.does_not_exist")
    problems = lanes.validate_lane_card(card)
    assert any("origin" in p for p in problems)
    assert any("unknown engine function" in p for p in problems)


def test_rejects_calibration_on_comparison_data():
    card = copy.deepcopy(lanes.load_lane_card(TEMPLATE))
    card["parameters"][0]["origin"] = "CALIBRATION"
    card["parameters"][0]["data_id"] = card["observable"]["comparison_data_ids"][0]
    assert any("calibrated on comparison data" in p for p in lanes.validate_lane_card(card))


def test_outside_action_needs_reason_and_no_functions():
    card = copy.deepcopy(lanes.load_lane_card(TEMPLATE))
    card["reach"] = "OUTSIDE_ACTION"
    card["outside_reason"] = ""
    problems = lanes.validate_lane_card(card)
    assert "OUTSIDE_ACTION cards must not list engine functions" in problems
    assert "OUTSIDE_ACTION cards need outside_reason" in problems
