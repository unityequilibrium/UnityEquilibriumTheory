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
                  "hartree_external_response_evidence_2026_10_01", "hartree_gauge_current_evidence_2026_10_01",
                  "hartree_real_axis_evidence_2026_10_01"):
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
    successor = PLAN[review["current_scientific_evidence_field"]]
    current = PLAN[successor["inherited_fixed_Phi_finite_q_poles_evidence_field"]]
    assert current["gauge_current_vertex_computed"] is True
    hartree_boundary = PLAN[successor["predecessor_validity_evidence_field"]]
    assert hartree_boundary["inherited_fixed_Phi_response_is_not_joint_response"] is True
    assert successor["prior_Hartree_results_are_not_new_EFT_dynamics"] is True
    assert PLAN[successor["inherited_joint_Phi_static_evidence_field"]]["joint_finite_q_complex_pole_computed"] is False
    response = PLAN[successor["inherited_joint_Phi_response_evidence_field"]]
    assert response["joint_finite_q_complex_pole_computed"] is True
    assert hartree_boundary["source_response_predecessor_invalidated"] is False
    assert current["real_axis_limit_admitted"] is True
    assert current["real_axis_admission_scope"] == "two_fixed_Phi_witnesses_and_ten_positive_frequency_q_points_not_global"
    assert current["global_real_axis_stability_proved"] is False
    assert current["controlled_truncation_error_established"] is False
    assert current["collisionless_soft_phase_kernel_derived"] is True
    assert current["soft_kernel_scope"] == "two_fixed_Phi_witnesses_four_velocity_rays_and_three_finite_q_cross_checks_not_global"
    assert current["real_axis_scope_is_inherited_from_predecessor"] is True
    assert current["collective_mode_speed_emitted"] is False
    assert current["collision_rate_emitted"] is False
    assert PLAN["hartree_gauge_current_evidence_2026_10_01"]["real_axis_limit_admitted"] is False
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


def test_portfolio_strategy_preserves_scientific_acceptance_and_existing_dates():
    strategy = PLAN["portfolio_strategy_2026_10_01"]
    assert strategy["record_class"] == "PLANNING_NOT_SCIENTIFIC_CLOSURE"
    assert strategy["status"] == "METHODS_ROUTE_SELECTED_FOR_PREPARATION"
    assert strategy["decision_dates"] == {
        "route_selection": "2026-10-02",
        "scientific_freeze": "2026-10-07",
        "portfolio_review": PLAN["delivery_date"],
    }
    assert strategy["new_real_axis_exploration_is_accepted_evidence"] is True
    assert "hartree_real_axis_evidence_2026_10_01" in strategy["accepted_preliminary_evidence_fields"]
    assert "hartree_soft_collective_evidence_2026_10_01" in strategy["accepted_preliminary_evidence_fields"]
    for flag in ("novelty_established_by_planning", "scientific_goal_completion_rule_changed",
                 "core_composition_gate_overwritten", "physical_gate_changed", "claim_promotion"):
        assert strategy[flag] is False
    assert strategy["review_readiness_not_submission_readiness"] is True
    for field in strategy["accepted_preliminary_evidence_fields"]:
        evidence = PLAN[field]
        assert evidence["closure_level"] == "CLOSED_FOR_LANE"
        assert hashlib.sha256((ROOT / evidence["path"]).read_bytes()).hexdigest() == evidence["sha256"]


def test_follow_on_aims_are_result_linked_not_promises_of_inputs_or_funding():
    strategy = PLAN["portfolio_strategy_2026_10_01"]
    result_ids = {card["id"] for card in PLAN["result_level_execution_2026_10_01"]["result_cards"]}
    assert [aim["id"] for aim in strategy["aims"]] == ["AIM1", "AIM2", "AIM3"]
    assert [aim["review_date"] for aim in strategy["aims"]] == [
        "2026-10-25", "2026-11-08", "2026-11-22"
    ]
    for aim in strategy["aims"]:
        assert set(aim["result_ids"]) <= result_ids
        for field in ("question", "acceptance", "failure_or_unresolved", "owner_role"):
            assert aim[field]
    scenario = strategy["next_round_scenario"]
    assert scenario["status"] == "SCENARIO_NOT_CONFIRMED_CALL"
    assert scenario["two_months_after_portfolio"] == "2026-12-11"
    assert scenario["three_months_after_portfolio"] == "2027-01-11"
    assert scenario["confirmed_call"] is None
    assert scenario["actual_call_deadline_overrides_week12"] is True
    assert scenario["portfolio_documents_alone_are_not_scientific_completion"] is True
    policy = strategy["resource_policy"]
    assert policy["model_trial_status"] == "NOT_RUN"
    assert policy["cash_budget"] is None
    for flag in ("model_configuration_changed", "lab_access_confirmed",
                 "purchase_or_external_contact_authorized"):
        assert policy[flag] is False


