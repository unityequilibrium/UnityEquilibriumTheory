"""Exact interpolation and conservative data/error scope."""

import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import Research_T13_Multi_Q_Estimator as M


@pytest.fixture(scope="module")
def artifact():
    return json.loads(M.OUTPUT.read_text())


def test_large_rational_serialization_preserves_global_safety_limit():
    limit = sys.get_int_max_str_digits()
    value = M.F(-(10**5000+7), 10**5001+3)
    record = M.fraction_record(value)
    assert M.decode(record) == value
    assert sys.get_int_max_str_digits() == limit
    assert M.integer_decimal(0) == "0"


@pytest.mark.parametrize("value", ["", "-", "1e2", "+2", " 3", "1"*(M.MAX_DECIMAL_DIGITS+1)],
                         ids=["empty", "sign", "exponent", "plus", "space", "over-limit"])
def test_invalid_or_unbounded_decimal_is_rejected(value):
    with pytest.raises(ValueError):
        M.decimal_integer(value)


def test_unbounded_integer_serialization_is_rejected():
    with pytest.raises(ValueError):
        M.integer_decimal(1 << M.MAX_INTEGER_BITS)


def test_known_polynomial_recovered_exactly_without_native_input_fit():
    qs = [M.F(1, 10), M.F(1, 20), M.F(1, 40)]
    beta = [M.F(1, 3), M.F(2, 7), -M.F(3, 11)]
    energies = [q*sum(beta[k]*q**(2*k) for k in range(3)) for q in qs]
    assert M.estimate(qs, energies) == beta
    assert M.newton_estimate(qs, energies) == beta


@pytest.mark.parametrize("qs", [[M.F(1)]*3, [M.F(0), M.F(1), M.F(2)], [M.F(-1), M.F(1), M.F(2)], [M.F(1), M.F(2)]])
def test_invalid_geometry_is_not_padded(qs):
    with pytest.raises(ValueError):
        M.weights(qs)


def test_common_axes_cancel_exactly_but_coefficient_covariance_does_not():
    qs = [M.F(1, 10), M.F(1, 20), M.F(1, 40)]
    energies = [q*(M.F(1, 3)+q*q-M.F(1, 2)*q**4) for q in qs]
    beta = M.estimate(qs, energies)
    jac = M.log_data_jacobian(qs, energies, beta)
    grad = M.ratio_gradient(beta, jac)
    assert sum(grad[:3]) == sum(grad[3:]) == 0
    assert sum(g*g for g in grad[:3]) > 0
    assert all(sum(row[:3]) == value for row, value in zip(jac, beta))
    assert all(sum(row[3:]) == -(1+2*k)*beta[k] for k, row in enumerate(jac))


def test_budget_rational_certificate_is_replayable_and_sufficient(artifact):
    for example in artifact["examples"]:
        native = {k: M.decode(v) for k, v in example["native_information_exact"].items()}
        for row in example["rows"]:
            prof = {k: [M.decode(v) for v in values] for k, values in row["profile_exact"].items()}
            low, high = M.decode(row["budget_lower_exact"]), M.decode(row["budget_upper_exact"])
            zero = M.target_box(prof, native, M.F(0))
            for key, value in zero.items():
                stored = row["zero_noise_box"][key]
                assert (M.decode(stored) if isinstance(value, M.F) else stored) == value
            assert not M.target_box(prof, native, high)["certified"]
            if low > 0:
                assert M.target_box(prof, native, low)["certified"]
                assert row["budget_corner_controls_pass"]
                assert high-low == M.F(1, 2**M.BUDGET_STEPS)
            else:
                assert not M.target_box(prof, native, M.F(0))["certified"]


def test_all_windows_including_noncertified_outcomes_are_retained(artifact):
    rows = [row for example in artifact["examples"] for row in example["rows"]]
    assert len(rows) == 10
    assert {row["q_max"] for row in rows} == set(M.Q_MAX_GRID)
    assert any(not row["budget_lower_certified"] for row in rows)
    assert any(row["budget_lower_certified"] for row in rows)
    assert all(not row["physical_noise_or_precision_assigned"] for row in rows)
    assert any(row["differential"]["inference_classification"] == "OUTSIDE_POSITIVE_KINETIC_CLASS" for row in rows)


