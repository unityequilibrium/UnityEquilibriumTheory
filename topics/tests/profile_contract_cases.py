"""Reusable software tests for the reviewed legacy Sim_* profile family.

Synthetic controls test input/comparison/output behavior, never a physical law.
The current public profile is replayed only against its saved comparison output.
"""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from topics._profile_thresholds import INTERPRETATION, profile_cli


CASES = (
    "saved_profile", "exact_limits", "below_minimum", "above_maximum",
    "empty_targets", "empty_parameters", "missing_min_zero", "missing_max_large",
    "unknown_target", "nonfinite_parameter", "nonfinite_target", "boolean_parameter",
    "string_parameter", "malformed_json", "duplicate_key", "missing_file",
    "contradictory_bounds", "unknown_quantity_not_zero", "cli_pass", "cli_fail",
    "outside_cwd_cli", "read_only_import", "output_failure",
)


def exercise_profile_case(topic: Path, script: str, filename: str, case: str, tmp_path: Path) -> None:
    source = topic / script
    original = topic / "Result/artifacts/rd_sim_artifact.json"
    original_bytes = original.read_bytes()
    data_bytes = (topic / "Data/05_Simulation" / filename).read_bytes()
    namespace = runpy.run_path(str(source))  # Import only: __main__ is not entered.
    run = namespace["run_simulation"]
    assert namespace["ROOT"] == topic.parents[1]
    assert original.read_bytes() == original_bytes
    assert (topic / "Data/05_Simulation" / filename).read_bytes() == data_bytes
    if case == "read_only_import":
        return
    output = tmp_path / "new-output"
    if case in {"saved_profile", "outside_cwd_cli"}:
        if case == "outside_cwd_cli":
            proc = subprocess.run(
                [sys.executable, "-X", "utf8", str(source), "--output-dir", str(output)],
                cwd=tmp_path, capture_output=True, text=True, timeout=30,
            )
            assert proc.returncode == 0, proc.stdout + proc.stderr
            actual = json.loads((output / "rd_sim_artifact.json").read_text())
        else:
            actual = run(output_dir=output)
        saved = json.loads(original_bytes)
        for field in ("parameters", "targets"):
            assert actual[field] == saved[field]
        assert actual["metadata"]["status"] == saved["metadata"]["status"]
        assert actual["metadata"]["topic"] == topic.name
        assert actual["metadata"]["interpretation"] == INTERPRETATION
        assert original.read_bytes() == original_bytes
        assert (topic / "Data/05_Simulation" / filename).read_bytes() == data_bytes
        return

    isolated = tmp_path / topic.name
    input_file = isolated / "Data/05_Simulation" / filename
    input_file.parent.mkdir(parents=True)
    run.__globals__["topic_path"] = isolated
    profile = {"parameters": {"x": 2, "y": 3}, "targets": {"min_x": 2, "max_y": 3}}
    if case == "below_minimum":
        profile["parameters"]["x"] = 1
    elif case == "above_maximum":
        profile["parameters"]["y"] = 4
    elif case == "empty_targets":
        profile["targets"] = {}
    elif case == "empty_parameters":
        profile["parameters"] = {}
    elif case == "missing_min_zero":
        profile["targets"] = {"min_unknown": 0}
    elif case == "missing_max_large":
        profile["targets"] = {"max_unknown": 1000000}
    elif case == "unknown_target":
        profile["targets"] = {"goal_x": 2}
    elif case == "nonfinite_parameter":
        profile["parameters"]["x"] = float("nan")
    elif case == "nonfinite_target":
        profile["targets"]["min_x"] = float("inf")
    elif case == "boolean_parameter":
        profile["parameters"]["x"] = True
    elif case == "string_parameter":
        profile["parameters"]["x"] = "2"
    elif case == "contradictory_bounds":
        profile["targets"]["max_x"] = 1
    elif case == "unknown_quantity_not_zero":
        profile["parameters"]["x"] = None
    elif case == "cli_fail":
        profile["parameters"]["x"] = 1
    if case == "malformed_json":
        content = "{broken"
    elif case == "duplicate_key":
        content = '{"parameters":{"x":1,"x":2},"targets":{"min_x":2}}'
    else:
        content = json.dumps(profile)
    if case != "missing_file":
        input_file.write_text(content, encoding="utf-8", newline="\n")

    if case in {"cli_pass", "cli_fail"}:
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(sys, "argv", [str(source), "--output-dir", str(output)])
            assert profile_cli(run) == (1 if case == "cli_fail" else 0)
    elif case == "output_failure":
        output.write_text("not a directory", encoding="utf-8")
        with pytest.raises(FileExistsError):
            run(output_dir=output)
        assert output.read_text() == "not a directory"
    elif case in {"exact_limits", "below_minimum", "above_maximum"}:
        expected = "PASS" if case == "exact_limits" else "FAIL"
        result = run(output_dir=output)
        assert result["metadata"]["status"] == expected
        assert json.loads((output / "rd_sim_artifact.json").read_text()) == result
    else:
        with pytest.raises(FileNotFoundError if case == "missing_file" else ValueError):
            run(output_dir=output)
        assert not output.exists(), "Invalid input must not produce a PASS artifact"
    assert original.read_bytes() == original_bytes
    assert (topic / "Data/05_Simulation" / filename).read_bytes() == data_bytes
