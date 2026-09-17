from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path


ROOT = repo_root()
PACKAGE_PATH = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "farooqui_2022_ig210_thermophysical_source_package.json"
)
RAW_PATH = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "farooqui_2022_ig210_thermophysical_table.pdf"
)


def load_package() -> dict:
    return json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))


def test_farooqui_raw_source_identity_is_locked() -> None:
    package = load_package()
    source = package["source"]
    if RAW_PATH.is_file():
        assert RAW_PATH.stat().st_size == source["local_raw_size_bytes"]
        assert hashlib.md5(RAW_PATH.read_bytes()).hexdigest() == source["local_raw_md5"]
        assert hashlib.sha256(RAW_PATH.read_bytes()).hexdigest() == source["local_raw_sha256"]
    else:
        # The public checkout carries the source package, not the raw PDF.
        # Keep the expected identity visible without fabricating local bytes.
        assert source["local_raw_path"] == RAW_PATH.relative_to(ROOT).as_posix()
        assert len(source["local_raw_md5"]) == 32
        assert len(source["local_raw_sha256"]) == 64
        assert source["local_raw_size_bytes"] > 0


def test_farooqui_rows_have_same_grade_properties_and_uncertainty() -> None:
    package = load_package()
    rows = package["source_rows"]
    assert [row["temperature_C"] for row in rows] == [500.0, 700.0, 1000.0]
    assert [row["density_kg_per_m3"] for row in rows] == [1781.0, 1775.0, 1765.0]
    assert [row["specific_heat_Cp_J_per_kg_K"] for row in rows] == [1549.0, 1807.0, 1892.0]
    assert all(row["uncertainty"]["coverage_factor"] == 2 for row in rows)
    assert all(row["uncertainty"]["density_relative_expanded"] == 0.003 for row in rows)
    assert all(row["uncertainty"]["specific_heat_relative_expanded"] == 0.06 for row in rows)


def test_farooqui_lane_does_not_emit_cv_kt_or_alpha_calibration() -> None:
    package = load_package()
    comparator = package["derived_comparator"]
    assert comparator["same_grade_ig210_source"] is True
    assert comparator["same_state_K_T_present"] is False
    assert comparator["c_v_present"] is False
    assert comparator["Ding_TTG_material_match_closed"] is False
    assert comparator["alpha_Phi_K_calibration_emitted"] is False
    assert package["holdout_policy"]["xie_2026_accessed"] is False
