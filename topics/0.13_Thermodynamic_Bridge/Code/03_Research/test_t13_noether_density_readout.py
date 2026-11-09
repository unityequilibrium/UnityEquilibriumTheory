"""Conservation, source/readout, restricted ambiguity and evidence scope."""

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import Research_T13_Noether_Density_Readout as D


@pytest.fixture(scope="module")
def state_action():
    action = D.EFT.controls()
    return D.EFT.tree_state(1.05, action=action), action


@pytest.fixture(scope="module")
def artifact():
    return json.loads(D.OUTPUT.read_text())


@pytest.mark.parametrize("q,z", [(-1, .02j), (.01, 0), (.01, -.01j), (float("nan"), .01j)])
def test_reject_unadmitted_frequency_or_geometry(state_action, q, z):
    state, action = state_action
    with pytest.raises(ValueError):
        D.density_response(q, z, state, action)


def test_dynamic_q0_is_closed_charge_not_static_compressibility(state_action):
    state, action = state_action
    row = D.density_response(0, .02j, state, action)
    assert abs(row["susceptibility"])/state["s"] < 1e-10
    assert D.static_density_susceptibility(state, action) > state["s"] > 0
    assert abs(row["matter_without_contact"])/state["s"] == pytest.approx(1.)


def test_source_phase_sign_and_density_contact(state_action):
    state, action = state_action
    z = .03+.02j
    source, detector = D.source_vertices(z, state)
    assert source[1] == -detector[1]
    assert source[0] == detector[0] and source[2] == detector[2] == 0
    row = D.density_response(.01, z, state, action)
    assert row["ward_error"] < 1e-10


def test_independent_state_space_and_spectral_projection(state_action):
    state, action = state_action
    q, z = .01, .03+.02j
    direct = D.density_response(q, z, state, action)
    first = D.density_response(q, z, state, action, True)
    modal, mixed = D.modal_response(q, z, state, action)
    assert D.WORK.relative(direct["susceptibility"], first["susceptibility"]) < 1e-8
    assert D.WORK.relative(direct["susceptibility"], modal) < 1e-8
    assert D.WORK.relative(direct["density_to_h"], mixed) < 1e-8


def test_density_mode_strengths_are_positive_and_obey_tree_sum_rule(state_action):
    state, action = state_action
    modes = D.projected_modes(.01, state, action)
    assert len(modes) == 3 and modes[0]["density_strength"] > 0
    assert all(r["density_strength"] >= 0 for r in modes)
    assert D.WORK.relative(sum(r["density_strength"] for r in modes), state["s"]*.01**2) < 1e-8


def test_Phi_coordinate_rescaling_is_not_detectable_by_density(state_action):
    state, action = state_action
    z, q, scale = .03+.02j, .01, 2.
    mapped_action = D.EFT.rescale_Phi_coordinate(action, scale)
    mapped_state = D.EFT.tree_state(state["mu"], action=mapped_action)
    original = D.density_response(q, z, state, action)
    mapped = D.density_response(q, z, mapped_state, mapped_action)
    assert D.WORK.relative(original["susceptibility"], mapped["susceptibility"]) < 1e-8
    assert D.WORK.relative(scale*original["density_to_h"], mapped["density_to_h"]) < 1e-8


def test_restricted_gain_null_and_conditional_inverse():
    information = D.gain_information()
    assert information["amplitude_only_rank"] == 1
    assert information["plus_independent_gain_rank"] == 2
    assert information["null_residual"] == 0
    assert all(r["same_intensity_product"] == 1 for r in information["witnesses"])
    product = D.intensity_product(3, 2)
    assert np.sqrt(product/3) == 2


def test_unit_family_changes_kinetic_but_not_retained_dispersion(state_action):
    state, action = state_action
    result = D.unit_information(state, action)
    assert result["dispersion_only_rank"] == 2
    assert result["plus_independent_volumetric_scale_rank"] == 3
    assert result["null_residual"] < 1e-12
    assert result["augmented_determinant"] == pytest.approx(result["analytic_determinant"])
    for row in result["witnesses"]:
        assert row["I_kinetic"] != result["I_kinetic_reference"]
        assert max(row["same_linear_coefficient_error"], row["same_cubic_coefficient_error"], row["static_native_pressure_error"]) < 1e-8
        assert row["volumetric_scale_ratio"] != 1
        assert row["independent_scale_inverse_error"] < 1e-8
    assert result["inverse_reference_error"] < 1e-8


def test_independent_scale_removes_the_constructive_family(state_action):
    state, action = state_action
    cf = D.EFT.rest_coefficients(state, action)
    info = D.unit_information(state, action)
    for row in info["witnesses"]:
        recovered = D.kinetic_inverse(cf["c"], cf["eta"], row["volumetric_scale_ratio"], cf["c"], info["eta_base"], state["s"])
        assert recovered["I_kinetic"] == pytest.approx(row["I_kinetic"], rel=1e-8)
        assert recovered["energy_unit"] == pytest.approx(row["energy_unit_ratio"])
        assert recovered["q_unit"] == pytest.approx(row["q_unit_ratio"])
    assert info["volumetric_relation_requires_declared_action_normalization"]


