from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "ding_2022_experimental_heating_input_source_package.json"
)
AUDIT = ROOT / "docs/core/artifacts/t13_ding_experimental_heating_input_boundary_audit.json"
GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)


DEPENDENCY = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_ding_heating_boundary_audit_passes_without_absorption_claim() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_SCOPED_DING_EXPERIMENTAL_HEATING_INPUT_BOUNDARY"
    assert all(audit["checks"].values())
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["derived_records"][0]["value_si"] == pytest.approx(
        6.189358898018153
    )
    assert audit["energy_density_contract"]["absorbed_energy_density"][
        "numeric_value"
    ] is None


def test_source_package_keeps_incident_fluence_separate_from_uet_scale() -> None:
    package = load(PACKAGE)
    rows = {row["row_id"]: row for row in package["source_rows"]}
    assert rows["ding_pump_pulse_energy"]["value_si"] == 70e-9
    assert rows["ding_pump_spot_diameter_1e2"]["value_si"] == 120e-6
    assert rows["ding_surface_temperature_rise_upper_bound"]["value_si"] is None
    assert package["energy_density_contract"]["absorbed_energy_density"][
        "status"
    ] == "OPEN_NOT_IDENTIFIED"
    assert package["energy_density_contract"]["base_phi_map"]["numeric_e0"] is None
    assert package["energy_density_contract"]["base_phi_map"][
        "numeric_alpha_Phi_K"
    ] is None


def test_full_gate_exposes_lane_without_unlocking_source_or_alpha() -> None:
    gate = load(GATE)
    dependency = load(DEPENDENCY)
    source_lane = gate["verification_status"]["source_package"][
        "ding_experimental_heating_input_boundary"
    ]
    assert source_lane["status"] == "PASS_SCOPED_DING_EXPERIMENTAL_HEATING_INPUT_BOUNDARY"
    assert gate["verification_status"]["source_package"]["status"] == "BLOCKED"
    assert gate["verification_status"]["alpha_Phi_K"]["status"] == "BLOCKED"
    assert gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert gate["claim_promotion"] is False
    assert gate["verification_status"]["holdout_integrity"]["holdout_consumed"] is False
    lane = dependency["topic13_partial_evidence"]["ding_experimental_heating_input_boundary"]
    assert lane["summary"]["status"] == "PASS_SCOPED_DING_EXPERIMENTAL_HEATING_INPUT_BOUNDARY"
    assert dependency["topic13_partial_evidence"]["full_core_unlock"] is False
    assert dependency["status"] == "BLOCKED_DOWNSTREAM_MAJOR_RESULTS"


def test_fluence_equation_has_si_unit_closure() -> None:
    package = load(PACKAGE)
    record = package["derived_records"][0]
    energy = 70e-9
    radius = 120e-6 / 2
    expected = energy / (math.pi * radius**2)
    assert record["unit_si"] == "J m^-2"
    assert record["value_si"] == pytest.approx(expected)
