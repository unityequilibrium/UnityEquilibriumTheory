"""Action normalization, independent derivatives and full thermal matching checks."""

from dataclasses import replace
import unittest

import numpy as np

from docs.core.uet_covariant_matter import CovariantMatterConfig, interaction_energy_density, matter_potential
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_matter_strain_susceptibility import (
    canonical_sources, deformed_free_energy, isentropic_matched_response, thermal_matching, thermal_moments,
)
from docs.core.uet_thermoelastic_spatial_compatibility import isotropic_stiffness


def fixture():
    matter = CovariantMatterConfig(matter_kinetic=1.2, matter_mass_sq=2.7, matter_quartic=.2, response_coupling=.84)
    response = CovariantResponseConfig(epsilon_nc=.5, phi_equilibrium=.1)
    raw = np.array([.48, -.24, .36, 0., 0., 0.])
    return matter, response, raw, canonical_sources(matter, response, raw)


class MatterStrainMatchingTests(unittest.TestCase):
    def test_canonical_mass_matches_actual_action_curvature(self):
        matter, response, raw, source = fixture()
        eps, phi = np.array([.02, -.01, .03, 0., 0., 0.]), .04
        expected = source["mass_squared"]-source["eta"]*phi+source["deformation"]@eps
        errors = []
        for step in (.002, .001, .0005):
            chi = np.array([step, 0.])
            potential = (matter_potential(chi, matter)+interaction_energy_density(response.phi_equilibrium+phi, chi, response, matter)
                         +.5*(raw@eps)*(chi@chi))
            curvature = 2*potential/(step**2*matter.matter_kinetic)
            errors.append(abs(curvature-expected))
        self.assertLess(errors[-1], 1e-7)
        self.assertTrue(errors[0] > errors[1] > errors[2])

    def test_free_energy_derivatives_independently(self):
        t, x = .8, 2.25
        m = thermal_moments(t, x)
        hx, ht = 1e-3, 5e-4
        f = lambda temp, mass: thermal_moments(temp, mass)["free_energy"]
        fx = (f(t, x+hx)-f(t, x-hx))/(2*hx)
        fxx = (f(t, x+hx)-2*f(t, x)+f(t, x-hx))/hx**2
        fxt = (f(t+ht, x+hx)-f(t+ht, x-hx)-f(t-ht, x+hx)+f(t-ht, x-hx))/(4*hx*ht)
        cv = -t*(f(t+ht, x)-2*f(t, x)+f(t-ht, x))/ht**2
        np.testing.assert_allclose([fx, fxx, fxt, cv], [m["mass_derivative"], m["mass_second_derivative"],
                                                      m["mass_temperature_derivative"], m["heat_capacity"]], rtol=2e-6, atol=1e-9)

    def test_mixed_phi_strain_and_temperature_derivatives(self):
        _, _, _, source = fixture()
        matched = thermal_matching(.8, source)
        zero = np.zeros(6)
        step = .002
        for axis in range(3):
            e = zero.copy()
            e[axis] = step
            mixed = (deformed_free_energy(.8, source, step, e)-deformed_free_energy(.8, source, step, -e)
                     -deformed_free_energy(.8, source, -step, e)+deformed_free_energy(.8, source, -step, -e))/(4*step**2)
            self.assertAlmostEqual(mixed/matched["G"][axis], 1., places=5)
        mixed_t = (deformed_free_energy(.8+step, source, step, zero)-deformed_free_energy(.8+step, source, -step, zero)
                   -deformed_free_energy(.8-step, source, step, zero)+deformed_free_energy(.8-step, source, -step, zero))/(4*step**2)
        np.testing.assert_allclose(mixed_t, -matched["entropy_phi_coefficient"], rtol=2e-5)

    def test_reciprocity_and_rank_one_softening(self):
        _, _, _, source = fixture()
        r = thermal_matching(.8, source)
        hessian = r["phi_strain_hessian"]
        np.testing.assert_array_equal(hessian, hessian.T)
        np.testing.assert_allclose(hessian[0, 1:], r["G"])
        self.assertEqual(np.linalg.matrix_rank(hessian, tol=1e-12), 1)
        self.assertLessEqual(np.max(np.linalg.eigvalsh(hessian)), 1e-12)
        self.assertLess(r["delta_phi_curvature"], 0.)
        self.assertGreater(r["delta_heat_capacity"], 0.)

    def test_quadrature_refinement(self):
        for t, x in ((.8, 2.25), (.3, 1.), (1.5, .1)):
            a, b = thermal_moments(t, x, 128), thermal_moments(t, x, 256)
            np.testing.assert_allclose(list(a.values()), list(b.values()), rtol=1e-8, atol=1e-12)

    def test_matter_field_reparameterization(self):
        matter, response, raw, source = fixture()
        original = thermal_matching(.8, source)
        for z in (.5, 3.):
            new = replace(matter, matter_kinetic=matter.matter_kinetic*z**2, matter_mass_sq=matter.matter_mass_sq*z**2,
                          response_coupling=matter.response_coupling*z**2, matter_quartic=matter.matter_quartic*z**4)
            matched = thermal_matching(.8, canonical_sources(new, response, raw*z**2))
            np.testing.assert_allclose(matched["G"], original["G"], rtol=1e-13)
            self.assertAlmostEqual(matched["entropy_phi_coefficient"], original["entropy_phi_coefficient"], places=14)

    def test_natural_energy_scaling(self):
        _, _, _, source = fixture()
        original = thermal_matching(.8, source)
        for z in (.2, 2., 5.):
            moved = dict(mass_squared=source["mass_squared"]*z**2, eta=source["eta"]*z, deformation=source["deformation"]*z**2)
            matched = thermal_matching(.8*z, moved)
            np.testing.assert_allclose(matched["G"]/z**3, original["G"], rtol=1e-12)
            self.assertAlmostEqual(matched["entropy_phi_coefficient"]/z**2, original["entropy_phi_coefficient"], places=13)
            np.testing.assert_allclose(matched["delta_stiffness"]/z**4, original["delta_stiffness"], rtol=1e-12)

    def test_zero_strain_source_does_not_remove_direct_entropy_response(self):
        _, _, _, source = fixture()
        matched = thermal_matching(.8, dict(source, deformation=np.zeros(6)))
        np.testing.assert_array_equal(matched["G"], 0.)
        self.assertGreater(matched["entropy_phi_coefficient"], 0.)
        off = thermal_matching(.8, dict(source, eta=0.))
        np.testing.assert_array_equal(off["G"], 0.)
        self.assertEqual(off["entropy_phi_coefficient"], 0.)

    def test_complete_isentropic_map_matches_entropy_and_stress(self):
        _, _, _, source = fixture()
        r = thermal_matching(.8, source)
        bare = isotropic_stiffness(5., 3.)
        total_k = bare+r["delta_stiffness"]
        total_beta = bare@np.array([.04, .04, .04, 0., 0., 0.])+r["delta_thermal_stress"]
        result = isentropic_matched_response(stiffness=total_k, thermal_stress=total_beta, coupling=r["G"],
                                            entropy_phi_coefficient=r["entropy_phi_coefficient"], temperature=.8,
                                            heat_capacity=2.4+r["delta_heat_capacity"], direction=[1., 0., 0.], delta_phi=.026)
        self.assertLess(abs(result["entropy_residual"]), 1e-14)
        self.assertLess(result["mechanical_residual"], 1e-14)
        self.assertAlmostEqual(result["delta_temperature"], result["gain"]*.026, places=14)
        self.assertGreater(abs(result["direct_entropy_gain"]), 10*abs(result["strain_only_gain"]))

    def test_response_normalization_is_not_fixed_by_thermal_matching(self):
        _, _, _, source = fixture()
        original = thermal_matching(.8, source)
        for scale in (.5, 3.):
            moved = thermal_matching(.8, dict(source, eta=source["eta"]/scale))
            np.testing.assert_allclose(moved["G"]*scale, original["G"], rtol=1e-13)
            self.assertAlmostEqual(moved["entropy_phi_coefficient"]*scale, original["entropy_phi_coefficient"], places=14)

    def test_total_stability_needs_bare_material_and_response_terms(self):
        _, _, _, source = fixture()
        r = thermal_matching(.8, source)
        k = isotropic_stiffness(5., 3.)+r["delta_stiffness"]
        schur = .8+r["delta_phi_curvature"]-r["G"]@np.linalg.solve(k, r["G"])
        self.assertGreater(schur, 0.)
        loop_only_curvature = r["delta_phi_curvature"]-r["G"]@np.linalg.solve(k, r["G"])
        self.assertLess(loop_only_curvature, 0.)

    def test_unstable_mass_and_bad_sources_are_rejected(self):
        _, _, _, source = fixture()
        for t, x in ((0., 1.), (1., 0.), (np.nan, 1.), (1., -1.)):
            with self.assertRaises(ValueError):
                thermal_moments(t, x)
        with self.assertRaises(ValueError):
            deformed_free_energy(.8, source, 100., np.zeros(6))
        with self.assertRaises(ValueError):
            thermal_matching(.8, dict(source, deformation=[1., 2.]))


if __name__ == "__main__":
    unittest.main()
