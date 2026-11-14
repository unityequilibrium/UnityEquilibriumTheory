"""Independent discontinuity, continuation, pole and non-promotion checks."""

import ast
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

P = runpy.run_path(str(Path(__file__).with_name("Research_T13_Hartree_Soft_Poles.py")))


def artifact():
    return json.loads(P["OUTPUT"].read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def kernel():
    return P["SoftKernel"](artifact()["examples"][0], 96)


def test_complex_dispersion_and_residues_recover_original_real_propagator():
    e = artifact()["examples"][0]
    for k in (.01, .1, 1., 10.):
        poles, residues, speeds = P["complex_poles"](k, e["mu"], e["a"], e["b"])
        original_poles, original_residues = P["G"]["extended_poles"](np.array([k]), e["mu"], e["a"], e["b"])
        assert poles == pytest.approx(np.asarray(original_poles, complex), abs=1e-12)
        assert residues == pytest.approx(np.asarray(original_residues, complex), abs=1e-11)
        assert speeds == pytest.approx(P["M"]["group_velocities"](k, e["mu"], e["a"], e["b"]), abs=1e-12)


def test_complex_group_velocity_matches_derivative_of_same_dispersion():
    e = artifact()["examples"][0]
    k, h = .2-.01j, 1e-6
    plus = P["complex_poles"](k+h, e["mu"], e["a"], e["b"])[0]
    minus = P["complex_poles"](k-h, e["mu"], e["a"], e["b"])[0]
    speed = P["complex_poles"](k, e["mu"], e["a"], e["b"])[2]
    assert speed == pytest.approx((plus-minus)/(2*h), rel=1e-7, abs=1e-8)


def test_tail_density_matches_independent_original_angular_discontinuity():
    for e in artifact()["examples"]:
        row = P["spectral_jump_check"](e, .3, 96)
        assert max(row["independent_original_angular_cut_errors"].values()) < 1e-10


def test_local_complex_velocity_thresholds_are_same_dispersion_roots():
    e = artifact()["examples"][0]
    v = .25-.01j
    for mode in (2, 3):
        k, error = P["velocity_root"](v, e, mode)
        assert error < 1e-9
        assert k.real > 0
        assert P["complex_poles"](k, e["mu"], e["a"], e["b"])[2][0, mode] == pytest.approx(v, abs=1e-9)


def test_two_homotopic_tail_contours_agree_without_fitted_width():
    e = artifact()["examples"][0]
    first, _ = P["spectral_tail"](.25-.01j, e, 96, "horizontal")
    second, _ = P["spectral_tail"](.25-.01j, e, 96, "return_to_real")
    for key in first:
        assert first[key] == pytest.approx(second[key], abs=1e-10)


def test_upper_half_plane_matches_accepted_independent_soft_integral(kernel):
    e = kernel.example
    v = .3+.02j
    direct = P["M"]["soft_difference"](v, e["T"], e["mu"], e["a"], e["b"], 512)
    fixed = kernel.principal_difference(v)
    for key in fixed:
        assert fixed[key] == pytest.approx(direct[key], abs=1e-9)


def test_original_unsplit_reference_convergence_is_reported_not_hidden():
    for e in artifact()["examples"]:
        rows = e["independent_upper_reference"]["runs"]
        assert [r["original_unsplit_order"] for r in rows] == [128, 256, 512]
        errors = [max(r["loop_disagreements"].values()) for r in rows]
        assert errors[-1] < errors[1] < errors[0]
        assert errors[-1] < 1e-9


def test_computed_pole_has_nonzero_derivative_and_inverse_residue(kernel):
    pole, residual = kernel.pole(.2-.01j)
    assert residual < P["ROOT_TOLERANCE"]
    row = P["derivative_audit"](kernel, pole)
    assert row["nonzero_derivative_modulus"] > 1e-3
    assert row["Cauchy_Riemann_disagreement"] < P["REFINEMENT_TOLERANCE"]
    derivative = P["G"]["unpack"](row["derivative"])
    residue = P["G"]["unpack"](row["local_inverse_residue_in_v"])
    assert derivative*residue == pytest.approx(1., abs=1e-12)


def test_principal_lower_shortcut_is_not_the_retarded_pole(kernel):
    pole = P["G"]["unpack"](artifact()["examples"][0]["pole_runs"][-1]["velocity_pole"])
    correct = kernel.response(pole)["phase_coefficient"]
    wrong = kernel.response(pole, sheet="principal_lower")["phase_coefficient"]
    assert abs(correct) < P["ROOT_TOLERANCE"]
    assert abs(wrong) > 1e-3


def test_retarded_continuation_approaches_the_real_cut_from_both_sides():
    for e in artifact()["examples"]:
        for row in e["continuation_boundaries"]:
            runs = row["runs"]
            for metric in ("above_error_from_real_axis", "below_error_from_real_axis", "upper_lower_difference"):
                assert runs[-1][metric] < runs[0][metric]
            assert runs[-1]["below_error_from_real_axis"] < .02


def test_simple_pole_is_not_a_radial_or_covariance_elimination_singularity():
    for e in artifact()["examples"]:
        for run in e["pole_runs"]:
            assert abs(P["G"]["unpack"](run["radial_inverse"])) > .01
            assert abs(P["G"]["unpack"](run["covariance_determinant"])) > .01
            assert run["uneliminated_determinant_residual"] < P["ROOT_TOLERANCE"]


def test_two_seeds_orders_and_alternate_grid_contour_recover_same_pole():
    for e in artifact()["examples"]:
        assert [r["order"] for r in e["pole_runs"]] == [64, 96, 128]
        assert max(e["pole_refinements"]) < P["REFINEMENT_TOLERANCE"]
        for metric in ("second_seed_disagreement", "alternate_grid_disagreement", "alternate_contour_disagreement"):
            assert e[metric] < P["REFINEMENT_TOLERANCE"]


def test_sampled_winding_has_orientation_and_resolution_negative_controls():
    points = P["contour_points"]((-1., 1., -1., 1.), 32)
    assert P["sampled_winding"](points)["sampled_winding"] == pytest.approx(1.)
    assert P["sampled_winding"](points[::-1])["sampled_winding"] == pytest.approx(-1.)
    assert P["sampled_winding"](points-2)["sampled_winding"] == pytest.approx(0.)
    assert P["sampled_winding"](points)["certified_zero_count"] is False


def test_contour_diagnostic_is_bounded_and_not_a_global_stability_proof():
    for e in artifact()["examples"]:
        for family, expected in (("upper_contour", 0), ("local_lower_contour", 1)):
            assert [r["steps_per_edge"] for r in e[family]] == [64, 128, 256, 512]
            for row in e[family]:
                for key in ("phase", "uneliminated"):
                    assert row[key]["sampled_winding"] == pytest.approx(expected, abs=1e-6)
                    assert row[key]["certified_zero_count"] is False
                for key in ("radial", "covariance"):
                    assert row[key]["sampled_winding"] == pytest.approx(0., abs=1e-6)
            assert e[family][-1]["phase"]["maximum_phase_increment"] < np.pi/2
    assert artifact()["config"]["upper_contour"][2] > 0


def test_invalid_local_domains_and_nonpositive_witnesses_are_refused(kernel):
    for velocity in (.05-.01j, .7-.01j, .3-.03j, np.nan):
        with pytest.raises(ValueError):
            kernel.response(velocity)
    for changed in ({"T": 0.}, {"b": 0.}, {"mu": 0.}, {"s": 0.}, {"u_canonical": -1.}):
        with pytest.raises(ValueError):
            P["SoftKernel"](kernel.example | changed)
    for order in (True, 16):
        with pytest.raises(ValueError):
            P["SoftKernel"](kernel.example, order)
    with pytest.raises(ValueError):
        P["spectral_tail"](.3, kernel.example, contour="undeclared")
    with pytest.raises(ValueError):
        P["velocity_root"](.3, kernel.example, 1)


def test_thermal_spectral_density_obeys_declared_energy_units():
    e = artifact()["examples"][0]
    scale = 1.7
    scaled = e | {"T": scale*e["T"], "mu": scale*e["mu"], "a": scale**2*e["a"], "b": scale**2*e["b"], "s": scale**2*e["s"]}
    base, _ = P["spectral_tail"](.3-.01j, e)
    other, _ = P["spectral_tail"](.3-.01j, scaled)
    for key, power in (("bubble", 0), ("mixed", 1), ("reverse", 1), ("loop_current", 2)):
        assert other[key] == pytest.approx(base[key]*scale**power, abs=1e-9)


def test_artifact_preserves_ontology_empirical_and_approximation_boundaries():
    record = artifact()
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert record["verification_status"] == "PASS_SCOPED_LOCAL_LANDAU_POLE"
    assert all(record["checks"].values())
    assert record["conditional_collisionless_soft_pole_computed"] is True
    assert len(record["report"]) == 11
    assert record["config"]["assigned_output_width"] is None
    assert record["config"]["radial_domain"] == "0<=k<infinity"
    for flag in ("certified_zero_count", "global_stability_proved", "finite_q_complex_pole_computed", "physical_mode_speed_emitted", "collision_rate_emitted",
                 "controlled_truncation_error_established", "joint_Phi_stationarity_derived", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "claim_promotion",
                 "parameter_fitting", "artificial_width", "clipping", "IR_filter", "imposed_Ward_projection", "xie_2026_accessed", "core_composition_gate_overwritten",
                 "C_relabelled_as_charge_or_mass", "R_gen_added_as_state"):
        assert record[flag] is False
    assert "R_gen" in record["excluded_variables"]
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"


def test_upstream_protected_hashes_and_tampered_lineage():
    record = artifact()
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((P["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    predecessor = json.loads((P["ROOT"]/P["PREVIOUS_ARTIFACT"]).read_text(encoding="utf-8"))
    assert P["R"]["predecessor_hashes_match"](predecessor)
    predecessor["evidence_artifacts"][0]["sha256"] = "0"*64
    assert not P["R"]["predecessor_hashes_match"](predecessor)


def test_audit_reads_only_declared_derived_predecessor_not_numeric_holdout():
    code = Path(__file__).with_name("Research_T13_Hartree_Soft_Poles.py").read_text(encoding="utf-8")
    tree = ast.parse(code)
    reads = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "read_text"]
    assert len(reads) == 1
    assert ast.unparse(reads[0].func.value) == "ROOT / PREVIOUS_ARTIFACT"
    assert P["PREVIOUS_ARTIFACT"].endswith("/t13_hartree_soft_collective.json")
