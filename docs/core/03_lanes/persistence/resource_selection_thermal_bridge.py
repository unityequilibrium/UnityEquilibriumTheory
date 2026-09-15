"""Explicit normalized bridge from interaction costs to a thermal ledger proxy.

This module does not identify C with temperature.  It maps the already declared
behavior and maintenance costs to a declared normalized dissipated-work ledger,
then reports the isothermal bath proxy

    Delta S_bath_proxy = Q_dissipated / T_bath

The scale and bath temperature are lane inputs, never fitted by this verifier.
A dimensional SI map remains open.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from docs.core.uet_resource_selection import (
    ResourceSelectionConfig,
    ResourceSelectionResult,
    simulate_resource_selection,
)

RESOURCE_THERMAL_BRIDGE_MODE = "resource_selection_thermal_bridge_v1"
RESOURCE_THERMAL_BRIDGE_STATUS = "PASS_WITH_OPEN_THERMAL_MAPPING"


@dataclass(frozen=True)
class ResourceThermalBridgeConfig:
    """Declared normalized work/heat bookkeeping for one comparator lane."""

    behavior_to_work_scale: float = 1.0
    maintenance_to_work_scale: float = 1.0
    bath_temperature: float = 1.0
    unit_lane: str = "normalized"

    def __post_init__(self) -> None:
        values = (
            self.behavior_to_work_scale,
            self.maintenance_to_work_scale,
            self.bath_temperature,
        )
        if not all(isfinite(float(value)) and float(value) > 0.0 for value in values):
            raise ValueError("thermal bridge scales and bath_temperature must be finite and positive")
        if self.unit_lane != "normalized":
            raise NotImplementedError(
                "resource thermal bridge v1 supports only unit_lane='normalized'"
            )


@dataclass(frozen=True)
class ResourceThermalSummary:
    """One interaction trajectory expressed in the declared thermal ledger."""

    behavior_heat_proxy: float
    maintenance_heat_proxy: float
    dissipated_work_proxy: float
    bath_entropy_proxy: float
    resource_decline_proxy: float
    ledger_closure_residual: float
    persistence_time: float | None


@dataclass(frozen=True)
class ResourceThermalBridgeResult:
    """Comparison of two declared interaction structures."""

    cooperative: ResourceThermalSummary
    conflict: ResourceThermalSummary
    status: str = RESOURCE_THERMAL_BRIDGE_STATUS
    mapping_status: str = "BLOCKED_OPEN_SI_WORK_HEAT_ENTROPY_MAP"


def summarize_resource_thermal_ledger(
    result: ResourceSelectionResult,
    config: ResourceThermalBridgeConfig,
) -> ResourceThermalSummary:
    """Map normalized declared costs to work and a bath entropy proxy."""

    behavior_heat = config.behavior_to_work_scale * result.behavior_work
    maintenance_heat = config.maintenance_to_work_scale * result.maintenance_work
    dissipated = behavior_heat + maintenance_heat
    entropy_proxy = dissipated / config.bath_temperature
    resource_decline = (
        result.available_resource[0]
        - result.available_resource[-1]
        - result.external_net_work
    )
    return ResourceThermalSummary(
        behavior_heat_proxy=behavior_heat,
        maintenance_heat_proxy=maintenance_heat,
        dissipated_work_proxy=dissipated,
        bath_entropy_proxy=entropy_proxy,
        resource_decline_proxy=resource_decline,
        ledger_closure_residual=resource_decline - dissipated,
        persistence_time=result.persistence_time,
    )


def run_resource_selection_thermal_bridge(
    cooperative_config: ResourceSelectionConfig,
    conflict_config: ResourceSelectionConfig,
    horizon: float,
    dt: float,
    config: ResourceThermalBridgeConfig | None = None,
) -> ResourceThermalBridgeResult:
    """Run two deterministic interaction lanes through the declared ledger map."""

    config = config or ResourceThermalBridgeConfig()
    cooperative = simulate_resource_selection(cooperative_config, horizon, dt)
    conflict = simulate_resource_selection(conflict_config, horizon, dt)
    return ResourceThermalBridgeResult(
        cooperative=summarize_resource_thermal_ledger(cooperative, config),
        conflict=summarize_resource_thermal_ledger(conflict, config),
    )


__all__ = [
    "RESOURCE_THERMAL_BRIDGE_MODE",
    "RESOURCE_THERMAL_BRIDGE_STATUS",
    "ResourceThermalBridgeConfig",
    "ResourceThermalSummary",
    "ResourceThermalBridgeResult",
    "summarize_resource_thermal_ledger",
    "run_resource_selection_thermal_bridge",
]