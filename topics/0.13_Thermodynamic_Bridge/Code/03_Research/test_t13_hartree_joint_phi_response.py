"""Independent action, counterterm, joint-response and claim-boundary checks."""

import ast
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

M = runpy.run_path(str(Path(__file__).with_name("Research_T13_Hartree_Joint_Phi_Response.py")))


def previous():
    return json.loads((M["ROOT"]/M["STATIC_ARTIFACT"]).read_text(encoding="utf-8"))


def artifact():
    return json.loads(M["OUTPUT"].read_text(encoding="utf-8"))


def formal_inputs():
    e = M["example_from_static"](previous()["examples"][0])
    bubble = np.array([[-.04, .003+.002j, .001], [.003-.001j, -.03, .002j],
                       [.001, -.002j, -.05]], complex)
    mixed = np.arange(12).reshape(3, 4)*(.003+.001j)
    return e, M["controls"](), {"bubble": bubble, "mixed": mixed,
                                "reverse": mixed.T.conj(), "loop_current": np.eye(4)*.01}


def test_kinetic_and_reciprocal_coupling_use_the_original_action():
    action = M["controls"]()
    assert action["response_kinetic"] == M["S"]["natural_bridge_config"]().eos.response.response_kinetic == 1.
    assert action["epsilon"] == .05
    assert action["gamma"] == pytest.approx(.04)
    e, _, _ = formal_inputs()
    q, z = .04, .012-.0002j
    tree = M["joint_tree"](q, z, e, action)
    assert tree[2, 2] == pytest.approx(action["epsilon"]*action["response_kinetic"]*(q*q-z*z)+M["S"]["response_curvature"](e["Phi"], action))
    assert tree[0, 2] == tree[2, 0] == pytest.approx(-action["gamma"]*np.sqrt(e["s"]))
    assert tree[1, 2] == tree[2, 1] == 0


def test_independent_parent_lagrangian_finite_differences_fix_kinetic_signs():
    from docs.core.uet_covariant_response import conservative_action_density
    cfg = M["S"]["natural_bridge_config"]().eos.response
    phi, h = .15, 1e-4
    metric = np.diag([-1., 1., 1., 1.])
    def lagrangian(gradient, response=phi):
        return conservative_action_density(metric, metric, 0., gradient, response, 0., cfg)
    center = lagrangian(np.zeros(4))
    for axis, sign in ((0, 1), (1, -1)):
        gradient = np.eye(4)[axis]*h
        value = (lagrangian(gradient)+lagrangian(-gradient)-2*center)/h**2
        assert value == pytest.approx(sign*cfg.epsilon_nc*cfg.response_kinetic, abs=1e-9)
    potential_curvature = -(lagrangian(np.zeros(4), phi+h)+lagrangian(np.zeros(4), phi-h)-2*center)/h**2
    assert potential_curvature == pytest.approx(M["S"]["response_curvature"](phi, M["controls"]()), abs=1e-8)


def test_noncommuting_complex_covariance_counterterms_cancel_in_all_sources():
    e, action, loops = formal_inputs()
    _, kernel, _ = M["joint_vertices"](e["s"], action)
    assert np.max(abs(kernel@loops["bubble"]-loops["bubble"]@kernel)) > 1e-3
    for divergence in M["S"]["CT"]["D_PROBES"]:
        errors = M["counterterm_response"](.04, .012-.0002j, e, action, loops, divergence)
        assert max(errors.values()) < 1e-12


def test_dynamic_contact_identity_matches_independent_normalization_derivatives():
    e, action, _ = formal_inputs()
    _, kernel, vertices = M["joint_vertices"](e["s"], action)
    for divergence in (.03, .1):
        contact = .5*divergence*vertices.T@np.linalg.solve(np.eye(3)+divergence*kernel, vertices)
        jet = M["S"]["normalization_jet"](e["Phi"], action, divergence, .11)
        assert contact[2, 2] == pytest.approx(jet["normalization_curvature"], abs=1e-14)
        assert -action["gamma"]*np.sqrt(e["s"])-contact[0, 2] == pytest.approx(jet["bare_mass_slope"]*np.sqrt(e["s"]), abs=1e-14)
        assert contact[1, 2] == 0


def test_freezing_Phi_counterterms_is_a_detectable_negative_control():
    e, action, loops = formal_inputs()
    correct = M["counterterm_response"](.04, .012-.0002j, e, action, loops, .03)
    wrong = M["counterterm_response"](.04, .012-.0002j, e, action, loops, .03, freeze_Phi=True)
    assert max(correct.values()) < 1e-12
    assert wrong["field"] > 1e-5


