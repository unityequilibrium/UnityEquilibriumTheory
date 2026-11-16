"""Software-only fixture checks; no CODATA comparison or real engine run.

Exercises the existing source-constant diagnostic's failure/reporting paths.
Synthetic constants below are not measured inputs or UET calibration values.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


def load_diagnostic():
    path = Path(__file__).with_name("Research_G_Constant.py")
    spec = importlib.util.spec_from_file_location("gravity_reporting_fixture", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("engine_g, expected", [(1.0, "PASS"), (2.0, "FAIL"),
                                               (0.0, "FAIL"), (float("nan"), "FAIL"),
                                               (float("inf"), "FAIL")])
def test_reporting_uses_native_threshold_and_writes_only_fixture_output(tmp_path, monkeypatch, engine_g, expected):
    diagnostic = load_diagnostic()
    data = tmp_path / "fixture.json"
    data.write_text(json.dumps({"constants": {"G": {"value": 1.0, "relative_uncertainty": 0.01}}}), encoding="utf-8")
    output = tmp_path / "output" / "result.json"
    monkeypatch.setattr(diagnostic, "ROOT", tmp_path)
    monkeypatch.setattr(diagnostic, "DATA_PATH", data)
    monkeypatch.setattr(diagnostic, "ARTIFACT_PATH", output)
    class FixtureEngine:
        def get_planck_units(self):
            return {"G": engine_g, "length": 1.0, "time": 1.0, "mass": 1.0}
    monkeypatch.setattr(diagnostic, "load_engine", lambda: FixtureEngine)
    assert diagnostic.test_gravitational_constant() is (expected == "PASS")
    def reject_nonfinite(value):
        raise ValueError(f"nonstandard JSON constant: {value}")
    record = json.loads(output.read_text(encoding="utf-8"), parse_constant=reject_nonfinite)
    assert record["status"] == expected
    assert record["threshold"]["max_relative_error_percent"] == 1.0
    if not diagnostic.np.isfinite(engine_g):
        assert record["metrics"]["G_engine"] is None
        assert record["metrics"]["relative_error_percent"] is None


def test_output_root_and_current_topic_locator(tmp_path, monkeypatch):
    monkeypatch.setenv("UET_OUTPUT_ROOT", str(tmp_path))
    diagnostic = load_diagnostic()
    assert diagnostic.TOPIC_DIR == diagnostic.ROOT / "topics/0.19_Gravity_GR"
    assert diagnostic.ARTIFACT_PATH.is_relative_to(tmp_path)