def test_local_pole_successor_changes_next_question_not_full_acceptance():
    field = "hartree_soft_poles_evidence_2026_10_01"
    current = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    predecessor = PLAN[current["inherited_fixed_Phi_finite_q_poles_evidence_field"]]
    assert predecessor["inherited_soft_poles_evidence_field"] == field
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    result = json.loads((ROOT/evidence["path"]).read_text(encoding="utf-8"))
    assert evidence["conditional_collisionless_soft_pole_computed"] is True
    assert result["conditional_collisionless_soft_pole_computed"] is True
    assert evidence["controlling_blocker"] == result["controlling_blocker"]
    assert evidence["soft_kernel_scope_is_inherited_from_predecessor"] is True
    for flag in ("certified_zero_count", "finite_q_complex_pole_computed", "controlled_truncation_error_established", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[flag] is False
        assert result[flag] is False
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_finite_q_discontinuity_is_not_finite_q_pole_or_funding_acceptance():
    field = "hartree_finite_q_discontinuity_evidence_2026_10_02"
    current = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    predecessor = PLAN[current["inherited_fixed_Phi_finite_q_poles_evidence_field"]]
    assert predecessor["inherited_finite_q_density_evidence_field"] == field
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text(encoding="utf-8"))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == result["verification_status"]
    assert evidence["finite_q_discontinuity_computed"] is result["finite_q_discontinuity_computed"] is True
    assert evidence["controlling_blocker"] == result["controlling_blocker"]
    assert evidence["soft_pole_scope_is_inherited_from_predecessor"] is True
    for flag in ("finite_q_complex_pole_computed", "controlled_truncation_error_established", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[flag] is False
        assert result[flag] is False
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_actual_finite_q_pole_successor_preserves_physical_and_prior_boundaries():
    field = "hartree_finite_q_poles_evidence_2026_10_02"
    review = PLAN["execution_review_2026_10_01"]
    successor = PLAN[review["current_scientific_evidence_field"]]
    assert successor["inherited_fixed_Phi_finite_q_poles_evidence_field"] == field
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text(encoding="utf-8"))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == result["verification_status"] == "PASS_SCOPED_FINITE_Q_POLES"
    assert evidence["closure_level"] == result["closure_level"] == "CLOSED_FOR_LANE"
    assert evidence["finite_q_complex_pole_computed"] is result["finite_q_complex_pole_computed"] is True
    assert evidence["controlling_blocker"] == result["controlling_blocker"]
    assert len(result["examples"]) == 2
    assert all(len(example["finite_q_runs"]) == 3 for example in result["examples"])
    assert all(result["checks"].values())
    for flag in ("controlled_truncation_error_established", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[flag] is False
        assert result[flag] is False
    assert PLAN[evidence["inherited_finite_q_density_evidence_field"]]["finite_q_complex_pole_computed"] is False
    assert PLAN[evidence["inherited_soft_poles_evidence_field"]]["finite_q_complex_pole_computed"] is False


def test_d05_portfolio_route_is_not_scientific_or_submission_acceptance():
    decision = PLAN["route_selection_2026_10_02"]
    strategy = PLAN["portfolio_strategy_2026_10_01"]
    assert decision["record_class"] == "PLANNING_NOT_SCIENTIFIC_CLOSURE"
    assert decision["status"] == strategy["status"] == "METHODS_ROUTE_SELECTED_FOR_PREPARATION"
    assert decision["decision_date"] == strategy["decision_dates"]["route_selection"]
    assert decision["selected_route"] == strategy["primary_portfolio_route"]
    # Preserve the historical decision basis rather than rewriting it with a later branch.
    assert decision["current_evidence_field"] == "hartree_finite_q_poles_evidence_2026_10_02"
    assert decision["current_evidence_field"] in strategy["accepted_preliminary_evidence_fields"]
    for flag in ("prediction_route_admitted", "novelty_established", "measurement_design_completed", "D05_scientific_milestone_accepted", "full_goal_accepted", "scientific_goal_completion_rule_changed", "physical_gate_changed", "core_composition_gate_overwritten", "submission_ready"):
        assert decision[flag] is False
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])
    assert {row["id"]: row for row in PLAN["milestones"]}["D05"]["status"] == "NOT_STARTED"
    assert PLAN["funder"] is PLAN["submission_deadline"] is PLAN["budget_amount"] is None


