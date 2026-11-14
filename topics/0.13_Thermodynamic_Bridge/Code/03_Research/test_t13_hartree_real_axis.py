"""PV/phase-space independence, contacts, scaling, domain and evidence tests."""

import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

M = runpy.run_path(str(Path(__file__).with_name("Research_T13_Hartree_Real_Axis.py")))
T, MU, A, B = .22, 1.05, .233463, .009692


def artifact():
    return json.loads(M["OUTPUT"].read_text(encoding="utf-8"))


def test_inverse_shell_recovers_original_dispersion_and_residue():
    for mu in (0., MU):
        for k in (.05, .3, 10.):
            poles, residues = M["F"]["poles_and_residues"](k, mu, A, B)
            for index, ell in enumerate(poles):
                k_sq, derivative, residue = M["inverse_shell"](ell, index, mu, A, B)
                assert float(k_sq) == pytest.approx(k*k, abs=1e-10)
                assert np.asarray(residue, complex) == pytest.approx(residues[index], abs=1e-10)
                assert np.sign(derivative) == np.sign(ell)


def test_exact_Cauchy_coordinate_matches_unsplit_upper_half_plane_integral():
    for k in (.05, .3, 1.2):
        errors = M["direct_angular_check"](k, .08, .15+.1j, T, MU, A, B)
        assert max(errors.values()) < M["POINT_TOLERANCE"]


def test_real_axis_delta_roots_are_independent_of_Cauchy_inverse_shell():
    for omega in (.015, .15, .4, -.15):
        check = M["point_cut_check"](.3, .08, omega, T, MU, A, B)
        for field in ("shell_residual", "direct_delta_vs_PV_cut_disagreement",
                      "PV_source_metric_discontinuity_disagreement", "transverse_discontinuity_disagreement"):
            assert check[field] < M["POINT_TOLERANCE"]
        assert check["relative_slope_FD_disagreement"] < 1e-6


def test_pair_and_scattering_are_kinematic_not_a_fitted_width():
    scattering = M["point_cut_check"](.3, .08, .015, T, MU, A, B)
    pair = M["point_cut_check"](.3, .08, .15, T, MU, A, B)
    assert scattering["scattering_norm"] > 1 and scattering["pair_norm"] == 0
    assert pair["pair_norm"] > 1 and pair["scattering_norm"] == 0
    cold = M["point_cut_check"](.3, .08, .015, 0., MU, A, B)
    assert cold["scattering_norm"] == 0


def test_omitting_i0_discontinuity_cannot_pass_spectral_check():
    joint, _, cuts = M["angular_kernel"](.3, .08, .15, T, MU, A, B)
    exact = cuts["pair"][0][0]+cuts["scattering"][0][0]
    without_cut = joint[0]-1j*exact
    metric = M["SOURCE_METRIC"]
    discontinuity = (without_cut-metric@without_cut.conj().T@metric)/(2j)
    assert np.max(np.abs(discontinuity-exact)) > 1.


def test_vacuum_pair_cut_has_analytic_four_dimensional_normalization():
    for row in artifact()["vacuum_reference_checks"]:
        assert row["bubble_Feynman_disagreement"] < M["POINT_TOLERANCE"]
        assert row["current_Feynman_disagreement"] < M["POINT_TOLERANCE"]
        assert row["pair_cut_normalization_disagreement"] < M["POINT_TOLERANCE"]
    assert artifact()["vacuum_reference_checks"][0]["pair_beta"] == 0
    assert artifact()["vacuum_reference_checks"][1]["pair_beta"] > 0


def test_independent_integrated_delta_phase_space_matches_PV_loops():
    for e in artifact()["examples"]:
        assert e["independent_integrated_delta_cut_disagreement"] < M["QUADRATURE_TOLERANCE"]
        assert e["zero_temperature_scattering_norm"] == 0


def test_reoptimized_real_axis_Ward_and_loss_on_declared_grid():
    for e in artifact()["examples"]:
        for row in e["responses"]:
            assert max(row["Ward_residuals"].values()) < M["WARD_TOLERANCE"]
            assert row["covariance_Ward_residual"] < M["WARD_TOLERANCE"]
            assert row["loop_discontinuity_vs_exact_cut"] < M["QUADRATURE_TOLERANCE"]
            assert min(row["minus_physical_current_spectral_eigenvalues"]) >= -M["POINT_TOLERANCE"]


def test_omitting_contacts_or_reoptimization_breaks_real_axis_Ward():
    e = artifact()["examples"][0]
    q, omega = .08, .15
    loops = M["retarded_loops"](q, omega, e["T"], e["mu"], e["a"], e["b"])
    response = M["reoptimized_response"](q, omega, e["mu"], e["a"], e["b"], e["s"], 1., loops)
    assert max(M["G"]["ward_residuals"](q, omega, e["s"], response).values()) < M["WARD_TOLERANCE"]
    bare = list(response)
    bare[3] = response[3]-e["s"]*np.eye(4)
    assert M["G"]["ward_residuals"](q, omega, e["s"], bare)["source_source"] > M["WARD_TOLERANCE"]
    assert np.linalg.norm(response[3]@np.array([omega, 1j*q, 0., 0.])) > M["WARD_TOLERANCE"]


