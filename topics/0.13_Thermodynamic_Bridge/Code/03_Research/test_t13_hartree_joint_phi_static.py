"""Counterterm, actual joint-state, reciprocal-source and boundary tests."""

import ast
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
M = runpy.run_path(str(HERE/"Research_T13_Hartree_Joint_Phi_Static.py"))


def artifact():
    return json.loads(M["OUTPUT"].read_text(encoding="utf-8"))


def test_action_inputs_are_the_original_declared_trial_controls():
    c = M["action_controls"]()
    assert c == pytest.approx({"Z": 1., "m0_sq": 1., "u": 1., "gamma": .04,
                              "epsilon": .05, "Phi_reference": 0., "response_mass_sq": 1., "response_quartic": 1.})
    assert M["mass_sq"](.15, c) == pytest.approx(.994)


def test_reciprocal_Phi_mass_slope_and_response_derivatives():
    c, phi, h = M["action_controls"](), .15, 1e-4
    slope = (M["mass_sq"](phi+h, c)-M["mass_sq"](phi-h, c))/(2*h)
    force = (M["response_potential"](phi+h, c)-M["response_potential"](phi-h, c))/(2*h)
    curvature = (M["response_force"](phi+h, c)-M["response_force"](phi-h, c))/(2*h)
    assert slope == pytest.approx(-c["gamma"], abs=1e-12)
    assert force == pytest.approx(M["response_force"](phi, c), abs=1e-9)
    assert curvature == pytest.approx(M["response_curvature"](phi, c), abs=1e-9)


def test_exact_rational_normalization_derivatives_are_not_frozen_constants():
    u, D, D2, m0, ref, gamma, phi = Q(4, 5), Q(3, 100), Q(11, 100), Q(13, 10), Q(7, 10), Q(1, 25), Q(3, 20)
    A, B = u/((1+2*u*D)*(1+4*u*D)), u/(1+2*u*D)
    def normalization(x):
        delta = m0-gamma*x-ref
        return delta*D2+delta*delta*D/2-(A+B)*(D2+delta*D)**2
    def bare_mass(x):
        mass = m0-gamma*x
        return mass-2*(A+B)*(D2+(mass-ref)*D)
    h = Q(1, 1000)
    force = (normalization(phi+h)-normalization(phi-h))/(2*h)
    curvature = (normalization(phi+h)+normalization(phi-h)-2*normalization(phi))/h**2
    slope = (bare_mass(phi+h)-bare_mass(phi-h))/(2*h)
    assert force == -gamma*(D2+(m0-gamma*phi-ref)*D)/(1+4*u*D)
    assert curvature == gamma*gamma*D/(1+4*u*D)
    assert slope == -gamma/(1+4*u*D)
    assert force != 0 and curvature != 0


def test_counterterm_force_identity_holds_for_arbitrary_signed_tadpoles():
    c = M["action_controls"]()
    for s, f1, f2 in M["CT"]["STATE_PROBES"]:
        for D in M["CT"]["D_PROBES"]:
            row = M["force_match"](.15, s, (f1, f2), .85, c, D, .11)
            assert abs(row["force_match_residual"]) < 1e-12
            assert abs(row["potential_match_residual"]) < 1e-12
            assert row["uncorrected_force_difference"] == pytest.approx(row["normalization_force"], abs=1e-12)


def test_bare_mass_and_response_terms_are_a_coupled_counterterm_contract():
    c, phi, D, D2 = M["action_controls"](), .15, .03, .11
    jet = M["normalization_jet"](phi, c, D, D2)
    assert jet["bare_mass_slope"] != pytest.approx(-c["gamma"])
    assert jet["bare_response_force"]+jet["normalization_force"] == pytest.approx(M["response_force"](phi, c))
    assert jet["bare_response_curvature"]+jet["normalization_curvature"] == pytest.approx(M["response_curvature"](phi, c))


