from docs.core.core_paths import repo_root
import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/t13_huang_2023_nims_mdr_payload_boundary_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "huang_2023_nims_mdr_payload_source_package.json"
)


def test_huang_nims_mdr_route_is_an_article_only_boundary() -> None:
    audit = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_SCOPED_HUANG_2023_NIMS_MDR_PAYLOAD_BOUNDARY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["major_result"]["data_role"] == "SOURCE_AVAILABILITY_BOUNDARY_NOT_CALIBRATION"
    assert audit["inventory"]["member_count"] == 1
    assert audit["inventory"]["members"][0]["path"] == "s41467-023-37380-5.pdf"
    assert audit["inventory"]["members"][0]["size_bytes"] == 1441389
    assert audit["checks"]["single_pdf_member"] is True
    assert audit["checks"]["no_force_constant_files"] is True
    assert audit["checks"]["no_shengbte_payload"] is True
    assert audit["checks"]["no_numeric_csrc_rows"] is True
    assert audit["payload_capabilities"]["article_pdf_only"] is True
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["claim_promotion"] is False
    assert package["source"]["license"] == "CC BY 4.0"
    assert package["row_identity_contract"]["machine_readable_numeric_rows"] == []
