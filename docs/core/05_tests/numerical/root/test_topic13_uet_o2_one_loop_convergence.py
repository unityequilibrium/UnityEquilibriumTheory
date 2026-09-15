from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_convergence_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_one_loop_convergence_audit_passes() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_ACTION_DERIVED_ONE_LOOP_CONVERGENCE"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_convergence_result_keeps_physical_boundaries_open() -> None:
    audit = load(AUDIT)
    assert audit["reference"]["cutoff_factor"] == 70.0
    assert audit["reference"]["quadrature_order"] == 256
    assert audit["policy"]["vacuum_counterterm_included"] is False
    assert audit["policy"]["condensate_included"] is False
    assert "physical_Kubo_coefficient_record_missing" in audit["major_result"]["open_blockers"]
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False
