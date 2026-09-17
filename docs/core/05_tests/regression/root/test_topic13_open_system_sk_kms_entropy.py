from __future__ import annotations

import numpy as np

from docs.core.uet_o2_open_system_sk_kms import (
    OpenSystemParameters,
    formal_entropy_production,
    kms_correlators,
    noise_kernel,
    open_system_sk_contract,
    retarded_poles,
)


def test_open_system_kms_and_fdt_identity() -> None:
    parameters = OpenSystemParameters(beta_th=4.0, kappa=1.2, chi=0.8, gamma=0.3)
    for omega in (0.15, 0.4, 1.7):
        correlators = kms_correlators(omega, parameters)
        assert np.isclose(correlators["kms_ratio"], correlators["kms_target"])
        assert np.isclose(noise_kernel(omega, parameters), correlators["noise"])
        assert correlators["rho"] >= 0.0


def test_retarded_poles_and_entropy_witness() -> None:
    parameters = OpenSystemParameters(beta_th=4.0, kappa=1.2, chi=0.8, gamma=0.3)
    assert np.max(np.imag(retarded_poles(parameters))) <= 1.0e-12
    assert formal_entropy_production(0.0, 0.25, parameters) == 0.0
    assert formal_entropy_production(1.1, 0.25, parameters) > 0.0


def test_contract_preserves_ontology_and_physical_boundary() -> None:
    contract = open_system_sk_contract()
    assert "not mass or charge" in contract["ontology"]["C"]
    assert "not new physical fields" in contract["ontology"]["Phi"]
    assert "no backreaction" in contract["ontology"]["R_gen"]
    assert "physical Kubo provenance" in contract["scope"]["open"]
    assert "alpha_Phi_K" in contract["scope"]["open"]
