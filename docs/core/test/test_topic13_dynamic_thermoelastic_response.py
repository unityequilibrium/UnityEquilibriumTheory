"""Independent dynamic, thermodynamic and limiting-case checks for the candidate."""

import unittest

import numpy as np
from scipy.integrate import solve_ivp

from docs.core.uet_dynamic_thermoelastic_response import material_mode
from docs.core.uet_thermoelastic_spatial_compatibility import (
    isotropic_stiffness, mandel, spatial_response, tensor,
)


def inputs():
    return dict(stiffness=isotropic_stiffness(5., 3.), expansion=np.array([.04, .04, .04, 0., 0., 0.]),
                coupling=np.array([.7, .7, .7, 0., 0., 0.]), direction=np.array([1., 0., 0.]),
                q=1., rho=1., temperature=.8, heat_capacity=2.4, conductivity=.3, relaxation=.2)


class DynamicMaterialTests(unittest.TestCase):
    def test_fourier_decoupled_analytic_heat_decay(self):
        p = dict(inputs(), relaxation=0., expansion=np.zeros(6))
        mode = material_mode(**p)
        x = mode.initial_state(.03)
        t = np.linspace(0, 10, 51)
        y = mode.evolve_constant(t, x)
        np.testing.assert_allclose(y[:, 6], x[6]*np.exp(-p["conductivity"]*p["q"]**2*t/p["heat_capacity"]),
                                   rtol=1e-12, atol=1e-14)

    def test_cattaneo_decoupled_analytic_underdamped_control(self):
        p = dict(inputs(), relaxation=2., conductivity=4., expansion=np.zeros(6))
        mode = material_mode(**p)
        x = mode.initial_state(.03)
        t = np.linspace(0, 12, 81)
        rate = 1/(2*p["relaxation"])
        omega = np.sqrt(p["conductivity"]*p["q"]**2/(p["heat_capacity"]*p["relaxation"])-rate**2)
        analytic = x[6]*np.exp(-rate*t)*(np.cos(omega*t)+rate/omega*np.sin(omega*t))
        np.testing.assert_allclose(mode.evolve_constant(t, x)[:, 6], analytic, rtol=1e-11, atol=1e-14)

    def test_entropy_is_independent_initial_input(self):
        mode = material_mode(**inputs())
        v = np.array([.003, -.004, .001])
        x = mode.initial_state(.03, strain=v)
        self.assertAlmostEqual(mode.thermal_stress@x[:3]+mode.heat_capacity*x[6]/mode.temperature, .03)
        heat_only = mode.evolve_constant([0., .5, 1.], mode.initial_state(.03))
        self.assertGreater(np.max(np.abs(heat_only[:, 6])), 1e-3)
        np.testing.assert_array_equal(mode.evolve_constant([0., 1.], mode.initial_state(0.)), 0.)

    def test_direct_balance_and_metric_identity(self):
        rng = np.random.default_rng(130908)
        for tau in (0., .2, 2.):
            mode = material_mode(**dict(inputs(), relaxation=tau))
            self.assertGreater(np.min(np.linalg.eigvalsh(mode.metric)), 0.)
            loss = np.zeros_like(mode.matrix)
            if tau:
                loss[7, 7] = -2/(mode.temperature*mode.conductivity)
            else:
                loss[6, 6] = -2*mode.conductivity*mode.q**2/mode.temperature
            np.testing.assert_allclose(mode.metric@mode.matrix+mode.matrix.T@mode.metric, loss, atol=1e-13)
            for _ in range(10):
                x = rng.normal(size=len(mode.matrix))*.1
                b = mode.balance(x, phi=.02, heat=.004)
                self.assertLess(abs(b["balance_residual"]), 1e-13)
                self.assertGreaterEqual(b["dissipation"], 0.)
                dx = mode.matrix@x+mode.phi_port*.02+mode.heat_port*.004
                flux = x[7] if tau else mode.conductivity*mode.q*x[6]
                entropy_rate = mode.thermal_stress@dx[:3]+mode.heat_capacity*dx[6]/mode.temperature
                self.assertAlmostEqual(entropy_rate, (.004-mode.q*flux)/mode.temperature, places=13)

    def test_time_solution_matches_independent_integration(self):
        for tau in (0., .2):
            mode = material_mode(**dict(inputs(), relaxation=tau))
            t = np.linspace(0, 8, 121)
            x = mode.initial_state(.03, strain_rate=[.001, 0., -.002])
            def rhs(_, y):
                flux = y[7] if tau else mode.conductivity*mode.q*y[6]
                out = np.zeros(len(y))
                out[:3] = y[3:6]
                out[3:6] = -mode.q**2/mode.rho*(mode.acoustic@y[:3]-mode.thermal_stress*y[6]+mode.coupling*.02)
                out[6] = (-mode.temperature*mode.thermal_stress@y[3:6]-mode.q*flux+.004)/mode.heat_capacity
                if tau:
                    out[7] = (mode.conductivity*mode.q*y[6]-y[7])/tau
                return out
            sol = solve_ivp(rhs, [0., 8.], x, t_eval=t, rtol=1e-10, atol=1e-12, method="DOP853")
            self.assertTrue(sol.success)
            np.testing.assert_allclose(mode.evolve_constant(t, x, phi=.02, heat=.004), sol.y.T,
                                       rtol=1e-7, atol=1e-10)

    def test_laplace_elimination_matches_state_resolvent(self):
        for tau in (0., .2):
            mode = material_mode(**dict(inputs(), relaxation=tau, direction=[1., 2., 3.]))
            for s in (.1+.01j, .1+.5j, .1+3j, .1+10j):
                ports = np.column_stack([mode.phi_port, mode.heat_port])
                result = np.linalg.solve(s*np.eye(len(mode.matrix))-mode.matrix, ports)[6]
                np.testing.assert_allclose(result, mode.laplace_transfer(s), rtol=1e-11, atol=1e-13)

    def test_source_superposition(self):
        mode = material_mode(**inputs())
        t = np.linspace(0, 3, 31)
        x = mode.initial_state(.03)
        zero = np.zeros_like(x)
        combined = mode.evolve_constant(t, x, .02, .004)
        separate = (mode.evolve_constant(t, x)+mode.evolve_constant(t, zero, .02, 0.)
                    +mode.evolve_constant(t, zero, 0., .004))
        np.testing.assert_allclose(combined, separate, rtol=1e-12, atol=1e-14)

    def test_static_limits_do_not_commute(self):
        p = inputs()
        static = spatial_response(stiffness=p["stiffness"], expansion=p["expansion"], coupling=p["coupling"],
                                  direction=p["direction"], temperature=p["temperature"], heat_capacity=p["heat_capacity"],
                                  phi_response=.026, response_curvature=.8)["gain_per_phi_response"]
        no_heat = material_mode(**dict(p, conductivity=0., relaxation=0.))
        self.assertAlmostEqual(no_heat.laplace_transfer(1e-6)[0].real, static, places=12)
        conducting = material_mode(**p)
        self.assertEqual(conducting.laplace_transfer(0.)[0], 0.)
        self.assertGreater(abs(static), .01)

    def test_principal_control_metric_and_unforced_stability(self):
        for q in (.1, 1., 10.):
            mode = material_mode(**dict(inputs(), q=q))
            principal = mode.matrix.copy()
            principal[7, 7] = 0.
            np.testing.assert_allclose(mode.metric@principal+principal.T@mode.metric, 0., atol=1e-12)
            self.assertLess(np.max(np.abs(np.linalg.eigvals(principal).real)), 1e-10)
            self.assertLess(np.max(np.linalg.eigvals(mode.matrix).real), 1e-10)

    def test_natural_unit_rescaling(self):
        p = inputs()
        mode = material_mode(**p)
        x = mode.initial_state(.03)
        base = mode.evolve_constant([0., .2, 1.], x, phi=.02, heat=.004)
        for z in (.1, 2., 10.):
            moved = material_mode(**dict(p, stiffness=p["stiffness"]*z**4, expansion=p["expansion"]/z,
                                         coupling=p["coupling"]*z**3, q=p["q"]*z, rho=p["rho"]*z**4,
                                         temperature=p["temperature"]*z, heat_capacity=p["heat_capacity"]*z**3,
                                         conductivity=p["conductivity"]*z**2, relaxation=p["relaxation"]/z))
            state_scale = np.r_[np.ones(3), np.ones(3)*z, z, z**4]
            got = moved.evolve_constant(np.array([0., .2, 1.])/z, moved.initial_state(.03*z**3), .02*z, .004*z**5)
            np.testing.assert_allclose(got/state_scale, base, rtol=1e-10, atol=1e-13)

    def test_full_material_rotation(self):
        p = inputs()
        p.update(stiffness=np.diag([8., 6., 4., 2., 3., 5.]), expansion=np.array([-.03, -.03, .18, .02, -.01, .04]),
                 coupling=np.array([.2, .2, .5, -.1, .04, .08]), direction=np.array([1., 2., 3.]))
        r, _ = np.linalg.qr(np.random.default_rng(113).normal(size=(3, 3)))
        change = np.column_stack([mandel(r@tensor(e)@r.T) for e in np.eye(6)])
        moved = dict(p, stiffness=change@p["stiffness"]@change.T, expansion=change@p["expansion"],
                     coupling=change@p["coupling"], direction=r@p["direction"])
        mode, rotated = material_mode(**p), material_mode(**moved)
        t = np.linspace(0, 3, 21)
        y = mode.evolve_constant(t, mode.initial_state(.03), phi=.02)
        z = rotated.evolve_constant(t, rotated.initial_state(.03), phi=.02)
        np.testing.assert_allclose(y[:, 6:], z[:, 6:], rtol=1e-11, atol=1e-13)
        np.testing.assert_allclose(y[:, :3]@r.T, z[:, :3], rtol=1e-11, atol=1e-13)

    def test_invalid_inputs_not_regularized(self):
        p = inputs()
        for bad in (dict(q=0.), dict(rho=-1.), dict(heat_capacity=0.), dict(conductivity=-1.),
                    dict(relaxation=-1.), dict(conductivity=0.), dict(temperature=np.nan),
                    dict(stiffness=-p["stiffness"]), dict(direction=[0., 0., 0.])):
            with self.assertRaises(ValueError):
                material_mode(**dict(p, **bad))
        mode = material_mode(**dict(p, relaxation=0.))
        with self.assertRaises(ValueError):
            mode.initial_state(.03, flux=.1)
        with self.assertRaises(ValueError):
            mode.evolve_constant([-1.], mode.initial_state(0.))
        with self.assertRaises(np.linalg.LinAlgError):
            material_mode(**inputs()).laplace_transfer(-5.)
        with self.assertRaises(np.linalg.LinAlgError):
            material_mode(**dict(p, conductivity=0., relaxation=0.)).laplace_transfer(0.)


if __name__ == "__main__":
    unittest.main()
