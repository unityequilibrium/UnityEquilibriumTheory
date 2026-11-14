"""Boundary tests for the Topic 0.13 dimensional-observable gate."""

from docs.scripts.audit.audit_uet_main_theory_dimensional_observable import build_artifacts


def test_dimensional_gate_blocks_without_fabricating_calibration() -> None:
    audit, gate = build_artifacts()
    assert audit["audit_status"] == "PASS_ACCOUNTING"
    assert gate["dimensional_observable_status"] == "BLOCKED"
    assert gate["track_status"]["o2_he4_core_ready"] == "CLOSED_FOR_CORE"
    assert gate["track_status"]["legacy_graphite_ttg_external_validation"] == "BLOCKED"
    assert audit["checks"]["o2_he4_core_ready"] is True
    assert gate["holdout_status"] == "LOCKED_UNCONSUMED"
    assert gate["claim_promotion"] is False


def test_all_three_controlling_gaps_remain_explicit() -> None:
    _, gate = build_artifacts()
    assert set(gate["controlling_blockers"]) == {
        "legacy_graphite_ttg_numeric_source_package_missing",
        "legacy_graphite_alpha_phi_k_independent_calibration_missing",
        "legacy_graphite_thermal_prearrival_leakage_gate_failed",
    }
