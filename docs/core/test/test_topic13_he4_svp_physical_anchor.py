from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from docs.core.he4_svp_reference import (
    T_LAMBDA_K,
    calibration_grid,
    superfluid_density_kg_m3,
    total_density_kg_m3,
)


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/core/artifacts/t13_he4_svp_physical_anchor_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "he4_svp_o2_physical_anchor_source_package.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_reference_grid_is_physical_and_closes_density_ledger() -> None:
    rows = calibration_grid()
    assert len(rows) == 7
    assert [row["temperature_K"] for row in rows] == [1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
    for row in rows:
        assert row["temperature_K"] < T_LAMBDA_K
        assert 0.0 < row["superfluid_fraction"] < 1.0
        assert math.isclose(
            row["total_density_kg_m3"],
            row["superfluid_density_kg_m3"] + row["normal_density_kg_m3"],
            rel_tol=1.0e-12,
        )


def test_reference_functions_reject_out_of_domain_inputs() -> None:
    with pytest.raises(ValueError):
        total_density_kg_m3(5.0)
    with pytest.raises(ValueError):
        superfluid_density_kg_m3(T_LAMBDA_K + 1.0e-6)


def test_source_audit_closes_anchor_without_inventing_uncertainty_or_mapping() -> None:
    package = load(PACKAGE)
    audit = load(AUDIT)
    assert audit["status"] == "PASS_HE4_EQUILIBRIUM_SOURCE_ANCHOR_UNCERTAINTY_OPEN"
    assert all(audit["checks"].values())
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert package["observable_contract"]["mapping_status"] == "OPEN_INDEPENDENT_FIELD_NORMALIZATION"
    assert package["uncertainty_contract"]["numeric_uncertainty_consumed"] is False
    assert package["holdout_policy"]["xie_2026_accessed"] is False
    assert "independent_Z_Phi_field_normalization_missing" in audit["major_result"]["open_blockers"]
