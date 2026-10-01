"""Coefficient, exact-rational, witness and no-promotion Hartree checks."""

from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest


HERE = Path(__file__).resolve().parent
M = runpy.run_path(str(HERE/"Research_T13_Hartree_Counterterm_Matching.py"))


def artifact():
    return json.loads(M["OUTPUT"].read_text(encoding="utf-8"))


def test_tensor_contraction_gives_two_distinct_gap_channels():
    identity = np.eye(2)
    A, B = .7, 1.1
    tensor = (A*np.einsum("ab,cd->abcd", identity, identity)
              +B*(np.einsum("ac,bd->abcd", identity, identity)
                  +np.einsum("ad,bc->abcd", identity, identity)))
    covariance = np.diag([.13, -.04])
    contracted = np.einsum("abcd,cd->ab", tensor, covariance)
    expected = M["projection_matrix"](A, B)@np.diag(covariance)
    assert np.diag(contracted) == pytest.approx(expected)
    assert contracted[0, 1] == 0


def test_counterterm_coefficients_match_independent_matrix_inverse():
    H = np.array([[3., 1.], [1., 3.]])
    for u in (.1, 1., 2.):
        for D in (-.08, .03, .2):
            ct = M["counterterms"](u, D, .11, 1.3, .7)
            independent = np.linalg.solve(np.eye(2)+D*u*H, u*H)
            assert M["projection_matrix"](ct["A"], ct["B"]) == pytest.approx(independent, rel=1e-13)


def test_singlet_and_traceless_eigenchannels_have_different_denominators():
    u, D = 1., .03
    ct = M["counterterms"](u, D, .11, 1.3, .7)
    bare = M["projection_matrix"](ct["A"], ct["B"])
    assert bare@np.array([1., 1.]) == pytest.approx(4*u/(1+4*u*D)*np.ones(2))
    assert bare@np.array([1., -1.]) == pytest.approx(2*u/(1+2*u*D)*np.array([1., -1.]))
    obstruction = M["single_coupling_obstruction"](u, D)
    assert obstruction["difference"] == pytest.approx(obstruction["difference_formula"])
    assert abs(obstruction["difference"]) > .01


def test_single_coupling_works_only_at_zero_divergence_in_this_class():
    ct = M["counterterms"](.7, 0., 0., 1.3, .7)
    for name in ("A", "B", "u4"):
        assert ct[name] == pytest.approx(.7, rel=1e-14, abs=0.)
    assert ct["bare_mass_sq"] == 1.3
    assert M["single_coupling_obstruction"](.7, 0.)["difference"] == 0


def test_arbitrary_amplitude_and_signed_finite_tadpoles_match_not_only_roots():
    rng = np.random.default_rng(17013)
    for _ in range(30):
        s, f1, f2 = rng.uniform(.02, .6, size=3)*[1., 1., -1.]
        row = M["state_match"](s, (f1, f2), 1.3, .8, .85, .04, -.07, .7)
        assert max(abs(v) for v in row["bare_gap_residual"]) < 1e-12
        assert abs(row["field_match_residual"]) < 1e-12
        assert abs(row["potential_match_residual"]) < 1e-12


def test_field_counterterm_is_not_the_internal_radial_coupling():
    ct = M["counterterms"](1., .03, .11, 1.3, .7)
    assert ct["delta_4"] == pytest.approx(ct["delta_A"]+2*ct["delta_B"])
    assert ct["u4"] != pytest.approx(ct["A"]+2*ct["B"])
    assert ct["u4"]-(ct["A"]+2*ct["B"]) == pytest.approx(-2.)


