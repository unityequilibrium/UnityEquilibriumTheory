"""Tests for Wave 11 downstream dependency decisions."""

from docs.scripts.audit.audit_uet_downstream_unlock import build_artifacts


def test_only_phase_internal_diagnostic_is_unlocked() -> None:
    audit, wave = build_artifacts()
    assert audit["audit_status"] == "PASS"
    assert wave["downstream_unlock_status"] == "BLOCKED_EXCEPT_PHASE_INTERNAL_DIAGNOSTIC"
    assert audit["decisions"]["phase_internal_diagnostic"]["status"] == "PASS_INTERNAL_ONLY"


def test_external_gravity_galaxy_and_particle_lanes_remain_blocked() -> None:
    audit, _ = build_artifacts()
    for lane in ("thermal_external_comparison", "phase_external_or_universality", "gravity_orbit", "galaxy_cosmology", "particle_dirac"):
        assert audit["decisions"][lane]["status"] == "BLOCKED"
