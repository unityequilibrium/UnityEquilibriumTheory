"""Same-field source/current/measure identities and the static IR claim boundary."""

import hashlib
import json
from math import pi, sqrt
from pathlib import Path
import runpy

import numpy as np
import pytest

M = runpy.run_path(str(Path(__file__).with_name("Research_T13_Polar_Static_IR_Observable.py")))


def test_complete_source_and_chemical_action_survives_coordinate_change():
    for rho, mu, r, Z, lam in ((.4, 1.05, .1085, 1., 1.), (.7, 1.2, .446, 1.3, .7), (.5, 0., .2, .8, .3)):
        result = M["action_coordinate_check"](rho, mu, r, Z, lam)
        assert result["full_source_action_residual"] < 1e-12
        assert result["Jacobian_determinant_residual"] < 1e-12
        assert result["source_torque_difference_residual"] < 1e-10
    np.testing.assert_allclose(M["polar_map"](.4, .7), M["polar_map"](.4, .7+2*pi), atol=1e-14)


def test_finite_dimensional_measure_is_not_silently_flattened():
    result = M["measure_integral"](1.4, .3)
    assert result["relative_disagreement"] < 1e-11
    assert abs(result["polar_without_jacobian"]/result["cartesian_integral"]-1) > .1
    for rho, theta in ((.4, .7), (.8, -.3)):
        step = 1e-6
        difference = np.stack(((M["polar_map"](rho+step, theta)-M["polar_map"](rho-step, theta))/(2*step),
                               (M["polar_map"](rho, theta+step)-M["polar_map"](rho, theta-step))/(2*step)), axis=1)
        np.testing.assert_allclose(difference, M["polar_jacobian"](rho, theta), atol=1e-9)


def test_offshell_zero_polar_angle_mass_does_not_close_stationarity():
    rho, r, Z, lam = .4, .1085, 1.3, .7
    result = M["offshell_angular_hessian"](rho, r, Z, lam)
    assert abs(result["radial_tadpole"]) > .001
    assert abs(result["cartesian_transverse_hessian"]) > .001
    assert result["linear_pullback"] == pytest.approx(-result["gradient_chain_term"])
    assert result["polar_angular_hessian"] == pytest.approx(0., abs=1e-14)
    A = sqrt(Z*r/lam)
    assert M["offshell_angular_hessian"](A, r, Z, lam)["radial_tadpole"] == pytest.approx(0., abs=1e-14)


def test_phase_schur_complement_retains_finite_density_time_term():
    nu, k, mu, r, Z, lam = .13, .2, 1.05, .1085, 1.3, .7
    x = Z*r/lam
    actual = M["phase_schur"](nu, k, mu, r, Z, lam)
    expected = Z*x*(nu*nu+k*k+4*mu*mu*nu*nu/(nu*nu+k*k+2*r))
    assert actual == pytest.approx(expected, rel=1e-12)
    assert actual > Z*x*(nu*nu+k*k)


def test_offshell_Cartesian_source_and_Jacobian_restore_the_same_Gaussian():
    mu, r, Z, lam = 1.05, .1085, 1.3, .7
    rho = 1.1*sqrt(Z*r/lam)
    for nu, k in ((.13, .2), (0., .3), (-.7, 1.)):
        kernel, logdet, source = M["source_completed_gaussian"](nu, k, rho, mu, r, Z, lam)
        cart = Z*M["FINITE"]["WARD"]["euclidean_kernel"](nu, k, mu, r, Z, lam, rho)
        transform = np.diag([1., rho])
        np.testing.assert_allclose(kernel, transform.T@cart@transform, atol=1e-12)
        assert logdet == pytest.approx(.5*np.linalg.slogdet(cart)[1], abs=1e-12)
        assert source != 0.
        assert .5*np.linalg.slogdet(kernel)[1]-logdet == pytest.approx(np.log(rho))
        _, changed_reference, _ = M["source_completed_gaussian"](nu, k, rho, mu, r, Z, lam, energy_reference=2.3)
        assert changed_reference == pytest.approx(.5*np.linalg.slogdet(cart/2.3**2)[1], abs=1e-12)


def test_source_complete_logdet_derivative_does_not_drop_transverse_tadpole():
    nu, k, mu, r, Z, lam = .2, .4, 1.05, .1085, 1.3, .7
    x = Z*r/lam
    step = 1e-5*x
    def correct(xx):
        return M["source_completed_gaussian"](nu, k, sqrt(xx), mu, r, Z, lam)[1]
    difference = (correct(x+step)-correct(x-step))/(2*step)
    G = np.linalg.inv(M["FINITE"]["WARD"]["euclidean_kernel"](nu, k, mu, r, Z, lam, sqrt(x)))
    expected = lam/(2*Z)*(3*G[0, 0]+G[1, 1])
    naive = 3*lam/(2*Z)*G[0, 0]
    assert difference == pytest.approx(expected, rel=1e-8)
    assert expected-naive == pytest.approx(lam/(2*Z)*G[1, 1])
    assert abs(difference-naive) > .1


def test_quadratic_observable_source_derivative_has_connected_Wick_factor():
    result = M["gaussian_source_check"]()
    assert result["source_difference"] > 0
    assert result["relative_disagreement"] < M["SOURCE_DIFFERENCE_TOLERANCE"]
    assert abs(result["source_difference"]/(.5*result["connected_Wick_susceptibility"])-1) > .9


