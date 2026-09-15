"""Weighted angular rule reaches susceptibility and conserved moments."""
from docs.core.core_paths import core_root
import numpy as np
import pytest
from docs.core.uet_o2_energy_momentum_conserving_bethe_salpeter import (
    _moment_direction_rule, energy_momentum_conserving_bs_state,
)
from docs.scripts.audit.audit_topic13_direction_moments import candidate14, moments


def test_named_rule_matches_independent_derivation():
    d, w = _moment_direction_rule("axis_cube14")
    expected_d, expected_w = candidate14()
    np.testing.assert_array_equal(d, expected_d)
    np.testing.assert_array_equal(w, expected_w)
    assert moments(d, w)["quadrupole_rank"] == 5
    with pytest.raises(ValueError):
        _moment_direction_rule("unknown")


@pytest.fixture(scope="module")
def states():
    kwargs = dict(radial_order=8, collision_integration_order=24, angular_order=24,
                  bs_frequency_over_rate=(), kms_frequency_over_temperature=())
    return [energy_momentum_conserving_bs_state(.22, .35, .15, **kwargs,
                                               _direction_rule=rule)
            for rule in ("axis6", "axis_cube14")]


def test_weights_reach_actual_state_without_changing_radial_measure(states):
    a, b = states
    wa = np.asarray(a.susceptibility_weights).reshape(2, 8, 6)
    wb = np.asarray(b.susceptibility_weights).reshape(2, 8, 14)
    np.testing.assert_allclose(wa.sum(axis=2), wb.sum(axis=2), rtol=1e-14)
    np.testing.assert_allclose(wb / wb.sum(axis=2, keepdims=True),
                               np.broadcast_to(_moment_direction_rule("axis_cube14")[1], wb.shape))
    assert (a.state_count, b.state_count) == (96, 224)


def test_weighted_projector_preserves_five_invariants_and_shear(states):
    for state in states:
        p = np.asarray(state.projector)
        inv = np.asarray(state.conserved_invariants)
        np.testing.assert_allclose(p @ inv, 0, atol=1e-12)
        assert state.invariant_rank == 5
        momentum = np.asarray(state.state_momenta)
        shear = momentum[:, 0] * momentum[:, 1] * np.sqrt(state.susceptibility_weights)
        if state.direction_count == 14:
            assert np.linalg.norm(shear) > 0
            np.testing.assert_allclose(p @ shear, shear, atol=1e-12)
        else:
            assert np.linalg.norm(shear) == 0


def test_full_path_artifact_keeps_failed_isotropy_visible():
    import json
    from pathlib import Path
    artifact = core_root() / "artifacts/t13_weighted_direction_pilot.json"
    record = json.loads(artifact.read_text())
    assert record["completed"] and not record["full_core_unlock"]
    a, b = record["rows"]
    assert a["rule"] == "axis6" and b["rule"] == "axis_cube14"
    assert (a["state_count"], b["state_count"]) == (96, 224)
    assert b["shear_xy_source_norm"] > 0
    assert not b["original_gates"]["isotropy"]
    assert all(row["original_gates"]["entropy"] for row in record["rows"])
    assert record["dependency_unlocked"] == []
