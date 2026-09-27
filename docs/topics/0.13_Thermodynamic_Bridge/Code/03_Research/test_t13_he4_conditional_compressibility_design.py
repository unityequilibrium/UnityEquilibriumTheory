"""Focused checks for the conditional He-4 response independence design."""

import hashlib
import importlib.util
from pathlib import Path

import numpy as np


SOURCE = Path(__file__).with_name("Research_T13_He4_Conditional_Compressibility_Design.py")
SPEC = importlib.util.spec_from_file_location("he4_conditional_compressibility", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
AUDIT = MODULE.audit()


def test_compressibility_is_a_conditional_independent_response_not_a_fit():
    assert AUDIT["verification_status"] == "PASS_SCOPED_CONDITIONAL_COMPRESSIBILITY_DESIGN"
    assert all(AUDIT["checks"].values())
    assert AUDIT["full_core_unlock"] is False
    assert AUDIT["dependency_unlocked"] == []
    assert AUDIT["data_role"] == "SYNTHETIC_CONDITIONAL_DESIGN_NO_PHYSICAL_RESPONSE_ROW"


def test_chain_rule_response_and_density_scale_cancellation():
    response = AUDIT["conditional_response"]
    assert response["kappa_T_clamped_Phi_per_Pa"] > 0
    assert np.isclose(response["n_E_mu_kappa"], response["chi_nat_over_n_nat"])
    assert "d_mu Phi" in AUDIT["equation_or_mapping"]["relaxed_phi_correction"]
    assert "Phi_clamp_or_relaxed_response_law_missing" in AUDIT["open_blockers"]
    for witness in AUDIT["synthetic_rescalings"]:
        assert np.isclose(witness["dimensionless_n_E_mu_kappa"], response["chi_nat_over_n_nat"])
    assert AUDIT["local_rank_witness"]["determinant_refinement_difference"] < abs(
        AUDIT["local_rank_witness"]["determinant_step_5e_minus_4"]
    ) / 10


def test_saved_inputs_are_current_and_no_holdout_is_used():
    paths = [entry["path"] for entry in AUDIT["evidence_artifacts"]]
    assert not any("xie" in path.lower() for path in paths)
    for entry in AUDIT["evidence_artifacts"]:
        path = MODULE.ROOT / entry["path"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
