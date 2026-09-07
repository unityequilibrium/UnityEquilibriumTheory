"""Independent He-4 calibration for the local normalized Phi response lane."""

from __future__ import annotations

import math

from docs.core.he4_svp_reference import reference_row


REFERENCE_TEMPERATURE_K = 1.7
TEMPERATURE_STEP_K = 0.1
SUPERFLUID_DENSITY_RELATIVE_UNCERTAINTY_BOUND = 0.005
TOTAL_DENSITY_FIT_RELATIVE_DEVIATION = 0.5e-6
ACTION_REFERENCE_TEMPERATURE_NATURAL = 0.22
ACTION_ALPHA_TEMPERATURE_NATURAL = 0.0023138578447835533
ACTION_ALPHA_TEMPERATURE_NATURAL_REFINED = 0.002313912812789792


def _fraction_uncertainty_bound(fraction: float) -> float:
    relative = (
        SUPERFLUID_DENSITY_RELATIVE_UNCERTAINTY_BOUND
        + TOTAL_DENSITY_FIT_RELATIVE_DEVIATION
    )
    return abs(fraction) * relative


def calibration_record() -> dict[str, float | str | dict[str, bool]]:
    """Derive a local, holdout-independent alpha and natural-field map."""

    lower = reference_row(REFERENCE_TEMPERATURE_K - TEMPERATURE_STEP_K)
    center = reference_row(REFERENCE_TEMPERATURE_K)
    upper = reference_row(REFERENCE_TEMPERATURE_K + TEMPERATURE_STEP_K)
    f_lower = float(lower["superfluid_fraction"])
    f_center = float(center["superfluid_fraction"])
    f_upper = float(upper["superfluid_fraction"])
    derivative = (f_upper - f_lower) / (2.0 * TEMPERATURE_STEP_K)
    derivative_uncertainty = (
        _fraction_uncertainty_bound(f_upper)
        + _fraction_uncertainty_bound(f_lower)
    ) / (2.0 * TEMPERATURE_STEP_K)

    alpha_phi_k = f_center / derivative
    alpha_uncertainty = abs(alpha_phi_k) * (
        _fraction_uncertainty_bound(f_center) / abs(f_center)
        + derivative_uncertainty / abs(derivative)
    )
    kelvin_per_natural_temperature = (
        REFERENCE_TEMPERATURE_K / ACTION_REFERENCE_TEMPERATURE_NATURAL
    )
    action_alpha_uncertainty = abs(
        ACTION_ALPHA_TEMPERATURE_NATURAL_REFINED
        - ACTION_ALPHA_TEMPERATURE_NATURAL
    )
    z_phi = (
        kelvin_per_natural_temperature
        * ACTION_ALPHA_TEMPERATURE_NATURAL
        / alpha_phi_k
    )
    z_phi_uncertainty = abs(z_phi) * (
        action_alpha_uncertainty / abs(ACTION_ALPHA_TEMPERATURE_NATURAL)
        + alpha_uncertainty / abs(alpha_phi_k)
    )
    return {
        "record_id": "T13_HE4_LOCAL_SUPERFLUID_RESPONSE_ALPHA",
        "record_kind": "EXTERNAL_INPUT",
        "data_role": "CALIBRATION",
        "temperature_K": REFERENCE_TEMPERATURE_K,
        "temperature_step_K": TEMPERATURE_STEP_K,
        "superfluid_fraction_lower": f_lower,
        "superfluid_fraction_reference": f_center,
        "superfluid_fraction_upper": f_upper,
        "d_superfluid_fraction_dT_per_K": derivative,
        "d_superfluid_fraction_dT_uncertainty_bound_per_K": derivative_uncertainty,
        "alpha_Phi_K": alpha_phi_k,
        "alpha_uncertainty_K_per_normalized_base_Phi": alpha_uncertainty,
        "alpha_units": "K per normalized base Phi",
        "phi_units": "normalized base Phi",
        "phi_mapping": "Delta_Phi_norm = Delta(rho_s/rho) / (rho_s/rho)|T0",
        "temperature_mapping": "T_K = theta_T * T_natural",
        "theta_T_K_per_natural_temperature": kelvin_per_natural_temperature,
        "Z_Phi_normalized_per_natural_Phi": z_phi,
        "Z_Phi_uncertainty_bound": z_phi_uncertainty,
        "action_mapping": "Delta_Phi_norm = Z_Phi Delta_Phi_natural",
        "uncertainty_class": "CONSERVATIVE_SOURCE_AND_NUMERICAL_BOUND_CONDITIONAL_ON_RECOMMENDED_T_GRID",
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "fit_or_tuning_used": False,
        },
    }
