from docs.core.core_paths import repo_root
import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_calorine_public_model_variant_boundary_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "calorine_zenodo_7811021_nep_cx_model_variant_source_package.json"
)


def test_calorine_public_model_variant_is_provenance_only() -> None:
    audit = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_SCOPED_CALORINE_PUBLIC_MODEL_VARIANT_BOUNDARY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["major_result"]["data_role"] == "EXTERNAL_MODEL_VARIANT_PROVENANCE_NOT_UNCERTAINTY"
    assert audit["inventory"]["sha256"] == "cf75256947a8953b8041ccc26a34ac307724f69bf2edbcc97b46d87bc5e72408"
    assert audit["inventory"]["md5"] == "fff758a996956f7331f2cc1be396d4ae"
    assert audit["inventory"]["size_bytes"] == 44098
    assert audit["checks"]["raw_hash_matches"] is True
    assert audit["checks"]["nep_header_matches"] is True
    assert audit["checks"]["variant_differs_from_tutorial"] is True
    assert audit["acceptance"]["accepted_for_full_topic13"] is False
    assert audit["acceptance"]["model_form_spread_emitted"] is False
    assert audit["acceptance"]["numeric_alpha_phi_k_emitted"] is False
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["claim_promotion"] is False
    assert package["source"]["model_variant"] == "C-CX"
    assert package["rerun_contract"]["numeric_rerun_performed"] is False
