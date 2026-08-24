import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/lowitzer_2006_graphite_pvt_full_source_package.json"
AUDIT_REL = "docs/core/artifacts/t13_lowitzer_graphite_pvt_full_source_pair_audit.json"
RAW_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/lowitzer_2006_graphite_pvt.pdf"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_lowitzer_full_pair_is_source_locked_and_scoped() -> None:
    package = load(PACKAGE_REL)
    audit = load(AUDIT_REL)
    raw = ROOT / RAW_REL

    assert package["status"] == "SOURCE_LOCKED_THERMODYNAMIC_PAIR_COMPARATOR_MATERIAL_MAPPING_OPEN"
    assert package["source"]["payload_state"] == "FULL_TEXT_ARCHIVED"
    assert raw.is_file()
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == package["source"]["local_raw_sha256"]
    assert package["source"]["local_raw_size_bytes"] == raw.stat().st_size
    assert len(package["source_rows"]) == 4
    assert all(row["temperature_K"] == 300.0 for row in package["source_rows"])
    assert package["pair_contract"]["same_study_pair_present"] is True
    assert package["pair_contract"]["same_sample_pair_present"] is True
    assert package["pair_contract"]["same_temperature_point_present"] is True
    assert package["pair_contract"]["same_grade_alpha_V_and_K_T_pair_closed"] is True
    assert package["pair_contract"]["Ding_material_regime_mapping_closed"] is False
    assert package["pair_contract"]["numeric_Ding_C_src_emitted"] is False
    assert package["derived_correction_witness"]["accepted_for_Ding_C_src"] is False
    assert package["derived_correction_witness"]["accepted_for_alpha_Phi_K"] is False
    assert audit["status"] == "PASS_SCOPED_SOURCE_LOCKED_LOWITZER_ALPHA_V_K_T_PAIR"
    assert all(audit["checks"].values())
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["calibration_path_may_read_holdout"] is False
    assert audit["derived_correction_witness"]["source_recorded_uncertainty_J_m3_K"] == 1583.27
    assert abs(audit["derived_correction_witness"]["uncertainty_J_m3_K"] - 1583.2725602371816) < 1e-12
