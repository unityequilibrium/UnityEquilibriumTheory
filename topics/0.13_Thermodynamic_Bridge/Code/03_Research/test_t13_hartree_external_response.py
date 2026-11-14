"""Independent full-loop, source-response and protected-scope checks."""

import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
M = runpy.run_path(str(HERE/"Research_T13_Hartree_External_Response.py"))
T, MU, A, B = .22, 1.05, .233463, .009692


def artifact():
    return json.loads(M["OUTPUT"].read_text(encoding="utf-8"))


def test_symmetric_basis_is_orthonormal_and_not_UET_C():
    basis = M["BASIS"]
    assert np.einsum("aij,bji->ab", basis, basis) == pytest.approx(np.eye(3))
    assert basis == pytest.approx(basis.transpose(0, 2, 1))


def test_poles_reconstruct_full_euclidean_internal_matrix():
    poles, residues = M["poles_and_residues"](.4, MU, A, B)
    for nu in (.0, .3, 1.2):
        direct = np.linalg.inv(M["euclidean_kernel"](nu, .4, MU, A, B))
        spectral = np.sum(residues/(1j*nu-poles)[:, None, None], axis=0)
        assert spectral == pytest.approx(direct, rel=1e-12, abs=1e-12)


def test_unmixed_degenerate_poles_are_handled_without_mass_split():
    poles, residues = M["poles_and_residues"](.4, 0., .7, .7)
    actual = np.sum(residues/(.3j-poles)[:, None, None], axis=0)
    assert actual == pytest.approx(np.eye(2)/(.09+.16+.7), rel=1e-13)


def test_full_loop_includes_vacuum_at_zero_temperature():
    value = M["point_bubble"](.4, .55, 0., MU, A, B, .15+.1j)
    assert np.linalg.norm(value) > .1
    thermal = M["point_bubble"](.4, .55, T, MU, A, B, .15+.1j)
    assert np.linalg.norm(thermal-value) > .1


def test_direct_matrix_frequency_sums_match_all_three_channels():
    for harmonic in (0, 1):
        result = M["matrix_frequency_check"](.4, .55, T, MU, A, B, harmonic)
        assert result["max_absolute_disagreement"] < M["POINT_TOLERANCE"]


def test_finite_vacuum_agrees_with_four_dimensional_feynman_parameters():
    q, z = .08, .15+.1j
    expected = M["equal_mass_vacuum_reference"](q, z, .7)
    for auxiliary in (.8, 1., 1.3):
        actual = M["direct_subtracted_bubble"](q, z, 0., 0., .7, .7, auxiliary=auxiliary)
        assert actual == pytest.approx(expected, rel=2e-6, abs=M["POINT_TOLERANCE"])


def test_absolute_zero_loop_recovers_diagonal_and_rotated_tadpole_derivatives():
    absolute = M["direct_subtracted_bubble"](0., 0j, T, MU, A, B)
    derivative = M["static_finite_bubble"](T, MU, A, B)
    assert absolute == pytest.approx(derivative, rel=1e-6, abs=1e-8)
    loop = M["H"]["loop_integrals"](T, MU, A, B)
    assert absolute[2, 2].real == pytest.approx((loop["sigma"]-loop["phase"])/(A-B), rel=1e-7)


def test_finite_Q_difference_and_absolute_subtraction_agree():
    q, z = .08, .15+.1j
    first = M["finite_bubble"](q, z, T, MU, A, B)
    second = M["direct_subtracted_bubble"](q, z, T, MU, A, B)
    assert first == pytest.approx(second, rel=1e-6, abs=1e-8)


def test_convergent_Q_difference_does_not_depend_on_momentum_routing():
    args = (.16, .15+.1j, T, MU, A, B)
    symmetric = M["bubble_difference"](*args)
    one_sided = M["bubble_difference"](*args, routing="one_sided")
    assert symmetric == pytest.approx(one_sided, abs=1e-8)


def test_zero_Q_difference_is_zero_and_small_static_Q_approaches_it():
    assert np.max(np.abs(M["bubble_difference"](0., 0j, T, MU, A, B))) < 1e-12
    large = M["bubble_difference"](.02, 0j, T, MU, A, B)
    small = M["bubble_difference"](.01, 0j, T, MU, A, B)
    assert np.linalg.norm(small) < .3*np.linalg.norm(large)


