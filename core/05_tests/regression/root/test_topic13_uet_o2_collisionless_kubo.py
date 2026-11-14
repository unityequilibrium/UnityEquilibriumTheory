from __future__ import annotations

import pytest

from docs.core.uet_o2_collisionless_kubo import (
    COLLISIONLESS_KUBO_STATUS,
    collisionless_kubo_contract,
    collisionless_kubo_witness,
    drude_spectral_density,
    regulated_kubo_dc_coefficient,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


def test_collisionless_witness_exposes_drude_no_go() -> None:
    witness = collisionless_kubo_witness(
        0.22,
        0.35,
        0.15,
        FiniteTemperatureO2QuasiparticleConfig(
            quadrature_order=96,
            cutoff_factor=55.0,
        ),
    )
    assert witness.drude_weight > 0.0
    assert witness.collisionless_dc_is_finite is False
    assert witness.physical_coefficient_emitted is False
    assert witness.regulated_dc_coefficients[0] < witness.regulated_dc_coefficients[-1]
    assert witness.regulated_dc_coefficients[-1] / witness.regulated_dc_coefficients[0] == pytest.approx(100.0)


def test_drude_spectral_density_has_positive_broadened_peak() -> None:
    witness = collisionless_kubo_witness(0.22, 0.35, 0.15)
    value = drude_spectral_density(0.2, 0.01, witness.drude_weight)
    assert value > 0.0
    assert drude_spectral_density(0.0, 0.01, witness.drude_weight) == 0.0
    assert regulated_kubo_dc_coefficient(0.01, witness.drude_weight) == pytest.approx(
        witness.drude_weight / 0.01
    )


def test_contract_keeps_physical_transport_open() -> None:
    contract = collisionless_kubo_contract()
    assert contract["status"] == COLLISIONLESS_KUBO_STATUS
    assert "no finite K_DC" in contract["equations"]["collisionless_limit"]
    assert "interaction collision kernel" in contract["scope"]["open"]
    assert "not temperature" in contract["units"]["Phi"]
