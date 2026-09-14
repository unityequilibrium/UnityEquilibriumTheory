"""Independent elasticity, coordinate and real-space checks; no source data."""

import unittest

import numpy as np

from docs.core.uet_thermoelastic_spatial_compatibility import (
    isotropic_stiffness, mandel, spatial_response, strain_map, tensor,
)


def reference():
    return dict(stiffness=isotropic_stiffness(5., 3.),
                expansion=np.array([.04, .04, .04, 0., 0., 0.]),
                coupling=np.array([.7, .7, .7, 0., 0., 0.]),
                direction=np.array([1., 0., 0.]), temperature=.8,
                heat_capacity=2.4, phi_response=.026, response_curvature=.8)


def rotated_inputs(p, rotation):
    basis = np.eye(6)
    change = np.column_stack([mandel(rotation @ tensor(e) @ rotation.T) for e in basis])
    return dict(p, stiffness=change @ p["stiffness"] @ change.T,
                expansion=change @ p["expansion"], coupling=change @ p["coupling"],
                direction=rotation @ p["direction"])


class SpatialCompatibilityTests(unittest.TestCase):
    def test_isotropic_longitudinal_solution_and_free_boundary_difference(self):
        p = reference()
        result = spatial_response(**p)
        analytic = .8*5*.12*.7 / ((5+4*3/3)*2.4 + .8*25*.12**2)
        self.assertAlmostEqual(result["gain_per_phi_response"], analytic, places=14)
        self.assertGreater(result["homogeneous_incompatible_strain_norm"], 1e-4)
        self.assertGreater(abs(result["homogeneous_gain_per_phi_response"]-analytic), .01)
        self.assertLess(result["mechanical_residual"], 1e-14)
        self.assertLess(abs(result["entropy_residual"]), 1e-14)
        self.assertGreater(np.linalg.norm(result["stress"]), 1e-3)

    def test_fixed_entropy_elimination_is_independent_block_solution(self):
        rng = np.random.default_rng(130907)
        for _ in range(10):
            p = reference()
            a = rng.normal(size=(6, 6))
            p.update(stiffness=a.T@a+np.eye(6), expansion=rng.normal(size=6)*.03,
                     coupling=rng.normal(size=6)*.2, direction=rng.normal(size=3))
            r = spatial_response(**p)
            b = strain_map(p["direction"])
            beta = p["stiffness"] @ p["expansion"]
            kad = p["stiffness"]+p["temperature"]/p["heat_capacity"]*np.outer(beta, beta)
            v = np.linalg.solve(b.T@kad@b, -b.T@p["coupling"]*p["phi_response"])
            dt = -p["temperature"]*(beta@b@v)/p["heat_capacity"]
            np.testing.assert_allclose(r["strain"], b@v, atol=1e-14, rtol=1e-12)
            self.assertAlmostEqual(r["delta_temperature"], dt, places=14)
            self.assertAlmostEqual(r["closed_form_temperature"], dt, places=14)

    def test_full_rotation_including_shear(self):
        p = reference()
        p.update(stiffness=np.diag([8., 6., 4., 2., 3., 5.]),
                 expansion=np.array([-.03, -.03, .18, .02, -.01, .04]),
                 coupling=np.array([.2, .2, .5, -.1, .04, .08]),
                 direction=np.array([1., 2., 3.]))
        rng = np.random.default_rng(32013)
        for _ in range(8):
            rot, _ = np.linalg.qr(rng.normal(size=(3, 3)))
            if np.linalg.det(rot) < 0:
                rot[:, 0] *= -1
            base, moved = spatial_response(**p), spatial_response(**rotated_inputs(p, rot))
            self.assertAlmostEqual(base["delta_temperature"], moved["delta_temperature"], places=14)
            np.testing.assert_allclose(tensor(moved["strain"]), rot@tensor(base["strain"])@rot.T,
                                       atol=1e-14, rtol=1e-12)

    def test_direct_tensor_equilibrium_and_compatible_gradient(self):
        p = reference()
        p["direction"] = np.array([2., -1., 3.])
        r = spatial_response(**p)
        n = p["direction"]/np.linalg.norm(p["direction"])
        v = np.array(r["displacement_gradient_amplitude"])
        eps = (np.outer(n, v)+np.outer(v, n))/2
        np.testing.assert_allclose(tensor(r["strain"]), eps, atol=1e-14)
        np.testing.assert_allclose(tensor(r["stress"])@n, np.zeros(3), atol=1e-14)

    def test_periodic_displacement_gradient_converges_without_padding(self):
        errors = []
        for size in (32, 64, 128):
            x = np.arange(size)*2*np.pi/size
            u = np.sin(x)
            du = (np.roll(u, -1)-np.roll(u, 1))/(4*np.pi/size)
            errors.append(np.max(np.abs(du-np.cos(x))))
        self.assertTrue(all(3.9 < errors[i]/errors[i+1] < 4.1 for i in range(2)))

    def test_energy_unit_rescaling(self):
        p = reference()
        base = spatial_response(**p)
        for scale in (.01, 2., 100.):
            moved = dict(p, stiffness=p["stiffness"]*scale**4,
                         expansion=p["expansion"]/scale, coupling=p["coupling"]*scale**3,
                         temperature=p["temperature"]*scale, heat_capacity=p["heat_capacity"]*scale**3,
                         phi_response=p["phi_response"]*scale, response_curvature=p["response_curvature"]*scale**2)
            r = spatial_response(**moved)
            np.testing.assert_allclose(r["strain"], base["strain"], atol=1e-14, rtol=1e-12)
            self.assertAlmostEqual(r["delta_temperature"]/scale, base["delta_temperature"], places=14)

    def test_isotropic_orientation_and_small_positive_shear_limit(self):
        p = reference()
        base = spatial_response(**p)
        for n in ([1., 2., 3.], [-1., 0., 0.], [0., 0., 1.], [1e200, 0., 0.]):
            r = spatial_response(**dict(p, direction=n))
            self.assertAlmostEqual(r["delta_temperature"], base["delta_temperature"], places=14)
        errors = []
        for shear in (.1, .01, .001):
            r = spatial_response(**dict(p, stiffness=isotropic_stiffness(5., shear)))
            errors.append(abs(r["gain_per_phi_response"]-r["homogeneous_gain_per_phi_response"]))
        self.assertTrue(errors[0] > errors[1] > errors[2])

    def test_invalid_parameters_and_zero_coupling(self):
        p = reference()
        for replacement in (dict(direction=[0., 0., 0.]), dict(stiffness=-p["stiffness"]),
                            dict(temperature=0.), dict(heat_capacity=-1.),
                            dict(coupling=[np.nan]*6), dict(stiffness=np.zeros((3, 3)))):
            with self.assertRaises(ValueError):
                spatial_response(**dict(p, **replacement))
        k = p["stiffness"].copy()*1e-20
        k[0, 1] += 1e-22
        with self.assertRaises(ValueError):
            spatial_response(**dict(p, stiffness=k))
        self.assertEqual(spatial_response(**dict(p, coupling=np.zeros(6)))["delta_temperature"], 0.)
        self.assertLess(spatial_response(**dict(p, coupling=p["coupling"]*100))[
            "directional_fixed_T_schur_margin"], 0.)


if __name__ == "__main__":
    unittest.main()
