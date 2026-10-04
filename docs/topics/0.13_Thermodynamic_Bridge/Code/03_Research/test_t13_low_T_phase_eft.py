"""Independent limits and negative controls of the declared new EFT lane."""

from pathlib import Path
import hashlib
import json
from math import pi, sqrt
import re
import runpy

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
M = runpy.run_path(str(ROOT/(PREFIX+"Code/03_Research/Research_T13_Low_T_Phase_EFT.py")))


@pytest.fixture
def example():
    action = M["controls"]()
    state = M["tree_state"](1.05, action=action)
    return action, state, M["rest_coefficients"](state, action)


def test_full_tree_action_stationarity_and_pressure(example):
    a, s, _ = example
    v, phi = sqrt(s["s"]), s["Phi"]
    def potential(vv, pp):
        x = pp-a["Phi_reference"]
        r = s["X"]-a["m0_sq"]+a["gamma"]*x
        return -r*vv*vv/2+a["u"]*vv**4/4+a["epsilon"]*(a["response_mass_sq"]*x*x/2+a["response_quartic"]*x**4/4)
    assert abs(potential(v, phi)+s["pressure_tree"]) < 1e-12
    assert abs(M["finite_difference"](lambda vv: potential(vv, phi), v, 1e-5)) < 1e-9
    assert abs(M["finite_difference"](lambda pp: potential(v, pp), phi, 1e-5)) < 1e-9


def test_tree_phase_chi_is_not_clamped_Phi(example):
    a, s, cf = example
    clamped = s["s"]+2*s["mu"]**2/a["u"]
    assert s["A"] > clamped
    assert cf["c"]**2 == pytest.approx(s["rho"]/s["A"])


def test_full_parent_polynomial_root_matches_schur(example):
    a, s, _ = example
    q = .04
    poly = np.polynomial.Polynomial
    ell = poly([q*q, -1.])
    response = s["V_curvature"]+a["epsilon"]*a["response_kinetic"]*ell
    determinant = ell*(ell+2*a["u"]*s["s"])*response-a["gamma"]**2*s["s"]*ell-4*s["mu"]**2*poly([0., 1.])*response
    roots = determinant.roots()
    assert all(abs(r.imag) < 1e-12 and r.real > 0 for r in roots)
    assert M["acoustic_energy"](q, s, a)**2 == pytest.approx(min(roots.real), rel=1e-9)


def test_decoupled_response_reduces_to_O2_tree(example):
    a, _, _ = example
    a = a | {"gamma": 0.}
    s = M["tree_state"](1.2, action=a)
    cf = M["rest_coefficients"](s, a)
    assert s["Phi"] == pytest.approx(a["Phi_reference"], abs=1e-14)
    assert s["s"] == pytest.approx((1.2**2-a["m0_sq"])/a["u"])
    assert cf["c"]**2 == pytest.approx((1.2**2-a["m0_sq"])/(3*1.2**2-a["m0_sq"]))
    assert cf["A4_h"] == 0


def test_thermal_entropy_envelope_independent_integral(example):
    a, s, cf = example
    t = cf["c"]*cf["dispersion_scale"]/64
    numerical = M["finite_difference"](lambda temp: M["parent_acoustic_pressure"](temp, s, a)["pressure"], t, t*1e-3)
    entropy = M["parent_acoustic_entropy"](t, s, a)["entropy"]
    assert numerical/entropy == pytest.approx(1., rel=1e-5)


def test_T6_bose_moment_coefficient(example):
    _, _, cf = example
    moment, _ = M["quad"](lambda x: x**5*np.exp(-x)/(1-np.exp(-x)), 0., np.inf)
    coefficient = -cf["eta"]*moment/(2*pi*pi*cf["c"]**6)
    assert coefficient == pytest.approx(cf["B6"], rel=1e-10)


def test_relative_flow_partition_equals_covariant_formula(example):
    a, _, _ = example
    s = M["tree_state"](1.05, xi=.04, action=a)
    cs = sqrt(s["c2_rest_at_X"])
    covariant = pi*pi/90*cs*s["X"]**2/(s["X"]-(1-cs*cs)*s["mu"]**2)**2
    assert s["A4_flow"] == pytest.approx(covariant, rel=1e-12)
    assert M["angular_a4"](s)[0] == pytest.approx(covariant, rel=1e-10)


def test_flow_current_and_stiffness_follow_same_pressure(example):
    a, s, _ = example
    h = 1e-4
    pressure = lambda xi: M["tree_state"](s["mu"], xi=xi, action=a)["pressure_tree"]
    assert -M["finite_difference"](pressure, .02, h) == pytest.approx(M["tree_state"](s["mu"], xi=.02, action=a)["s"]*.02, rel=1e-6)
    assert -M["finite_difference"](pressure, 0., h, 2) == pytest.approx(s["rho"], rel=1e-6)


