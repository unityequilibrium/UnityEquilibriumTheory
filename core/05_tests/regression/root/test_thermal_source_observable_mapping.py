import json
from pathlib import Path
from docs.core.core_paths import repo_root

import pytest

from docs.core.thermal_source_observable_map import (
    normalized_ttg_signal,
    quasi_temperature_difference_from_phi,
    ttg_wave_speed,
    ttg_wavevector,
    ttg_propagation_length,
)
from docs.scripts.audit.audit_thermal_source_observable_mapping import build_artifact


def test_normalized_ttg_operator_is_dimensionless_and_scale_free() -> None:
    assert normalized_ttg_signal(0.25, -0.25, 0.5) == pytest.approx(1.0)


def test_normalized_ttg_operator_rejects_zero_reference() -> None:
    with pytest.raises(ValueError, match="nonzero"):
        normalized_ttg_signal(1.0, 1.0, 0.0)


def test_dimensional_map_requires_explicit_temperature_scale() -> None:
    assert quasi_temperature_difference_from_phi(0.25, -0.25, None) is None
    assert quasi_temperature_difference_from_phi(0.25, -0.25, 4.0) == pytest.approx(2.0)


def test_ttg_wave_speed_uses_half_grating_period() -> None:
    assert ttg_wave_speed(2.0e-6, 1.0e-9) == pytest.approx(1000.0)


def test_ttg_wavevector_and_propagation_length_are_source_diagnostics() -> None:
    assert ttg_wavevector(2.0e-6) == pytest.approx(3.141592653589793e6)
    assert ttg_propagation_length(2.0e-6, -0.5) == pytest.approx(1.4426950408889634e-6)


def test_ttg_propagation_length_rejects_invalid_dip_domain() -> None:
    with pytest.raises(ValueError, match="-1 < dip < 0"):
        ttg_propagation_length(2.0e-6, 0.0)
    with pytest.raises(ValueError, match="-1 < dip < 0"):
        ttg_propagation_length(2.0e-6, -1.0)

def test_source_readiness_artifact_exposes_blocked_lanes() -> None:
    artifact = build_artifact()
    assert artifact["audit_status"] == "PASS_WITH_BLOCKED_DIMENSIONAL_AND_DATA_LANES"
    assert artifact["mapping_status"].endswith("BLOCKED")
    assert artifact["gates"]["standard_normalized_ttg_operator_defined"]
    assert artifact["gates"]["standard_ttg_diagnostic_relations_defined"]
    assert not artifact["gates"]["dimensional_phi_to_quasi_temperature_scale_defined"]
    assert artifact["gates"]["local_numeric_source_package_present"]
    assert artifact["gates"]["holdout_data_not_consumed"]


def test_source_review_records_external_identity_and_local_gap() -> None:
    path = repo_root() / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_thermal_source_review.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["numeric_fitting_allowed"] is False
    assert payload["holdout_consumed"] is False
    assert all(row["doi"] and row["url"] for row in payload["sources"])
    non_holdout = [row for row in payload["sources"] if "holdout" not in row["source_id"]]
    assert any(row["local_numeric_path"] for row in non_holdout)
    holdout = next(row for row in payload["sources"] if "holdout" in row["source_id"])
    assert holdout["local_numeric_path"] is None
