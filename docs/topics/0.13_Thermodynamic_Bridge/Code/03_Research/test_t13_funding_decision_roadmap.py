"""Planning invariants; these checks do not validate any physical branch."""

import hashlib
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
RECORD = json.loads(
    (TOPIC / "Data/03_Research/funding_decision_roadmap_2026_10_02.json").read_text(
        encoding="utf-8"
    )
)
CANONICAL = json.loads(
    (ROOT / RECORD["canonical_acceptance_contract"]).read_text(encoding="utf-8")
)


def test_planning_does_not_accept_scientific_work():
    assert RECORD["record_class"] == "PLANNING_NOT_SCIENTIFIC_CLOSURE"
    assert not RECORD["sprint"]["scientific_disposition_accepted"]
    assert not RECORD["sprint"]["portfolio_ready_implies_science_closed"]
    assert not RECORD["sprint"]["portfolio_ready_implies_submission_ready"]
    assert not CANONICAL["completion_rule"]["documents_alone_satisfy_goal"]
    assert not CANONICAL["completion_rule"]["unresolved_satisfies_goal"]


def test_baseline_hash_and_blocker_match_evidence():
    baseline = RECORD["baseline"]
    payload = (ROOT / baseline["artifact"]).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == baseline["sha256"]
    assert baseline["controlling_blocker"] == (
        CANONICAL["hartree_low_T_validity_evidence_2026_10_02"]["controlling_blocker"]
    )
    assert not baseline["new_scientific_validation_performed_by_this_record"]


def test_sprint_dates_not_restarted():
    sprint = RECORD["sprint"]
    review = CANONICAL["execution_review_2026_10_01"]["two_week_decision"]
    assert sprint["start"] == "2026-09-28"
    assert sprint["route_review"] == review["route_decision_date"]
    assert sprint["scientific_freeze"] == review["scientific_freeze_date"]
    assert sprint["portfolio_review"] == review["portfolio_date"]
    assert not sprint["restarted"]


def test_long_term_dates_preserve_existing_review_cards():
    old = CANONICAL["execution_review_2026_10_01"]["next_round_review_cards"]
    new = RECORD["long_term_reviews"]
    assert [item["date"] for item in new] == [item["review_date"] for item in old]
    assert [item["results"] for item in new] == [item["result_ids"] for item in old]
    assert all(item["status"] == "PLANNED_NOT_ACCEPTED" for item in new)


def test_call_scenarios_have_buffers_not_confirmed_deadlines():
    assert RECORD["funding_unknowns"]["confirmed_call"] is None
    assert RECORD["funding_unknowns"]["actual_deadline"] is None
    for item in RECORD["call_scenarios"]:
        deadline = date.fromisoformat(item["assumed_deadline"])
        assert item["status"] == "SCENARIO_NOT_CONFIRMED_CALL"
        for field, days in (
            ("scientific_freeze", 14),
            ("institutional_documents", 7),
            ("attachment_review", 3),
        ):
            assert (deadline - date.fromisoformat(item[field])).days == days
        assert item["overrides_later_research_review"]


def test_model_recommendations_not_a_completed_trial():
    models = RECORD["model_recommendations"]
    assert models["trial_status"] == "NOT_RUN"
    assert models["trial_result"] is None
    assert not models["model_configuration_changed"]
    old = CANONICAL["execution_review_2026_10_01"]["model_trial"]
    assert models["lead"]["model"] == old["recommended_owner"]
    assert models["lead"]["effort"] == old["recommended_owner_effort"]
    assert models["trial_minutes_per_configuration_max"] == old["pilot_minutes_cap"]


def test_protected_physical_and_holdout_boundaries():
    protected = RECORD["protected_boundaries"]
    for key in (
        "canonical_completion_rule_changed", "physical_gate_changed",
        "core_composition_overwritten", "dependency_unlock", "claim_promotion",
        "xie_2026_use_allowed", "new_numeric_holdout_access", "ontology_changed",
        "public_api_added",
    ):
        assert protected[key] is False
    assert protected["causal_leakage_threshold"] == 1e-6
    assert protected["conserved_C_failed_branch"] == "BLOCKED"
    assert protected["prior_xie_exposure"] == "REVIEW_REQUIRED"


def test_roadmap_links_and_reports_are_present():
    document = ROOT / RECORD["decision_document"]
    content = document.read_text(encoding="utf-8")
    for field in CANONICAL["report_fields"]:
        assert f"{field}:" in content
    assert RECORD["report_fields"] == CANONICAL["report_fields"]
    for target in re.findall(r"\]\(([^)]+)\)", content):
        if target.startswith("https://"):
            continue
        assert (document.parent / target).is_file(), target


def test_no_automatic_goal_reconfiguration_or_external_action():
    policy = RECORD["execution_policy"]
    assert policy["decisive_questions_in_flight_max"] == 1
    for key in (
        "new_goal_or_automation_created", "existing_active_goal_reconfigured",
        "purchase_contact_or_submission_authorized_by_plan",
        "unchanged_reruns_are_progress", "model_agreement_is_external_replication",
    ):
        assert policy[key] is False
    assert all(item["status"] == "PLANNED_NOT_ACCEPTED" for item in RECORD["work_packets"])
