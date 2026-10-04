"""Finite-external-momentum loop checks, including independent frequency sums."""

import hashlib
import json
from math import pi, sqrt
from pathlib import Path
import runpy

import numpy as np
import pytest
from scipy.integrate import quad

M = runpy.run_path(str(Path(__file__).with_name("Research_T13_Finite_Momentum_Thermal_1PI.py")))


def test_residue_propagator_matches_direct_inverse_not_only_its_determinant():
    for mu, r in ((1.05, .1085), (1.2, .446), (0., .3)):
        for k in (.02, .4, 3.):
            poles, residues = M["poles_and_residues"](k, mu, r)
            for z in (.15+.1j, 1.7j):
                reconstructed = np.sum(residues/(z-poles)[:, None, None], axis=0)
                inverse = np.linalg.inv(np.array([[k*k+2*r-z*z, 2j*mu*z],
                                                 [-2j*mu*z, k*k-z*z]]))
                np.testing.assert_allclose(reconstructed, inverse, rtol=1e-10, atol=1e-10)


def test_static_coincident_poles_use_bose_derivative_not_zero_or_clipping():
    p = np.array([-.2, .2, 3.])
    n = M["bose"](np.abs(p), .22)
    np.testing.assert_allclose(M["convolution_weight"](p, p, .22, 0j), n*(1+n)/.22)
    near = M["convolution_weight"](p, p*(1+1e-10), .22, 0j)
    np.testing.assert_allclose(near, n*(1+n)/.22, rtol=2e-9)


def test_full_matrix_frequency_sum_has_nonzero_antisymmetric_mixing():
    result = M["matrix_frequency_check"](.4, .55, .22, 1.05, .1085, 1.3, .7, 1, 256)
    assert result["relative_disagreement"] < M["POINT_TOLERANCE"]
    assert result["spectral_imaginary_max"] < 1e-10
    direct = np.array(result["direct"])
    assert abs(direct[0, 1]) > 1e-3
    assert direct[0, 1] == pytest.approx(-direct[1, 0], abs=1e-11)


def test_zero_mode_convolution_is_checked_by_independent_feynman_parameter_integral():
    for q, a, b in ((.04, 0., 0.), (.04, .3, 0.), (.08, .3, .3), (.1, .2, .5)):
        independent = quad(lambda x: 1/sqrt(x*a*a+(1-x)*b*b+x*(1-x)*q*q),
                           0., 1., epsabs=1e-10, epsrel=1e-10)[0]/(8*pi)
        assert M["convolution_3d"](q, a, b) == pytest.approx(independent, rel=1e-9)


def test_finite_q_static_and_dynamic_loops_have_energy_squared_units():
    for frequency in (0j, .15+.1j):
        base = M["integrated_bubble"](.04, .22, 1.05, .1085, 1.3, .7, frequency, 64, 32)
        scale = 1.8
        changed = M["integrated_bubble"](.04*scale, .22*scale, 1.05*scale, .1085*scale**2,
                                        1.3, .7, frequency*scale, 64, 32)
        np.testing.assert_allclose(changed, base*scale**2, rtol=1e-8, atol=1e-10)


def test_bubble_is_thermal_difference_and_formal_lambda_scaling_not_a_fit():
    base = M["integrated_bubble"](.04, .22, 1.05, .1085, 1., 1., radial_order=64, angular_order=32)
    changed = M["integrated_bubble"](.04, .22, 1.05, .1085, 1., .1, radial_order=64, angular_order=32)
    np.testing.assert_allclose(changed, .1*base, rtol=1e-9, atol=1e-10)
    zero = M["integrated_bubble"](.04, 0., 1.05, .1085, 1., 1., radial_order=32, angular_order=16)
    np.testing.assert_array_equal(zero, np.zeros((2, 2)))


def test_static_radial_IR_coefficient_is_retained_and_not_a_physical_cutoff():
    t, mu, r, Z, lam = .22, 1.05, .1085, 1.3, .7
    coefficient = -lam*r*t/(4*Z*Z)
    values = [q*M["zero_matsubara_integral"](q, t, mu, r, Z, lam)[0, 0] for q in (.01, .005, .001)]
    errors = [abs(v/coefficient-1) for v in values]
    assert errors[2] < errors[1] < errors[0]
    assert errors[2] < .01


def test_live_static_result_and_current_match_the_record():
    record = json.loads(M["OUTPUT"].read_text(encoding="utf-8"))
    assert all(record["checks"].values())
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    for example in record["examples"]:
        row = example["static"][1]
        live = M["integrated_bubble"](row["q"], example["T"], example["mu"], example["r"],
                                      example["Z"], example["lambda"])
        np.testing.assert_allclose(live.real, row["bubble"]["real"], rtol=1e-6, atol=1e-10)
        assert example["current_from_finite_q"] == pytest.approx(example["previous_static_current"], rel=1e-4)
        assert example["formal_IR_breakdown_momentum"] == pytest.approx(.0275)
        assert example["IR_ratio_to_tree_radial_mass"][0]["ratio"] > 1


def test_artifact_hashes_preserve_prior_failures_and_no_physical_unlock():
    record = json.loads(M["OUTPUT"].read_text(encoding="utf-8"))
    for flag in ("real_axis_damping_derived", "IR_resummation_derived", "controlled_truncation_error_established",
                 "physical_Kubo_emitted", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock",
                 "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting", "xie_2026_accessed",
                 "clipping", "IR_filter", "momentum_cutoff"):
        assert record[flag] is False
    assert record["inverse_used_as_Dyson_resummation"] is False
    assert record["order_matched_thermal_inverse_computed"] is True
    assert set(record["report"]) == {
        "MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED",
        "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER",
        "NEXT_ACTION", "CLAIM_BOUNDARY"}
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((M["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_order_matched_inverse_uses_prior_tadpole_shift_not_a_new_counterterm():
    zero = M["WARD"]["thermal_diagrams"](.22, 1.05, .1085, 1., 1.)
    bubble = M["integrated_bubble"](.04, .22, 1.05, .1085, 1., 1., radial_order=64, angular_order=32)
    inverse = M["formal_inverse_from_bubble"](.04, 0j, 1.05, .1085, 1., zero, bubble)
    assert inverse[1, 1] == pytest.approx(.04**2+bubble[1, 1]-zero["transverse_bubble"])
    assert inverse[0, 0] == pytest.approx(.04**2+2*.1085-4*zero["Omega_G_x"]+bubble[0, 0])
    zero_bubble = np.diag([0., zero["transverse_bubble"]])
    assert M["formal_inverse_from_bubble"](0., 0j, 1.05, .1085, 1., zero, zero_bubble)[1, 1] == 0.


def test_invalid_frequency_and_unstable_domains_are_rejected():
    for z in (.15, .15-.1j, complex(float("nan"), .1)):
        with pytest.raises(ValueError):
            M["point_bubble"](.4, .55, .22, 1.05, .1085, 1., 1., z)
    with pytest.raises(ValueError):
        M["poles_and_residues"](0., 1.05, .1085)
    with pytest.raises(ValueError):
        M["integrated_bubble"](.04, .22, 1.05, -.1, 1., 1.)
    with pytest.raises(ValueError):
        M["integrated_bubble"](.04, .22, 1.05, .1085, 1., 1., radial_order=True)
