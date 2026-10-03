"""Finite-q response must recover static population without invented collisions."""

import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

LOCAL = Path(__file__).resolve().parent
ROOT = LOCAL.parents[4]
M = runpy.run_path(str(LOCAL/"Research_T13_Finite_Q_Thermal_Source.py"))
EFT, VIRT, CURV, PREFIX = M["EFT"], M["VIRT"], M["CURV"], M["PREFIX"]


@pytest.fixture
def example():
    action = EFT.controls()
    return EFT.tree_state(1.2, action=action), action


@pytest.mark.parametrize("p,r,q", M["MOMENTUM_TRIPLES"])
def test_cross_covariance_uses_both_populations_and_physical_triangle(example, p, r, q):
    state, action = example
    assert abs(p-r) < q < p+r
    z, temperature = .05j, M["COVARIANCE_TEMPERATURE"]
    bubble = M["paired_bubble"](p, r, z, temperature, state, action)
    covariance = M["cross_covariance_bubble"](p, r, z, temperature, state, action)
    assert VIRT.matrix_error(bubble, covariance) < 1e-7
    assert VIRT.matrix_error(bubble.T, M["paired_bubble"](p, r, -z, temperature, state, action)) < 1e-9
    left, right = M["source_response"](q, -z, state, action), M["source_response"](q, z, state, action)
    assert left@bubble@right == pytest.approx(left@covariance@right, rel=1e-7)


def test_batched_angular_inverse_matches_direct_geometry_loop(example):
    state, action = example
    p, q, z = .02, .005, .03+.02j
    angles, weights = np.polynomial.legendre.leggauss(16)
    expected = sum(weight*M["insertion"](p, np.sqrt((p-q)**2+2*p*q*(1+cosine)), z, state, action)/2
                   for cosine, weight in zip(angles, weights))
    assert VIRT.matrix_error(expected, M["angular_insertion"](p, q, z, state, action, angles, weights)) < 1e-9


def test_batched_exact_modes_and_static_channels_match_scalar_without_reduced_grid(example):
    state, action = example
    p, q, temperature = .02, .02, .004
    momenta = np.array([1e-7, .001, .005, .02, .031, .039])
    energies, units = M["QUAD"].tree_modes_batch(momenta, state, action)
    for r, es, us in zip(momenta, energies, units):
        for (energy, unit), e, u in zip(VIRT.tree_modes(float(r), state, action), es, us):
            assert e == pytest.approx(energy, rel=1e-9)
            assert VIRT.matrix_error(np.outer(unit, unit.conjugate()), np.outer(u, u.conjugate())) < 1e-9
    vertex, _ = M["static_vertex"](q, state, action)
    batch = M["QUAD"].static_channels_batch(p, momenta, vertex, temperature, state, action, VIRT.tree_modes(p, state, action))
    for i, r in enumerate(momenta):
        expected = M["static_channels"](p, float(r), q, temperature, state, action)
        for key in batch:
            assert batch[key][i] == pytest.approx(expected[key], rel=1e-9)


def test_Bose_divided_difference_is_finite_symmetric_and_has_derivative_limit():
    energy, temperature = .007, .004
    n = M["TH"].bose(energy/temperature)
    expected = n*(1+n)/temperature
    assert M["bose_divided_difference"](energy, energy, temperature) == pytest.approx(expected, rel=1e-14)
    for step in (1e-4, 1e-8, 1e-12):
        a = M["bose_divided_difference"](energy-step, energy+step, temperature)
        assert a == M["bose_divided_difference"](energy+step, energy-step, temperature)
        assert a > 0
    assert M["bose_divided_difference"](energy, energy+1e-12, temperature) == pytest.approx(expected, rel=1e-8)


def test_static_diagonal_recovers_population_and_virtual_completion(example):
    state, action = example
    p, temperature = .02, .004
    channels = M["static_channels"](p, p, 0., temperature, state, action)
    jets = CURV.energy_jets(p, state, action)
    n = M["TH"].bose(jets["E"]/temperature)
    completion = VIRT.static_completion(p, state, action)
    assert channels["intrabranch_population"] == pytest.approx(n*(1+n)*jets["E_h"]**2/temperature, rel=1e-9)
    assert channels["pair"]+channels["mixed_number"] == pytest.approx(n*(completion["pair_per_n"]+sum(completion["mixed_per_n"])), rel=1e-9)


def test_finite_q_static_phase_entry_is_exact_radial_equation_not_mass_repair(example):
    state, action = example
    q = .002
    vertex, source = M["static_vertex"](q, state, action)
    expected = -q*q*source[0]/np.sqrt(state["s"])
    raw = np.einsum("ijk,k->ij", M["MOD"].cubic_tensor(state, action), source)
    assert vertex[1, 1] == expected
    assert raw == pytest.approx(vertex, rel=1e-8, abs=1e-12)
    assert np.linalg.norm(VIRT.kernel(q, 0., state, action)@source-np.array([0., 0., 1.])) < 1e-9


