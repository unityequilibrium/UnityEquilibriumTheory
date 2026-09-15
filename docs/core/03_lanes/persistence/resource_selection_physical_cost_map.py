"""Opt-in dimensional contract for resource-selection costs.

The dynamic-game lane produces normalized behavior and maintenance work.  This
module does not infer a joule scale from those values.  A physical map must
provide an independently derived or source-locked energy scale for each cost
channel, provenance, uncertainty, and a measurement-operator identifier.
Incomplete or fitted records are rejected before conversion.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

PHYSICAL_COST_MAP_OPERATOR_MODE = "resource_selection_physical_cost_map_v1"
PHYSICAL_COST_MAP_STATUS = "BLOCKED_OPEN_INDEPENDENT_CALIBRATION"


class PhysicalCostMapValidationError(ValueError):
    """Raised when a dimensional cost map is incomplete or non-physical."""


@dataclass(frozen=True)
class PhysicalCostMapRecord:
    """Provenance-bearing map from normalized work to integrated SI heat."""

    map_id: str
    material_or_system: str
    behavior_energy_scale_j: float | None = None
    maintenance_energy_scale_j: float | None = None
    bath_temperature_k: float | None = None
    source_locator: str = ""
    source_hash: str = ""
    uncertainty_record: str = ""
    measurement_operator_id: str = ""
    parameter_origin: str = "open"
    unit_lane: str = "si_contract"
    status: str = "OPEN"

    def validate_contract(self, *, require_ready: bool = False) -> None:
        """Validate the contract, optionally requiring a usable physical map."""

        if not self.map_id or not self.material_or_system:
            raise PhysicalCostMapValidationError(
                "map_id and material_or_system are required"
            )
        if self.unit_lane != "si_contract":
            raise PhysicalCostMapValidationError(
                "v1 requires unit_lane='si_contract'"
            )
        if self.parameter_origin == "fit":
            raise PhysicalCostMapValidationError(
                "fitted cost scales cannot be promoted to a physical map"
            )
        if self.parameter_origin not in {"open", "derived", "external_source", "test_fixture"}:
            raise PhysicalCostMapValidationError(
                "parameter_origin must be open, derived, external_source, or test_fixture"
            )
        if not require_ready:
            return

        required = {
            "behavior_energy_scale_j": self.behavior_energy_scale_j,
            "maintenance_energy_scale_j": self.maintenance_energy_scale_j,
            "bath_temperature_k": self.bath_temperature_k,
            "source_locator": self.source_locator,
            "source_hash": self.source_hash,
            "uncertainty_record": self.uncertainty_record,
            "measurement_operator_id": self.measurement_operator_id,
        }
        missing = [key for key, value in required.items() if value in (None, "")]
        if missing:
            raise PhysicalCostMapValidationError(
                "ready physical map missing: " + ", ".join(missing)
            )
        if self.parameter_origin == "open":
            raise PhysicalCostMapValidationError(
                "ready physical map requires derived or external_source provenance"
            )
        numeric = (
            self.behavior_energy_scale_j,
            self.maintenance_energy_scale_j,
            self.bath_temperature_k,
        )
        if not all(isfinite(float(value)) and float(value) > 0.0 for value in numeric):
            raise PhysicalCostMapValidationError(
                "energy scales and bath temperature must be finite and positive"
            )

    def require_ready(self) -> None:
        self.validate_contract(require_ready=True)


@dataclass(frozen=True)
class PhysicalCostMapResult:
    """Integrated heat and isothermal bath entropy in SI units."""

    heat_j: float
    entropy_j_per_k: float
    measurement_operator_id: str
    map_id: str


def map_normalized_work_to_si(
    behavior_work: float,
    maintenance_work: float,
    record: PhysicalCostMapRecord,
) -> PhysicalCostMapResult:
    """Convert declared normalized work only through a ready map."""

    record.require_ready()
    if not all(
        isfinite(float(value)) and float(value) >= 0.0
        for value in (behavior_work, maintenance_work)
    ):
        raise PhysicalCostMapValidationError(
            "normalized behavior and maintenance work must be finite and non-negative"
        )
    heat_j = (
        float(record.behavior_energy_scale_j) * float(behavior_work)
        + float(record.maintenance_energy_scale_j) * float(maintenance_work)
    )
    entropy_j_per_k = heat_j / float(record.bath_temperature_k)
    return PhysicalCostMapResult(
        heat_j=heat_j,
        entropy_j_per_k=entropy_j_per_k,
        measurement_operator_id=record.measurement_operator_id,
        map_id=record.map_id,
    )


__all__ = [
    "PHYSICAL_COST_MAP_OPERATOR_MODE",
    "PHYSICAL_COST_MAP_STATUS",
    "PhysicalCostMapValidationError",
    "PhysicalCostMapRecord",
    "PhysicalCostMapResult",
    "map_normalized_work_to_si",
]
