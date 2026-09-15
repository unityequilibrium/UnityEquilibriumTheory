from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path

import pytest

from docs.core.thermal_dimensional_bridge import (
    ConditionalThermalInputs,
    alpha_phi_k_from_local_equilibrium,
    entropy_density_J_per_m3_K,
    free_energy_density_J_per_m3,
)


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_dimensional_bridge_contract_audit.json"
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_conditional_bridge_artifact_closes_formula_not_calibration() -> None:
    artifact = load(AUDIT)
    assert artifact["status"] == "PASS_CONDITIONAL_FORMULA_OPEN_INPUTS"
    assert all(artifact["checks"].values())
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["conditional_inputs"]["a_Phi_T"]["status"] == "OPEN_NOT_SOURCE_LOCKED"
    assert artifact["witness"]["role"].startswith("unit and regularity test")


def test_topic13_gate_records_conditional_formula_without_promoting_alpha() -> None:
    gate = load(GATE)
    alpha = gate["verification_status"]["alpha_Phi_K"]
    assert alpha["conditional_formula_status"] == "CLOSED_FOR_LANE"
    assert alpha["conditional_unit_contract_status"] == "CLOSED_FOR_LANE"
    assert alpha["independent_calibration_or_derivation"] is False
    assert gate["claim_promotion"] is False


def test_conditional_formula_requires_regular_stable_equilibrium() -> None:
    with pytest.raises(ValueError):
        alpha_phi_k_from_local_equilibrium(
            ConditionalThermalInputs(a_phi_T0=0.2, b_phi=1.0, phi0=0.0, da_phi_dT_per_K=0.01)
        )
    with pytest.raises(ValueError):
        alpha_phi_k_from_local_equilibrium(
            ConditionalThermalInputs(a_phi_T0=-1.0, b_phi=1.0, phi0=0.5, da_phi_dT_per_K=0.01)
        )


def test_dimensional_units_are_applied_only_with_explicit_scale() -> None:
    assert free_energy_density_J_per_m3(0.25, 4.0) == 1.0
    assert entropy_density_J_per_m3_K(4.0, 0.5, 0.02) == -0.04
    assert alpha_phi_k_from_local_equilibrium(
        ConditionalThermalInputs(a_phi_T0=0.2, b_phi=1.0, phi0=0.5, da_phi_dT_per_K=0.01)
    ) == -190.0
