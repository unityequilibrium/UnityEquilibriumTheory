from docs.core.core_paths import repo_root
import json
from pathlib import Path

from docs.core.thermal_cp_cv_correction import (
    CpCvCorrectionInputs,
    cp_minus_cv_mass_J_per_kg_K,
    cp_minus_cv_volumetric_J_per_m3_K,
    cv_mass_from_cp_J_per_kg_K,
    cv_volumetric_from_cp_J_per_m3_K,
    cv_volumetric_uncertainty_J_per_m3_K,
)


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_cp_cv_correction_audit.json"


def _inputs() -> CpCvCorrectionInputs:
    return CpCvCorrectionInputs(
        temperature_K=573.15,
        cp_mass_J_per_kg_K=1259.81694473522,
        density_kg_per_m3=1780.0,
        alpha_volume_per_K=2.0e-5,
        bulk_modulus_Pa=3.0e10,
        sigma_temperature_K=0.1,
        sigma_cp_mass_J_per_kg_K=69.8470681678102,
        sigma_density_kg_per_m3=20.0,
        sigma_alpha_volume_per_K=1.0e-6,
        sigma_bulk_modulus_Pa=1.0e9,
    )


def test_mass_and_volumetric_corrections_are_consistent():
    inputs = _inputs()
    assert abs(
        cp_minus_cv_volumetric_J_per_m3_K(inputs)
        - inputs.density_kg_per_m3 * cp_minus_cv_mass_J_per_kg_K(inputs)
    ) < 1.0e-9
    assert abs(
        cv_mass_from_cp_J_per_kg_K(inputs)
        - cv_volumetric_from_cp_J_per_m3_K(inputs) / inputs.density_kg_per_m3
    ) < 1.0e-12


def test_uncertainty_requires_all_inputs_and_is_positive():
    assert cv_volumetric_uncertainty_J_per_m3_K(_inputs()) > 0.0
    incomplete = CpCvCorrectionInputs(
        temperature_K=573.15,
        cp_mass_J_per_kg_K=1259.81694473522,
        density_kg_per_m3=1780.0,
        alpha_volume_per_K=2.0e-5,
        bulk_modulus_Pa=3.0e10,
    )
    try:
        cv_volumetric_uncertainty_J_per_m3_K(incomplete)
    except ValueError as error:
        assert "uncertainties" in str(error)
    else:
        raise AssertionError("missing uncertainties must remain blocked")


def test_audit_keeps_source_and_holdout_boundaries_explicit():
    artifact = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_FORMULA_UNIT_CONTRACT_OPEN_INPUTS"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["witness"]["not_a_source_value"] is True
    assert artifact["source_anchor"]["numeric_graphite_inputs_consumed"] is False
    assert artifact["holdout_policy"]["xie_2026_accessed"] is False
    assert "volumetric_alpha_V_not_source_locked" in artifact["major_result"]["open_blockers"]
