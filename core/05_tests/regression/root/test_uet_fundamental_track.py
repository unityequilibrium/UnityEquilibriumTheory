"""Boundary tests for the non-blocking fundamental-unification track."""

from docs.scripts.audit.audit_uet_fundamental_track import build_artifacts


def test_fundamental_track_is_blocked_without_blocking_eft() -> None:
    inventory, gate = build_artifacts()
    assert gate["audit_status"] == "PASS_ACCOUNTING"
    assert gate["fundamental_unification_status"] == "HYPOTHESIS_TRACK_BLOCKED"
    assert gate["primary_eft_dependency"] == "NON_BLOCKING"
    assert inventory["components"]["neutrino_positron_uet_identity"]["status"] == "REJECTED_UNDERIVED"


def test_symmetry_unitarity_and_renormalization_gaps_are_explicit() -> None:
    _, gate = build_artifacts()
    assert set(gate["controlling_blockers"]) == {
        "local_gauge_symmetry", "dirac_spinor_action", "c_p_t_cpt",
        "anomaly_cancellation", "renormalization", "mass_generation",
    }
