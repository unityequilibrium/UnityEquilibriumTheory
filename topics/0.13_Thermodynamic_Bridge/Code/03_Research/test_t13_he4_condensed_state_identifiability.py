"""Regression checks for the scoped condensed-state selection boundary."""

import hashlib
import importlib.util
from pathlib import Path

import numpy as np

from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_finite_density_eos import o2_equilibrium_state


SOURCE = Path(__file__).with_name("Research_T13_He4_Condensed_State_Identifiability.py")
SPEC = importlib.util.spec_from_file_location("he4_condensed_state_identifiability", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
AUDIT = MODULE.audit()


def test_two_stable_natural_candidates_are_not_physical_heii_matches():
    assert AUDIT["verification_status"] == "PASS_SCOPED_CONDENSED_STATE_SELECTION_BOUNDARY"
    assert all(AUDIT["checks"].values())
    first, second = AUDIT["witnesses"]
    assert first["tree_charge_density"] < second["tree_charge_density"]
    assert first["tree_goldstone_speed_sq"] < second["tree_goldstone_speed_sq"]
    assert first["alpha_phi_t_natural"] != second["alpha_phi_t_natural"]
    assert all(w["quadrature_relative_span"] < 1e-4 for w in (first, second))
    assert all(w["response_refinement_relative_change"] < 1e-3 for w in (first, second))
    assert not first["physical_HeII_state_admitted"]
    assert not second["physical_HeII_state_admitted"]
    assert AUDIT["dependency_unlocked"] == []
    assert AUDIT["full_core_unlock"] is False


def test_charge_monotonicity_identity_on_condensed_witnesses():
    eos = natural_bridge_config().eos
    kinetic = eos.matter.matter_kinetic
    quartic = eos.matter.matter_quartic
    phi = AUDIT["fixed_inputs"]["space_response_natural"]
    m2 = AUDIT["fixed_inputs"]["tree_mass_sq_at_fixed_phi"]
    for witness in AUDIT["witnesses"]:
        mu = witness["mu_natural"]
        h = 1e-5
        derivative = (
            o2_equilibrium_state(mu + h, phi, eos).charge_density
            - o2_equilibrium_state(mu - h, phi, eos).charge_density
        ) / (2 * h)
        analytic = kinetic * (3 * kinetic * mu**2 - m2) / quartic
        assert analytic > 0
        assert np.isclose(derivative, analytic, rtol=1e-9)


def test_embedded_evidence_hashes_match_current_sources():
    for entry in AUDIT["evidence_artifacts"]:
        path = MODULE.ROOT / entry["path"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
