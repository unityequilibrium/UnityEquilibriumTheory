"""Formal finite-temperature two-sector thermodynamic split for Topic 13.

This module separates the declared O(2) quasiparticle pressure into a tree
condensate sector and a thermal quasiparticle sector. The split closes only
thermodynamic identities in natural units. It does not define a Landau normal
mass density, a transverse current response, a Kubo coefficient, or an SI
observable map.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    condensate_control,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    finite_temperature_o2_state,
    quasiparticle_pressure,
)


FORMAL_TWO_SECTOR_STATUS = "PASS_FORMAL_TWO_SECTOR_THERMODYNAMIC_CONSISTENCY"


@dataclass(frozen=True)
class FormalTwoSectorState:
    """Thermodynamic sectors on a fixed ``(T, mu, Phi)`` state point."""

    branch: str
    temperature: float
    chemical_potential: float
    space_response: float
    total_pressure: float
    condensate_pressure: float
    normal_pressure: float
    total_charge_density: float
    condensate_charge_density: float
    normal_charge_density: float
    total_entropy_density: float
    condensate_entropy_density: float
    normal_entropy_density: float
    total_energy_density: float
    condensate_energy_density: float
    normal_energy_density: float
    total_susceptibility: float
    condensate_susceptibility: float
    normal_susceptibility: float
    data_role: str = "ACTION_DERIVED_FORMAL_TWO_SECTOR_THERMODYNAMICS"


def _central(function, value: float, step: float) -> float:
    h = step * max(1.0, abs(float(value)))
    return (float(function(value + h)) - float(function(value - h))) / (2.0 * h)


def _condensate_pressure(
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
) -> float:
    q = condensate_control(chemical_potential, space_response, config)
    if q <= config.branch_tolerance:
        return 0.0
    return float(q * q / (4.0 * config.matter.matter_quartic))


def condensate_pressure(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
) -> float:
    """Return the explicit tree condensate pressure; temperature is a label."""

    del temperature
    config = config or FiniteTemperatureO2QuasiparticleConfig()
    return _condensate_pressure(chemical_potential, space_response, config.eos)


def normal_quasiparticle_pressure(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
) -> float:
    """Return total pressure minus the explicit tree condensate pressure."""

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    total = quasiparticle_pressure(
        temperature, chemical_potential, space_response, config
    )
    return float(
        total
        - condensate_pressure(
            temperature, chemical_potential, space_response, config
        )
    )


def formal_two_sector_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
) -> FormalTwoSectorState:
    """Evaluate the formal condensate/normal thermodynamic decomposition.

    ``normal_charge_density`` is a thermodynamic quasiparticle charge
    derivative. It is intentionally not named or used as a transverse normal
    mass density.
    """

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    base = finite_temperature_o2_state(
        temperature, chemical_potential, space_response, config
    )
    step = config.derivative_step
    p_s = lambda t, mu: condensate_pressure(t, mu, space_response, config)
    p_n = lambda t, mu: normal_quasiparticle_pressure(t, mu, space_response, config)

    p_s_value = p_s(temperature, chemical_potential)
    p_n_value = p_n(temperature, chemical_potential)
    n_s = _central(lambda mu: p_s(temperature, mu), chemical_potential, step)
    n_n = _central(lambda mu: p_n(temperature, mu), chemical_potential, step)
    s_s = _central(lambda t: p_s(t, chemical_potential), temperature, step)
    s_n = _central(lambda t: p_n(t, chemical_potential), temperature, step)
    chi_s = _central(
        lambda mu: _central(lambda nested: p_s(temperature, nested), mu, step),
        chemical_potential,
        step,
    )
    chi_n = _central(
        lambda mu: _central(lambda nested: p_n(temperature, nested), mu, step),
        chemical_potential,
        step,
    )
    e_s = -p_s_value + temperature * s_s + chemical_potential * n_s
    e_n = -p_n_value + temperature * s_n + chemical_potential * n_n
    values = (
        p_s_value,
        p_n_value,
        n_s,
        n_n,
        s_s,
        s_n,
        e_s,
        e_n,
        chi_s,
        chi_n,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("formal two-sector split produced a non-finite value")
    return FormalTwoSectorState(
        branch=base.branch,
        temperature=base.temperature,
        chemical_potential=base.chemical_potential,
        space_response=base.space_response,
        total_pressure=base.pressure,
        condensate_pressure=p_s_value,
        normal_pressure=p_n_value,
        total_charge_density=base.charge_density,
        condensate_charge_density=n_s,
        normal_charge_density=n_n,
        total_entropy_density=base.entropy_density,
        condensate_entropy_density=s_s,
        normal_entropy_density=s_n,
        total_energy_density=base.energy_density,
        condensate_energy_density=e_s,
        normal_energy_density=e_n,
        total_susceptibility=base.susceptibility,
        condensate_susceptibility=chi_s,
        normal_susceptibility=chi_n,
    )


def formal_two_sector_contract() -> dict[str, object]:
    """Return the equations and boundary of the formal two-sector lane."""

    return {
        "status": FORMAL_TWO_SECTOR_STATUS,
        "equations": {
            "pressure_split": "p_2sector = p_condensate + p_normal",
            "charge_split": "n_i = partial_mu p_i; n = n_condensate + n_normal",
            "entropy_split": "s_condensate = partial_T p_condensate = 0; s = s_normal",
            "energy_split": "epsilon_i = -p_i + T*s_i + mu*n_i; epsilon = sum_i epsilon_i",
            "susceptibility_split": "chi_i = partial_mu n_i; chi = chi_condensate + chi_normal",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "pressure_energy_density": "natural energy density",
            "charge_entropy_density": "natural density",
            "normal_density_label": "thermodynamic quasiparticle charge derivative, not Landau mass density",
            "sector_derivative_sign_policy": (
                "condensate and normal charge/energy entries are signed derivatives "
                "of their declared grand-pressure sectors; positivity is required "
                "for the total thermodynamic state and the static transverse response, "
                "not for a residual sector label"
            ),
            "Phi": "effective response input; not temperature",
            "C": "not relabeled as charge density",
            "R_gen": "derived history trace only; not a state or feedback term",
        },
        "closed_scope": "formal thermodynamic decomposition of the declared tree-condensate plus thermal-quasiparticle EOS",
        "excluded_scope": "transverse normal current response, Landau normal density, interacting self-energy, physical Kubo coefficients, microscopic SK/KMS matching, heat-flux closure, SI Phi map, alpha_Phi_K, and TTG validation",
        "data_role": "ACTION_DERIVED_FORMAL_TWO_SECTOR_THERMODYNAMICS",
        "claim_boundary": "This lane closes only sector-wise thermodynamic identities in natural units. It is not a complete finite-temperature two-fluid transport theory or external validation.",
    }


__all__ = [
    "FORMAL_TWO_SECTOR_STATUS",
    "FormalTwoSectorState",
    "condensate_pressure",
    "normal_quasiparticle_pressure",
    "formal_two_sector_state",
    "formal_two_sector_contract",
]
