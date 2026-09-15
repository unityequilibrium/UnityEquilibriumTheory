"""Canonical Topic 13 thermal-bridge support package."""

from .t13_formal_thermodynamic_bridge_integration import (
    FORMAL_T13_BRIDGE_STATUS,
    formal_thermodynamic_bridge_witness,
)
from .t13_thermal_bridge_scale_dependency import (
    FieldRescalingWitness,
    JointScaleWitness,
    build_scale_dependency_witness,
    scale_dependency_contract,
)
from .topic13_closure_record_contract import (
    topic13_closure_record_schema,
    validate_base_phi_alpha_record,
    validate_ding_csrc_payload,
    validate_physical_transport_record,
)

__all__ = [
    "FORMAL_T13_BRIDGE_STATUS",
    "FieldRescalingWitness",
    "JointScaleWitness",
    "build_scale_dependency_witness",
    "formal_thermodynamic_bridge_witness",
    "scale_dependency_contract",
    "topic13_closure_record_schema",
    "validate_base_phi_alpha_record",
    "validate_ding_csrc_payload",
    "validate_physical_transport_record",
]
