"""Tests for the conditional Phi/amplitude no-go interface."""

import importlib.util
import json
from pathlib import Path


MODULE = Path(__file__).with_name("Research_T13_He4_Phi_Amplitude_Compatibility.py")
SPEC = importlib.util.spec_from_file_location("t13_phi_amplitude_compatibility", MODULE)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def test_saved_no_go_application_is_scoped_and_reproducible():
    result = AUDIT.audit()
    assert json.loads(AUDIT.OUTPUT.read_text(encoding="utf-8")) == result
    assert result["verification_status"] == "PASS_SCOPED_PHI_ROOT_AMPLITUDE_NO_GO"
    assert result["closure_level"] == "CLOSED_AS_NO_GO"
    assert result["full_core_unlock"] is False
    assert result["dependency_unlocked"] == []
    assert all(result["checks"].values())


def test_amplitude_witnesses_do_not_claim_a_full_UET_no_go():
    result = json.loads(AUDIT.OUTPUT.read_text(encoding="utf-8"))
    assert len(result["representative_mode_witnesses"]) == 3
    assert len(result["one_sided_amplitude_secants"]) == 6
    assert all(row["total_Omega_secant"] > 0 for row in result["one_sided_amplitude_secants"])
    assert "not a universal no-go" in result["claim_boundary"]
