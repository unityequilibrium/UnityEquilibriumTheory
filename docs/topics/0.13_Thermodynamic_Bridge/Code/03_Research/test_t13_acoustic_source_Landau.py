"""Off-shell Landau support/source and conditional energy-flux checks."""

import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

LOCAL = Path(__file__).resolve().parent
ROOT = LOCAL.parents[4]
M = runpy.run_path(str(LOCAL/"Research_T13_Acoustic_Source_Landau.py"))
MOD, TH, EFT, PAIR, PREFIX = M["MOD"], M["TH"], M["EFT"], M["PAIR"], M["PREFIX"]


@pytest.fixture
def example():
    action = EFT.controls()
    return EFT.tree_state(1.2, action=action), action


def test_flux_identity_derives_velocity_and_conditional_front_bound(example):
    state, action = example
    row = M["flux_bound"](.04, state, action)
    assert row["velocity_identity_error"] < 1e-9 and row["velocity_FD_error"] < 1e-6
    assert row["energy_minus_flux_identity_error"] < 1e-9 and row["mass_form"] >= 0
    assert 0 < row["v_flux"] < 1
    with pytest.raises(ValueError):
        M["flux_bound"](.04, state | {"V_curvature": .00001}, action)


@pytest.mark.parametrize("ratio", [.5, .9, 1.001])
def test_support_and_independent_angular_root(example, ratio):
    state, action = example
    q, omega = .02, ratio*TH.energy_value(.02, state, action)
    start = M["support_start"](q, omega, state, action)
    assert start["status"] == "SUPPORTED"
    p = start["p_min"]+.003
    r, cosine = M["landau_root"](q, p, omega, state, action)
    other, angular = M["angular_root"](q, p, omega, state, action)
    assert r == pytest.approx(other, rel=1e-10) and cosine == pytest.approx(angular, abs=1e-10)
    assert -1 < cosine < 1


def test_outside_front_support_is_not_a_thermal_cutoff_zero(example):
    state, action = example
    for omega in (.02, .04):
        result = M["landau_matrix"](.02, omega, .001, state, action)
        assert result["support"]["status"] == "NO_LANDAU_SUPPORT_CONDITIONAL_UNIT_FRONT_SPEED_BOUND"
        assert result["source_spectral_response"] is None and result["matrix"] is None


def test_on_shell_cut_projects_to_previous_modal_rate(example):
    state, action = example
    q, temperature = .04, .001
    energy = TH.energy_value(q, state, action)
    result = M["landau_matrix"](q, energy, temperature, state, action, on_shell=True)
    reference = 2*energy*MOD.cut_rate(q, temperature, state, action, "Landau")["gamma_pole"]
    assert result["modal_projection"] == pytest.approx(reference, rel=1e-6)


def test_Landau_source_is_positive_and_decoupling_and_zero_T_are_explicit(example):
    state, action = example
    q, omega = .02, .9*TH.energy_value(.02, state, action)
    result = M["landau_matrix"](q, omega, .001, state, action)
    assert result["source_spectral_response"] > 0
    assert result["decimal_gram_source"] == pytest.approx(result["source_spectral_response"], rel=1e-9)
    assert result["matrix"] == pytest.approx(result["matrix"].conjugate().T, abs=1e-12)
    zero = M["landau_matrix"](q, omega, 0., state, action)
    assert zero["source_spectral_response"] == 0 and zero["zero_T_limit"]
    other_action = action | {"gamma": 0.}
    other = EFT.tree_state(state["mu"], action=other_action)
    decoupled = M["landau_matrix"](q, .9*TH.energy_value(q, other, other_action), .001, other, other_action)
    assert decoupled["source_spectral_response"] == 0


def test_Phi_source_covariance_does_not_create_a_calibration(example):
    state, action = example
    q, omega = .02, .9*TH.energy_value(.02, state, action)
    reference = M["landau_matrix"](q, omega, .001, state, action)["source_spectral_response"]
    for scale in (.5, 2.):
        modified = EFT.rescale_Phi_coordinate(action, scale)
        other = EFT.tree_state(state["mu"], action=modified)
        assert M["landau_matrix"](q, omega, .001, other, modified)["source_spectral_response"] == pytest.approx(scale**2*reference, rel=1e-8)


def test_sound_lower_bound_is_consistent_with_the_same_schur_root(example):
    state, action = example
    c = M["INT"].dispersion_coefficients(state, action)["c"]
    for p in (.02, .04, .1):
        energy = TH.energy_value(p, state, action)
        mode = MOD.mode(p, state, action)
        a0 = M["INT"].dispersion_coefficients(state, action)["A0"]
        assert mode["den"] >= a0
        assert energy/p == pytest.approx((mode["den"]/(mode["den"]+4*state["mu"]**2))**.5, rel=1e-10)
        assert c <= energy/p < 1


def test_combined_window_does_not_invent_pair_support_or_full_retarded_acceptance():
    record = json.loads((ROOT/(PREFIX+"Result/artifacts/t13_acoustic_source_Landau.json")).read_text())
    for example in record["examples"]:
        for row in example["off_shell_Landau_rows"]:
            assert not row["combined_window_is_full_retarded_response"]
            assert row["combined_pair_Landau_source_response"] == row["pair_source_response"]+row["source_spectral_response"]
            if row["omega_over_Eq"] < 1:
                assert row["pair_source_response"] == 0 and row["pair_support_status"] == "NO_PAIR_SUPPORT_CONDITIONAL_Ep_GE_cp_BOUND"
            else:
                assert row["pair_source_response"] > 0 and row["pair_support_status"] == "PAIR_SUPPORT_EVALUATED_ABOVE_Eq"


@pytest.mark.parametrize("case", ["zero_frequency", "negative_T", "false_pole", "short_tail"])
def test_invalid_inputs_or_false_support_claim_rejected(example, case):
    state, action = example
    q, omega = .02, .9*TH.energy_value(.02, state, action)
    with pytest.raises(ValueError):
        M["landau_matrix"](q, 0. if case == "zero_frequency" else omega,
                           -.001 if case == "negative_T" else .001, state, action,
                           tail=8. if case == "short_tail" else 40., on_shell=case == "false_pole")


def test_artifact_and_hashes_do_not_promote_full_matching_or_physics():
    record = json.loads((ROOT/(PREFIX+"Result/artifacts/t13_acoustic_source_Landau.json")).read_text())
    assert all(record["checks"].values()) and record["verification_status"] == "PASS_SCOPED_LANDAU_SOURCE_INTERFACE"
    assert len(record["report"]) == 11 and record["thresholds"]["original_causal_leakage"] == 1e-6
    for key in ("full_off_shell_source_matching_closed", "full_real_self_energy_matched", "full_two_loop_pressure_computed",
                "all_parent_modes_and_quantum_Phi_loops_included", "full_SK_KMS_matching_closed", "physical_Kubo_emitted",
                "independent_alpha_Phi_K_admitted", "finite_thermal_tail_is_total_error_bound", "controlled_full_action_truncation_error_established",
                "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting", "assigned_width",
                "clipping", "cone_padding", "xie_2026_accessed"):
        assert record[key] is False
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
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
    result = M["audit"]()
    allowed = {(ROOT/x["path"]).resolve() for x in result["evidence_artifacts"]+result["protected_evidence_hashes"]}
    assert accessed and set(accessed) <= allowed and all("xie" not in p.name.lower() for p in accessed)
    assert all(result["checks"].values())
