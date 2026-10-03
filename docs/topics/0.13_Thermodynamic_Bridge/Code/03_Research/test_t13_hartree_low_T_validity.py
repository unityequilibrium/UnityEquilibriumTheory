"""Independent dispersion, envelope, asymptotic and claim-boundary checks."""

import ast
import hashlib
import json
from math import exp, pi, sqrt
from pathlib import Path
import runpy

import numpy as np
import pytest
from scipy.integrate import quad

HERE = Path(__file__).resolve().parent
M = runpy.run_path(str(HERE/"Research_T13_Hartree_Low_T_Validity.py"))


def artifact():
    return json.loads(M["OUTPUT"].read_text(encoding="utf-8"))


def test_gap_jet_is_the_original_unrepaired_internal_dispersion():
    mu, a, b = 1.1, .3, .004
    jet = M["gap_jet"](mu, a, b)
    original = M["H"]["modes"](0., mu, a, b)[0]
    assert jet["gap"] == pytest.approx(original, rel=1e-13)
    for k in (1e-4, 5e-5, 2.5e-5):
        low = M["H"]["modes"](k, mu, a, b)[0]
        derivative = (low-original)/k**2
        assert derivative == pytest.approx(jet["low_energy_k_squared_coefficient"], rel=2e-5)
    assert jet["effective_quadratic_mass"] == pytest.approx(1/(2*jet["low_energy_k_squared_coefficient"]))


def test_positive_gap_and_monotone_low_branch_for_positive_internal_masses():
    for mu, a, b in ((0., .3, .004), (.8, .5, .03), (1.2, .9, .003)):
        jet = M["gap_jet"](mu, a, b)
        assert min(jet.values()) > 0
        k = np.linspace(0., 4., 201)
        low = M["H"]["modes"](k, mu, a, b)[0]
        assert np.all(np.diff(low) > 0)


def test_invalid_gapless_repair_inputs_are_not_admitted():
    for a, b in ((.2, 0.), (0., .01), (.2, -1.), (np.nan, .01)):
        with pytest.raises(ValueError):
            M["gap_jet"](1.1, a, b)
    for t in (0., -1., np.nan):
        with pytest.raises(ValueError):
            M["independent_entropy"](t, 1.1, .2, .003)


def test_entropy_weight_retains_the_small_free_energy_term():
    for x in (.01, 1., 10.):
        expected = x/np.expm1(x)-np.log(-np.expm1(-x))
        assert M["entropy_weight"](x) == pytest.approx(expected, rel=1e-12)
    # Computing log(1-exp(-x)) via log(-expm1(-x)) loses its tiny term here.
    x = 64.
    assert M["entropy_weight"](x)/exp(-x) == pytest.approx(x+1, rel=1e-14)
    for x in (0., -1., np.inf, np.nan):
        with pytest.raises(ValueError):
            M["entropy_weight"](x)


def test_independent_equal_mass_entropy_matches_direct_energy_integral():
    t, mass = .08, .12
    direct = quad(lambda k: k*k/pi**2*M["entropy_weight"](sqrt(k*k+mass*mass)/t),
                  0., np.inf, epsabs=1e-12, epsrel=1e-10)[0]
    actual = M["independent_entropy"](t, 0., mass*mass, mass*mass)["entropy"]
    assert actual == pytest.approx(direct, rel=1e-9)


def test_conditional_gapless_bose_mode_coefficient_is_integrated_not_fitted():
    integral = quad(lambda x: x*x*M["entropy_weight"](x), 0., np.inf,
                    epsabs=1e-10, epsrel=1e-10)[0]/(2*pi*pi)
    assert integral == pytest.approx(2*pi*pi/45, rel=1e-10)
    for c in (.2, .4):
        assert integral/c**3 > 0


def test_gap_and_entropy_rescale_in_the_declared_natural_unit_lane():
    factor = 1.7
    mu, a, b, t = .9, .3, .002, .003
    base = M["gap_jet"](mu, a, b)
    scaled = M["gap_jet"](mu*factor, a*factor**2, b*factor**2)
    assert scaled["gap"] == pytest.approx(base["gap"]*factor)
    assert scaled["effective_quadratic_mass"] == pytest.approx(base["effective_quadratic_mass"]*factor)
    entropy = M["independent_entropy"](t, mu, a, b)["entropy"]
    actual = M["independent_entropy"](t*factor, mu*factor, a*factor**2, b*factor**2)["entropy"]
    assert actual == pytest.approx(entropy*factor**3, rel=1e-10)


def test_entropy_envelope_identity_includes_gap_residuals_off_stationarity():
    S, H = M["S"], M["H"]
    c = M["M"]["controls"]()
    s, a, b, phi, t, mu = .12, .26, .004, .05, .02, 1.05
    h = 1e-5*t
    lo = H["loop_integrals"](t-h, mu, a, b)
    hi = H["loop_integrals"](t+h, mu, a, b)
    entropy = -(S["joint_potential"](s,a,b,phi,t+h,mu,c)-S["joint_potential"](s,a,b,phi,t-h,mu,c))/(2*h)
    residual = S["joint_residual"](s,a,b,phi,t,mu,c)
    correction = .5*(residual[1]*(hi["sigma"]-lo["sigma"])+residual[2]*(hi["phase"]-lo["phase"]))/ (2*h)
    qp = H["loop_integrals"](t,mu,a,b)["quasiparticle_entropy"]
    assert abs(correction) > 1e-6
    assert entropy == pytest.approx(qp+correction, rel=2e-6)


