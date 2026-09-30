"""Independent EFT/action and linear algebra checks of the conditional map."""

import hashlib
import json
from math import isclose
from pathlib import Path
import runpy

import numpy as np
import pytest

MODULE = runpy.run_path(str(Path(__file__).with_name("Research_T13_Conditional_TwoFluid_Operator.py")))
ROOT, OUTPUT = MODULE["ROOT"], MODULE["OUTPUT"]
causal_stiffness_interval = MODULE["causal_stiffness_interval"]
coefficients, modes, pressure_jet = (MODULE[k] for k in ("coefficients", "modes", "pressure_jet"))
COMPARATOR = runpy.run_path(str(Path(__file__).with_name("Research_T13_Funding_RestEOS_Dynamic_Degeneracy.py")))
longitudinal_state = COMPARATOR["longitudinal_state"]


def assert_numeric_reproduction(actual, saved):
    if isinstance(saved, dict):
        assert actual.keys() == saved.keys()
        for key in saved:
            assert_numeric_reproduction(actual[key], saved[key])
    elif isinstance(saved, list):
        assert len(actual) == len(saved)
        for left, right in zip(actual, saved):
            assert_numeric_reproduction(left, right)
    elif isinstance(saved, float):
        # Hessian cancellation varies slightly between Windows and Linux libm.
        assert isclose(actual, saved, rel_tol=1e-6, abs_tol=1e-9)
    else:
        assert actual == saved


def test_pressure_hessian_map_recovers_existing_analytic_eft():
    jet = pressure_jet(lambda t, mu: t**4 / 4 + mu**2, 1., 1., 1e-4)
    for stiffness in (.1, .2):
        mapped = coefficients(1., 1., jet, stiffness)
        existing = longitudinal_state(1., 1., stiffness)
        for key in mapped:
            assert mapped[key] == pytest.approx(existing[key], rel=2e-7, abs=1e-8)
        assert modes(mapped)["speed_sq"] == pytest.approx(
            [existing["speed_sq_low"], existing["speed_sq_high"]], rel=2e-7
        )


def test_independent_F_derivatives_cancel_stiffness_derivatives_and_xi_fourth_order():
    b, y, t, fs = .8, 1.1, .7, .2
    jet = {"s": b, "n": .6, "a_p_TT": 1.5, "h_p_Tmu": .3, "c_p_mumu": 2.}
    expected = coefficients(t, y, jet, fs)

    def action(vec):
        entropy, x, chem = vec
        db, dy = entropy - b, chem - y
        f0 = (-t * db + jet["n"] * dy - db**2 / (2 * jet["a_p_TT"])
              + jet["h_p_Tmu"] / jet["a_p_TT"] * db * dy
              + .5 * (jet["c_p_mumu"] - jet["h_p_Tmu"]**2 / jet["a_p_TT"]) * dy**2)
        relative_flow = x + chem**2
        g = -fs / 2 + .07 * db - .11 * dy
        return f0 + g * relative_flow + .13 * relative_flow**2

    anchor = np.array([b, -y*y, y])
    h = 1e-4
    basis = np.eye(3) * h
    first = [(action(anchor + v) - action(anchor - v)) / (2*h) for v in basis]
    second = np.array([
        [(action(anchor + u + v) - action(anchor + u - v)
          - action(anchor - u + v) + action(anchor - u - v)) / (4*h*h)
         for v in basis] for u in basis
    ])
    fb, fx, fy = first
    independent = {
        "K_N": fy*y - fb*b, "G_N": -second[0, 0]*b*b,
        "K_S": (second[2, 2] - 2*fx)*y*y - 4*second[2, 1]*y**3 + 4*second[1, 1]*y**4,
        "G_S": -2*fx*y*y,
        "M": second[0, 2]*b*y - fy*y - 2*second[0, 1]*b*y*y,
    }
    assert independent == pytest.approx(expected, rel=2e-6, abs=1e-7)


def test_analytic_interval_agrees_with_direct_modes_without_selecting_stiffness():
    jet = {"s": 1., "n": 2., "a_p_TT": 3., "h_p_Tmu": 0., "c_p_mumu": 2.}
    interval = causal_stiffness_interval(1., 1., jet)
    assert interval["exists"]
    for fs in np.linspace(.01, 2.99, 40):
        expected = interval["f_s_lower_exclusive"] < fs < interval["f_s_upper_exclusive"]
        state = modes(coefficients(1., 1., jet, fs))
        assert state["subluminal"] == bool(expected)
    upper = interval["f_s_upper_exclusive"]
    assert max(modes(coefficients(1., 1., jet, upper))["speed_sq"]) == pytest.approx(1.)


def test_recorded_domain_rejection_and_physical_boundaries_are_preserved():
    record = json.loads(OUTPUT.read_text(encoding="utf-8"))
    current = MODULE["audit"]()
    assert {k: v for k, v in current.items() if k != "examples"} == {
        k: v for k, v in record.items() if k != "examples"
    }
    assert_numeric_reproduction(current["examples"], record["examples"])
    assert all(e["reference"]["modes"]["secular_relative_residual"] < 1e-12
               for e in current["examples"])
    required = {"major_result_id", "topic", "closure_level", "what_is_closed",
                "equation_or_mapping", "units", "derivation_class", "observable",
                "data_role", "evidence_artifacts", "verification_status",
                "open_blockers", "dependency_unlocked", "claim_boundary"}
    assert required <= record.keys()
    plan = json.loads((ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/funding_portfolio_14d_plan.json").read_text(encoding="utf-8"))
    linked = plan["conditional_operator_evidence_2026_10_01"]
    assert hashlib.sha256((ROOT / linked["path"]).read_bytes()).hexdigest() == linked["sha256"]
    assert linked["verification_status"] == record["verification_status"]
    assert record["verification_status"] == "FAIL_CONDITIONAL_OPERATOR_SCREEN"
    first, second = record["examples"]
    assert first["reference"]["modes"]["speed_sq"][1] > 1.
    assert second["reference"]["modes"]["subluminal"]
    for example in record["examples"]:
        assert example["step_last_relative_change"] < record["refinement_tolerance"]
        assert example["quadrature_last_relative_change"] < record["refinement_tolerance"]
        assert example["causal_stiffness_interval"]["root_classification_agrees"]
        assert not example["physical_HeII_state_admitted"]
    for key in ("g1_physical_unlock", "g2_science_unlock", "full_core_unlock",
                "claim_promotion", "xie_2026_accessed", "parameter_fitting"):
        assert record[key] is False
    assert record["finite_T_stiffness_numeric_value_emitted"] is False
    for evidence in record["evidence_hashes"]:
        assert hashlib.sha256((ROOT / evidence["path"]).read_bytes()).hexdigest() == evidence["sha256"]


def test_nonpositive_thermal_curvature_is_rejected():
    with pytest.raises(ValueError):
        coefficients(.2, 1., {"s": 1., "n": 1., "a_p_TT": 0., "h_p_Tmu": 0., "c_p_mumu": 1.}, .1)


def test_reproduction_comparison_rejects_meaningful_numeric_or_status_drift():
    assert_numeric_reproduction({"root": 1.821912968}, {"root": 1.821912967})
    with pytest.raises(AssertionError):
        assert_numeric_reproduction({"root": 1.82}, {"root": 1.81})
    with pytest.raises(AssertionError):
        assert_numeric_reproduction({"subluminal": True}, {"subluminal": False})
