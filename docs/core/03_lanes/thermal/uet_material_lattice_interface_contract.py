"""Conditional UET-to-material-lattice interface contract for Topic 13.

This module closes ontology, unit and exchange-ledger bookkeeping only. It does
not add a physical coupling to the UET action or identify Phi with temperature,
strain, displacement or a phonon field.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


MATERIAL_LATTICE_INTERFACE_STATUS = (
    "PASS_CONDITIONAL_MATERIAL_LATTICE_INTERFACE_CONTRACT"
)


@dataclass(frozen=True)
class InterfaceRescalingWitness:
    phi_energy_amplitude: float
    volumetric_strain: float
    coupling: float
    scale: float
    interaction_energy_density: float
    rescaled_phi_energy_amplitude: float
    rescaled_coupling: float
    rescaled_interaction_energy_density: float
    interaction_relative_residual: float
    alpha_product: float
    rescaled_alpha_product: float
    alpha_product_relative_residual: float


def interface_rescaling_witness(
    phi_energy_amplitude: float = 0.3,
    volumetric_strain: float = 0.02,
    coupling: float = 0.5,
    scale: float = 2.0,
) -> InterfaceRescalingWitness:
    """Verify the field-residue/coupling rescaling degeneracy."""

    values = (phi_energy_amplitude, volumetric_strain, coupling, scale)
    if not all(np.isfinite(value) for value in values):
        raise ValueError("interface witness inputs must be finite")
    if scale <= 0.0:
        raise ValueError("scale must be positive")
    if coupling == 0.0:
        raise ValueError("coupling must be nonzero for the identifiability witness")
    original = coupling * phi_energy_amplitude * volumetric_strain
    phi_rescaled = scale * phi_energy_amplitude
    coupling_rescaled = coupling / scale
    transformed = coupling_rescaled * phi_rescaled * volumetric_strain
    denominator = max(abs(original), abs(transformed), 1.0e-300)
    alpha_product = coupling * phi_energy_amplitude
    alpha_product_rescaled = coupling_rescaled * phi_rescaled
    return InterfaceRescalingWitness(
        phi_energy_amplitude=float(phi_energy_amplitude),
        volumetric_strain=float(volumetric_strain),
        coupling=float(coupling),
        scale=float(scale),
        interaction_energy_density=float(original),
        rescaled_phi_energy_amplitude=float(phi_rescaled),
        rescaled_coupling=float(coupling_rescaled),
        rescaled_interaction_energy_density=float(transformed),
        interaction_relative_residual=float(abs(original - transformed) / denominator),
        alpha_product=float(alpha_product),
        rescaled_alpha_product=float(alpha_product_rescaled),
        alpha_product_relative_residual=float(
            abs(alpha_product - alpha_product_rescaled)
            / max(abs(alpha_product), abs(alpha_product_rescaled), 1.0e-300)
        ),
    )


def exchange_ledger_witness(exchange_rate_density: float = 0.7) -> dict[str, float]:
    """Return equal-and-opposite subsystem exchange sources."""

    value = float(exchange_rate_density)
    if not np.isfinite(value):
        raise ValueError("exchange_rate_density must be finite")
    uet_source = -value
    lattice_source = value
    return {
        "uet_energy_source": uet_source,
        "lattice_energy_source": lattice_source,
        "total_energy_source": uet_source + lattice_source,
    }


def material_lattice_interface_contract() -> dict[str, object]:
    """Return the machine-readable conditional interface contract."""

    return {
        "status": MATERIAL_LATTICE_INTERFACE_STATUS,
        "state_ownership": {
            "UET": ["C", "Phi", "Pi"],
            "material_lattice": ["u_i", "strain_ij", "delta_n_qnu"],
            "excluded_from_state": ["R_gen", "R_obs"],
        },
        "ontology": {
            "u_i": "external material displacement field",
            "strain_ij": "symmetric gradient of u_i",
            "delta_n_qnu": "phonon distribution perturbation",
            "Phi": "UET effective response variable; not temperature, displacement or strain",
            "C": "unchanged collective coordinate; not lattice mass or heat capacity",
            "R_gen": "derived history trace with no interface backreaction",
        },
        "equations": {
            "strain": "strain_ij=(partial_i u_j+partial_j u_i)/2",
            "volumetric_strain": "theta=strain_i^i=div(u)",
            "canonical_response_map": "Phi_E=Z_Phi*DeltaPhi",
            "conditional_interaction": "L_int=-g_Phi_theta*Phi_E*theta",
            "phonon_heat_current": "J_Q^i=sum_qnu hbar*omega_qnu*v_qnu^i*delta_n_qnu/V",
            "pbte": "partial_t delta_n+v.grad(delta_n)=-C_ph[delta_n]+S_Phi",
            "collision_split": "C_ph=C_N+C_R; C_N preserves crystal momentum; C_R relaxes it",
            "exchange_ledger": "partial_mu T_UET^(mu0)=-Q_ex; partial_mu T_lat^(mu0)=+Q_ex",
            "conditional_temperature_map": "DeltaT=(chi_u_theta*g_Phi_theta*Z_Phi/C_src)*DeltaPhi",
            "conditional_alpha": "alpha_Phi_K=chi_u_theta*g_Phi_theta*Z_Phi/C_src with SI conversion and uncertainty",
        },
        "natural_unit_exponents": {
            "coordinate_x": -1,
            "derivative": 1,
            "displacement_u": -1,
            "strain_theta": 0,
            "Phi_E": 1,
            "g_Phi_theta": 3,
            "interaction_energy_density": 4,
            "phonon_energy_density": 4,
            "heat_current": 4,
            "exchange_rate_density": 5,
            "C_src_natural": 3,
            "alpha_per_normalized_Phi_natural": 1,
        },
        "input_roles": {
            "Z_Phi": "DERIVED_OR_INDEPENDENT_CALIBRATION_REQUIRED",
            "g_Phi_theta": "DERIVED_FROM_ACTION_OR_EXTERNAL_MATCH_REQUIRED",
            "chi_u_theta": "SOURCE_BACKED_MATERIAL_RESPONSE_REQUIRED",
            "C_src": "SOURCE_BACKED_MATERIAL_INPUT_REQUIRED",
            "C_N_C_R": "SOURCE_BACKED_OR_MICROSCOPIC_MATCH_REQUIRED",
        },
        "admitted_current_evidence": {
            "calorine_mode_source_fields": True,
            "normal_umklapp_collision_split": False,
            "physical_Z_Phi": False,
            "physical_g_Phi_theta": False,
            "physical_alpha_Phi_K": False,
        },
        "claim_boundary": (
            "Conditional interface architecture only; no physical coupling, "
            "alpha calibration, material transport coefficient or UET validation."
        ),
    }


__all__ = [
    "MATERIAL_LATTICE_INTERFACE_STATUS",
    "InterfaceRescalingWitness",
    "exchange_ledger_witness",
    "interface_rescaling_witness",
    "material_lattice_interface_contract",
]
