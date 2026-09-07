from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUT_AUDIT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"
RECONCILIATION = "docs/core/artifacts/t13_csrc_reconciliation_audit.json"


def test_csrc_reconciliation_is_projected_with_all_prior_waves() -> None:
    audit = json.loads(INPUT_AUDIT.read_text(encoding="utf-8-sig"))
    package = next(
        item for item in audit["packages"]
        if item["package_id"] == "T13_INPUT_DING_TTG_SOURCE"
    )
    current = package["current_evidence"]
    evidence_paths = {item["path"] for item in audit["evidence_artifacts"]}
    assert RECONCILIATION in evidence_paths
    assert "docs/core/artifacts/t13_cv_source_reconciliation_audit.json" in evidence_paths
    assert "docs/core/artifacts/t13_physical_transport_reconciliation_audit.json" in evidence_paths
    assert "docs/core/artifacts/t13_base_phi_si_reconciliation_audit.json" in evidence_paths
    assert current["csrc_reconciliation_status"] == "PASS_SCOPED_CSRC_RECONCILIATION_OPEN"
    assert current["csrc_route_count"] == 10
    assert current["numeric_csrc_candidate_count"] == 3
    assert current["source_grade_uncertainty_count"] == 0
    assert current["ding_material_state_match_count"] == 0
    assert current["accepted_independent_reproduction_count"] == 0
    assert current["eligible_csrc_input_count"] == 0
    assert audit["checks"]["csrc_reconciliation_is_fail_closed"] is True
