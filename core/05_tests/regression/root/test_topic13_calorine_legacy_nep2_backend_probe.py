from docs.core.core_paths import repo_root
import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_calorine_legacy_nep2_backend_probe_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "calorine_legacy_nep2_backend_probe_source_package.json"
)


def test_legacy_nep2_probe_is_source_locked_without_csrc_promotion() -> None:
    audit = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_SCOPED_CALORINE_LEGACY_NEP2_BACKEND_PROBE"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["runtime_probe"]["status"] == "PASS_LEGACY_NEP2_MODEL_PROBE"
    assert audit["runtime_probe"]["observed"]["returncode"] == "0"
    assert audit["runtime_probe"]["observed"]["potential_count"] == "4"
    assert audit["runtime_probe"]["observed"]["virial_count"] == "36"
    assert audit["checks"]["numeric_csrc_emitted"] is False
    assert audit["checks"]["numeric_alpha_phi_k_emitted"] is False
    assert audit["checks"]["holdout_accessed"] is False
    assert audit["claim_promotion"] is False
    assert package["source"]["backend"]["commit"] == (
        "eedb2ac9f49cb60a64512e987b98993d3a44e186"
    )
    assert package["acceptance"]["accepted_as_independent_csrc_reproduction"] is False