def test_normalization_unit_rescaling_is_algebra_not_loop_RG():
    c, factor = M["action_controls"](), 1.7
    scaled = c | {"m0_sq": c["m0_sq"]*factor**2, "gamma": c["gamma"]*factor,
                  "Phi_reference": c["Phi_reference"]*factor, "response_mass_sq": c["response_mass_sq"]*factor**2}
    base = M["normalization_jet"](.15, c, .03, .11, reference_logdet=.17)
    actual = M["normalization_jet"](.15*factor, scaled, .03, .11*factor**2, factor**2, .17*factor**4)
    for field, power in (("normalization", 4), ("normalization_force", 3), ("normalization_curvature", 2), ("bare_mass_slope", 1), ("bare_response_force", 3), ("bare_response_curvature", 2)):
        assert actual[field] == pytest.approx(base[field]*factor**power, rel=1e-12)


def test_zero_response_coupling_has_no_mass_or_normalization_force():
    c = M["action_controls"]() | {"gamma": 0.}
    jet = M["normalization_jet"](.15, c, .03, .11)
    assert M["mass_sq"](.15, c) == c["m0_sq"]
    assert jet["normalization_force"] == jet["normalization_curvature"] == jet["bare_mass_slope"] == 0
    row = M["force_match"](.15, .2, (.01, -.02), .85, c, .03, .11)
    assert row["finite_force"] == pytest.approx(M["response_force"](.15, c))


def test_projection_poles_invalid_controls_and_noncondensed_chart_are_rejected():
    c = M["action_controls"]()
    for bad in (c | {"u": 0.}, c | {"epsilon": 0.}, c | {"gamma": -1.}, c | {"m0_sq": np.nan}):
        with pytest.raises(ValueError):
            M["mass_sq"](.15, bad)
    with pytest.raises(ValueError):
        M["mass_sq"](np.nan, c)
    for D in (-.25, -.5):
        with pytest.raises(ValueError):
            M["normalization_jet"](.15, c, D, .11)
    with pytest.raises(ValueError):
        M["joint_residual"](.1, .2, .01, .15, .22, .8, c)


def test_joint_state_is_solved_not_the_old_fixed_Phi_anchor():
    record = artifact()
    c = record["action_controls"]
    assert len(record["examples"]) == 2
    for e in record["examples"]:
        state = e["joint_state"]
        residual = M["joint_residual"](state["s"], state["a"], state["b"], state["Phi"], e["T"], e["mu"], c)
        assert np.max(abs(residual)) < M["ROOT_TOLERANCE"]
        assert state["scaled_residual_max"] < M["ROOT_TOLERANCE"]
        assert state["residual_scale_units"] == ["E^2", "E^2", "E^2", "E^3"]
        assert state["residual_scales"][-1] == pytest.approx(c["epsilon"]*M["MS_SCALE"]**3)
        assert abs(state["Phi"]-e["prior_fixed_Phi"]) > 1e-4
        assert abs(e["prior_fixed_Phi_joint_force"]) > 1e-4
        assert state["mass_sq"] == pytest.approx(M["mass_sq"](state["Phi"], c))
        assert state["b"] > 0


def test_joint_states_refine_and_seeds_do_not_become_parameter_fits():
    for e in artifact()["examples"]:
        assert len(e["quadrature_runs"]) == len(M["ORDERS"])
        assert e["maximum_last_state_refinement"] < M["REFINEMENT_TOLERANCE"]
        assert e["maximum_seed_disagreement"] < M["REFINEMENT_TOLERANCE"]
        assert all(state["scaled_residual_max"] < M["ROOT_TOLERANCE"] for state in e["quadrature_runs"])


def test_actual_mixed_source_loop_Hessian_and_static_Ward_agree():
    for e in artifact()["examples"]:
        covariance = e["static_covariance_hessian"]
        assert covariance["reciprocity_residual"] < M["IDENTITY_TOLERANCE"]
        assert covariance["covariance_min_singular_value"] > .01
        assert [row["radial_order"] for row in e["independent_source_loop_hessian"]] == list(M["LOOP_ORDERS"])
        loop = e["independent_source_loop_hessian"][-1]
        assert loop["maximum_hessian_disagreement"] < M["HESSIAN_TOLERANCE"]
        assert abs(loop["phase_Ward_inverse"]) < M["HESSIAN_TOLERANCE"]
        assert loop["imaginary_residual"] < 1e-10
        assert loop["covariance_min_singular_value"] > .01


