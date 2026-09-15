from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/07_artifacts/topic13/t13_nist_graphite_alpha_v_source_boundary_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_nist_alpha_v_source_boundary_is_closed_without_k_t_or_ttg_promotion() -> None:
    lane = load(LANE)
    major = lane["major_result"]
    assert lane["status"] == "PASS_SCOPED_NIST_ALPHA_V_SOURCE_BOUNDARY"
    assert major["major_result_id"] == "T13_NIST_GRAPHITE_ALPHA_V_SOURCE_BOUNDARY"
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert major["data_role"] == "INTERNAL_SOURCE_COMPARATOR_NOT_DING_TTG_GRADE"
    assert lane["source"]["material"] == "AXM-5Q1 fine-grained isotropic graphite"
    assert [row["temperature_K"] for row in lane["rows"]] == [200.0, 225.0, 250.0, 300.0]
    assert all(row["alpha_V_per_K"] > 0.0 for row in lane["rows"])
    assert all(lane["checks"].values())
    assert lane["holdout_accessed"] is False
    assert lane["target_fit_performed"] is False
    assert lane["numeric_alpha_Phi_K_emitted"] is False
    assert "not a Ding/HOPG material match" in major["claim_boundary"]
