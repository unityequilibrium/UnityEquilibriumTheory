"""Moving-spectrum derivative checks and preservation of stationarity limits."""

import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

MODULE = runpy.run_path(str(Path(__file__).with_name("Research_T13_Moving_Background_Thermal_Stiffness.py")))


def test_implicit_spectral_derivatives_match_independent_quartic_roots():
    mu, r = 1.05, .1085
    h = 1e-4
    for k in (.03, .2, 1., 3.):
        zero = MODULE["moving_energies"](k, 0., 0., mu, r)
        for cosine in (-.8, .3, 1.):
            plus = MODULE["moving_energies"](k, cosine, h, mu, r)
            minus = MODULE["moving_energies"](k, cosine, -h, mu, r)
            for energy, ep, em in zip(zero, plus, minus):
                d1, _ = MODULE["root_derivatives"](k, energy, mu, r)
                d2 = MODULE["root_directional_second"](k, energy, cosine, mu, r)
                assert (ep-em)/(2*h) == pytest.approx(d1*cosine, rel=2e-5, abs=1e-7)
                assert (ep+em-2*energy)/h**2 == pytest.approx(d2, rel=2e-4, abs=2e-6)


def test_massless_phonon_limit_matches_low_temperature_gradient_curvature():
    mu, r, k = 1., 1., 1e-3
    energy = MODULE["moving_energies"](k, 0., 0., mu, r)[0]
    d1, d2 = MODULE["root_derivatives"](k, energy, mu, r)
    c0 = 1/np.sqrt(3.)
    assert energy/k == pytest.approx(c0, rel=1e-6)
    assert d1/k == pytest.approx(-2/3, rel=1e-6)
    assert d2/k == pytest.approx(-8/(27*c0), rel=1e-6)
    # Integrating these coefficients gives delta_f_s=-8*p_phonon/mu^2.
    phonon_pressure_coefficient = np.pi**2/(90*c0**3)
    integral_kf_coefficient = np.pi**2/(30*c0**4)
    gradient_coefficient = (d2/k - 4*(d1/k)**2/(3*c0))*integral_kf_coefficient
    assert gradient_coefficient == pytest.approx(-8*phonon_pressure_coefficient, rel=2e-6)


def test_recorded_two_method_curvature_and_tadpole_chain_rule():
    record = json.loads(MODULE["OUTPUT"].read_text(encoding="utf-8"))
    assert all(record["checks"].values())
    assert record["verification_status"] == "PASS_TREE_RELAXED_THERMAL_CURVATURE"
    for example in record["examples"]:
        reference = example["reference"]
        assert reference["f_s_tree_relaxed_thermal"] < reference["f_s_tree"]
        assert reference["Omega_x_at_tree_amplitude"] > 0
        assert reference["path_chain_rule_absolute_residual"] < 1e-12
        assert reference["f_s_tree_relaxed_thermal"] == pytest.approx(
            reference["f_s_held_amplitude_thermal"] + reference["amplitude_path_term"], abs=1e-12
        )
        assert reference["unresummed_phase_mass_sq_after_linearized_shift"] < 0
        assert example["direct_derivative_relative_disagreement"] < record["numeric_tolerance"]
        assert example["thermal_curvature_modes"]["subluminal"]
        assert example["path_current_identification_admitted"] is False
        assert example["held_amplitude_mode_mixing_role"] == "INCONSISTENT_EOS_DERIVATIVE_PROTOCOL_SCREEN_ONLY"
        assert example["physical_HeII_state_admitted"] is False
    assert record["examples"][0]["old_tree_modes"]["subluminal"] is False
    for key in ("g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "claim_promotion",
                "physical_finite_T_stiffness_admitted", "microscopic_Ward_loop_response_computed",
                "parameter_fitting", "xie_2026_accessed"):
        assert record[key] is False
    for item in record["evidence_artifacts"]:
        assert hashlib.sha256((MODULE["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_live_static_curvature_reproduces_record_without_bitwise_float_assumption():
    record = json.loads(MODULE["OUTPUT"].read_text(encoding="utf-8"))
    config = MODULE["replace"](MODULE["natural_bridge_config"](), quadrature_order=256)
    for example in record["examples"]:
        actual = MODULE["thermal_stiffness"](example["T"], example["mu"], example["Phi_fixed"], config)
        assert actual == pytest.approx(example["reference"], rel=1e-7, abs=1e-10)


def test_moving_condensate_rejects_out_of_domain_gradient():
    with pytest.raises(ValueError):
        MODULE["moving_energies"](.1, .5, .5, 1.05, .1085)
