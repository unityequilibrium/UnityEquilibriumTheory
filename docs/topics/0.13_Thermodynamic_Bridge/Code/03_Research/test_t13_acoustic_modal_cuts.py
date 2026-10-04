"""Tree modal matching, independent potential/propagator and protected scope."""

import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

LOCAL = Path(__file__).resolve().parent
ROOT = LOCAL.parents[4]
M = runpy.run_path(str(LOCAL/"Research_T13_Acoustic_Modal_Cuts.py"))
TH, EFT, INT = M["TH"], M["EFT"], M["INT"]
PREFIX = M["PREFIX"]


@pytest.fixture
def example():
    action = EFT.controls()
    return EFT.tree_state(1.2, action=action), action


def test_parent_kernel_pole_and_symplectic_norm(example):
    state, action = example
    q = .01
    mode = M["mode"](q, state, action)
    u, omega = mode["polarization"], mode["omega"]
    assert np.max(abs(M["kernel"](q, omega, state, action)@u))/q**2 < 1e-9
    step = omega*1e-4
    derivative = (M["kernel"](q, omega+step, state, action)-M["kernel"](q, omega-step, state, action))/(2*step)
    assert -np.vdot(u, derivative@u)/(2*omega) == pytest.approx(1., abs=1e-10)
    assert M["residue_matrix_check"](q, state, action, .0001) < 1e-6
    negative = M["mode"](q, state, action, -1)
    assert negative["polarization"] == pytest.approx(u.conjugate())


def test_tensor_is_symmetric_and_independent_full_potential_derivative(example):
    state, action = example
    tensor = M["cubic_tensor"](state, action)
    assert tensor == pytest.approx(tensor.transpose(2, 1, 0))
    assert M["tensor_potential_check"](state, action, .005) < 1e-5


def test_projection_matches_raw_tensor_and_soft_EFT(example):
    state, action = example
    k, p = .01, .0037
    r, cosine = M["pair_root"](k, p, state, action)
    projected = M["amplitude"]((k, p, r), (1, -1, -1), state, action)
    raw = M["amplitude"]((k, p, r), (1, -1, -1), state, action, False)
    assert raw == pytest.approx(projected, rel=1e-7)
    lo = TH.vertex(*(TH.energy_value(q, state, action) for q in (k, p, r)), k, p, cosine, INT.vertices(state, action))
    assert abs(projected) == pytest.approx(abs(lo), rel=.005)


def test_projected_vertex_is_permutation_and_reality_covariant(example):
    state, action = example
    k, p = .01, .0037
    r, _ = M["pair_root"](k, p, state, action)
    base = M["amplitude"]((k, p, r), (1, -1, -1), state, action)
    assert M["amplitude"]((p, r, k), (-1, -1, 1), state, action) == pytest.approx(base, rel=1e-12)
    assert M["amplitude"]((k, p, r), (-1, 1, 1), state, action) == pytest.approx(base.conjugate(), rel=1e-12)


def test_Phi_coordinate_rescaling_keeps_modal_vertex(example):
    state, action = example
    k, p = .01, .0037
    r, _ = M["pair_root"](k, p, state, action)
    base = M["amplitude"]((k, p, r), (1, -1, -1), state, action)
    for scale in (.5, 2.):
        modified = EFT.rescale_Phi_coordinate(action, scale)
        other = EFT.tree_state(state["mu"], action=modified)
        assert M["mode"](k, other, modified)["Z_pi"] == pytest.approx(M["mode"](k, state, action)["Z_pi"], rel=1e-12)
        assert M["amplitude"]((k, p, r), (1, -1, -1), other, modified) == pytest.approx(base, rel=1e-10)


def test_decoupled_response_does_not_remove_matter_interaction(example):
    state, action = example
    action = action | {"gamma": 0.}
    state = EFT.tree_state(state["mu"], action=action)
    assert M["mode"](.01, state, action)["B"] == 0
    assert M["cut_rate"](.01, 0., state, action, "pair")["gamma_pole"] > 0
    assert M["cut_rate"](.01, 0., state, action, "Landau")["gamma_pole"] == 0


@pytest.mark.parametrize("case", ["zero_q", "nan_q", "bad_sign", "wrong_energy", "wrong_legs", "bad_channel", "negative_T"])
def test_invalid_inputs_and_nonconserved_vertex_rejected(example, case):
    state, action = example
    with pytest.raises(ValueError):
        if case == "zero_q":
            M["mode"](0., state, action)
        elif case == "nan_q":
            M["mode"](np.nan, state, action)
        elif case == "bad_sign":
            M["mode"](.01, state, action, 0)
        elif case == "wrong_energy":
            M["amplitude"]((.01, .006, .006), (1, -1, -1), state, action)
        elif case == "wrong_legs":
            M["amplitude"]((.01, .006), (1, -1), state, action)
        else:
            M["cut_rate"](.01, -.01 if case == "negative_T" else .01, state, action, "other" if case == "bad_channel" else "pair")


def test_artifact_hashes_and_scope_not_all_mode_quantum_closure():
    record = json.loads((ROOT/(PREFIX+"Result/artifacts/t13_acoustic_modal_cuts.json")).read_text())
    assert record["verification_status"] == "PASS_SCOPED_ACOUSTIC_MODAL_CUT"
    assert record["closure_level"] == "CLOSED_FOR_LANE" and all(record["checks"].values())
    assert len(record["report"]) == 11
    for key in ("all_parent_modes_and_quantum_Phi_loops_included", "full_off_shell_source_matching_closed", "full_real_self_energy_matched", "full_two_loop_pressure_computed", "full_finite_T_collision_operator_computed", "full_SK_KMS_matching_closed", "controlled_full_action_truncation_error_established", "independent_alpha_Phi_K_admitted", "physical_Kubo_emitted", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting", "assigned_damping_width", "clipping", "cone_padding", "target_source_accessed", "xie_2026_accessed"):
        assert record[key] is False
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert record["thresholds"]["original_causal_leakage"] == 1e-6
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
