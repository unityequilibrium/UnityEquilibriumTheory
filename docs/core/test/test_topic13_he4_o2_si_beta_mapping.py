from __future__ import annotations

import json
import math
from pathlib import Path

from docs.core.he4_o2_si_beta_mapping import si_beta_record


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/core/artifacts/t13_he4_o2_si_beta_mapping_audit.json"


def test_si_beta_record_is_finite_uncertainty_bearing_and_non_circular() -> None:
    record = si_beta_record()
    assert record["temperature_standard_uncertainty_K"] > 0.0
    assert record["energy_density_scale_J_m3"] > 0.0
    assert record["energy_density_scale_uncertainty_J_m3"] > 0.0
    assert math.isfinite(record["beta_T13"])
    assert record["beta_T13_uncertainty_bound"] > 0.0
    assert math.isfinite(record["beta_SI_J_m3_per_normalized_Phi2"])
    assert record["beta_SI_uncertainty_J_m3_per_normalized_Phi2"] > 0.0
    assert record["holdout_policy"]["landauer_identity_used"] is False
    assert record["holdout_policy"]["xie_2026_accessed"] is False


def test_si_beta_audit_closes_only_the_dimensional_lane() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_HE4_SI_SCALE_AND_NORMALIZED_BETA"
    assert all(audit["checks"].values())
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["major_result"]["open_blockers"] == [
        "physical_transport_coefficient_not_closed"
    ]
