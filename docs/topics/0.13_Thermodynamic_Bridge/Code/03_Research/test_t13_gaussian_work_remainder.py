"""Scope, parity, known-tail and provenance checks for the finite-pair result."""

import hashlib
import json
from pathlib import Path
import sys

import mpmath as mp
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import Research_T13_Gaussian_Work_Remainder as R


@pytest.fixture(scope="module")
def artifact():
    return json.loads(R.OUTPUT.read_text(encoding="utf-8"))


def test_predecessor_failure_is_unchanged():
    old = R.load_predecessor()
    assert old["closure_level"] == "PARTIAL"
    assert not all(old["checks"].values())
    assert old["declared_protocol"]["amplitudes"] == list(R.WORK.AMPLITUDES)


@pytest.mark.parametrize("order", [0, 2, 4, 6, 8])
def test_positive_even_tail_against_independent_cosh(order):
    with mp.workdps(80):
        x = mp.mpf(".4")
        expected = 3*(mp.cosh(x)-sum(x**n/mp.factorial(n) for n in range(0, order+1, 2)))
    result = R.even_remainder(3., 2., .1, order)
    assert result["value"] == pytest.approx(float(expected), rel=1e-13)
    assert not result["overflow_in_binary64"]


def test_tiny_tail_does_not_subtract_near_equal_floats():
    value = R.even_remainder(1., 1., 1e-15, 2)["value"]
    assert value == pytest.approx((2e-15)**4/24, rel=1e-13, abs=0)
    assert value > 0


@pytest.mark.parametrize("args", [(-1, 1, .1, 2), (1, -1, .1, 2), (1, 1, float("nan"), 2), (1, 1, .1, 3), (1, 1, .1, -2)])
def test_reject_invalid_bound_inputs(args):
    with pytest.raises(ValueError):
        R.even_remainder(*args)


def test_bound_parity_zero_and_overflow():
    assert R.even_remainder(1, 1, .2, 6) == R.even_remainder(1, 1, -.2, 6)
    assert R.even_remainder(1, 0, .2, 6)["value"] == 0
    overflow = R.even_remainder(1, 1000, 1, 6)
    assert overflow["value"] is None and overflow["overflow_in_binary64"]
    assert overflow["log10_value"] > 308


def test_missing_factor_two_fails_saturating_control():
    correct = R.even_remainder(1, 1, .1, 2)["value"]
    wrong = R.even_remainder(1, .5, .1, 2)["value"]
    assert R.WORK.relative(correct, wrong) > R.GATES["negative_control_minimum"]


def test_sufficient_domain_bounds_relative_linear_error():
    limit = R.sufficient_linear_amplitude(3, 2, .001)["amplitude_upper_evaluated"]
    assert 2*limit*2 <= 1
    tail = R.even_remainder(3, 2, limit, 2)["value"]
    assert tail <= R.GATES["linear_relative_tolerance"]*.001*limit**2
    assert not R.sufficient_linear_amplitude(3, 2, .001)["numeric_interval_certificate"]


@pytest.mark.parametrize("args", [(0, 1, 1), (1, 0, 1), (1, 1, -1)])
def test_reject_nonpositive_linear_certificate_inputs(args):
    with pytest.raises(ValueError):
        R.sufficient_linear_amplitude(*args)


def test_prediction_uses_independent_leading_not_binary64_coefficient():
    coefficients = [{"order": 2, "work_coefficient": -999}, {"order": 4, "work_coefficient": 3}, {"order": 6, "work_coefficient": 4}]
    assert R.prediction(2, coefficients, .1) == pytest.approx(.02+.0003+.000004)
    assert R.prediction(2, coefficients, .1) == R.prediction(2, coefficients, -.1)


def test_tones_reconstruct_prescribed_source_vertex():
    action = R.EFT.controls()
    state = R.EFT.tree_state(R.WORK.MU_GRID[0], action=action)
    q = R.WORK.MOMENTUM_TRIPLES[0][2]
    cubic = R.MOD.cubic_tensor(state, action)
    for t in (0., 5., 23., 40., R.WORK.DURATION):
        b = R.WORK.source_path(t, q, state, action)[0]
        direct = np.einsum("ijk,k->ij", cubic, b)
        tones = sum(R.tone_vertex(c/2, nu, q, state, action)*np.exp(-1j*nu*t)
                    for c, freq in R.WORK.tones() for nu in (freq, -freq))
        assert np.linalg.norm(tones-direct) < 1e-11


