"""Virtual/contact completion needs independent spectral and time-domain checks."""

import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

LOCAL = Path(__file__).resolve().parent
ROOT = LOCAL.parents[4]
M = runpy.run_path(str(LOCAL/"Research_T13_Thermal_Virtual_Response.py"))
EFT, CURV, PREFIX = M["EFT"], M["CURV"], M["PREFIX"]


@pytest.fixture
def example():
    action = EFT.controls()
    return EFT.tree_state(1.2, action=action), action


@pytest.mark.parametrize("mu", [1.05, 1.2])
def test_virtual_and_contact_terms_independently_complete_static_curvature(mu):
    action = EFT.controls()
    state = EFT.tree_state(mu, action=action)
    for p in M["MOMENTA"]:
        point = M["static_completion"](p, state, action)
        jets = CURV.energy_jets(p, state, action)
        assert point["nonpopulation_per_n"] == pytest.approx(-jets["E_hh"], rel=1e-9)
        assert all(x > 0 for x in point["mixed_per_n"])
        assert point["nonpopulation_per_n"] != pytest.approx(point["pair_per_n"], rel=.01)
        contact, force, shift = M["contact_matrix"](p, state, action)
        first = CURV.source_jets(state, action)["first"]
        assert M["decimal_contact_projection"](p, state, action) == pytest.approx(point["contact_per_n"], rel=1e-9)
        assert np.linalg.norm((M["LAND"].parent_mass_matrix(state, action)@shift+force)[[0, 2]]) < 1e-9


def test_mixed_completion_matches_independent_pressure_finite_difference(example):
    state, action = example
    temperature, step = .001, 1e-4
    point = M["thermal_completion"](temperature, state, action)
    minus, zero, plus = [CURV.pressure_at_source(h, temperature, state, action, order=48) for h in (-step, 0., step)]
    assert point["chi_completed"] == pytest.approx((plus-2*zero+minus)/step**2, rel=1e-4)
    assert point["matching_error"] < 1e-9


def test_first_binary64_contact_failure_remains_visible_not_a_looser_gate():
    action = EFT.controls()
    state = EFT.tree_state(1.05, action=action)
    p = .005
    first = CURV.source_jets(state, action)["first"]
    contact = M["contact_matrix"](p, state, action)[0]
    target = M["static_completion"](p, state, action)["contact_per_n"]
    assert M["INT"].relative(first@contact@first, target) > M["GATES"]["identity_relative"]
    assert M["INT"].relative(M["decimal_contact_projection"](p, state, action), target) < M["GATES"]["identity_relative"]


@pytest.mark.parametrize("z", M["FREQUENCIES"])
def test_real_time_covariance_checks_full_dynamic_source_not_static_residual(example, z):
    state, action = example
    p = .02
    inverse = M["insertion_bubble"](p, z, state, action)
    spectral = M["insertion_bubble"](p, z, state, action, spectral=True)
    covariance = M["covariance_bubble"](p, z, state, action)
    assert M["matrix_error"](inverse, spectral) < 1e-9
    assert M["matrix_error"](inverse, covariance) < 1e-7
    assert M["dynamic_point"](p, z, state, action) == pytest.approx(M["dynamic_point"](p, z, state, action, "covariance"), rel=1e-7)
    assert M["matrix_error"](inverse.T, M["insertion_bubble"](p, -z, state, action)) < 1e-9
    source = M["source_response"](z, state, action)
    assert abs(2*state["mu"]*source[0]-1j*z*source[1]) < 1e-9
    assert M["dynamic_point"](p, -z.conjugate(), state, action) == pytest.approx(M["dynamic_point"](p, z, state, action).conjugate(), rel=1e-9)


def test_tree_mode_completeness_not_heavy_thermal_population(example):
    state, action = example
    p, z = .02, .03+.02j
    modes = M["tree_modes"](p, state, action)
    assert len(modes) == 3 and modes[0][0] < modes[1][0] < modes[2][0]
    inverse = np.linalg.inv(M["kernel"](p, z, state, action))
    assert M["matrix_error"](inverse, M["spectral_propagator"](p, z, state, action, modes)) < 1e-9
    kinetic, linear, _ = M["matrices"](p, state, action)
    for energy, unit in modes:
        assert np.linalg.norm(M["kernel"](p, energy, state, action)@unit) < 1e-9
        assert -np.vdot(unit, (-2*energy*kinetic+linear)@unit).real == pytest.approx(2*energy, rel=1e-9)


