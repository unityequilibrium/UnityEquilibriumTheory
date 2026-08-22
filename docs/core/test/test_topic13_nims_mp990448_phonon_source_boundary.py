import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_nims_mp990448_phonon_source_boundary_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "nims_mdr_mp990448_phonon_source_package.json"
)
ARCHIVE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "nims_mdr_mp990448_graphite_phonon_dataset.zip"
)
LEGACY_ARCHIVE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "nims_mdr_wd3761563_legacy.zip"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_nims_mp990448_is_a_payload_boundary_not_numeric_csrc() -> None:
    audit = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_SCOPED_NIMS_MP990448_PHONON_PAYLOAD_BOUNDARY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["major_result"]["data_role"] == "SOURCE_PAYLOAD_BOUNDARY_NOT_CALIBRATION"
    assert audit["inventory"]["member_count"] == 6
    assert audit["checks"]["expected_member_set"] is True
    assert audit["checks"]["no_force_constants_data"] is True
    assert audit["checks"]["no_frequency_mesh"] is True
    assert audit["checks"]["no_machine_readable_thermal_rows"] is True
    assert audit["checks"]["thermal_properties_is_figure_only"] is True
    assert audit["checks"]["legacy_route_archive_exists"] is True
    assert audit["checks"]["legacy_route_hash_and_size_match_current"] is True
    assert audit["legacy_route"]["route_decision"] == "BYTE_IDENTICAL_ALIAS_OF_CURRENT_NIMS_ARCHIVE"
    assert audit["payload_capabilities"]["has_force_constants_data"] is False
    assert audit["payload_capabilities"]["has_frequency_mesh"] is False
    assert package["source"]["license"] == "CC BY 4.0"
    assert package["row_identity_contract"]["machine_readable_numeric_rows"] == []
    assert package["holdout_policy"]["xie_2026_accessed"] is False
    assert package["claim_promotion"] is False
    assert digest(ARCHIVE) == audit["source"]["archive_sha256"]
    assert digest(LEGACY_ARCHIVE) == audit["source"]["archive_sha256"]