def test_static_spatial_current_is_source_derivative_not_a_fitted_coefficient():
    grad, a, stiffness = np.array([.1, -.2, .3]), np.array([-.01, .02, .03]), .12
    step = 1e-6
    expected = stiffness*(grad-a)
    for i in range(3):
        shift = np.eye(3)[i]*step
        source_current = -(M["spatial_source_density"](grad, a+shift, stiffness)-
                           M["spatial_source_density"](grad, a-shift, stiffness))/(2*step)
        assert source_current == pytest.approx(expected[i], rel=1e-9, abs=1e-11)
    assert M["spatial_source_density"](grad+a, a, stiffness) == pytest.approx(M["spatial_source_density"](grad, np.zeros(3), stiffness))


def test_cartesian_susceptibility_units_IR_coefficient_and_zero_temperature():
    base = M["static_response"](.0025, .22, 1.05, .1085, 1.3, .7)
    for scale in (.7, 1.8):
        changed = M["static_response"](.0025*scale, .22*scale, 1.05*scale, .1085*scale**2, 1.3, .7)
        assert changed["cartesian_longitudinal_susceptibility"] == pytest.approx(base["cartesian_longitudinal_susceptibility"]/scale**2)
        assert changed["normalized_longitudinal_inverse"] == pytest.approx(base["normalized_longitudinal_inverse"]*scale**2)
    coefficient = -(2*.1085)**2*1.3*base["x_tree"]*.22/(16*base["stiffness"]**2)
    assert coefficient == pytest.approx(-.7*.1085*.22/(4*1.3**2))
    zero = M["static_response"](.0025, 0., 1.05, .1085, 1.3, .7)
    assert zero["cartesian_longitudinal_composite_susceptibility"] == 0.
    assert zero["normalized_longitudinal_inverse"] == pytest.approx(.0025**2+2*.1085)
    field, dt, gradients, source = np.array([.4, .2]), np.array([.1, -.2]), np.array([[.2, .1], [-.1, .3]]), np.array([.03, -.02])
    action = M["cartesian_density"](field, dt, gradients, 1.05, .1085, 1.3, .7, source)
    scale = 1.8
    scaled = M["cartesian_density"](field*scale, dt*scale**2, gradients*scale**2,
                                    1.05*scale, .1085*scale**2, 1.3, .7, source*scale**3)
    assert scaled == pytest.approx(action*scale**4)


def test_positive_IR_susceptibility_is_not_the_uncontrolled_inverse_expansion():
    row = M["static_response"](.0025, .22, 1.05, .1085, 1., 1.)
    assert row["inverse_expansion_parameter"] > 10
    bare_expanded = .0025**2+2*.1085+row["small_correction_inverse_term"]
    assert bare_expanded < 0 < row["normalized_longitudinal_inverse"]
    assert row["cartesian_longitudinal_susceptibility"] > row["radial_modulus_susceptibility"]
    # It is the nonlinear Cartesian source observable, not merely rho, that has the 1/q term.
    finer = M["static_response"](.00125, .22, 1.05, .1085, 1., 1.)
    assert finer["cartesian_longitudinal_composite_susceptibility"] == pytest.approx(2*row["cartesian_longitudinal_composite_susceptibility"])
    assert finer["normalized_longitudinal_inverse"] < row["normalized_longitudinal_inverse"]


def test_record_and_evidence_preserve_microscopic_and_physical_open_gates():
    record = json.loads(M["OUTPUT"].read_text(encoding="utf-8"))
    assert all(record["checks"].values())
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert record["static_IR_observable_match_derived"] is True
    for flag in ("microscopic_IR_resummation_derived", "continuum_measure_counterterms_matched",
                 "vacuum_renormalization_matched",
                 "joint_Phi_stationarity_derived", "renormalized_order_parameter_matched", "real_axis_response_derived",
                 "controlled_truncation_error_established", "physical_Kubo_emitted", "g1_physical_unlock",
                 "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion",
                 "parameter_fitting", "xie_2026_accessed", "phase_mass_added", "IR_filter", "clipping",
                 "arbitrary_Pade_prescription", "C_relabelled_as_charge_or_mass", "R_gen_added_as_state"):
        assert record[flag] is False
    assert set(record["report"]) == {"MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN",
        "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION",
        "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY"}
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((M["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_live_reconstruction_reproduces_record_without_reading_measured_rows():
    record = json.loads(M["OUTPUT"].read_text(encoding="utf-8"))
    for example in record["examples"]:
        for row in example["susceptibility_refinement"]:
            live = M["static_response"](row["q"], example["T"], example["mu"], example["r"], example["Z"], example["lambda"])
            assert live == pytest.approx({key: value for key, value in row.items() if key != "q"}, rel=1e-10, abs=1e-12)


def test_singular_chart_and_bad_source_domains_are_rejected():
    with pytest.raises(ValueError):
        M["polar_map"](0., .7)
    with pytest.raises(ValueError):
        M["static_response"](0., .22, 1.05, .1085, 1., 1.)
    with pytest.raises(ValueError):
        M["static_response"](.0025, .22, 1.05, .1085, 1., 1., stiffness=-.1)
    with pytest.raises(ValueError):
        M["polar_density"](.4, .7, .1, .2, [.1], [.1, .2], 1.05, .1085, 1., 1.)