def test_joint_Phi_static_successor_cannot_inherit_fixed_Phi_dynamic_or_full_acceptance():
    field = "hartree_joint_phi_static_evidence_2026_10_02"
    current = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    assert current["inherited_joint_Phi_static_evidence_field"] == field
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text(encoding="utf-8"))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == result["verification_status"] == "PASS_SCOPED_JOINT_PHI_STATIC"
    assert evidence["controlling_blocker"] == result["controlling_blocker"]
    assert evidence["branch_id"] == result["branch_id"] != evidence["parent_branch_id"]
    assert evidence["homogeneous_classical_Phi_stationarity_derived"] is result["homogeneous_classical_Phi_stationarity_derived"] is True
    for flag in ("joint_finite_q_complex_pole_computed", "prior_fixed_Phi_poles_reused_as_joint",
                 "full_quantum_joint_Phi_stationarity_derived", "physical_Kubo_emitted",
                 "independent_alpha_Phi_K_admitted", "controlled_truncation_error_established",
                 "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[flag] is result[flag] is False
    assert all(result["checks"].values())
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_joint_classical_Phi_response_is_computed_not_full_material_acceptance():
    field = "hartree_joint_phi_response_evidence_2026_10_02"
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    assert latest["inherited_joint_Phi_response_evidence_field"] == field
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text(encoding="utf-8"))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == result["verification_status"] == "PASS_SCOPED_JOINT_PHI_RESPONSE"
    assert evidence["controlling_blocker"] == result["controlling_blocker"]
    assert evidence["joint_finite_q_complex_pole_computed"] is result["joint_finite_q_complex_pole_computed"] is True
    assert evidence["joint_classical_Phi_retarded_response_computed"] is result["joint_classical_Phi_retarded_response_computed"] is True
    assert len(result["examples"]) == 2 and all(len(e["finite_q_runs"]) == 3 for e in result["examples"])
    assert all(result["checks"].values())
    for flag in ("prior_fixed_Phi_poles_reused_as_joint", "full_frequency_joint_spectrum_classified",
                 "controlled_truncation_error_established", "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted",
                 "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[flag] is result[flag] is False
    assert PLAN[evidence["inherited_joint_Phi_static_evidence_field"]]["joint_finite_q_complex_pole_computed"] is False
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_low_T_boundary_blocks_admission_without_retracting_response_or_accepting_goal():
    field = "hartree_low_T_validity_evidence_2026_10_02"
    successor = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    assert successor["predecessor_validity_evidence_field"] == field
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text(encoding="utf-8"))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == result["verification_status"] == "PASS_SCOPED_LOW_T_EXCLUSION"
    assert evidence["controlling_blocker"] == result["controlling_blocker"]
    assert evidence["physical_low_T_EOS_admission"] == result["physical_low_T_EOS_admission"] == "BLOCKED_ASYMPTOTIC_SPECTRUM_THERMODYNAMICS_MISMATCH"
    assert evidence["conditional_asymptotic_exclusion_established"] is result["conditional_asymptotic_exclusion_established"] is True
    for flag in ("source_response_predecessor_invalidated", "global_UET_no_go", "phonon_free_energy_added", "mass_repair",
                 "controlled_truncation_error_established", "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted",
                 "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[flag] is result[flag] is False
    assert PLAN[evidence["inherited_joint_Phi_response_evidence_field"]]["joint_finite_q_complex_pole_computed"] is True
    assert all(result["checks"].values())
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_new_phase_eft_thermal_lane_is_not_Hartree_repair_or_full_acceptance():
    field = "low_T_phase_eft_evidence_2026_10_02"
    successor = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    assert successor["phase_eft_predecessor_evidence_field"] == field
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text(encoding="utf-8"))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == result["verification_status"] == "PASS_SCOPED_TREE_MATCHED_LOW_T_EFT"
    assert evidence["branch_id"] == result["branch_id"] != PLAN[evidence["predecessor_validity_evidence_field"]]["branch_id"]
    assert evidence["controlling_blocker"] == result["controlling_blocker"]
    assert all(result["checks"].values())
    assert (ROOT/evidence["measurement_card"]).is_file()
    assert not result["measurement_design"]["physical_precision_or_lab_feasibility_established"]
    for key in ("old_Hartree_branch_repaired", "controlled_full_action_truncation_error_established",
                "independent_alpha_Phi_K_admitted", "physical_Kubo_emitted", "g1_physical_unlock",
                "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[key] is result[key] is False
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_interaction_successor_narrows_controller_without_full_thermal_acceptance():
    field = "low_T_interaction_evidence_2026_10_02"
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    assert latest["interaction_predecessor_evidence_field"] == field
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    r = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == r["verification_status"] == "PASS_SCOPED_INTERACTION_KERNEL"
    assert evidence["controlling_blocker"] == r["controlling_blocker"]
    assert evidence["branch_id"] == r["branch_id"] == PLAN[evidence["phase_eft_predecessor_evidence_field"]]["branch_id"]
    assert all(r["checks"].values())
    for key in ("full_two_loop_pressure_computed", "quartic_TT_is_total_error_bound", "assigned_damping_width",
                "finite_T_collision_computed", "full_SK_KMS_matching_closed", "controlled_full_action_truncation_error_established",
                "independent_alpha_Phi_K_admitted", "physical_Kubo_emitted", "g1_physical_unlock", "g2_science_unlock",
                "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[key] is r[key] is False
    note = ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/T13_LOW_T_INTERACTIONS_2026-10-02.md"
    content = note.read_text()
    assert evidence["sha256"] in content
    assert all(k+":" in content for k in r["report"])
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_vacuum_cut_log_successor_is_not_full_matching_or_physical_acceptance():
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    field = latest["vacuum_predecessor_evidence_field"]
    assert field == "vacuum_cut_log_evidence_2026_10_03"
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    r = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert r["verification_status"] == evidence["verification_status"] == "PASS_SCOPED_VACUUM_CUT_LOG"
    assert r["controlling_blocker"] == evidence["controlling_blocker"]
    assert r["branch_id"] == evidence["branch_id"]
    assert r["real_nonlocal_linear_loop_computed"] and r["four_subtracted_reconstruction_checked"]
    assert r["local_matching_information"]["leading_on_shell_rank"] == 1
    assert not r["local_matching_information"]["four_lab_measurements_required_claimed"]
    note = ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/T13_VACUUM_CUT_LOG_2026-10-03.md"
    content = note.read_text()
    assert evidence["sha256"] in content
    assert all(name+":" in content for name in r["report"])
    for key in ("local_Wilson_matching_completed", "internal_curvature_real_self_energy_computed",
                "full_real_self_energy_matched", "full_two_loop_pressure_computed", "finite_T_collision_computed",
                "full_SK_KMS_matching_closed", "controlled_full_action_truncation_error_established",
                "independent_alpha_Phi_K_admitted", "physical_Kubo_emitted", "g1_physical_unlock",
                "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[key] is r[key] is False
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_thermal_cut_successor_does_not_accept_full_collision_matching_or_goal():
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    field = latest["thermal_predecessor_evidence_field"]
    assert field == "thermal_cut_stiffness_evidence_2026_10_03"
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    r = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == r["verification_status"] == "PASS_SCOPED_THERMAL_CUT_STIFFNESS"
    assert evidence["controlling_blocker"] == r["controlling_blocker"]
    assert evidence["branch_id"] == r["branch_id"]
    assert all(r["checks"].values())
    assert evidence["finite_T_pair_and_Landau_cuts_computed"] is r["finite_T_pair_and_Landau_cuts_computed"] is True
    assert evidence["static_LO_thermal_coherence_checked"] is r["static_LO_thermal_coherence_checked"] is True
    for key in ("full_finite_T_collision_operator_computed", "higher_derivative_vertices_and_residues_matched", "full_real_self_energy_matched", "full_two_loop_pressure_computed", "full_SK_KMS_matching_closed", "controlled_full_action_truncation_error_established", "independent_alpha_Phi_K_admitted", "physical_Kubo_emitted", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[key] is r[key] is False
    content = (ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/T13_THERMAL_CUT_STIFFNESS_2026-10-03.md").read_text()
    assert evidence["sha256"] in content
    assert all(name+":" in content for name in r["report"])
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_acoustic_modal_matching_is_three_legs_not_full_response_or_goal():
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    field = latest["acoustic_predecessor_evidence_field"]
    assert field == "acoustic_modal_cut_evidence_2026_10_03"
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert result["verification_status"] == evidence["verification_status"] == "PASS_SCOPED_ACOUSTIC_MODAL_CUT"
    assert result["controlling_blocker"] == evidence["controlling_blocker"]
    assert result["branch_id"] == evidence["branch_id"]
    assert result["acoustic_tree_residues_and_cubic_vertex_matched"] is evidence["acoustic_tree_residues_and_cubic_vertex_matched"] is True
    assert all(result["checks"].values())
    for key in ("all_parent_modes_and_quantum_Phi_loops_included", "full_off_shell_source_matching_closed",
                "full_real_self_energy_matched", "full_two_loop_pressure_computed", "full_finite_T_collision_operator_computed",
                "full_SK_KMS_matching_closed", "controlled_full_action_truncation_error_established",
                "independent_alpha_Phi_K_admitted", "physical_Kubo_emitted", "g1_physical_unlock",
                "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten"):
        assert result[key] is evidence[key] is False
    content = (ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/T13_ACOUSTIC_MODAL_CUTS_2026-10-03.md").read_text()
    assert evidence["sha256"] in content and all(name+":" in content for name in result["report"])
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_pair_source_interface_is_not_complete_retarded_or_physical_response():
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    field = latest["pair_predecessor_evidence_field"]
    assert field == "acoustic_source_pair_evidence_2026_10_03"
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == result["verification_status"] == "PASS_SCOPED_PAIR_SOURCE_INTERFACE"
    assert evidence["controlling_blocker"] == result["controlling_blocker"]
    assert all(result["checks"].values())
    for key in ("full_off_shell_source_matching_closed", "full_real_self_energy_matched", "full_two_loop_pressure_computed",
                "all_parent_modes_and_quantum_Phi_loops_included", "full_SK_KMS_matching_closed", "physical_Kubo_emitted",
                "independent_alpha_Phi_K_admitted", "full_core_unlock", "core_composition_gate_overwritten"):
        assert result[key] is evidence[key] is False
    content = (ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/T13_ACOUSTIC_SOURCE_PAIR_2026-10-03.md").read_text()
    assert evidence["sha256"] in content and all(name+":" in content for name in result["report"])
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_Landau_source_and_support_bounds_are_not_complete_physical_response():
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    field = latest["source_Landau_predecessor_evidence_field"]
    assert field == "acoustic_source_Landau_evidence_2026_10_03"
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == result["verification_status"] == "PASS_SCOPED_LANDAU_SOURCE_INTERFACE"
    assert evidence["controlling_blocker"] == result["controlling_blocker"]
    assert all(result["checks"].values()) and result["closure_level"] == evidence["closure_level"] == "CLOSED_FOR_LANE"
    for key in ("full_off_shell_source_matching_closed", "full_real_self_energy_matched", "full_two_loop_pressure_computed",
                "all_parent_modes_and_quantum_Phi_loops_included", "full_SK_KMS_matching_closed", "physical_Kubo_emitted",
                "independent_alpha_Phi_K_admitted", "controlled_full_action_truncation_error_established", "full_core_unlock", "core_composition_gate_overwritten"):
        assert result[key] is evidence[key] is False
    content = (ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/T13_ACOUSTIC_SOURCE_LANDAU_2026-10-03.md").read_text()
    assert evidence["sha256"] in content and all(name+":" in content for name in result["report"])
    assert result["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert not result["xie_2026_accessed"] and not result["claim_promotion"]
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_thermal_source_curvature_is_not_assigned_dynamic_contact_or_physics():
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    field = latest["source_curvature_predecessor_evidence_field"]
    assert field == "thermal_source_curvature_evidence_2026_10_03"
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == result["verification_status"] == "PASS_SCOPED_THERMAL_SOURCE_CURVATURE"
    assert evidence["controlling_blocker"] == result["controlling_blocker"]
    assert all(result["checks"].values()) and evidence["closure_level"] == result["closure_level"] == "CLOSED_FOR_LANE"
    for key in ("full_off_shell_source_matching_closed", "full_real_self_energy_matched", "dynamic_contact_fixed_from_static_residual",
                "full_two_loop_pressure_computed", "all_parent_modes_and_quantum_Phi_loops_included", "full_SK_KMS_matching_closed",
                "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted", "controlled_full_action_truncation_error_established",
                "full_core_unlock", "core_composition_gate_overwritten"):
        assert result[key] is evidence[key] is False
    content = (ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/T13_THERMAL_SOURCE_CURVATURE_2026-10-03.md").read_text()
    assert evidence["sha256"] in content and all(name+":" in content for name in result["report"])
    assert result["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED" and not result["xie_2026_accessed"]
    assert not result["claim_promotion"]
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_virtual_completion_is_named_and_does_not_unlock_physical_or_full_goal():
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    field = latest["virtual_source_predecessor_evidence_field"]
    assert field == "thermal_virtual_response_evidence_2026_10_03"
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == result["verification_status"] == "PASS_SCOPED_THERMAL_VIRTUAL_RESPONSE"
    assert evidence["controlling_blocker"] == result["controlling_blocker"]
    assert evidence["branch_id"] == result["branch_id"] != result["parent_branch_id"] == evidence["parent_branch_id"]
    assert all(result["checks"].values()) and evidence["closure_level"] == result["closure_level"] == "CLOSED_FOR_LANE"
    for key in ("static_virtual_contact_matching_closed_for_prescription", "q0_complex_dynamic_covariance_checked"):
        assert evidence[key] is result[key] is True
    for key in ("full_off_shell_source_matching_closed", "full_real_self_energy_matched", "dynamic_contact_fixed_from_static_residual",
                "all_parent_modes_and_quantum_Phi_loops_included", "full_two_loop_pressure_computed", "full_SK_KMS_matching_closed",
                "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted", "controlled_full_action_truncation_error_established",
                "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[key] is result[key] is False
    content = (ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/T13_THERMAL_VIRTUAL_RESPONSE_2026-10-03.md").read_text()
    assert evidence["sha256"] in content and all(name+":" in content for name in result["report"])
    assert not result["xie_2026_accessed"] and result["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_finite_q_static_population_is_not_assigned_collision_or_physical_transport():
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    field = latest["finite_q_source_predecessor_evidence_field"]
    assert field == "finite_q_thermal_source_evidence_2026_10_03"
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == result["verification_status"] == "PASS_SCOPED_FINITE_Q_THERMAL_SOURCE"
    assert evidence["controlling_blocker"] == result["controlling_blocker"]
    assert evidence["branch_id"] == result["branch_id"]
    assert all(result["checks"].values()) and evidence["closure_level"] == result["closure_level"] == "CLOSED_FOR_LANE"
    for key in ("static_population_limit_derived", "finite_q_source_checked_for_prescription"):
        assert evidence[key] is result[key] is True
    for key in ("full_loop_source_current_Ward_closed", "full_energy_exchange_ledger_closed", "assigned_relaxation_time", "full_collision_operator_computed",
                "full_off_shell_source_matching_closed", "full_real_self_energy_matched", "all_parent_modes_and_quantum_Phi_loops_included",
                "full_two_loop_pressure_computed", "full_SK_KMS_matching_closed", "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted",
                "controlled_full_action_truncation_error_established", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[key] is result[key] is False
    content = (ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/T13_FINITE_Q_THERMAL_SOURCE_2026-10-03.md").read_text()
    assert evidence["sha256"] in content and all(name+":" in content for name in result["report"])
    assert not result["xie_2026_accessed"] and result["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_noether_source_balance_is_first_order_gaussian_not_full_dissipation():
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    field = latest["noether_source_predecessor_evidence_field"]
    assert field == "thermal_noether_response_evidence_2026_10_03"
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert result["verification_status"] == evidence["verification_status"] == "PASS_SCOPED_GAUSSIAN_NOETHER_RESPONSE"
    assert result["branch_id"] == evidence["branch_id"]
    assert result["controlling_blocker"] == evidence["controlling_blocker"]
    assert all(result["checks"].values()) and result["closure_level"] == evidence["closure_level"] == "CLOSED_FOR_LANE"
    assert len(result["examples"]) == 48
    for key in ("gaussian_pair_local_charge_Ward_closed", "first_order_Gaussian_energy_balance_closed"):
        assert evidence[key] is result[key] is True
    for key in ("full_loop_source_current_Ward_closed", "full_energy_exchange_ledger_closed", "assigned_relaxation_time", "full_collision_operator_computed",
                "full_off_shell_source_matching_closed", "full_real_self_energy_matched", "all_parent_modes_and_quantum_Phi_loops_included",
                "full_two_loop_pressure_computed", "full_SK_KMS_matching_closed", "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted",
                "controlled_full_action_truncation_error_established", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[key] is result[key] is False
    content = (ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/T13_THERMAL_NOETHER_RESPONSE_2026-10-03.md").read_text()
    assert evidence["sha256"] in content and all(name+":" in content for name in result["report"])
    assert not result["xie_2026_accessed"] and result["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_collisionless_soft_ray_does_not_accept_physical_transport_or_full_goal():
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    field = latest["soft_source_predecessor_evidence_field"]
    assert field == "collisionless_soft_source_evidence_2026_10_03"
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert result["verification_status"] == evidence["verification_status"] == "PASS_SCOPED_COLLISIONLESS_SOFT_SOURCE"
    assert result["controlling_blocker"] == evidence["controlling_blocker"]
    assert result["branch_id"] == evidence["branch_id"]
    assert all(result["checks"].values()) and result["closure_level"] == evidence["closure_level"] == "CLOSED_FOR_LANE"
    for key in ("gaussian_collisionless_soft_ray_response_closed", "static_pressure_endpoint_checked_for_prescription"):
        assert evidence[key] is result[key] is True
    for key in ("full_loop_source_current_Ward_closed", "full_energy_exchange_ledger_closed", "assigned_relaxation_time", "full_collision_operator_computed",
                "full_off_shell_source_matching_closed", "full_real_self_energy_matched", "all_parent_modes_and_quantum_Phi_loops_included",
                "full_two_loop_pressure_computed", "full_SK_KMS_matching_closed", "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted",
                "controlled_full_action_truncation_error_established", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[key] is result[key] is False
    content = (ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/T13_COLLISIONLESS_SOFT_SOURCE_2026-10-03.md").read_text()
    assert evidence["sha256"] in content and all(name+":" in content for name in result["report"])
    assert result["numerical_repair"]["first_failure_preserved"] and result["numerical_repair"]["finite_truncated_tail_gate_still_fails"]
    assert not result["xie_2026_accessed"] and result["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_gaussian_work_identity_does_not_relabel_failed_grid_or_unlock_full_goal():
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    field = latest["source_work_predecessor_evidence_field"]
    assert field == "gaussian_source_work_evidence_2026_10_03"
    assert field in PLAN["portfolio_strategy_2026_10_01"]["observed_partial_evidence_fields"]
    assert field not in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text(encoding="utf-8"))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert evidence["verification_status"] == result["verification_status"] == "FAIL_SCOPED_GAUSSIAN_SOURCE_WORK"
    assert evidence["closure_level"] == result["closure_level"] == "PARTIAL"
    assert evidence["branch_id"] == result["branch_id"]
    assert evidence["controlling_blocker"] == result["controlling_blocker"]
    assert not all(result["checks"].values()) and all(result["extended_leading_checks"].values())
    for key in ("leading_work_identity_verified", "first_failure_is_not_relabelled_by_extended_checks", "full_rank_entropy_control_is_diagnostic_only"):
        assert evidence[key] is result[key] is True
    for key in ("leading_finite_pair_source_work_closed", "primary_covariance_entropy_defined", "full_energy_exchange_ledger_closed", "full_collision_operator_computed", "full_SK_KMS_matching_closed", "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[key] is result[key] is False
    assert all(x["closure_level"] == "CLOSED_FOR_LANE" for x in result["subresults"])
    content = (ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/T13_GAUSSIAN_SOURCE_WORK_2026-10-03.md").read_text()
    assert evidence["sha256"] in content and all(name+":" in content for name in result["report"])
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_even_work_remainder_does_not_accept_parent_error_or_physical_input():
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    field = latest["work_remainder_predecessor_evidence_field"]
    assert field == "gaussian_work_remainder_evidence_2026_10_03"
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert result["closure_level"] == evidence["closure_level"] == "CLOSED_FOR_LANE"
    assert result["verification_status"] == evidence["verification_status"] == "PASS_SCOPED_GAUSSIAN_WORK_REMAINDER"
    assert all(result["checks"].values())
    assert result["controlling_blocker"] == evidence["controlling_blocker"]
    assert result["branch_id"] == evidence["branch_id"]
    for key in ("finite_pair_even_work_hierarchy_verified", "formal_finite_pair_remainder_formula_derived"):
        assert evidence[key] is result[key] is True
    for key in ("old_source_work_audit_promoted", "useful_linear_certificate_on_original_grid", "numeric_bound_interval_certified",
                "nonlinear_parent_action_completed", "full_energy_exchange_ledger_closed", "full_collision_operator_computed",
                "full_SK_KMS_matching_closed", "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted",
                "controlled_full_action_truncation_error_established", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[key] is result[key] is False
    content = (ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/T13_GAUSSIAN_WORK_REMAINDER_2026-10-03.md").read_text()
    assert evidence["sha256"] in content and all(name+":" in content for name in result["report"])
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_density_readout_closure_does_not_admit_physical_measurement_or_full_goal():
    latest = PLAN[PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]]
    field = latest["density_readout_predecessor_evidence_field"]
    assert field == "noether_density_readout_evidence_2026_10_03"
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    assert result["closure_level"] == evidence["closure_level"] == "CLOSED_FOR_LANE"
    assert result["verification_status"] == evidence["verification_status"] == "PASS_SCOPED_NOETHER_DENSITY_READOUT"
    assert result["branch_id"] == evidence["branch_id"]
    assert result["controlling_blocker"] == evidence["controlling_blocker"]
    assert all(result["checks"].values())
    for key in ("tree_Noether_density_readout_verified", "restricted_gain_density_map_ambiguity_verified", "conditional_dispersion_unit_scale_information_verified"):
        assert evidence[key] is result[key] is True
    for key in ("physical_Noether_to_atomic_density_map_admitted", "physical_measurement_protocol_admitted",
                "physical_resolution_or_intrinsic_damping_admitted", "full_measurement_design_completed",
                "independent_alpha_Phi_K_admitted", "physical_Kubo_emitted", "full_SK_KMS_matching_closed",
                "nonlinear_parent_action_completed", "controlled_full_action_truncation_error_established",
                "old_source_work_audit_promoted", "full_core_unlock", "core_composition_gate_overwritten"):
        assert evidence[key] is result[key] is False
    for note in ("T13_NOETHER_DENSITY_READOUT_2026-10-03.md", "T13_DENSITY_SPECTROSCOPY_MEASUREMENT_CARD_2026-10-03.md"):
        content = (ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts"/note).read_text()
        assert evidence["sha256"] in content and all(name+":" in content for name in result["report"])
    assert result["external_numeric_rows_admitted"] == 0
    assert not result["xie_2026_accessed"] and result["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert not result["claim_promotion"] and not result["parameter_fitting"]
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])


def test_q5_information_does_not_admit_physical_precision_or_full_goal():
    field = PLAN["execution_review_2026_10_01"]["current_scientific_evidence_field"]
    assert field == "q5_dispersion_information_evidence_2026_10_03"
    assert field in PLAN["portfolio_strategy_2026_10_01"]["accepted_preliminary_evidence_fields"]
    evidence = PLAN[field]
    path = ROOT/evidence["path"]
    result = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
    for key in ("closure_level", "verification_status", "controlling_blocker", "branch_id"):
        assert evidence[key] == result[key]
    assert result["closure_level"] == "CLOSED_FOR_LANE" and all(result["checks"].values())
    assert result["verification_status"] == "PASS_SCOPED_Q5_INFORMATION"
    for key in ("q5_tree_coefficient_verified", "restricted_unit_free_inverse_verified", "exact_rational_tree_witness_envelope_verified"):
        assert evidence[key] is result[key] is True
    for key in ("physical_q5_measured", "physical_measurement_design_completed", "physical_material_map_admitted",
                "independent_alpha_Phi_K_admitted", "full_SK_KMS_matching_closed", "physical_Kubo_emitted",
                "nonlinear_parent_action_completed", "controlled_full_action_truncation_error_established",
                "full_core_unlock", "core_composition_gate_overwritten", "old_source_work_audit_promoted"):
        assert evidence[key] is result[key] is False
    for note in ("T13_Q5_DISPERSION_INFORMATION_2026-10-03.md", "T13_Q5_MEASUREMENT_INFORMATION_CARD_2026-10-03.md"):
        text = (ROOT/"docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts"/note).read_text()
        assert evidence["sha256"] in text and all(name+":" in text for name in result["report"])
    assert not result["xie_2026_accessed"] and result["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert result["external_numeric_rows_admitted"] == 0 and not result["claim_promotion"]
    assert all(card["status"] == "PLANNED_NOT_ACCEPTED" for card in PLAN["result_level_execution_2026_10_01"]["result_cards"])
