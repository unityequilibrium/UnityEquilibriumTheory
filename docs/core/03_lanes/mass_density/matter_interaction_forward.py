"""Forward matter-source to relational-interaction comparator.

This module makes the direction of the correspondence explicit:

    independent matter source + geometry
        -> density observable and relational C coordinate
        -> standard interaction potential
        -> force and acceleration

It is intentionally a standard-physics comparator.  It does not define C as mass,
does not infer a matter amplitude from C, and does not add an extra UET force.  A
future UET response law must be declared as a separate constitutive lane.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .mass_density_correspondence import (
    MassDensityLaneConfig,
    integrated_density,
    mass_density_from_point_masses,
)
from docs.core.relational_two_body_baseline import (
    RelationalBaselineConfig,
    TwoBodyState,
    accelerations,
    force_on_a,
    interaction_coordinate,
    interaction_energy,
    interaction_energy_from_coordinate,
)


Vector2 = Tuple[float, float]

FORWARD_MAPPING_STATUS = "STANDARD_COMPARATOR_ONLY"
UET_EXTRA_RESPONSE_STATUS = "BLOCKED_MISSING_CONSTITUTIVE_LAW"


@dataclass(frozen=True)
class MatterSource:
    """Independent matter/amplitude input for the normalized comparator."""

    mass_a: float = 1.0
    mass_b: float = 1.0


@dataclass(frozen=True)
class MatterInteractionForwardConfig:
    """Normalized source-to-interaction configuration.

    ``G``, masses, distances, and density are code-unit quantities.  The module
    deliberately rejects an SI label until a dimensional source and observable
    contract is supplied.
    """

    G: float = 1.0
    separation_reference: float = 2.0
    density_lane: MassDensityLaneConfig = field(
        default_factory=MassDensityLaneConfig
    )
    unit_lane: str = "normalized_comparator"


@dataclass(frozen=True)
class MatterInteractionForwardResult:
    """All layers of one forward-comparator evaluation."""

    interaction_coordinate: float
    density: List[float]
    density_dx: float
    density_integral: float
    interaction_energy: float
    interaction_energy_from_coordinate: float
    force_on_a: Vector2
    acceleration_on_a: Vector2
    mapping_status: str = FORWARD_MAPPING_STATUS
    extra_uet_response_status: str = UET_EXTRA_RESPONSE_STATUS


def _baseline_config(
    source: MatterSource, config: MatterInteractionForwardConfig
) -> RelationalBaselineConfig:
    return RelationalBaselineConfig(
        G=config.G,
        mass_a=source.mass_a,
        mass_b=source.mass_b,
        separation_reference=config.separation_reference,
        steps=0,
    )


def matter_to_interaction_forward(
    state: TwoBodyState,
    source: MatterSource,
    config: MatterInteractionForwardConfig | None = None,
) -> MatterInteractionForwardResult:
    """Map an independent matter source to the declared standard interaction.

    The source masses determine the density amplitude and the standard interaction
    amplitude.  Geometry determines the normalized relational coordinate ``C``.
    Thus the function tests the forward direction without asserting the inverse
    relation ``rho=f(C)``.
    """

    config = config or MatterInteractionForwardConfig()
    if config.unit_lane != "normalized_comparator":
        raise ValueError(
            "only normalized_comparator is supported until the source/SI contract is closed"
        )
    if config.G <= 0.0:
        raise ValueError("G must be positive in the normalized comparator")
    if config.separation_reference <= 0.0:
        raise ValueError("separation_reference must be positive")
    if source.mass_a <= 0.0 or source.mass_b <= 0.0:
        raise ValueError("source masses must be positive")

    baseline = _baseline_config(source, config)
    density, dx = mass_density_from_point_masses(
        state,
        source.mass_a,
        source.mass_b,
        config.density_lane,
    )
    coordinate = interaction_coordinate(
        state,
        config.separation_reference,
    )
    energy = interaction_energy(state, baseline)
    energy_from_coordinate = interaction_energy_from_coordinate(state, baseline)
    force = force_on_a(state, baseline)
    acceleration_a, _ = accelerations(state, baseline)
    return MatterInteractionForwardResult(
        interaction_coordinate=coordinate,
        density=density,
        density_dx=dx,
        density_integral=integrated_density(density, dx),
        interaction_energy=energy,
        interaction_energy_from_coordinate=energy_from_coordinate,
        force_on_a=force,
        acceleration_on_a=acceleration_a,
    )


__all__ = [
    "FORWARD_MAPPING_STATUS",
    "UET_EXTRA_RESPONSE_STATUS",
    "MatterInteractionForwardConfig",
    "MatterInteractionForwardResult",
    "MatterSource",
    "matter_to_interaction_forward",
]
