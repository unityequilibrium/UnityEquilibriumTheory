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
                  "thermal_oneloop_ward_current_evidence_2026_10_01", "finite_momentum_thermal_1pi_evidence_2026_10_01"):
        evidence = PLAN[field]
        path = ROOT / evidence["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
        record = json.loads(path.read_text(encoding="utf-8"))
        assert record["verification_status"] == evidence["verification_status"]
        for flag in ("g1_physical_unlock", "g2_science_unlock", "full_core_unlock"):
            assert evidence[flag] is False
            assert record[flag] is False
