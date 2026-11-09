"""Independent phase-space, direct pressure and known-limit controls."""

from pathlib import Path
import hashlib
import json
from math import pi, sqrt
import runpy

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
M = runpy.run_path(str(ROOT/(PREFIX+"Code/03_Research/Research_T13_Low_T_Interactions.py")))
EFT = M["EFT"]


@pytest.fixture(params=[1.05, 1.2])
def example(request):
    action = EFT.controls()
    state = EFT.tree_state(request.param, action=action)
    return action, state, M["dispersion_coefficients"](state, action), M["vertices"](state, action)


@pytest.mark.parametrize("direction", [(1., 0.), (0., 1.), (1., .7)])
def test_vertices_from_direct_reoptimized_tree_pressure(example, direction):
    a, s, cf, v = example
    t, z = direction
    def pressure(e):
        return EFT.tree_state(s["mu"]-e*t/sqrt(s["A"]), xi=e*z/sqrt(s["A"]), action=a)["pressure_tree"]
    linear = -s["mu"]*s["s"]*t/sqrt(s["A"])
    quadratic = (t*t-cf["c"]**2*z*z)/2
    cubic = v["g_t"]*t**3+v["g_s"]*t*z*z
    quartic = v["h_t"]*t**4+v["h_m"]*t*t*z*z+v["h_s"]*z**4
    e = .01
    if cubic != 0:
        direct3 = ((pressure(e)-pressure(-e))/2-linear*e)/e**3
        assert direct3 == pytest.approx(cubic, rel=1e-3)
    direct4 = ((pressure(e)+pressure(-e))/2-pressure(0)-quadratic*e*e)/e**4
    assert direct4 == pytest.approx(quartic, rel=1e-3, abs=1e-7)


def test_decoupled_quadratic_pressure_has_zero_P3_P4():
    a = EFT.controls() | {"gamma": 0.}
    s = EFT.tree_state(1.2, action=a)
    v = M["vertices"](s, a)
    assert v["P3"] == v["P4"] == 0
    assert v["g_t"] != 0 and v["g_s"] != 0
    assert v["h_t"] == pytest.approx(v["h_s"])
    assert v["h_m"] == pytest.approx(-2*v["h_t"])


def test_dilute_nonrelativistic_Beliaev_known_limit_and_factor_two():
    mass, density, chi = 2.3, .8, 1.4
    c = sqrt(density/(mass*chi))
    gs = 1/(2*mass*sqrt(chi))
    occupation_coefficient = M["decay_leading_coefficient"]({"c": c}, {"g_t": 0., "g_s": gs})
    assert occupation_coefficient/2 == pytest.approx(3/(640*pi*mass*density), rel=1e-12)
    assert occupation_coefficient == pytest.approx(3/(320*pi*mass*density), rel=1e-12)


def test_independent_collinear_phase_space_integral(example):
    _, _, cf, v = example
    g = v["g_t"]+v["g_s"]/cf["c"]**2
    k, c = .01, cf["c"]
    moment = M["quad"](lambda p: p*p*(k-p)**2, 0., k, epsabs=1e-20)[0]
    occupation = 36*g*g*c**3*k*k*moment/(32*pi*c*k*k)
    assert occupation/k**5 == pytest.approx(M["decay_leading_coefficient"](cf, v), rel=1e-12)


def test_exact_tree_kinematic_rate_refinement_and_energy_conservation(example):
    a, s, cf, v = example
    values = [M["decay_phase_space"](k, s, a) for k in (.02, .01, .005)]
    errors = [abs(x["coefficient_q5"]/M["decay_leading_coefficient"](cf, v)-1) for x in values]
    assert errors[2] < errors[1] < errors[0]
    for x in values:
        assert x["gamma_pole"]*2 == x["Gamma_occupation"]
        assert x["minimum_angular_support_margin"] > 0
        assert x["energy_balance_relative_max"] < 1e-10
        assert x["Bose_gain_loss_relative_max"] < 1e-10
    assert values[-1]["gamma_pole_over_omega"] < values[0]["gamma_pole_over_omega"]


