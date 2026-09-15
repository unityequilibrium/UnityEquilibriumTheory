from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_physical_kubo_coefficient_provenance_audit.json"
CONTRACT = ROOT / "docs/core/07_artifacts/archive/covariant_superfluid_transport_contract.json"
VERIFICATION = ROOT / "docs/core/07_artifacts/verification/covariant_superfluid_transport_verification.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_provenance_gate_passes_without_emitting_a_coefficient() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_KUBO_PROVENANCE_GATE_OPEN_PHYSICAL_COEFFICIENT"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["checks"]["numeric_transport_coefficient_not_emitted"] is True
    assert audit["controlling_blocker"] == "physical_Kubo_coefficient_record_missing"


def test_current_sources_are_not_numeric_coefficient_data() -> None:
    audit = load(AUDIT)
    assert len(audit["source_inventory"]) == 5
    assert all(item["coefficient_data_status"] == "NOT_PROVIDED" for item in audit["source_inventory"])


def test_transport_contract_and_verifier_keep_physical_lane_blocked() -> None:
    contract = load(CONTRACT)
    verification = load(VERIFICATION)
    assert contract["core_contract"]["transport_values"] == "REQUIRED_EXTERNAL_OR_MICROSCOPIC_MATCH_NO_DEFAULTS"
    assert verification["physical_coefficient_evidence"] == "BLOCKED_NOT_PROVIDED"
    assert verification["finite_temperature_two_fluid_completion"] == "BLOCKED"
