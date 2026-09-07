"""Independent local energy, entropy, resolvent and covariance checks."""

import unittest

import numpy as np
from scipy.integrate import solve_ivp

from docs.core.uet_dynamic_thermoelastic_response import material_mode
from docs.core.uet_matter_strain_susceptibility import isentropic_matched_response
from docs.core.uet_reciprocal_thermal_dynamics import reciprocal_mode
from docs.core.uet_thermoelastic_spatial_compatibility import isotropic_stiffness, mandel, tensor, strain_map


def material_inputs():
    return dict(stiffness=isotropic_stiffness(5., 3.), expansion=np.array([.04, .04, .04, 0., 0., 0.]),
                coupling=np.array([.7, .5, .4, .04, -.02, .03]), direction=[1., 2., 3.],
                q=1., rho=1., temperature=.8, heat_capacity=2.4, conductivity=.3, relaxation=.2)


def response_inputs():
    return dict(entropy_phi=.17, response_kinetic=1.2, response_curvature=.8,
                response_gradient=.3, response_damping=.08)


class ReciprocalThermalTests(unittest.TestCase):
    def test_forces_and_entropy_from_independent_free_energy_derivatives(self):
        mode = reciprocal_mode(material_mode(**material_inputs()), **response_inputs())
        m = mode.material
        y = np.array([.02, -.01, .03, .015, -.025])
        def potential(z):
            v, theta, phi = z[:3], z[3], z[4]
            return (v@m.acoustic@v/2-theta*m.thermal_stress@v-m.heat_capacity*theta**2/(2*m.temperature)
                    +phi*m.coupling@v+mode.response_curvature_q*phi**2/2-mode.entropy_phi*phi*theta)
        step = 1e-5
        gradient = np.array([(potential(y+step*e)-potential(y-step*e))/(2*step) for e in np.eye(5)])
        state = np.zeros(len(mode.matrix))
        state[:3], state[6], state[mode.phi_index] = y[:3], y[3], y[4]
        rate = mode.matrix@state
        np.testing.assert_allclose(-gradient[:3], m.rho/m.q**2*rate[3:6], atol=1e-12)
        self.assertAlmostEqual(-gradient[3], mode.entropy(state), places=12)
        self.assertAlmostEqual(-gradient[4], mode.response_kinetic*rate[mode.pi_index], places=12)

    def test_old_complete_isentropic_map_is_stationary_coupled_limit(self):
        p = dict(material_inputs(), conductivity=0., relaxation=0.)
        r = response_inputs()
        mode = reciprocal_mode(material_mode(**p), **r)
        static = isentropic_matched_response(stiffness=p['stiffness'],
            thermal_stress=p['stiffness']@p['expansion'], coupling=p['coupling'],
            entropy_phi_coefficient=r['entropy_phi'], temperature=p['temperature'],
            heat_capacity=p['heat_capacity'], direction=p['direction'], delta_phi=.026)
        v = np.linalg.lstsq(strain_map(p['direction']),
                            static['strain'], rcond=None)[0]
        x = mode.initial_state(0., phi=.026, strain=v)
        self.assertAlmostEqual(x[6], static['delta_temperature'], places=13)
        force = mode.response_curvature_q*.026+mode.material.coupling@v-mode.entropy_phi*x[6]
        np.testing.assert_allclose(mode.matrix@x+mode.force_port*force, 0., atol=1e-13)

    def test_symmetric_availability_identity_and_arbitrary_state_balance(self):
        rng = np.random.default_rng(130909)
        for tau in (0., .2, 2.):
            mode = reciprocal_mode(material_mode(**dict(material_inputs(), relaxation=tau)), **response_inputs())
            np.testing.assert_allclose(mode.metric@mode.matrix+mode.matrix.T@mode.metric,
                                       -2*mode.dissipation_metric, atol=2e-14)
            self.assertGreater(np.min(np.linalg.eigvalsh(mode.metric)), 0.)
            for _ in range(12):
                record = mode.balance(rng.normal(size=len(mode.matrix)), heat=.03, force=-.02)
                self.assertLess(abs(record['balance_residual']), 1e-12)
                self.assertLess(abs(record['linear_entropy_residual']), 1e-13)
                self.assertGreaterEqual(record['entropy_production_budget'], 0.)

    def test_one_sided_entropy_coupling_fails_energy_identity(self):
        mode = reciprocal_mode(material_mode(**material_inputs()), **response_inputs())
        for row, col in ((6, mode.pi_index), (mode.pi_index, 6)):
            wrong = mode.matrix.copy()
            wrong[row, col] = 0.
            defect = mode.metric@wrong+wrong.T@mode.metric+2*mode.dissipation_metric
            self.assertGreater(np.linalg.norm(defect), .1)

    def test_initial_entropy_and_thermal_feedback_are_not_phi_identity(self):
        mode = reciprocal_mode(material_mode(**material_inputs()), **response_inputs())
        x = mode.initial_state(.03, phi=.02, pi=-.01, strain=[.001, .003, -.002])
        self.assertAlmostEqual(mode.entropy(x), .03, places=14)
        hot = mode.initial_state(.03)
        self.assertGreater((mode.matrix@hot)[mode.pi_index], 0.)
        self.assertEqual(hot[mode.phi_index], 0.)

    def test_resolvent_matches_independent_elimination(self):
        for tau in (0., .2):
            mode = reciprocal_mode(material_mode(**dict(material_inputs(), relaxation=tau)), **response_inputs())
            ports = np.column_stack([mode.heat_port, mode.force_port])
            for s in (.1+.02j, .2+.8j, .3+3j, .4+10j):
                got = np.linalg.solve(s*np.eye(len(mode.matrix))-mode.matrix, ports)[[6, mode.phi_index]]
                np.testing.assert_allclose(got, mode.laplace_transfer(s), rtol=1e-11, atol=1e-13)

    def test_direct_equations_match_matrix_exponential(self):
        for tau in (0., .2):
            mode = reciprocal_mode(material_mode(**dict(material_inputs(), relaxation=tau)), **response_inputs())
            m = mode.material
            x = mode.initial_state(.03, phi=.02, pi=.004, strain_rate=[.002, .001, -.001])
            times = np.linspace(0, 8, 65)
            def rhs(_, y):
                theta, phi, pi = y[6], y[mode.phi_index], y[mode.pi_index]
                flux = y[7] if tau else m.conductivity*m.q*theta
                out = np.zeros_like(y)
                out[:3] = y[3:6]
                out[3:6] = -m.q**2/m.rho*(m.acoustic@y[:3]-m.thermal_stress*theta+m.coupling*phi)
                out[6] = (-m.temperature*m.thermal_stress@y[3:6]-m.temperature*mode.entropy_phi*pi-m.q*flux+.004)/m.heat_capacity
                if tau:
                    out[7] = (m.conductivity*m.q*theta-flux)/tau
                out[mode.phi_index] = pi
                out[mode.pi_index] = (-mode.response_curvature_q*phi-m.coupling@y[:3]+mode.entropy_phi*theta-mode.response_damping*pi+.002)/mode.response_kinetic
                return out
            sol = solve_ivp(rhs, [0, 8], x, method='DOP853', t_eval=times, rtol=1e-10, atol=1e-12)
            self.assertTrue(sol.success)
            np.testing.assert_allclose(mode.evolve_constant(times, x, heat=.004, force=.002), sol.y.T,
                                       rtol=2e-7, atol=2e-10)

    def test_conservative_limit_and_damped_availability(self):
        for k, gamma in ((0., 0.), (.3, .08)):
            mode = reciprocal_mode(material_mode(**dict(material_inputs(), conductivity=k, relaxation=0.)),
                                   **dict(response_inputs(), response_damping=gamma))
            x = mode.initial_state(.03, phi=.02, pi=.01)
            states = mode.evolve_constant(np.linspace(0, 20, 161), x)
            energy = np.einsum('ti,ij,tj->t', states, mode.metric, states)/2
            if k == 0:
                np.testing.assert_allclose(energy, energy[0], rtol=1e-11, atol=1e-14)
            else:
                self.assertLessEqual(np.max(np.diff(energy)), 1e-13)
                self.assertLess(energy[-1], energy[0])
            self.assertLess(np.max(np.linalg.eigvals(mode.matrix).real), 1e-10)

    def test_zero_coupling_preserves_old_comparator(self):
        m = material_mode(**dict(material_inputs(), coupling=np.zeros(6)))
        before = m.matrix.copy()
        mode = reciprocal_mode(m, **dict(response_inputs(), entropy_phi=0.))
        t = np.linspace(0, 3, 25)
        got = mode.evolve_constant(t, mode.initial_state(.03, phi=.02), heat=.004)
        want = m.evolve_constant(t, m.initial_state(.03), heat=.004)
        np.testing.assert_allclose(got[:, :len(m.matrix)], want, atol=1e-13)
        np.testing.assert_array_equal(m.matrix, before)

    def test_phi_normalization_covariance(self):
        p, r = material_inputs(), response_inputs()
        mode = reciprocal_mode(material_mode(**p), **r)
        x = mode.initial_state(.03, phi=.02, pi=.004)
        t = np.array([0., .2, 1.])
        baseline = mode.evolve_constant(t, x, heat=.004, force=.002)
        for z in (-3., .2, 4.):
            scaled = dict(r, entropy_phi=r['entropy_phi']/z)
            for key in ('response_kinetic', 'response_curvature', 'response_gradient', 'response_damping'):
                scaled[key] /= z*z
            moved = reciprocal_mode(material_mode(**dict(p, coupling=p['coupling']/z)), **scaled)
            scale = np.r_[np.ones(len(mode.material.matrix)), z, z]
            got = moved.evolve_constant(t, x*scale, heat=.004, force=.002/z)
            np.testing.assert_allclose(got/scale, baseline, rtol=1e-11, atol=1e-13)
            self.assertAlmostEqual(moved.balance(x*scale)['availability'], mode.balance(x)['availability'])

    def test_natural_unit_covariance(self):
        p, r = material_inputs(), response_inputs()
        mode = reciprocal_mode(material_mode(**p), **r)
        t = np.array([0., .2, 1.])
        x = mode.initial_state(.03, phi=.02, pi=.004)
        baseline = mode.evolve_constant(t, x, heat=.004, force=.002)
        for z in (.1, 2., 10.):
            moved = reciprocal_mode(material_mode(**dict(p, stiffness=p['stiffness']*z**4,
                expansion=p['expansion']/z, coupling=p['coupling']*z**3, q=p['q']*z,
                rho=p['rho']*z**4, temperature=p['temperature']*z, heat_capacity=p['heat_capacity']*z**3,
                conductivity=p['conductivity']*z**2, relaxation=p['relaxation']/z)),
                **dict(r, entropy_phi=r['entropy_phi']*z**2, response_curvature=r['response_curvature']*z**2,
                       response_damping=r['response_damping']*z))
            scale = np.r_[np.ones(3), np.ones(3)*z, z, z**4, z, z**2]
            got = moved.evolve_constant(t/z, x*scale, heat=.004*z**5, force=.002*z**3)
            np.testing.assert_allclose(got/scale, baseline, rtol=1e-10, atol=1e-13)
            self.assertAlmostEqual(moved.balance(x*scale)['availability']/z**4, mode.balance(x)['availability'])

    def test_full_rotation(self):
        p = material_inputs()
        p['stiffness'] = np.diag([8., 6., 4., 2., 3., 5.])
        rot, _ = np.linalg.qr(np.random.default_rng(908).normal(size=(3, 3)))
        change = np.column_stack([mandel(rot@tensor(e)@rot.T) for e in np.eye(6)])
        m = reciprocal_mode(material_mode(**p), **response_inputs())
        moved = reciprocal_mode(material_mode(**dict(p, stiffness=change@p['stiffness']@change.T,
            expansion=change@p['expansion'], coupling=change@p['coupling'], direction=rot@p['direction'])), **response_inputs())
        t = np.linspace(0, 3, 16)
        y = m.evolve_constant(t, m.initial_state(.03, phi=.02))
        z = moved.evolve_constant(t, moved.initial_state(.03, phi=.02))
        np.testing.assert_allclose(y[:, :3]@rot.T, z[:, :3], atol=1e-13)
        np.testing.assert_allclose(y[:, 6:], z[:, 6:], atol=1e-13)

    def test_dc_temperature_not_constant_phi_gain(self):
        mode = reciprocal_mode(material_mode(**material_inputs()), **response_inputs())
        transfer = mode.laplace_transfer(0.)
        self.assertAlmostEqual(transfer[0, 1], 0.)
        self.assertAlmostEqual(transfer[1, 1], 1/mode.schur_margin)

    def test_rejection_of_unstable_singular_and_invalid_inputs(self):
        m = material_mode(**material_inputs())
        for change in (dict(response_kinetic=0.), dict(entropy_phi=np.nan), dict(response_damping=-.1),
                       dict(response_gradient=-1.), dict(response_curvature=-1.)):
            with self.assertRaises(ValueError):
                reciprocal_mode(m, **dict(response_inputs(), **change))
        mode = reciprocal_mode(m, **response_inputs())
        with self.assertRaises(np.linalg.LinAlgError):
            mode.laplace_transfer(-5.)
        with self.assertRaises(ValueError):
            mode.initial_state(.03, phi=np.inf)
        with self.assertRaises(ValueError):
            mode.evolve_constant([-1.], mode.initial_state(0.))


if __name__ == '__main__':
    unittest.main()
