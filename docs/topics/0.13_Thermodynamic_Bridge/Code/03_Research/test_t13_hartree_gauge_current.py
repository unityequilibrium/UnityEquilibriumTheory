"""Actual source vertices, independent loops, contact controls and scope tests."""

import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
M = runpy.run_path(str(HERE/"Research_T13_Hartree_Gauge_Current.py"))
F = M["F"]
T, MU, A, B = .22, 1.05, .233463, .009692


def artifact():
    return json.loads(M["OUTPUT"].read_text(encoding="utf-8"))


def test_source_vertex_and_seagull_are_action_derivatives():
    generator = M["ROTATION"]
    momentum = np.array([.3, .2, .1, .4])
    source = np.array([1j*MU, 0, 0, 0], complex)
    physical_mass = np.diag([A+MU*MU, B+MU*MU])
    def kernel(a):
        return np.dot(momentum, momentum)*np.eye(2)-2j*np.dot(momentum, a)*generator+np.dot(a, a)*np.eye(2)+physical_mass
    step = 1e-4
    for alpha in range(4):
        direction = np.eye(4)[alpha]
        first = (kernel(source+step*direction)-kernel(source-step*direction))/(2*step)
        second = (kernel(source+step*direction)-2*kernel(source)+kernel(source-step*direction))/(step*step)
        assert first == pytest.approx(-2j*momentum[alpha]*generator+2*source[alpha]*np.eye(2), abs=1e-10)
        assert second == pytest.approx(2*np.eye(2), abs=1e-7)


def test_finite_Q_vertex_Ward_identity_precedes_loop_projection():
    nu, omega, k, q = .3, .6, .4, .08
    generator = M["ROTATION"]
    v0 = -1j*(2*nu+omega)*generator+2j*MU*np.eye(2)
    vl = -1j*(2*k+q)*generator
    mass = np.diag([A+MU*MU, B+MU*MU])
    rhs = F["euclidean_kernel"](nu+omega, k+q, MU, A, B)@generator
    rhs -= generator@F["euclidean_kernel"](nu, k, MU, A, B)
    rhs -= mass@generator-generator@mass
    assert 1j*omega*v0+1j*q*vl == pytest.approx(rhs, abs=1e-12)


def test_polynomial_frequency_contact_cancels_by_residue_sum():
    p, r = M["extended_poles"](.4, MU, A, B)
    assert np.sum(r, axis=0) == pytest.approx(np.zeros((2, 2)), abs=1e-15)
    assert np.sum(p[:, None, None]*r, axis=0) == pytest.approx(-np.eye(2), abs=1e-15)


def test_independent_matrix_sums_match_derivative_vertex_moments():
    for harmonic in (0, 1):
        result = M["direct_frequency_check"](.4, .55, .2, T, MU, A, B, harmonic)
        for key in ("mixed_disagreement", "reverse_disagreement", "current_disagreement"):
            assert result[key] < M["POINT_TOLERANCE"]


def test_mixed_loop_includes_vacuum_and_is_not_only_thermal():
    vacuum = M["point_gauge"](.4, .55, .2, 0., MU, A, B, .15+.1j)
    thermal = M["point_gauge"](.4, .55, .2, T, MU, A, B, .15+.1j)
    assert np.linalg.norm(vacuum[0]) > .01
    assert np.linalg.norm(thermal[0]-vacuum[0]) > .01


def test_uniform_mixed_source_matches_fixed_physical_mass_tadpole_derivative():
    def covariance(mu):
        loops = M["H"]["loop_integrals"](T, mu, A+MU*MU-mu*mu, B+MU*MU-mu*mu)
        return np.array([loops["sigma"]+loops["phase"], loops["sigma"]-loops["phase"], 0.])/np.sqrt(2)
    actual = M["gauge_loops"](0., 0j, T, MU, A, B)[0][:, 0]
    derivatives = [-1j*(covariance(MU+step)-covariance(MU-step))/(2*step)
                   for step in (2e-5, 5e-6)]
    assert np.max(np.abs(derivatives[-1]-actual)) < np.max(np.abs(derivatives[0]-actual))/8
    expected = derivatives[-1]
    assert actual == pytest.approx(expected, rel=2e-6, abs=1e-8)


def test_vacuum_current_matches_independent_four_dimensional_reference():
    for q, z in ((.16, 0j), (.08, .15+.1j), (0., .3j)):
        actual = M["gauge_loops"](q, z, 0., 0., .7, .7)[2]
        reference = M["reference_current"](q, z, .7)
        assert actual == pytest.approx(reference, abs=M["POINT_TOLERANCE"])


def test_UV_surface_removal_is_fixed_by_mass_trace_not_Ward_residual():
    correction = M["spatial_surface_contact"](MU, A, B, 1.)
    assert correction == pytest.approx((A+B+2*MU*MU-2)/(24*np.pi*np.pi))
    with_surface = M["gauge_loops"](.08, .15+.1j, T, MU, A, B)[2]
    without = M["gauge_loops"](.08, .15+.1j, T, MU, A, B, remove_surface=False)[2]
    assert with_surface-without == pytest.approx(np.diag([0., correction, correction, correction]), abs=1e-12)


