"""Lane cards: how a topic declares which part of the UET engine it uses.

A lane card is a small JSON file (template: core/engine/LANE_CARD_TEMPLATE.json). It says what chi,
psi, F and P are in the topic, which engine functions compute the result, and where every number
comes from. validate_lane_card() returns a list of problems; an empty list means the card is well
formed. It does not judge whether the physics is right; that is the job of physics tests and Test Cards.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import layer1, layer23

REACH = {"LAYER1", "LAYER23", "LAYER1_AND_LAYER23", "OUTSIDE_ACTION"}
ORIGIN = {"DERIVED", "MEASURED_INDEPENDENT", "REGISTERED_LIMIT", "CALIBRATION"}
REQUIRED = ("schema", "topic", "reach", "system", "mapping", "engine_functions", "parameters",
            "observable", "legacy", "drafted_by")
ENGINE_MODULES = {"layer1": layer1, "layer23": layer23}


def _engine_function_exists(name: str) -> bool:
    module, _, attr = name.partition(".")
    return module in ENGINE_MODULES and callable(getattr(ENGINE_MODULES[module], attr, None))


def validate_lane_card(card: dict) -> list[str]:
    problems = [f"missing field: {k}" for k in REQUIRED if k not in card]
    if problems:
        return problems
    if card["schema"] != "uet-lane-card-v1":
        problems.append("schema must be uet-lane-card-v1")
    reach = card["reach"]
    if reach not in REACH:
        problems.append(f"reach must be one of {sorted(REACH)}")
    functions = card["engine_functions"]
    if reach == "OUTSIDE_ACTION":
        if functions:
            problems.append("OUTSIDE_ACTION cards must not list engine functions")
        if not card.get("outside_reason"):
            problems.append("OUTSIDE_ACTION cards need outside_reason")
    else:
        if not functions:
            problems.append("a card that uses the engine must list engine_functions")
        for name in functions:
            if not _engine_function_exists(name):
                problems.append(f"unknown engine function: {name}")
        if reach in {"LAYER1", "LAYER1_AND_LAYER23"} and not card["mapping"].get("chi"):
            problems.append("layer-1 cards must say what chi is (Theory Card section 7)")
        if reach in {"LAYER23", "LAYER1_AND_LAYER23"}:
            for key in ("F", "P"):
                if not card["mapping"].get(key):
                    problems.append(f"layer-2/3 cards must define {key}")
    comparison = set(card["observable"].get("comparison_data_ids", []))
    for p in card["parameters"]:
        name = p.get("name", "?")
        if p.get("origin") not in ORIGIN:
            problems.append(f"parameter {name}: origin must be one of {sorted(ORIGIN)} (no topic-local fits)")
        if not p.get("source"):
            problems.append(f"parameter {name}: source is required")
        if p.get("origin") == "CALIBRATION" and p.get("data_id") in comparison:
            problems.append(f"parameter {name}: calibrated on comparison data {p.get('data_id')}")
    return problems


def load_lane_card(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
