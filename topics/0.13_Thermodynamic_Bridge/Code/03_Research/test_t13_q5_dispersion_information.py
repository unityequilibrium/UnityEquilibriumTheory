"""Tree q5 information, exact witness envelope and conservative admission."""

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import Research_T13_Q5_Dispersion_Information as Q


@pytest.fixture(scope="module")
def inputs():
    action = Q.EFT.controls()
    state = Q.EFT.tree_state(1.05, action=action)
    return state, action, Q.parameters(state, action)


@pytest.fixture(scope="module")
def artifact():
    return json.loads(Q.OUTPUT.read_text())


def test_q5_is_derived_from_series_not_fit(inputs):
    state, action, p = inputs
    cf = Q.coefficients(p)
    assert cf["eta"] == pytest.approx(Q.EFT.rest_coefficients(state, action)["eta"])
    assert cf["zeta"] < 0 < cf["eta"]
    assert cf["zeta"] == pytest.approx(cf["zeta_base"]*(1+cf["s"]*cf["I"])**2-cf["K"]*cf["I"]**2)


def test_independent_U_is_not_needed_for_the_restricted_q5_inverse(inputs):
    cf = Q.coefficients(inputs[2])
    # Arbitrary constructive unit ratios, not calibration data.
    e_unit, q_unit = 2., 3.
    a, b, cc = e_unit*cf["c"]/q_unit, e_unit*cf["eta"]/q_unit**3, e_unit*cf["zeta"]/q_unit**5
    result = Q.inverse(a, b, cc, cf["c"], cf["eta_base"], cf["r0"], cf["D"], cf["s"])
    assert result["I"] == pytest.approx(cf["I"], rel=1e-8)
    assert result["energy_unit"] == pytest.approx(e_unit, rel=1e-8)
    assert result["q_unit"] == pytest.approx(q_unit, rel=1e-8)


def test_information_has_rank_but_reports_conditioning(inputs):
    info = Q.information(inputs[2])
    assert info["rank"] == 3
    assert info["determinant"] == pytest.approx(info["analytic_determinant"])
    assert info["ratio_derivative_dI"] < 0
    assert info["relative_I_per_relative_ratio_condition"] > 0
    assert info["gradient_relative_error"] < Q.GATES["gradient_relative"]


def test_rational_envelope_retains_exact_leading_cancellation(inputs):
    p = inputs[2]
    result = Q.tree_envelope(.01, p)
    assert result["first_four_residual_coefficients_exactly_zero"]
    fraction = result["normalized_energy_error_bound_exact"]
    exact = Q.F(int(fraction["numerator"]), int(fraction["denominator"]))
    assert exact > 0 and float(exact) == result["normalized_energy_error_bound"]
    root = Q.high_precision_root_check(.01, p, 80)
    assert root["normalized_E5_error"] <= float(exact)


@pytest.mark.parametrize("q", [0., -1., float("nan"), 1e4])
def test_envelope_rejects_unproved_domain(inputs, q):
    with pytest.raises(ValueError):
        Q.tree_envelope(q, inputs[2])


def test_decoupled_Phi_is_not_identifiable_as_a_kinetic_input(inputs):
    state, action, _ = inputs
    other = action | {"gamma": 0.}
    p = Q.parameters(Q.EFT.tree_state(state["mu"], action=other), other)
    assert Q.information(p)["classification"] == "NOT_APPLICABLE_DECOUPLED_PHI"
    assert "I" not in Q.coefficients(p)
    assert Q.tree_envelope(.01, p)["first_four_residual_coefficients_exactly_zero"]


@pytest.mark.parametrize("index", range(8))
def test_inverse_rejects_unadmitted_input_instead_of_clipping(inputs, index):
    cf = Q.coefficients(inputs[2])
    values = [cf["c"], cf["eta"], cf["zeta"], cf["c"], cf["eta_base"], cf["r0"], cf["D"], cf["s"]]
    values[index] = float("nan")
    with pytest.raises(ValueError):
        Q.inverse(*values)


