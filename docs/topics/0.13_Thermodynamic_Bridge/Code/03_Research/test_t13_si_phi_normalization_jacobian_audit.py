from __future__ import annotations

from pathlib import Path
import sys


RESEARCH_DIR = Path(__file__).resolve().parent
if str(RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(RESEARCH_DIR))

from Research_T13_SI_Phi_Normalization_Jacobian_Audit import build_audit


def test_normalized_alpha_contains_field_scale_jacobian() -> None:
    result = build_audit()
    equation = result["equation_or_mapping"]["normalized_derivative_chain_rule"]

    assert "Phi_scale_nat" in equation
    assert result["chain_rule_witness"]["normalized_to_covariant_derivative_ratio"] == 3.0


def test_existing_converter_is_not_misrepresented_as_normalized_alpha() -> None:
    result = build_audit()

    assert result["checks"]["si_helper_has_no_field_scale_argument"]
    assert result["checks"]["existing_alpha_formula_omits_phi_scale_jacobian"]
    assert result["numeric_alpha_Phi_K_emitted"] is False


def test_physical_scale_and_derivative_coordinate_remain_open() -> None:
    result = build_audit()

    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert "Phi_scale_nat" in " ".join(result["what_remains_open"])
    assert result["derivative_coordinate_resolution"]["o2_action_coordinate"] == (
        "covariant Phi passed as space_response"
    )
    assert result["derivative_coordinate_resolution"]["o2_action_natural_mass_dimension"] == 1
    assert result["derivative_coordinate_resolution"]["map_status"] == (
        "OPEN_SOURCE_BACKED_PHI_SCALE_MISSING"
    )
    assert result["dependency_unlocked"].startswith("None")


def test_holdout_and_target_inputs_are_not_used() -> None:
    result = build_audit()

    assert result["target_data_used"] is False
    assert result["parameter_fitting_performed"] is False
    assert result["holdout_use"]["numeric_payload_consumed_by_this_local_audit"] is False
    assert result["holdout_use"]["blind_eligibility"] == (
        "REVIEW_REQUIRED_AFTER_SESSION_EXPOSURE"
    )


def test_all_boundary_checks_pass() -> None:
    result = build_audit()

    assert all(result["checks"].values())
    assert result["report"]["STATUS"] == (
        "PASS_SCOPED_SI_PHI_NORMALIZATION_JACOBIAN_BOUNDARY"
    )
