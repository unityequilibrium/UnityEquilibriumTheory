from fractions import Fraction as Q
import importlib.util
from itertools import product
from pathlib import Path
import unittest

s=importlib.util.spec_from_file_location('preparation',Path(__file__).with_name('Research_T13_Graphite_Preparation.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)


class PreparationTests(unittest.TestCase):
    def test_left_inverse_and_rank(self):
        self.assertEqual(m.reconstruct(m.observe(Q(1),Q(0))),(1,0))
        self.assertEqual(m.reconstruct(m.observe(Q(0),Q(1))),(0,1))
        self.assertEqual(sum(m.observe(Q(5,7),Q(-2,9))),0)

    def test_common_mode_is_closure_error_not_a_reconstructed_displacement(self):
        y=m.observe(Q(2),Q(3)); c=Q(4,5)
        shifted=tuple(t+c for t in y)
        self.assertEqual(m.reconstruct(shifted),(2,3))
        self.assertEqual(sum(shifted),3*c)

    def test_joint_box_bounds_without_independence(self):
        values=[m.reconstruct(e) for e in product((Q(-1),Q(1)),repeat=3)]
        self.assertEqual(max(abs(v[0]) for v in values),1)
        self.assertEqual(max(abs(v[1]) for v in values),Q(2,3))

    def test_full_state_jet_inverse(self):
        q,v,d,w=Q(2,3),Q(-1,4),Q(3,5),Q(-2,7)
        args=Q(5,4),Q(1),Q(3,4),Q(3,10)
        a,j=m.matter_jet(q,v,d,w,*args)
        self.assertEqual(m.hidden_state(q,v,a,j,*args),(d,w))

    def test_q_and_velocity_alone_do_not_determine_acceleration(self):
        args=Q(1),Q(2),Q(3),Q(1,2)
        a=m.matter_jet(Q(1),Q(0),Q(0),Q(0),*args)
        b=m.matter_jet(Q(1),Q(0),Q(2),Q(0),*args)
        self.assertEqual(b[0]-a[0],1)

    def test_matching_acceleration_still_leaves_response_velocity(self):
        args=Q(1),Q(2),Q(3),Q(1,2)
        a=m.matter_jet(Q(1),Q(0),Q(0),Q(0),*args)
        b=m.matter_jet(Q(1),Q(0),Q(0),Q(2),*args)
        self.assertEqual(a[0],b[0]);self.assertEqual(b[1]-a[1],1)

    def test_singular_and_invalid_state_estimators_refused(self):
        for q,g,z,quartic in ((0,1,1,1),(1,0,1,1),(1,1,0,1),(1,1,1,0)):
            with self.assertRaises(ValueError):m.hidden_state(Q(q),Q(0),Q(0),Q(0),Q(z),Q(1),Q(quartic),Q(g))

    def test_no_physical_result_or_kernel_substitution(self):
        r=m.calculate()
        for k in ('old_four_frequency_kernel_evaluated','physical_forecast_run','physical_acceptance','new_core_term','numeric_records_acquired'):
            self.assertFalse(r[k])

    def test_two_layer_reduced_mass_reference(self):
        r=m.finite_layer_projection(2)
        self.assertAlmostEqual(r['rigid_overlap_fraction'],1)
        self.assertAlmostEqual(r['pole_mass_per_layer_mass'],.5)

    def test_nine_layer_mass_is_coordinate_projected_not_total_mass(self):
        r=m.finite_layer_projection(9)
        self.assertGreater(r['pole_mass_per_layer_mass'],r['rigid_mass_per_layer_mass'])
        self.assertLess(r['rigid_overlap_fraction'],1)
        self.assertAlmostEqual(r['pole_mass_per_layer_mass']*r['rigid_overlap_fraction'],20/9)
        self.assertFalse(r['observer_admitted']);self.assertFalse(r['uet_field_map_admitted'])

    def test_independent_spectrum_and_mode_mass_work_identity(self):
        import numpy as np
        for n in (3,4,9):
            r=m.finite_layer_projection(n);e=np.array(r['profile'])
            d=np.eye(n-1,n,k=1)-np.eye(n-1,n)
            values,vectors=np.linalg.eigh(d.T@d)
            self.assertAlmostEqual(values[-1],4*r['frequency_over_bulk']**2)
            self.assertAlmostEqual(abs(float(vectors[:,-1]@e))/float(np.linalg.norm(e)),1)
            force=np.arange(1,n+1,dtype=float);dq=.3
            displacement=e*dq/r['centroid_projection']
            self.assertAlmostEqual(float(force@displacement),float(e@force)*dq/r['centroid_projection'])
            self.assertAlmostEqual(float(e@np.ones(n)),0)

    def test_invalid_layer_counts_refused(self):
        for n in (0,1,2.5,True):
            with self.assertRaises(ValueError):m.finite_layer_projection(n)

    def test_conditional_finite_layer_readout_ratio(self):
        self.assertEqual(m.finite_layer_projection(9)['conditional_equal_layer_basal_observer_ratio'],'20/21')
        self.assertEqual(m.finite_layer_projection(4)['conditional_equal_layer_basal_observer_ratio'],'1')
        import cmath
        import math
        phi=2*math.pi/3;na,nb=5,4
        s=na+nb*cmath.exp(-1j*phi)
        derivative=-1j*na*nb/(na+nb)*(1-cmath.exp(-1j*phi))
        slope=2*(s.conjugate()*derivative).real/abs(s)**2
        self.assertAlmostEqual(slope/math.tan(phi/2),20/21)


if __name__=='__main__':unittest.main()