def test_zero_reciprocal_coupling_decouples_Phi_without_adding_a_state():
    e, action, loops = formal_inputs()
    action = action | {"gamma": 0.}
    actual = M["assemble"](.04, .012+.001j, e, action, loops)
    assert np.max(abs(actual["field"][2, :2])) == np.max(abs(actual["field"][:2, 2])) == 0
    assert np.max(abs(actual["forward"][2])) == np.max(abs(actual["reverse"][:, 2])) == 0
    assert actual["field"][2, 2] == M["joint_tree"](.04, .012+.001j, e, action)[2, 2]


def test_formal_block_units_rescale_without_claiming_loop_RG():
    e, action, loops = formal_inputs()
    factor = 1.7
    scaled = e | {key: e[key]*factor**power for key, power in (("T", 1), ("mu", 1), ("Phi", 1), ("s", 2), ("a", 2), ("b", 2))}
    cfg = action | {"m0_sq": action["m0_sq"]*factor**2, "gamma": action["gamma"]*factor,
                    "Phi_reference": action["Phi_reference"]*factor, "response_mass_sq": action["response_mass_sq"]*factor**2}
    lp = loops | {"mixed": loops["mixed"]*factor, "reverse": loops["reverse"]*factor,
                  "loop_current": loops["loop_current"]*factor**2}
    base = M["assemble"](.04, .012+.001j, e, action, loops)
    actual = M["assemble"](.04*factor, (.012+.001j)*factor, scaled, cfg, lp)
    for name in ("field", "forward", "reverse", "aa", "relaxed_current"):
        assert np.max(abs(actual[name]-base[name]*factor**2)) < 1e-12
    assert actual["phase_coefficient"] == pytest.approx(base["phase_coefficient"], abs=1e-11)


def test_invalid_tree_inputs_and_old_upper_only_validator_are_not_weakened():
    e, action, loops = formal_inputs()
    with pytest.raises(ValueError):
        M["joint_tree"](.04, np.nan, e, action)
    with pytest.raises(ValueError):
        M["joint_tree"](-.04, .012j, e, action)
    with pytest.raises(ValueError):
        M["joint_tree"](.04, .012j, e, action | {"response_kinetic": 0.})
    with pytest.raises(ValueError):
        M["assemble"](.04, .012j, e, action, loops | {"bubble": np.ones((2, 2))})
    with pytest.raises(ValueError):
        M["F"]["validate"](e["T"], e["mu"], e["a"], e["b"], .04, .012-.0002j)
    assert np.all(np.isfinite(M["joint_tree"](.04, .012-.0002j, e, action)))


def test_even_block_elimination_matches_independent_full_determinant():
    e, action, loops = formal_inputs()
    actual = M["assemble"](.04, .012+.001j, e, action, loops)
    independent = np.linalg.det(actual["field"])/actual["even_determinant"]
    assert actual["phase_inverse"] == pytest.approx(independent, abs=1e-12)
    assert actual["even_min_singular_value"] > .01


def test_new_response_uses_the_actual_joint_states_not_old_fixed_Phi_parameters():
    record = artifact()
    prior = previous()
    assert record["branch_id"] == prior["branch_id"]
    for e, p in zip(record["examples"], prior["examples"], strict=True):
        for name in ("s", "a", "b", "Phi"):
            assert e[name] == p["joint_state"][name]
        assert e["Phi"] != p["prior_fixed_Phi"]
    assert record["prior_fixed_Phi_poles_reused_as_joint"] is False
    assert prior["joint_finite_q_complex_pole_computed"] is False


def test_six_new_local_joint_poles_have_nonzero_arrival_frequency_and_residuals():
    record = artifact()
    assert len(record["examples"]) == 2
    for e in record["examples"]:
        assert [q["q"] for q in e["finite_q_runs"]] == list(M["Q_GRID"])
        for q in e["finite_q_runs"]:
            v = M["G"]["unpack"](q["pole_runs"][-1]["velocity_pole"])
            z = M["G"]["unpack"](q["pole_runs"][-1]["frequency_pole"])
            assert .19 < v.real < .45 and -.015 < v.imag < 0
            assert z == pytest.approx(q["q"]*v) and z != 0
            for run in q["pole_runs"]:
                assert run["inverse_residual"] < M["ROOT_TOLERANCE"]
                assert run["uneliminated_scaled_determinant_residual"] < M["ROOT_TOLERANCE"]


def test_orders_seeds_grids_and_tail_paths_agree_without_old_answers():
    for e in artifact()["examples"]:
        for q in e["finite_q_runs"]:
            assert len(q["pole_runs"]) == len(M["ORDERS"])
            assert q["pole_refinements"][-1] < M["REFINEMENT_TOLERANCE"]
            assert q["second_seed_disagreement"] < M["REFINEMENT_TOLERANCE"]
            assert q["alternate_grid_disagreement"] < M["REFINEMENT_TOLERANCE"]
            assert q["alternate_tail_inverse_residual"] < M["ROOT_TOLERANCE"]
            assert q["wrong_principal_sheet_residual"] > 1e-4