def test_preregistered_protocol_matches_executed_controls(artifact):
    protocol = artifact["declared_protocol"]
    assert tuple(protocol["mu_grid"]) == M.MU_GRID
    assert tuple(protocol["q_max_grid"]) == M.Q_MAX_GRID
    assert tuple(M.F(v) for v in protocol["q_ratios"]) == M.RATIOS
    assert protocol["root_digits"] == M.ROOT_DIGITS
    assert tuple(protocol["estimator_digits"]) == M.ESTIMATOR_DIGITS
    assert protocol["log_fd_step"] == M.FD_STEP
    assert protocol["budget_bisection_steps"] == M.BUDGET_STEPS
    assert tuple(M.F(v) for v in protocol["common_axis_scales"]) == M.AXIS_SCALES
    assert M.F(str(protocol["illustrative_relative_I_target"])) == M.TARGET
    assert protocol["target_is_not_physical_acceptance_gate"] and protocol["locked_before_first_audit"]


def test_negative_energy_error_bound_is_rejected():
    with pytest.raises(ValueError):
        M.target_box({}, {}, -M.F(1))


def test_covariance_includes_energy_q_and_native_inputs(artifact):
    assert len(artifact["covariance_input_order"]) == 9
    for example in artifact["examples"]:
        for row in example["rows"]:
            d = row["differential"]
            assert d["energy_common_mode_null_exact"] and d["q_common_mode_null_exact"]
            assert d["ratio_gradient_relative_error"] < M.GATES["jacobian_relative"]
            if d["I_full_log_gradient"] is not None:
                assert len(d["I_full_log_gradient"]) == 9
                assert d["native_gradient_relative_error"] < M.GATES["jacobian_relative"]
                assert d["gain_is_response_to_unit_covariance_control_not_instrument_noise"]


def test_artifact_scope_and_registry(artifact):
    assert all(artifact["checks"].values())
    assert artifact["closure_level"] == "CLOSED_FOR_LANE" and len(artifact["report"]) == 11
    registry = json.loads((M.ROOT/M.REGISTRY).read_text())
    assert registry["thresholds"] == artifact["thresholds"]
    assert registry["protocol"] == artifact["declared_protocol"]
    assert not registry["core_registry_modified"]
    required = {"ontology", "units", "derivation_class", "observable", "data_role", "verification_status", "controlling_blocker", "claim_boundary"}
    assert all(required <= set(e) for e in registry["entries"])
    assert artifact["external_numeric_rows_admitted"] == 0
    assert artifact["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert artifact["thresholds"]["original_causal_leakage"] == 1e-6
    assert {"C", "UET_Pi", "R_gen", "R_obs"} <= set(artifact["excluded_variables"])


@pytest.mark.parametrize("flag", ["physical_noise_acquired", "physical_resolution_admitted", "physical_q5_measured", "physical_measurement_design_completed", "physical_material_map_admitted", "independent_alpha_Phi_K_admitted", "physical_Kubo_emitted", "full_SK_KMS_matching_closed", "nonlinear_parent_action_completed", "controlled_full_action_truncation_error_established", "full_core_unlock", "core_composition_gate_overwritten", "old_source_work_audit_promoted", "external_parameter_fitting", "clipping", "cone_padding", "assigned_width", "claim_promotion", "xie_2026_accessed"])
def test_no_physical_noise_or_acceptance_from_estimator(artifact, flag):
    assert artifact[flag] is False


def test_current_and_protected_hashes(artifact):
    for item in artifact["evidence_artifacts"]+artifact["protected_evidence_hashes"]:
        assert hashlib.sha256((M.ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    M.load_predecessor()


def test_runtime_path_read_allowlist(monkeypatch, artifact):
    allowed = {str((M.ROOT/item["path"]).resolve()).casefold() for item in artifact["evidence_artifacts"]+artifact["protected_evidence_hashes"]}
    old_bytes, old_text, observed = Path.read_bytes, Path.read_text, set()

    def guard(path):
        value = str(path.resolve()).casefold()
        assert value in allowed, f"undeclared data read: {path}"
        observed.add(value)

    def read_bytes(path):
        guard(path)
        return old_bytes(path)

    def read_text(path, *args, **kwargs):
        guard(path)
        return old_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    monkeypatch.setattr(Path, "read_text", read_text)
    result = M.audit()
    assert result["checks"] == artifact["checks"]
    assert observed and not result["xie_2026_accessed"]
