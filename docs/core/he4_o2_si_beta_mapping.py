"""State-matched SI scale and normalized beta map for the He-4 O(2) lane."""

from __future__ import annotations

from docs.core.he4_o2_response_calibration import calibration_record
from docs.core.he4_svp_reference import reference_row


REFERENCE_TEMPERATURE_K = 1.7
TEMPERATURE_STANDARD_UNCERTAINTY_K = 0.0002
BOLTZMANN_CONSTANT_J_PER_K = 1.380649e-23
HE4_RELATIVE_ATOMIC_MASS = 4.00260325413
HE4_RELATIVE_ATOMIC_MASS_UNCERTAINTY = 0.00000000006
ATOMIC_MASS_CONSTANT_KG = 1.66053906892e-27
ATOMIC_MASS_CONSTANT_UNCERTAINTY_KG = 0.00000000052e-27
TOTAL_DENSITY_RELATIVE_UNCERTAINTY_BOUND = 0.5e-6
ACTION_BETA_NATURAL = -2.4271981641363002e-6
ACTION_BETA_NATURAL_REFINED = -2.427707354265597e-6


def si_beta_record() -> dict[str, float | str | dict[str, bool]]:
    """Return the explicit external SI scale and propagated beta mapping."""

    density = float(reference_row(REFERENCE_TEMPERATURE_K)["total_density_kg_m3"])
    he4_mass = HE4_RELATIVE_ATOMIC_MASS * ATOMIC_MASS_CONSTANT_KG
    he4_mass_relative_uncertainty = (
        HE4_RELATIVE_ATOMIC_MASS_UNCERTAINTY / HE4_RELATIVE_ATOMIC_MASS
        + ATOMIC_MASS_CONSTANT_UNCERTAINTY_KG / ATOMIC_MASS_CONSTANT_KG
    )
    number_density = density / he4_mass
    e0 = number_density * BOLTZMANN_CONSTANT_J_PER_K * REFERENCE_TEMPERATURE_K
    e0_relative_uncertainty = (
        TOTAL_DENSITY_RELATIVE_UNCERTAINTY_BOUND
        + he4_mass_relative_uncertainty
        + TEMPERATURE_STANDARD_UNCERTAINTY_K / REFERENCE_TEMPERATURE_K
    )
    e0_uncertainty = abs(e0) * e0_relative_uncertainty

    calibration = calibration_record()
    z_phi = float(calibration["Z_Phi_normalized_per_natural_Phi"])
    z_phi_uncertainty = float(calibration["Z_Phi_uncertainty_bound"])
    beta_natural_uncertainty = abs(
        ACTION_BETA_NATURAL_REFINED - ACTION_BETA_NATURAL
    )
    beta_t13 = ACTION_BETA_NATURAL / (z_phi * z_phi)
    beta_t13_relative_uncertainty = (
        beta_natural_uncertainty / abs(ACTION_BETA_NATURAL)
        + 2.0 * z_phi_uncertainty / abs(z_phi)
    )
    beta_t13_uncertainty = abs(beta_t13) * beta_t13_relative_uncertainty
    beta_si = e0 * beta_t13
    beta_si_relative_uncertainty = (
        beta_t13_relative_uncertainty + e0_relative_uncertainty
    )
    beta_si_uncertainty = abs(beta_si) * beta_si_relative_uncertainty

    return {
        "record_id": "T13_HE4_O2_SI_SCALE_AND_NORMALIZED_BETA",
        "record_kind": "EXTERNAL_SCALE_CONVENTION_PLUS_ACTION_DERIVATION",
        "data_role": "CALIBRATION",
        "temperature_scale": "ITS-90",
        "temperature_K": REFERENCE_TEMPERATURE_K,
        "temperature_standard_uncertainty_K": TEMPERATURE_STANDARD_UNCERTAINTY_K,
        "total_density_kg_m3": density,
        "he4_atom_mass_kg": he4_mass,
        "he4_atom_mass_relative_uncertainty_bound": he4_mass_relative_uncertainty,
        "number_density_m3": number_density,
        "energy_density_scale_J_m3": e0,
        "energy_density_scale_uncertainty_J_m3": e0_uncertainty,
        "energy_density_scale_relative_uncertainty_bound": e0_relative_uncertainty,
        "energy_scale_mapping": "e0 = (rho / m_He4) k_B T0",
        "free_energy_mapping": "f_SI = e0 f_natural",
        "phi_mapping": "Delta_Phi_norm = Z_Phi Delta_Phi_natural",
        "Z_Phi_normalized_per_natural_Phi": z_phi,
        "Z_Phi_uncertainty_bound": z_phi_uncertainty,
        "beta_action_natural": ACTION_BETA_NATURAL,
        "beta_action_natural_uncertainty_bound": beta_natural_uncertainty,
        "beta_T13": beta_t13,
        "beta_T13_uncertainty_bound": beta_t13_uncertainty,
        "beta_T13_units": "natural free-energy scale per normalized Phi squared",
        "beta_SI_J_m3_per_normalized_Phi2": beta_si,
        "beta_SI_uncertainty_J_m3_per_normalized_Phi2": beta_si_uncertainty,
        "beta_mapping": "beta_T13 = beta_natural / Z_Phi^2; beta_SI = e0 beta_T13",
        "uncertainty_policy": "Conservative absolute-bound addition; no independence assumption.",
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "fit_or_tuning_used": False,
            "landauer_identity_used": False,
        },
    }
