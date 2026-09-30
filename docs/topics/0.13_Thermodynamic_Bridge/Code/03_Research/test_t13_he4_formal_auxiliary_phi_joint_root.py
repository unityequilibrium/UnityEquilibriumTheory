"""Tests for the fixed-prescription formal auxiliary joint root."""

import importlib.util
import json
import math
from pathlib import Path


MODULE = Path(__file__).with_name("Research_T13_He4_Formal_Auxiliary_Phi_Joint_Root.py")
SPEC = importlib.util.spec_from_file_location("t13_formal_auxiliary_phi_root", MODULE)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def _assert_same_with_fp_tolerance(actual, saved):
    if isinstance(actual, dict):
        assert actual.keys() == saved.keys()
        for key in actual:
            _assert_same_with_fp_tolerance(actual[key], saved[key])
    elif isinstance(actual, list):
        assert len(actual) == len(saved)
        for current, recorded in zip(actual, saved):
            _assert_same_with_fp_tolerance(current, recorded)
    elif isinstance(actual, float):
        assert math.isclose(actual, saved, rel_tol=1e-12, abs_tol=1e-13)
    else:
        assert actual == saved


def test_saved_formal_root_is_reproducible_and_scoped():
    result = AUDIT.audit()
    _assert_same_with_fp_tolerance(result, json.loads(AUDIT.OUTPUT.read_text(encoding="utf-8")))
    assert result["verification_status"] == "PASS_FORMAL_AUXILIARY_PHI_JOINT_ROOT"
    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert result["full_core_unlock"] is False
    assert result["dependency_unlocked"] == []
    assert all(result["checks"].values())


def test_formal_route_cannot_be_transplanted_to_normalized_root():
    result = json.loads(AUDIT.OUTPUT.read_text(encoding="utf-8"))
    config = result["reference_config"]
    assert config["Z_prior_normalized"] == 1.0
    assert config["Z_auxiliary"] > 1.0
    assert config["normalized_domain_rejection"] == "auxiliary-field condensed lane requires Z > 1"
    assert "not a microscopic" in json.loads(AUDIT.AUXILIARY_AUDIT.read_text(encoding="utf-8"))["major_result"]["claim_boundary"]
    assert len(result["temperature_and_resolution_records"]) == 6
    assert len(result["off_root_envelope_witnesses"]) == 6
    assert all(abs(row["analytic_Phi_residual"] - row["profiled_Phi_derivative_fd"]) < 1e-7
               for row in result["off_root_envelope_witnesses"])
    assert "No Xie 2026 holdout was used" in result["claim_boundary"]
