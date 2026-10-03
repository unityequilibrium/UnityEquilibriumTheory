"""Independent limits and scope checks for the thermal phase cut diagnostic."""

import hashlib
import json
from math import pi, sqrt
from pathlib import Path
import runpy

import numpy as np
import pytest
from scipy.optimize import brentq

LOCAL = Path(__file__).resolve().parent
ROOT = LOCAL.parents[4]
M = runpy.run_path(str(LOCAL/"Research_T13_Thermal_Cut_Stiffness.py"))
EFT, INT, PREFIX = M["EFT"], M["INT"], M["PREFIX"]


@pytest.fixture
def example():
    action = EFT.controls()
    state = EFT.tree_state(1.2, action=action)
    return state, action


def test_Landau_energy_root_independent_angular_solution(example):
    state, action = example
    k, p = .0002, .003
    r, ep, er, cosine, residual = M["landau_root"](k, p, state, action)
    ek = EFT.acoustic_energy(k, state, action)
    angular = brentq(lambda z: EFT.acoustic_energy(sqrt(k*k+p*p-2*k*p*z), state, action)-ep-ek, -1., 1., xtol=1e-14)
    assert cosine == pytest.approx(angular, abs=1e-10)
    assert r > p and residual < 1e-10
    assert er == pytest.approx(ep+ek, rel=1e-12)


def test_cancellation_free_dispersion_is_same_parent_not_fitted_series(example):
    state, action = example
    assert M["energy_value"](0., state, action) == 0
    for q in (1e-5, .0001, .005, .1, .28):
        energy = M["energy_value"](q, state, action)
        assert energy == pytest.approx(EFT.acoustic_energy(q, state, action), rel=1e-12)
        assert abs(EFT.phase_inverse(q, energy, state, action))/q**2 < 1e-12


def test_mismatched_energy_does_not_pass_Bose_balance():
    for channel, er in (("pair", .8), ("Landau", 1.8)):
        weights = M["thermal_weights"](.7 if channel == "Landau" else .3, er, 1., 1., channel)
        assert weights["KMS_ratio_error"] > .01


@pytest.mark.parametrize("channel,ep,er", [("pair", .3, .7), ("Landau", .7, 1.7)])
def test_cut_Bose_detailed_balance_and_FDT(channel, ep, er):
    for temperature in (.01, .1, 1., 10.):
        weights = M["thermal_weights"](ep, er, 1., temperature, channel)
        assert weights["difference"] > 0
        assert max(weights["KMS_ratio_error"], weights["FDT_error"]) < 1e-12


def test_pair_zero_temperature_recovers_predecessor_and_occupation_factor_two(example):
    state, action = example
    rate = M["pair_rate"](.005, 0., state, action)
    previous = INT.decay_phase_space(.005, state, action)
    assert rate["gamma_pole"] == pytest.approx(previous["gamma_pole"], rel=1e-12)
    assert rate["Gamma_occupation"] == 2*rate["gamma_pole"]
    cold = M["pair_rate"](.005, 1e-8, state, action)
    assert cold["gamma_pole"] == pytest.approx(rate["gamma_pole"], rel=1e-9)
    assert M["landau_rate"](.005, 0., state, action)["gamma_pole"] == 0


def test_independent_Bose_moment_and_nonrelativistic_soft_control():
    mass, density, chi = 2., 3., 5.
    c = sqrt(density/(mass*chi))
    vv = {"g_t": 0., "g_s": 1/(2*mass*sqrt(chi))}
    expected = 3*pi**3/(40*mass*density*c**4)
    assert M["soft_landau_coefficient"](c, vv) == pytest.approx(expected, rel=1e-13)
    assert M["soft_landau_moment"](c, vv) == pytest.approx(expected, rel=1e-11)


def test_soft_limit_uses_internal_curvature_and_positive_supported_rate(example):
    state, action = example
    cf = INT.dispersion_coefficients(state, action)
    t = cf["c"]*cf["dispersion_scale"]/512
    k = .025*t/cf["c"]
    rate = M["landau_rate"](k, t, state, action)
    expected = M["soft_landau_coefficient"](cf["c"], INT.vertices(state, action))*k*t**4
    assert rate["gamma_pole"] == pytest.approx(expected, rel=M["GATES"]["soft_limit_relative"])
    assert rate["angular_support_margin_min"] > 0
    assert rate["Gamma_occupation"] == 2*rate["gamma_pole"]
    assert not rate["thermal_tail_is_total_EFT_error"]


