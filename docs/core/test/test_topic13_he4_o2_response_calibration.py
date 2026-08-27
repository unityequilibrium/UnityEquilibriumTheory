from __future__ import annotations

import json
import math
from pathlib import Path

from docs.core.he4_o2_response_calibration import calibration_record


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/core/artifacts/t13_he4_o2_response_calibration_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_calibration_is_finite_signed_and_uncertainty_bearing() -> None:
    record = calibration_record()
    assert math.isfinite(record["alpha_Phi_K"])
    assert record["alpha_Phi_K"] < 0.0
    assert record["alpha_uncertainty_K_per_normalized_base_Phi"] > 0.0
    assert record["Z_Phi_normalized_per_natural_Phi"] < 0.0
    assert record["Z_Phi_uncertainty_bound"] > 0.0


def test_calibration_audit_closes_alpha_lane_without_closing_topic() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_HE4_LOCAL_ALPHA_AND_FIELD_NORMALIZATION"
    assert all(audit["checks"].values())
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert "SI_energy_density_scale_not_closed" in audit["major_result"]["open_blockers"]
    assert audit["record"]["holdout_policy"]["xie_2026_accessed"] is False
