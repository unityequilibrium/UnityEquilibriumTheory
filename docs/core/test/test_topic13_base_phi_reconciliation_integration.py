from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUT_AUDIT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"
RECONCILIATION = "docs/core/artifacts/t13_base_phi_si_reconciliation_audit.json"


def test_base_phi_reconciliation_is_projected_with_prior_waves() -> None:
    audit = json.loads(INPUT_AUDIT.read_text(encoding="utf-8-sig"))
    package = next(
        item for item in audit["packages"]
        if item["package_id"] == "T13_INPUT_BASE_PHI_SI_ALPHA_BETA"
    )
    current = package["current_evidence"]
    evidence_paths = {item["path"] for item in audit["evidence_artifacts"]}
    assert RECONCILIATION in evidence_paths
    assert "docs/core/artifacts/t13_cv_source_reconciliation_audit.json" in evidence_paths
    assert "docs/core/artifacts/t13_physical_transport_reconciliation_audit.json" in evidence_paths
    assert current["base_phi_reconciliation_status"] == "PASS_SCOPED_BASE_PHI_RECONCILIATION_OPEN"
    assert current["paired_alpha_search_candidate_count"] == 74
    assert current["eligible_paired_alpha_record_count"] == 0
    assert current["named_phi_e_comparator_count"] == 1
    assert current["independent_base_phi_si_record_count"] == 0
    assert current["eligible_base_phi_input_count"] == 0
    assert audit["checks"]["base_phi_reconciliation_is_fail_closed"] is True
