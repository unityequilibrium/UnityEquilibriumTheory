"""Finite-potential stationarity is not a physical internal Goldstone pole."""

import hashlib
import json
from math import log, pi, sqrt
from pathlib import Path
import runpy

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.special import zeta

M = runpy.run_path(str(Path(__file__).with_name("Research_T13_Renormalized_Hartree_Background.py")))


def artifact():
    return json.loads(M["OUTPUT"].read_text(encoding="utf-8"))


def test_symmetric_vacuum_retains_the_ms_finite_term_not_a_no_sea_drop():
    mass_sq = 1.3**2
    expected_i = mass_sq/(16*pi*pi)*(log(mass_sq)-1)
    expected_v = mass_sq**2/(32*pi*pi)*(log(mass_sq)-1.5)
    for mu in (0., .4, .8):
        got = M["vacuum_integrals"](mu, mass_sq-mu*mu, mass_sq-mu*mu)
        np.testing.assert_allclose(got, [expected_i, expected_i, expected_v], rtol=1e-7)
        assert abs(got[2]) > .001


def test_auxiliary_mass_is_subtraction_coordinates_not_a_fitted_scale():
    for item in M["symmetric_vacuum_reference_check"]():
        assert item["relative_residual"] < 1e-6
    for example in artifact()["examples"]:
        assert example["auxiliary_reference_relative_residual"] < 1e-5


def test_thermal_zero_temperature_part_vanishes_separately_from_vacuum():
    np.testing.assert_array_equal(M["thermal_integrals"](0., 1.05, .2, .01), np.zeros(4))
    loops = M["loop_integrals"](0., 1.05, .2, .01)
    assert abs(loops["loop_free_energy"]) > .001
    assert loops["quasiparticle_entropy"] == 0.


def test_actual_matrix_frequency_sum_matches_thermal_covariance():
    t, mu, a, b, k, terms = .22, 1.05, .2, .01, .3, 256
    def covariance(nu):
        kernel = np.array([[nu*nu+k*k+a, -2*mu*nu], [2*mu*nu, nu*nu+k*k+b]])
        return np.diag(np.linalg.inv(kernel))
    summed = t*sum((covariance(2*pi*t*n) for n in range(-terms, terms+1)), start=np.zeros(2))
    tail = 2*t*(zeta(2., terms+1)/(2*pi*t)**2
                -np.array([k*k+a+4*mu*mu, k*k+b+4*mu*mu])*zeta(4., terms+1)/(2*pi*t)**4)
    vacuum = np.array([quad(lambda nu: covariance(nu)[j], 0., np.inf, epsabs=1e-12)[0]/pi for j in range(2)])
    low, high = M["modes"](k, mu, a, b)
    jl = 1/(low*np.expm1(low/t))
    jh = 1/(high*np.expm1(high/t))
    expected = np.array([((k*k+b-low*low)*jl+(high*high-k*k-b)*jh)/(high*high-low*low),
                         ((k*k+a-low*low)*jl+(high*high-k*k-a)*jh)/(high*high-low*low)])
    np.testing.assert_allclose(summed+tail-vacuum, expected, rtol=1e-7)


def test_finite_trace_log_derivative_includes_vacuum_and_thermal_tadpoles():
    for t in (0., .22):
        result = M["loop_derivative_check"](t, 1.05, .2, .03)
        assert result["relative_residual"] < 2e-5


def test_double_bubble_has_the_wick_diagram_coefficients():
    sigma, phase, coupling = .03, .07, .8
    covariance = np.diag([sigma, phase])
    wick = coupling/4*(np.trace(covariance)**2+2*np.trace(covariance@covariance))
    assert M["double_bubble"](sigma, phase, coupling) == pytest.approx(wick)
    h = 1e-6
    derivative = (M["double_bubble"](sigma+h, phase, coupling)-M["double_bubble"](sigma-h, phase, coupling))/(2*h)
    assert 2*derivative == pytest.approx(coupling*(3*sigma+phase), rel=1e-9)


def test_stationary_candidate_solves_field_and_propagator_equations():
    for example in artifact()["examples"]:
        bg = example["background"]
        s, a, b = (bg[k] for k in ("s", "a", "b"))
        coupling = example["u_canonical"]
        residual = M["residuals"](s, a, b, example["T"], example["mu"], example["r"], coupling)
        assert np.max(np.abs(residual)) < 1e-7
        assert a == pytest.approx(2*coupling*s, rel=1e-8)
        assert b == pytest.approx(2*coupling*(bg["loops"]["phase"]-bg["loops"]["sigma"]), rel=1e-8)
        assert bg["internal_low_frequency_gap"] > 0


def test_variational_mass_derivatives_vanish_without_a_forced_phase_mass():
    e = artifact()["examples"][0]
    bg = e["background"]
    s, a, b = (bg[k] for k in ("s", "a", "b"))
    h = 1e-4*b
    def potential(am, bm):
        return M["variational_potential"](s, am, bm, e["T"], e["mu"], e["r"], e["u_canonical"])
    gradients = [(potential(a+h, b)-potential(a-h, b))/(2*h),
                 (potential(a, b+h)-potential(a, b-h))/(2*h)]
    assert max(abs(v) for v in gradients) < 1e-7


