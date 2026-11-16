"""Software-only checks of supplied profile values, not a physical simulation.

The legacy Sim_* wrappers own their file/Topic association. This shared helper
does not derive values, choose targets, call a UET law or validate source data.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path


INTERPRETATION = "PROFILE_THRESHOLD_CHECK_ONLY_NOT_PHYSICAL_VALIDATION"


def _finite_number(value: object, name: str) -> float | int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name}: expected a finite number, not {type(value).__name__}")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(f"{name}: nonfinite value")
    return value


def evaluate_profile(data: object) -> bool:
    """Apply the supplied inclusive min/max targets, rejecting unknown inputs.

Missing data is never replaced with a fabricated zero or a large sentinel.
Targets are a profile's requested comparisons, not author-approved physics.
"""
    if not isinstance(data, dict):
        raise ValueError("profile must be an object")
    parameters, targets = data.get("parameters"), data.get("targets")
    if not isinstance(parameters, dict) or not parameters:
        raise ValueError("parameters must be a nonempty object")
    if not isinstance(targets, dict) or not targets:
        raise ValueError("targets must be a nonempty object")
    for name, value in parameters.items():
        if not isinstance(name, str) or not name:
            raise ValueError("parameter names must be nonempty strings")
        _finite_number(value, f"parameter {name}")
    bounds: dict[str, dict[str, float | int]] = {}
    passed = True
    for name, threshold in targets.items():
        if not isinstance(name, str) or not name.startswith(("min_", "max_")) or not name[4:]:
            raise ValueError(f"unsupported target: {name!r}")
        key, direction = name[4:], name[:3]
        threshold = _finite_number(threshold, f"target {name}")
        if key not in parameters:
            raise ValueError(f"missing parameter: {key}")
        bounds.setdefault(key, {})[direction] = threshold
        value = parameters[key]
        passed = passed and (value >= threshold if direction == "min" else value <= threshold)
    for key, limits in bounds.items():
        if "min" in limits and "max" in limits and limits["min"] > limits["max"]:
            raise ValueError(f"contradictory bounds: {key}")
    return passed


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def run_profile_check(topic_path: Path, filename: str, *, output_dir: Path | None = None) -> dict:
    data_file = topic_path / "Data" / "05_Simulation" / filename
    data = json.loads(data_file.read_text(encoding="utf-8-sig"), object_pairs_hook=_unique_object)
    passed = evaluate_profile(data)  # Validate before creating or replacing output.
    result = {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "topic": topic_path.name,
            "status": "PASS" if passed else "FAIL",
            "interpretation": INTERPRETATION,
        },
        "parameters": data["parameters"],
        "targets": data["targets"],
    }
    destination = output_dir if output_dir is not None else topic_path / "Result" / "artifacts"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "rd_sim_artifact.json").write_text(
        json.dumps(result, indent=4, allow_nan=False) + "\n", encoding="utf-8", newline="\n",
    )
    print(f"Topic {topic_path.name} profile threshold status: {result['metadata']['status']}")
    return result


def profile_cli(run_simulation) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output-dir", type=Path, help="isolate generated output from legacy evidence")
    args = parser.parse_args()
    result = run_simulation(output_dir=args.output_dir)
    return 0 if result["metadata"]["status"] == "PASS" else 1
