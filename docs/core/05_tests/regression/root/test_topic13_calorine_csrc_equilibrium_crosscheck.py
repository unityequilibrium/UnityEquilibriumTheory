from docs.core.core_paths import repo_root
import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_calorine_csrc_equilibrium_crosscheck_audit.json"


def test_calorine_equilibrium_crosscheck_is_scoped_and_source_separated() -> None:
    audit = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_SCOPED_CALORINE_C_SRC_EQUILIBRIUM_CROSSCHECK"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["major_result"]["data_role"] == "COMPARISON_ONLY_NOT_CALIBRATION"
    assert audit["checks"]["equilibrium_crosscheck_computed"] is True
    assert audit["checks"]["iaea_standard_uncertainty_not_promoted"] is True
    assert audit["checks"]["target_curve_used"] is False
    assert audit["checks"]["fit_performed"] is False
    assert audit["checks"]["alpha_phi_k_fit_performed"] is False
    assert audit["checks"]["holdout_accessed"] is False
    assert audit["claim_promotion"] is False
