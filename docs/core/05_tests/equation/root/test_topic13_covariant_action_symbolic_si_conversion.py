from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path

import pytest

from docs.core.thermal_covariant_action_si_conversion import (
    ExactSIConstants,
    NaturalUnitScale,
    symbolic_si_conversion_contract,
)


ROOT = repo_root()
CONSTANTS_REL = "docs/data/external/constants/codata/si_2019_exact_constants.json"
AUDIT_REL = "docs/core/artifacts/t13_covariant_action_symbolic_si_conversion_audit.json"


def constants() -> ExactSIConstants:
    payload = json.loads((ROOT / CONSTANTS_REL).read_text(encoding="utf-8-sig"))
    values = payload["constants"]
    return ExactSIConstants(
        h_J_s=values["h"]["value"],
        c_m_per_s=values["c"]["value"],
        k_B_J_per_K=values["k_B"]["value"],
    )


def test_conditional_unit_scales_are_dimensionally_consistent() -> None:
    scale = NaturalUnitScale(energy_reference_J=1.0e-20, constants=constants())
    assert scale.length_reference_m == pytest.approx(
        scale.constants.hbar_J_s * scale.constants.c_m_per_s / scale.energy_reference_J
    )
    assert scale.time_reference_s == pytest.approx(
        scale.constants.hbar_J_s / scale.energy_reference_J
    )
    assert scale.temperature_reference_K == pytest.approx(
        scale.energy_reference_J / scale.constants.k_B_J_per_K
    )
    assert scale.energy_density_scale_J_per_m3 > 0.0
    assert scale.heat_capacity_density_scale_J_per_m3_K > 0.0


def test_density_heat_capacity_and_alpha_maps_use_declared_reference() -> None:
    scale = NaturalUnitScale(energy_reference_J=2.0e-20, constants=constants())
    assert scale.density_to_si(2.0) == pytest.approx(
        2.0 * scale.energy_density_scale_J_per_m3
    )
    assert scale.heat_capacity_to_si(3.0) == pytest.approx(
        3.0 * scale.heat_capacity_density_scale_J_per_m3_K
    )
    assert scale.alpha_energy_to_si(4.0) == pytest.approx(
        4.0 * scale.temperature_reference_K
    )


def test_field_normalization_is_explicit_not_base_phi_identity() -> None:
    scale = NaturalUnitScale(energy_reference_J=1.0e-20, constants=constants())
    assert scale.normalized_phi_from_covariant(6.0, 2.0) == pytest.approx(3.0)
    assert scale.covariant_phi_scale_to_si_energy(2.0) == pytest.approx(2.0e-20)
    contract = symbolic_si_conversion_contract()
    assert contract["base_phi_to_phi_e"] == "OPEN_DERIVATION_OR_INDEPENDENT_CALIBRATION"
    assert contract["e0"] == "OPEN; no physical energy-density scale is emitted"


def test_symbolic_conversion_audit_is_passed_but_not_physical_closure() -> None:
    artifact = json.loads((ROOT / AUDIT_REL).read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_SCOPED_SYMBOLIC_ACTION_SI_CONVERSION_CONTRACT"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["checks"].values())
    assert artifact["inputs"]["energy_reference_J"] is None
    assert artifact["inputs"]["e0_nat"] is None
    assert artifact["holdout_policy"]["xie_2026_accessed"] is False
    assert "Full Topic 13 closure" in artifact["claim_boundary"]
