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

    def test_full_bilayer_intensity_and_cubic_are_known_analytically(self):
        import math
        phi=2*math.pi/3
        for t in (-.1,0.,.1):
            r=m.finite_layer_observer(2,t,phi)
            self.assertAlmostEqual(r['intensity'],(1+math.cos(phi-t))/(1+math.cos(phi)))
            k1,k2,k3=r['derivatives_at_zero']
            self.assertAlmostEqual(k1,math.tan(phi/2));self.assertAlmostEqual(k3,-k1)

    def test_global_and_cubic_bounds_at_predeclared_controls(self):
        for n in (2,3,4,9):
            for t in (0.,-.001,.001,-.01,.01,-.1,.1):
                r=m.finite_layer_observer(n,t)
                self.assertLessEqual(r['linear_error'],r['linear_bound_coefficient']*t*t+1e-12)
                self.assertLessEqual(r['cubic_error'],r['cubic_bound_coefficient']*t**4+1e-12)
                self.assertFalse(r['physical_displacement_or_error_budget_assigned'])

    def test_bound_coefficient_matches_independent_variance_identity(self):
        import numpy as np
        p=m.finite_layer_projection(9);b=np.array(p['profile'])/p['centroid_projection']
        expected=(9*float(b@b)-float(b.sum())**2)/21
        self.assertAlmostEqual(m.finite_layer_observer(9,.1)['linear_bound_coefficient'],expected)

    def test_nine_layer_linear_slope_recovers_preceding_projection(self):
        import math
        r=m.finite_layer_observer(9,0.)
        self.assertAlmostEqual(r['derivatives_at_zero'][0]/math.sqrt(3),20/21)

    def test_sinusoidal_material_input_generates_cubic_detector_harmonic(self):
        import numpy as np
        k1,k2,k3=m.finite_layer_observer(9,0.)['derivatives_at_zero']
        angles=2*np.pi*np.arange(16)/16;amplitude=.01;t=amplitude*np.cos(angles)
        polynomial=1+k1*t+k2*t*t/2+k3*t*t*t/6
        cosine3=float(2*np.mean(polynomial*np.cos(3*angles)))
        self.assertNotEqual(k3,0)
        self.assertAlmostEqual(cosine3,k3*amplitude**3/24,places=14)

    def test_extinct_baselines_and_nonfinite_inputs_refused(self):
        import math
        for t,phi in ((0.,math.pi),(float('nan'),0.),(0.,float('inf'))):
            with self.assertRaises(ValueError):m.finite_layer_observer(2,t,phi)

    def test_common_clock_phase_cancels_but_constant_gain_does_not(self):
        import cmath
        y1,y3=1+.4j,.02-.01j;angle=.7;gain=2.
        raw=y3/y1**3
        shifted=(y3*cmath.exp(-3j*angle))/(y1*cmath.exp(-1j*angle))**3
        self.assertAlmostEqual(abs(shifted-raw),0)
        self.assertAlmostEqual(abs((gain*y3)/(gain*y1)**3-raw/gain**2),0)

    def test_common_gaussian_temporal_blur_does_not_cancel(self):
        import math
        u=.6  # dimensionless omega*sigma, mathematical input not experiment calibration
        h1=math.exp(-u*u/2);h3=math.exp(-9*u*u/2)
        self.assertAlmostEqual(h3/h1**3,math.exp(-3*u*u))
        self.assertNotEqual(h3/h1**3,1)

    def test_two_orders_separate_material_and_observer_third_exactly(self):
        k1,k3=Q(2),Q(-3);b,c=Q(1,1000),Q(2,1000000)
        first=k1*b+k3*c;second=-2*k1*b-8*k3*c
        self.assertEqual(m.two_order_third(first,second,k1,k3),(b,c))
        self.assertEqual(m.two_order_third(k3*c,-8*k3*c,k1,k3),(0,c))

    def test_two_order_joint_error_bound_and_singular_refusal(self):
        k1,k3=Q(2),Q(-3);e1,e2=Q(1,100),Q(1,200)
        errors=[abs(m.two_order_third(a*e1,b*e2,k1,k3)[0]) for a,b in product((-1,1),repeat=2)]
        self.assertEqual(max(errors),(8*e1+e2)/(6*abs(k1)))
        with self.assertRaises(ValueError):m.two_order_third(Q(1),Q(1),Q(0),k3)

    def test_two_order_conjugate_derivatives_and_mixed_cubic_harmonic(self):
        import math
        import numpy as np
        first=m.finite_layer_observer(9,0.,2*math.pi/3)['derivatives_at_zero']
        second=m.finite_layer_observer(9,0.,-2*math.pi/3)['derivatives_at_zero']
        self.assertAlmostEqual(first[0],-second[0]);self.assertAlmostEqual(first[2],-second[2])
        angle=2*np.pi*np.arange(32)/32;a,b=.1,.02
        q=a*np.cos(angle)+b*np.cos(3*angle)
        c=float(2*np.mean(q**3*np.cos(3*angle)))/6
        self.assertAlmostEqual(c,a**3/24+a*a*b/4+b**3/8)


if __name__=='__main__':unittest.main()