def test_free_vertices_zero_attenuation_and_static_loop(example):
    state, action = example
    vv = {k: 0. for k in ("g_t", "g_s", "h_t", "h_m", "h_s")}
    assert M["pair_rate"](.005, .001, state, action, vv=vv)["gamma_pole"] == 0
    assert M["landau_rate"](.005, .001, state, action, vv=vv)["gamma_pole"] == 0
    assert M["static_coefficients"](.4, vv)["total"] == 0
    assert M["static_integrated"](.4, vv) == 0


def test_static_diagrams_match_pressure_and_need_bubble(example):
    state, action = example
    c, vv = INT.dispersion_coefficients(state, action)["c"], INT.vertices(state, action)
    static = M["static_coefficients"](c, vv)
    pressure = M["static_pressure_check"](state, action, .0001)
    assert static["total"] == pytest.approx(pressure, rel=2e-5)
    assert M["static_integrated"](c, vv) == pytest.approx(static["total"], rel=1e-10)
    assert M["static_pressure_analytic"](state, vv) == pytest.approx(static["total"], rel=1e-12)
    assert abs(static["tadpole"]-pressure)/abs(pressure) > .1


def test_Phi_coordinate_rescaling_preserves_thermal_response(example):
    state, action = example
    t, k = .001, .0001
    base = M["landau_rate"](k, t, state, action)
    base_static = M["static_coefficients"](INT.dispersion_coefficients(state, action)["c"], INT.vertices(state, action))
    for scale in (.5, 2.):
        other_action = EFT.rescale_Phi_coordinate(action, scale)
        other = EFT.tree_state(state["mu"], action=other_action)
        assert M["landau_rate"](k, t, other, other_action)["gamma_pole"] == pytest.approx(base["gamma_pole"], rel=1e-9)
        static = M["static_coefficients"](INT.dispersion_coefficients(other, other_action)["c"], INT.vertices(other, other_action))
        assert static["total"] == pytest.approx(base_static["total"], rel=1e-10)


@pytest.mark.parametrize("k,t,order,tail", [(0., .1, 48, 40.), (-.1, .1, 48, 40.), (.1, -.1, 48, 40.), (np.nan, .1, 48, 40.), (.1, np.nan, 48, 40.), (.1, .1, True, 40.), (.1, .1, 1, 40.), (.1, .1, 48, 16.), (.1, .1, 48, np.nan)])
def test_invalid_inputs_rejected(example, k, t, order, tail):
    with pytest.raises(ValueError):
        M["landau_rate"](k, t, *example, order=order, tail=tail)


def test_artifact_scope_and_hashes():
    record = json.loads((ROOT/(PREFIX+"Result/artifacts/t13_thermal_cut_stiffness.json")).read_text())
    assert record["verification_status"] == "PASS_SCOPED_THERMAL_CUT_STIFFNESS"
    assert all(record["checks"].values()) and len(record["report"]) == 11
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    for field in ("full_finite_T_collision_operator_computed", "higher_derivative_vertices_and_residues_matched", "full_real_self_energy_matched", "full_two_loop_pressure_computed", "full_SK_KMS_matching_closed", "controlled_full_action_truncation_error_established", "independent_alpha_Phi_K_admitted", "physical_Kubo_emitted", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting", "assigned_damping_width", "clipping", "cone_padding", "old_Hartree_branch_repaired", "target_source_accessed", "xie_2026_accessed"):
        assert record[field] is False
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert record["thresholds"]["original_causal_leakage"] == 1e-6
    assert "R_gen" in record["ontology"]["excluded_state_variables"]
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_runtime_read_allowlist_excludes_holdout(monkeypatch):
    accessed = []
    original_bytes, original_text = Path.read_bytes, Path.read_text
    def read_bytes(path):
        accessed.append(path.resolve())
        return original_bytes(path)
    def read_text(path, *args, **kwargs):
        accessed.append(path.resolve())
        return original_text(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    monkeypatch.setattr(Path, "read_text", read_text)
    record = M["audit"]()
    allowed = {(ROOT/item["path"]).resolve() for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]}
    assert accessed and set(accessed) <= allowed
    assert all("xie" not in path.name.lower() for path in accessed)
    assert all(record["checks"].values())
