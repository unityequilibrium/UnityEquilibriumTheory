from docs.core.core_paths import core_root
import json
from pathlib import Path


ROOT = core_root()
AUDIT_PATH = ROOT / "artifacts/t13_xie_2026_holdout_access_audit.json"
FULL_GATE_PATH = ROOT.parent / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_holdout_audit_distinguishes_metadata_from_data_consumption() -> None:
    artifact = _load(AUDIT_PATH)
    controls = artifact["audit"]

    assert artifact["status"] == "PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY"
    assert controls["metadata_only_observed"] is True
    assert controls["source_data_payload_observed"] is False
    assert controls["numeric_payload_consumed"] is False
    assert controls["numeric_rows_consumed"] is False
    assert controls["used_for_fit"] is False
    assert controls["used_for_tuning"] is False
    assert controls["used_for_calibration"] is False
    assert controls["used_for_threshold_adjustment"] is False
    assert controls["audit_path_read_source_data"] is False
    assert controls["locked_holdout_remains_unconsumed"] is True
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["claim_boundary"]


def test_full_gate_uses_canonical_holdout_audit_when_present() -> None:
    gate = _load(FULL_GATE_PATH)
    holdout = gate["verification_status"]["holdout_integrity"]
    assert holdout["canonical_access_audit"]["path"] == (
        "docs/core/07_artifacts/topic13/t13_xie_2026_holdout_access_audit.json"
    )
    assert holdout["metadata_only_observed"] is True
    assert holdout["numeric_payload_consumed"] is False
    assert holdout["used_for_fit"] is False
    assert holdout["used_for_tuning"] is False
    assert holdout["used_for_calibration"] is False
    assert holdout["used_for_threshold_adjustment"] is False
