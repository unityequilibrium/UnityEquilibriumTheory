"""Delivery/model planning checks, not scientific or funding acceptance."""

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
PLAN = json.loads(
    (TOPIC / "Data/03_Research/funding_portfolio_14d_plan.json").read_text(
        encoding="utf-8"
    )
)
ADDENDUM = PLAN["delivery_and_model_addendum_2026_10_02"]


def test_plan_does_not_accept_pending_science_or_restart_sprint():
    assert ADDENDUM["record_class"] == "PLANNING_NOT_SCIENTIFIC_CLOSURE"
    assert PLAN["start_date"] == "2026-09-28"
    assert PLAN["delivery_date"] == "2026-10-11"
    assert not ADDENDUM["uncommitted_vacuum_cut_exploration_accepted"]
    for name in (
        "goal_completion_rule_changed", "goal_or_automation_created",
        "physical_gate_changed", "claim_promotion", "dependency_unlock",
    ):
        assert ADDENDUM[name] is False
    assert not PLAN["completion_rule"]["documents_alone_satisfy_goal"]
    assert not PLAN["completion_rule"]["unresolved_satisfies_goal"]


def test_existing_scientific_baseline_is_hash_identified_not_promoted():
    field = ADDENDUM["scientific_baseline_evidence_field"]
    baseline = PLAN[field]
    assert hashlib.sha256((ROOT / baseline["path"]).read_bytes()).hexdigest() == (
        baseline["sha256"]
    )
    assert baseline["closure_level"] == "CLOSED_FOR_LANE"
    assert not baseline["full_core_unlock"]
    assert not baseline["independent_alpha_Phi_K_admitted"]
    assert not baseline["physical_Kubo_emitted"]


def test_core_observation_does_not_certify_current_gate_or_blinding():
    observed = ADDENDUM["core_owner_observation"]
    assert observed["role"] == "READ_ONLY_PRIMARY_CHECKOUT_SNAPSHOT_NOT_REVALIDATION"
    assert observed["recorded_closure"] == "CLOSED_FOR_CORE"
    assert not observed["reverified_by_this_plan"]
    assert not observed["owner_files_changed"]
    assert observed["holdout_eligibility"] == "REVIEW_REQUIRED"
    assert not observed["older_PASS_is_pristine_blinding_certificate"]
    for name in ("matrix_sha256", "holdout_incident_sha256"):
        assert len(observed[name]) == 64
        assert all(char in "0123456789abcdef" for char in observed[name])


def test_major_result_requires_connected_deliverables_not_artifact_count():
    package = ADDENDUM["minimum_major_result_package"]
    assert len(package["components"]) == 3
    assert package["all_components_required_for_package_acceptance"]
    assert package["existing_evidence_is_preliminary_not_complete_package"]
    assert not package["missing_source_implies_no_go"]
    assert not package["acceptance_changes_G0_G5_or_R1_R5"]


def test_four_delivery_packets_fit_original_freeze_and_review():
    packets = ADDENDUM["pre_freeze_packets"]
    assert [item["due"] for item in packets] == [
        "2026-10-03", "2026-10-05", "2026-10-07", "2026-10-11"
    ]
    assert all(item["status"] == "PLANNED_NOT_ACCEPTED" for item in packets)
    assert all(item["owner"] and item["acceptance"] for item in packets)
    assert packets[-1]["due"] == PLAN["delivery_date"]
    review = PLAN["execution_review_2026_10_01"]["two_week_decision"]
    assert packets[2]["due"] == review["scientific_freeze_date"]


def test_model_policy_is_recommendation_not_measured_outcome():
    models = ADDENDUM["model_use_policy"]
    assert models["lead"] == {"model": "gpt-6-astra", "effort": "high"}
    assert models["implementation"] == {"model": "gpt-6.1-sol", "effort": "high"}
    assert models["bounded_proof_review"]["effort"] == "xhigh"
    assert models["single_model_with_usage_constraints"] == "gpt-6.1-sol"
    assert models["trial_status"] == "NOT_RUN"
    assert models["trial_minutes_cap_per_configuration"] == 90
    assert models["critical_errors_allowed"] == 0
    assert models["measured_cost"] is None
    assert not models["model_configuration_changed"]
    assert not models["model_agreement_is_external_replication"]


def test_effort_and_anti_rerun_rules_do_not_authorize_external_actions():
    limits = ADDENDUM["operating_limits"]
    assert limits["decisive_calculations_in_flight_max"] == 1
    assert limits["parallel_source_inventory_allowed"]
    for name in ("before_freeze_effort_percent", "after_freeze_effort_percent"):
        assert sum(limits[name].values()) == 100
    assert limits["percentages_are_planning_allocations_not_measured_usage"]
    assert limits["no_new_evidence_waves_before_explicit_route_review"] == 2
    assert not limits["unchanged_reruns_count_as_scientific_progress"]
    assert not limits["purchase_contact_submission_authorized"]


def test_long_term_results_and_unknown_calls_are_not_replaced():
    old = PLAN["execution_review_2026_10_01"]["next_round_review_cards"]
    new = ADDENDUM["long_term_progress_units"]
    assert [item["review"] for item in new] == [item["review_date"] for item in old]
    assert [item["results"] for item in new] == [item["result_ids"] for item in old]
    policy = ADDENDUM["missed_round_policy"]
    assert ADDENDUM["user_confirmed_funder_status"] == "NOT_YET_SELECTED"
    assert PLAN["funder"] is None and PLAN["submission_deadline"] is None
    for name in (
        "first_round_eligibility_known", "first_round_missed_is_assumed",
        "next_call_date_known", "full_topic_closure_guaranteed_within_three_months",
    ):
        assert policy[name] is False
    assert policy["preserve_portfolio_v1"]
    portfolio = date.fromisoformat(PLAN["delivery_date"])
    assert date.fromisoformat(policy["two_month_scenario"]) > portfolio
    assert policy["three_month_scenario"] == "2027-01-11"
    assert policy["actual_call_overrides_internal_release"]


def test_readable_plan_covers_model_results_and_unknown_funder():
    content = (ROOT / ADDENDUM["document"]).read_text(encoding="utf-8")
    for token in (
        "GPT-6 Astra / high", "GPT-6.1 Sol / high", "R1", "R2", "R3", "R4", "R5",
        "REVIEW_REQUIRED", "NOT_RUN", "11 ม.ค. 2027", "ยังไม่เลือกทุน",
    ):
        assert token in content
    for field in PLAN["report_fields"]:
        assert f"{field}:" in content