def test_inverse_rejects_boundary_or_impossible_ratio(inputs):
    cf = Q.coefficients(inputs[2])
    for ratio in (cf["r0"], cf["r0"]-2*cf["D"]/cf["s"]**2):
        with pytest.raises(ValueError):
            Q.inverse(1., 1., ratio, cf["c"], cf["eta_base"], cf["r0"], cf["D"], cf["s"])


def test_moving_or_nonzero_source_state_requires_another_derivation(inputs):
    state, action, _ = inputs
    for change in ({"xi": .01}, {"h": .01}, {"mu": 0.}):
        with pytest.raises(ValueError):
            Q.parameters(state | change, action)


def test_artifact_and_registry_control_scope(artifact):
    assert all(artifact["checks"].values())
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert len(artifact["report"]) == 11
    assert artifact["external_numeric_rows_admitted"] == 0
    assert artifact["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert artifact["thresholds"]["original_causal_leakage"] == 1e-6
    registry = json.loads((Q.ROOT/Q.REGISTRY).read_text())
    assert registry["thresholds"] == artifact["thresholds"]
    assert registry["protocol"] == artifact["declared_protocol"]
    required = {"ontology", "units", "derivation_class", "observable", "data_role", "verification_status", "controlling_blocker", "claim_boundary"}
    assert all(required <= set(e) for e in registry["entries"])
    assert {"C", "UET_Pi", "R_gen", "R_obs"} <= set(artifact["excluded_variables"])


def test_rank_does_not_make_finite_q_proxy_an_unbiased_measurement(artifact):
    rows = [q for e in artifact["examples"] for q in e["q_rows"]]
    assert all(q["finite_q_proxy_I_relative_bias"] > 0 for q in rows)
    assert all(not q["finite_q_proxy_is_calibration_or_prediction"] for q in rows)
    diagnostic = artifact["finite_q_inference_diagnostic"]
    assert diagnostic["not_acceptance_gate"] and diagnostic["target_is_illustrative_requirement_not_measurement"]
    assert artifact["examples"][0]["q_rows"][-1]["finite_q_proxy_I_relative_bias"] > diagnostic["relative_I_example_target"]


def test_rational_certificate_inputs_can_be_replayed_without_tree_solver(artifact):
    for example in artifact["examples"]:
        decode = lambda v: Q.F(int(v["numerator"]), int(v["denominator"]))
        p = {key: decode(value) for key, value in example["declared_rational_parameters"].items()}
        z = {key: decode(value) for key, value in example["declared_rational_series"].items()}
        assert z == Q.series(p)
        for row in example["q_rows"]:
            replay = Q.tree_envelope(row["q"], p)
            assert replay["normalized_energy_error_bound_exact"] == row["envelope"]["normalized_energy_error_bound_exact"]
            assert replay["first_four_residual_coefficients_exactly_zero"]


@pytest.mark.parametrize("flag", ["physical_q5_measured", "physical_measurement_design_completed", "physical_material_map_admitted", "independent_alpha_Phi_K_admitted", "full_SK_KMS_matching_closed", "physical_Kubo_emitted", "nonlinear_parent_action_completed", "controlled_full_action_truncation_error_established", "full_core_unlock", "core_composition_gate_overwritten", "old_source_work_audit_promoted", "parameter_fitting", "assigned_width", "clipping", "cone_padding", "claim_promotion", "xie_2026_accessed"])
def test_no_physical_admission_from_q5(artifact, flag):
    assert artifact[flag] is False


def test_protected_and_current_hashes(artifact):
    for item in artifact["evidence_artifacts"]+artifact["protected_evidence_hashes"]:
        assert hashlib.sha256((Q.ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    Q.load_predecessor()


def test_audit_runtime_path_read_allowlist(monkeypatch, artifact):
    allowed = {str((Q.ROOT/x["path"]).resolve()).casefold() for x in artifact["evidence_artifacts"]+artifact["protected_evidence_hashes"]}
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
    result = Q.audit()
    assert result["checks"] == artifact["checks"]
    assert observed and not result["xie_2026_accessed"]