def test_known_hyperbolic_covariance_control():
    from scipy.linalg import expm
    amplitude, eta = .1, 1.
    generator = np.array([[0., 1.], [1., 0.]])
    flow = expm(amplitude*eta*generator)
    energy_gain = .5*np.trace(flow@flow.T)-1
    series = 2*amplitude**2+R.even_remainder(1, eta, amplitude, 2)["value"]
    assert energy_gain == pytest.approx(series, rel=1e-12)


def test_artifact_status_tracks_all_checks(artifact):
    passed = all(artifact["checks"].values())
    assert artifact["finite_pair_even_work_hierarchy_verified"] is passed
    assert artifact["closure_level"] == ("CLOSED_FOR_LANE" if passed else "PARTIAL")
    assert artifact["verification_status"] == ("PASS_SCOPED_GAUSSIAN_WORK_REMAINDER" if passed else "FAIL_SCOPED_GAUSSIAN_WORK_REMAINDER")


@pytest.mark.parametrize("field", ["old_source_work_audit_promoted", "useful_linear_certificate_on_original_grid", "numeric_bound_interval_certified", "full_energy_exchange_ledger_closed", "nonlinear_parent_action_completed", "physical_Kubo_emitted", "full_SK_KMS_matching_closed", "independent_alpha_Phi_K_admitted", "controlled_full_action_truncation_error_established", "full_core_unlock", "core_composition_gate_overwritten", "parameter_fitting", "assigned_relaxation_time", "quantum_vacuum_population_added", "clipping", "cone_padding", "claim_promotion", "xie_2026_accessed"])
def test_no_physical_or_old_failure_promotion(artifact, field):
    assert artifact[field] is False


def test_frozen_grid_and_higher_order_diagnostics(artifact):
    assert len(artifact["examples"]) == 6
    for row in artifact["examples"]:
        assert [c["order"] for c in row["hierarchy"]["coefficients"]] == [2, 4, 6]
        assert [c["amplitude"] for c in row["comparisons"]] == list(R.WORK.AMPLITUDES)
        assert not row["hierarchy"]["finite_amplitude_fit_used"]
        assert not row["sufficient_linear_domain"]["selected_from_target_work"]
        assert all(not c["inside_sufficient_linear_domain"] for c in row["comparisons"])


def test_evidence_hashes_and_registry(artifact):
    for item in artifact["evidence_artifacts"]+artifact["protected_evidence_hashes"]:
        assert hashlib.sha256((R.ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    registry = json.loads((R.ROOT/R.REGISTRY).read_text())
    assert artifact["equation_registry_ids"] == [x["id"] for x in registry["entries"]]
    assert not registry["core_registry_modified"]
    assert registry["numerical_protocol"]["coefficient_solvers"] == list(R.SOLVERS)
    required = {"ontology", "units", "derivation_class", "observable", "data_role", "verification_status", "controlling_blocker", "claim_boundary"}
    assert all(required <= set(entry) for entry in registry["entries"])


def test_report_scope_and_holdout(artifact):
    assert len(artifact["report"]) == 11
    assert {"C", "UET_Pi", "R_gen", "R_obs"} <= set(artifact["excluded_variables"])
    assert artifact["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert not artifact["primary_covariance_entropy_defined"]
    assert artifact["thresholds"]["original_causal_leakage"] == 1e-6


def test_runtime_read_allowlist(monkeypatch, artifact):
    allowed = {str((R.ROOT/x["path"]).resolve()).casefold() for x in artifact["evidence_artifacts"]+artifact["protected_evidence_hashes"]}
    raw_read, text_read = Path.read_bytes, Path.read_text
    reads = set()

    def guard(path):
        resolved = str(path.resolve()).casefold()
        assert resolved in allowed, f"undeclared evidence read: {path}"
        reads.add(resolved)

    def read_bytes(path):
        guard(path)
        return raw_read(path)

    def read_text(path, *args, **kwargs):
        guard(path)
        return text_read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    monkeypatch.setattr(Path, "read_text", read_text)
    rerun = R.audit()
    assert rerun["checks"] == artifact["checks"]
    assert reads and not rerun["xie_2026_accessed"]
