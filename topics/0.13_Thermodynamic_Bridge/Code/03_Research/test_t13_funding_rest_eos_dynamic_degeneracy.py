"""Check the restricted rest-EOS versus sound-stiffness witness."""

import importlib.util
import json
from pathlib import Path


SOURCE = Path(__file__).with_name("Research_T13_Funding_RestEOS_Dynamic_Degeneracy.py")
SPEC = importlib.util.spec_from_file_location("t13_rest_eos_dynamic_degeneracy", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_same_rest_eos_different_stable_sound_speeds():
    audit = MODULE.audit()
    assert all(audit["checks"].values())
    assert audit["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["g1_physical_unlock"] is False
    assert audit["g2_science_unlock"] is False
    assert audit["full_core_unlock"] is False
    assert audit["xie_2026_accessed"] is False
    for b, y in ((0.5, 0.8), (1.0, 1.0), (1.5, 1.2)):
        first = MODULE.rest_state(b, y, MODULE.ZETA_VALUES[0])
        second = MODULE.rest_state(b, y, MODULE.ZETA_VALUES[1])
        for key in (
            "F",
            "pressure",
            "charge_density",
            "entropy_density",
            "temperature",
            "energy_density",
        ):
            assert abs(first[key] - second[key]) < 1e-12
        for state in (first, second):
            assert abs(
                state["energy_density"] + state["pressure"]
                - state["temperature"] * state["entropy_density"]
                - y * state["charge_density"]
            ) < 1e-12
    assert audit == json.loads(MODULE.OUTPUT.read_text(encoding="utf-8"))


def test_relative_flow_curvature_is_the_explicit_missing_input():
    audit = MODULE.audit()
    values = [item["rest_state"]["relative_flow_curvature_minus_2_F_X"] for item in audit["examples"]]
    assert values == list(MODULE.ZETA_VALUES)
    low = [item["longitudinal_state"]["speed_sq_low"] for item in audit["examples"]]
    assert low[0] != low[1]
    assert all(item["longitudinal_state"]["positive_quadratic_energy"] for item in audit["examples"])
    near_normal = MODULE.longitudinal_state(1.0, 1.0, 1e-6)
    assert abs(near_normal["speed_sq_low"] / 1e-6 - 1.0 / 14.0) < 1e-5
    assert abs(near_normal["speed_sq_high"] - 7.0 / 9.0) < 1e-5


def test_conditional_tree_correspondence_does_not_admit_heii():
    mapping = MODULE.conditional_core_tree_mapping()
    assert mapping["frozen_q"] < 0.0
    assert mapping["frozen_f_s_tree"] == 0.0
    assert len(mapping["candidate_tree_states"]) == 2
    assert all(item["f_s_tree"] > 0.0 for item in mapping["candidate_tree_states"])
    assert all(
        item["physical_HeII_state_admitted"] is False
        for item in mapping["candidate_tree_states"]
    )
    assert mapping["finite_T_physical_correspondence_admitted"] is False
    assert mapping["SI_or_HeII_material_map_admitted"] is False
