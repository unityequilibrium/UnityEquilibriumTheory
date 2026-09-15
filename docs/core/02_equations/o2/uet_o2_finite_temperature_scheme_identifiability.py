"""Finite-counterterm identifiability boundary for the O(2) thermal action."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class FiniteTemperatureSchemeWitness:
    """One finite local counterterm completion in natural units."""

    name: str
    finite_coefficient: float
    reference_mass_sq: float
    scale_sq: float
    reference_value: float
    reference_first_derivative: float
    reference_second_derivative: float
    off_reference_value: float
    off_reference_first_derivative: float
    off_reference_second_derivative: float
    unit_lane: str = "natural"
    coefficient_origin: str = "underdetermined_finite_local_counterterm"


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def finite_local_counterterm(
    mass_sq: float,
    reference_mass_sq: float,
    scale_sq: float,
    finite_coefficient: float,
) -> tuple[float, float, float]:
    """Return a finite local potential term and its first two mass derivatives.

    The cubic subtraction is zero through second order at the declared
    reference point, but changes the off-reference finite-temperature action.
    The reference scale supplies the natural-unit dimension of the local term.
    """

    mass_sq = _finite(mass_sq, "mass_sq")
    reference_mass_sq = _finite(reference_mass_sq, "reference_mass_sq")
    scale_sq = _positive(scale_sq, "scale_sq")
    finite_coefficient = _finite(finite_coefficient, "finite_coefficient")
    delta = mass_sq - reference_mass_sq
    value = finite_coefficient * delta**3 / scale_sq
    first = 3.0 * finite_coefficient * delta**2 / scale_sq
    second = 6.0 * finite_coefficient * delta / scale_sq
    return float(value), float(first), float(second)


def finite_temperature_scheme_witnesses(
    *,
    reference_mass_sq: float = 0.5,
    off_reference_mass_sq: float = 0.65,
    scale_sq: float | None = None,
) -> tuple[FiniteTemperatureSchemeWitness, FiniteTemperatureSchemeWitness]:
    """Build two admissible scheme completions with shared reference conditions."""

    reference_mass_sq = _positive(reference_mass_sq, "reference_mass_sq")
    off_reference_mass_sq = _positive(off_reference_mass_sq, "off_reference_mass_sq")
    scale_sq = reference_mass_sq if scale_sq is None else _positive(scale_sq, "scale_sq")
    witnesses = []
    for name, coefficient in (("scheme_A", 0.0), ("scheme_B", 0.75)):
        reference = finite_local_counterterm(
            reference_mass_sq,
            reference_mass_sq,
            scale_sq,
            coefficient,
        )
        off_reference = finite_local_counterterm(
            off_reference_mass_sq,
            reference_mass_sq,
            scale_sq,
            coefficient,
        )
        witnesses.append(
            FiniteTemperatureSchemeWitness(
                name=name,
                finite_coefficient=coefficient,
                reference_mass_sq=reference_mass_sq,
                scale_sq=scale_sq,
                reference_value=reference[0],
                reference_first_derivative=reference[1],
                reference_second_derivative=reference[2],
                off_reference_value=off_reference[0],
                off_reference_first_derivative=off_reference[1],
                off_reference_second_derivative=off_reference[2],
            )
        )
    return tuple(witnesses)  # type: ignore[return-value]


def finite_temperature_scheme_identifiability_contract() -> dict[str, Any]:
    """Return the no-go scope and the named-branch boundary."""

    return {
        "status": "SCOPED_FINITE_TEMPERATURE_SCHEME_IDENTIFIABILITY_BOUNDARY",
        "equations": {
            "finite_local_counterterm": "Delta V_a(x)=a*(x-x_*)^3/Lambda_*^2",
            "reference_conditions": "Delta V_a(x_*)=partial_x Delta V_a(x_*)=partial_x^2 Delta V_a(x_*)=0",
            "off_reference_difference": "Delta V_a(x)!=0 for a!=0 and x!=x_*",
            "named_hartree_branch": "M^2=m_eff^2(Phi)+(N+2)*lambda*I_T(M^2;T,mu)",
        },
        "units": {
            "unit_lane": "natural",
            "x_and_x_star": "mass squared",
            "Lambda_star_sq": "mass squared",
            "Delta_V": "energy density",
            "finite_coefficient": "dimensionless local scheme parameter",
        },
        "derivation_class": "algebraic finite-local-counterterm identifiability no-go under shared second-order reference conditions",
        "observable": "difference between admissible off-reference finite-temperature action completions; no physical observable emitted",
        "data_role": "INTERNAL_STRUCTURAL_NO_GO_NO_SOURCE_ROWS_OR_HOLDOUT",
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective response variable; not temperature",
            "R_gen": "derived history trace only; not an independent state",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "claim_boundary": "This closes only the non-uniqueness of the finite local renormalization completion under the currently declared reference conditions. It does not provide a physical counterterm, select a microscopic scheme, or close the Hartree branch, transport, KMS, SI map, alpha_Phi_K, or Full Topic 13.",
    }


__all__ = [
    "FiniteTemperatureSchemeWitness",
    "finite_local_counterterm",
    "finite_temperature_scheme_witnesses",
    "finite_temperature_scheme_identifiability_contract",
]