def test_current_contact_reference_and_routing_are_not_physical_cutoffs():
    args = (.08, .15+.1j, T, MU, A, B)
    base = M["gauge_loops"](*args)
    for kwargs in ({"auxiliary": .8}, {"auxiliary": 1.3}, {"routing": "one_sided"}):
        changed = M["gauge_loops"](*args, **kwargs)
        for i in range(3):
            assert changed[i] == pytest.approx(base[i], abs=M["QUADRATURE_TOLERANCE"])


def test_source_contact_scale_change_is_declared_not_physical_RG_match():
    q, z, factor = .08, .15+.1j, 1.7
    qe = np.array([-1j*z, q, 0, 0])
    expected = np.log(factor)/(24*np.pi*np.pi)*((q*q-z*z)*np.eye(4)-np.outer(qe, qe))
    changed = M["reference_current"](q, z, .7, scale=factor)
    base = M["reference_current"](q, z, .7)
    assert changed-base == pytest.approx(expected, abs=1e-15)
    assert artifact()["RG_invariance_established"] is False


def test_density_current_and_static_stiffness_have_independent_envelope_check():
    for e in artifact()["examples"]:
        for check in e["charge_envelope"]:
            assert check["relative_disagreement"] < 2e-5
            assert check["uniform_spatial_stiffness"] > 0
            assert check["phase_density_mixing_residual"] < 1e-9
            assert "not fixed shifted r" in check["protocol"]


def test_full_current_transversality_requires_contacts_and_reoptimization():
    for e in artifact()["examples"]:
        for row in e["responses"]:
            assert max(row["Ward_residuals"].values()) < M["WARD_TOLERANCE"]
            assert row["covariance_Ward_residual"] < M["WARD_TOLERANCE"]
            assert row["omit_spatial_UV_surface_Ward"] > M["WARD_TOLERANCE"]
            assert row["omit_classical_seagull_Ward"] > M["WARD_TOLERANCE"]
            current = M["unpack"](row["onshell_current"])
            assert current[2, 2] == pytest.approx(current[3, 3])
            assert np.max(np.abs(current[:2, 2:])) == 0


def test_counterterm_check_uses_actual_current_and_mixed_loops():
    q, z = .08, .15+.1j
    bubble = F["finite_bubble"](q, z, T, MU, A, B)
    loops = M["gauge_loops"](q, z, T, MU, A, B)
    for D in (-.03, .04):
        residual = M["counterterm_check"](q, z, MU, A, B, .116732, 1., bubble, loops, D)
        assert residual < 1e-12


def test_current_has_correct_energy_scaling_not_SI_relabelling():
    factor = 1.7
    base = M["gauge_loops"](.08, .15+.1j, T, MU, A, B)
    changed = M["gauge_loops"](.08*factor, (.15+.1j)*factor, T*factor, MU*factor,
                                  A*factor**2, B*factor**2, auxiliary=factor, scale=factor)
    for i in range(3):
        assert changed[i] == pytest.approx(base[i]*factor**(1 if i < 2 else 2), abs=2e-7)


def test_invalid_domains_do_not_invent_width_or_Goldstone_pseudoinverse():
    for args, kwargs in (((.08, .1, T, MU, A, B), {}), ((.08, -.1j, T, MU, A, B), {}),
                         ((.08, .1j, T, MU, A, 0.), {}), ((.08, .1j, T, MU, A, B), {"auxiliary": 0.}),
                         ((.08, .1j, T, MU, A, B), {"routing": "filtered"})):
        with pytest.raises(ValueError):
            M["gauge_loops"](*args, **kwargs)
    with pytest.raises(ValueError):
        M["source_hessians"](0., 0j, MU, A, B, .116732, 1., np.eye(3), None)


def test_artifact_reports_actual_current_not_physical_heat_or_full_closure():
    record = artifact()
    assert record["verification_status"] == "PASS_REST_FRAME_HARTREE_SOURCE_CURRENT"
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert record["gauge_current_vertex_computed"] and record["rest_frame_current_Ward_verified"]
    assert all(record["checks"].values())
    assert len(record["report"]) == 11
    assert "nondynamical_A_source" in record["excluded_variables"]
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    for flag in ("full_core_unlock", "g1_physical_unlock", "g2_science_unlock", "claim_promotion",
                 "full_covariant_counterterm_match", "RG_invariance_established", "imposed_Ward_projection",
                 "physical_current_contact_normalization_admitted", "real_axis_limit_admitted",
                 "physical_Kubo_emitted", "xie_2026_accessed", "IR_filter", "clipping", "parameter_fitting",
                 "C_relabelled_as_charge_or_mass", "R_gen_added_as_state"):
        assert record[flag] is False
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((M["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_audit_only_reads_predecessor_artifacts_not_numeric_or_holdout_sources(monkeypatch):
    paths = []
    original = Path.read_text
    def tracking(path, *args, **kwargs):
        paths.append(path.relative_to(M["ROOT"]).as_posix())
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", tracking)
    result = M["audit"]()
    assert set(paths) == {F["BACKGROUND_ARTIFACT"], M["FIELD_ARTIFACT"]}
    assert result["verification_status"] == "PASS_REST_FRAME_HARTREE_SOURCE_CURRENT"
