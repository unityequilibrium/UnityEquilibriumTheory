"""Spectroscopic constraints, not identification of UET Phi or material modes."""

from __future__ import annotations

from itertools import product

import numpy as np
from scipy.constants import c, h, k as k_B


def spectral_constraint(wavenumber_cm, log_pressure_slope_GPa, *, frequency_error=0., slope_error=0.):
    values = [wavenumber_cm, log_pressure_slope_GPa, frequency_error, slope_error]
    if not np.isfinite(values).all() or frequency_error < 0 or slope_error < 0 or wavenumber_cm-frequency_error <= 0:
        raise ValueError('finite values, nonnegative errors and positive frequency interval required')
    def energy(nu):
        return h*c*100*nu
    def derivative(nu, delta):
        return 2*energy(nu)**2*delta/1e9
    freq_interval = [wavenumber_cm-frequency_error, wavenumber_cm+frequency_error]
    slope_interval = [log_pressure_slope_GPa-slope_error, log_pressure_slope_GPa+slope_error]
    corners = [derivative(nu, delta) for nu, delta in product(freq_interval, slope_interval)]
    return dict(gap_J=energy(wavenumber_cm), gap_over_k_B_K=energy(wavenumber_cm)/k_B,
                squared_gap_J2=energy(wavenumber_cm)**2,
                squared_gap_pressure_derivative_J2_per_Pa=derivative(wavenumber_cm, log_pressure_slope_GPa),
                log_squared_gap_pressure_derivative_per_Pa=2*log_pressure_slope_GPa/1e9,
                gap_sensitivity_envelope_J=[energy(nu) for nu in freq_interval],
                pressure_derivative_sensitivity_envelope_J2_per_Pa=[min(corners), max(corners)],
                uncertainty_interpretation='endpoint sensitivity envelope, not a confidence interval')


def absolute_slope_constraint(wavenumber_cm, absolute_slope_cm_per_GPa, *, frequency_error=0., slope_error=0.):
    values = [wavenumber_cm, absolute_slope_cm_per_GPa, frequency_error, slope_error]
    if not np.isfinite(values).all() or frequency_error < 0 or slope_error < 0 or wavenumber_cm-frequency_error <= 0:
        raise ValueError('finite values, nonnegative errors and positive frequency interval required')
    def derivative(nu, slope):
        return 2*(h*c*100)**2*nu*slope/1e9
    corners = [derivative(nu, slope) for nu, slope in product(
        [wavenumber_cm-frequency_error, wavenumber_cm+frequency_error],
        [absolute_slope_cm_per_GPa-slope_error, absolute_slope_cm_per_GPa+slope_error])]
    return dict(squared_gap_pressure_derivative_J2_per_Pa=derivative(wavenumber_cm, absolute_slope_cm_per_GPa),
                pressure_derivative_sensitivity_envelope_J2_per_Pa=[min(corners), max(corners)],
                uncertainty_interpretation='endpoint sensitivity envelope, not a confidence interval')


def hydrostatic_row(modulus_a_GPa, modulus_c_GPa):
    if not np.isfinite([modulus_a_GPa, modulus_c_GPa]).all() or min(modulus_a_GPa, modulus_c_GPa) <= 0:
        raise ValueError('finite positive axial moduli required')
    return np.array([-2/modulus_a_GPa, -1/modulus_c_GPa])


def tensor_identifiability(modulus_a_GPa, modulus_c_GPa, mode_count=1):
    if not isinstance(mode_count, int) or isinstance(mode_count, bool) or mode_count < 1:
        raise ValueError('positive integer mode count required')
    row = hydrostatic_row(modulus_a_GPa, modulus_c_GPa)
    null = np.array([-row[1], row[0]])
    null /= np.linalg.norm(null)
    matrix = np.kron(np.eye(mode_count), row[None, :])
    return dict(measurement_matrix=matrix, matrix_units='GPa^-1',
                unknowns='two dimensionless D_i/x_mode coefficients per mode',
                rank=int(np.linalg.matrix_rank(matrix)), unknown_count=2*mode_count,
                nullity=mode_count, single_mode_null_direction=null,
                null_residual=float(abs(row@null)), component_bounds_identified=False)


def independent_axial_design(modulus_a_GPa, modulus_c_GPa, log_pressure_slope_GPa,
                             log_frequency_axial_strain_slope):
    """Hypothetical complete two-direction design, not filled from Raman pressure alone."""
    if not np.isfinite([log_pressure_slope_GPa, log_frequency_axial_strain_slope]).all():
        raise ValueError('both independently supplied measured slopes must be finite')
    row = hydrostatic_row(modulus_a_GPa, modulus_c_GPa)
    matrix = np.vstack([row, [0., 1.]])
    rhs = np.array([2*log_pressure_slope_GPa, 2*log_frequency_axial_strain_slope])
    return np.linalg.solve(matrix, rhs)


def oscillator_heat_capacity_ratio(wavenumber_cm, temperature_K):
    """One oscillator at a frozen source frequency; not a branch/sample heat capacity."""
    if not np.isfinite([wavenumber_cm, temperature_K]).all() or min(wavenumber_cm, temperature_K) <= 0:
        raise ValueError('finite positive frequency and temperature required')
    z = h*c*100*wavenumber_cm/(k_B*temperature_K)
    denominator = -np.expm1(-z)
    return float((z/denominator)**2*np.exp(-z))
