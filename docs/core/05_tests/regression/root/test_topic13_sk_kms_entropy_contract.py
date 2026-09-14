"""Unit checks for the formal Topic 13 SK/KMS/entropy interface."""

from __future__ import annotations

import numpy as np
import pytest

from docs.core.thermal_sk_kms_entropy_contract import (
    entropy_production_witness,
    sk_kms_noise_kernel,
    thermal_sk_kms_entropy_contract,
)


def test_kms_and_entropy_witnesses_are_positive() -> None:
    value = sk_kms_noise_kernel(2.0e20, 1.0e-22, 0.7)
    entropy = entropy_production_witness(np.array([-0.2, 0.4]), np.array([[1.2, 0.15], [0.15, 0.8]]))
    assert value > 0.0
    assert entropy >= 0.0


def test_non_psd_onsager_matrix_is_rejected() -> None:
    with pytest.raises(ValueError, match="positive semidefinite"):
        entropy_production_witness(np.array([1.0, 0.0]), np.array([[1.0, 2.0], [2.0, 1.0]]))


def test_contract_preserves_ontology_and_beta_separation() -> None:
    contract = thermal_sk_kms_entropy_contract()
    assert "collective system-behaviour coordinate" in contract["C_meaning"]
    assert "effective Phi" in contract["sk_field_meaning"]
    assert "no backreaction" in contract["R_gen_meaning"]
    assert "not beta_th" in contract["beta_T13_relation"]
