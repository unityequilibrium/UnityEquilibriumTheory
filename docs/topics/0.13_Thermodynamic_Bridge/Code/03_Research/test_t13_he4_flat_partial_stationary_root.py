"""Tests for the conditional flat partial-action stationary root."""

import importlib.util
import json
from pathlib import Path

import pytest


MODULE = Path(__file__).with_name("Research_T13_He4_Flat_Partial_Stationary_Root.py")
SPEC = importlib.util.spec_from_file_location("t13_flat_partial_root", MODULE)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def test_saved_stationary_root_is_conditional_and_non_promoting():
    result = AUDIT.audit()
    assert json.loads(AUDIT.OUTPUT.read_text(encoding="utf-8")) == result
    assert result["verification_status"] == "PASS_CONDITIONAL_FLAT_PARTIAL_STATIONARY_ROOT"
    assert result["full_core_unlock"] is False
    assert result["dependency_unlocked"] == []
    assert all(result["checks"].values())


def test_new_root_does_not_validate_recycled_density():
    result = json.loads(AUDIT.OUTPUT.read_text(encoding="utf-8"))
    fine = result["runs"][1]
    assert fine["joint_phi"] != result["prior_anchor"]["Phi_natural"]
    assert fine["old_mu_fixed_stationary_density"] != result["prior_anchor"]["target_natural_charge"]
    assert fine["joint_branch"] == "condensed"
    assert fine["effective_Phi_curvature"] > 0
    assert "CIRCULAR" in result["data_role"]


def test_bracket_without_sign_change_is_rejected():
    config = AUDIT.natural_bridge_config()
    with pytest.raises(ValueError):
        AUDIT._stationary_phi(0.22, 1.85568856925511, 5e-4, replace_with_zero_coupling(config))


def replace_with_zero_coupling(config):
    from dataclasses import replace

    response = replace(config.eos.response, epsilon_nc=0.0)
    eos = replace(config.eos, response=response)
    return replace(config, eos=eos)
