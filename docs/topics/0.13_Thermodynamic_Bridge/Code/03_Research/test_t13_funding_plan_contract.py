"""Planning dates and model recommendations must not promote scientific gates."""

from datetime import date, timedelta
import hashlib
import json
from pathlib import Path


TOPIC = Path(__file__).resolve().parents[2]
ROOT = Path(__file__).resolve().parents[5]
PLAN = json.loads((TOPIC / "Data/03_Research/funding_portfolio_14d_plan.json").read_text(encoding="utf-8"))


def test_model_recommendations_are_not_configuration_changes():
    policy = PLAN["model_policy"]
    assert policy["recommendation_checked_on"] == "2026-10-01"
    assert policy["goal_owner"]["model"] == "gpt-6-astra"
    assert policy["implementation"]["model"] == "gpt-6.1-sol"
    assert policy["configuration_changed"] is False
    assert policy["automatic_model_switching_assumed"] is False
    assert policy["recommendations_are_not_repo_benchmark_results"] is True
    assert policy["api_price_is_not_codex_account_cost"] is True
    assert policy["critical_false_claims_allowed"] == 0


def test_calendar_revision_preserves_original_sprint_and_call_uncertainty():
    start = date.fromisoformat(PLAN["start_date"])
    end = date.fromisoformat(PLAN["delivery_date"])
    assert (end - start).days + 1 == PLAN["user_confirmed_duration_days"] == 14
    revision = PLAN["planning_revision_2026_10_01"]
    assert revision["delivery_date_unchanged"] is True
    assert revision["start_date_restarted"] is False
    assert revision["next_call_dates_verified"] is False
    assert PLAN["submission_deadline"] is None
    previous = end
    for checkpoint in PLAN["long_term_roadmap"]["checkpoints"]:
        first = date.fromisoformat(checkpoint["start_date"])
        last = date.fromisoformat(checkpoint["end_date"])
        assert first == previous + timedelta(days=1)
        assert (last - first).days + 1 == 14
        assert checkpoint["status"] == "NOT_STARTED"
        previous = last
    assert previous == date(2026, 12, 20)


def test_planning_revision_cannot_complete_research_or_overwrite_core_scope():
    revision = PLAN["planning_revision_2026_10_01"]
    assert revision["record_class"] == "PLANNING_NOT_SCIENTIFIC_CLOSURE"
    assert revision["goal_reconfigured"] is False
    assert revision["physical_gate_changed"] is False
    assert len(set(revision["readiness_dimensions"])) == 3
    assert sum(revision["initial_effort_fraction"].values()) == 1.0
    assert PLAN["claim_promotion"] is False
    assert PLAN["dependency_unlock_performed"] is False
    for field in ("documents_alone_satisfy_goal", "timeout_satisfies_goal", "unresolved_satisfies_goal"):
        assert PLAN["completion_rule"][field] is False


def test_plan_documents_and_latest_evidence_are_linked_without_holdout_reads():
    for field in ("plan_document", "goal_brief", "long_term_plan_document"):
        assert (ROOT / PLAN[field]).is_file()
    for field in ("conditional_operator_evidence_2026_10_01", "thermal_gradient_evidence_2026_10_01",
                  "thermal_oneloop_ward_current_evidence_2026_10_01", "finite_momentum_thermal_1pi_evidence_2026_10_01",
                  "polar_static_ir_observable_evidence_2026_10_01", "polar_dynamic_composite_evidence_2026_10_01",
                  "renormalized_hartree_background_evidence_2026_10_01", "hartree_counterterm_matching_evidence_2026_10_01",
                  "hartree_external_response_evidence_2026_10_01"):
        evidence = PLAN[field]
        path = ROOT / evidence["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
        record = json.loads(path.read_text(encoding="utf-8"))
        assert record["verification_status"] == evidence["verification_status"]
        for flag in ("g1_physical_unlock", "g2_science_unlock", "full_core_unlock"):
            assert evidence[flag] is False
            assert record[flag] is False


def test_result_ladder_is_planned_and_cannot_substitute_for_physics():
    execution = PLAN["result_level_execution_2026_10_01"]
    assert execution["record_class"] == "PLANNING_NOT_SCIENTIFIC_CLOSURE"
    cards = {card["id"]: card for card in execution["result_cards"]}
    assert set(cards) == {"R1", "R2", "R3", "R4", "R5"}
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in cards.values())
    for field in execution["evidence_baseline_fields"]:
        assert PLAN[field]["closure_level"] == "CLOSED_FOR_LANE"
    assert "internal propagator" in cards["R1"]["not_sufficient"]
    assert cards["R3"]["source_acquisition_parallel_to_R1"] is True
    assert cards["R3"]["feasibility_counts_as_empirical_input"] is False
    assert "R3 numeric-input admission" in cards["R4"]["empirical_requires"]
    assert cards["R4"]["missing_source_counts_as_no_go"] is False
    assert cards["R5"]["portfolio_completion_unlocks_physics"] is False
    for field in ("physical_gate_changed", "core_composition_gate_overwritten", "goal_reconfigured"):
        assert execution[field] is False
    assert len(execution["full_thermal_acceptance_still_requires"]) == 7


