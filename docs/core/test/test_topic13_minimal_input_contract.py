from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "docs/core/artifacts/t13_full_closure_minimal_input_contract.json"
PROGRESS = ROOT / "docs/core/artifacts/t13_full_closure_progress.json"
INPUT_AUDIT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_minimal_input_contract_covers_current_open_subresults() -> None:
    contract = load(CONTRACT)
    progress = load(PROGRESS)
    input_audit = load(INPUT_AUDIT)

    assert progress["minimal_input_contract"]["path"] == "docs/core/artifacts/t13_full_closure_minimal_input_contract.json"
    assert progress["minimal_input_contract"]["sha256"] == digest(CONTRACT)
    assert progress["minimal_input_contract"]["status"] == contract["status"]
    assert contract["status"] == "PASS_SCOPED_MINIMAL_INPUT_CONTRACT_OPEN"
    assert contract["full_closure_rule"]["required_subresult_count"] == 36
    assert contract["full_closure_rule"]["current_open_subresult_count"] == 10
    assert contract["full_closure_rule"]["required_root_input_package_count"] == 3
    assert contract["full_closure_rule"]["target_result"] == "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY"

    package_ids = {item["package_id"] for item in contract["packages"]}
    assert package_ids == {
        "T13_INPUT_DING_TTG_SOURCE",
        "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
        "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
    }
    assert package_ids == {item["package_id"] for item in input_audit["packages"]}

    open_ids = {item["subresult_id"] for item in progress["open_subresults"]}
    unlock_ids = {
        subresult_id
        for package in contract["packages"]
        for subresult_id in package["unlocks_subresults"]
    }
    assert open_ids <= unlock_ids
    assert all(item["status"] == "BLOCKED" for item in contract["current_evidence"].values())


def test_minimal_input_contract_preserves_claim_and_holdout_boundaries() -> None:
    contract = load(CONTRACT)
    policy = contract["holdout_policy"]

    assert policy["xie_2026_accessed"] is False
    assert policy["calibration_path_may_read_holdout"] is False
    assert policy["target_fit_performed"] is False
    assert policy["alpha_fit_performed"] is False
    assert policy["threshold_adjustment_allowed"] is False
    assert contract["full_closure_rule"]["claim_promotion_remains_false_until_transition"] is True
    assert "does not satisfy any missing input" in contract["claim_boundary"]
    assert "C_src" not in contract["current_evidence"]
