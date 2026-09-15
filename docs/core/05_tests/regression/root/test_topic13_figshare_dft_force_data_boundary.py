from docs.core.core_paths import repo_root
import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/t13_figshare_dft_force_data_boundary_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "t13_figshare_dft_force_data_source_package.json"
)


def test_figshare_force_data_route_is_a_scoped_boundary() -> None:
    audit = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_SCOPED_FIGSHARE_DFT_FORCE_DATA_BOUNDARY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["major_result"]["data_role"] == "EXTERNAL_SOURCE_INPUT_NOT_CALIBRATION"
    assert audit["inventory"]["xyz_configuration_count"] == 4788
    assert audit["inventory"]["graphite_configuration_count"] == 742
    assert audit["checks"]["no_direct_pbte_payload_fields"] is True
    assert audit["payload_capabilities"]["has_third_order_force_constants"] is False
    assert audit["payload_capabilities"]["has_mode_heat_capacity"] is False
    assert audit["payload_capabilities"]["has_scattering_rates"] is False
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["claim_promotion"] is False
    assert package["source"]["license"] == "CC BY 4.0"
    assert package["row_identity_contract"]["all_member_paths_unique"] is True