def test_potential_cancellation_is_exact_for_rational_probe_inputs():
    u, D, D2, m, ref, mu = Q(4, 5), Q(3, 100), Q(11, 100), Q(13, 10), Q(7, 10), Q(17, 20)
    A = u/((1+2*u*D)*(1+4*u*D))
    B = u/(1+2*u*D)
    u4 = A+2*B-2*u
    mb = m-2*(A+B)*(D2+(m-ref)*D)
    constant = Q(17, 100)+(m-ref)*D2+(m-ref)**2*D/2-(A+B)*(D2+(m-ref)*D)**2
    for s, f1, f2 in ((Q(0), Q(0), Q(0)), (Q(27, 100), Q(3, 50), Q(-1, 50)), (Q(2, 5), Q(3, 100), Q(17, 100))):
        p = m+3*u*s+u*(3*f1+f2)
        q = m+u*s+u*(f1+3*f2)
        t1, t2 = f1+D2+(p-ref)*D, f2+D2+(q-ref)*D
        div = Q(17, 100)+(p+q-2*ref)*D2/2+((p-ref)**2+(q-ref)**2)*D/4
        bare = (mb-mu**2)*s/2+u4*s*s/4+div-(A+B)*(t1+t2)**2/4-B*(t1-t2)**2/4
        finite = (m-mu**2)*s/2+u*s*s/4-u*(3*f1*f1+2*f1*f2+3*f2*f2)/4
        assert bare-finite-constant == 0


def test_normalization_is_independent_of_amplitude_chemical_potential_and_tadpoles():
    differences = []
    for s, f1, f2 in M["STATE_PROBES"]:
        for mu in (.4, .85, 1.2):
            row = M["state_match"](s, (f1, f2), 1.3, 1., mu, .03, .11, .7)
            differences.append(row["bare_on_gap_potential"]-row["finite_on_gap_potential"])
    assert max(differences)-min(differences) < 1e-12


def test_negative_control_equal_bare_couplings_leaves_a_gap_coefficient_residual():
    u, D = 1., .03
    scalar = u/(1+2*u*D)
    H = np.array([[3., 1.], [1., 3.]])
    residual = scalar*H@(np.eye(2)+D*u*H)-u*H
    assert np.max(np.abs(residual)) > .1


def test_units_whole_action_rescaling_preserves_counterterm_and_potential_match():
    k = 2.3
    base = M["state_match"](.27, (.06, -.02), 1.3, 1., .85, .03, .11, .7)
    scaled = M["state_match"](.27*k*k, (.06*k*k, -.02*k*k), 1.3*k*k, 1., .85*k,
                              .03, .11*k*k, .7*k*k, .19*k**4, .17*k**4)
    for key in ("A", "B", "u4"):
        assert scaled["counterterms"][key] == pytest.approx(base["counterterms"][key])
    assert scaled["counterterms"]["bare_mass_sq"] == pytest.approx(base["counterterms"]["bare_mass_sq"]*k*k)
    for key in ("bare_on_gap_potential", "finite_on_gap_potential", "state_independent_normalization"):
        assert scaled[key] == pytest.approx(base[key]*k**4, rel=1e-13)


def test_previous_stationary_candidate_is_matched_without_new_calibration():
    record = artifact()
    assert len(record["previous_stationary_witnesses"]) == 2
    for e in record["previous_stationary_witnesses"]:
        assert e["on_gap_potential_to_previous_residual"] < 1e-10
        assert e["shifted_masses_to_previous_residual"] < 1e-10
        for row in e["rows"]:
            assert abs(row["finite_field_bracket"]) < 1e-10


def test_counterterms_do_not_take_temperature_or_finite_tadpole_as_input():
    import inspect
    assert tuple(inspect.signature(M["counterterms"]).parameters) == ("coupling", "D", "D2", "mass_sq", "reference_sq")
    assert artifact()["temperature_dependent_counterterms"] is False


