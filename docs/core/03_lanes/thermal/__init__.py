"""Canonical thermal lane for source-backed He-4 support records."""

from .he4_normal_viscosity_kubo import physical_transport_record, source_hash
from .he4_o2_response_calibration import calibration_record
from .he4_o2_si_beta_mapping import si_beta_record
from .he4_svp_reference import (
    SOURCE_DOI,
    SOURCE_SNAPSHOT_BYTES,
    SOURCE_SNAPSHOT_SHA256,
    SOURCE_URL,
    T_LAMBDA_K,
    calibration_grid,
    reference_row,
    superfluid_density_kg_m3,
    total_density_kg_m3,
)

__all__ = [
    "SOURCE_DOI",
    "SOURCE_SNAPSHOT_BYTES",
    "SOURCE_SNAPSHOT_SHA256",
    "SOURCE_URL",
    "T_LAMBDA_K",
    "calibration_grid",
    "calibration_record",
    "physical_transport_record",
    "reference_row",
    "si_beta_record",
    "source_hash",
    "superfluid_density_kg_m3",
    "total_density_kg_m3",
]
