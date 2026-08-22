from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_kim_2018_graphite_green_kubo_external_input_audit.json"
PACKAGE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/kim_2018_graphite_green_kubo_source_package.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_kim_external_transport_input_is_source_locked_but_not_uet() -> None:
    artifact = load(ARTIFACT)
    package = load(PACKAGE)
    assert artifact["status"] == "PASS_SCOPED_SOURCE_LOCKED_EXTERNAL_GREEN_KUBO_INPUT"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["checks"].values())
    assert package["acceptance"]["accepted_for_external_transport_input"] is True
    assert package["acceptance"]["accepted_for_uet_physical_kubo_coefficient"] is False
    assert package["acceptance"]["accepted_for_alpha_Phi_K_calibration"] is False


def test_kim_rows_preserve_uncertainty_and_no_holdout_access() -> None:
    artifact = load(ARTIFACT)
    rows = artifact["coefficient_rows"]
    assert {row["row_id"] for row in rows} == {
        "kim2018_pristine_graphite_c_axis_300K",
        "kim2018_pristine_graphite_basal_plane_300K",
    }
    assert all(row["uncertainty"] > 0 for row in rows)
    assert artifact["holdout_policy"]["xie_2026_accessed"] is False
    assert artifact["holdout_policy"]["xie_2026_source_data_consumed"] is False
    assert artifact["holdout_policy"]["fit_performed"] is False
