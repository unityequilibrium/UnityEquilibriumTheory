from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
from pathlib import Path


ROOT = (repo_root() / "docs")
SCRIPT = ROOT / "scripts" / "audit" / "audit_topic13_berut_figure3_digitization.py"


def load_module():
    spec = importlib.util.spec_from_file_location("t13_berut_figure3_digitization", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_figure_digitization_is_scoped_and_non_calibrating():
    artifact = load_module().build_artifact()
    assert artifact["status"] == "PASS_SCOPED_BERUT_FIGURE3_DIGITIZATION"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["row_count"] == 10
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["parameter_fitting_performed"] is False
    assert artifact["target_data_used"] is False
    assert artifact["xie_2026_accessed"] is False


def test_figure_digitization_keeps_measurement_uncertainty_open():
    artifact = load_module().build_artifact()
    assert artifact["preprocessing"]["measurement_error_bars_transcribed"] is False
    assert "figure_derived_not_raw_numeric_source" in artifact["open_blockers"][0]
    assert artifact["axis_mapping"]["x"]["coordinate_uncertainty_px"] > 0
