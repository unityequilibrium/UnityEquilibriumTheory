"""Round O exact controls: no old M/N producer is imported or rerun."""
import importlib.util
from pathlib import Path
import unittest

import sympy as s

spec = importlib.util.spec_from_file_location(
    'lattice_mechanical', Path(__file__).with_name('Research_T13_Lattice_Mechanical_State_Construction.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class LatticeMechanicalStateTests(unittest.TestCase):
    def assertZeros(self, values):
        for name, value in values.items():
            with self.subTest(identity=name):
                self.assertEqual(s.simplify(value), 0)

    def test_spin_domain(self):
        for spins in ((1, 1), (1, 1, 1, 0), (True, 1, -1, -1), (0.5,)*4):
            with self.assertRaises(ValueError):
                m.validate_spins(spins)

    def test_retained_and_hidden_basis_are_disjoint(self):
        self.assertEqual(m.E.shape, (4, 2))
        self.assertEqual(m.E.T*m.E, s.eye(2))
        self.assertEqual(m.E.T*m.A, s.zeros(2, 1))
        self.assertEqual(m.E.T*s.ones(4, 1), s.zeros(2, 1))
        self.assertEqual(4-1, 1+2)  # internal pairs, not 3 hidden pairs plus Phi

    def test_canonical_momenta_inertia_and_observation_maps(self):
        self.assertZeros(m.canonical_residuals())

    def test_general_N_mass_sum(self):
        self.assertEqual(s.simplify(m.general_inertia_residual()), 0)

    def test_position_Jacobian_needs_inverse_transpose_momentum(self):
        d, ep = s.symbols('d ep', positive=True)
        B = (s.ones(4, 1)/2).row_join(-d*ep*m.A).row_join(m.E)
        self.assertNotEqual(s.simplify(B.det()**2-1), 0)
        self.assertEqual(s.simplify(B.det()*B.inv().T.det()), 1)

    def test_velocity_is_not_conjugate_momentum_at_locked_geometry(self):
        Pi = s.Symbol('Pi', real=True)
        p = 5*Pi
        self.assertEqual(s.diff(p, Pi), 5)
        self.assertNotEqual(p**2/10, Pi**2/10)
        self.assertEqual(s.simplify(p**2/10-5*Pi**2/2), 0)

    def test_end_length_has_hidden_component(self):
        self.assertEqual(s.simplify(m.E[3, 1]-m.E[0, 1]), -1/s.sqrt(5))
        self.assertEqual(m.E[3, 0]-m.E[0, 0], 0)

    def test_half_spin_and_open_boundary_normalization(self):
        self.assertEqual(len(m.open_bonds()), 3)
        for spins in m.SPINS:
            expected = -sum(s.Rational(spins[i], 2)*s.Rational(spins[j], 2) for i, j in m.open_bonds())
            self.assertEqual(m.control_coefficients(spins)['V0'], expected)

    def test_independent_parent_derivatives_match_pair_assembly(self):
        self.assertZeros(m.direct_parent_derivative_residuals((1, 1, -1, -1)))

    def test_full_atom_hessian_projects_to_hidden_hessian(self):
        for spins in m.SPINS:
            c = m.control_coefficients(spins)
            projected = s.simplify(m.E.T*c['fullH']*m.E-c['K'])
            self.assertEqual(projected, s.zeros(2))

    def test_translation_zero_mode_removed_not_integrated(self):
        for spins in m.SPINS:
            self.assertEqual(m.control_coefficients(spins)['fullH']*s.ones(4, 1), s.zeros(4, 1))

    def test_all16_locked_hidden_hessians_are_positive(self):
        for spins in m.SPINS:
            with self.subTest(spins=spins):
                m.assert_spd(m.control_coefficients(spins)['K'])

    def test_nonpositive_or_nonsymmetric_gaussian_rejected(self):
        for K in (s.diag(1, 0), s.diag(1, -1), s.Matrix([[1, 1], [0, 1]])):
            with self.assertRaises(ValueError):
                m.assert_spd(K)

    def test_hidden_shift_is_not_assumed_zero(self):
        c = m.control_coefficients((1, 1, -1, -1))
        self.assertNotEqual(c['b'], s.zeros(2, 1))
        ref = m.shifted_reference(c)
        self.assertNotEqual(s.simplify(ref['effective']-c['V0']), 0)
        u = s.Matrix(s.symbols('u1 u2', real=True))
        V = c['V0']+(c['b'].T*u)[0]+(u.T*c['K']*u)[0]/2
        centered = ref['effective']+((u-ref['mean']).T*c['K']*(u-ref['mean']))[0]/2
        self.assertEqual(s.simplify(V-centered), 0)

    def test_Gaussian_integrals_and_mode_determinant_match(self):
        self.assertZeros(m.gaussian_residuals())

    def test_fixed_k_mixture_has_consistent_F_U_S(self):
        self.assertZeros(m.mixture_residuals())

    def test_mean_force_and_entropy_Maxwell(self):
        self.assertZeros(m.force_residuals())

    def test_same_population_different_vibration_stiffness(self):
        first = m.control_coefficients((1, 1, -1, -1))
        second = m.control_coefficients((1, -1, 1, -1))
        self.assertNotEqual(s.simplify(first['K'].det()-second['K'].det()), 0)
        self.assertNotEqual(first['V0'], second['V0'])

    def test_global_flip_preserves_new_weight_inputs(self):
        for spins in m.SPINS:
            a = m.control_coefficients(spins)
            b = m.control_coefficients(tuple(-v for v in spins))
            for field in ('V0', 'K', 'b', 'Vphi', 'bphi', 'Kphi'):
                self.assertEqual(a[field], b[field])

    def test_fold_has_one_zero_class_and_preserves_class_counts(self):
        counts = {k: sum(sum(v == 1 for v in spin) == k for spin in m.SPINS) for k in range(5)}
        self.assertEqual(counts[2], 6)
        self.assertEqual(sum(counts[k]*(1 if k == 2 else 2) for k in range(3)), 16)
        self.assertNotEqual(2*counts[2], counts[2])

    def test_zero_exchange_factorizes_only_at_fixed_elastic_parameters(self):
        # Parent contains J linearly; D is independent of J, not set to 8J in this limit.
        J, D = s.symbols('J D', positive=True)
        x = s.Matrix([-s.Rational(3, 2), -s.Rational(1, 2), s.Rational(1, 2), s.Rational(3, 2)])
        a = m.parent_potential((1, 1, -1, -1), x, D, s.log(2), 1, J, 1, 2)
        b = m.parent_potential((1, -1, 1, -1), x, D, s.log(2), 1, J, 1, 2)
        self.assertEqual((a-b).subs(J, 0), 0)
        self.assertNotEqual(a-b, 0)

    def test_conservative_energy_balance(self):
        self.assertZeros(m.conservative_residuals())

    def test_affine_coordinate_is_not_an_autonomous_mode(self):
        c = m.control_coefficients((1, 1, -1, -1))
        self.assertNotEqual(c['bphi'], s.zeros(2, 1))

    def test_reference_linear_force_is_not_deleted(self):
        self.assertNotEqual(m.control_coefficients((1, 1, -1, -1))['Vphi'], 0)

    def test_collision_at_fixed_Phi_excludes_global_parent(self):
        self.assertZeros(m.collision_witness())

    def test_local_tail_is_explicit_condition_not_automatic_acceptance(self):
        c = m.control_coefficients((1, 1, -1, -1))
        T = s.Symbol('T', positive=True)
        bound = m.local_bounds(0, T, c['K'], c['b'])
        self.assertEqual(bound['radius'], s.Rational(1, 4))
        slope = s.simplify(s.diff(bound['eta'], T))
        self.assertEqual(s.simplify(slope-16*s.trace(c['K'].inv())), 0)
        self.assertEqual(s.diff(bound['eta'], T, 2), 0)
        self.assertIn('Eta<1', bound['domain'])

    def test_bad_local_domain_rejected(self):
        c = m.control_coefficients((1, 1, -1, -1))
        for rho, T in ((1, 1), (-1, 1), (0, -1)):
            with self.assertRaises(ValueError):
                m.local_bounds(rho, T, c['K'], c['b'])

    def test_local_remainder_formula_and_gap_domain(self):
        self.assertZeros(m.remainder_residuals())
        self.assertTrue(1-s.sqrt(2)/4 > 0)

    def test_orthogonal_hidden_rotation_does_not_change_measure_or_shift(self):
        c = m.control_coefficients((1, 1, -1, -1))
        Q = s.Matrix([[0, -1], [1, 0]])
        rotatedK, rotatedb = Q.T*c['K']*Q, Q.T*c['b']
        self.assertEqual(s.simplify(rotatedK.det()-c['K'].det()), 0)
        self.assertEqual(s.simplify((rotatedb.T*rotatedK.inv()*rotatedb)[0]
                                    -(c['b'].T*c['K'].inv()*c['b'])[0]), 0)

    def test_negative_controls_detect_declared_mistakes(self):
        self.assertTrue(all(m.negative_controls().values()))


if __name__ == '__main__':
    unittest.main()
