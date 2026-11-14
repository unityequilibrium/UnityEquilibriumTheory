"""Independent soft moments, full-response convergence and closure boundaries."""

import ast
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

M = runpy.run_path(str(Path(__file__).with_name("Research_T13_Hartree_Soft_Collective.py")))


def artifact():
    return json.loads(M["OUTPUT"].read_text(encoding="utf-8"))


def test_angular_moments_match_independent_original_Cauchy_integral():
    for v in (.1, .3, 1.2, -1.2):
        for w in (.2, -.5, .8):
            assert M["angular_check"](v, w) < 1e-10


def test_static_and_large_velocity_limits_are_different():
    assert M["angular_moments"](0., .5)[0] == pytest.approx([-1., 0., -1/3])
    fast = M["angular_moments"](1e5, .5)[0]
    assert fast[0].real == pytest.approx((.5/1e5)**2/3, rel=1e-9)
    assert fast[1].real == pytest.approx((.5/1e5)/3, rel=1e-9)
    assert np.max(np.abs(fast)) < 2e-6


def test_signed_group_velocity_preserves_even_and_odd_angular_parity():
    forward = M["angular_moments"](.3, .6)[0]
    backward = M["angular_moments"](.3, -.6)[0]
    assert backward == pytest.approx(forward*np.array([1., -1., 1.]), abs=1e-12)


def test_exact_thermal_spectral_cut_not_finite_width():
    v, w = .3, .6
    moments = M["angular_moments"](v, w)[0]
    assert moments.imag == pytest.approx([-np.pi/2*(v/w)**(n+1) for n in range(3)])
    assert M["angular_moments"](1.2, w)[0].imag == pytest.approx([0., 0., 0.])
    with pytest.raises(ValueError):
        M["angular_moments"](w, w)


def test_upper_half_plane_moments_approach_exact_retarded_cut():
    exact = M["angular_moments"](.3, .6)[0]
    distances = [np.linalg.norm(M["angular_moments"](.3+1j*eta, .6)[0]-exact) for eta in (.01, .005, .0025)]
    assert distances[2] < distances[1] < distances[0]


def test_dispersion_group_velocity_matches_independent_finite_difference():
    for k in (.01, .1, 1., 10.):
        h = k*1e-5
        expected = (M["F"]["poles_and_residues"](k+h, 1.05, .23, .01)[0]-M["F"]["poles_and_residues"](k-h, 1.05, .23, .01)[0])/(2*h)
        assert M["group_velocities"](k, 1.05, .23, .01)[0] == pytest.approx(expected, rel=2e-6, abs=1e-8)


def test_velocity_endpoints_are_actual_dispersion_roots_not_IR_filter():
    roots = M["velocity_endpoints"](.3, 1.05, .23, .01)
    assert len(roots) == 2
    for k in roots:
        assert np.min(abs(abs(M["group_velocities"](k, 1.05, .23, .01)[0])-.3)) < 1e-10


def test_cold_and_static_equal_branch_differences_vanish():
    for velocity, t in ((.3, 0.), (0., .22)):
        loops = M["soft_difference"](velocity, t, 1.05, .23, .01)
        for key in ("bubble", "mixed", "reverse", "loop_current"):
            assert np.count_nonzero(loops[key]) == 0


def test_thermal_ray_is_not_same_as_equilibrium_polynomial():
    for e in artifact()["examples"]:
        row = next(row for row in e["rays"] if row["velocity_ray"] == .3)
        assert row["difference_from_static_polynomial"] > 1e-3
        assert abs(row["phase_coefficient"]["imaginary"]) > 1e-3
        fast = next(row for row in e["rays"] if row["velocity_ray"] == 1.2)
        assert abs(fast["phase_coefficient"]["imaginary"]) < 1e-8


def test_unchanged_full_finite_q_operator_approaches_soft_kernel():
    for e in artifact()["examples"]:
        for row in e["rays"]:
            runs = row["finite_q_runs"]
            assert [r["q"] for r in runs] == [.04, .02, .01]
            assert runs[-1]["phase_error_from_soft"] < runs[0]["phase_error_from_soft"]
            assert runs[-1]["loop_max_disagreement_from_soft"] < runs[0]["loop_max_disagreement_from_soft"]
            assert max(r["phase_vs_current_Ward_disagreement"] for r in runs) < 1e-3