def test_submission_scenarios_respect_buffers_not_internal_week_dates():
    buffer = PLAN["result_level_execution_2026_10_01"]["submission_review_buffer"]
    assert buffer["status"] == "SCENARIO_NOT_CONFIRMED_CALL"
    assert date.fromisoformat(buffer["start_date"]) == date(2026, 12, 21)
    assert date.fromisoformat(buffer["end_date"]) == date(2027, 1, 11)
    assert buffer["actual_deadline_overrides_internal_calendar"] is True
    assert buffer["new_theory_expansion_allowed"] is False
    offsets = PLAN["long_term_roadmap"]["submission_buffers_days_before_actual_deadline"]
    for example in buffer["examples_not_confirmed_deadlines"]:
        deadline = date.fromisoformat(example["deadline"])
        for field, days in offsets.items():
            key = {
                "scientific_scope_freeze": "scientific_freeze",
                "final_forms_and_attachments": "forms_and_attachments",
            }.get(field, field)
            assert date.fromisoformat(example[key]) == deadline - timedelta(days=days)
    assert PLAN["submission_deadline"] is None


def test_execution_review_is_not_a_model_trial_or_physical_closure():
    review = PLAN["execution_review_2026_10_01"]
    assert review["record_class"] == "PLANNING_NOT_SCIENTIFIC_CLOSURE"
    assert review["scientific_deliverable_is_not_full_topic_closure"] is True
    assert PLAN[review["current_scientific_evidence_field"]]["gauge_current_vertex_computed"] is False
    trial = review["model_trial"]
    assert trial["status"] == "NOT_RUN"
    assert trial["configuration_changed"] is False
    assert trial["recommended_owner"] == PLAN["model_policy"]["goal_owner"]["model"]
    assert trial["execution_alternative"] == PLAN["model_policy"]["implementation"]["model"]
    assert trial["same_input_packet_required"] and trial["same_acceptance_required"]
    assert trial["critical_errors_allowed"] == 0
    assert trial["missing_usage_or_cost_is_null_not_zero"] is True
    assert trial["different_model_is_not_independent_physical_evidence"] is True
    assert "independent_check" in trial["record_fields"]
    assert "reviewer_correction_minutes" in trial["record_fields"]
    for flag in ("scope_and_date_alone_accept_results", "physical_gate_changed", "goal_reconfigured"):
        assert review[flag] is False


def test_execution_review_dates_match_existing_milestones():
    review = PLAN["execution_review_2026_10_01"]
    first = review["two_week_decision"]
    assert first["route_decision_date"] == "2026-10-02"
    assert first["scientific_freeze_date"] == "2026-10-07"
    assert first["portfolio_date"] == PLAN["delivery_date"]
    cards = review["next_round_review_cards"]
    checkpoints = PLAN["long_term_roadmap"]["checkpoints"]
    assert [card["review_date"] for card in cards] == [card["end_date"] for card in checkpoints]
    result_ids = {card["id"] for card in PLAN["result_level_execution_2026_10_01"]["result_cards"]}
    assert all(set(card["result_ids"]) <= result_ids for card in cards)
    assert "new_evidence_hashes" in review["weekly_review_fields"]
