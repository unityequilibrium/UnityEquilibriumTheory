"""Reader-facing planning guardrails, not scientific acceptance."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
PLAN = json.loads((TOPIC / "Data/03_Research/funding_portfolio_14d_plan.json").read_text(encoding="utf-8"))
BRIEF = PLAN["execution_reading_brief_2026_10_03"]


def test_brief_preserves_existing_dates_and_controller():
    assert BRIEF["record_class"] == "PLANNING_NOT_SCIENTIFIC_CLOSURE"
    assert BRIEF["canonical_controller_is_this_plan"]
    assert PLAN["start_date"] == "2026-09-28"
    assert BRIEF["scientific_freeze"] == "2026-10-07"
    assert BRIEF["portfolio_review"] == PLAN["delivery_date"] == "2026-10-11"
    assert BRIEF["review_dates"] == PLAN["user_timeline_review_2026_10_03"]["review_dates_unchanged"]


def test_brief_is_not_science_or_goal_acceptance():
    for name in (
        "pending_Landau_exploration_accepted_by_brief", "model_configuration_changed",
        "goal_reconfigured", "scientific_gate_changed", "completion_rule_changed",
        "physical_dependency_unlocked", "holdout_policy_changed", "claim_promotion",
    ):
        assert BRIEF[name] is False
    assert not PLAN["completion_rule"]["documents_alone_satisfy_goal"]
    assert not PLAN["completion_rule"]["unresolved_satisfies_goal"]
    assert not PLAN["holdout_policy"]["xie_2026_use_allowed"]
    assert PLAN["holdout_policy"]["blind_eligibility"] == "REVIEW_REQUIRED"


def test_brief_snapshot_is_hash_identified_preliminary_evidence():
    evidence = PLAN[BRIEF["snapshot_evidence_field"]]
    assert hashlib.sha256((ROOT / evidence["path"]).read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["closure_level"] == "CLOSED_FOR_LANE"
    assert not evidence["full_core_unlock"]
    assert not evidence["independent_alpha_Phi_K_admitted"]


def test_funding_and_model_uncertainty_remain_explicit():
    assert BRIEF["funder_status"] == "NOT_YET_SELECTED"
    assert PLAN["funder"] is None and PLAN["submission_deadline"] is None
    assert BRIEF["model_trial_status"] == "NOT_RUN"
    for name in ("full_topic_closure_within_three_months_guaranteed", "next_funding_call_confirmed", "submission_ready"):
        assert BRIEF[name] is False
    assert all(url.startswith("https://developers.openai.com/") for url in BRIEF["model_guidance_sources"])


def test_reading_brief_connects_deliverables_and_report_fields():
    content = (ROOT / BRIEF["document"]).read_text(encoding="utf-8")
    for token in (
        "T13_HE4_PREDICTIVE_CONTENT_AND_MEASUREMENT_DESIGN", "G2/G3", "G4", "G5",
        "R1", "R2-R3", "R4", "R5", "GPT-6 Astra / high", "GPT-6.1 Sol / high",
        "90 นาที", "NOT_RUN", "REVIEW_REQUIRED", "UNRESOLVED",
        "11 ธ.ค. 2026", "11 ม.ค. 2027", "scenario", "source-to-state-to-detector",
    ):
        assert token in content
    for field in PLAN["report_fields"]:
        assert f"{field}:" in content