@pytest.mark.parametrize("index", range(6))
def test_conditional_inverse_rejects_missing_or_invalid_inputs(index):
    values = [1.] * 6
    for invalid in (0., -1., float("nan"), float("inf")):
        values[index] = invalid
        with pytest.raises(ValueError):
            D.kinetic_inverse(*values)


def test_covariance_gradient_matches_independent_log_differences(state_action):
    state, action = state_action
    cf = D.EFT.rest_coefficients(state, action)
    info = D.unit_information(state, action)
    values = np.array([cf["c"], cf["eta"], 1., cf["c"], info["eta_base"], state["s"]])
    analytic = D.kinetic_log_gradient(*values)
    differences = []
    for index in range(6):
        plus, minus = values.copy(), values.copy()
        plus[index] *= np.exp(1e-5)
        minus[index] *= np.exp(-1e-5)
        differences.append((D.kinetic_inverse(*plus)["I_kinetic"]-D.kinetic_inverse(*minus)["I_kinetic"])/2e-5)
    assert np.allclose(analytic, differences, rtol=1e-7, atol=1e-8)


def test_negative_kinetic_inverse_is_not_clipped_to_a_physical_state():
    result = D.kinetic_inverse(1, .1, 1, 1, 1, 1)
    assert result["I_kinetic"] < 0
    # Such an inferred value rejects this positive-kinetic class; it is not a fit repair.


@pytest.mark.parametrize("gain,mapping", [(0, 1), (1, -1), (1, float("nan"))])
def test_gain_witness_is_not_allowed_to_hide_invalid_units(gain, mapping):
    with pytest.raises(ValueError):
        D.intensity_product(gain, mapping)


def test_artifact_verification_controls_closure(artifact):
    passed = all(artifact["checks"].values())
    assert artifact["tree_Noether_density_readout_verified"] is passed
    assert artifact["closure_level"] == ("CLOSED_FOR_LANE" if passed else "PARTIAL")
    assert len(artifact["report"]) == 11


@pytest.mark.parametrize("flag", ["physical_Noether_to_atomic_density_map_admitted", "physical_measurement_protocol_admitted", "physical_resolution_or_intrinsic_damping_admitted", "full_measurement_design_completed", "independent_alpha_Phi_K_admitted", "physical_Kubo_emitted", "full_SK_KMS_matching_closed", "nonlinear_parent_action_completed", "controlled_full_action_truncation_error_established", "old_source_work_audit_promoted", "full_core_unlock", "core_composition_gate_overwritten", "C_relabelled_as_charge_or_mass", "parameter_fitting", "assigned_width", "assigned_relaxation_time", "quantum_Phi_loops_added", "predecessor_covariance_vacuum_populations_changed", "clipping", "cone_padding", "claim_promotion", "xie_2026_accessed"])
def test_no_physical_admission_from_tree_readout(artifact, flag):
    assert artifact[flag] is False


def test_protocol_has_no_numeric_data_or_blindness_claim(artifact):
    protocol = json.loads((D.ROOT/D.PROTOCOL).read_text())
    assert all(r["numeric_rows_admitted"] == 0 for r in protocol["records"])
    assert not protocol["physical_measurement_protocol_admitted"]
    assert not protocol["lab_feasibility_established"]
    assert artifact["external_numeric_rows_admitted"] == 0
    assert artifact["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert artifact["thresholds"]["original_causal_leakage"] == 1e-6


def test_current_and_protected_hashes_and_registry_fields(artifact):
    for item in artifact["evidence_artifacts"]+artifact["protected_evidence_hashes"]:
        assert hashlib.sha256((D.ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    registry = json.loads((D.ROOT/D.REGISTRY).read_text())
    assert not registry["core_registry_modified"]
    required = {"ontology", "units", "derivation_class", "observable", "data_role", "verification_status", "controlling_blocker", "claim_boundary"}
    assert all(required <= set(r) for r in registry["entries"])
    assert artifact["equation_registry_ids"] == [r["id"] for r in registry["entries"]]
    assert {"C", "R_gen", "R_obs", "external_a0"} <= set(artifact["excluded_variables"])
    D.load_predecessor()


def test_audit_runtime_read_allowlist(monkeypatch, artifact):
    allowed = {str((D.ROOT/x["path"]).resolve()).casefold() for x in artifact["evidence_artifacts"]+artifact["protected_evidence_hashes"]}
    original_bytes, original_text = Path.read_bytes, Path.read_text
    observed = set()

    def guard(path):
        identity = str(path.resolve()).casefold()
        assert identity in allowed, f"undeclared data access: {path}"
        observed.add(identity)

    def read_bytes(path):
        guard(path)
        return original_bytes(path)

    def read_text(path, *args, **kwargs):
        guard(path)
        return original_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    monkeypatch.setattr(Path, "read_text", read_text)
    rerun = D.audit()
    assert rerun["checks"] == artifact["checks"]
    assert observed and not rerun["xie_2026_accessed"]
