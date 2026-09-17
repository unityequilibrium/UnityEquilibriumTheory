"""Unit, source-role, rank and conditional-design tests for the Raman route."""

import unittest

import numpy as np
from scipy.constants import c, h, hbar, k as k_B

from docs.core.uet_raman_deformation_constraint import (
    spectral_constraint, absolute_slope_constraint, hydrostatic_row, tensor_identifiability,
    independent_axial_design, oscillator_heat_capacity_ratio,
)


class RamanDeformationTests(unittest.TestCase):
    def test_absolute_and_logarithmic_slopes_have_same_central_conversion(self):
        for nu, delta in ((44., .11), (1579., .00296)):
            a = spectral_constraint(nu, delta)['squared_gap_pressure_derivative_J2_per_Pa']
            b = absolute_slope_constraint(nu, nu*delta)['squared_gap_pressure_derivative_J2_per_Pa']
            self.assertAlmostEqual(a/b, 1., places=14)

    def test_source_table_error_is_not_substituted_for_abstract_error(self):
        narrow = spectral_constraint(1579., .00296, frequency_error=1., slope_error=.00002)
        broad = absolute_slope_constraint(1579., 4.7, frequency_error=1., slope_error=.3)
        n = narrow['pressure_derivative_sensitivity_envelope_J2_per_Pa']
        b = broad['pressure_derivative_sensitivity_envelope_J2_per_Pa']
        self.assertLess(b[0], n[0])
        self.assertGreater(b[1], n[1])

    def test_wavenumber_matches_independent_angular_frequency(self):
        for nu in (44., 1579.):
            got = spectral_constraint(nu, .11)
            self.assertAlmostEqual(got['gap_J']/(hbar*2*np.pi*c*100*nu), 1., places=14)
            self.assertAlmostEqual(got['gap_over_k_B_K']*k_B/got['gap_J'], 1., places=14)

    def test_pressure_derivative_matches_independent_finite_difference(self):
        for nu, slope in ((44., .11), (1579., .00296), (300., -.02)):
            step_Pa = 1e3
            def spectral_energy_squared(p_Pa):
                frequency_Hz = c*100*nu*np.exp(slope*p_Pa/1e9)
                return (h*frequency_Hz)**2
            fd = (spectral_energy_squared(step_Pa)-spectral_energy_squared(-step_Pa))/(2*step_Pa)
            expected = spectral_constraint(nu, slope)['squared_gap_pressure_derivative_J2_per_Pa']
            self.assertLess(abs(fd/expected-1), 1e-7)

    def test_uncertainty_envelope_contains_all_correlated_samples(self):
        rng = np.random.default_rng(1989)
        for slope in (.11, 0., -.11):
            result = spectral_constraint(44., slope, frequency_error=1., slope_error=.008)
            low, high = result['pressure_derivative_sensitivity_envelope_J2_per_Pa']
            for nu, delta in zip(rng.uniform(43, 45, 100), rng.uniform(slope-.008, slope+.008, 100)):
                value = spectral_constraint(nu, delta)['squared_gap_pressure_derivative_J2_per_Pa']
                self.assertGreaterEqual(value, low)
                self.assertLessEqual(value, high)

    def test_hydrostatic_rank_and_null_family(self):
        record = tensor_identifiability(1250., 35.7)
        row = hydrostatic_row(1250., 35.7)
        self.assertEqual(record['rank'], 1)
        self.assertEqual(record['nullity'], 1)
        base = np.array([2., -8.])
        for offset in (-100., -1., 0., 10., 100.):
            self.assertAlmostEqual(row@(base+offset*record['single_mode_null_direction']), row@base, places=14)
        self.assertFalse(record['component_bounds_identified'])

    def test_two_modes_are_not_two_observations_of_same_coefficients(self):
        record = tensor_identifiability(1250., 35.7, mode_count=2)
        self.assertEqual(record['rank'], 2)
        self.assertEqual(record['unknown_count'], 4)
        self.assertEqual(record['nullity'], 2)

    def test_independent_strain_design_recovers_synthetic_components(self):
        row = hydrostatic_row(1250., 35.7)
        target = np.array([-.4, -8.])
        pressure_slope = row@target/2
        axial_slope = target[1]/2
        got = independent_axial_design(1250., 35.7, pressure_slope, axial_slope)
        np.testing.assert_allclose(got, target, rtol=1e-12, atol=1e-12)

    def test_oscillator_ratio_is_independent_energy_temperature_derivative(self):
        for nu in (44., 1579.):
            for temperature in (100., 200., 300.):
                energy = h*c*100*nu
                dt = temperature*1e-5
                def internal_energy(t):
                    return energy/np.expm1(energy/(k_B*t))
                fd = (internal_energy(temperature+dt)-internal_energy(temperature-dt))/(2*dt*k_B)
                value = oscillator_heat_capacity_ratio(nu, temperature)
                self.assertLess(abs(fd/value-1), 1e-7)
                self.assertGreater(value, 0.)
                self.assertLessEqual(value, 1.)

    def test_oscillator_limits_and_ordering(self):
        self.assertAlmostEqual(oscillator_heat_capacity_ratio(44., 1e7), 1., places=10)
        self.assertLess(oscillator_heat_capacity_ratio(1579., 10.), 1e-80)
        for temperature in (100., 200., 300.):
            self.assertGreater(oscillator_heat_capacity_ratio(44., temperature), oscillator_heat_capacity_ratio(1579., temperature))

    def test_no_free_physical_alpha_or_D_output(self):
        record = spectral_constraint(44., .11)
        self.assertNotIn('alpha_Phi_K', record)
        self.assertNotIn('D_ab', record)
        self.assertNotIn('D_c', record)

    def test_invalid_inputs_are_not_regularized(self):
        for args in ((0., .1), (-1., .1), (44., np.nan)):
            with self.assertRaises(ValueError):
                spectral_constraint(*args)
        with self.assertRaises(ValueError):
            spectral_constraint(44., .1, frequency_error=45.)
        with self.assertRaises(ValueError):
            hydrostatic_row(0., 35.)
        with self.assertRaises(ValueError):
            tensor_identifiability(1250., 35., mode_count=0)
        with self.assertRaises(ValueError):
            independent_axial_design(1250., 35., .11, np.nan)
        with self.assertRaises(ValueError):
            oscillator_heat_capacity_ratio(44., 0.)


if __name__ == '__main__':
    unittest.main()
