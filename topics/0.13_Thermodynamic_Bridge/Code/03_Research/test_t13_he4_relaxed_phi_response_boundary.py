"""Tests for the conditional relaxed-Phi response boundary."""

import importlib.util
import json
from pathlib import Path

import pytest


MODULE = Path(__file__).with_name("Research_T13_He4_Relaxed_Phi_Response_Boundary.py")
SPEC = importlib.util.spec_from_file_location("t13_relaxed_phi_response", MODULE)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def test_saved_local_response_witness_is_non_promoting():
    result = AUDIT.audit()
    assert json.loads(AUDIT.OUTPUT.read_text(encoding="utf-8")) == result
    assert result["verification_status"] == "PASS_SCOPED_RELAXED_RESPONSE_NONIDENTIFIABILITY"
    assert result["full_core_unlock"] is False
    assert result["dependency_unlocked"] == []
    first, second = result["synthetic_local_completions"]
    assert first["chi_clamped_natural"] == second["chi_clamped_natural"]
    assert first["chi_relaxed_natural"] > second["chi_relaxed_natural"]
    assert first["Omega_PhiPhi_at_anchor"] == 1.0
    assert second["Omega_PhiPhi_at_anchor"] == 2.0
    flat = result["declared_flat_partial_action_probe"]
    assert flat["Omega_Phi_at_anchor"] != 0.0
    assert flat["status"] == "NONSTATIONARY_AT_CONDITIONAL_ROOT_FOR_DECLARED_FLAT_PARTIAL_POTENTIAL"
    assert all(result["checks"].values())


def test_positive_curvature_required():
    with pytest.raises(ValueError):
        AUDIT._completion({"p_phi": 0.0, "p_phiphi": 0.0, "p_muphi": 1.0, "p_mumu": 1.0}, 0.0, 1.0)