def test_real_axis_quadrature_and_endpoint_scan_do_not_clip_domains():
    for e in artifact()["examples"]:
        for row in e["responses"]:
            assert row["quadrature_refinements"][-1] < M["QUADRATURE_TOLERANCE"]
            assert row["endpoint_scan_refinement"] < M["POINT_TOLERANCE"]
            assert row["radial_compact_splits"][0] == 0
            assert row["radial_compact_splits"][-1] == 1
    record = artifact()
    assert record["config"]["radial_domain"] == "0<=k<infinity"
    assert record["config"]["output_imaginary_width"] == 0


def test_auxiliary_reference_and_negative_frequency_are_consistent():
    for e in artifact()["examples"]:
        assert e["auxiliary_reference_disagreement"] < M["QUADRATURE_TOLERANCE"]
        assert e["retarded_current_reality_residual"] < M["QUADRATURE_TOLERANCE"]
        assert e["upper_half_plane_predecessor_disagreement"] < M["QUADRATURE_TOLERANCE"]


def test_width_sequence_is_verification_not_a_selected_physical_parameter():
    for e in artifact()["examples"]:
        sequence = e["upper_half_plane_to_exact_angular_limit"]
        assert [row["eta_verification_only"] for row in sequence] == [.02, .01, .005, .0025]
        assert all(y["angular_distance_to_exact_limit"] < x["angular_distance_to_exact_limit"]
                   for x, y in zip(sequence, sequence[1:]))
    assert artifact()["artificial_width"] is False


def test_natural_energy_scaling_is_not_a_physical_SI_anchor():
    for e in artifact()["examples"]:
        assert e["unit_scaling_disagreement"] < M["QUADRATURE_TOLERANCE"]
    assert artifact()["physical_current_contact_normalization_admitted"] is False


def test_legacy_validators_remain_restricted_and_no_pseudoinverse_added():
    with pytest.raises(ValueError):
        M["F"]["validate"](T, MU, A, B, .08, .15)
    for args, kwargs in (((0., .15, T, MU, A, B), {}), ((.08, -.1j, T, MU, A, B), {}),
                         ((.08, .15, T, MU, A, 0.), {}), ((.08, .15, T, MU, A, B), {"auxiliary": 0.}),
                         ((.08, .15, T, MU, A, B), {"radial_order": True}),
                         ((.08, .15, T, MU, A, B), {"scan_order": 0})):
        with pytest.raises(ValueError):
            M["retarded_loops"](*args, **kwargs)
    with pytest.raises(ValueError):
        M["direct_angular_check"](.3, .08, .15, T, MU, A, B)


def test_artifact_claims_only_scoped_real_axis_not_global_or_physical_closure():
    record = artifact()
    assert record["verification_status"] == "PASS_SCOPED_HARTREE_REAL_AXIS_RESPONSE"
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert record["real_axis_limit_admitted"] is True
    assert all(record["checks"].values())
    assert len(record["report"]) == 11
    assert len([row for e in record["examples"] for row in e["responses"]]) == 10
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert "R_gen" in record["excluded_variables"]
    for flag in ("global_real_axis_stability_proved", "controlled_truncation_error_established",
                 "full_covariant_counterterm_match", "RG_invariance_established", "joint_Phi_stationarity_derived",
                 "physical_Kubo_emitted", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock",
                 "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting",
                 "imposed_Ward_projection", "clipping", "IR_filter", "artificial_width", "xie_2026_accessed",
                 "internal_gap_used_as_physical_Goldstone_mass", "C_relabelled_as_charge_or_mass",
                 "R_gen_added_as_state", "causal_leakage_threshold_changed"):
        assert record[flag] is False
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((M["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_changed_predecessor_hash_cannot_be_silently_renewed():
    predecessor = json.loads((M["ROOT"]/M["CURRENT_ARTIFACT"]).read_text(encoding="utf-8"))
    assert M["predecessor_hashes_match"](predecessor) is True
    predecessor["evidence_artifacts"][0]["sha256"] = "0"*64
    assert M["predecessor_hashes_match"](predecessor) is False


def test_audit_only_reads_current_predecessor_not_numeric_or_holdout(monkeypatch):
    paths = []
    original = Path.read_text
    def tracking(path, *args, **kwargs):
        paths.append(path.relative_to(M["ROOT"]).as_posix())
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", tracking)
    result = M["audit"]()
    assert set(paths) == {M["CURRENT_ARTIFACT"]}
    assert result["verification_status"] == "PASS_SCOPED_HARTREE_REAL_AXIS_RESPONSE"
