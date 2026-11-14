"""Finite-pair work checks; no physical thermal or entropy admission."""

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pytest

LOCAL = Path(__file__).resolve().parent
if str(LOCAL) not in sys.path:
    sys.path.insert(0, str(LOCAL))
import Research_T13_Gaussian_Source_Work as W


@pytest.fixture(scope="module")
def setup():
    action = W.EFT.controls()
    return W.EFT.tree_state(1.2, action=action), action


@pytest.fixture(scope="module")
def artifact():
    return json.loads(W.OUTPUT.read_text(encoding="utf-8"))


@pytest.mark.parametrize("t", [-1., 0., W.DURATION, W.DURATION+1])
def test_analytic_compact_endpoints(t):
    assert np.array_equal(W.pulse_jet(t), np.zeros(8))


@pytest.mark.parametrize("t", [7., 19., 41., 73.])
def test_jet_matches_direct_pulse_and_time_derivative(t):
    assert W.pulse_jet(t)[0] == pytest.approx(np.sin(np.pi*t/W.DURATION)**8*np.cos(W.CARRIER*t), abs=1e-14)
    step = 1e-3
    numerical = (W.pulse_jet(t+step)[:-1]-W.pulse_jet(t-step)[:-1])/(2*step)
    assert np.linalg.norm(numerical-W.pulse_jet(t)[1:])/np.linalg.norm(W.pulse_jet(t)[1:]) < 1e-7


@pytest.mark.parametrize("nu", [0., .04, -.04, .3, 1.4, 2.7])
def test_fourier_is_independent_finite_interval_integral(nu):
    assert abs(W.pulse_fourier(nu)-W.pulse_fourier_quadrature(nu))/W.DURATION < W.GATES["fourier_absolute_scaled"]
    assert W.pulse_fourier(-nu) == pytest.approx(W.pulse_fourier(nu).conjugate(), abs=1e-14)


@pytest.mark.parametrize("q,nu", [(0., 0.), (0., .04), (.02, .01), (.02, .3), (.02, 1.4)])
def test_source_is_Phi_only_not_arbitrary_radial_forcing(setup, q, nu):
    state, action = setup
    b, h = W.source_fourier(nu, q, state, action)
    residual = W.VIRT.kernel(q, nu, state, action)@b-np.array([0., 0., h])
    assert np.linalg.norm(residual)/max(abs(h), np.linalg.norm(b), 1e-30) < 1e-9
    assert W.source_path(27., q, state, action)[3] < W.GATES["source_equation_relative"]


def test_canonical_poisson_map_and_stationary_covariance(setup):
    state, action = setup
    k, g, v, c, poisson, canonical = W.pair_hamiltonian(.02, .031, .004, state, action)
    generator = np.block([[np.zeros((6, 6)), np.eye(6)], [-np.linalg.solve(k, v), -np.linalg.solve(k, g)]])
    assert np.linalg.norm(generator@c+c@generator.T)/np.linalg.norm(c) < 1e-10
    j = np.block([[np.zeros((6, 6)), np.eye(6)], [-np.eye(6), np.zeros((6, 6))]])
    assert W.VIRT.matrix_error(canonical@poisson@canonical.T, j) < 1e-12
    wrong = canonical.copy()
    wrong[6:, :6] *= -1
    assert W.VIRT.matrix_error(wrong@poisson@wrong.T, j) > .1
    assert np.linalg.matrix_rank(c) == 4


def test_frozen_audit_failure_is_not_relabelled_by_a_better_method(artifact):
    assert artifact["verification_status"] == "FAIL_SCOPED_GAUSSIAN_SOURCE_WORK"
    assert artifact["closure_level"] == "PARTIAL"
    assert len(artifact["examples"]) == 6
    assert len(artifact["checks"]) == 13
    assert not artifact["checks"]["leading_amplitude_limit"]
    assert not artifact["checks"]["source_cycle_resolution"]
    assert all(artifact["extended_leading_checks"].values())
    assert artifact["leading_work_identity_verified"]
    assert artifact["declared_protocol"]["locked_before_first_audit"]
    assert artifact["declared_protocol"]["amplitudes"] == list(W.AMPLITUDES)
    assert artifact["thresholds"] == W.GATES
    raw = json.loads(W.FIRST_FAILURE.read_text(encoding="utf-8"))
    assert raw["checks"] == artifact["checks"]
    assert raw["declared_protocol"] == artifact["declared_protocol"]
    assert raw["thresholds"] == artifact["thresholds"]


def test_real_pair_orientation_is_not_silently_half_the_Hamiltonian(artifact):
    assert artifact["declared_protocol"]["pair_orientation_factor"] == 2
    for row in artifact["examples"]:
        assert row["wrong_half_orientation_relative"] > W.GATES["negative_control_minimum"]
        accurate = row["extended_leading"]
        assert W.relative(accurate["time_convolution_work"]/2, accurate["modal_work"]) == pytest.approx(.5, abs=2e-6)
        assert row["extended_leading"]["method_relative"] < W.GATES["work_method_relative"]


