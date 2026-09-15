"""Structural beta-correspondence witnesses for the Topic 13 bridge.

The action-derived normal lane has a natural-unit curvature/slope, while the
named Topic 13 beta contract is a dimensionless K-local stiffness slope.  This
module records the scale transformations that leave the current evidence
unchanged and therefore prevent identifying one with the other without a new
normalization and energy/temperature map.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BetaCorrespondenceWitness:
    field_scale: float
    energy_scale: float
    temperature_scale: float
    normalized_beta_t13: float
    action_beta_natural: float
    inferred_beta_t13_from_bridge: float | None
    inferred_alpha_phi_k: float | None


def scale_witness(
    *,
    field_scale: float,
    energy_scale: float,
    temperature_scale: float,
    normalized_beta_t13: float,
    action_beta_natural: float,
) -> BetaCorrespondenceWitness:
    """Return one admissible scale completion without selecting a physical one.

    A natural curvature/slope can be converted only after field, free-energy,
    and temperature scales are supplied.  The returned inferred values are
    intentionally optional and are not promoted as measurements.
    """

    if field_scale <= 0.0 or energy_scale <= 0.0 or temperature_scale <= 0.0:
        raise ValueError("scale witnesses require positive scales")
    return BetaCorrespondenceWitness(
        field_scale=float(field_scale),
        energy_scale=float(energy_scale),
        temperature_scale=float(temperature_scale),
        normalized_beta_t13=float(normalized_beta_t13),
        action_beta_natural=float(action_beta_natural),
        inferred_beta_t13_from_bridge=None,
        inferred_alpha_phi_k=None,
    )


def beta_correspondence_contract() -> dict[str, object]:
    """Return the no-go scope and the missing map required for correspondence."""

    return {
        "status": "SCOPED_BETA_CORRESPONDENCE_UNDERDETERMINED",
        "equations": {
            "action_lane": "beta_action_natural=T*partial_T(partial_Phi^2 Omega_T)",
            "topic13_lane": "beta_T13=T0*(da_Phi/dT)|T0",
            "required_map": "beta_T13 = F(field_normalization, free_energy_scale, temperature_unit, action_beta_natural)",
            "scale_family": "Phi'=s_Phi*Phi; e0'=s_e*e0; T'=s_T*T leaves normalized lane unchanged until F is declared",
        },
        "units": {
            "beta_action_natural": "natural mass dimension two",
            "beta_T13": "dimensionless local stiffness-temperature slope",
            "alpha_Phi_K": "K per normalized Phi; independent calibration or derivation required",
            "missing_scales": "field normalization, free-energy density scale, and natural-to-Kelvin map",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not charge or beta",
            "Phi": "effective response variable; action field and normalized lane require explicit mapping",
            "R_gen": "derived history trace only; not used as state or feedback",
            "R_obs": "observer record separate from the correspondence map",
        },
        "claim_boundary": "The current action-derived normal curvature and the named normalized beta contract cannot be identified numerically without a declared scale map. This is a scoped no-go, not a proof that a future finite-temperature action or independent calibration cannot provide the map.",
    }


__all__ = ["BetaCorrespondenceWitness", "scale_witness", "beta_correspondence_contract"]