def test_actual_upper_bubble_and_joint_field_have_an_independent_subtraction_check():
    for e in artifact()["examples"]:
        for q in e["finite_q_runs"]:
            assert q["independent_upper_bubble_disagreement"] < M["REFINEMENT_TOLERANCE"]
            assert q["independent_upper_joint_field_disagreement"] < M["REFINEMENT_TOLERANCE"]


def test_neutral_Phi_Ward_and_nonzero_elimination_factors():
    for e in artifact()["examples"]:
        for q in e["finite_q_runs"]:
            for run in q["pole_runs"]:
                assert run["phase_current_Ward_disagreement"] < M["WARD_TOLERANCE"]
                assert run["even_min_singular_value"] > .01
                assert run["covariance_min_singular_value"] > .01


def test_local_derivatives_are_simple_and_analytic_not_a_global_zero_count():
    for e in artifact()["examples"]:
        for q in e["finite_q_runs"]:
            check = q["local_derivative_check"]
            assert check["derivative_modulus"] > .01
            assert check["runs"][-1]["Cauchy_Riemann_disagreement"] < 2e-5


def test_dynamic_counterterm_identity_holds_on_actual_computed_loops():
    for e in artifact()["examples"]:
        for q in e["finite_q_runs"]:
            for ct in q["counterterm_checks"]:
                assert max(ct[name] for name in ("field", "forward", "reverse", "aa")) < M["IDENTITY_TOLERANCE"]
            assert q["frozen_Phi_counterterm_negative_control"]["field"] > 1e-5


def test_clamped_Phi_answer_is_not_reused_as_a_joint_pole():
    for e in artifact()["examples"]:
        for q in e["finite_q_runs"]:
            assert abs(M["G"]["unpack"](q["clamped_Phi_inverse_at_joint_pole"])) > 1e-5


def test_joint_static_charge_response_matches_full_reoptimized_potential():
    for e in artifact()["examples"]:
        row = e["static_response"]
        assert row["static_Hessian_disagreement"] < M["REFINEMENT_TOLERANCE"]
        assert row["phase_Ward_inverse"] < M["REFINEMENT_TOLERANCE"]
        assert row["charge_imaginary_residual"] < 1e-10
        assert row["envelope_checks"][-1]["relative_disagreement"] < M["REFINEMENT_TOLERANCE"]
        assert abs(row["joint_charge_susceptibility"]-row["clamped_Phi_charge_susceptibility"]) > 1e-5


def test_read_path_does_not_import_old_poles_as_answers_or_read_empirical_sources():
    code = Path(__file__).with_name("Research_T13_Hartree_Joint_Phi_Response.py").read_text(encoding="utf-8")
    reads = [node for node in ast.walk(ast.parse(code)) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "read_text"]
    assert len(reads) == 1
    assert ast.unparse(reads[0].func.value) == "ROOT / STATIC_ARTIFACT"
    assert "/Result/artifacts/" in M["STATIC_ARTIFACT"]
    assert M["SEEDS"] == (.2-.01j, .4-.005j)
    assert "Landauer" not in code


def test_artifact_source_and_protected_core_hashes_are_current():
    record = artifact()
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((M["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_scoped_joint_response_does_not_close_quantum_material_or_full_topic():
    record = artifact()
    assert record["verification_status"] == "PASS_SCOPED_JOINT_PHI_RESPONSE"
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert all(record["checks"].values())
    assert record["joint_finite_q_complex_pole_computed"] is record["joint_classical_Phi_retarded_response_computed"] is True
    assert len(record["report"]) == 11
    for name in ("full_quantum_joint_Phi_stationarity_derived", "full_frequency_joint_spectrum_classified",
                 "global_phase_minimum_proved", "controlled_truncation_error_established", "full_covariant_counterterm_match",
                 "RG_invariance_established", "physical_Kubo_emitted", "collision_rate_emitted", "independent_alpha_Phi_K_admitted",
                 "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion",
                 "parameter_fitting", "assigned_width", "mass_repair", "clipping", "IR_filter", "target_source_accessed", "xie_2026_accessed",
                 "C_relabelled_as_charge_or_mass", "R_gen_added_as_state"):
        assert record[name] is False
    assert record["thresholds"]["causal_leakage_unchanged"] == 1e-6
    assert record["excluded_variables"] == ["R_gen", "R_obs", "nondynamical_A"]
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
