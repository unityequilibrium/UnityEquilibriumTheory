from docs.core.core_paths import canonical_artifact_path
import numpy as np
import pytest
from docs.core.uet_o2_continuum_collision_operator import _weighted_transition_rows, continuum_collision_operator_state
from docs.scripts.audit.audit_topic13_transition_coordinate_map import coordinate_rows


def test_production_pullback_matches_independent_coordinate_identity():
    v=np.array([[1.,-2.],[3.,4.]])
    s=np.array([[.2,.3],[.8,.7]])
    we=np.array([4.,9.]); wb=np.array([16.,25.])
    np.testing.assert_allclose(_weighted_transition_rows(v,s,we,wb),coordinate_rows(v,s,we,wb))
    psi=np.array([2.,5.])
    np.testing.assert_allclose(_weighted_transition_rows(v,s,we,wb)@(np.sqrt(wb)*psi),
                               v@(np.sqrt(we)*(s.T@psi)))


def test_invalid_mapping_fails_before_building():
    with pytest.raises(ValueError,match="unknown transition"):
        continuum_collision_operator_state(.22,.35,.15,_transition_map="unknown")


def test_invalid_weights_rejected():
    with pytest.raises(ValueError):
        _weighted_transition_rows(np.ones((1,2)),np.eye(2),[1.,-1.],[2.,3.])


def test_failed_pilot_cannot_unlock_physical_result():
    import json
    from pathlib import Path
    path=canonical_artifact_path("t13_transition_pullback_pilot.json")
    record=json.loads(path.read_text())
    assert record["completed"] and not record["full_core_unlock"]
    assert record["status"] == "BLOCKED_PULLBACK_NUMERICAL_FAILURE"
    assert len(record["rows"]) == 4
    for row in record["rows"]:
        if row["map"] == "weighted_psi_pullback":
            assert row["status"] == "ERROR"
            assert "kappa" not in row
        else:
            assert row["status"] == "EVALUATED"
