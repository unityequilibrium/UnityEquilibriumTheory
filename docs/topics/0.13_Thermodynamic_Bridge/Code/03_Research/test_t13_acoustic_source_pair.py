"""Source susceptibility, pair optical projection and bounded evidence."""

import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

LOCAL = Path(__file__).resolve().parent
ROOT = LOCAL.parents[4]
M = runpy.run_path(str(LOCAL/"Research_T13_Acoustic_Source_Pair.py"))
MOD, TH, EFT, PREFIX = M["MOD"], M["TH"], M["EFT"], M["PREFIX"]


@pytest.fixture
def example():
    action = EFT.controls()
    return EFT.tree_state(1.2, action=action), action


def test_schur_source_is_original_matrix_and_static_derivative(example):
    state, action = example
    q = .02
    omega = 1.5*TH.energy_value(q, state, action)
    actual = np.linalg.inv(MOD.kernel(q, omega, state, action))[2, 2]
    assert actual == pytest.approx(M["source_schur"](q, omega, state, action), rel=1e-10)
    assert M["static_source_derivative"](state, action, 2.5e-5) < 1e-5


def test_pair_gram_projection_reproduces_modal_decay(example):
    state, action = example
    q = .04
    energy = TH.energy_value(q, state, action)
    result = M["pair_matrix"](q, energy, 0., state, action, 48, True)
    reference = 2*energy*MOD.cut_rate(q, 0., state, action, "pair", 48)["gamma_pole"]
    assert result["modal_projection"] == pytest.approx(reference, rel=1e-6)


def test_off_shell_source_and_matrix_are_positive(example):
    state, action = example
    q = .02
    result = M["pair_matrix"](q, 1.5*TH.energy_value(q, state, action), .001, state, action)
    matrix = result["matrix"]
    assert matrix == pytest.approx(matrix.conjugate().T, abs=1e-12)
    assert np.linalg.eigvalsh(matrix)[0] >= -1e-12*np.linalg.norm(matrix)
    assert result["source_spectral_response"] > 0
    assert result["strict_support_margin"] > 0 and result["energy_residual"] < 1e-9


def test_decoupled_h_source_has_zero_pair_absorption(example):
    state, action = example
    action = action | {"gamma": 0.}
    state = EFT.tree_state(state["mu"], action=action)
    result = M["pair_matrix"](.02, 1.5*TH.energy_value(.02, state, action), 0., state, action)
    assert result["source_spectral_response"] == 0
    assert M["source_schur"](.02, .005, state, action) == pytest.approx(1/(state["V_curvature"]+action["epsilon"]*action["response_kinetic"]*(.02**2-.005**2)))


def test_source_response_is_covariant_not_coordinate_invariant(example):
    state, action = example
    q, omega = .02, 1.5*TH.energy_value(.02, state, action)
    base = M["pair_matrix"](q, omega, 0., state, action)
    for scale in (.5, 2.):
        modified = EFT.rescale_Phi_coordinate(action, scale)
        other = EFT.tree_state(state["mu"], action=modified)
        assert M["source_schur"](q, omega, other, modified) == pytest.approx(scale**2*M["source_schur"](q, omega, state, action), rel=1e-10)
        result = M["pair_matrix"](q, omega, 0., other, modified)
        assert result["source_spectral_response"] == pytest.approx(scale**2*base["source_spectral_response"], rel=1e-8)


def test_decimal_complex_gram_checks_phase_orientation_independently():
    vectors = [np.array([1+2j, 3-1j, -2+.5j]), np.array([-.4+1j, 2+.1j, .3-2j])]
    samples = list(zip((.7, 1.3), vectors))
    dressed = np.array([.3-2j, 1+.6j, -.9+1j])
    expected = sum(weight*abs(np.vdot(dressed, vector))**2 for weight, vector in samples)
    assert M["decimal_gram_source"](samples, dressed) == pytest.approx(expected, rel=1e-14)


@pytest.mark.parametrize("omega,flag", [(0., False), (float("nan"), False), (.001, False), (.02, True)])
def test_invalid_support_or_false_on_shell_flag_rejected(example, omega, flag):
    state, action = example
    with pytest.raises(ValueError):
        M["pair_matrix"](.02, omega, 0., state, action, on_shell=flag)


def test_artifact_is_hash_linked_without_physical_or_full_matching_acceptance():
    record = json.loads((ROOT/(PREFIX+"Result/artifacts/t13_acoustic_source_pair.json")).read_text())
    assert all(record["checks"].values())
    assert record["verification_status"] == "PASS_SCOPED_PAIR_SOURCE_INTERFACE"
    for key in ("full_off_shell_source_matching_closed", "full_real_self_energy_matched", "full_two_loop_pressure_computed",
                "all_parent_modes_and_quantum_Phi_loops_included", "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted",
                "full_SK_KMS_matching_closed", "parameter_fitting", "clipping", "cone_padding",
                "core_composition_gate_overwritten", "full_core_unlock", "claim_promotion", "xie_2026_accessed"):
        assert record[key] is False
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert len(record["report"]) == 11 and record["thresholds"]["original_causal_leakage"] == 1e-6
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
    assert accessed and set(accessed) <= allowed
    assert all("xie" not in p.name.lower() for p in accessed)
    assert all(result["checks"].values())