def test_new_kinetic_measurement_is_locally_invertible(example):
    a, s, _ = example
    def eta(z):
        action = a | {"response_kinetic": z}
        return M["rest_coefficients"](M["tree_state"](s["mu"], action=action), action)["eta"]
    intercept = eta(1.)-(eta(2.)-eta(1.))
    slope = eta(2.)-eta(1.)
    assert slope > 0
    assert (eta(.7)-intercept)/slope == pytest.approx(.7, rel=1e-10)
    decoupled = a | {"gamma": 0.}
    s0 = M["tree_state"](s["mu"], action=decoupled)
    assert M["rest_coefficients"](s0, decoupled)["eta"] == M["rest_coefficients"](s0, decoupled | {"response_kinetic": 2.})["eta"]


def test_positive_energy_gyroscopic_parent(example):
    a, s, _ = example
    check = M["parent_energy_check"](.02, s, a)
    assert check["energy_conservation_residual"] < 1e-12
    assert check["kinetic_min_eigenvalue"] > 0
    assert check["potential_min_eigenvalue"] > 0
    assert len(check["positive_mode_frequencies"]) == 3
    assert check["mode_real_growth_max"] < 1e-12


def test_field_coordinate_change_is_not_physical_kinetic_ambiguity(example):
    a, s, cf = example
    transformed = M["rescale_Phi_coordinate"](a, 2.)
    other = M["tree_state"](s["mu"], action=transformed)
    oc = M["rest_coefficients"](other, transformed)
    assert other["Phi"] == pytest.approx(2*s["Phi"])
    assert other["pressure_tree"] == pytest.approx(s["pressure_tree"], rel=1e-12)
    assert oc["eta"] == pytest.approx(cf["eta"], rel=1e-12)
    assert transformed["gamma"]**2*transformed["epsilon"]*transformed["response_kinetic"]/other["V_curvature"]**2 == pytest.approx(a["gamma"]**2*a["epsilon"]*a["response_kinetic"]/s["V_curvature"]**2)


@pytest.mark.parametrize("t", [0., -1., float("nan"), float("inf")])
def test_invalid_temperature_rejected(example, t):
    a, s, _ = example
    with pytest.raises(ValueError):
        M["parent_acoustic_pressure"](t, s, a)


@pytest.mark.parametrize("changes", [{"u": 0.}, {"response_kinetic": -1.}, {"response_mass_sq": .001}])
def test_invalid_or_nonmonotone_inputs_rejected(example, changes):
    a, _, _ = example
    with pytest.raises(ValueError):
        M["tree_state"](1.05, action=a | changes)


@pytest.mark.parametrize("args", [{"mu": .8}, {"mu": 1.05, "xi": 1.05}, {"mu": 1.05, "xi": .2}])
def test_noncondensed_nontimelike_and_negative_energy_flow_rejected(example, args):
    a, _, _ = example
    with pytest.raises(ValueError):
        M["tree_state"](action=a, **args)


def test_artifact_does_not_promote_physics_or_repair_old_branch():
    record = json.loads((ROOT/(PREFIX+"Result/artifacts/t13_low_T_phase_eft.json")).read_text(encoding="utf-8"))
    assert all(record["checks"].values())
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    for key in ("old_Hartree_branch_repaired", "Hartree_internal_mass_reused",
                "phonon_pressure_appended_to_old_Hartree", "external_h_is_state",
                "controlled_full_action_truncation_error_established", "independent_alpha_Phi_K_admitted",
                "physical_Kubo_emitted", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock",
                "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting", "clipping",
                "IR_filter", "cone_padding", "target_source_accessed", "xie_2026_accessed",
                "C_relabelled_as_charge_or_mass", "R_gen_added_as_state"):
        assert record[key] is False
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert record["thresholds"]["original_causal_leakage"] == 1e-6
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    assert len(record["report"]) == 11


@pytest.mark.parametrize("name", ["T13_LOW_T_PHASE_EFT_2026-10-02.md",
                                  "T13_LOW_T_PHASE_EFT_MEASUREMENT_CARD_2026-10-02.md"])
def test_result_notes_match_artifact_and_reporting_contract(name):
    path = ROOT/(PREFIX+"Result/artifacts/"+name)
    content = path.read_text(encoding="utf-8")
    artifact = ROOT/(PREFIX+"Result/artifacts/t13_low_T_phase_eft.json")
    record = json.loads(artifact.read_text(encoding="utf-8"))
    assert hashlib.sha256(artifact.read_bytes()).hexdigest() in content
    for field in record["report"]:
        assert field+":" in content
    for target in re.findall(r"\]\(([^)]+)\)", content):
        if target.startswith("https://"):
            continue
        assert (path.parent/target).is_file(), target