def test_source_vertices_follow_full_invariant_gap_derivative():
    s, u, step = .12, .7, 1e-6
    v = np.array([np.sqrt(s), 0.])
    w, kernel, vertices = M["source_vertices"](s, u)
    def tree_mass(field):
        return u*(np.dot(field, field)*np.eye(2)+2*np.outer(field, field))
    columns = []
    for delta in np.eye(2):
        derivative = (tree_mass(v+step*delta)-tree_mass(v-step*delta))/(2*step)
        columns.append(np.einsum("aij,ji->a", M["BASIS"], derivative))
    assert vertices == pytest.approx(np.column_stack(columns), rel=1e-10, abs=1e-10)
    assert vertices == pytest.approx(kernel@w)


def test_external_static_inverse_recovers_potential_without_mass_fix():
    for e in artifact()["examples"]:
        zero = M["static_finite_bubble"](e["T"], e["mu"], e["a"], e["b"])
        inverse = M["external_inverse"](0., 0j, e["mu"], e["a"], e["b"], e["s"], 1., zero)
        assert inverse[0, 0].real == pytest.approx(e["external_static_radial_reference"], rel=2e-5)
        assert abs(inverse[1, 1]) < 1e-9
        assert e["b"] > .001


def test_actual_dynamic_bubble_counterterm_source_match():
    bubble = M["finite_bubble"](.08, .15+.1j, T, MU, A, B)
    for D in (-.03, .04):
        assert M["counterterm_source_check"](.08, .15+.1j, MU, A, B, .116732, 1., bubble, D) < 1e-12


def test_retarded_reality_and_chemical_channel_parity():
    z = .15+.1j
    first = M["point_bubble"](.4, .55, T, MU, A, B, z)
    conjugate = M["point_bubble"](.4, .55, T, MU, A, B, -z.conjugate())
    assert conjugate == pytest.approx(first.conjugate(), abs=1e-12)
    parity = np.diag([1., 1., -1.])
    assert first.T == pytest.approx(parity@first@parity, abs=1e-12)


def test_subtracted_bubble_has_correct_energy_rescaling():
    factor = 1.7
    base = M["direct_subtracted_bubble"](.08, .15+.1j, T, MU, A, B)
    changed = M["direct_subtracted_bubble"](.08*factor, (.15+.1j)*factor, T*factor,
                                            MU*factor, A*factor**2, B*factor**2,
                                            scale=factor, auxiliary=factor)
    assert changed == pytest.approx(base, rel=1e-6, abs=1e-8)


def test_invalid_domains_do_not_add_width_clip_mass_or_filter():
    for q, z, a, b in ((.08, .1, A, B), (.08, -.1j, A, B), (-.1, 0j, A, B), (.08, 0j, A, 0.)):
        with pytest.raises(ValueError):
            M["bubble_difference"](q, z, T, MU, a, b)
    with pytest.raises(ValueError):
        M["bubble_difference"](.08, .1j, T, MU, A, B, routing="filter")


def test_artifact_reports_scope_and_protected_evidence_hashes():
    record = artifact()
    assert record["verification_status"] == "PASS_SUBTRACTED_HARTREE_EXTERNAL_FIELD_RESPONSE"
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert all(record["checks"].values())
    assert len(record["report"]) == 11
    assert "R_gen" in record["excluded_variables"]
    for flag in ("full_core_unlock", "g1_physical_unlock", "g2_science_unlock", "claim_promotion",
                 "full_covariant_counterterm_match", "RG_invariance_established", "gauge_current_vertex_computed",
                 "real_axis_limit_admitted", "physical_Kubo_emitted", "xie_2026_accessed", "IR_filter", "clipping"):
        assert record[flag] is False
    for source in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((M["ROOT"]/source["path"]).read_bytes()).hexdigest() == source["sha256"]


def test_audit_only_reads_declared_artifacts_and_does_not_mutate_them(monkeypatch):
    paths = []
    original = Path.read_text
    def tracking(path, *args, **kwargs):
        paths.append(path.relative_to(M["ROOT"]).as_posix())
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", tracking)
    result = M["audit"]()
    assert set(paths) == {M["BACKGROUND_ARTIFACT"], M["MATCH_ARTIFACT"]}
    assert result["verification_status"] == artifact()["verification_status"]
    assert result["parameter_fitting"] is False
