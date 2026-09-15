"""Resolve the open factors in the conditional Topic 13 material bridge.

This module distinguishes the implemented response--matter operator from the
still-hypothetical response--strain operator. It does not add a new action term
or emit a physical ``alpha_Phi_K``.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Mapping

from docs.core.uet_covariant_matter import NATURAL_UNIT_MATTER_DIMENSIONS
from docs.core.uet_covariant_response import NATURAL_UNIT_MASS_DIMENSIONS
from docs.core.uet_material_lattice_interface_contract import (
    material_lattice_interface_contract,
)


MATERIAL_INTERFACE_FACTOR_STATUS = (
    "PASS_FACTOR_RESOLUTION_WITH_COUPLING_SUBSTITUTION_NO_GO"
)


@dataclass(frozen=True)
class ConditionalAlphaWitness:
    """Synthetic arithmetic witness for the declared product and uncertainty."""

    alpha_natural: float
    relative_standard_uncertainty: float
    standard_uncertainty_natural: float


def conditional_alpha_witness(
    *,
    chi_u_theta: float,
    g_phi_theta: float,
    z_phi: float,
    c_src: float,
    standard_uncertainties: Mapping[str, float],
) -> ConditionalAlphaWitness:
    """Evaluate the conditional factor product with independent uncertainties."""

    factors = {
        "chi_u_theta": float(chi_u_theta),
        "g_phi_theta": float(g_phi_theta),
        "z_phi": float(z_phi),
        "c_src": float(c_src),
    }
    if not all(isfinite(value) and value != 0.0 for value in factors.values()):
        raise ValueError("all conditional-alpha factors must be finite and nonzero")
    if set(standard_uncertainties) != set(factors):
        raise ValueError("standard uncertainties must be supplied for every factor")
    uncertainties = {
        name: float(standard_uncertainties[name]) for name in factors
    }
    if not all(isfinite(value) and value >= 0.0 for value in uncertainties.values()):
        raise ValueError("standard uncertainties must be finite and non-negative")

    alpha = (
        factors["chi_u_theta"]
        * factors["g_phi_theta"]
        * factors["z_phi"]
        / factors["c_src"]
    )
    relative_variance = sum(
        (uncertainties[name] / factors[name]) ** 2 for name in factors
    )
    relative_uncertainty = sqrt(relative_variance)
    return ConditionalAlphaWitness(
        alpha_natural=float(alpha),
        relative_standard_uncertainty=float(relative_uncertainty),
        standard_uncertainty_natural=float(abs(alpha) * relative_uncertainty),
    )


def material_interface_factor_resolution() -> dict[str, object]:
    """Return the factor matrix and current-action substitution no-go."""

    interface_units = material_lattice_interface_contract()[
        "natural_unit_exponents"
    ]
    matter_units = NATURAL_UNIT_MATTER_DIMENSIONS
    response_units = NATURAL_UNIT_MASS_DIMENSIONS
    return {
        "status": MATERIAL_INTERFACE_FACTOR_STATUS,
        "equations": {
            "required_material_bridge": (
                "alpha_Phi_K=chi_u_theta*g_Phi_theta*Z_Phi/C_src"
            ),
            "implemented_matter_operator": (
                "V_int=-epsilon_nc*h*delta_phi*(chi_1^2+chi_2^2)/2"
            ),
            "required_strain_operator": "L_int=-g_Phi_theta*Phi_E*theta",
            "response_map": "Phi_E=Z_Phi*DeltaPhi",
            "action_natural_bridge": (
                "alpha_Phi_T^nat=(partial_Phi epsilon)/(partial_T epsilon)"
            ),
            "independent_uncertainty": (
                "(sigma_alpha/|alpha|)^2=(sigma_chi/chi)^2+"
                "(sigma_g/g)^2+(sigma_Z/Z)^2+(sigma_C/C_src)^2"
            ),
            "correlated_uncertainty": "Var(alpha)=grad(alpha)^T Sigma grad(alpha)",
        },
        "operator_substitution_no_go": {
            "implemented_operator_fields": ["delta_phi", "chi_1", "chi_2"],
            "required_operator_fields": ["Phi_E", "theta", "u_i"],
            "implemented_coefficient": "response_coupling_h",
            "implemented_coefficient_mass_dimension": matter_units[
                "response_coupling"
            ],
            "required_coefficient": "g_Phi_theta",
            "required_coefficient_mass_dimension": interface_units["g_Phi_theta"],
            "missing_mass_dimension": (
                interface_units["g_Phi_theta"]
                - matter_units["response_coupling"]
            ),
            "implemented_operator_mass_dimension_without_coefficient": (
                response_units["phi"] + 2 * matter_units["matter_doublet"]
            ),
            "required_operator_mass_dimension_without_coefficient": (
                interface_units["Phi_E"] + interface_units["strain_theta"]
            ),
            "conclusion": (
                "response_coupling_h cannot be relabeled as g_Phi_theta; the "
                "operators have different state support and the coefficients "
                "differ by natural mass dimension two"
            ),
        },
        "factor_matrix": {
            "Z_Phi": {
                "required_role": "normalized Phi to energy-dimension response residue",
                "required_mass_dimension": interface_units["Phi_E"],
                "current_evidence": (
                    "the action declares phi mass dimension one and a dimensionless "
                    "kinetic coefficient, but field rescaling leaves the physical "
                    "amplitude unidentified"
                ),
                "resolution_status": "OPEN_PHYSICAL_RESIDUE_NONIDENTIFIABLE",
                "admissible_route": (
                    "source-locked pole residue or independent observable-amplitude/SI map"
                ),
            },
            "response_coupling_h": {
                "required_role": "implemented Phi--O(2)-amplitude interaction",
                "required_mass_dimension": matter_units["response_coupling"],
                "current_evidence": "present in the current natural-unit action",
                "resolution_status": "ACTION_SLOT_PRESENT_NOT_STRAIN_COUPLING",
                "admissible_route": "retain only in its declared O(2)-matter operator",
            },
            "g_Phi_theta": {
                "required_role": "Phi_E--volumetric-strain coupling",
                "required_mass_dimension": interface_units["g_Phi_theta"],
                "current_evidence": "no displacement or strain operator in current action",
                "resolution_status": "ABSENT_FROM_CURRENT_ACTION",
                "admissible_route": (
                    "new F0--F4 action extension or independent microscopic matching"
                ),
            },
            "chi_u_theta": {
                "required_role": "dimensionless material response kernel in declared lane",
                "required_mass_dimension": 0,
                "current_evidence": "no source-backed strain-to-energy response kernel",
                "resolution_status": "OPEN_SOURCE_OR_MICROSCOPIC_MATCH",
                "admissible_route": (
                    "same-material/state deformation-potential, Gruneisen or response kernel"
                ),
            },
            "C_src": {
                "required_role": "volumetric heat-capacity denominator",
                "required_mass_dimension": interface_units["C_src_natural"],
                "current_evidence": (
                    "hash-locked Calorine mode heat capacities exist as a comparator; "
                    "Ding-equivalent accepted calibration input remains open"
                ),
                "resolution_status": "COMPARATOR_AVAILABLE_ACCEPTED_INPUT_OPEN",
                "admissible_route": (
                    "authorized Ding payload or accepted same-regime PBTE reproduction"
                ),
            },
            "C_N_C_R": {
                "required_role": "normal/resistive collision decomposition",
                "required_mass_dimension": 1,
                "current_evidence": (
                    "total RTA gamma is available but cannot be relabeled as resistive-only"
                ),
                "resolution_status": "OPEN_COLLISION_DECOMPOSITION",
                "admissible_route": (
                    "process-resolved rates or stable full collision operator/eigenvectors"
                ),
            },
            "alpha_Phi_T_natural": {
                "required_role": "local homogeneous action response",
                "required_mass_dimension": 1,
                "current_evidence": "derived on one natural-unit O(2) quasiparticle branch",
                "resolution_status": "DERIVED_DIFFERENT_LANE_NOT_SI_ALPHA",
                "admissible_route": (
                    "retain as internal action bridge; do not substitute for material alpha"
                ),
            },
            "alpha_Phi_K": {
                "required_role": "kelvin per normalized base Phi",
                "required_mass_dimension": 1,
                "current_evidence": "no admissible complete factor product",
                "resolution_status": "OPEN_COMPOSITE_COEFFICIENT",
                "admissible_route": (
                    "resolve Z_Phi, g_Phi_theta, chi_u_theta and accepted C_src independently"
                ),
            },
        },
        "ontology": {
            "Phi": "effective response variable; not temperature or strain",
            "chi_A": "O(2) matter scalar components; not material displacement",
            "u_i": "external material displacement",
            "theta": "volumetric strain div(u)",
            "C": "collective coordinate; not heat capacity or lattice mass",
            "R_gen": "derived history trace; excluded from state and backreaction",
        },
        "claim_boundary": (
            "Factor-resolution and current-operator substitution no-go only; no new "
            "action term, physical residue/coupling, numeric alpha, TTG prediction or "
            "Full Topic 13 closure."
        ),
    }


__all__ = [
    "MATERIAL_INTERFACE_FACTOR_STATUS",
    "ConditionalAlphaWitness",
    "conditional_alpha_witness",
    "material_interface_factor_resolution",
]