def test_reactive_zero_is_not_reported_as_a_real_axis_pole():
    for e in artifact()["examples"]:
        root = e["reactive_zero"]
        assert .1 < root["velocity_ray_at_Re_inverse_zero"] < .6
        assert abs(root["phase_inverse_at_reactive_zero"]["real"]) < 1e-8
        assert root["phase_inverse_at_reactive_zero"]["imaginary"] < -1e-3
        assert root["is_a_real_frequency_pole"] is False
        assert root["quadrature_ray_difference"] < 1e-5


def test_rays_do_not_impose_goldstone_mass_or_current_projection():
    for e in artifact()["examples"]:
        for row in e["rays"]:
            assert row["zero_order_phase_Ward_residual"] < M["WARD_TOLERANCE"]
            assert row["covariance_min_singular_value"] > 0
    assert artifact()["imposed_Ward_projection"] is False


def test_invalid_soft_domains_are_refused():
    for v, w in ((.3, 0.), (-.1j, .5), (np.inf, .5), (.3, np.nan)):
        with pytest.raises(ValueError):
            M["angular_moments"](v, w)
    for kwargs in ({"order": True}, {"order": 16}):
        with pytest.raises(ValueError):
            M["soft_difference"](.3, .22, 1.05, .23, .01, **kwargs)
    with pytest.raises(ValueError):
        M["soft_difference"](.3, .22, 1.05, .23, 0.)


def test_natural_energy_scaling_preserves_soft_phase_not_material_SI():
    e = artifact()["examples"][0]
    base = M["soft_difference"](.3, e["T"], e["mu"], e["a"], e["b"])
    f = 1.7
    scaled = M["soft_difference"](.3, f*e["T"], f*e["mu"], f*f*e["a"], f*f*e["b"])
    for key, power in (("bubble", 0), ("mixed", 1), ("reverse", 1), ("loop_current", 2)):
        assert scaled[key] == pytest.approx(base[key]*f**power, abs=1e-9)


def test_artifact_preserves_physical_and_global_proof_boundaries_and_hashes():
    record = artifact()
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert record["verification_status"] == "PASS_SCOPED_COLLISIONLESS_SOFT_RESPONSE"
    assert all(record["checks"].values())
    assert len(record["report"]) == 11
    assert record["config"]["output_width"] == 0
    assert record["config"]["radial_domain"] == "0<=k<infinity"
    for flag in ("global_real_axis_stability_proved", "collective_mode_speed_emitted", "collision_rate_emitted", "controlled_truncation_error_established",
                 "joint_Phi_stationarity_derived", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "claim_promotion",
                 "parameter_fitting", "artificial_width", "clipping", "IR_filter", "imposed_Ward_projection", "xie_2026_accessed",
                 "core_composition_gate_overwritten", "C_relabelled_as_charge_or_mass", "R_gen_added_as_state"):
        assert record[flag] is False
    assert "R_gen" in record["excluded_variables"]
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((M["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_changed_upstream_hash_stays_detectable():
    record = json.loads((M["ROOT"]/M["PREVIOUS_ARTIFACT"]).read_text(encoding="utf-8"))
    assert M["R"]["predecessor_hashes_match"](record)
    record["evidence_artifacts"][0]["sha256"] = "0"*64
    assert not M["R"]["predecessor_hashes_match"](record)


def test_audit_has_only_the_declared_derived_predecessor_text_read():
    code = Path(__file__).with_name("Research_T13_Hartree_Soft_Collective.py").read_text(encoding="utf-8")
    tree = ast.parse(code)
    reads = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Attribute) and node.func.attr == "read_text"]
    assert len(reads) == 1
    assert ast.unparse(reads[0].func.value) == "ROOT / PREVIOUS_ARTIFACT"
    assert M["PREVIOUS_ARTIFACT"].endswith("/t13_hartree_real_axis.json")
