"""Thermal source curvature is a matching target, not fitted dynamic contact."""

import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

LOCAL = Path(__file__).resolve().parent
ROOT = LOCAL.parents[4]
M = runpy.run_path(str(LOCAL/"Research_T13_Thermal_Source_Curvature.py"))
EFT, TH, INT, PREFIX = M["EFT"], M["TH"], M["INT"], M["PREFIX"]


@pytest.fixture
def example():
    action = EFT.controls()
    return EFT.tree_state(1.2, action=action), action


def test_stationary_source_jets_are_independent_of_detector_calibration(example):
    state, action = example
    jets = M["source_jets"](state, action)
    step = 1e-4
    states = [EFT.tree_state(state["mu"], h=h, action=action) for h in (-step, 0., step)]
    coordinates = [np.array([np.sqrt(s["s"]), 0., s["Phi"]]) for s in states]
    assert (coordinates[2]-coordinates[0])/(2*step) == pytest.approx(jets["first"], rel=1e-5, abs=1e-8)
    assert (coordinates[2]-2*coordinates[1]+coordinates[0])/step**2 == pytest.approx(jets["second"], rel=1e-4, abs=1e-7)
    assert jets["D_h"][1, 1] == jets["D_hh"][1, 1] == 0
    assert jets["stationary_Ward_cancellation"] < 1e-9


@pytest.mark.parametrize("p", [.005, .02, .04])
def test_energy_variation_and_Landau_vertex_agree_with_recomputed_states(example, p):
    state, action = example
    jets = M["energy_jets"](p, state, action)
    step = 1e-4
    minus, plus = [TH.energy_value(p, EFT.tree_state(state["mu"], h=h, action=action), action) for h in (-step, step)]
    assert jets["E_h"] == pytest.approx((plus-minus)/(2*step), rel=1e-4)
    assert jets["E_hh"] == pytest.approx((plus-2*jets["E"]+minus)/step**2, rel=1e-4)
    assert max(jets["vertex_derivative_error"], jets["mode_norm_error"], jets["kernel_derivative_residual"]) < 1e-9


def test_stationary_kernel_derivatives_match_independent_action_states(example):
    state, action = example
    jets = M["source_jets"](state, action)
    step, p, omega = 1e-4, .02, .003
    matrices = [M["MOD"].kernel(p, omega, EFT.tree_state(state["mu"], h=h, action=action), action) for h in (-step, 0., step)]
    assert (matrices[2]-matrices[0])/(2*step) == pytest.approx(jets["D_h"], rel=1e-4, abs=1e-8)
    assert (matrices[2]-2*matrices[1]+matrices[0])/step**2 == pytest.approx(jets["D_hh"], rel=1e-4, abs=1e-7)


def test_raw_small_momentum_cancellation_is_visible_not_a_relaxed_gate(example):
    state, action = example
    jets = M["energy_jets"](1e-7, state, action)
    assert jets["raw_source_contraction_error"] > 1e-8
    assert max(jets["vertex_derivative_error"], jets["mode_norm_error"], jets["kernel_derivative_residual"]) < 1e-9


def test_pressure_source_hessian_uses_common_fixed_momentum_domain(example):
    state, action = example
    temperature = .001
    result = M["thermal_response"](temperature, state, action)
    step = 1e-4
    minus, zero, plus = [M["pressure_at_source"](h, temperature, state, action, order=48) for h in (-step, 0., step)]
    assert result["thermal_Phi"] == pytest.approx((plus-minus)/(2*step), rel=1e-4)
    assert result["chi_thermal"] == pytest.approx((plus-2*zero+minus)/step**2, rel=1e-4)


def test_population_and_pair_do_not_replace_actual_source_curvature(example):
    state, action = example
    result = M["thermal_response"](.001, state, action)
    assert result["chi_population"] > 0 and result["chi_pair_static"] > 0
    assert result["chi_thermal"] == result["chi_population"]+result["chi_energy_curvature"]
    assert result["required_additional_static_matching"] == result["chi_pair_static"]-result["chi_energy_curvature"]
    assert result["missing_curvature_fraction"] > .01
    assert result["acoustic_cut_only_relative_mismatch"] > .01