def test_absorption_is_not_primary_covariance_entropy(artifact):
    assert not artifact["primary_covariance_entropy_defined"]
    assert artifact["full_rank_entropy_control_is_diagnostic_only"]
    assert not artifact["quantum_vacuum_population_added"]
    for row in artifact["examples"]:
        assert row["spectral"]["work"] > 0
        assert row["zero_temperature_work_absolute"] == 0
        assert not row["spectral"]["vacuum_plus_one_included"]
        for cycle in row["cycles"]:
            assert cycle["insertion_rank"] == cycle["evolved_insertion_rank"] == 4
            assert "UNDEFINED" in cycle["insertion_entropy"]
            assert abs(cycle["conditional_full_rank_entropy_change"]) < W.GATES["volume_entropy_absolute"]


def test_protected_sources_and_evidence_hashes_are_current(artifact):
    for item in artifact["evidence_artifacts"]+artifact["protected_evidence_hashes"]:
        assert hashlib.sha256((W.ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_registry_units_ontology_and_reporting(artifact):
    registry = json.loads((W.ROOT/W.REGISTRY).read_text(encoding="utf-8"))
    assert registry["branch_id"] == W.VIRT.BRANCH == artifact["branch_id"]
    assert [e["id"] for e in registry["entries"]] == artifact["equation_registry_ids"]
    for entry in registry["entries"]:
        for name in ("ontology", "units", "derivation_class", "observable", "data_role", "verification_status", "controlling_blocker", "claim_boundary"):
            assert entry[name]
    for key in ("full_core_unlock", "full_energy_exchange_ledger_closed", "full_collision_operator_computed", "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted", "full_SK_KMS_matching_closed", "core_composition_gate_overwritten", "parameter_fitting", "assigned_width", "assigned_relaxation_time", "clipping", "cone_padding", "xie_2026_accessed", "claim_promotion"):
        assert artifact[key] is False
    assert set(artifact["excluded_variables"]) == {"C", "UET_Pi", "R_gen", "R_obs"}
    assert artifact["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert len(artifact["report"]) == 11
    json.dumps(artifact, allow_nan=False)


def test_zero_temperature_is_not_vacuum_heating(setup):
    state, action = setup
    result = W.spectral_work(.02, .031, .02, 0., state, action)
    assert result["work"] == 0
    assert all(x["pair_work"] == x["number_work"] == 0 for x in result["channels"])


def test_extended_zero_amplitude_coefficient_is_not_a_fit(setup):
    state, action = setup
    result = W.extended_leading_work(.02, .031, .02, .004, state, action, 35)
    assert result["time_convolution_work"] > 0
    assert result["method_relative"] < W.GATES["work_method_relative"]
    assert not result["finite_amplitude_fit_used"]


def test_audit_reads_only_declared_evidence_not_holdout(monkeypatch, artifact):
    allowed = {W.ROOT/x["path"] for x in artifact["evidence_artifacts"]+artifact["protected_evidence_hashes"]+artifact["preserved_first_failure_identity"]}
    seen = set()
    original_bytes, original_text = Path.read_bytes, Path.read_text

    def read_bytes(path):
        assert path in allowed
        seen.add(path)
        return original_bytes(path)

    def read_text(path, *args, **kwargs):
        assert path in allowed
        seen.add(path)
        return original_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    monkeypatch.setattr(Path, "read_text", read_text)
    fresh = W.audit()
    assert fresh["checks"] == artifact["checks"]
    assert fresh["extended_leading_checks"] == artifact["extended_leading_checks"]
    assert fresh["zero_drive_control"]["work"] == 0
    assert not fresh["zero_drive_drift_subtracted_from_work"]
    assert seen == allowed


@pytest.mark.parametrize("duration,carrier", [(0., .04), (-1., .04), (80., -.1), (float("nan"), .04)])
def test_bad_source_protocol_is_rejected(duration, carrier):
    with pytest.raises(ValueError):
        W.tones(duration, carrier)


@pytest.mark.parametrize("q,nu", [(-1., .04), (.02, float("nan"))])
def test_bad_fourier_source_inputs(setup, q, nu):
    state, action = setup
    with pytest.raises(ValueError):
        W.source_fourier(nu, q, state, action)


def test_decoupled_source_requires_separate_branch(setup):
    state, action = setup
    with pytest.raises(ValueError):
        W.source_path(20., .02, state, {**action, "gamma": 0.})


def test_source_work_geometry_rejected(setup):
    state, action = setup
    with pytest.raises(ValueError):
        W.spectral_work(.02, .031, 0., .004, state, action)
