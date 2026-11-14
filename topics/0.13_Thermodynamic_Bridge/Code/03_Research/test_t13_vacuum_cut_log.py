"""Cut, subtracted Cauchy reconstruction and restricted matching controls."""

import hashlib
import json
from math import pi, sqrt
from pathlib import Path
import runpy

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
M = runpy.run_path(str(ROOT/(PREFIX+"Code/03_Research/Research_T13_Vacuum_Cut_Log.py")))


@pytest.fixture(params=[1.05, 1.2])
def example(request):
    eft, interaction = M["EFT"], M["INT"]
    action = eft.controls()
    state = eft.tree_state(request.param, action=action)
    return interaction.dispersion_coefficients(state, action), interaction.vertices(state, action)


def test_independent_expanded_cut_polynomial(example):
    cf, v = example
    k2, z = .03, .05
    barred = v["g_s"]/cf["c"]**2
    g = v["g_t"]+barred
    s = z-k2
    expanded = z*(6*g*g*z*z/5+(3*g*g/5-4*g*barred)*z*s
                  +(9*g*g/20-2*g*barred+4*barred**2)*s*s)
    assert M["cut_polynomial"](k2, cf, v)(z) == pytest.approx(expanded, rel=1e-12)


def test_direct_original_vertex_cut_and_retarded_sign(example):
    cf, v = example
    q, omega = .01, .01*cf["c"]*1.2
    direct = M["direct_cut_phase_space"](omega, q, cf, v)
    imaginary = M["cut_imaginary"](omega, q, cf, v)
    sigma = M["retarded_real_frequency"](omega, q, cf, v)
    assert imaginary < 0
    assert direct["Im_Sigma"] == pytest.approx(imaginary, rel=1e-12)
    assert sigma.imag == pytest.approx(imaginary, rel=1e-12)
    assert direct["angular_support_margin_min"] > 0
    assert direct["energy_residual_max"] < 1e-12
    assert M["retarded_real_frequency"](-omega, q, cf, v) == sigma.conjugate()


def test_upper_half_frequency_limit_has_retarded_cut(example):
    cf, v = example
    q = .01
    omega = 1.2*cf["c"]*q
    target = M["retarded_real_frequency"](omega, q, cf, v)
    values = [M["nonlocal_z"]((omega+1j*omega*e)**2, q, cf, v) for e in (1e-4, 1e-6, 1e-8)]
    errors = [abs(x-target)/abs(target) for x in values]
    assert errors[2] < errors[1] < errors[0]
    assert errors[-1] < 1e-6


@pytest.mark.parametrize("ratio", [-.5, 0., .5, .5+.25j])
def test_subtracted_real_part_by_independent_cauchy_integral(example, ratio):
    cf, v = example
    q = .01
    z = ratio*(cf["c"]*q)**2
    integral = M["four_subtracted_dispersion"](z, q, cf, v)
    analytic = M["four_subtracted_analytic"](z, q, cf, v)
    assert integral["Sigma_subtracted"] == pytest.approx(analytic, rel=1e-8, abs=1e-30)


def test_scale_running_is_local_and_four_subtracted_part_invariant(example):
    cf, v = example
    q = .01
    k2 = (cf["c"]*q)**2
    z = .5*k2
    expected = -2*np.log(2)*M["cut_polynomial"](k2, cf, v)(z)/(32*pi*pi*cf["c"]**3)
    difference = M["nonlocal_z"](z, q, cf, v, 2)-M["nonlocal_z"](z, q, cf, v, 1)
    assert difference == pytest.approx(expected, rel=1e-12)
    assert M["four_subtracted_analytic"](z, q, cf, v, 2) == pytest.approx(
        M["four_subtracted_analytic"](z, q, cf, v, .5), rel=1e-10, abs=1e-30)


def test_threshold_optical_theorem_recovers_prior_width(example):
    cf, v = example
    q = .01
    omega = cf["c"]*q*sqrt(1+1e-6)
    coefficient = -M["cut_imaginary"](omega, q, cf, v)/(2*omega*q**5)
    assert coefficient == pytest.approx(M["INT"].decay_leading_coefficient(cf, v)/2, rel=2e-5)


def test_known_nonrelativistic_pole_width_not_occupation_width():
    mass, density, chi = 2.3, .8, 1.4
    c = sqrt(density/(mass*chi))
    q, offset = .01, 1e-7
    omega = c*q*sqrt(1+offset)
    cf, v = {"c": c}, {"g_t": 0., "g_s": 1/(2*mass*sqrt(chi))}
    actual = -M["cut_imaginary"](omega, q, cf, v)/(2*omega*q**5)
    assert actual == pytest.approx(3/(640*pi*mass*density), rel=2e-6)


def test_free_cubic_zero_loop_and_spacelike_zero_cut():
    cf, v = {"c": .4}, {"g_t": 0., "g_s": 0.}
    assert M["cut_imaginary"](.02, .01, cf, v) == 0
    assert M["nonlocal_z"](.0005j, .01, cf, v) == 0
    assert M["cut_imaginary"](.001, .01, cf, {"g_t": 1., "g_s": 1.}) == 0
    assert M["nonlocal_z"](0, 0, cf, v) == 0