def test_full_symmetric_tensor_includes_offdiagonal_covariance_channel():
    ct = M["counterterms"](1., .03, 0., 1., 1.)
    X = np.array([[.13, -.04], [-.04, .07]])
    response = ct["A"]*np.trace(X)*np.eye(2)+2*ct["B"]*X
    basis = (np.eye(2)/np.sqrt(2), np.diag([1., -1.])/np.sqrt(2), np.array([[0., 1.], [1., 0.]])/np.sqrt(2))
    coefficients = np.array([np.sum(v*X) for v in basis])
    _, bare = M["symmetric_tensor_projection"](1., .03)
    projected = bare@coefficients
    assert projected == pytest.approx([np.sum(v*response) for v in basis])


def test_conditional_vertex_subtraction_does_not_require_commuting_bubbles():
    J = np.array([[.03, .02, -.01], [.02, -.04, .015], [-.01, .015, .06]])+1j*.01*np.eye(3)
    row = M["conditional_vertex_subtraction"](1., .03, J)
    assert row["maximum_response_residual"] < 1e-12
    assert row["bare_inverse_subtraction_residual"] < 1e-12
    assert row["noncommuting_bubble_residual"] > .01


def test_conditional_vertex_identity_does_not_claim_a_computed_frequency_loop():
    record = artifact()
    assert record["conditional_vertex_subtraction_identity_derived"] is True
    assert record["finite_frequency_bubble_divergence_computed"] is False
    assert record["external_finite_frequency_response_derived"] is False


def test_artifact_hashes_and_nonpromotion_contract():
    record = artifact()
    assert all(record["checks"].values())
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert record["homogeneous_counterterm_projection_derived"] is True
    assert record["on_gap_potential_counterterm_cancellation_derived"] is True
    for flag in ("same_coupling_counterterm_sufficient", "finite_probe_is_physical_UV_limit", "full_covariant_counterterm_match", "RG_invariance_established", "external_finite_frequency_response_derived", "joint_Phi_stationarity_derived", "internal_gap_used_as_physical_Goldstone_mass", "physical_Kubo_emitted", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting", "xie_2026_accessed", "C_relabelled_as_charge_or_mass", "R_gen_added_as_state"):
        assert record[flag] is False
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((M["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    assert len(record["report"]) == 11


def test_audit_reads_only_declared_predecessor_code_and_protected_artifacts(monkeypatch):
    original_text, original_bytes = Path.read_text, Path.read_bytes
    accessed = []
    def track(path):
        name = path.resolve().relative_to(M["ROOT"]).as_posix()
        assert "/Data/" not in name and "xie" not in name.lower()
        accessed.append(name)
    def read_text(path, *args, **kwargs):
        track(path)
        return original_text(path, *args, **kwargs)
    def read_bytes(path, *args, **kwargs):
        track(path)
        return original_bytes(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", read_text)
    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    record = M["audit"]()
    assert set(accessed) == {v["path"] for v in record["evidence_artifacts"]+record["protected_evidence_hashes"]}


def test_counterterm_projection_poles_and_invalid_inputs_are_not_repaired():
    for D in (-.25, -.5):
        with pytest.raises(ValueError):
            M["counterterms"](1., D, .11, 1.3, .7)
    for values in ((0., .03, .11, 1.3, .7), (1., float("nan"), .11, 1.3, .7), (1., .03, .11, 1.3, 0.)):
        with pytest.raises(ValueError):
            M["counterterms"](*values)


def test_failed_predecessor_is_not_promoted_by_matching_algebra(monkeypatch):
    original = Path.read_text
    predecessor = M["ROOT"]/M["PREVIOUS"]
    def read_text(path, *args, **kwargs):
        result = original(path, *args, **kwargs)
        if path == predecessor:
            record = json.loads(result)
            record["checks"]["nonzero_stationary_amplitude_and_gap_equations"] = False
            return json.dumps(record)
        return result
    monkeypatch.setattr(Path, "read_text", read_text)
    record = M["audit"]()
    assert record["checks"]["previous_candidate_acceptance_and_scope_preserved"] is False
    assert record["verification_status"] == "FAIL_HARTREE_COUNTERTERM_MATCH"
    assert record["closure_level"] == "PARTIAL"
