"""Conditional anisotropic thermoelastic response bridge for Topic 13."""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

import numpy as np


ANISOTROPIC_THERMOELASTIC_BRIDGE_STATUS = (
    "PASS_CONDITIONAL_ANISOTROPIC_THERMOELASTIC_RESPONSE_BRIDGE"
)


@dataclass(frozen=True)
class AnisotropicThermoelasticWitness:
    temperature: float
    c_strain_vol: float
    c_stress_vol: float
    response_residue: float
    response_curvature: float
    delta_phi: float
    phi_energy_amplitude: float
    strain: tuple[float, float, float]
    delta_temperature: float
    delta_temperature_closed_form: float
    thermal_stress: tuple[float, float, float]
    thermoelastic_contraction: float
    coupling_contraction: float
    stress_residual_norm: float
    entropy_residual: float
    heat_capacity_identity_residual: float
    temperature_map_relative_residual: float
    stability_margin: float


def _vector(values: Any, name: str) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    if result.shape != (3,) or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite length-three vector")
    return result


def _stiffness(values: Any) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    if result.shape != (3, 3) or not np.all(np.isfinite(result)):
        raise ValueError("stiffness must be a finite 3x3 normal-strain block")
    if not np.allclose(result, result.T, rtol=0.0, atol=1.0e-13):
        raise ValueError("stiffness must be symmetric")
    if float(np.min(np.linalg.eigvalsh(result))) <= 0.0:
        raise ValueError("stiffness must be positive definite")
    return result


def hexagonal_normal_stiffness(
    *, c11: float, c12: float, c13: float, c33: float
) -> np.ndarray:
    """Return the normal-strain block for a hexagonal material."""

    values = tuple(float(value) for value in (c11, c12, c13, c33))
    if not all(isfinite(value) for value in values):
        raise ValueError("hexagonal stiffness inputs must be finite")
    return _stiffness(
        [
            [values[0], values[1], values[2]],
            [values[1], values[0], values[2]],
            [values[2], values[2], values[3]],
        ]
    )


def anisotropic_thermoelastic_response(
    *,
    temperature: float,
    alpha_tensor: Any,
    stiffness: Any,
    c_strain_vol: float,
    coupling_tensor: Any,
    response_residue: float,
    response_curvature: float,
    delta_phi: float,
) -> AnisotropicThermoelasticWitness:
    """Solve zero normal stress and fixed entropy in the 3D normal block."""

    scalar_values = {
        "temperature": float(temperature),
        "c_strain_vol": float(c_strain_vol),
        "response_residue": float(response_residue),
        "response_curvature": float(response_curvature),
        "delta_phi": float(delta_phi),
    }
    if not all(isfinite(value) for value in scalar_values.values()):
        raise ValueError("anisotropic thermoelastic scalar inputs must be finite")
    for name in ("temperature", "c_strain_vol", "response_curvature"):
        if scalar_values[name] <= 0.0:
            raise ValueError(f"{name} must be positive")

    alpha = _vector(alpha_tensor, "alpha_tensor")
    coupling = _vector(coupling_tensor, "coupling_tensor")
    stiffness_matrix = _stiffness(stiffness)
    compliance = np.linalg.inv(stiffness_matrix)
    thermal_stress = stiffness_matrix @ alpha
    thermoelastic = float(alpha @ stiffness_matrix @ alpha)
    coupling_contraction = float(alpha @ coupling)
    c_stress_vol = scalar_values["c_strain_vol"] + temperature * thermoelastic
    phi_energy = scalar_values["response_residue"] * scalar_values["delta_phi"]

    matrix = np.zeros((4, 4), dtype=float)
    matrix[:3, :3] = stiffness_matrix
    matrix[:3, 3] = -thermal_stress
    matrix[3, :3] = thermal_stress
    matrix[3, 3] = scalar_values["c_strain_vol"] / temperature
    source = np.concatenate((-coupling * phi_energy, np.asarray([0.0])))
    solution = np.linalg.solve(matrix, source)
    strain = solution[:3]
    delta_temperature = float(solution[3])
    closed_form = float(
        temperature * coupling_contraction * phi_energy / c_stress_vol
    )
    stress_residual = (
        stiffness_matrix @ strain
        - thermal_stress * delta_temperature
        + coupling * phi_energy
    )
    entropy_residual = float(
        thermal_stress @ strain
        + scalar_values["c_strain_vol"] * delta_temperature / temperature
    )
    heat_capacity_residual = float(
        c_stress_vol
        - scalar_values["c_strain_vol"]
        - temperature * thermoelastic
    )
    response_scale = max(abs(delta_temperature), abs(closed_form), 1.0e-300)
    stability_margin = float(
        scalar_values["response_curvature"] - coupling @ compliance @ coupling
    )
    return AnisotropicThermoelasticWitness(
        temperature=temperature,
        c_strain_vol=scalar_values["c_strain_vol"],
        c_stress_vol=float(c_stress_vol),
        response_residue=scalar_values["response_residue"],
        response_curvature=scalar_values["response_curvature"],
        delta_phi=scalar_values["delta_phi"],
        phi_energy_amplitude=float(phi_energy),
        strain=tuple(float(value) for value in strain),
        delta_temperature=delta_temperature,
        delta_temperature_closed_form=closed_form,
        thermal_stress=tuple(float(value) for value in thermal_stress),
        thermoelastic_contraction=thermoelastic,
        coupling_contraction=coupling_contraction,
        stress_residual_norm=float(np.linalg.norm(stress_residual)),
        entropy_residual=entropy_residual,
        heat_capacity_identity_residual=heat_capacity_residual,
        temperature_map_relative_residual=float(
            abs(delta_temperature - closed_form) / response_scale
        ),
        stability_margin=stability_margin,
    )


