"""Conditional scalar thermoelastic response bridge for Topic 13.

The bridge derives a static adiabatic temperature response from standard
linear thermoelasticity plus the proposed ``Phi_E * div(u)`` interaction. It
does not add that interaction to the accepted UET action and does not supply
physical material coefficients.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

import numpy as np


SCALAR_THERMOELASTIC_BRIDGE_STATUS = (
    "PASS_CONDITIONAL_SCALAR_THERMOELASTIC_RESPONSE_BRIDGE"
)


@dataclass(frozen=True)
class ThermoelasticResponseWitness:
    temperature: float
    alpha_v: float
    bulk_modulus: float
    c_v_vol: float
    c_p_vol: float
    coupling: float
    response_residue: float
    response_curvature: float
    delta_phi: float
    phi_energy_amplitude: float
    delta_temperature: float
    delta_temperature_closed_form: float
    volumetric_strain: float
    stress_residual: float
    entropy_residual: float
    cp_cv_identity_residual: float
    temperature_map_relative_residual: float
    chi_u_theta: float
    alpha_phi_temperature_natural: float
    stability_margin: float


def scalar_thermoelastic_response(
    *,
    temperature: float,
    alpha_v: float,
    bulk_modulus: float,
    c_v_vol: float,
    coupling: float,
    response_residue: float,
    response_curvature: float,
    delta_phi: float,
) -> ThermoelasticResponseWitness:
    """Solve the zero-stress, adiabatic scalar thermoelastic response."""

    values = {
        "temperature": float(temperature),
        "alpha_v": float(alpha_v),
        "bulk_modulus": float(bulk_modulus),
        "c_v_vol": float(c_v_vol),
        "coupling": float(coupling),
        "response_residue": float(response_residue),
        "response_curvature": float(response_curvature),
        "delta_phi": float(delta_phi),
    }
    if not all(isfinite(value) for value in values.values()):
        raise ValueError("thermoelastic inputs must be finite")
    for name in (
        "temperature",
        "bulk_modulus",
        "c_v_vol",
        "response_curvature",
    ):
        if values[name] <= 0.0:
            raise ValueError(f"{name} must be positive")

    temperature = values["temperature"]
    alpha_v = values["alpha_v"]
    bulk_modulus = values["bulk_modulus"]
    c_v_vol = values["c_v_vol"]
    coupling = values["coupling"]
    response_residue = values["response_residue"]
    response_curvature = values["response_curvature"]
    delta_phi = values["delta_phi"]
    phi_energy = response_residue * delta_phi
    c_p_vol = c_v_vol + temperature * alpha_v**2 * bulk_modulus

    matrix = np.asarray(
        [
            [bulk_modulus, -bulk_modulus * alpha_v],
            [bulk_modulus * alpha_v, c_v_vol / temperature],
        ],
        dtype=float,
    )
    source = np.asarray([-coupling * phi_energy, 0.0], dtype=float)
    volumetric_strain, delta_temperature = np.linalg.solve(matrix, source)
    closed_form = (
        temperature
        * alpha_v
        * coupling
        * phi_energy
        / c_p_vol
    )
    stress_residual = (
        bulk_modulus * volumetric_strain
        - bulk_modulus * alpha_v * delta_temperature
        + coupling * phi_energy
    )
    entropy_residual = (
        bulk_modulus * alpha_v * volumetric_strain
        + c_v_vol * delta_temperature / temperature
    )
    cp_cv_residual = c_p_vol - c_v_vol - temperature * alpha_v**2 * bulk_modulus
    scale = max(abs(delta_temperature), abs(closed_form), 1.0e-300)
    chi_u_theta = temperature * alpha_v * c_v_vol / c_p_vol
    alpha_natural = temperature * alpha_v * coupling * response_residue / c_p_vol
    stability_margin = response_curvature * bulk_modulus - coupling**2
    return ThermoelasticResponseWitness(
        temperature=temperature,
        alpha_v=alpha_v,
        bulk_modulus=bulk_modulus,
        c_v_vol=c_v_vol,
        c_p_vol=float(c_p_vol),
        coupling=coupling,
        response_residue=response_residue,
        response_curvature=response_curvature,
        delta_phi=delta_phi,
        phi_energy_amplitude=float(phi_energy),
        delta_temperature=float(delta_temperature),
        delta_temperature_closed_form=float(closed_form),
        volumetric_strain=float(volumetric_strain),
        stress_residual=float(stress_residual),
        entropy_residual=float(entropy_residual),
        cp_cv_identity_residual=float(cp_cv_residual),
        temperature_map_relative_residual=float(
            abs(delta_temperature - closed_form) / scale
        ),
        chi_u_theta=float(chi_u_theta),
        alpha_phi_temperature_natural=float(alpha_natural),
        stability_margin=float(stability_margin),
    )


def scalar_thermoelastic_bridge_contract() -> dict[str, object]:
    """Return F0--F4 metadata for the conditional static bridge."""

    return {
        "status": SCALAR_THERMOELASTIC_BRIDGE_STATUS,
        "equations": {
            "free_energy_increment": (
                "delta_f=K_T*theta^2/2-K_T*alpha_V*theta*DeltaT-"
                "C_v^V*DeltaT^2/(2*T)+g_Phi_theta*Phi_E*theta+"
                "a_Phi*Phi_E^2/2"
            ),
            "zero_stress": (
                "K_T*theta-K_T*alpha_V*DeltaT+g_Phi_theta*Phi_E=0"
            ),
            "adiabatic_entropy": (
                "K_T*alpha_V*theta+(C_v^V/T)*DeltaT=0"
            ),
            "cp_cv_identity": "C_p^V-C_v^V=T*alpha_V^2*K_T",
            "temperature_response": (
                "DeltaT=T*alpha_V*g_Phi_theta*Phi_E/"
                "(C_v^V+T*alpha_V^2*K_T)"
            ),
            "material_response_factor": (
                "chi_u_theta=T*alpha_V*C_v^V/"
                "(C_v^V+T*alpha_V^2*K_T)=T*alpha_V*C_v^V/C_p^V"
            ),
            "conditional_alpha": (
                "alpha_Phi_T^nat=T*alpha_V*g_Phi_theta*Z_Phi/C_p^V"
            ),
            "static_stability": "a_Phi*K_T-g_Phi_theta^2>0",
        },
        "ontology": {
            "Phi_E": "energy-dimension UET response amplitude; not temperature",
            "theta": "external material volumetric strain div(u)",
            "DeltaT": "small material temperature perturbation",
            "C_v_vol": "heat capacity per volume at fixed strain/volume",
            "C_p_vol": "stress-free heat capacity per volume in scalar model",
            "C": "unchanged collective coordinate; not C_v or C_p",
            "R_gen": "derived history trace; absent from state and response",
        },
        "natural_unit_exponents": {
            "temperature": 1,
            "alpha_v": -1,
            "bulk_modulus": 4,
            "c_v_vol": 3,
            "c_p_vol": 3,
            "theta": 0,
            "Phi_E": 1,
            "g_Phi_theta": 3,
            "a_Phi": 2,
            "free_energy_density": 4,
            "chi_u_theta": 0,
            "alpha_per_normalized_Phi": 1,
        },
        "f0_ontology": "CLOSED_FOR_CONDITIONAL_SCALAR_MATERIAL_LANE",
        "f1_standard_correspondence": (
            "linear isotropic scalar thermoelasticity at zero external stress and "
            "fixed entropy, plus a proposed Phi_E--volumetric-strain interaction"
        ),
        "f2_units": "CLOSED_NATURAL_UNITS_SI_COEFFICIENTS_OPEN",
        "f3_derivation": (
            "linear stationarity/entropy solve and positive static Phi_E--theta Hessian"
        ),
        "f4_observable": (
            "conditional local adiabatic DeltaPhi-to-DeltaT map; no TTG dynamics"
        ),
        "source_roles": {
            "temperature": "SOURCE_MATCHED_MATERIAL_STATE_REQUIRED",
            "alpha_V": "SOURCE_MATCHED_INPUT_REQUIRED",
            "K_T": "SOURCE_MATCHED_ISOTHERMAL_INPUT_REQUIRED",
            "C_v_vol": "SOURCE_MATCHED_INPUT_REQUIRED",
            "g_Phi_theta": "UET_DERIVATION_OR_MICROSCOPIC_MATCH_REQUIRED",
            "Z_Phi": "PHYSICAL_RESPONSE_RESIDUE_REQUIRED",
            "a_Phi": "UET_RESPONSE_CURVATURE_REQUIRED_FOR_STABILITY",
        },
        "excluded": {
            "accepted_UET_action_term": True,
            "anisotropic_graphite_tensor": True,
            "finite_frequency_transport": True,
            "KMS_or_noise": True,
            "numeric_physical_alpha": True,
            "TTG_holdout": True,
        },
        "claim_boundary": (
            "Conditional static scalar thermoelastic derivation only; not an accepted "
            "UET action extension, anisotropic graphite model, dynamic transport, "
            "physical alpha calibration, TTG prediction or Full Topic 13 closure."
        ),
    }


__all__ = [
    "SCALAR_THERMOELASTIC_BRIDGE_STATUS",
    "ThermoelasticResponseWitness",
    "scalar_thermoelastic_bridge_contract",
    "scalar_thermoelastic_response",
]
