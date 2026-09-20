"""Regression coverage for the canonical thermal-observable migration."""

from importlib import import_module
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]


def test_thermal_bridge_legacy_import_is_a_facade() -> None:
    legacy = import_module("docs.core.thermal_observable_bridge")
    canonical = import_module(
        "docs.core.03_lanes.thermal.thermal_observable_bridge"
    )

    assert legacy.ThermalObservableBridgeConfig is canonical.ThermalObservableBridgeConfig
    assert legacy.ThermalObservableBridgeResult is canonical.ThermalObservableBridgeResult
    assert legacy.__canonical_module__ == canonical.__name__
    assert (
        ROOT / "docs/core/03_lanes/thermal/thermal_observable_bridge.py"
    ).is_file()


def test_thermal_source_map_legacy_import_is_a_facade() -> None:
    legacy = import_module("docs.core.thermal_source_observable_map")
    canonical = import_module(
        "docs.core.03_lanes.thermal.thermal_source_observable_map"
    )

    assert legacy.ThermalPhiCalibration is canonical.ThermalPhiCalibration
    assert legacy.normalized_ttg_signal is canonical.normalized_ttg_signal
    assert legacy.__canonical_module__ == canonical.__name__
    assert (
        ROOT / "docs/core/03_lanes/thermal/thermal_source_observable_map.py"
    ).is_file()


def test_thermal_package_exports_observable_pair() -> None:
    lane = import_module("docs.core.03_lanes.thermal")

    assert lane.ThermalObservableBridgeConfig is not None
    assert lane.ThermalPhiCalibration is not None
    assert "run_thermal_observable_bridge" in lane.__all__
    assert "normalized_ttg_signal" in lane.__all__
