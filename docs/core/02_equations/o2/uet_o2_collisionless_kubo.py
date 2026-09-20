"""Collisionless Kubo boundary for the Topic 13 O(2) response lane.

The existing static transverse response is a positive equilibrium witness, but
it does not contain a collision kernel.  This module makes the resulting
transport boundary explicit: a collisionless current has a zero-width Drude
peak, so the DC Kubo coefficient is not a finite derived number.  A positive
width is shown only as a diagnostic regulator and is never treated as a
physical coefficient.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_formal_transverse_response import (
    formal_transverse_quasiparticle_response,
)


COLLISIONLESS_KUBO_STATUS = "PASS_COLLISIONLESS_KUBO_DC_NO_GO"


@dataclass(frozen=True)
class CollisionlessKuboWitness:
    """A finite-temperature normal-branch Drude-boundary witness."""

    temperature: float
    chemical_potential: float
    space_response: float
    drude_weight: float
    diagnostic_widths: tuple[float, ...]
    regulated_dc_coefficients: tuple[float, ...]
    collisionless_dc_is_finite: bool = False
    physical_coefficient_emitted: bool = False
    data_role: str = "ACTION_DERIVED_COLLISIONLESS_KUBO_NO_GO"


def _finite_positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return result


def drude_spectral_density(
    omega: float,
    diagnostic_width: float,
    drude_weight: float,
) -> float:
    """Return the positive-frequency broadened Drude spectral density."""

    width = _finite_positive(diagnostic_width, "diagnostic_width")
    weight = _finite_positive(drude_weight, "drude_weight")
    frequency = float(omega)
    if not isfinite(frequency) or frequency < 0.0:
        raise ValueError("omega must be finite and non-negative")
    return 2.0 * weight * frequency * width / (width * width + frequency * frequency)


def regulated_kubo_dc_coefficient(
    diagnostic_width: float,
    drude_weight: float,
) -> float:
    """Return the diagnostic ``D/gamma`` coefficient for a nonzero width."""

    return _finite_positive(drude_weight, "drude_weight") / _finite_positive(
        diagnostic_width,
        "diagnostic_width",
    )


def collisionless_kubo_witness(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    diagnostic_widths: tuple[float, ...] = (1.0e-1, 1.0e-2, 1.0e-3),
) -> CollisionlessKuboWitness:
    """Evaluate the collisionless Drude boundary on the normal branch.

    For a positive Drude weight ``D`` and a diagnostic width ``gamma > 0``,
    the regulated Kubo coefficient is ``D / gamma``.  The width is not
    derived here; it is varied only to demonstrate that the collisionless
    limit has no finite DC value.
    """

    widths = tuple(_finite_positive(value, "diagnostic_width") for value in diagnostic_widths)
    if len(widths) < 2:
        raise ValueError("at least two diagnostic widths are required")
    if any(left <= right for left, right in zip(widths, widths[1:])):
        raise ValueError("diagnostic_widths must decrease toward the collisionless limit")
    config = config or FiniteTemperatureO2QuasiparticleConfig()
    response = formal_transverse_quasiparticle_response(
        temperature,
        chemical_potential,
        space_response,
        config,
    )
    drude_weight = _finite_positive(
        response.normal_momentum_susceptibility,
        "normal-branch Drude weight",
    )
    coefficients = tuple(
        regulated_kubo_dc_coefficient(width, drude_weight) for width in widths
    )
    if not all(isfinite(value) and value > 0.0 for value in coefficients):
        raise FloatingPointError("regulated collisionless Kubo coefficients are invalid")
    return CollisionlessKuboWitness(
        temperature=float(temperature),
        chemical_potential=float(chemical_potential),
        space_response=float(space_response),
        drude_weight=drude_weight,
        diagnostic_widths=widths,
        regulated_dc_coefficients=coefficients,
    )


def collisionless_kubo_contract() -> dict[str, object]:
    """Return the equations, units, and non-promotion boundary."""

    return {
        "status": COLLISIONLESS_KUBO_STATUS,
        "equations": {
            "collisionless_conductivity": "sigma(omega;gamma)=D/(gamma-i*omega)",
            "retarded_spectral_density": "rho_JJ(omega;gamma)=2*D*omega*gamma/(gamma^2+omega^2)",
            "dc_kubo_limit": "K_DC(gamma)=1/2 lim_{omega->0} rho_JJ/omega=D/gamma",
            "collisionless_limit": "gamma->0^+ gives a zero-width Drude peak and no finite K_DC",
            "drude_weight": "D=chi_perp_qp from the declared static normal response witness",
        },
        "units": {
            "unit_lane": "natural",
            "drude_weight": "formal natural-unit response weight",
            "diagnostic_width": "formal inverse-time/energy unit",
            "regulated_coefficient": "formal response-coefficient unit; diagnostic only",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": "action-derived static response plus exact Drude-limit boundary; no collision kernel",
        "observable": "finite-temperature normal retarded-current transport boundary",
        "data_role": "INTERNAL_STRUCTURAL_NO_GO_NO_SOURCE_ROWS",
        "scope": {
            "closed": "collisionless normal response cannot yield a finite DC Kubo coefficient",
            "open": "interaction collision kernel, microscopic self-energy/width, matched retarded correlator, SI map, alpha_Phi_K, and TTG validation",
        },
        "claim_boundary": "This is a scoped collisionless no-go. Diagnostic widths are regulators only; no physical transport coefficient, SI observable, alpha_Phi_K, or external validation is emitted.",
    }


__all__ = [
    "COLLISIONLESS_KUBO_STATUS",
    "CollisionlessKuboWitness",
    "drude_spectral_density",
    "regulated_kubo_dc_coefficient",
    "collisionless_kubo_witness",
    "collisionless_kubo_contract",
]
