"""Canonical ontology-contract surface for UET core."""

from .uet_coarse_graining import (
    COARSE_GRAINING_STATUS,
    SUPPORTED_C_LANES,
    CollectiveCoordinateState,
    CoarseGrainingConsistency,
    CoarseGrainingOperator,
    CoarseGrainingRecord,
    ScaleDependenceResult,
    coarse_grain,
    coarse_graining_consistency,
    coarse_graining_contract,
    refine_coarse_graining,
    scale_dependence_audit,
)

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