def test_T8_coefficient_independent_Bose_integrals(example):
    _, _, cf, _ = example
    assert M["dispersion_pressure_moment"](cf) == pytest.approx(cf["C8_disp"], rel=1e-10)
    moment7 = M["bose_moment"](7)
    derivative_integral = M["quad"](lambda x: x**8*np.exp(-x)/(-np.expm1(-x))**2, 0., np.inf)[0]
    assert derivative_integral == pytest.approx(8*moment7, rel=1e-10)


def test_quartic_subtracted_tensor_contractions(example):
    _, _, cf, v = example
    assert M["wick_quartic_independent"](v, cf["c"]) == pytest.approx(M["quartic_thermal_thermal"](v, cf["c"]), rel=1e-10)
    assert M["quartic_thermal_thermal"]({"h_t": 0., "h_m": 0., "h_s": 0.}, cf["c"]) == 0


def test_free_cubic_vertex_has_zero_decay():
    assert M["decay_leading_coefficient"]({"c": .4}, {"g_t": 0., "g_s": 0.}) == 0


@pytest.mark.parametrize("k,order", [(0., 48), (-1., 48), (float("nan"), 48), (.01, 1), (.01, 2.5)])
def test_invalid_decay_arguments_rejected(example, k, order):
    a, s, _, _ = example
    with pytest.raises(ValueError):
        M["decay_phase_space"](k, s, a, order)


def test_new_artifact_hashes_and_full_scope_boundary():
    r = json.loads((ROOT/(PREFIX+"Result/artifacts/t13_low_T_interactions.json")).read_text())
    assert r["verification_status"] == "PASS_SCOPED_INTERACTION_KERNEL"
    assert r["closure_level"] == "CLOSED_FOR_LANE"
    assert all(r["checks"].values())
    assert len(r["report"]) == 11
    for key in ("full_two_loop_pressure_computed", "quartic_TT_is_total_error_bound", "real_self_energy_computed",
                "finite_q_complete_decay_computed", "finite_T_collision_computed", "assigned_damping_width", "full_SK_KMS_matching_closed",
                "controlled_full_action_truncation_error_established", "independent_alpha_Phi_K_admitted",
                "physical_Kubo_emitted", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock",
                "core_composition_gate_overwritten", "claim_promotion", "old_Hartree_branch_repaired",
                "parameter_fitting", "clipping", "cone_padding", "target_source_accessed", "xie_2026_accessed"):
        assert r[key] is False
    assert r["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert r["thresholds"]["original_causal_leakage"] == 1e-6
    for e in r["evidence_artifacts"]+r["protected_evidence_hashes"]:
        assert hashlib.sha256((ROOT/e["path"]).read_bytes()).hexdigest() == e["sha256"]
    previous = r["protected_evidence_hashes"][0]
    assert previous["sha256"] == "050aceb4f94f3534929d8c59c75da4dda8efe16ce7aec250a34f6f8b5868dcb7"
    registry = json.loads((ROOT/M["REGISTRY"]).read_text())
    assert r["equation_registry_ids"] == [e["id"] for e in registry["entries"]]
    assert registry["core_registry_modified"] is False


def test_audit_file_access_excludes_holdout_and_external_numeric_source(monkeypatch):
    accessed = []
    original_bytes, original_text = Path.read_bytes, Path.read_text
    def checked_bytes(path):
        accessed.append(path.resolve())
        assert "xie" not in path.name.lower()
        return original_bytes(path)
    def checked_text(path, *args, **kwargs):
        accessed.append(path.resolve())
        assert "xie" not in path.name.lower()
        return original_text(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_bytes", checked_bytes)
    monkeypatch.setattr(Path, "read_text", checked_text)
    r = M["audit"]()
    allowed = {(ROOT/e["path"]).resolve() for e in r["evidence_artifacts"]+r["protected_evidence_hashes"]}
    assert accessed and set(accessed) <= allowed
    assert all(r["checks"].values())
