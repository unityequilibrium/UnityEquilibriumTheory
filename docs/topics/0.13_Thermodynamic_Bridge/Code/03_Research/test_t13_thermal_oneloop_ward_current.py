"""Independent kernel checks and boundaries of thermal one-loop matching."""

import hashlib
import json
from math import pi, sqrt
from pathlib import Path
import runpy

import numpy as np
import pytest

MODULE = runpy.run_path(str(Path(__file__).with_name("Research_T13_Thermal_OneLoop_Ward_Current.py")))


def test_transverse_matrix_tadpole_and_bubble_obey_Ward_without_enforcing_it():
    for mu, r, z, lam in ((1.05, .1085, 1., 1.), (1.2, .446, 1., 1.), (.7, .18, 1.7, .3)):
        for k in (.03, .2, 1., 3.):
            for nu in (0., .13, -.7, 4.):
                tadpole, bubble, rhs = MODULE["ward_kernel"](nu, k, mu, r, z, lam)
                assert tadpole+bubble == pytest.approx(rhs, rel=1e-11, abs=1e-11)
                assert abs(bubble) > 1e-8
                assert abs(tadpole-rhs) > 1e-8


def test_matrix_loop_derivative_matches_independent_log_determinant_difference():
    mu, r, z, lam = 1.05, .1085, 1.3, .7
    amplitude = sqrt(z*r/lam)
    step = 1e-4
    for k, nu in ((.1, 0.), (.4, .2), (1., -.7)):
        def logdet(y):
            kernel = MODULE["euclidean_kernel"](nu, k, mu, r, z, lam, amplitude, y)
            sign, logabs = np.linalg.slogdet(kernel)
            assert sign > 0
            return .5*logabs/z
        numeric = (logdet(step)+logdet(-step)-2*logdet(0.))/step**2
        tadpole, bubble, _ = MODULE["ward_kernel"](nu, k, mu, r, z, lam)
        assert numeric == pytest.approx(tadpole+bubble, rel=1e-5, abs=1e-7)


def test_direct_Matsubara_sum_checks_thermal_subtraction_not_only_Ward_algebra():
    result = MODULE["matsubara_thermal_check"](.4, .22, 1.05, .1085, 1.3, .7, 512)
    assert result["maximum_relative_disagreement"] < MODULE["MATSUBARA_TOLERANCE"]
    direct = result["direct_matrix_sum_thermal"]
    assert direct[0]+direct[1] == pytest.approx(direct[2], abs=1e-11)


def test_thermal_loop_inverse_has_energy_squared_units_and_vanishes_at_zero_T():
    base = MODULE["thermal_diagrams"](.22, 1.05, .1085, 1.3, .7)
    for scale in (.7, 1.8):
        changed = MODULE["thermal_diagrams"](.22*scale, 1.05*scale, .1085*scale**2, 1.3, .7)
        for key in ("Omega_G_x", "transverse_tadpole", "transverse_bubble", "delta_x_order_one_loop"):
            assert changed[key] == pytest.approx(base[key]*scale**2, rel=1e-10, abs=1e-12)
    zero = MODULE["thermal_diagrams"](0., 1.05, .1085, 1.3, .7)
    assert zero["transverse_tadpole"] == zero["transverse_bubble"] == zero["Omega_G_x"] == 0.


def test_lambda_scaling_is_a_formal_loop_control_not_a_material_fit():
    base = MODULE["thermal_diagrams"](.22, 1.05, .1085, 1., 1.)
    smaller = MODULE["thermal_diagrams"](.22, 1.05, .1085, 1., .1)
    assert smaller["transverse_loop_inverse_at_zero"] == pytest.approx(.1*base["transverse_loop_inverse_at_zero"])
    assert smaller["fractional_amplitude_sq_shift"] == pytest.approx(.1*base["fractional_amplitude_sq_shift"])
    assert smaller["delta_x_order_one_loop"] == pytest.approx(base["delta_x_order_one_loop"])


def test_amplitude_Hessian_has_nonintegrable_IR_asymptote_not_finite_error_bar():
    t, z, lam = .22, 1.3, .7
    expected = -(lam/z)**2*t/(4*pi*pi)
    for mu, r in ((1.05, .1085), (1.2, .446)):
        errors = []
        for k in (1e-3, 2.5e-4, 1e-4):
            value = MODULE["amplitude_hessian_integrand"](k, t, mu, r, z, lam)
            errors.append(abs(k*k*value/expected-1))
        assert errors[2] < errors[1] < errors[0]
        assert errors[2] < 1e-4


def test_record_has_computed_loop_but_no_full_stationary_or_physical_unlock():
    record = json.loads(MODULE["OUTPUT"].read_text(encoding="utf-8"))
    assert all(record["checks"].values())
    assert record["verification_status"] == "PASS_THERMAL_ONE_LOOP_WARD_CURRENT"
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert record["thermal_zero_momentum_loop_computed"] is True
    for key in ("finite_momentum_retarded_response_derived", "joint_Phi_stationarity_derived",
                "exact_stationary_finite_T_background_derived", "vacuum_renormalization_matched",
                "controlled_truncation_error_established", "physical_Kubo_emitted",
                "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "claim_promotion",
                "parameter_fitting", "xie_2026_accessed"):
        assert record[key] is False
    for example in record["examples"]:
        assert example["reference"]["Ward_cancellation_absolute_residual"] < 1e-10
        assert example["static_current_order_matching_absolute_residual"] < 1e-10
        assert example["bare_shifted_low_mode_sq_at_k_zero"] < 0
        assert example["bare_shifted_Gaussian_not_evaluated_as_equilibrium"] is True
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((MODULE["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_live_thermal_diagrams_reproduce_the_record_across_float_libraries():
    record = json.loads(MODULE["OUTPUT"].read_text(encoding="utf-8"))
    for example in record["examples"]:
        actual = MODULE["thermal_diagrams"](example["T"], example["mu"], example["r"], example["Z"], example["lambda"])
        assert actual == pytest.approx(example["reference"], rel=1e-8, abs=1e-12)


def test_invalid_or_unstable_domain_is_rejected_not_clipped():
    with pytest.raises(ValueError):
        MODULE["thermal_diagrams"](-.1, 1.05, .1085, 1., 1.)
    with pytest.raises(ValueError):
        MODULE["thermal_diagrams"](.22, 1.05, -.1, 1., 1.)
    with pytest.raises(ValueError):
        MODULE["energies"](0., 1.05, .1085)
    with pytest.raises(ValueError):
        MODULE["thermal_diagrams"](.22, 1.05, .1085, 1., 1., order=True)
