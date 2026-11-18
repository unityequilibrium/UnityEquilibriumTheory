"""Stellar-model systematic for the T002 prediction R = tau_HB / tau_RGB (sensitivity only).

Test Card T002 (closed, INCONCLUSIVE at z = 2.05) fixed "no stellar-model systematic added (none
quoted)". The source fit R_th = 6.26 Y - 0.12 (Ayala et al. 2014) gives no model error. This module
turns published model-physics ranges into an error on R, so the size of the gap can be judged. It
does NOT change the T002 outcome: the card fixed its rule before the comparison, and adding an error
after seeing the result would be a post-hoc rescue. A new comparison needs a new approved card (T014).

Published ranges, expressed by the source as shifts of the helium abundance Y inferred from R:
  Cassisi, Salaris & Irwin 2003 (ApJ 588, 862; arXiv:astro-ph/0301378), Monte Carlo inputs:
    12C(alpha,gamma)16O rate: Y varies by +/- 0.008, uniform
    breathing-pulse suppression technique: Y increases by 0.003, uniform over [0, 0.003]
Cross-check on the HB lifetime itself:
  Tognini et al. 2023 (arXiv:2310.05745): central He-burning lifetime changes by less than 4 percent
  for 3alpha +/- 24 percent and 12C(alpha,gamma) +/- 35 percent; R scales with tau_HB.
Mixing at the convective-core boundary is the largest open issue (Constantino et al. 2016,
arXiv:1512.04845). Models with unsuppressed breathing pulses are excluded by the observed
R2 = N_AGB / N_HB, so the range above covers only the mixing schemes that pass R2.
"""

from __future__ import annotations

from math import sqrt

R_SLOPE_Y = 6.26  # Ayala et al. 2014, Eq. (1)
R_PRED_T002 = 1.4669
SIGMA_PRED_T002 = 0.0225
R_OBS_T002, SIGMA_OBS_T002 = 1.39, 0.03

C_ALPHA_GAMMA_Y_HALF_RANGE = 0.008
BREATHING_PULSE_Y_RANGE = 0.003
TOGNINI_HB_LIFETIME_MAX_FRACTION = 0.04


def uniform_sigma(full_width: float) -> float:
    return full_width / sqrt(12.0)


def sigma_model_cassisi() -> float:
    """Model error on R from the two Cassisi et al. 2003 ranges, added in quadrature."""
    s_y = sqrt(uniform_sigma(2.0 * C_ALPHA_GAMMA_Y_HALF_RANGE) ** 2 + uniform_sigma(BREATHING_PULSE_Y_RANGE) ** 2)
    return R_SLOPE_Y * s_y


def sigma_model_tognini(r_pred: float = R_PRED_T002) -> float:
    """Cross-check: a uniform +/- 4 percent change of tau_HB, hence of R."""
    return uniform_sigma(2.0 * TOGNINI_HB_LIFETIME_MAX_FRACTION * r_pred)


def z_with_model(sigma_model: float) -> float:
    return abs(R_PRED_T002 - R_OBS_T002) / sqrt(SIGMA_PRED_T002**2 + SIGMA_OBS_T002**2 + sigma_model**2)


def compute() -> dict:
    sc, st = sigma_model_cassisi(), sigma_model_tognini()
    return {
        "sigma_model_cassisi2003": sc,
        "sigma_model_tognini2023_crosscheck": st,
        "z_t002_as_registered": z_with_model(0.0),
        "z_sensitivity_with_cassisi_model_error": z_with_model(sc),
        "z_sensitivity_with_tognini_model_error": z_with_model(st),
    }


if __name__ == "__main__":
    for key, value in compute().items():
        print(f"{key}: {value:.4f}")
