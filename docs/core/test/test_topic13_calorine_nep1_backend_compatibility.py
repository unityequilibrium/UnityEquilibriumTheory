from docs.core.core_paths import repo_root
import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/t13_calorine_nep1_backend_compatibility_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "calorine_nep1_backend_compatibility_source_package.json"
)


def test_calorine_nep1_backend_boundary_is_explicit() -> None:
    audit = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_SCOPED_CALORINE_NEP1_BACKEND_COMPATIBILITY_BOUNDARY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["model_format"]["format_id"] == "NEP1_LEGACY_SPACE_VERSION"
    assert audit["source"]["model"]["sha256"] == (
        "cf75256947a8953b8041ccc26a34ac307724f69bf2edbcc97b46d87bc5e72408"
    )
    assert audit["checks"]["model_bytes_not_rewritten"] is True
    assert audit["checks"]["numeric_csrc_emitted"] is False
    assert audit["checks"]["alpha_calibration_emitted"] is False
    assert audit["checks"]["holdout_accessed"] is False
    assert audit["runtime_preflight"]["numeric_rerun_performed"] is False
    assert audit["claim_promotion"] is False
    assert package["source"]["model_format"]["version"] == 1
    assert package["acceptance"]["accepted_as_independent_csrc_reproduction"] is False
