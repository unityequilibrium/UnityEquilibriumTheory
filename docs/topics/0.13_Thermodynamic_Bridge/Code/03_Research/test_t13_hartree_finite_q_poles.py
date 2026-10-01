"""Actual finite-q poles, independent moment algebra and bounded claims."""

import ast
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

N = runpy.run_path(str(Path(__file__).with_name("Research_T13_Hartree_Finite_Q_Poles.py")))


def artifact():
    return json.loads(N["OUTPUT"].read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def example():
    return json.loads((N["ROOT"]/N["PREVIOUS_ARTIFACT"]).read_text(encoding="utf-8"))["examples"][0]


@pytest.fixture(scope="module")
def kernel(example):
    return N["FiniteQKernel"](example, .04, 64, 24)


def test_analytic_extended_shell_recovers_previous_formula(example):
    for mode, ell in ((2, .06-.001j), (1, -.06-.001j), (3, 2.3-.001j), (0, -2.3-.001j)):
        actual = N["inverse_shell"](ell, mode, example["mu"], example["a"], example["b"])
        previous = N["D"]["complex_inverse_shell"](ell, mode, example)
        for first, second in zip(actual, previous):
            assert first == pytest.approx(second, abs=1e-11)


def test_occupation_difference_retains_vacuum_halves_and_complex_thermal_tail(example):
    for incoming, outgoing, p, ell in ((2, 2, .06, .07-.001j), (1, 1, -.06, -.05-.001j), (2, 1, .06, -.05-.001j)):
        expected = N["D"]["signed_occupation"](p, incoming, example["T"])-N["D"]["signed_occupation"](ell, outgoing, example["T"])
        actual = N["occupation_difference"](p, ell, incoming, outgoing, example["T"])
        assert actual == pytest.approx(expected, abs=1e-12)
    tiny = N["occupation_difference"](10., 10.01-.0001j, 2, 2, example["T"])
    assert abs(tiny) > 0
    assert N["occupation_difference"](.06, -.05, 2, 1, 0.) == 1
    assert N["occupation_difference"](.06, .07, 2, 2, 0.) == 0


def test_frequency_polynomial_is_original_source_numerator(example):
    k, q, p, z = .4, .04, .07, .012+.003j
    rp = np.eye(2, dtype=complex)
    ell = np.array([.06, .08])
    poly, transverse = N["joint_polynomial"](k, q, p, rp, ell, 2, 2, example["T"], example["mu"], example["a"], example["b"])
    actual = N["evaluate_polynomial"](poly, z)
    original, tr = N["R"]["shell_coefficient"](k, q, p, rp, ell, 2, z, example["T"], example["mu"], example["a"], example["b"])
    assert actual == pytest.approx(original, abs=1e-9)
    assert transverse == pytest.approx(tr, abs=1e-9)


def test_complex_cauchy_subtraction_matches_unsplit_frequency_moments_in_both_half_planes(example):
    angular = N["AngularKernel"]([.3], .04, example["T"], example["mu"], example["a"], example["b"], 48)
    for z in (.012+.004j, .012-.004j):
        joint, transverse = angular.evaluate(z)
        actual = N["R"]["unpack_joint"](joint[0], transverse[0])
        direct = N["direct_angular_moments"](.3, .04, z, example)
        for first, second in zip(actual, direct):
            assert first == pytest.approx(second, abs=1e-9)


def test_independent_frequency_moments_recover_old_upper_only_point_method(example):
    k, q, z = .3, .04, .012+.004j
    c, w = np.polynomial.legendre.leggauss(256)
    shifted = np.sqrt(k*k+q*q+2*k*q*c)
    midpoint = k*c+q/2
    bubble = N["F"]["point_bubble"](k, shifted, example["T"], example["mu"], example["a"], example["b"], z)
    mixed, reverse, current = N["G"]["point_gauge"](k, shifted, midpoint, example["T"], example["mu"], example["a"], example["b"], z)
    transverse = N["G"]["point_transverse"](k, shifted, k*k*(1-c*c), example["T"], example["mu"], example["a"], example["b"], z)
    actual = N["direct_angular_moments"](k, q, z, example)
    assert actual[0] == pytest.approx(np.sum(w[:, None, None]*bubble, axis=0), abs=1e-10)
    assert actual[1][:, :2] == pytest.approx(np.sum(w[:, None, None]*mixed, axis=0), abs=1e-10)
    assert actual[2][:2, :] == pytest.approx(np.sum(w[:, None, None]*reverse, axis=0), abs=1e-10)
    assert actual[3][:2, :2] == pytest.approx(np.sum(w[:, None, None]*current, axis=0), abs=1e-10)
    assert actual[3][2, 2] == pytest.approx(np.sum(w*transverse), abs=1e-10)


def test_source_time_signature_not_elementwise_conjugation(example):
    upper = dict(zip(("bubble", "mixed", "reverse", "loop_current"), N["direct_angular_moments"](.3, .04, .012+.004j, example)))
    lower = dict(zip(upper, N["direct_angular_moments"](.3, .04, .012-.004j, example)))
    expected = N["lower_reciprocity"](upper)
    assert max(N["D"]["errors"](lower, expected).values()) < 1e-9
    wrong = upper["reverse"].conj().T
    assert np.max(abs(wrong-lower["mixed"])) > 1e-3


def test_centered_vacuum_moments_match_independent_angular_integral():
    vacuum = N["VacuumAngularKernel"](np.array([.02, .2, 1., 20.]), .04)
    target = vacuum.energy+vacuum.mid_energy+.012+.003j
    moments = vacuum.moments(target)
    c, weights = np.polynomial.legendre.leggauss(64)
    for power, moment in enumerate(moments):
        eta = vacuum.half_width[:, None]*c
        direct = np.sum(weights*vacuum.half_width[:, None]*eta**power/(target[:, None]-eta), axis=1)
        assert moment == pytest.approx(direct, abs=1e-12)
    with pytest.raises(ValueError):
        vacuum.moments(vacuum.half_width)


def test_centered_vacuum_geometry_avoids_subtraction_of_k_squared():
    vacuum = N["VacuumAngularKernel"](np.array([.02, .2, 1., 20., 150.]), .04)
    assert vacuum.half_width*vacuum.mid_energy == pytest.approx(vacuum.k*.04, abs=1e-12)
    assert vacuum.mid_energy**2+vacuum.half_width**2 == pytest.approx(vacuum.k**2+.04**2+1., abs=1e-10)


def test_analytic_reference_matches_unchanged_full_vacuum_angular_kernel():
    k, q, z = np.array([.02, .2, 1., 20., 150.]), .04, .012+.003j
    actual = N["VacuumAngularKernel"](k, q).evaluate(z)
    original = N["R"]["angular_kernel"](k, q, z, 0., 0., 1., 1., 64)
    assert actual[0] == pytest.approx(original[0], abs=1e-9)
    assert actual[1] == pytest.approx(original[1], abs=1e-9)


def test_fixed_radial_nodes_do_not_move_with_trial_frequency(kernel):
    before_k = kernel.actual.k.copy()
    before_weights = kernel.measure.copy()
    kernel.principal_loops(.3+.02j)
    kernel.principal_loops(.22-.007j)
    assert np.array_equal(kernel.actual.k, before_k)
    assert np.array_equal(kernel.measure, before_weights)
    assert kernel.splits[0] == 0 and kernel.splits[-1] == 1


def test_integrated_direct_lower_matches_derived_source_reciprocity(kernel):
    v = .22-.007j
    reciprocal = kernel.principal_loops(v)
    independent_lower = kernel.principal_loops(v, direct_lower=True)
    assert max(N["D"]["errors"](reciprocal, independent_lower).values()) < 1e-9


def test_same_source_block_matches_original_upper_half_plane_response(kernel):
    v = .3+.02j
    loops = kernel.principal_loops(v)
    e = kernel.example
    expected = N["R"]["reoptimized_response"](.04, .04*v, e["mu"], e["a"], e["b"], e["s"], e["u_canonical"], loops)
    result = N["response"](.04, .04*v, e, loops)
    assert result["field"] == pytest.approx(expected[0], abs=1e-12)
    phase = expected[0][1, 1]-expected[0][1, 0]*expected[0][0, 1]/expected[0][0, 0]
    assert result["phase_coefficient"] == pytest.approx(phase/.04**2, abs=1e-12)


def test_uneliminated_determinant_matches_full_source_block(kernel):
    v, q, e = .3+.02j, kernel.q, kernel.example
    z = q*v
    loops = kernel.principal_loops(v)
    _, kcov, vertices = N["F"]["source_vertices"](e["s"], e["u_canonical"])
    covariance = np.eye(3)-kcov@loops["bubble"]
    internal = np.array([[q*q+e["a"]-z*z, 2j*e["mu"]*z], [-2j*e["mu"]*z, q*q+e["b"]-z*z]])
    block = np.block([[covariance, -vertices], [.5*vertices.T@loops["bubble"], internal]])
    result = N["response"](q, z, e, loops)
    assert result["uneliminated_scaled_determinant"] == pytest.approx(np.linalg.det(block)/q**2, abs=1e-10)


def test_actual_pole_at_nonzero_q_not_substituted_soft_answer(kernel, example):
    soft = N["G"]["unpack"](example["complex_density_runs"][0]["velocity_reference_is_prior_soft_pole_not_finite_q_pole"])
    pole, residual = kernel.pole(soft)
    assert residual < N["ROOT_TOLERANCE"]
    assert pole.imag < 0
    assert abs(pole-soft) > 1e-6
    assert abs(kernel.response(pole, sheet="principal_lower")["phase_coefficient"]) > 1e-3


def test_same_candidate_phase_and_radial_source_ward_not_projected(kernel):
    result = kernel.response(.22-.007j)
    assert result["phase_current_Ward_disagreement"] < N["PHASE_WARD_TOLERANCE"]
    assert abs(result["radial_inverse"]) > .01
    assert result["covariance_min_singular_value"] > .01


def test_source_block_dimensions_are_covariant_without_new_si_mapping(kernel):
    q, z, e, factor = .04, .04*(.3+.02j), kernel.example, 1.7
    loops = kernel.principal_loops(.3+.02j)
    scaled_e = e | {"mu": factor*e["mu"], "a": factor**2*e["a"], "b": factor**2*e["b"], "s": factor**2*e["s"]}
    scaled_loops = {key: value*factor**power for (key, value), power in zip(loops.items(), (0, 1, 1, 2))}
    actual = N["response"](factor*q, factor*z, scaled_e, scaled_loops)
    base = N["response"](q, z, e, loops)
    assert actual["field"] == pytest.approx(base["field"]*factor**2, abs=1e-10)
    assert actual["radial_current"] == pytest.approx(base["radial_current"]*factor**2, abs=1e-10)
    assert actual["phase_coefficient"] == pytest.approx(base["phase_coefficient"], abs=1e-10)
    assert actual["uneliminated_scaled_determinant"] == pytest.approx(base["uneliminated_scaled_determinant"]*factor**2, abs=1e-10)


def test_invalid_domains_exact_zero_fill_and_old_lower_validator_are_not_bypassed(kernel, example):
    for velocity in (.1-.001j, .5-.001j, .3-.02j, np.nan):
        with pytest.raises(ValueError):
            kernel.response(velocity)
    with pytest.raises(ValueError):
        kernel.response(.3-.005j, sheet="undeclared")
    with pytest.raises(ValueError):
        N["FiniteQKernel"](example, 0.)
    with pytest.raises(ValueError):
        N["fixed_radial_nodes"](.04, example, True)
    with pytest.raises(ValueError):
        N["R"]["validate"](.04, .01-.001j, example["T"], example["mu"], example["a"], example["b"])


def test_all_six_actual_poles_refine_and_approach_prior_soft_limit():
    for e in artifact()["examples"]:
        assert [row["q"] for row in e["finite_q_runs"]] == list(N["D"]["Q_GRID"])
        differences = [row["difference_from_soft_pole"] for row in e["finite_q_runs"]]
        assert differences[2] < differences[1] < differences[0]
        assert differences[0] > 1e-6
        assert e["alternate_fixed_grid_pole_disagreement"] < N["REFINEMENT_TOLERANCE"]
        for row in e["finite_q_runs"]:
            assert [(r["radial_order"], r["angular_order"]) for r in row["pole_runs"]] == list(N["ORDERS"])
            assert max(row["pole_refinements"]+row["second_seed_disagreements"]) < N["REFINEMENT_TOLERANCE"]
            assert row["alternate_tail_inverse_residual"] < N["ROOT_TOLERANCE"]
            for run in row["pole_runs"]:
                v = N["G"]["unpack"](run["velocity_pole"])
                assert N["G"]["unpack"](run["frequency_pole"]) == pytest.approx(row["q"]*v, abs=1e-14)
                assert run["inverse_residual"] < N["ROOT_TOLERANCE"]
                assert abs(N["G"]["unpack"](run["radial_inverse"])) > .01
                assert run["uneliminated_scaled_determinant_residual"] < N["ROOT_TOLERANCE"]


def test_simple_local_derivative_and_independent_upper_reference_are_recorded():
    for e in artifact()["examples"]:
        for row in e["finite_q_runs"]:
            derivative = row["simple_pole_derivative"]
            assert derivative["derivative_modulus"] > 1e-3
            assert derivative["derivative_refinement"] < N["REFINEMENT_TOLERANCE"]
            assert max(run["Cauchy_Riemann_disagreement"] for run in derivative["runs"]) < N["REFINEMENT_TOLERANCE"]
            assert [run["original_radial_order"] for run in row["original_upper_reference"]] == [64, 96, 128]
            assert max(row["original_upper_reference"][-1]["loop_disagreements"].values()) < N["REFINEMENT_TOLERANCE"]


def test_finite_q_result_cannot_promote_material_or_core_closure():
    record = artifact()
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert record["verification_status"] == "PASS_SCOPED_FINITE_Q_POLES"
    assert record["finite_q_complex_pole_computed"] is True
    assert all(record["checks"].values())
    assert len(record["report"]) == 11
    assert record["config"]["assigned_output_width"] is None
    assert record["runtime_arithmetic"]["extended_precision_not_assumed"] is True
    assert record["thresholds"]["causal_leakage_unchanged"] == 1e-6
    for flag in ("certified_global_stability", "certified_global_contour_homotopy", "physical_mode_speed_emitted", "collision_rate_emitted", "controlled_truncation_error_established",
                 "joint_Phi_stationarity_derived", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "claim_promotion", "parameter_fitting", "artificial_width", "clipping",
                 "IR_filter", "imposed_Ward_projection", "xie_2026_accessed", "core_composition_gate_overwritten", "C_relabelled_as_charge_or_mass", "R_gen_added_as_state"):
        assert record[flag] is False
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert "R_gen" in record["excluded_variables"]


def test_evidence_and_protected_core_hashes_unchanged():
    record = artifact()
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((N["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    predecessor = json.loads((N["ROOT"]/N["PREVIOUS_ARTIFACT"]).read_text(encoding="utf-8"))
    assert N["R"]["predecessor_hashes_match"](predecessor)
    predecessor["evidence_artifacts"][0]["sha256"] = "0"*64
    assert not N["R"]["predecessor_hashes_match"](predecessor)


def test_audit_reads_only_derived_predecessor_not_numeric_holdout():
    code = Path(__file__).with_name("Research_T13_Hartree_Finite_Q_Poles.py").read_text(encoding="utf-8")
    reads = [node for node in ast.walk(ast.parse(code)) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "read_text"]
    assert len(reads) == 1
    assert ast.unparse(reads[0].func.value) == "ROOT / PREVIOUS_ARTIFACT"
    assert N["PREVIOUS_ARTIFACT"].endswith("/t13_hartree_finite_q_discontinuity.json")