def test_tree_source_obeys_continuity_not_homogeneous_fixed_mu_limit(example):
    state, action = example
    q, z = .005, .02j
    source = M["source_response"](q, z, state, action)
    density = 2*state["mu"]*source[0]-1j*z*source[1]
    assert abs(-1j*z*density+q*q*source[1]) < 1e-9
    assert abs(density) > 0
    assert M["source_response"](0., z, state, action) == pytest.approx(VIRT.source_response(z, state, action), rel=1e-10)


def test_q0_thermal_static_and_dynamic_recover_previous_prescription(example):
    state, action = example
    temperature, z = .001, .05j
    static = M["static_thermal"](0., temperature, state, action, order=24, angular_order=32)
    target = CURV.thermal_response(temperature, state, action, order=24)
    assert static["chi"] == pytest.approx(target["chi_thermal"], rel=1e-6)
    dynamic = M["dynamic_thermal"](0., z, temperature, state, action, order=24, angular_order=32)
    assert dynamic == pytest.approx(VIRT.dynamic_thermal(z, temperature, state, action, order=24), rel=1e-9)


def test_zero_temperature_and_coordinate_rescaling_are_not_transport_inputs(example):
    state, action = example
    assert M["dynamic_thermal"](.005, .05j, 0., state, action) == 0j
    assert all(x == 0 for x in M["static_thermal"](.005, 0., state, action).values())
    q, z = .005, .05j
    first = M["source_response"](q, z, state, action)
    modified = EFT.rescale_Phi_coordinate(action, 2.)
    other = EFT.tree_state(state["mu"], action=modified)
    second = M["source_response"](q, z, other, modified)
    assert second[2] == pytest.approx(4*first[2], rel=1e-9)
    reference = M["static_channels"](.02, .031, q, .004, state, action)
    rescaled = M["static_channels"](.02, .031, q, .004, other, modified)
    for key in reference:
        assert rescaled[key] == pytest.approx(4*reference[key], rel=1e-8)


def test_decoupled_source_has_zero_thermal_response_without_calibration(example):
    state, action = example
    modified = action | {"gamma": 0.}
    other = EFT.tree_state(state["mu"], action=modified)
    assert all(x == 0 for x in M["static_channels"](.02, .031, .02, .004, other, modified).values())
    assert abs(M["dynamic_thermal"](.005, .05j, .001, other, modified, order=12, angular_order=16)) < 1e-15


@pytest.mark.parametrize("case", ["negative_q", "real_frequency", "negative_T", "short_tail", "zero_energy", "moving"])
def test_unadmitted_domain_rejected_not_clipped(example, case):
    state, action = example
    with pytest.raises(ValueError):
        if case == "negative_q":
            M["source_response"](-.01, .05j, state, action)
        elif case == "real_frequency":
            M["insertion"](.02, .031, .05, state, action)
        elif case == "zero_energy":
            M["bose_divided_difference"](0., .01, .004)
        elif case == "moving":
            M["source_response"](.005, .05j, EFT.tree_state(1.2, xi=.01, action=action), action)
        else:
            M["static_thermal"](.005, -.001 if case == "negative_T" else .001, state, action, tail=8. if case == "short_tail" else 40.)


def test_artifact_retains_collision_and_physical_boundaries():
    record = json.loads((ROOT/(PREFIX+"Result/artifacts/t13_finite_q_thermal_source.json")).read_text())
    assert record["verification_status"] == "PASS_SCOPED_FINITE_Q_THERMAL_SOURCE"
    assert all(record["checks"].values()) and len(record["report"]) == 11
    for key in ("assigned_relaxation_time", "full_collision_operator_computed", "physical_Kubo_emitted", "full_off_shell_source_matching_closed",
                "full_loop_source_current_Ward_closed", "full_energy_exchange_ledger_closed",
                "full_real_self_energy_matched", "full_two_loop_pressure_computed", "all_parent_modes_and_quantum_Phi_loops_included",
                "full_SK_KMS_matching_closed", "independent_alpha_Phi_K_admitted", "controlled_full_action_truncation_error_established",
                "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting", "assigned_width",
                "clipping", "cone_padding", "xie_2026_accessed"):
        assert record[key] is False
    assert record["thresholds"]["original_causal_leakage"] == 1e-6
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    registry = json.loads((ROOT/M["REGISTRY"]).read_text())
    assert all(item["verification_status"] == record["verification_status"] and item["controlling_blocker"] == record["controlling_blocker"] for item in registry["entries"])


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