def test_reoptimized_potential_matches_both_diagonal_and_mixed_Hessian():
    for e in artifact()["examples"]:
        assert [row["Phi_step"] for row in e["reoptimized_potential_Hessian"]] == list(M["PHI_STEPS"])
        last = e["reoptimized_potential_Hessian"][-1]
        assert last["maximum_absolute_disagreement"] < M["HESSIAN_TOLERANCE"]
        assert np.asarray(last["matrix"])[0, 1] != 0


def test_relaxed_Phi_curvature_includes_radial_backreaction():
    for e in artifact()["examples"]:
        hessian = np.asarray(e["static_covariance_hessian"]["matrix"])
        expected = hessian[1, 1]-hessian[1, 0]*hessian[0, 1]/hessian[0, 0]
        assert e["static_covariance_hessian"]["radial_relaxed_Phi_curvature"] == pytest.approx(expected, abs=1e-12)
        assert abs(expected-hessian[1, 1]) > 1e-4
        assert e["radial_relaxed_Phi_force_derivative"][-1]["absolute_disagreement"] < M["HESSIAN_TOLERANCE"]
        assert min(e["static_covariance_hessian"]["eigenvalues"]) > 0


def test_formal_counterterm_replay_preserves_joint_force_without_adjustment():
    for e in artifact()["examples"]:
        for row in e["formal_counterterm_replay_at_joint_state"]:
            assert abs(row["force_match_residual"]) < M["IDENTITY_TOLERANCE"]
            assert abs(row["finite_force"]) < M["ROOT_TOLERANCE"]


def test_new_named_static_branch_does_not_inherit_old_dynamic_poles():
    record = artifact()
    prior = json.loads((M["ROOT"]/M["POLES"]).read_text(encoding="utf-8"))
    assert record["parent_branch_id"] == prior["branch_id"]
    assert record["branch_id"] != prior["branch_id"]
    assert prior["finite_q_complex_pole_computed"] is True
    assert record["joint_finite_q_complex_pole_computed"] is False
    assert record["prior_fixed_Phi_poles_reused_as_joint"] is False
    assert prior["joint_Phi_stationarity_derived"] is False


def test_static_result_cannot_close_full_quantum_Phi_or_material_transport():
    record = artifact()
    assert record["homogeneous_classical_Phi_stationarity_derived"] is True
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert record["verification_status"] == "PASS_SCOPED_JOINT_PHI_STATIC"
    assert all(record["checks"].values())
    assert len(record["report"]) == 11
    assert record["thresholds"]["causal_leakage_unchanged"] == 1e-6
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    for flag in ("full_quantum_joint_Phi_stationarity_derived", "joint_finite_q_complex_pole_computed", "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted", "controlled_truncation_error_established", "global_phase_minimum_proved", "full_covariant_counterterm_match", "RG_invariance_established", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting", "target_source_accessed", "xie_2026_accessed", "clipping", "IR_filter", "mass_repair", "C_relabelled_as_charge_or_mass", "R_gen_added_as_state"):
        assert record[flag] is False
    assert "R_gen" in record["excluded_variables"] and "R_obs" in record["excluded_variables"]


def test_evidence_source_and_protected_core_hashes_are_current():
    record = artifact()
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((M["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_audit_reads_only_derived_predecessors_not_empirical_holdout():
    code = Path(__file__).with_name("Research_T13_Hartree_Joint_Phi_Static.py").read_text(encoding="utf-8")
    reads = [node for node in ast.walk(ast.parse(code)) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "read_text"]
    assert len(reads) == 1
    assert ast.unparse(reads[0].func.value) == "ROOT / path"
    assert all("/Result/artifacts/" in M[key] for key in ("BACKGROUND", "COUNTERTERM", "POLES"))
    assert "Landauer" not in code