def test_external_source_hessian_is_not_the_internal_hartree_inverse():
    for e in artifact()["examples"]:
        response = e["external_response"]
        rows = response["source_reoptimized_Hessian"]
        assert rows[-1]["radial_relative_residual"] < 2e-5
        assert response["external_radial_curvature"] > 0
        assert abs(response["external_radial_curvature"]/e["background"]["a"]-1) > .01
        assert abs(e["background"]["external_transverse_curvature"]) < 1e-7
        assert e["background"]["b"] > .001


def test_massless_internal_substitution_would_break_this_variational_branch():
    for e in artifact()["examples"]:
        assert abs(e["external_response"]["forcing_internal_b_zero_gap_residual"]) > .001
        assert e["external_response"]["internal_b_identity_residual"] < 1e-7
    assert artifact()["manual_Goldstone_mass_fix"] is False
    assert artifact()["internal_gap_used_as_physical_Goldstone_mass"] is False


def test_stationary_entropy_equals_pressure_derivative_not_extra_fitting():
    for e in artifact()["examples"]:
        thermo = e["thermodynamic_envelope"]
        assert thermo["quasiparticle_entropy"] > 0
        assert thermo["entropy_relative_residual"] < 2e-5
        assert thermo["entropy_envelope_relative_residual"] < 2e-5
        assert thermo["energy_identity_is_not_dynamical_ledger_proof"] is True


def test_charge_protocol_keeps_m_phi_fixed_instead_of_r():
    e = artifact()["examples"][0]
    bg = e["background"]
    s, a, b = (bg[k] for k in ("s", "a", "b"))
    mu, r, t, coupling = (e[k] for k in ("mu", "r", "T", "u_canonical"))
    h = 1e-4*mu
    wrong = -(M["variational_potential"](s, a, b, t, mu+h, r, coupling)
              -M["variational_potential"](s, a, b, t, mu-h, r, coupling))/(2*h)
    correct = e["thermodynamic_envelope"]["fixed_variational_charge"]
    assert abs(wrong/correct-1) > .5
    assert e["thermodynamic_envelope"]["charge_envelope_relative_residual"] < 2e-5


def test_natural_unit_rescaling_preserves_the_finite_potential_contract():
    t, mu, a, b, s, r, coupling, scale = .22, 1.05, .2, .03, .12, .1085, 1., 2.3
    base = M["loop_integrals"](t, mu, a, b)
    changed = M["loop_integrals"](t*scale, mu*scale, a*scale**2, b*scale**2, scale=scale, auxiliary=scale)
    for name, power in (("sigma", 2), ("phase", 2), ("loop_free_energy", 4), ("quasiparticle_entropy", 3)):
        assert changed[name] == pytest.approx(base[name]*scale**power, rel=1e-7)
    potential = M["variational_potential"](s, a, b, t, mu, r, coupling)
    scaled = M["variational_potential"](s*scale**2, a*scale**2, b*scale**2, t*scale, mu*scale, r*scale**2, coupling, scale=scale, auxiliary=scale)
    assert scaled == pytest.approx(potential*scale**4, rel=1e-7)


def test_ms_scale_variation_is_not_silently_declared_rg_invariant():
    first = M["vacuum_integrals"](0., 1.3**2, 1.3**2, scale=1.)
    second = M["vacuum_integrals"](0., 1.3**2, 1.3**2, scale=1.4)
    assert abs(second[0]/first[0]-1) > .1
    assert artifact()["renormalization_scheme_material_match"] is False


def test_artifact_hashes_and_physical_boundaries_are_preserved():
    record = artifact()
    assert all(record["checks"].values())
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert record["global_phase_minimum_selected"] is False
    assert record["finite_q_local_stability_established"] is False
    for flag in ("full_covariant_counterterm_match", "renormalization_scheme_material_match", "joint_Phi_stationarity_derived", "exact_microscopic_stationarity", "external_finite_frequency_response_derived", "microscopic_IR_matching_established", "physical_Kubo_emitted", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting", "xie_2026_accessed", "IR_filter", "clipping", "C_relabelled_as_charge_or_mass", "R_gen_added_as_state"):
        assert record[flag] is False
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((M["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    assert len(record["report"]) == 11


def test_audit_reads_declared_artifact_and_code_only(monkeypatch):
    accessed = []
    original_text, original_bytes = Path.read_text, Path.read_bytes
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


def test_invalid_domains_are_rejected_without_mass_clipping():
    for a, b in ((-.1, .03), (.2, -.01)):
        with pytest.raises(ValueError):
            M["loop_integrals"](.22, 1.05, a, b)
    with pytest.raises(ValueError):
        M["vacuum_integrals"](1.05, .2, .03, scale=0.)
    with pytest.raises(ValueError):
        M["thermal_integrals"](-.22, 1.05, .2, .03)
