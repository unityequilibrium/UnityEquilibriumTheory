from __future__ import annotations

from pathlib import Path
import sys


RESEARCH_DIR = Path(__file__).resolve().parent
if str(RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(RESEARCH_DIR))

from Research_T13_PhiE_Lane_Composition_Boundary import build_audit


def test_cross_lane_phi_e_coordinates_are_not_silently_identified() -> None:
    result = build_audit()
    units = result["f3_units"]

    assert units["Phi_E_field"] == 1
    assert units["Phi_E_energy"] == 0
    assert units["kappa_E_required"] == -1
    assert "OPEN" in result["f2_physical_correspondence"]["map_status"]


def test_both_conditional_alpha_routes_close_only_after_explicit_map() -> None:
    result = build_audit()

    assert result["f3_units"]["alpha_Phi_base"] == 1
    assert result["f3_units"]["alpha_energy_composition"] == 1
    assert "not asserted" in result["equation_or_mapping"]["cross_route_equality"]


def test_material_residue_coupling_and_same_state_inputs_remain_open() -> None:
    result = build_audit()

    assert result["checks"]["physical_field_residue_remains_open"]
    assert result["checks"]["physical_strain_coupling_is_absent_from_current_action"]
    assert "same_state" in " ".join(result["what_remains_open"])


def test_no_physical_alpha_or_dependency_is_promoted() -> None:
    result = build_audit()

    assert result["numeric_alpha_Phi_K_emitted"] is False
    assert result["full_core_unlock"] is False
    assert result["claim_promotion"] is False
    assert result["holdout_use"]["blind_eligibility"] == (
        "REVIEW_REQUIRED_AFTER_SESSION_EXPOSURE"
    )


def test_all_f0_f4_boundary_checks_pass() -> None:
    result = build_audit()

    assert all(result["checks"].values())
    assert result["verification_status"] == (
        "PASS_SCOPED_PHI_E_LANE_COMPOSITION_BOUNDARY"
    )
