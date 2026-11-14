"""Regression checks for the scoped thermal comparator measurement design."""

import importlib.util
from pathlib import Path

import numpy as np


SOURCE = Path(__file__).with_name("Research_T13_Thermal_Pole_Measurement_Design.py")
SPEC = importlib.util.spec_from_file_location("thermal_pole_measurement_design", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_same_frequency_does_not_identify_transport_pair():
    result = MODULE.audit()
    assert result["verification_status"] == "ANALYTIC_AND_SYNTHETIC_CONTROL_PASS"
    first, second = result["witnesses"]
    assert np.isclose(first["omega_per_s"], second["omega_per_s"])
    assert not np.isclose(first["gamma_per_s"], second["gamma_per_s"])
    assert not np.isclose(first["conductivity_W_per_m_K"], second["conductivity_W_per_m_K"])
    assert result["full_core_unlock"] is False


def test_pole_pair_and_heat_capacity_recover_coefficients():
    c, kappa, tau, q = 1000.0, 0.125, 0.01, 1000.0
    roots = MODULE.poles(heat_capacity=c, conductivity=kappa, relaxation=tau, wave_number=q)
    recovered = MODULE.inverted_coefficients(
        omega=abs(roots[0].imag), gamma=-roots[0].real,
        wave_number=q, heat_capacity=c,
    )
    assert np.isclose(recovered["relaxation_s"], tau)
    assert np.isclose(recovered["conductivity_W_per_m_K"], kappa)


def test_quadratic_balance_for_multiple_states():
    for temperature, flux in ((0.1, 0.2), (-0.3, 0.8), (0.0, -0.1)):
        result = MODULE.mode_quadratic_balance(
            amplitude_temperature=temperature, amplitude_flux=flux,
            heat_capacity=1000.0, conductivity=0.125,
            relaxation=0.01, wave_number=1000.0,
        )
        assert result["quadratic_functional"] >= 0
        assert result["dissipation"] >= 0
        assert abs(result["ledger_residual"]) < 1e-12


def test_uncertainty_formula_against_finite_difference():
    omega, gamma, q, c = 100.0, 50.0, 1000.0, 1000.0
    f = lambda w, g, k, h: MODULE.inverted_coefficients(
        omega=w, gamma=g, wave_number=k, heat_capacity=h,
    )["conductivity_W_per_m_K"]
    central = f(omega, gamma, q, c)
    sigmas = (5.0, 2.5, 10.0, 50.0)
    values = [omega, gamma, q, c]
    finite_terms = []
    for index, sigma in enumerate(sigmas):
        step = values[index] * 1e-5
        plus, minus = values.copy(), values.copy()
        plus[index] += step
        minus[index] -= step
        derivative = (f(*plus) - f(*minus)) / (2 * step)
        finite_terms.append((derivative * sigma / central) ** 2)
    finite_relative = np.sqrt(sum(finite_terms))
    analytic_relative = MODULE.conductivity_relative_uncertainty(
        omega=omega, gamma=gamma, wave_number=q, heat_capacity=c,
        sigma_omega=sigmas[0], sigma_gamma=sigmas[1],
        sigma_wave_number=sigmas[2], sigma_heat_capacity=sigmas[3],
    )
    assert np.isclose(analytic_relative, finite_relative, rtol=1e-8)
