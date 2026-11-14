from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_nist_axm5q1_density_source_boundary_audit.json"
PACKAGE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/nist_axm5q1_density_source_package.json"


def test_nist_axm5q1_density_boundary_is_source_locked_without_cv_promotion() -> None:
    result = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    row = result["rows"][0]
    assert result["status"] == "PASS_SCOPED_NIST_AXM5Q1_DENSITY_SOURCE_BOUNDARY"
    assert result["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert row["density_g_per_cm3"] == 1.721
    assert row["density_kg_per_m3"] == 1721.0
    assert row["measurement_method"] == "hydrostatic weighing"
    assert row["uncertainty_boundary"]["reported_relative_precision_bound"] == 0.001
    assert row["uncertainty_boundary"]["do_not_use_as_standard_uncertainty"] is True
    assert result["direct_volumetric_c_v_emitted"] is False
    assert result["numeric_alpha_Phi_K_emitted"] is False
    assert result["holdout_accessed"] is False
    assert package["rows"][0]["source_row_id"] == row["source_row_id"]
    assert "density_uncertainty_not_source_locked" in result["major_result"]["open_blockers"]
