"""Guard the source-route decision without treating it as data admission."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
AUDIT = json.loads((ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_independent_measurement_route_screen.json").read_text(encoding="utf-8"))


def test_route_roles_do_not_promote_response_data():
    routes = {row["route_id"]: row for row in AUDIT["routes"]}
    assert AUDIT["calibration_source_family"]["adopted_keys_in_calibration_window"] == [2, 3]
    assert routes["J02_RECOMMENDED_TABLE_4_3"]["decision"] == "COMPARATOR_ONLY_SOURCE_ANCESTRY_OVERLAP"
    assert routes["HEISERMAN_TABLE_4_1_KEY_1"]["decision"].startswith("NOT_INDEPENDENT")
    assert routes["TAM_AHLERS_TABLE_4_1_KEY_3"]["decision"].startswith("NOT_INDEPENDENT")
    assert routes["WANG_WAGNER_DONNELLY_TABLE_4_1_KEY_5"]["primary_full_text_or_raw_rows_verified"] is False
    assert routes["WANG_WAGNER_DONNELLY_TABLE_4_1_KEY_5"]["primary_abstract_verified"] is True
    assert "mixed_author_spline" in AUDIT["admission_requirements"][-2]
    assert routes["DASH_TAYLOR_OSCILLATING_DISK_NORMAL_DENSITY"]["numeric_rows_protocol_uncertainty_and_modern_temperature_scale_verified"] is False
    assert AUDIT["numeric_response_rows_admitted"] == 0
    assert AUDIT["independent_heii_validation_admitted"] is False
    assert AUDIT["xie_2026_accessed"] is False
    assert AUDIT["dependency_unlocked"] == []
    assert AUDIT["full_core_unlock"] is False


def test_local_evidence_hashes_match():
    for item in AUDIT["evidence_artifacts"]:
        path = ROOT / item["path"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
