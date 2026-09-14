from docs.core.uet_o2_finite_temperature_normal_component import (
    thermodynamic_normal_component_contract,
    thermodynamic_normal_component_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


def test_thermodynamic_normal_component_is_explicit_and_suppressed_at_low_temperature() -> None:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=96,
        cutoff_factor=55.0,
    )
    normal_high = thermodynamic_normal_component_state(0.22, 0.35, 0.15, config)
    normal_low = thermodynamic_normal_component_state(0.06, 0.35, 0.15, config)
    condensed_high = thermodynamic_normal_component_state(0.20, 1.28, 0.15, config)
    condensed_low = thermodynamic_normal_component_state(0.04, 1.28, 0.15, config)

    assert normal_high.branch == "normal"
    assert condensed_high.branch == "condensed"
    assert normal_high.normal_entropy_density >= 0.0
    assert condensed_high.normal_entropy_density >= 0.0
    assert normal_low.normal_entropy_density < normal_high.normal_entropy_density
    assert condensed_low.normal_entropy_density < condensed_high.normal_entropy_density
    assert normal_low.normal_momentum_susceptibility < normal_high.normal_momentum_susceptibility
    assert condensed_low.normal_momentum_susceptibility < condensed_high.normal_momentum_susceptibility


def test_normal_component_keeps_physical_flow_and_si_boundaries_open() -> None:
    contract = thermodynamic_normal_component_contract()
    assert contract["unit_contract"]["unit_lane"] == "natural"
    assert "physical normal-fluid mass density" in contract["excluded_scope"]
    assert "retarded physical Kubo coefficient" in contract["excluded_scope"]
    assert "SI Phi normalization and alpha_Phi_K" in contract["excluded_scope"]
