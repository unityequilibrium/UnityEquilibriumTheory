"""Checks for the frozen He-4/O(2) branch-admissibility result."""

import importlib.util
from pathlib import Path

import numpy as np

from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_finite_density_eos import condensate_control, o2_equilibrium_state


SOURCE = Path(__file__).with_name("Research_T13_He4_Frozen_Branch_Compatibility.py")
SPEC = importlib.util.spec_from_file_location("he4_frozen_branch_compatibility", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_frozen_state_and_physical_anchor_have_incompatible_branch_roles():
    result = MODULE.audit()
    assert result["verification_status"] == "PASS_SCOPED_FROZEN_STATE_BRANCH_MISMATCH"
    assert all(result["checks"].values())
    assert result["frozen_natural_state"]["branch"] == "normal"
    assert result["frozen_natural_state"]["condensate_amplitude"] == 0
    assert result["physical_anchor"]["phase"] == "He II"
    assert result["physical_anchor"]["superfluid_fraction"] > 0
    assert result["checks"]["static_and_collision_lanes_exclude_complete_two_fluid_transport"]
    assert result["full_core_unlock"] is False


def test_tree_boundaries_solve_the_declared_branch_control():
    result = MODULE.audit()["frozen_natural_state"]
    config = natural_bridge_config().eos
    mu = result["chemical_potential"]
    phi = result["space_response"]
    assert np.isclose(
        condensate_control(result["mu_critical_at_frozen_phi"], phi, config),
        0.0, atol=1e-12,
    )
    assert np.isclose(
        condensate_control(mu, result["phi_critical_at_frozen_mu"], config),
        0.0, atol=1e-12,
    )
    assert o2_equilibrium_state(mu, phi, config).branch == "normal"
    assert o2_equilibrium_state(result["mu_critical_at_frozen_phi"] + 1e-4,
                                phi, config).branch == "condensed"


def test_a_small_local_phi_probe_does_not_cross_branch():
    state = MODULE.audit()["frozen_natural_state"]
    config = natural_bridge_config().eos
    for displacement in (-0.001, 0.0, 0.001):
        assert o2_equilibrium_state(
            state["chemical_potential"], state["space_response"] + displacement,
            config,
        ).branch == "normal"