def anisotropic_thermoelastic_bridge_contract() -> dict[str, object]:
    """Return F0--F4 metadata for the anisotropic conditional bridge."""

    return {
        "status": ANISOTROPIC_THERMOELASTIC_BRIDGE_STATUS,
        "equations": {
            "free_energy_increment": (
                "delta_f=epsilon:C:epsilon/2-DeltaT*(C:alpha):epsilon-"
                "C_epsilon*DeltaT^2/(2*T)+Phi_E*G:epsilon+a_Phi*Phi_E^2/2"
            ),
            "zero_stress": "C:epsilon-(C:alpha)*DeltaT+G*Phi_E=0",
            "adiabatic_entropy": "(C:alpha):epsilon+(C_epsilon/T)*DeltaT=0",
            "heat_capacity_identity": (
                "C_sigma=C_epsilon+T*alpha:C:alpha"
            ),
            "temperature_response": (
                "DeltaT=T*(alpha:G)*Phi_E/(C_epsilon+T*alpha:C:alpha)"
            ),
            "hexagonal_numerator": "alpha:G=2*alpha_a*g_a+alpha_c*g_c",
            "hexagonal_denominator": (
                "alpha:C:alpha=2*(C11+C12)*alpha_a^2+"
                "4*C13*alpha_a*alpha_c+C33*alpha_c^2"
            ),
            "static_stability": "a_Phi-G:S:G>0; S=C^-1",
        },
        "ontology": {
            "epsilon": "external material normal-strain tensor block",
            "alpha": "material thermal-expansion tensor",
            "C_tensor": "material stiffness tensor, not UET C",
            "G": "candidate Phi_E--strain coupling tensor",
            "Phi_E": "energy-dimension UET response amplitude; not temperature",
            "R_gen": "derived history trace; excluded from state",
        },
        "natural_unit_exponents": {
            "temperature": 1,
            "alpha_tensor": -1,
            "stiffness": 4,
            "compliance": -4,
            "c_strain_vol": 3,
            "c_stress_vol": 3,
            "strain": 0,
            "Phi_E": 1,
            "coupling_tensor": 3,
            "response_curvature": 2,
            "free_energy_density": 4,
            "alpha_per_normalized_Phi": 1,
        },
        "f0_ontology": "CLOSED_FOR_CONDITIONAL_ANISOTROPIC_MATERIAL_LANE",
        "f1_standard_correspondence": (
            "linear anisotropic thermoelasticity in the normal-strain block"
        ),
        "f2_units": "CLOSED_NATURAL_UNITS_SOURCE_SI_MAP_OPEN",
        "f3_derivation": (
            "block linear solve, compliance elimination and Schur-complement stability"
        ),
        "f4_observable": (
            "conditional local adiabatic tensor DeltaPhi-to-DeltaT map"
        ),
        "excluded": {
            "accepted_UET_action_term": True,
            "physical_graphite_tensor_input": True,
            "finite_frequency_transport": True,
            "SK_KMS_noise": True,
            "numeric_physical_alpha": True,
            "TTG_holdout": True,
        },
        "claim_boundary": (
            "Conditional static anisotropic derivation only; not an accepted UET "
            "action, source-matched graphite tensor, dynamic transport, physical "
            "alpha calibration, TTG prediction or Full Topic 13 closure."
        ),
    }


__all__ = [
    "ANISOTROPIC_THERMOELASTIC_BRIDGE_STATUS",
    "AnisotropicThermoelasticWitness",
    "anisotropic_thermoelastic_bridge_contract",
    "anisotropic_thermoelastic_response",
    "hexagonal_normal_stiffness",
]