def test_Phi_coordinate_rescaling_does_not_change_phase_loop(example):
    cf, v = example
    eft, interaction = M["EFT"], M["INT"]
    action = eft.controls()
    for factor in (.5, 2.):
        rescaled = eft.rescale_Phi_coordinate(action, factor)
        state = eft.tree_state(1.2, action=rescaled)
        modified_cf = interaction.dispersion_coefficients(state, rescaled)
        modified_v = interaction.vertices(state, rescaled)
        original_state = eft.tree_state(1.2, action=action)
        original_cf = interaction.dispersion_coefficients(original_state, action)
        original_v = interaction.vertices(original_state, action)
        z, q = .0003j, .01
        assert M["nonlocal_z"](z, q, modified_cf, modified_v) == pytest.approx(
            M["nonlocal_z"](z, q, original_cf, original_v), rel=1e-10)


def test_fixed_convention_rank_does_not_count_physical_parameters():
    information = M["matching_information"]()
    assert information["matrix_rank"] == 4
    assert information["leading_on_shell_rank"] == 1
    assert information["synthetic_algebra_witness_reconstruction_error"] < 1e-12
    assert not information["four_independent_physical_parameters_claimed"]
    assert not information["four_lab_measurements_required_claimed"]
    assert information["field_redefinition_and_source_contact_matching_required"]
    # z^2(z-K2) changes off-shell response, not the leading on-shell pole.
    assert M["local_degree_six"](.1, .1, [1., -1., 0., 0.]) == pytest.approx(0, abs=1e-18)
    assert M["local_degree_six"](.05, .1, [1., -1., 0., 0.]) != 0


def test_local_terms_leave_cut_unchanged_but_real_response_not_unique(example):
    cf, v = example
    q, omega = .01, .012*cf["c"]
    k2 = (cf["c"]*q)**2
    base = M["retarded_real_frequency"](omega, q, cf, v)
    shifted = base+M["local_degree_six"](omega**2, k2, [0., 0., 0., .5/cf["c"]**6])
    assert shifted.imag == base.imag
    assert shifted.real != base.real
    assert shifted.real-base.real == pytest.approx(.5*q**6, rel=1e-10)


@pytest.mark.parametrize("case", ["threshold", "zero_q_subtraction", "nan_frequency", "negative_q", "zero_c", "nan_cubic", "nan_tolerance", "negative_scale", "on_cut_integral", "nan_z", "invalid_local"])
def test_invalid_or_unclosed_prescriptions_are_rejected(case):
    cf, v = {"c": .4}, {"g_t": .1, "g_s": .2}
    with pytest.raises(ValueError):
        if case == "threshold":
            M["retarded_real_frequency"](.4*.01, .01, cf, v)
        elif case == "zero_q_subtraction":
            M["four_subtracted_analytic"](.1, 0, cf, v)
        elif case == "nan_frequency":
            M["cut_imaginary"](float("nan"), .01, cf, v)
        elif case == "negative_q":
            M["cut_imaginary"](.1, -.01, cf, v)
        elif case == "zero_c":
            M["cut_polynomial"](.1, {"c": 0}, v)
        elif case == "nan_cubic":
            M["cut_polynomial"](.1, cf, v | {"g_t": float("nan")})
        elif case == "nan_tolerance":
            M["four_subtracted_dispersion"](-.1, .01, cf, v, float("nan"))
        elif case == "negative_scale":
            M["four_subtracted_analytic"](-.1, .01, cf, v, -1)
        elif case == "on_cut_integral":
            M["four_subtracted_dispersion"](.1, .01, cf, v)
        elif case == "nan_z":
            M["four_subtracted_dispersion"](complex(float("nan")), .01, cf, v)
        else:
            M["local_degree_six"](.1, .1, [1., 2.])


def test_artifact_hashes_and_no_physical_or_holdout_unlock():
    r = json.loads((ROOT/(PREFIX+"Result/artifacts/t13_vacuum_cut_log.json")).read_text())
    assert r["verification_status"] == "PASS_SCOPED_VACUUM_CUT_LOG"
    assert all(r["checks"].values()) and len(r["report"]) == 11
    assert r["closure_level"] == "CLOSED_FOR_LANE"
    for name in ("local_Wilson_matching_completed", "internal_curvature_real_self_energy_computed", "full_real_self_energy_matched", "full_two_loop_pressure_computed", "finite_T_collision_computed", "full_SK_KMS_matching_closed", "controlled_full_action_truncation_error_established", "independent_alpha_Phi_K_admitted", "physical_Kubo_emitted", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting", "assigned_damping_width", "clipping", "cone_padding", "old_Hartree_branch_repaired", "target_source_accessed", "xie_2026_accessed", "formal_UV_integral_is_physical_EFT_validity"):
        assert r[name] is False
    assert r["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert r["thresholds"]["original_causal_leakage"] == 1e-6
    assert "R_gen" in r["ontology"]["excluded_state_variables"]
    for item in r["evidence_artifacts"]+r["protected_evidence_hashes"]:
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_runtime_file_allowlist_excludes_holdout(monkeypatch):
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
