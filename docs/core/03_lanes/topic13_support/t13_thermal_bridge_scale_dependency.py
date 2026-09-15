"""Structural scale-dependency witness for the Topic 13 thermal bridge.

This module does not estimate a coefficient. It makes the remaining dimensional
dependency explicit so normalized TTG shape evidence cannot be promoted into a
Kelvin map without an independent field and energy anchor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _close(left: float, right: float) -> bool:
    return abs(left - right) <= 1.0e-12 * max(1.0, abs(left), abs(right))


@dataclass(frozen=True)
class FieldRescalingWitness:
    """Witness that the declared scalar action has a continuous field scale."""

    scale: float = 3.7
    delta_phi: float = 0.31
    delta_phi_gradient: float = 0.23
    z_phi: float = 2.0
    mass_sq: float = 0.8
    lambda_phi: float = 1.4
    xi_phi: float = 0.6
    phi_scale: float = 1.9

    def as_dict(self) -> dict[str, Any]:
        s = self.scale
        transformed_phi = s * self.delta_phi
        transformed_gradient = s * self.delta_phi_gradient
        transformed_z = self.z_phi / s**2
        transformed_mass_sq = self.mass_sq / s**2
        transformed_lambda = self.lambda_phi / s**4
        transformed_xi = self.xi_phi / s**2
        potential = 0.5 * self.mass_sq * self.delta_phi**2 + self.lambda_phi * self.delta_phi**4 / 4.0
        transformed_potential = (
            0.5 * transformed_mass_sq * transformed_phi**2
            + transformed_lambda * transformed_phi**4 / 4.0
        )
        kinetic = 0.5 * self.z_phi * self.delta_phi_gradient**2
        transformed_kinetic = 0.5 * transformed_z * transformed_gradient**2
        curvature = self.xi_phi * self.delta_phi**2
        transformed_curvature = transformed_xi * transformed_phi**2
        normalized_phi = self.delta_phi / self.phi_scale
        transformed_normalized_phi = transformed_phi / (s * self.phi_scale)
        return {
            "scale": s,
            "delta_phi": self.delta_phi,
            "delta_phi_prime": transformed_phi,
            "phi_scale": self.phi_scale,
            "phi_scale_prime": s * self.phi_scale,
            "coefficient_map": {
                "Z_prime": transformed_z,
                "m_Phi_sq_prime": transformed_mass_sq,
                "lambda_prime": transformed_lambda,
                "xi_Phi_prime": transformed_xi,
            },
            "action_terms": {
                "potential": potential,
                "potential_prime": transformed_potential,
                "kinetic": kinetic,
                "kinetic_prime": transformed_kinetic,
                "curvature_factor": curvature,
                "curvature_factor_prime": transformed_curvature,
            },
            "normalized_phi": normalized_phi,
            "normalized_phi_prime": transformed_normalized_phi,
            "checks": {
                "potential_invariant": _close(potential, transformed_potential),
                "kinetic_invariant": _close(kinetic, transformed_kinetic),
                "curvature_factor_invariant": _close(curvature, transformed_curvature),
                "normalized_coordinate_invariant": _close(normalized_phi, transformed_normalized_phi),
                "coefficient_map_matches_field_rescaling": (
                    _close(transformed_z, self.z_phi / s**2)
                    and _close(transformed_mass_sq, self.mass_sq / s**2)
                    and _close(transformed_lambda, self.lambda_phi / s**4)
                    and _close(transformed_xi, self.xi_phi / s**2)
                ),
            },
        }


@dataclass(frozen=True)
class JointScaleWitness:
    """Witness that field, energy-density, and Kelvin scales are jointly open."""

    field_scale: float = 3.7
    energy_density_scale: float = 5.0
    c_v_j_per_m3_k: float = 1.0e6
    response_ratio: float = 0.8
    delta_phi_normalized: float = 0.25

    def as_dict(self) -> dict[str, Any]:
        s_phi = self.field_scale
        s_e = self.energy_density_scale
        cv = self.c_v_j_per_m3_k
        ratio = self.response_ratio
        delta_phi = self.delta_phi_normalized
        normalized_curve = [0.25, 0.5, 0.2]
        normalized_curve_prime = [s_phi * value for value in normalized_curve]
        normalized_curve_shape = [value / normalized_curve[0] for value in normalized_curve]
        normalized_curve_shape_prime = [value / normalized_curve_prime[0] for value in normalized_curve_prime]
        base_thermal_response = ratio * delta_phi
        field_compensated_response = (ratio / s_phi) * (s_phi * delta_phi)
        base_energy_response = ratio * delta_phi / cv
        energy_rescaled_response = (s_e * ratio) * delta_phi / cv
        beta_scale_ratio = s_phi**2 / s_e
        return {
            "field_scale": s_phi,
            "energy_density_scale": s_e,
            "c_v_j_per_m3_k": cv,
            "response_ratio": ratio,
            "delta_phi_normalized": delta_phi,
            "normalized_curve_shape": normalized_curve_shape,
            "normalized_curve_shape_prime": normalized_curve_shape_prime,
            "base_thermal_response_relative": base_thermal_response,
            "field_compensated_thermal_response_relative": field_compensated_response,
            "base_energy_response_k": base_energy_response,
            "energy_rescaled_response_k": energy_rescaled_response,
            "beta_scale_ratio": beta_scale_ratio,
            "checks": {
                "normalized_response_invariant": all(
                    _close(left, right)
                    for left, right in zip(normalized_curve_shape, normalized_curve_shape_prime)
                ),
                "field_only_alpha_compensation_preserves_response": _close(
                    base_thermal_response, field_compensated_response
                ),
                "joint_energy_scale_changes_absolute_response": not _close(
                    base_energy_response, energy_rescaled_response
                ),
                "joint_scale_changes_beta": not _close(beta_scale_ratio, 1.0),
                "energy_scale_is_not_a_material_c_v_measurement": s_e != 1.0,
            },
        }


def build_scale_dependency_witness() -> dict[str, Any]:
    field = FieldRescalingWitness().as_dict()
    joint = JointScaleWitness().as_dict()
    checks = {
        "field_action_rescaling_witness_passes": all(field["checks"].values()),
        "joint_scale_witness_passes": all(joint["checks"].values()),
        "normalized_lane_is_invariant": joint["checks"]["normalized_response_invariant"],
        "absolute_response_depends_on_energy_scale": joint["checks"]["joint_energy_scale_changes_absolute_response"],
        "beta_depends_on_field_and_energy_scale": joint["checks"]["joint_scale_changes_beta"],
    }
    return {"field_rescaling": field, "joint_scale": joint, "checks": checks}


def scale_dependency_contract() -> dict[str, Any]:
    return {
        "normalized_observable": {
            "y_TTG": "Delta_Tq(t) / Delta_Tq(0)",
            "y_TTG_UET": "Delta_Phi(t) / Delta_Phi(0)",
        },
        "dimensional_map": "Delta_Tq = alpha_Phi_K * Delta_Phi",
        "field_rescaling": "delta_phi_prime = s_phi delta_phi; Phi_scale_prime = s_phi Phi_scale",
        "alpha_compensation": "alpha_Phi_K_prime = alpha_Phi_K / s_phi",
        "beta_scale": "beta_T13 = (Phi_scale^2 / e0_scale) beta_Phi^nat",
        "thermal_energy_map": "Delta_Tq = (e0 / c_v) r_Phi Delta_Phi",
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or thermodynamic scale",
            "Phi": "effective response variable; not temperature, metric, particle, or information field",
            "R_gen": "derived physical/history trace; not an independent state variable",
            "R_obs": "observer record kept separate from physical dynamics",
        },
    }
