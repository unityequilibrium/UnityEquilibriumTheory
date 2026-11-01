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

    def test_source_basis_reproduces_published_linear_rows(self):
        import math
        expected={(1,0):(2*math.pi*math.sqrt(3),2*math.pi),
                  (0,1):(0.,-4*math.pi),(-1,1):(-2*math.pi*math.sqrt(3),2*math.pi)}
        for (h,k),row in expected.items():
            actual=m.source_geometry(h,k,2)['linear_row_wrt_article_P']
            for a,b in zip(actual,row):self.assertAlmostEqual(a,b)

    def test_source_first_second_order_conjugacy_and_finite_layer_factor(self):
        first=m.source_geometry(1,0);second=m.source_geometry(2,0)
        self.assertAlmostEqual(first['layer_phase'],-second['layer_phase'])
        self.assertAlmostEqual(first['layer_factor_ratio_abs'],1)
        bulk=m.source_geometry(1,0,2)['linear_row_wrt_article_P']
        for a,b in zip(first['linear_row_wrt_article_P'],bulk):self.assertAlmostEqual(a/b,20/21)

    def test_reference_zero_linear_is_not_zero_quadratic(self):
        import numpy as np
        ref=m.source_geometry(1,1)
        self.assertLess(max(abs(x) for x in ref['linear_row_wrt_article_P']),1e-12)
        self.assertLess(ref['coherent_reference_second_derivative'],0)
        p=m.finite_layer_projection(9);b=np.array(p['profile'])/p['centroid_projection']
        self.assertAlmostEqual(ref['coherent_reference_second_derivative'],-2*float(b@b)/9)

    def test_polynomial_division_derivatives_multiply_back_exactly(self):
        a1,a2,a3,b2=Q(2),Q(3),Q(-4),Q(-1,5)
        c1,c2,c3=m.divided_cubic(a1,a2,a3,b2)
        self.assertEqual(c1,a1);self.assertEqual(c2+b2,a2)
        self.assertEqual(c3+3*c1*b2,a3)

    def test_shared_reference_defeats_uncorrected_two_order_discriminant(self):
        k1,k3,b2,c=Q(2),Q(-3),Q(1,10),Q(1,100000)
        first=(k3-3*k1*b2)*c;second=(-8*k3+6*k1*b2)*c
        inferred,_=m.two_order_third(first,second,k1,k3)
        self.assertEqual(inferred,-3*b2*c)
        self.assertNotEqual(inferred,0)  # True coordinate third is zero in this counterexample.

    def test_divisor_error_envelope_and_refusal(self):
        mag,rho=Q(2),Q(1,10)
        self.assertEqual(m.division_omission_bound(mag,rho),mag/(1-rho)-mag)
        for rho in (Q(-1),Q(1),Q(2)):
            with self.assertRaises(ValueError):m.division_omission_bound(mag,rho)

    def test_more_processed_third_orders_cannot_remove_common_divisor_null(self):
        b,c,e=Q(0),Q(1,100000),Q(-1,1000000);delta=Q(1,10000000)
        for order,k1,k3 in ((1,Q(2),Q(-3)),(2,Q(-2),Q(3)),(4,Q(2),Q(-3)),(5,Q(-2),Q(3))):
            before=k1*order*(b-3*e)+k3*order**3*c
            after=k1*order*((b+3*delta)-3*(e+delta))+k3*order**3*c
            self.assertEqual(before,after)
        self.assertLess(e/c,0);self.assertLess((e+delta)/c,0)

    def test_common_applied_divisor_cancels_exactly_for_full_traces(self):
        values=(Q(11,10),Q(9,10),Q(1))
        expected=m.shared_divisor_ratios(values)
        for d in (Q(1,2),Q(1),Q(2)):
            self.assertEqual(m.shared_divisor_ratios(tuple(v/d for v in values)),expected)

    def test_linear_surrogate_recovers_state_and_arbitrary_common_divisor(self):
        x,z,scale=Q(1,1000),Q(-1,2000),Q(2)
        for d in (Q(1,2),Q(1),Q(2)):
            observed=tuple((1+scale*v)/d for v in m.observe(x,z))
            self.assertEqual(m.linear_common_reconstruct(observed,scale),(x,z,d))

    def test_full_nine_layer_ratio_geometry_has_rank_two(self):
        import math
        r=m.full_ratio_observer(9,.0001,-.0002)
        self.assertAlmostEqual(r['baseline_ratio_jacobian_determinant'],24*math.pi**2*math.sqrt(3)*(20/21)**2)
        self.assertGreater(r['baseline_ratio_jacobian_determinant'],0)
        h=1e-6
        plus=m.full_ratio_observer(9,h,0)['ratios'];minus=m.full_ratio_observer(9,-h,0)['ratios']
        expected=2*math.pi*(20/21)*math.sqrt(3)
        self.assertAlmostEqual((plus[0]-minus[0])/(2*h),expected,places=6)

    def test_different_divisors_do_not_cancel(self):
        values=(Q(11,10),Q(9,10),Q(1))
        changed=(values[0]/2,values[1],values[2])
        self.assertNotEqual(m.shared_divisor_ratios(values),m.shared_divisor_ratios(changed))

    def test_joint_quotient_bound_and_invalid_domains(self):
        a,b,ea,eb=Q(2),Q(3),Q(1,10),Q(1,5)
        bound=m.quotient_error_bound(a,b,ea,eb)
        for sa,sb in product((-1,1),repeat=2):
            self.assertLessEqual(abs((a+sa*ea)/(b+sb*eb)-a/b),bound)
        with self.assertRaises(ValueError):m.quotient_error_bound(a,b,ea,b)
        with self.assertRaises(ValueError):m.shared_divisor_ratios((1,0,1))

    def test_ratio_of_convolutions_is_not_convolution_of_ratio(self):
        from fractions import Fraction as F
        a=(F(1),F(3));b=(F(1),F(2))
        ratio_after=sum(a)/sum(b)
        ratio_before=(a[0]/b[0]+a[1]/b[1])/2
        self.assertNotEqual(ratio_after,ratio_before)


if __name__=='__main__':unittest.main()
