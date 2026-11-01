from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('action_discrimination',Path(__file__).with_name('Research_T13_Action_Discrimination.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def add(*polys):
    return [sum((p[i] if i<len(p) else Q(0)) for p in polys) for i in range(4)]


def scale(p,a):
    return [a*x for x in p]


def mul(p,q):
    return [sum(p[j]*q[i-j] for j in range(i+1)) for i in range(4)]


class ActionDiscriminationTests(unittest.TestCase):
    def test_coefficient_dictionary_retains_curvature_and_cosmological_terms(self):
        before,after=m.exact_action_coefficients(m.exact_fixture(),Q(2),Q(3),Q(3,2),Q(2))
        self.assertEqual(before,after)
        self.assertNotEqual(after['R_psi2'],0)
        self.assertEqual(len(before),10)

    def test_onto_map_is_not_a_locked_coefficient_relation(self):
        target=dict(M2=Q(7),m2=Q(-3),ls=Q(5),lm=Q(2),g=Q(11),X=Q(-1,50),r0=Q(13))
        parent=(Q(1),Q(1),Q(1),target['M2'],target['m2'],target['ls'],target['lm'],target['g'],target['X'],target['r0'])
        self.assertEqual(m.canonical_coefficients(*parent,Q(1),Q(1)),target)

    def test_singular_epsilon_chart_is_refused(self):
        for e in (Q(0),Q(-1)):
            p=list(m.exact_fixture()); p[0]=e
            with self.assertRaises(ValueError):
                m.canonical_coefficients(*p,Q(2),Q(3))

    def test_wrong_roots_are_not_silent_normalization(self):
        with self.assertRaises(ValueError):
            m.canonical_coefficients(*m.exact_fixture(),Q(3),Q(3))

    def test_parent_sign_domain_is_preserved(self):
        for index in (3,5,6,7):
            p=list(m.exact_fixture()); p[index]=Q(-1)
            with self.assertRaises(ValueError):
                m.canonical_coefficients(*p,Q(2),Q(3))

    def test_current_action_evaluator_matches_transformation(self):
        self.assertLessEqual(m.production_action_control()['relative_scaled_residual'],1e-12)

    def test_current_normalized_lanes_match_constructed_rhs(self):
        r=m.phase_field_operator_controls()
        self.assertEqual(set(r),{'conserved','nonconserved'})
        self.assertLessEqual(max(r.values()),1e-12)

    def test_memory_feedback_and_covariance_match_declared_comparator(self):
        r=m.open_system_operator_controls()
        self.assertEqual(set(r),{'retarded_memory_rate','state_update','classical_covariance','local_inverse_oscillator_kernel'})
        self.assertLessEqual(max(r.values()),1e-12)

    def test_existing_action_admits_zero_response_even_at_nonzero_epsilon(self):
        import numpy as np
        from docs.core.uet_covariant_response import CovariantResponseConfig,response_stress_tensor
        from docs.core.uet_covariant_matter import CovariantMatterConfig,coupled_response_scalar_equation_residual,interaction_energy_density
        rc=CovariantResponseConfig(epsilon_nc=2,curvature_coupling=0,equilibrium_density=0)
        mc=CovariantMatterConfig(response_coupling=0)
        fields=np.array([.2,-.7]); metric=np.diag([-1.,1.,1.,1.])
        self.assertEqual(coupled_response_scalar_equation_residual(3,0,0,fields,rc,mc),0)
        self.assertEqual(interaction_energy_density(0,fields,rc,mc),0)
        np.testing.assert_array_equal(response_stress_tensor(metric,metric,np.zeros(4),0,rc),np.zeros((4,4)))

    def test_static_source_and_softening_sign(self):
        r=m.static_state_at_response(Q(5),Q(3),Q(2),Q(4),Q(1,2))
        self.assertEqual(r['s'],Q(23,8))
        self.assertGreater(r['dpsi_ds'],0)
        self.assertLess(r['effective_second'],Q(4,2))
        self.assertGreater(r['effective_third'],0)

    def test_implicit_series_and_schur_derivatives_are_exact(self):
        mass,quartic,g,lm,psi=Q(5),Q(3),Q(2),Q(4),Q(1,2)
        r=m.static_state_at_response(mass,quartic,g,lm,psi); d=r['D']
        a=g/(2*d); b=-3*quartic*psi*a*a/d; c=-(6*quartic*psi*a*b+quartic*a**3)/d
        p=[psi,a,b,c]; s=[r['s'],Q(1),Q(0),Q(0)]
        p2=mul(p,p); p3=mul(p2,p); p4=mul(p2,p2)
        residual=add(scale(p,mass),scale(p3,quartic),scale(s,-g/2))
        self.assertEqual(residual,[0]*4)
        v=add(scale(p2,mass/2),scale(p4,quartic/4),scale(mul(s,s),lm/4),scale(mul(p,s),-g/2))
        self.assertEqual(2*v[2],r['effective_second'])
        self.assertEqual(6*v[3],r['effective_third'])

    def test_massless_origin_is_not_regularized(self):
        with self.assertRaises(ValueError):
            m.static_state_at_response(Q(0),Q(3),Q(2),Q(4),Q(0))
        r=m.static_state_at_response(Q(0),Q(3),Q(2),Q(4),Q(1))
        self.assertEqual(r['s'],Q(3))

    def test_source_control_inverse_and_reserved_prediction(self):
        a,b=m.identify_cubic_source(Q(1),Q(5),Q(2),Q(28))
        self.assertEqual((a,b),(2,3))
        lo,hi=m.cubic_root_bracket(a,b,Q(105,8),Q(2))
        self.assertLessEqual(lo,Q(3,2)); self.assertGreaterEqual(hi,Q(3,2))
        self.assertLessEqual(hi-lo,Q(1,2**39))

    def test_cubic_calibration_requires_informative_controls(self):
        for z1,z2 in ((Q(0),Q(1)),(Q(1),Q(1)),(Q(-1),Q(2))):
            with self.assertRaises(ValueError):
                m.identify_cubic_source(z1,Q(5),z2,Q(28))

    def test_wrong_sign_constitutive_control_is_detected(self):
        with self.assertRaises(ValueError):
            m.identify_cubic_source(Q(1),Q(5),Q(2),Q(6))

    def test_joint_enclosure_and_disjoint_synthetic_output(self):
        lo,hi=m.rectangular_prediction_enclosure((Q(199,100),Q(201,100)),(Q(149,50),Q(151,50)),
                                               (Q(105,8)-Q(1,1000),Q(105,8)+Q(1,1000)),Q(2))
        self.assertLess(lo,Q(3,2)); self.assertGreater(hi,Q(3,2))
        self.assertLess(hi,Q(2))  # Synthetic measured interval [2,21/10] would be disjoint.

    def test_enclosure_rejects_unbounded_or_unphysical_inputs(self):
        with self.assertRaises(ValueError):
            m.rectangular_prediction_enclosure((Q(-1),Q(2)),(Q(1),Q(3)),(Q(1),Q(2)),Q(2))
        with self.assertRaises(ValueError):
            m.cubic_root_bracket(Q(1),Q(1),Q(100),Q(1))
        for steps in (0,65):
            with self.assertRaises(ValueError):
                m.cubic_root_bracket(Q(1),Q(1),Q(1),Q(2),steps)

    def test_no_physical_or_unique_theory_promotion(self):
        r=m.calculate()
        self.assertFalse(r['physical_acceptance'])
        self.assertFalse(r['unique_UET_discriminator_against_constructed_scalar_comparator'])
        self.assertEqual(r['experimental_rows_scored'],0)
        self.assertEqual(r['new_core_terms'],0)
        self.assertEqual(len(r['alternatives_reviewed']),7)


if __name__=='__main__':
    unittest.main()