def test_fixed_mu_static_is_not_q0_closed_charge_dynamic_limit(example):
    state, action = example
    static = M["source_response"](0, state, action, "grand_canonical_static")
    dynamic = M["source_response"](1e-5j, state, action)
    _, _, v0 = M["matrices"](0., state, action)
    expected = 1/(v0[2, 2]-v0[0, 2]**2/(v0[0, 0]+4*state["mu"]**2))
    assert dynamic[2].real == pytest.approx(expected, rel=1e-9)
    assert abs(static[2]-dynamic[2])/abs(static[2]) > .01
    assert abs(dynamic[1]) > 1


def test_zero_temperature_and_decoupling_create_no_calibration_or_width(example):
    state, action = example
    assert all(x == 0 for x in M["thermal_completion"](0., state, action).values())
    assert M["dynamic_thermal"](.05j, 0., state, action) == 0j
    decoupled = action | {"gamma": 0.}
    other = EFT.tree_state(state["mu"], action=decoupled)
    assert M["thermal_completion"](.001, other, decoupled)["chi_completed"] == 0
    assert abs(M["dynamic_point"](.02, .05j, other, decoupled)) < 1e-15


def test_coordinate_covariance_does_not_fix_kelvin_scale(example):
    state, action = example
    reference = M["dynamic_point"](.02, .05j, state, action)
    static = M["thermal_completion"](.001, state, action)["chi_completed"]
    for scale in (.5, 2.):
        modified = EFT.rescale_Phi_coordinate(action, scale)
        other = EFT.tree_state(state["mu"], action=modified)
        assert M["dynamic_point"](.02, .05j, other, modified) == pytest.approx(scale**2*reference, rel=1e-8)
        assert M["thermal_completion"](.001, other, modified)["chi_completed"] == pytest.approx(scale**2*static, rel=1e-8)


@pytest.mark.parametrize("case", ["real_frequency", "negative_p", "moving", "negative_T", "short_tail", "unknown_method", "unknown_ensemble"])
def test_unadmitted_domain_rejected_not_repaired(example, case):
    state, action = example
    with pytest.raises(ValueError):
        if case == "real_frequency":
            M["dynamic_point"](.02, .05, state, action)
        elif case == "negative_p":
            M["tree_modes"](-.02, state, action)
        elif case == "moving":
            M["matrices"](.02, EFT.tree_state(1.2, xi=.01, action=action), action)
        elif case == "unknown_method":
            M["dynamic_point"](.02, .05j, state, action, "assigned_contact")
        elif case == "unknown_ensemble":
            M["source_response"](.05j, state, action, "fitted")
        else:
            M["thermal_completion"](-.001 if case == "negative_T" else .001, state, action, tail=8. if case == "short_tail" else 40.)


def test_artifact_and_hashes_keep_full_physical_gates_closed():
    record = json.loads((ROOT/(PREFIX+"Result/artifacts/t13_thermal_virtual_response.json")).read_text())
    assert record["verification_status"] == "PASS_SCOPED_THERMAL_VIRTUAL_RESPONSE"
    assert all(record["checks"].values()) and len(record["report"]) == 11
    assert record["branch_id"] != record["parent_branch_id"]
    assert record["prescription"]["thermal_population"] == "acoustic only"
    for name in ("full_off_shell_source_matching_closed", "full_real_self_energy_matched", "dynamic_contact_fixed_from_static_residual",
                 "all_parent_modes_and_quantum_Phi_loops_included", "full_two_loop_pressure_computed", "full_SK_KMS_matching_closed",
                 "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted", "controlled_full_action_truncation_error_established",
                 "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting", "assigned_width",
                 "clipping", "cone_padding", "xie_2026_accessed"):
        assert record[name] is False
    assert record["thresholds"]["original_causal_leakage"] == 1e-6
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_audit_runtime_path_allowlist_does_not_read_holdout(monkeypatch):
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
    assert accessed and set(accessed) <= allowed and all(record["checks"].values())
    assert all("xie" not in x.name.lower() for x in accessed)