def test_curvature_decomposition_is_derived_not_an_assigned_static_contact(example):
    state, action = example
    result = M["thermal_response"](.001, state, action)
    terms = [result[name] for name in ("chi_seagull_background", "chi_kinematic", "chi_virtual_polarization")]
    assert sum(terms) == pytest.approx(result["chi_energy_curvature"], rel=1e-9)
    assert all(abs(term) > 0 for term in terms)
    assert result["curvature_decomposition_error"] < 1e-9


def test_free_and_zero_temperature_limits_do_not_create_matching_input(example):
    state, action = example
    assert all(value == 0 for value in M["thermal_response"](0., state, action).values())
    decoupled_action = action | {"gamma": 0.}
    other = EFT.tree_state(state["mu"], action=decoupled_action)
    result = M["thermal_response"](.001, other, decoupled_action)
    assert result["chi_thermal"] == result["required_additional_static_matching"] == 0.
    assert result["pressure"] > 0


def test_source_coordinate_covariance_is_not_kelvin_mapping(example):
    state, action = example
    reference = M["thermal_response"](.001, state, action)
    for scale in (.5, 2.):
        modified = EFT.rescale_Phi_coordinate(action, scale)
        other = EFT.tree_state(state["mu"], action=modified)
        result = M["thermal_response"](.001, other, modified)
        assert result["pressure"] == pytest.approx(reference["pressure"], rel=1e-10)
        for name in ("chi_thermal", "chi_population", "chi_pair_static", "required_additional_static_matching"):
            assert result[name] == pytest.approx(scale**2*reference[name], rel=1e-8)


@pytest.mark.parametrize("case", ["negative_T", "short_tail", "zero_p", "moving_state"])
def test_invalid_or_unadmitted_source_domain_is_rejected(example, case):
    state, action = example
    with pytest.raises(ValueError):
        if case == "zero_p":
            M["energy_jets"](0., state, action)
        elif case == "moving_state":
            M["source_jets"](EFT.tree_state(1.2, xi=.01, action=action), action)
        else:
            M["thermal_response"](-.001 if case == "negative_T" else .001, state, action, tail=8. if case == "short_tail" else 40.)


def test_artifact_preserves_matching_and_physics_boundaries():
    record = json.loads((ROOT/(PREFIX+"Result/artifacts/t13_thermal_source_curvature.json")).read_text())
    assert all(record["checks"].values())
    assert record["verification_status"] == "PASS_SCOPED_THERMAL_SOURCE_CURVATURE"
    assert len(record["report"]) == 11
    assert record["thresholds"]["original_causal_leakage"] == 1e-6
    for name in ("full_off_shell_source_matching_closed", "full_real_self_energy_matched", "dynamic_contact_fixed_from_static_residual",
                 "full_two_loop_pressure_computed", "all_parent_modes_and_quantum_Phi_loops_included", "full_SK_KMS_matching_closed",
                 "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted", "controlled_full_action_truncation_error_established",
                 "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting", "assigned_width",
                 "clipping", "cone_padding", "xie_2026_accessed"):
        assert record[name] is False
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_audit_time_path_read_allowlist_excludes_holdout(monkeypatch):
    accessed = []
    read_bytes, read_text = Path.read_bytes, Path.read_text
    def tracked_bytes(path):
        accessed.append(path.resolve())
        return read_bytes(path)
    def tracked_text(path, *args, **kwargs):
        accessed.append(path.resolve())
        return read_text(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_bytes", tracked_bytes)
    monkeypatch.setattr(Path, "read_text", tracked_text)
    record = M["audit"]()
    allowed = {(ROOT/x["path"]).resolve() for x in record["evidence_artifacts"]+record["protected_evidence_hashes"]}
    assert accessed and set(accessed) <= allowed
    assert all("xie" not in p.name.lower() for p in accessed) and all(record["checks"].values())