def test_actual_zero_T_states_are_joint_and_unrepaired():
    r = artifact()
    for e in r["examples"]:
        state, mu = e["zero_T_state"], e["mu"]
        residual = M["S"]["joint_residual"](*(state[k] for k in ("s","a","b","Phi")),0.,mu,r["action_controls"])
        assert max(abs(residual/np.array(state["residual_scales"]))) < M["ROOT_TOLERANCE"]
        assert state["a"] == pytest.approx(2*r["action_controls"]["u"]*state["s"], abs=1e-10)
        assert state["b"] == pytest.approx(2*r["action_controls"]["u"]*(state["loops"]["phase"]-state["loops"]["sigma"]), abs=1e-10)
        assert state["b"] > 0


def test_zero_T_source_coefficients_and_upper_expansion_are_local_not_global():
    for e in artifact()["examples"]:
        response = e["zero_T_external_response"]
        runs = response["source_runs"]
        assert abs(runs[-1]["charge_susceptibility"]/runs[-2]["charge_susceptibility"]-1) < 2e-5
        assert abs(runs[-1]["spatial_stiffness"]/runs[-2]["spatial_stiffness"]-1) < 2e-5
        c = sqrt(runs[-1]["spatial_stiffness"]/runs[-1]["charge_susceptibility"])
        assert response["external_derivative_expansion_speed"] == pytest.approx(c)
        assert response["conditional_one_gapless_mode_entropy_T_cubed_coefficient"] == pytest.approx(2*pi*pi/(45*c**3))
        assert len(response["finite_q_upper_plane_checks"]) == 6
        assert all(q["relative_expansion_disagreement"] < M["EXPANSION_TOLERANCE"] for q in response["finite_q_upper_plane_checks"] if q["q"] == M["Q_GRID"][-1])


def test_recorded_entropy_envelope_reoptimizes_Phi_not_a_fixed_background():
    for e in artifact()["examples"]:
        for row in e["entropy_envelope_checks"]:
            assert row["runs"][-1]["joint_relative_disagreement"] < M["ENVELOPE_TOLERANCE"]
            assert row["runs"][-1]["fixed_relative_disagreement"] < M["ENVELOPE_TOLERANCE"]
            assert "reoptimized" in row["protocol"]


def test_deep_low_T_entropy_has_positive_gap_asymptotic_not_T_cubed():
    for e in artifact()["examples"]:
        rows = e["low_T_runs"]
        assert [r["gap_over_T"] for r in rows] == list(M["TEMPERATURE_DIVISORS"])
        assert rows[-1]["Boltzmann_asymptotic_relative_difference"] < .1
        assert rows[-1]["conditional_gapless_entropy_ratio"] < 1e-20
        assert rows[-1]["entropy_over_T_cubed"] < rows[-2]["entropy_over_T_cubed"] < rows[-3]["entropy_over_T_cubed"]
        for row in rows:
            assert row["independent_entropy"]["entropy"] > 0
            assert row["entropy_over_T_cubed"] == pytest.approx(row["independent_entropy"]["entropy"]/row["T"]**3)


def test_predecessor_and_source_hashes_are_current():
    r = artifact()
    for item in r["evidence_artifacts"]+r["protected_evidence_hashes"]:
        assert hashlib.sha256((M["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    previous = json.loads((M["ROOT"]/M["JOINT_ARTIFACT"]).read_text(encoding="utf-8"))
    assert previous["verification_status"] == "PASS_SCOPED_JOINT_PHI_RESPONSE"
    assert previous["joint_finite_q_complex_pole_computed"] is True


def test_negative_admission_is_not_full_closure_or_global_no_go():
    r = artifact()
    assert all(r["checks"].values())
    assert r["verification_status"] == "PASS_SCOPED_LOW_T_EXCLUSION"
    assert r["closure_level"] == "CLOSED_FOR_LANE"
    assert r["physical_low_T_EOS_admission"] == "BLOCKED_ASYMPTOTIC_SPECTRUM_THERMODYNAMICS_MISMATCH"
    assert len(r["compatibility_assumptions"]) == 4
    assert r["conditional_asymptotic_exclusion_established"] is True
    for flag in ("global_UET_no_go", "source_response_predecessor_invalidated", "phonon_free_energy_added",
                 "mass_repair", "parameter_fitting", "physical_Kubo_emitted", "independent_alpha_Phi_K_admitted",
                 "controlled_truncation_error_established", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock",
                 "core_composition_gate_overwritten", "claim_promotion", "clipping", "IR_filter",
                 "target_source_accessed", "xie_2026_accessed", "C_relabelled_as_charge_or_mass", "R_gen_added_as_state"):
        assert r[flag] is False
    assert r["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert r["excluded_variables"] == ["R_gen","R_obs","nondynamical_A"]
    assert r["thresholds"]["causal_leakage_unchanged"] == 1e-6


def test_report_has_all_major_and_original_fields():
    r = artifact()
    assert set(r["report"]) == {"MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY"}
    assert r["controlling_blocker"] == "gapless_equilibrium_thermal_prescription_not_derived"


def test_audit_does_not_read_measured_source_or_old_pole_answers():
    tree = ast.parse((HERE/"Research_T13_Hartree_Low_T_Validity.py").read_text())
    paths = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("read_text","read_bytes")]
    assert paths
    audit_source = ast.get_source_segment((HERE/"Research_T13_Hartree_Low_T_Validity.py").read_text(), next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == "audit"))
    assert "json.loads((ROOT/JOINT_ARTIFACT).read_text" in audit_source
    assert "Xie" not in audit_source.split('"prior_Xie_context_exposure_review"')[0]
