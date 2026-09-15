"""Lane-specific coarse-graining operators for UET collective coordinates.

The module makes information loss, scale, frame, units, and observable targets
explicit. It never treats distinct C lanes as a universal physical identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from typing import Any, Mapping, Protocol, runtime_checkable

import numpy as np


COARSE_GRAINING_STATUS = "CANDIDATE_LANE_SPECIFIC_COARSE_GRAINING_V1"
SUPPORTED_C_LANES = ("phase", "charge", "density", "telegraph")


def _finite_positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def _field(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.ndim != 1 or result.size < 2:
        raise ValueError(f"{name} must be a one-dimensional field with >=2 samples")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite values")
    return result


@dataclass(frozen=True)
class CoarseGrainingRecord:
    """Provenance and ontology record for one collective-coordinate map."""

    lane_id: str
    microscopic_state_type: str
    kernel: str
    reference_frame: str
    spatial_scale: float
    temporal_scale: float
    boundary_rule: str
    unit_lane: str
    parameter_provenance: str
    information_lost: tuple[str, ...]
    observable_target: str
    output_cells: int
    reference_value: float = 0.0
    coordinate_scale: float = 1.0

    def __post_init__(self) -> None:
        if self.lane_id not in SUPPORTED_C_LANES:
            raise ValueError(f"unsupported C lane: {self.lane_id}")
        for name in (
            "microscopic_state_type",
            "kernel",
            "reference_frame",
            "boundary_rule",
            "unit_lane",
            "parameter_provenance",
            "observable_target",
        ):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} must be declared")
        _finite_positive(self.spatial_scale, "spatial_scale")
        _finite_positive(self.temporal_scale, "temporal_scale")
        _finite_positive(self.coordinate_scale, "coordinate_scale")
        if isinstance(self.output_cells, bool) or self.output_cells < 1:
            raise ValueError("output_cells must be a positive integer")
        if int(self.output_cells) != self.output_cells:
            raise ValueError("output_cells must be an integer")
        if not self.information_lost:
            raise ValueError("information_lost must declare at least one lost layer")
        if self.kernel != "uniform_block_average_v1":
            raise NotImplementedError(
                "coarse-graining v1 supports only uniform_block_average_v1"
            )


@dataclass(frozen=True)
class CollectiveCoordinateState:
    """One lane-specific coarse collective coordinate."""

    lane_id: str
    C: np.ndarray
    coarse_physical_field: np.ndarray
    record: CoarseGrainingRecord
    diagnostics: Mapping[str, Any]


@dataclass(frozen=True)
class CoarseGrainingConsistency:
    lane_id: str
    global_mean_drift: float
    refinement_l2: tuple[float, ...]
    information_loss_declared: bool
    universal_identity_claimed: bool
    status: str


@dataclass(frozen=True)
class ScaleDependenceResult:
    scales: tuple[float, ...]
    logarithmic_slopes: Mapping[str, tuple[float, ...]]
    status: str
    claim_boundary: str


@runtime_checkable
class CoarseGrainingOperator(Protocol):
    """Protocol for lane-specific maps from a declared lower-level field."""

    def __call__(
        self,
        microscopic_state: Any,
        record: CoarseGrainingRecord,
    ) -> CollectiveCoordinateState:
        ...


def _block_average(field: np.ndarray, output_cells: int) -> np.ndarray:
    cells = int(output_cells)
    if field.size % cells != 0:
        raise ValueError("field length must be divisible by output_cells")
    return np.asarray(field.reshape(cells, field.size // cells).mean(axis=1))


def _validate_lane_input(field: np.ndarray, record: CoarseGrainingRecord) -> None:
    if record.lane_id == "density" and np.min(field) < 0.0:
        raise ValueError("density lane requires a non-negative declared density field")
    required_types = {
        "phase": {"microscopic_order_field", "lower_level_order_statistics"},
        "charge": {"coarse_o2_noether_charge_density", "local_noether_charge_samples"},
        "density": {"si_mass_density_field", "declared_number_density_field"},
        "telegraph": {"order_response_field", "finite_cone_collective_field"},
    }
    if record.microscopic_state_type not in required_types[record.lane_id]:
        raise ValueError(
            f"microscopic_state_type is not accepted for {record.lane_id} lane"
        )
    if record.lane_id == "density" and record.unit_lane not in {
        "si_mass_density",
        "si_number_density",
    }:
        raise ValueError("density lane requires an explicit SI density unit lane")
    if record.lane_id in {"phase", "telegraph"} and record.unit_lane != "normalized":
        raise ValueError(f"{record.lane_id} lane v1 requires unit_lane='normalized'")
    if record.lane_id == "charge" and record.unit_lane != "natural_to_normalized":
        raise ValueError(
            "charge lane v1 requires unit_lane='natural_to_normalized'"
        )


def coarse_grain(
    microscopic_state: Any,
    record: CoarseGrainingRecord,
) -> CollectiveCoordinateState:
    """Map a declared lower-level field to a lane-specific coordinate."""

    field = _field(microscopic_state, "microscopic_state")
    _validate_lane_input(field, record)
    coarse = _block_average(field, record.output_cells)
    C = (coarse - record.reference_value) / record.coordinate_scale
    block_size = field.size // record.output_cells
    diagnostics = {
        "operator_status": COARSE_GRAINING_STATUS,
        "input_samples": int(field.size),
        "output_cells": int(record.output_cells),
        "block_size": int(block_size),
        "input_mean": float(np.mean(field)),
        "coarse_mean": float(np.mean(coarse)),
        "mean_preservation_error": abs(float(np.mean(field) - np.mean(coarse))),
        "map_invertible": False,
        "information_loss": list(record.information_lost),
        "universal_C_identity": False,
        "observable_target": record.observable_target,
    }
    return CollectiveCoordinateState(
        lane_id=record.lane_id,
        C=np.asarray(C, dtype=float),
        coarse_physical_field=np.asarray(coarse, dtype=float),
        record=record,
        diagnostics=diagnostics,
    )


def refine_coarse_graining(
    microscopic_state: Any,
    records: tuple[CoarseGrainingRecord, ...],
) -> tuple[CollectiveCoordinateState, ...]:
    """Evaluate one lane at an ordered set of output resolutions."""

    if not records:
        raise ValueError("at least one coarse-graining record is required")
    lane = records[0].lane_id
    if any(record.lane_id != lane for record in records):
        raise ValueError("refinement records must use one C lane")
    cell_counts = [record.output_cells for record in records]
    if cell_counts != sorted(cell_counts):
        raise ValueError("refinement records must be ordered by output_cells")
    return tuple(coarse_grain(microscopic_state, record) for record in records)


def _prolong(coarse: np.ndarray, target_size: int) -> np.ndarray:
    if target_size % coarse.size != 0:
        raise ValueError("refinement cell counts must be integer multiples")
    return np.repeat(coarse, target_size // coarse.size)


def coarse_graining_consistency(
    states: tuple[CollectiveCoordinateState, ...],
) -> CoarseGrainingConsistency:
    """Report mean preservation and successive refinement differences."""

    if not states:
        raise ValueError("at least one collective state is required")
    lane = states[0].lane_id
    if any(state.lane_id != lane for state in states):
        raise ValueError("all collective states must use one lane")
    reference_mean = float(np.mean(states[-1].coarse_physical_field))
    mean_drift = max(
        abs(float(np.mean(state.coarse_physical_field)) - reference_mean)
        for state in states
    )
    refinement_l2: list[float] = []
    for coarse_state, fine_state in zip(states, states[1:]):
        prolonged = _prolong(
            coarse_state.coarse_physical_field,
            fine_state.coarse_physical_field.size,
        )
        refinement_l2.append(
            float(
                np.linalg.norm(prolonged - fine_state.coarse_physical_field)
                / np.sqrt(fine_state.coarse_physical_field.size)
            )
        )
    declared = all(state.record.information_lost for state in states)
    return CoarseGrainingConsistency(
        lane_id=lane,
        global_mean_drift=float(mean_drift),
        refinement_l2=tuple(refinement_l2),
        information_loss_declared=bool(declared),
        universal_identity_claimed=False,
        status="PASS_INTERNAL_CONSISTENCY" if mean_drift <= 1e-12 else "FAIL",
    )


def scale_dependence_audit(
    parameter_sets: Mapping[float, Mapping[str, float]],
) -> ScaleDependenceResult:
    """Compute descriptive log-scale slopes; this is not an RG derivation."""

    if len(parameter_sets) < 2:
        raise ValueError("at least two scales are required")
    scales = tuple(sorted(_finite_positive(scale, "scale") for scale in parameter_sets))
    parameter_names = set(parameter_sets[scales[0]])
    if not parameter_names or any(set(parameter_sets[scale]) != parameter_names for scale in scales):
        raise ValueError("every scale must provide the same non-empty parameter set")
    log_scales = np.log(np.asarray(scales, dtype=float))
    slopes: dict[str, tuple[float, ...]] = {}
    for name in sorted(parameter_names):
        values = np.asarray([parameter_sets[scale][name] for scale in scales], dtype=float)
        if not np.all(np.isfinite(values)):
            raise ValueError("scale-dependent parameters must be finite")
        slopes[name] = tuple(
            float(value)
            for value in np.diff(values) / np.diff(log_scales)
        )
    return ScaleDependenceResult(
        scales=scales,
        logarithmic_slopes=slopes,
        status="DESCRIPTIVE_SCALE_AUDIT_ONLY",
        claim_boundary="finite-difference scale dependence; not a beta function or RG derivation",
    )


def coarse_graining_contract() -> dict[str, Any]:
    return {
        "status": COARSE_GRAINING_STATUS,
        "lanes": list(SUPPORTED_C_LANES),
        "kernel": "uniform_block_average_v1",
        "many_to_one": True,
        "microscopic_inversion": False,
        "universal_C_identity": False,
        "scale_audit": "descriptive_not_RG_derivation",
        "physical_closure": {
            "charge": "coarse Noether density accepted; microscopic amplitude map open",
            "phase": "normalized order statistics only",
            "density": "requires already-declared SI density field; catalog/material map open",
            "telegraph": "normalized finite-cone coordinate only",
        },
    }


__all__ = [
    "COARSE_GRAINING_STATUS",
    "SUPPORTED_C_LANES",
    "CoarseGrainingRecord",
    "CollectiveCoordinateState",
    "CoarseGrainingConsistency",
    "ScaleDependenceResult",
    "CoarseGrainingOperator",
    "coarse_grain",
    "refine_coarse_graining",
    "coarse_graining_consistency",
    "scale_dependence_audit",
    "coarse_graining_contract",
]
